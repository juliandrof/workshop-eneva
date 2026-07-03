# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab2.png" width="100%"/>
# MAGIC
# MAGIC **Lab 2 — Guia visual do LakeFlow Designer (low-code)**
# MAGIC
# MAGIC O **LakeFlow Designer** é a experiência **visual e sem código** para construir
# MAGIC pipelines de transformação no Databricks. Você monta o fluxo arrastando blocos e o
# MAGIC Designer gera, por baixo, um pipeline declarativo (SDP) — exatamente o código dos
# MAGIC notebooks `02b`/`02c`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo a passo no LakeFlow Designer
# MAGIC
# MAGIC 1. No menu lateral, vá em **Jobs & Pipelines** > **Create** > **ETL Pipeline**
# MAGIC 2. Escolha **Use the LakeFlow Designer** (experiência visual / no-code)
# MAGIC 3. **Nome do pipeline**: `pipeline_eneva_<seu_nome>`
# MAGIC 4. **Catálogo de destino**: `workshop_eneva` — **Schema**: `<seu_nome>` (o mesmo do Lab 1)
# MAGIC
# MAGIC ### Fontes de dados (nós de entrada)
# MAGIC Adicione como fontes as tabelas que você subiu no Lab 1 (em `workshop_eneva.<seu_nome>`):
# MAGIC - `fato_geracao`
# MAGIC - `dim_usinas`
# MAGIC - `dim_unidades_geradoras`
# MAGIC - `enriquecimento_municipios`
# MAGIC - `enriquecimento_fabricantes`
# MAGIC
# MAGIC ### As 4 transformações (blocos visuais)
# MAGIC
# MAGIC As camadas são identificadas pelo **prefixo** do nome (`silver_*`, `gold_*`), todas no
# MAGIC seu schema `workshop_eneva.<seu_nome>`.
# MAGIC
# MAGIC | # | Bloco no Designer | O que fazer | Resultado |
# MAGIC | -- | -- | -- | -- |
# MAGIC | 1 | **Cast + Derive** | Ajustar tipos de `fato_geracao` e derivar `ano/mês/dia/hora/turno` | `silver_geracao` |
# MAGIC | 2 | **Join** | Juntar `dim_usinas` + `enriquecimento_municipios` por `município + uf` | `silver_usinas` |
# MAGIC | 3 | **Join + Compute** | Juntar geração agregada + `dim_unidades_geradoras` + `enriquecimento_fabricantes` e calcular `fator_capacidade` | `silver_desempenho_unidades` |
# MAGIC | 4 | **Aggregate + Window** | Agregar geração por usina, `row_number()` para ranking e `% participação` | `gold_geracao_por_usina` |
# MAGIC
# MAGIC ### Data Quality (Expectations)
# MAGIC No bloco da transformação 1, adicione regras de qualidade (no Designer é o painel
# MAGIC **Data quality**):
# MAGIC - `geracao_mwh >= 0`  → **drop** as linhas inválidas
# MAGIC - `disponibilidade BETWEEN 0 AND 1` → **drop**
# MAGIC
# MAGIC ### Publicar
# MAGIC Clique em **Publish** e depois **Run** — o Designer materializa Silver e Gold e
# MAGIC mostra o **grafo de linhagem** (lineage) automaticamente.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prefere ver o código?
# MAGIC
# MAGIC Os notebooks abaixo contêm exatamente o pipeline que o Designer gera:
# MAGIC
# MAGIC - **Exercício (TO-DOs):** `02b_transformacao_to_do.py`
# MAGIC - **Referência (completo):** `02c_transformacao_completo.py`
# MAGIC
# MAGIC Você pode usar qualquer um dos dois como *source code* do pipeline, caso prefira a
# MAGIC abordagem por código em vez do Designer visual.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação (após rodar o pipeline)
# MAGIC
# MAGIC Execute a célula abaixo (fora do pipeline, em um cluster comum) para conferir as
# MAGIC tabelas Silver e Gold geradas.

# COMMAND ----------

dbutils.widgets.text("nome_participante", "", "Seu Nome (sem espaços/acentos)")
nome = dbutils.widgets.get("nome_participante").strip().lower().replace(" ", "_")
if nome:
    catalog_name = "workshop_eneva"
    schema_name = nome
    tabelas = [
        "silver_geracao", "silver_usinas", "silver_desempenho_unidades",
        "gold_geracao_por_usina", "gold_geracao_por_fonte", "gold_geracao_por_submercado",
    ]
    for t in tabelas:
        try:
            c = spark.table(f"{catalog_name}.{schema_name}.{t}").count()
            print(f"  ✓ {t}: {c} registros")
        except Exception:
            print(f"  ✗ {t}: ainda não criada — rode o pipeline")
else:
    print("Preencha o widget nome_participante para verificar as tabelas.")
