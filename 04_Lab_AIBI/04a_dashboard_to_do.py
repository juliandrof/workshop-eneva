# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab4.png" width="100%"/>
# MAGIC
# MAGIC **Lab 4 — Criando um AI/BI Dashboard (exercício com TO-DOs)**
# MAGIC
# MAGIC Neste lab vamos construir um **AI/BI Dashboard** interativo sobre a geração do parque
# MAGIC Eneva, usando as tabelas Gold. Você vai:
# MAGIC 1. Preparar/validar os datasets (queries SQL)
# MAGIC 2. Criar o Dashboard na UI
# MAGIC 3. Montar as visualizações seguindo o layout de referência

# COMMAND ----------

dbutils.widgets.text("nome_participante", "", "Seu Nome (sem espaços/acentos)")

# COMMAND ----------

nome = dbutils.widgets.get("nome_participante").strip().lower().replace(" ", "_")
assert nome != "", "Por favor, preencha seu nome no widget acima!"
catalog_name = f"workshop_eneva_{nome}"
spark.sql(f"USE CATALOG {catalog_name}")
print(f"Usando catálogo: {catalog_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Validar os dados Gold antes de montar o dashboard

# COMMAND ----------

# TO-DO 1: Confira o KPI de resumo geral
# ────────────────────────────────────────
# Dica: complete a query somando a geração total (SUM(geracao_mwh)),
#       contando usinas distintas e a disponibilidade média,
#       a partir de gold.vw_geracao_detalhada.
display(spark.sql(f"""
    SELECT
        -- ROUND(SUM(geracao_mwh), 2) AS geracao_total_mwh,   <- complete
        -- COUNT(DISTINCT nome_usina) AS usinas_ativas,        <- complete
        -- ROUND(AVG(disponibilidade), 4) AS disponibilidade_media  <- complete
        COUNT(*) AS total_leituras
    FROM {catalog_name}.gold.vw_geracao_detalhada
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criar o Dashboard (na UI)
# MAGIC
# MAGIC 1. Vá em **Dashboards** > **Create dashboard**
# MAGIC 2. **Nome**: `Dashboard Geração Eneva - <seu_nome>`
# MAGIC 3. Na aba **Data**, crie um dataset para cada query da próxima célula
# MAGIC 4. Na aba **Canvas**, adicione os widgets seguindo o layout de referência

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Queries dos datasets
# MAGIC
# MAGIC Execute a célula abaixo para imprimir as queries. Copie cada uma para um **dataset**
# MAGIC no dashboard. Complete os TO-DOs que faltam.

# COMMAND ----------

queries = {
    "KPI - Resumo Geral": f"""
SELECT
    ROUND(SUM(geracao_mwh), 2) AS geracao_total_mwh,
    COUNT(DISTINCT nome_usina) AS usinas_ativas,
    ROUND(AVG(disponibilidade), 4) AS disponibilidade_media,
    ROUND(SUM(consumo_combustivel), 2) AS combustivel_total
FROM {catalog_name}.gold.vw_geracao_detalhada
""",

    "Geração por Fonte": f"""
SELECT fonte, combustivel,
       ROUND(geracao_total_mwh, 2) AS geracao_mwh,
       num_usinas
FROM {catalog_name}.gold.gold_geracao_por_fonte
ORDER BY geracao_total_mwh DESC
""",

    "Ranking de Usinas": f"""
SELECT ranking, nome_usina, fonte, uf,
       ROUND(geracao_total_mwh, 2) AS geracao_mwh,
       pct_participacao
FROM {catalog_name}.gold.gold_geracao_por_usina
ORDER BY ranking
""",

    # TO-DO 2: Query de geração por submercado do SIN
    # ─────────────────────────────────────────────────
    # Dica: selecione submercado_sin, regiao, geracao_total_mwh, num_usinas
    #       de gold.gold_geracao_por_submercado, ordenando por geração desc.
    "Geração por Submercado": f"""
-- complete a query aqui
""",

    # TO-DO 3: Query de perfil de geração por turno
    # ───────────────────────────────────────────────
    # Dica: agrupe vw_geracao_detalhada por turno e fonte, some geracao_mwh.
    #       Isso mostra o perfil solar (dia) vs térmica (constante).
    "Geração por Turno": f"""
-- complete a query aqui
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
