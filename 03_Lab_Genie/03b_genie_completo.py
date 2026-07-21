# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab3.png" width="100%"/>
# MAGIC
# MAGIC **Lab 3 — Criando e Curando uma Genie Agent (versão completa / referência)**

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
# MAGIC ## 1. Comentários nas tabelas Gold
# MAGIC
# MAGIC O Genie usa os comentários de tabelas e colunas como contexto. Vamos comentar as
# MAGIC tabelas Gold que a Genie Agent vai usar.

# COMMAND ----------

spark.sql(f"""
    COMMENT ON TABLE {catalog_name}.{schema_name}.gold_geracao_por_fonte IS
    'Geração agregada por fonte de energia (Termelétrica/Solar) e combustível, em MWh'
""")
spark.sql(f"""
    COMMENT ON TABLE {catalog_name}.{schema_name}.gold_geracao_por_usina IS
    'Geração total por usina com ranking e participação percentual na matriz de geração da Eneva'
""")
spark.sql(f"""
    COMMENT ON TABLE {catalog_name}.{schema_name}.gold_geracao_por_submercado IS
    'Geração agregada por submercado do Sistema Interligado Nacional (SIN)'
""")
print("Comentários de tabela adicionados!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Comentários em colunas-chave

# COMMAND ----------

comentarios_colunas = [
    ("gold_geracao_por_usina", "geracao_total_mwh", "Energia total gerada no período, em MWh"),
    ("gold_geracao_por_usina", "disponibilidade_media", "Disponibilidade média da usina (0 a 1)"),
    ("gold_geracao_por_usina", "pct_participacao", "Participação percentual da usina na matriz de geração"),
    ("gold_geracao_por_usina", "ranking", "Posição da usina no ranking de geração (1 = maior)"),
    ("gold_geracao_por_fonte", "geracao_total_mwh", "Energia total gerada pela fonte, em MWh"),
    ("gold_geracao_por_submercado", "geracao_total_mwh", "Energia total gerada no submercado, em MWh"),
]
for tabela, coluna, comentario in comentarios_colunas:
    spark.sql(f"ALTER TABLE {catalog_name}.{schema_name}.{tabela} "
              f"ALTER COLUMN {coluna} COMMENT '{comentario}'")
print("Comentários de coluna adicionados!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Criar a Genie Agent (na UI)
# MAGIC
# MAGIC 1. Vá em **Genie** > **New**
# MAGIC 2. **Título**: `Geração Eneva - <seu_nome>`
# MAGIC 3. **Tabelas** (todas em `workshop_eneva.<seu_nome>`):
# MAGIC    - Dimensões: `dim_usinas`, `dim_unidades_geradoras`
# MAGIC    - Gold: `gold_geracao_por_usina`, `gold_geracao_por_fonte`, `gold_geracao_por_submercado`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Instruções customizadas do Genie

# COMMAND ----------

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
# MAGIC ## 5. Testar o Genie
# MAGIC
# MAGIC Após criar a Genie Agent, teste com perguntas como:
# MAGIC
# MAGIC 1. **"Qual usina gerou mais energia no período?"**
# MAGIC 2. **"Qual a participação de cada fonte na matriz de geração?"**
# MAGIC 3. **"Compare a geração de gás natural com a de carvão mineral"**
# MAGIC 4. **"Qual submercado do SIN concentra mais geração?"**
# MAGIC 5. **"Qual a disponibilidade média das usinas termelétricas?"**
# MAGIC 6. **"Quanto combustível foi consumido no total?"**
# MAGIC 7. **"Quais são as 5 usinas com maior participação na matriz?"**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Próximo passo
# MAGIC
# MAGIC Siga para o **Lab 4 — AI/BI Dashboards** para criar visualizações interativas sobre
# MAGIC as mesmas tabelas Gold.
