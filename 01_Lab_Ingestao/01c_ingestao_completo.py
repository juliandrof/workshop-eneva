# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab1.png" width="100%"/>
# MAGIC
# MAGIC **Lab 1 — Ingestão de Dados (versão completa / referência)**
# MAGIC
# MAGIC Neste lab ingerimos dados na camada **Bronze** da arquitetura Medallion:
# MAGIC 1. **Auto Loader** — ingestão incremental dos JSONs de geração (streaming)
# MAGIC 2. **Tabelas de referência** — cópia das dimensões e tabelas de enriquecimento para Bronze

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

# COMMAND ----------

df_bronze = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", f"{volume_path}/_schema")
    .schema(schema_geracao)
    .load(volume_path)
    .withColumn("arquivo_origem", col("_metadata.file_path"))
    .withColumn("data_ingestao", current_timestamp())
)

# COMMAND ----------

checkpoint_path = f"{volume_path}/_checkpoint_bronze"
(
    df_bronze.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .outputMode("append")
    .trigger(availableNow=True)
    .toTable(f"{catalog_name}.bronze.bronze_geracao")
)
print("Ingestão da geração concluída!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Ingerir as tabelas de referência para a camada Bronze

# COMMAND ----------

(
    spark.table(f"{catalog_name}.raw.dim_usinas")
    .write.mode("overwrite")
    .saveAsTable(f"{catalog_name}.bronze.bronze_usinas")
)
print("bronze_usinas ingerida!")

(
    spark.table(f"{catalog_name}.raw.dim_unidades_geradoras")
    .write.mode("overwrite")
    .saveAsTable(f"{catalog_name}.bronze.bronze_unidades")
)
print("bronze_unidades ingerida!")

(
    spark.table(f"{catalog_name}.raw.enriquecimento_municipios")
    .write.mode("overwrite")
    .saveAsTable(f"{catalog_name}.bronze.bronze_municipios")
)
print("bronze_municipios ingerida!")

(
    spark.table(f"{catalog_name}.raw.enriquecimento_fabricantes")
    .write.mode("overwrite")
    .saveAsTable(f"{catalog_name}.bronze.bronze_fabricantes")
)
print("bronze_fabricantes ingerida!")

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
    c = spark.table(f"{catalog_name}.bronze.{t}").count()
    print(f"  ✓ bronze.{t}: {c} registros")
print(f"{'='*60}")

# COMMAND ----------

# Amostra dos dados de geração ingeridos
display(
    spark.table(f"{catalog_name}.bronze.bronze_geracao")
    .select("id_usina", "data_hora", size("leituras").alias("qtd_leituras"),
            "arquivo_origem", "data_ingestao")
    .orderBy("data_hora")
    .limit(10)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Próximo passo
# MAGIC
# MAGIC Com a camada **Bronze** populada, siga para o **Lab 2 — Transformação** usando o
# MAGIC **LakeFlow Designer** para construir as camadas Silver e Gold.
