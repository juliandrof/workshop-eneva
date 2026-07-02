# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab1.png" width="100%"/>
# MAGIC
# MAGIC **Lab 1 — Ingestão de Dados (exercício com TO-DOs)**
# MAGIC
# MAGIC Neste lab vamos ingerir dados na camada **Bronze** da arquitetura Medallion:
# MAGIC 1. **Auto Loader** — ingestão incremental dos JSONs de geração (streaming)
# MAGIC 2. **Tabelas de referência** — cópia das dimensões e tabelas de enriquecimento para Bronze
# MAGIC
# MAGIC > **Antes de começar:** deixe o notebook `01a_gerador_geracao_streaming` rodando.

# COMMAND ----------

dbutils.widgets.text("nome_participante", "", "Seu Nome (sem espaços/acentos)")

# COMMAND ----------

nome = dbutils.widgets.get("nome_participante").strip().lower().replace(" ", "_")
assert nome != "", "Por favor, preencha seu nome no widget acima!"
catalog_name = f"workshop_eneva_{nome}"
spark.sql(f"USE CATALOG {catalog_name}")
volume_path = f"/Volumes/{catalog_name}/raw/geracao_json"
print(f"Usando catálogo: {catalog_name}")
print(f"Volume de origem: {volume_path}")

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Definir o schema do JSON de geração
# MAGIC
# MAGIC Cada arquivo JSON representa uma usina em um instante, com um array de `leituras`
# MAGIC (uma por unidade geradora).

# COMMAND ----------

schema_geracao = StructType([
    StructField("id_usina", IntegerType(), False),
    StructField("data_hora", StringType(), False),
    StructField("leituras", ArrayType(StructType([
        StructField("id_leitura", LongType(), False),
        StructField("id_unidade", IntegerType(), False),
        StructField("id_usina", IntegerType(), False),
        StructField("geracao_mwh", DoubleType(), False),
        StructField("consumo_combustivel", DoubleType(), False),
        StructField("disponibilidade", DoubleType(), False),
        StructField("temperatura_c", DoubleType(), False),
    ])), False),
])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Ingestão com Auto Loader → `bronze.bronze_geracao`
# MAGIC
# MAGIC O **Auto Loader** (`cloudFiles`) detecta automaticamente novos arquivos no Volume e
# MAGIC os ingere de forma incremental e *exactly-once*.

# COMMAND ----------

# TO-DO 1: Complete a leitura com Auto Loader
# ─────────────────────────────────────────────
# Dica: use spark.readStream.format("cloudFiles")
#   - .option("cloudFiles.format", "json")
#   - .option("cloudFiles.schemaLocation", f"{volume_path}/_schema")
#   - .schema(schema_geracao)
#   - .load(volume_path)
# Adicione também duas colunas de metadados de ingestão:
#   - "arquivo_origem" = col("_metadata.file_path")
#   - "data_ingestao" = current_timestamp()
df_bronze = (
    spark.readStream
    .format("cloudFiles")
    # .option(...)  <- complete aqui
    # .schema(...)
    # .load(...)
    # .withColumn("arquivo_origem", ...)
    # .withColumn("data_ingestao", ...)
)

# COMMAND ----------

# Gravar a stream na tabela bronze_geracao (checkpoint gerenciado)
checkpoint_path = f"{volume_path}/_checkpoint_bronze"
(
    df_bronze.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .outputMode("append")
    .trigger(availableNow=True)   # processa tudo o que já chegou e finaliza
    .toTable(f"{catalog_name}.bronze.bronze_geracao")
)
print("Ingestão da geração concluída!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Ingerir as tabelas de referência para a camada Bronze
# MAGIC
# MAGIC As dimensões e tabelas de enriquecimento vêm do schema `raw`. Vamos materializá-las
# MAGIC em `bronze` para que o Lab 2 (transformação) trabalhe sobre uma base consistente.

# COMMAND ----------

# bronze_usinas
(
    spark.table(f"{catalog_name}.raw.dim_usinas")
    .write.mode("overwrite")
    .saveAsTable(f"{catalog_name}.bronze.bronze_usinas")
)
print("bronze_usinas ingerida!")

# COMMAND ----------

# TO-DO 2: Ingira a dimensão de unidades geradoras para bronze_unidades
# ─────────────────────────────────────────────────────────────────────
# Dica: siga exatamente o padrão de bronze_usinas acima.
#   - Origem:  {catalog_name}.raw.dim_unidades_geradoras
#   - Destino: {catalog_name}.bronze.bronze_unidades


# COMMAND ----------

# TO-DO 3: Ingira as DUAS tabelas de enriquecimento para bronze
# ──────────────────────────────────────────────────────────────
# Dica: repita o padrão para as duas tabelas:
#   - raw.enriquecimento_municipios   -> bronze.bronze_municipios
#   - raw.enriquecimento_fabricantes  -> bronze.bronze_fabricantes


# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Verificação da ingestão

# COMMAND ----------

print(f"\n{'='*60}")
print("VERIFICAÇÃO DA CAMADA BRONZE")
print(f"{'='*60}")
tabelas_bronze = [
    "bronze_geracao", "bronze_usinas", "bronze_unidades",
    "bronze_municipios", "bronze_fabricantes",
]
for t in tabelas_bronze:
    try:
        c = spark.table(f"{catalog_name}.bronze.{t}").count()
        print(f"  ✓ bronze.{t}: {c} registros")
    except Exception as e:
        print(f"  ✗ bronze.{t}: NÃO ENCONTRADA (complete os TO-DOs)")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Próximo passo
# MAGIC
# MAGIC Com a camada **Bronze** populada, siga para o **Lab 2 — Transformação** usando o
# MAGIC **LakeFlow Designer** para construir as camadas Silver e Gold.
