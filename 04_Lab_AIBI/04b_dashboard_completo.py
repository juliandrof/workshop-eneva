# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab4.png" width="100%"/>
# MAGIC
# MAGIC **Lab 4 — Criando um AI/BI Dashboard (versão completa / referência)**

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
# MAGIC ## 1. Validar os dados Gold

# COMMAND ----------

display(spark.sql(f"""
    SELECT
        ROUND(SUM(geracao_total_mwh), 2) AS geracao_total_mwh,
        COUNT(DISTINCT nome_usina) AS usinas_ativas,
        ROUND(AVG(disponibilidade_media), 4) AS disponibilidade_media,
        ROUND(SUM(consumo_combustivel_total), 2) AS combustivel_total
    FROM {catalog_name}.{schema_name}.gold_geracao_por_usina
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criar o Dashboard (na UI)
# MAGIC
# MAGIC 1. **Dashboards** > **Create dashboard**
# MAGIC 2. **Nome**: `Dashboard Geração Eneva - <seu_nome>`
# MAGIC 3. Crie um dataset por query abaixo e monte os widgets do layout de referência.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Queries dos datasets (completas)

# COMMAND ----------

queries = {
    "KPI - Resumo Geral": f"""
SELECT
    ROUND(SUM(geracao_total_mwh), 2) AS geracao_total_mwh,
    COUNT(DISTINCT nome_usina) AS usinas_ativas,
    ROUND(AVG(disponibilidade_media), 4) AS disponibilidade_media,
    ROUND(SUM(consumo_combustivel_total), 2) AS combustivel_total
FROM {catalog_name}.{schema_name}.gold_geracao_por_usina
""",

    "Geração por Fonte": f"""
SELECT fonte, combustivel,
       ROUND(geracao_total_mwh, 2) AS geracao_mwh,
       num_usinas
FROM {catalog_name}.{schema_name}.gold_geracao_por_fonte
ORDER BY geracao_total_mwh DESC
""",

    "Ranking de Usinas": f"""
SELECT ranking, nome_usina, fonte, uf,
       ROUND(geracao_total_mwh, 2) AS geracao_mwh,
       pct_participacao
FROM {catalog_name}.{schema_name}.gold_geracao_por_usina
ORDER BY ranking
""",

    "Geração por Submercado": f"""
SELECT submercado_sin, regiao,
       ROUND(geracao_total_mwh, 2) AS geracao_mwh,
       num_usinas, num_estados
FROM {catalog_name}.{schema_name}.gold_geracao_por_submercado
ORDER BY geracao_total_mwh DESC
""",

    "Geração por Turno": f"""
SELECT g.turno, u.fonte,
       ROUND(SUM(g.geracao_mwh), 2) AS geracao_mwh
FROM {catalog_name}.{schema_name}.silver_geracao g
LEFT JOIN {catalog_name}.{schema_name}.dim_usinas u ON g.id_usina = u.id_usina
GROUP BY g.turno, u.fonte
ORDER BY
    CASE g.turno WHEN 'Madrugada' THEN 1 WHEN 'Manhã' THEN 2
               WHEN 'Tarde' THEN 3 ELSE 4 END,
    u.fonte
""",

    "Disponibilidade por Usina": f"""
SELECT nome_usina, fonte,
       ROUND(disponibilidade_media * 100, 1) AS disponibilidade_pct
FROM {catalog_name}.{schema_name}.gold_geracao_por_usina
ORDER BY disponibilidade_media DESC
""",
}

print("=" * 60)
print("QUERIES PARA OS DATASETS DO DASHBOARD")
print("=" * 60)
for titulo, sql in queries.items():
    print(f"\n--- {titulo} ---")
    print(sql)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Layout de referência
# MAGIC
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/dashboard_layout.png" width="100%"/>
# MAGIC
# MAGIC | Dataset | Visualização |
# MAGIC | -- | -- |
# MAGIC | KPI - Resumo Geral | **Counter** (4 counters) |
# MAGIC | Geração por Fonte | **Pie Chart** |
# MAGIC | Ranking de Usinas | **Bar Chart** (horizontal) |
# MAGIC | Geração por Submercado | **Bar Chart** |
# MAGIC | Geração por Turno | **Bar Chart** (agrupado por fonte) |
# MAGIC | Disponibilidade por Usina | **Table** |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parabéns! Workshop Concluído!
# MAGIC
# MAGIC Você completou todos os 4 labs do Workshop Eneva:
# MAGIC
# MAGIC - **Lab 1** — Ingestão: upload manual de CSV/XLSX → camada Bronze
# MAGIC - **Lab 2** — Transformação: LakeFlow Designer (Silver/Gold, 4 transformações)
# MAGIC - **Lab 3** — Genie Agent: análise em linguagem natural
# MAGIC - **Lab 4** — AI/BI Dashboard: visualizações interativas
