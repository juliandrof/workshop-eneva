# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab2.png" width="100%"/>
# MAGIC
# MAGIC **Lab 2 — Transformação de Dados com LakeFlow Designer (versão completa / referência)**
# MAGIC
# MAGIC Pipeline declarativo com as **4 transformações** que constroem Silver e Gold:
# MAGIC
# MAGIC | # | Transformação | Camada |
# MAGIC | -- | -- | -- |
# MAGIC | 1 | **Limpeza + Tempo**: cast de tipos, extração de data/hora/turno e Data Quality | Silver |
# MAGIC | 2 | **Enriquecimento** das usinas com dados de município (região/submercado) | Silver |
# MAGIC | 3 | **Enriquecimento** das unidades com fabricante + **fator de capacidade** | Silver |
# MAGIC | 4 | **Agregação com janela**: ranking de usinas e % de participação na matriz | Gold |

# COMMAND ----------

import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuração
# MAGIC
# MAGIC > **Como criar o pipeline (LakeFlow Designer / SDP):**
# MAGIC > 1. Vá em **Jobs & Pipelines** > **ETL pipeline**
# MAGIC > 2. **Pipeline name**: `pipeline_eneva_<seu_nome>`
# MAGIC > 3. **Source code**: selecione este notebook
# MAGIC > 4. **Target catalog**: `workshop_eneva_<seu_nome>`
# MAGIC > 5. **Target schema**: `default`
# MAGIC > 6. **Configuration** → adicione: `pipeline.nome_participante` = `<seu_nome>`
# MAGIC > 7. **Compute**: Serverless (recomendado)
# MAGIC > 8. Clique em **Create** e depois **Start**

# COMMAND ----------

nome_participante = spark.conf.get("pipeline.nome_participante", "default")
catalog_name = f"workshop_eneva_{nome_participante}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRANSFORMAÇÃO 1 — Silver: Limpeza + Tempo

# COMMAND ----------

