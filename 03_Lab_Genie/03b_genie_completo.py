# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab3.png" width="100%"/>
# MAGIC
# MAGIC **Lab 3 — Criando e Curando uma Genie Space (versão completa / referência)**

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
# MAGIC ## 1. Views de apoio para o Genie

# COMMAND ----------

spark.sql(f"""
    CREATE OR REPLACE VIEW {catalog_name}.{schema_name}.vw_geracao_detalhada AS
    SELECT
        g.data_hora, g.ano, g.mes, g.dia, g.turno,
        u.nome_usina, u.fonte, u.combustivel, u.municipio, u.uf,
        u.regiao, u.submercado_sin,
        g.geracao_mwh, g.consumo_combustivel, g.disponibilidade, g.temperatura_c
    FROM {catalog_name}.{schema_name}.silver_geracao g
    LEFT JOIN {catalog_name}.{schema_name}.silver_usinas u ON g.id_usina = u.id_usina
""")
print("View vw_geracao_detalhada criada!")

spark.sql(f"""
    CREATE OR REPLACE VIEW {catalog_name}.{schema_name}.vw_desempenho_usinas AS
    SELECT
        nome_usina, fonte, combustivel, uf, regiao, submercado_sin,
        ROUND(geracao_total_mwh, 2) AS geracao_total_mwh,
        ROUND(disponibilidade_media, 4) AS disponibilidade_media,
        ROUND(consumo_combustivel_total, 2) AS consumo_combustivel_total,
        potencia_instalada_mw,
        ranking,
        pct_participacao
    FROM {catalog_name}.{schema_name}.gold_geracao_por_usina
""")
print("View vw_desempenho_usinas criada!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Comentários nas tabelas Gold

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
# MAGIC ## 3. Comentários em colunas-chave

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
# MAGIC ## 4. Criar a Genie Space (na UI)
# MAGIC
# MAGIC 1. Vá em **Genie** > **New**
# MAGIC 2. **Título**: `Geração Eneva - <seu_nome>`
# MAGIC 3. **Tabelas** (todas em `workshop_eneva.<seu_nome>`):
# MAGIC    - `gold_geracao_por_usina`, `gold_geracao_por_fonte`, `gold_geracao_por_submercado`
# MAGIC    - `vw_geracao_detalhada`, `vw_desempenho_usinas`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Instruções customizadas do Genie

# COMMAND ----------

instrucoes_genie = """
## Contexto do Negócio
Você é um assistente de análise de dados da Eneva, uma das maiores empresas privadas de
geração de energia do Brasil, com foco em geração termelétrica a gás natural e carvão, além
de usinas solares. Os dados representam a geração horária das unidades geradoras do parque
gerador da Eneva.

## Glossário (jargão do setor)
- **MWh**: megawatt-hora, unidade de energia gerada no período.
- **Fonte**: tipo de geração — "Termelétrica" ou "Solar".
- **Combustível**: insumo da usina — "Gás Natural", "Carvão Mineral" ou "Fotovoltaica".
- **SIN**: Sistema Interligado Nacional. O Brasil é dividido em submercados
  (Norte, Nordeste, Sudeste/Centro-Oeste, Sul) além de sistemas isolados (ex.: Manaus).
- **Fator de capacidade**: razão entre geração média e potência nominal (0 a 1).
- **Disponibilidade**: fração do tempo em que a unidade esteve apta a gerar (0 a 1).
- **Despacho**: acionamento de uma usina pelo ONS para gerar energia.

## Regras de Resposta
- Sempre expresse energia em **MWh** e potência em **MW**, com separador de milhar.
- Percentuais com uma casa decimal (ex.: 12,5%).
- Quando perguntarem por "maior/melhor usina", use `geracao_total_mwh` como métrica padrão.
- "Participação na matriz" = coluna `pct_participacao` de gold_geracao_por_usina.
- Usinas solares só geram durante o dia — geração noturna zero é esperada, não é erro.
- Ao comparar térmica vs solar, deixe claro que são perfis de geração diferentes.

## Exemplos de Perguntas
- "Qual usina gerou mais energia no período?"
- "Qual a participação de cada fonte na matriz de geração?"
- "Compare a geração de Gás Natural com a de Carvão Mineral."
- "Qual submercado do SIN concentra mais geração?"
- "Qual a disponibilidade média das usinas termelétricas?"
- "Quanto gás natural foi consumido no total?"
- "Quais usinas têm fator de capacidade abaixo da referência do fabricante?"
- "Como varia a geração solar ao longo dos turnos do dia?"
"""

print("=" * 70)
print("INSTRUÇÕES PARA A GENIE SPACE (copie e cole no campo 'Instructions')")
print("=" * 70)
print(instrucoes_genie)
print("=" * 70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Testar o Genie
# MAGIC
# MAGIC Após criar a Genie Space, teste com perguntas como:
# MAGIC
# MAGIC 1. **"Qual usina gerou mais energia no período?"**
# MAGIC 2. **"Qual a participação de cada fonte na matriz de geração?"**
# MAGIC 3. **"Compare a geração de gás natural com a de carvão mineral"**
# MAGIC 4. **"Qual submercado do SIN concentra mais geração?"**
# MAGIC 5. **"Qual a disponibilidade média das usinas termelétricas?"**
# MAGIC 6. **"Quanto gás natural foi consumido no total?"**
# MAGIC 7. **"Como varia a geração solar ao longo dos turnos do dia?"**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Próximo passo
# MAGIC
# MAGIC Siga para o **Lab 4 — AI/BI Dashboards** para criar visualizações interativas sobre
# MAGIC as mesmas tabelas Gold.
