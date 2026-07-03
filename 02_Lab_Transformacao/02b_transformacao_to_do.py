# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab2.png" width="100%"/>
# MAGIC
# MAGIC **Lab 2 — Transformação de Dados com LakeFlow Designer (exercício com TO-DOs)**
# MAGIC
# MAGIC Este notebook contém o pipeline declarativo (Spark Declarative Pipelines) que o
# MAGIC **LakeFlow Designer** gera visualmente. Vamos construir as camadas **Silver** e
# MAGIC **Gold** com **4 transformações**:
# MAGIC
# MAGIC | # | Transformação | Camada |
# MAGIC | -- | -- | -- |
# MAGIC | 1 | **Limpeza + Tempo**: cast de tipos, extração de data/hora/turno e Data Quality | Silver |
# MAGIC | 2 | **Enriquecimento** das usinas com dados de município (região/submercado) | Silver |
# MAGIC | 3 | **Enriquecimento** das unidades com fabricante + **fator de capacidade** | Silver |
# MAGIC | 4 | **Agregação com janela**: ranking de usinas e % de participação na matriz | Gold |
# MAGIC
# MAGIC > No **LakeFlow Designer** você monta essas transformações arrastando blocos. Aqui
# MAGIC > mostramos o código equivalente para você entender o que acontece "por baixo".

# COMMAND ----------

import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *

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
# MAGIC
# MAGIC A tabela `bronze.fato_geracao` veio de um upload de CSV/Excel: precisamos garantir os
# MAGIC **tipos** corretos, derivar componentes de **tempo** (ano/mês/dia/hora/turno) e aplicar
# MAGIC regras de **Data Quality** para descartar leituras inválidas.

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
        # TRANSFORMAÇÃO 1 — TO-DO 1: garanta os tipos corretos das colunas
        # ─────────────────────────────────────────────────────────────────
        # A UI de upload pode inferir texto onde queremos número/timestamp.
        # Dica: use .withColumn("<col>", col("<col>").cast("<tipo>"))
        #   - data_hora          -> timestamp
        #   - geracao_mwh        -> double
        #   - consumo_combustivel-> double
        #   - disponibilidade    -> double
        #   - temperatura_c      -> double
        # .withColumn("data_hora", col("data_hora").cast("timestamp"))   <- complete
        # .withColumn("geracao_mwh", col("geracao_mwh").cast("double"))
        # ... (demais colunas)

        # TRANSFORMAÇÃO 1 — TO-DO 2: extraia ano, mês, dia e hora de data_hora
        # ─────────────────────────────────────────────────────────────────────
        # Dica: use year(), month(), dayofmonth() e hour() sobre "data_hora"
        # .withColumn("ano", year("data_hora"))     <- complete
        # .withColumn("mes", month("data_hora"))
        # .withColumn("dia", dayofmonth("data_hora"))
        # .withColumn("hora", hour("data_hora"))

        # Turno de operação a partir da hora (já pronto — depende do TO-DO 2)
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
# MAGIC
# MAGIC A dimensão de usinas ganha **região**, **submercado do SIN** e **população** vindos
# MAGIC da tabela de enriquecimento de municípios.

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
        # TRANSFORMAÇÃO 2 — TO-DO 3: enriquecer com municípios
        # ─────────────────────────────────────────────────────
        # Dica: faça um join de "usinas" com "municipios" pelas colunas
        #       ["municipio", "uf"] usando how="left".
        #       Isso traz regiao, submercado_sin e populacao.
        # .join(municipios, ["municipio", "uf"], "left")   <- complete aqui
        .withColumn(
            "idade_anos",
            lit(2025) - col("ano_operacao")
        )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRANSFORMAÇÃO 3 — Silver: Unidades + Fabricante + Fator de Capacidade
# MAGIC
# MAGIC Juntamos a geração de cada unidade com seu **fabricante** e calculamos o **fator de
# MAGIC capacidade real** (geração média ÷ potência nominal), comparando com o fator de
# MAGIC disponibilidade de referência do fabricante.

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

    # Geração média por unidade
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
        # TRANSFORMAÇÃO 3 — TO-DO 4: enriquecer com fabricante e calcular métricas
        # ─────────────────────────────────────────────────────────────────────────
        # Dica 1: faça .join(fabricantes, "fabricante", "left")
        # Dica 2: crie a coluna "fator_capacidade" =
        #           geracao_media_mwh / potencia_nominal_mw
        #         (use round(..., 4))
        # Dica 3: crie "gap_vs_referencia" =
        #           fator_capacidade - fator_disponibilidade_ref
        # .join(fabricantes, "fabricante", "left")           <- complete aqui
        # .withColumn("fator_capacidade", ...)
        # .withColumn("gap_vs_referencia", ...)
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## TRANSFORMAÇÃO 4 — Gold: Ranking de usinas com janela (participação na matriz)
# MAGIC
# MAGIC Agregamos a geração por usina e usamos **funções de janela** para calcular a
# MAGIC posição no ranking e o **percentual de participação** de cada usina no total gerado.

# COMMAND ----------

from pyspark.sql.window import Window

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

    # TRANSFORMAÇÃO 4 — TO-DO 5: janela para ranking e % de participação
    # ────────────────────────────────────────────────────────────────────
    # Dica 1: defina uma janela global ordenada pela geração:
    #           w = Window.orderBy(desc("geracao_total_mwh"))
    # Dica 2: crie "ranking" = row_number().over(w)
    # Dica 3: crie "pct_participacao" =
    #           round(geracao_total_mwh / sum(geracao_total_mwh).over(Window.partitionBy()) * 100, 2)
    # w = Window.orderBy(desc("geracao_total_mwh"))
    # return base.withColumn("ranking", ...).withColumn("pct_participacao", ...)
    return base

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
