# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab3.png" width="100%"/>
# MAGIC
# MAGIC **Lab 3 — Criando e Curando uma Genie Agent (exercício com TO-DOs)**
# MAGIC
# MAGIC O **Genie** permite que qualquer pessoa pergunte aos dados em **linguagem natural**
# MAGIC (português!). Neste lab vamos:
# MAGIC 1. Adicionar **comentários** nas dimensões e tabelas Gold (ajudam o Genie a entender os dados)
# MAGIC 2. Criar uma **Genie Agent** com as dimensões e as tabelas Gold
# MAGIC 3. Escrever **instruções customizadas** (o segredo de um bom Genie)
# MAGIC 4. Testar com perguntas de negócio

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
# MAGIC ## 1. Comentários nas tabelas (metadados = melhores respostas)
# MAGIC
# MAGIC O Genie usa os **comentários** de tabelas e colunas como contexto. Quanto melhores
# MAGIC os comentários, melhores as respostas. Vamos comentar as tabelas Gold que a Genie usará.

# COMMAND ----------

# TO-DO 1: Adicione comentários descritivos às tabelas Gold
# ──────────────────────────────────────────────────────────
# Dica: use COMMENT ON TABLE ... IS '...'
# Exemplo pronto (gold_geracao_por_fonte):
spark.sql(f"""
    COMMENT ON TABLE {catalog_name}.{schema_name}.gold_geracao_por_fonte IS
    'Geração agregada por fonte de energia (Termelétrica/Solar) e combustível, em MWh'
""")

# Complete com comentários para:
#   - gold_geracao_por_usina
#   - gold_geracao_por_submercado


# COMMAND ----------

# TO-DO 2: Adicione comentários em COLUNAS-chave
# ────────────────────────────────────────────────
# Dica: ALTER TABLE ... ALTER COLUMN ... COMMENT '...'
# Exemplo:
#   spark.sql(f"ALTER TABLE {catalog_name}.{schema_name}.gold_geracao_por_usina "
#             f"ALTER COLUMN geracao_total_mwh COMMENT 'Energia total gerada no período, em MWh'")
# Comente pelo menos: geracao_total_mwh, disponibilidade_media, pct_participacao


# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criar a Genie Agent (na UI)
# MAGIC
# MAGIC 1. Vá em **Genie** (menu lateral) > **New**
# MAGIC 2. **Título**: `Geração Eneva - <seu_nome>`
# MAGIC 3. **Tabelas** (adicione, em `workshop_eneva.<seu_nome>`):
# MAGIC    - Dimensões: `dim_usinas`, `dim_unidades_geradoras`
# MAGIC    - Gold: `gold_geracao_por_usina`, `gold_geracao_por_fonte`, `gold_geracao_por_submercado`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Instruções customizadas do Genie
# MAGIC
# MAGIC Este é o passo mais importante! Execute a célula abaixo e **copie o texto** para o
# MAGIC campo **Instructions** da sua Genie Agent.

# COMMAND ----------

# TO-DO 3: Revise e personalize as instruções abaixo
# ────────────────────────────────────────────────────
# Dica: as instruções já vêm prontas — leia, entenda e ajuste se quiser.
#       Boas instruções cobrem: contexto do negócio, glossário/jargão,
#       regras de formatação e exemplos de perguntas.
instrucoes_genie = """
## Contexto do Negócio
Você é um assistente de análise de dados da Eneva, uma das maiores empresas privadas de
geração de energia do Brasil, com foco em geração termelétrica a gás natural e carvão, além
de usinas solares. Os dados representam a geração das usinas do parque gerador da Eneva.

## Glossário (jargão do setor)
- **MWh**: megawatt-hora, unidade de energia gerada no período.
- **Fonte**: tipo de geração — "Termelétrica" ou "Solar".
- **Combustível**: insumo da usina — "Gás Natural", "Carvão Mineral" ou "Fotovoltaica".
- **SIN**: Sistema Interligado Nacional. O Brasil é dividido em submercados
  (Norte, Nordeste, Sudeste/Centro-Oeste, Sul) além de sistemas isolados (ex.: Manaus).
- **Disponibilidade**: fração do tempo em que a unidade esteve apta a gerar (0 a 1).
- **Despacho**: acionamento de uma usina pelo ONS para gerar energia.

## Regras de Resposta
- Sempre expresse energia em **MWh** e potência em **MW**, com separador de milhar.
- Percentuais com uma casa decimal (ex.: 12,5%).
- Quando perguntarem por "maior/melhor usina", use `geracao_total_mwh` como métrica padrão.
- "Participação na matriz" = coluna `pct_participacao` de gold_geracao_por_usina.
- Ao comparar térmica vs solar, deixe claro que são perfis de geração diferentes.

## Exemplos de Perguntas
- "Qual usina gerou mais energia no período?"
- "Qual a participação de cada fonte na matriz de geração?"
- "Compare a geração de Gás Natural com a de Carvão Mineral."
- "Qual submercado do SIN concentra mais geração?"
- "Qual a disponibilidade média das usinas termelétricas?"
- "Quanto combustível foi consumido no total?"
- "Quais são as 5 usinas com maior participação na matriz?"
"""

print("=" * 70)
print("INSTRUÇÕES PARA A GENIE AGENT (copie e cole no campo 'Instructions')")
print("=" * 70)
print(instrucoes_genie)
print("=" * 70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Perguntas de exemplo (curadoria)
# MAGIC
# MAGIC Na Genie Agent, cadastre algumas perguntas como **Sample Questions** para orientar
# MAGIC os usuários:
# MAGIC
# MAGIC 1. *"Qual usina gerou mais energia?"*
# MAGIC 2. *"Qual a participação de cada fonte na matriz?"*
# MAGIC 3. *"Qual submercado do SIN concentra mais geração?"*
# MAGIC 4. *"Compare gás natural com carvão mineral em geração e disponibilidade"*
# MAGIC 5. *"Quais são as 5 usinas com maior participação na matriz?"*
