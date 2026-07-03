# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab1.png" width="100%"/>
# MAGIC
# MAGIC **Lab 1 — Ingestão de Dados (guia de upload manual)**
# MAGIC
# MAGIC Neste lab vamos ingerir os dados fazendo o **upload manual** dos arquivos da pasta
# MAGIC `dados/` — sem escrever código. É a forma mais simples e comum de trazer planilhas e
# MAGIC extrações (CSV/Excel) para o Databricks.
# MAGIC
# MAGIC > **Destino:** todas as tabelas vão para o **seu schema pessoal** dentro do catálogo
# MAGIC > compartilhado: `workshop_eneva.<seu_nome>`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Arquivos que vamos ingerir
# MAGIC
# MAGIC A pasta `dados/` do repositório contém 5 tabelas — a **fato em CSV** e as
# MAGIC **dimensões/enriquecimento em Excel (XLSX)**:
# MAGIC
# MAGIC | Arquivo | Formato | Tipo | Descrição |
# MAGIC | -- | -- | -- | -- |
# MAGIC | `fato_geracao.csv` | CSV | **Fato** | Leituras horárias de geração por unidade (MWh, combustível, disponibilidade) |
# MAGIC | `dim_usinas.xlsx` | XLSX | Dimensão | Usinas termelétricas (gás/carvão) e solares |
# MAGIC | `dim_unidades_geradoras.xlsx` | XLSX | Dimensão | Motores, turbinas e inversores por usina |
# MAGIC | `enriquecimento_municipios.xlsx` | XLSX | Enriquecimento | Região, submercado do SIN e população |
# MAGIC | `enriquecimento_fabricantes.xlsx` | XLSX | Enriquecimento | País, eficiência e disponibilidade de referência |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo a passo — Catalog > Create table (Upload files)
# MAGIC
# MAGIC Repita para **cada um dos 5 arquivos**:
# MAGIC
# MAGIC 1. No menu lateral, abra **Catalog**
# MAGIC 2. Navegue até o catálogo `workshop_eneva` > seu schema **`<seu_nome>`**
# MAGIC 3. Clique em **Create** > **Create table** (ou **Add data** > **Create or modify table**)
# MAGIC 4. **Arraste o arquivo** (ex.: `fato_geracao.csv`) ou clique para selecioná-lo
# MAGIC 5. Confira a prévia:
# MAGIC    - **Catalog**: `workshop_eneva`
# MAGIC    - **Schema**: `<seu_nome>`
# MAGIC    - **Table name**: use o nome do arquivo sem a extensão (ex.: `fato_geracao`)
# MAGIC    - **First row contains header**: ativado
# MAGIC    - Confira os tipos de coluna sugeridos (número vs texto)
# MAGIC 6. Clique em **Create table**
# MAGIC
# MAGIC > **Dica:** a UI de Create table aceita **CSV e XLSX**. Para os arquivos Excel
# MAGIC > (`.xlsx`), a primeira planilha (`Dados`) é usada automaticamente.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tabelas esperadas ao final
# MAGIC
# MAGIC Depois de subir os 5 arquivos, o seu schema deve conter:
# MAGIC
# MAGIC ```
# MAGIC workshop_eneva.<seu_nome>.fato_geracao
# MAGIC workshop_eneva.<seu_nome>.dim_usinas
# MAGIC workshop_eneva.<seu_nome>.dim_unidades_geradoras
# MAGIC workshop_eneva.<seu_nome>.enriquecimento_municipios
# MAGIC workshop_eneva.<seu_nome>.enriquecimento_fabricantes
# MAGIC ```
# MAGIC
# MAGIC > Use o notebook **`01b_validacao.py`** para conferir se todas as tabelas foram
# MAGIC > criadas corretamente antes de seguir para o Lab 2.
