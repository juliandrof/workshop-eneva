# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab1.png" width="100%"/>
# MAGIC
# MAGIC **Lab 1 — Validação da Ingestão**
# MAGIC
# MAGIC Depois de fazer o upload manual dos 5 arquivos para o seu schema
# MAGIC (veja `01a_guia_upload_dados.py`), execute este notebook para conferir se tudo
# MAGIC foi ingerido corretamente.

# COMMAND ----------

dbutils.widgets.text("nome_participante", "", "Seu Nome (sem espaços/acentos)")

# COMMAND ----------

nome = dbutils.widgets.get("nome_participante").strip().lower().replace(" ", "_")
assert nome != "", "Por favor, preencha seu nome no widget acima!"
catalog_name = "workshop_eneva"
schema_name = nome
spark.sql(f"USE CATALOG {catalog_name}")
spark.sql(f"USE SCHEMA {schema_name}")
print(f"Usando: {catalog_name}.{schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Conferir se as 5 tabelas existem e têm dados

# COMMAND ----------

esperado = {
    "fato_geracao": 5832,                 # 72h x 81 unidades geradoras
    "dim_usinas": 15,
    "dim_unidades_geradoras": 81,
    "enriquecimento_municipios": 9,
    "enriquecimento_fabricantes": 7,
}

print(f"\n{'='*60}")
print(f"VALIDAÇÃO — {catalog_name}.{schema_name}")
print(f"{'='*60}")
tudo_ok = True
for tabela, qtd_esperada in esperado.items():
    try:
        c = spark.table(f"{catalog_name}.{schema_name}.{tabela}").count()
        status = "✓" if c == qtd_esperada else "⚠"
        if c != qtd_esperada:
            tudo_ok = False
        print(f"  {status} {tabela}: {c} linhas (esperado ~{qtd_esperada})")
    except Exception:
        tudo_ok = False
        print(f"  ✗ {tabela}: NÃO ENCONTRADA — faça o upload deste arquivo")
print(f"{'='*60}")
print("Tudo certo! Siga para o Lab 2." if tudo_ok else
      "Revise os uploads faltantes/divergentes antes de seguir.")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Amostra da tabela fato (`fato_geracao`)

# COMMAND ----------

display(
    spark.table(f"{catalog_name}.{schema_name}.fato_geracao")
    .orderBy("id_leitura")
    .limit(10)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Conferir os tipos de coluna
# MAGIC
# MAGIC A UI de Create table infere os tipos automaticamente. Confirme que colunas numéricas
# MAGIC (como `geracao_mwh`, `disponibilidade`) vieram como número, e datas/textos como string.
# MAGIC No Lab 2 faremos o *cast* e a limpeza necessários.

# COMMAND ----------

for tabela in esperado:
    try:
        print(f"\n--- {tabela} ---")
        spark.table(f"{catalog_name}.{schema_name}.{tabela}").printSchema()
    except Exception:
        print(f"  ({tabela} ainda não existe)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Próximo passo
# MAGIC
# MAGIC Com as tabelas ingeridas, siga para o **Lab 2 — Transformação** usando o
# MAGIC **LakeFlow Designer** para construir as tabelas Silver e Gold.
