# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab3.png" width="100%"/>
# MAGIC
# MAGIC **Lab 3 — Criando e Curando uma Genie Space (exercício com TO-DOs)**
# MAGIC
# MAGIC O **Genie** permite que qualquer pessoa pergunte aos dados em **linguagem natural**
# MAGIC (português!). Neste lab vamos:
# MAGIC 1. Preparar **views** e **comentários** que ajudam o Genie a entender os dados
# MAGIC 2. Criar uma **Genie Space** com as tabelas Gold
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
# MAGIC ## 1. View de apoio para o Genie
# MAGIC
# MAGIC Uma view "achatada" (desnormalizada) facilita a vida do Genie: ele encontra tudo em
# MAGIC um só lugar, sem precisar adivinhar joins.

# COMMAND ----------

# View de geração detalhada por usina/hora (já pronta como exemplo)
spark.sql(f"""
    CREATE OR REPLACE VIEW {catalog_name}.{schema_name}.vw_geracao_detalhada AS
    SELECT
        g.data_hora,
        g.ano,
        g.mes,
        g.dia,
        g.turno,
        u.nome_usina,
        u.fonte,
        u.combustivel,
        u.municipio,
        u.uf,
        u.regiao,
        u.submercado_sin,
        g.geracao_mwh,
        g.consumo_combustivel,
        g.disponibilidade,
        g.temperatura_c
    FROM {catalog_name}.{schema_name}.silver_geracao g
    LEFT JOIN {catalog_name}.{schema_name}.silver_usinas u ON g.id_usina = u.id_usina
""")
print("View vw_geracao_detalhada criada!")

# COMMAND ----------

# TO-DO 1: Crie uma view de desempenho por usina
# ────────────────────────────────────────────────
# Dica: crie {catalog_name}.{schema_name}.vw_desempenho_usinas a partir de
#       gold.gold_geracao_por_usina, selecionando as colunas mais relevantes
#       para negócio: nome_usina, fonte, combustivel, uf, regiao,
#       geracao_total_mwh, disponibilidade_media, ranking, pct_participacao.


# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Comentários nas tabelas (metadados = melhores respostas)
# MAGIC
# MAGIC O Genie usa os **comentários** de tabelas e colunas como contexto. Quanto melhores
# MAGIC os comentários, melhores as respostas.

# COMMAND ----------

# TO-DO 2: Adicione comentários descritivos às tabelas Gold
# ──────────────────────────────────────────────────────────
# Dica: use COMMENT ON TABLE ... IS '...'
# Exemplo pronto (gold_geracao_por_fonte):
spark.sql(f"""
    COMMENT ON TABLE {catalog_name}.{schema_name}.gold_geracao_por_fonte IS
    'Geração agregada por fonte de energia (Termelétrica/Solar) e combustível, em MWh'
""")

# Complete com comentários para:
#   - gold.gold_geracao_por_usina
#   - gold.gold_geracao_por_submercado


# COMMAND ----------

# TO-DO 3: Adicione comentários em COLUNAS-chave
# ────────────────────────────────────────────────
# Dica: ALTER TABLE ... ALTER COLUMN ... COMMENT '...'
# Exemplo:
#   spark.sql(f"ALTER TABLE {catalog_name}.{schema_name}.gold_geracao_por_usina "
#             f"ALTER COLUMN geracao_total_mwh COMMENT 'Energia total gerada no período, em MWh'")
# Comente pelo menos: geracao_total_mwh, disponibilidade_media, pct_participacao


# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Criar a Genie Space (na UI)
# MAGIC
# MAGIC 1. Vá em **Genie** (menu lateral) > **New**
# MAGIC 2. **Título**: `Geração Eneva - <seu_nome>`
# MAGIC 3. **Tabelas** (adicione todas as Gold + views, em `workshop_eneva.<seu_nome>`):
# MAGIC    - `workshop_eneva.<nome>.gold_geracao_por_usina`
# MAGIC    - `workshop_eneva.<nome>.gold_geracao_por_fonte`
# MAGIC    - `workshop_eneva.<nome>.gold_geracao_por_submercado`
# MAGIC    - `workshop_eneva.<nome>.vw_geracao_detalhada`
# MAGIC    - `workshop_eneva.<nome>.vw_desempenho_usinas`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Instruções customizadas do Genie
# MAGIC
# MAGIC Este é o passo mais importante! Execute a célula abaixo e **copie o texto** para o
# MAGIC campo **Instructions** da sua Genie Space.

# COMMAND ----------

# TO-DO 4: Revise e personalize as instruções abaixo
# ────────────────────────────────────────────────────
# Dica: as instruções já vêm prontas — leia, entenda e ajuste se quiser.
#       Boas instruções cobrem: contexto do negócio, glossário/jargão,
#       regras de formatação e exemplos de perguntas.
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
# MAGIC ## 5. Perguntas de exemplo (curadoria)
# MAGIC
# MAGIC Na Genie Space, cadastre algumas perguntas como **Sample Questions** para orientar
# MAGIC os usuários:
# MAGIC
# MAGIC 1. *"Qual usina gerou mais energia?"*
# MAGIC 2. *"Qual a participação de cada fonte na matriz?"*
# MAGIC 3. *"Qual submercado do SIN concentra mais geração?"*
# MAGIC 4. *"Compare gás natural com carvão mineral em geração e disponibilidade"*
# MAGIC 5. *"Quais usinas estão abaixo do fator de capacidade de referência?"*
