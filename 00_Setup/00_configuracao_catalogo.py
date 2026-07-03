# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_setup.png" width="100%"/>
# MAGIC
# MAGIC Este notebook prepara o ambiente do workshop:
# MAGIC - Usa um **catálogo compartilhado** `workshop_eneva` (criado uma vez e reaproveitado)
# MAGIC - Cria um **schema pessoal** com o seu nome, onde ficarão todas as suas tabelas
# MAGIC
# MAGIC **Importante:** Preencha o widget `nome_participante` com seu primeiro nome (sem espaços, sem acentos, minúsculo).

# COMMAND ----------

# Widget para personalização
dbutils.widgets.text("nome_participante", "", "Seu Nome (sem espaços/acentos)")

# COMMAND ----------

nome = dbutils.widgets.get("nome_participante").strip().lower().replace(" ", "_")
assert nome != "", "Por favor, preencha seu nome no widget acima!"
print(f"Participante: {nome}")

catalog_name = "workshop_eneva"   # catálogo fixo, compartilhado por todos
schema_name = nome                # cada participante usa um schema com o próprio nome
print(f"Catálogo: {catalog_name}")
print(f"Schema:   {schema_name}")
print(f"Destino das suas tabelas: {catalog_name}.{schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Criando o Catálogo (se ainda não existir) e o seu Schema
# MAGIC
# MAGIC O catálogo `workshop_eneva` é **compartilhado**: se outro participante já o criou,
# MAGIC ele é **reaproveitado** (graças ao `IF NOT EXISTS`). Cada pessoa isola seu trabalho
# MAGIC em um **schema próprio** (`workshop_eneva.<seu_nome>`).

# COMMAND ----------

# Catálogo compartilhado — criado uma única vez, reaproveitado nas próximas execuções
spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
print(f"Catálogo '{catalog_name}' pronto (criado ou reaproveitado).")

# COMMAND ----------

# Schema pessoal do participante
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}")
print(f"Schema '{catalog_name}.{schema_name}' pronto!")

# COMMAND ----------

# Define o schema padrão da sessão para facilitar os próximos passos
spark.sql(f"USE CATALOG {catalog_name}")
spark.sql(f"USE SCHEMA {schema_name}")
print(f"Sessão configurada para usar {catalog_name}.{schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação

# COMMAND ----------

print(f"\n{'='*60}")
print(f"AMBIENTE PRONTO!")
print(f"{'='*60}")
print(f"\nCatálogo: {catalog_name}  (compartilhado)")
print(f"Schema:   {schema_name}  (seu)")
print(f"\nTodas as suas tabelas ficarão em: {catalog_name}.{schema_name}")
print(f"\n{'='*60}")
print(f"Próximo passo: Lab 1 — Ingestão de Dados")
print(f"Faça o upload dos arquivos CSV/XLSX da pasta 'dados/' para o")
print(f"schema '{catalog_name}.{schema_name}' via Catalog > Create table.")
print(f"{'='*60}")
