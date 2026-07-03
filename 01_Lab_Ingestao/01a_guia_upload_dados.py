# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab1.png" width="100%"/>
# MAGIC
# MAGIC **Lab 1 — Ingestão de Dados (guia de upload manual)**
# MAGIC
# MAGIC Neste lab vamos ingerir os dados na camada **Bronze** fazendo o **upload manual** dos
# MAGIC arquivos da pasta `dados/` — sem escrever código. É a forma mais simples e comum de
# MAGIC trazer planilhas e extrações (CSV/Excel) para o Databricks.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Arquivos que vamos ingerir
# MAGIC
# MAGIC A pasta `dados/` do repositório contém 5 tabelas, cada uma em **CSV** e **XLSX**
# MAGIC (use o formato que preferir):
# MAGIC
# MAGIC | Arquivo | Tipo | Descrição |
# MAGIC | -- | -- | -- |
# MAGIC | `fato_geracao` | **Fato** | Leituras horárias de geração por unidade (MWh, combustível, disponibilidade) |
# MAGIC | `dim_usinas` | Dimensão | Usinas termelétricas (gás/carvão) e solares |
# MAGIC | `dim_unidades_geradoras` | Dimensão | Motores, turbinas e inversores por usina |
# MAGIC | `enriquecimento_municipios` | Enriquecimento | Região, submercado do SIN e população |
# MAGIC | `enriquecimento_fabricantes` | Enriquecimento | País, eficiência e disponibilidade de referência |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo a passo — Catalog > Create table (Upload files)
# MAGIC
# MAGIC Repita para **cada um dos 5 arquivos**:
# MAGIC
# MAGIC 1. No menu lateral, abra **Catalog**
# MAGIC 2. Navegue até o seu catálogo `workshop_eneva_<seu_nome>` > schema **`bronze`**
# MAGIC 3. Clique em **Create** > **Create table** (ou **Add data** > **Create or modify table**)
# MAGIC 4. **Arraste o arquivo** (ex.: `fato_geracao.csv`) ou clique para selecioná-lo
# MAGIC 5. Confira a prévia:
# MAGIC    - **Catalog**: `workshop_eneva_<seu_nome>`
# MAGIC    - **Schema**: `bronze`
# MAGIC    - **Table name**: use exatamente o nome do arquivo (ex.: `fato_geracao`)
# MAGIC    - **First row contains header**: ativado
# MAGIC    - Confira os tipos de coluna sugeridos (número vs texto)
# MAGIC 6. Clique em **Create table**
# MAGIC
# MAGIC > **Dica:** você pode subir **CSV ou XLSX** — a UI de Create table aceita os dois.
# MAGIC > Para o Excel, a primeira planilha (`Dados`) é usada automaticamente.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tabelas esperadas ao final
# MAGIC
# MAGIC Depois de subir os 5 arquivos, o schema `bronze` deve conter:
# MAGIC
# MAGIC ```
# MAGIC workshop_eneva_<seu_nome>.bronze.fato_geracao
# MAGIC workshop_eneva_<seu_nome>.bronze.dim_usinas
# MAGIC workshop_eneva_<seu_nome>.bronze.dim_unidades_geradoras
# MAGIC workshop_eneva_<seu_nome>.bronze.enriquecimento_municipios
# MAGIC workshop_eneva_<seu_nome>.bronze.enriquecimento_fabricantes
# MAGIC ```
# MAGIC
# MAGIC > Use o notebook **`01b_validacao.py`** para conferir se todas as tabelas foram
# MAGIC > criadas corretamente antes de seguir para o Lab 2.