@dlt.table(
    name="silver.silver_geracao",
    comment="Leituras de geração limpas, tipadas e com features de tempo",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("geracao_nao_negativa", "geracao_mwh >= 0")
@dlt.expect_or_drop("disponibilidade_valida", "disponibilidade BETWEEN 0 AND 1")
def silver_geracao():
    bronze = spark.read.table(f"{catalog_name}.bronze.fato_geracao")

    return (
        bronze
        # Garante os tipos corretos (a UI de upload pode inferir texto)
        .withColumn("data_hora", col("data_hora").cast("timestamp"))
        .withColumn("geracao_mwh", col("geracao_mwh").cast("double"))
        .withColumn("consumo_combustivel", col("consumo_combustivel").cast("double"))
        .withColumn("disponibilidade", col("disponibilidade").cast("double"))
        .withColumn("temperatura_c", col("temperatura_c").cast("double"))
        # Features de tempo
        .withColumn("ano", year("data_hora"))
        .withColumn("mes", month("data_hora"))
        .withColumn("dia", dayofmonth("data_hora"))
        .withColumn("hora", hour("data_hora"))
        .withColumn(
            "turno",
            when(col("hora").between(6, 11), "Manhã")
            .when(col("hora").between(12, 17), "Tarde")
            .when(col("hora").between(18, 23), "Noite")
            .otherwise("Madrugada")
        )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRANSFORMAÇÃO 2 — Silver: Usinas enriquecidas com Município

# COMMAND ----------

@dlt.table(
    name="silver.silver_usinas",
    comment="Dimensão de usinas enriquecida com dados de município",
    table_properties={"quality": "silver"},
)
def silver_usinas():
    usinas = spark.read.table(f"{catalog_name}.bronze.dim_usinas")
    municipios = spark.read.table(f"{catalog_name}.bronze.enriquecimento_municipios")

    return (
        usinas
        .join(municipios, ["municipio", "uf"], "left")
        .withColumn("idade_anos", lit(2025) - col("ano_operacao"))
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRANSFORMAÇÃO 3 — Silver: Unidades + Fabricante + Fator de Capacidade

# COMMAND ----------

@dlt.table(
    name="silver.silver_desempenho_unidades",
    comment="Desempenho por unidade geradora com fator de capacidade vs referência",
    table_properties={"quality": "silver"},
)
def silver_desempenho_unidades():
    geracao = dlt.read("silver.silver_geracao")
    unidades = spark.read.table(f"{catalog_name}.bronze.dim_unidades_geradoras")
    fabricantes = spark.read.table(f"{catalog_name}.bronze.enriquecimento_fabricantes")

    agg = (
        geracao
        .groupBy("id_unidade", "id_usina")
        .agg(
            avg("geracao_mwh").alias("geracao_media_mwh"),
            sum("geracao_mwh").alias("geracao_total_mwh"),
            avg("disponibilidade").alias("disponibilidade_media"),
            count("*").alias("num_leituras"),
        )
    )

    return (
        agg
        .join(unidades, ["id_unidade", "id_usina"], "left")
        .join(fabricantes, "fabricante", "left")
        .withColumn(
            "fator_capacidade",
            round(col("geracao_media_mwh") / col("potencia_nominal_mw"), 4)
        )
        .withColumn(
            "gap_vs_referencia",
            round(col("fator_capacidade") - col("fator_disponibilidade_ref"), 4)
        )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRANSFORMAÇÃO 4 — Gold: Ranking de usinas com janela (participação na matriz)

# COMMAND ----------

@dlt.table(
    name="gold.gold_geracao_por_usina",
    comment="Geração total por usina com ranking e participação percentual",
    table_properties={"quality": "gold"},
)
def gold_geracao_por_usina():
    geracao = dlt.read("silver.silver_geracao")
    usinas = dlt.read("silver.silver_usinas")

    base = (
        geracao
        .groupBy("id_usina")
        .agg(
            sum("geracao_mwh").alias("geracao_total_mwh"),
            avg("disponibilidade").alias("disponibilidade_media"),
            sum("consumo_combustivel").alias("consumo_combustivel_total"),
        )
        .join(usinas.select("id_usina", "nome_usina", "fonte", "combustivel",
                            "municipio", "uf", "regiao", "submercado_sin",
                            "potencia_instalada_mw"),
              "id_usina", "left")
    )

    w_rank = Window.orderBy(desc("geracao_total_mwh"))
    w_total = Window.partitionBy()

    return (
        base
        .withColumn("ranking", row_number().over(w_rank))
        .withColumn(
            "pct_participacao",
            round(col("geracao_total_mwh") / sum("geracao_total_mwh").over(w_total) * 100, 2)
        )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## GOLD — Geração por Fonte (matriz energética)

# COMMAND ----------

@dlt.table(
    name="gold.gold_geracao_por_fonte",
    comment="Geração agregada por fonte de energia",
    table_properties={"quality": "gold"},
)
def gold_geracao_por_fonte():
    geracao = dlt.read("silver.silver_geracao")
    usinas = dlt.read("silver.silver_usinas")

    return (
        geracao
        .join(usinas.select("id_usina", "fonte", "combustivel"), "id_usina", "left")
        .groupBy("fonte", "combustivel")
        .agg(
            sum("geracao_mwh").alias("geracao_total_mwh"),
            avg("geracao_mwh").alias("geracao_media_mwh"),
            countDistinct("id_usina").alias("num_usinas"),
            avg("disponibilidade").alias("disponibilidade_media"),
        )
        .orderBy(desc("geracao_total_mwh"))
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## GOLD — Geração por Submercado do SIN

# COMMAND ----------

@dlt.table(
    name="gold.gold_geracao_por_submercado",
    comment="Geração agregada por submercado do Sistema Interligado Nacional",
    table_properties={"quality": "gold"},
)
def gold_geracao_por_submercado():
    geracao = dlt.read("silver.silver_geracao")
    usinas = dlt.read("silver.silver_usinas")

    return (
        geracao
        .join(usinas.select("id_usina", "regiao", "submercado_sin", "uf"), "id_usina", "left")
        .groupBy("submercado_sin", "regiao")
        .agg(
            sum("geracao_mwh").alias("geracao_total_mwh"),
            countDistinct("id_usina").alias("num_usinas"),
            countDistinct("uf").alias("num_estados"),
            avg("disponibilidade").alias("disponibilidade_media"),
        )
        .orderBy(desc("geracao_total_mwh"))
    )
