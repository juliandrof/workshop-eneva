# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab2.png" width="100%"/>
# MAGIC
# MAGIC **Lab 2 — Guia visual do LakeFlow Designer (low-code)**
# MAGIC
# MAGIC O **LakeFlow Designer** é a experiência **visual e sem código** ("Visual data prep")
# MAGIC para preparar e transformar dados no Databricks. Você monta o fluxo arrastando
# MAGIC **operadores** em um canvas, sem escrever código.
# MAGIC
# MAGIC > O passo a passo completo (com todas as fórmulas para copiar) está no **README** do
# MAGIC > repositório, na seção **Lab 02**. Este notebook é um resumo de apoio.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Abrir o LakeFlow Designer (Visual data prep)
# MAGIC
# MAGIC 1. Na **barra lateral esquerda**, clique no ícone **+ (New)**
# MAGIC 2. Selecione **Visual data prep**
# MAGIC 3. Abre o **canvas** em branco com a tela de boas-vindas
# MAGIC
# MAGIC > O rascunho é salvo automaticamente. Você pode renomeá-lo no topo para
# MAGIC > `visual_prep_eneva_<seu_nome>`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Adicionar as fontes de dados (operador Source)
# MAGIC
# MAGIC Para cada tabela que você ingeriu no Lab 1:
# MAGIC
# MAGIC 1. Na tela de boas-vindas, clique em **Select source operator** (ou, no canvas, abra o
# MAGIC    menu de operadores e escolha **Source**)
# MAGIC 2. Na aba de configuração, escolha **Browse** e selecione a tabela existente em
# MAGIC    `workshop_eneva` > `<seu_nome>`
# MAGIC 3. Repita para as 5 tabelas de entrada:
# MAGIC    - `fato_geracao`
# MAGIC    - `dim_usinas`
# MAGIC    - `dim_unidades_geradoras`
# MAGIC    - `enriquecimento_municipios`
# MAGIC    - `enriquecimento_fabricantes`
# MAGIC
# MAGIC > Para **conectar** operadores, arraste da bolinha de **saída** (borda direita) de um
# MAGIC > operador até a bolinha de **entrada** (borda esquerda) do próximo.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Preparação + as 3 transformações (operadores no canvas)
# MAGIC
# MAGIC Abra o **menu de operadores** (painel à esquerda) e arraste cada operador para o canvas.
# MAGIC Para configurar um operador, dê **duplo clique** nele (ou clique no ícone de **lápis**).
# MAGIC As camadas são identificadas pelo **prefixo** do nome da tabela de saída
# MAGIC (`silver_*`, `gold_*`), todas no seu schema `workshop_eneva.<seu_nome>`.
# MAGIC
# MAGIC > Os tipos das colunas já vêm corretos do upload (Lab 1) — **não é preciso fazer cast**.
# MAGIC
# MAGIC | # | A partir de | Operadores no Designer | Resultado (Output) |
# MAGIC | -- | -- | -- | -- |
# MAGIC | Prep | `fato_geracao` | **Prepare** (`ano/mês/dia/hora/turno`) + **Filter** (`geracao_mwh >= 0` e `disponibilidade BETWEEN 0 AND 1`) | `silver_geracao` |
# MAGIC | 1 | `dim_usinas` + `enriquecimento_municipios` | **Join** por `municipio` + `uf` | `silver_usinas` |
# MAGIC | 2 | `silver_geracao` + `dim_unidades_geradoras` + `enriquecimento_fabricantes` | **Aggregate** (média por unidade) + **Join** + **Prepare** (`fator_capacidade`) | `silver_desempenho_unidades` |
# MAGIC | 3 | `silver_geracao` + `silver_usinas` | **Aggregate** por usina + **Prepare/Window** (ranking e `% participação`) | `gold_geracao_por_usina` |
# MAGIC
# MAGIC > **Passo a passo completo, com as fórmulas para copiar, está no README (seção Lab 02).**

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Pré-visualizar os resultados
# MAGIC
# MAGIC - Clique em qualquer operador para ver a **prévia dos dados** no painel inferior
# MAGIC - Use o seletor **Rows scanned** para controlar o volume processado na prévia

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Publicar cada saída (operador Output) e executar
# MAGIC
# MAGIC Para cada tabela de resultado (Silver e Gold):
# MAGIC
# MAGIC 1. Adicione um operador **Output** ligado ao último operador da transformação
# MAGIC 2. Configure:
# MAGIC    - **Table name**: ex. `silver_geracao`, `gold_geracao_por_usina`, ...
# MAGIC    - **Output location**: catálogo `workshop_eneva` + schema `<seu_nome>`
# MAGIC 3. Clique em **Run** — cada execução **cria ou substitui** a tabela gerenciada
# MAGIC 4. (Opcional) Clique em **Schedule** para agendar execuções recorrentes
# MAGIC
# MAGIC > O Designer mostra o **grafo de linhagem** (lineage) entre as tabelas automaticamente.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação (após executar)
# MAGIC
# MAGIC Execute a célula abaixo (em um cluster comum) para conferir as tabelas Silver e Gold geradas.

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
