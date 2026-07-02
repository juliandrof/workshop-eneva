# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_setup.png" width="100%"/>
# MAGIC
# MAGIC Este notebook gera os dados sintéticos de cadastro do parque gerador Eneva:
# MAGIC - **Usinas** (dimensão): ~15 usinas termelétricas e solares
# MAGIC - **Unidades Geradoras** (dimensão): ~60 unidades (motores, turbinas, inversores)
# MAGIC - **Municípios** (enriquecimento): dados de localização e submercado do SIN
# MAGIC - **Fabricantes** (enriquecimento): tecnologia, eficiência e país de origem
# MAGIC
# MAGIC > A tabela **fato** (`fato_geracao`) NÃO é criada aqui — ela chega em streaming
# MAGIC > no **Lab 1 (Ingestão)** através do gerador de leituras dos medidores.

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
# MAGIC ## 1. Dimensão: Usinas (parque gerador)
# MAGIC
# MAGIC Cada usina possui: fonte de energia, combustível, potência instalada, município e
# MAGIC data de entrada em operação comercial.

# COMMAND ----------

from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType, DateType
)
import datetime

# (id, nome, fonte, combustivel, potencia_instalada_mw, municipio, uf, ano_operacao)
usinas = [
    (1,  "UTE Parnaíba I",     "Termelétrica", "Gás Natural", 675.0,  "Santo Antônio dos Lopes", "MA", 2013),
    (2,  "UTE Parnaíba II",    "Termelétrica", "Gás Natural", 519.0,  "Santo Antônio dos Lopes", "MA", 2016),
    (3,  "UTE Parnaíba III",   "Termelétrica", "Gás Natural", 178.0,  "Santo Antônio dos Lopes", "MA", 2013),
    (4,  "UTE Parnaíba IV",    "Termelétrica", "Gás Natural", 56.0,   "Santo Antônio dos Lopes", "MA", 2016),
    (5,  "UTE Parnaíba V",     "Termelétrica", "Gás Natural", 385.0,  "Santo Antônio dos Lopes", "MA", 2023),
    (6,  "UTE Jaguatirica II", "Termelétrica", "Gás Natural", 141.0,  "Boa Vista",               "RR", 2022),
    (7,  "UTE Itaqui",         "Termelétrica", "Carvão Mineral", 360.0, "São Luís",              "MA", 2013),
    (8,  "UTE Pecém II",       "Termelétrica", "Carvão Mineral", 365.0, "São Gonçalo do Amarante","CE", 2013),
    (9,  "UTE Nova Venécia 2", "Termelétrica", "Gás Natural", 176.0,  "Santo Antônio dos Lopes", "MA", 2010),
    (10, "UFV Futura I",       "Solar",        "Fotovoltaica", 870.0,  "Juazeiro",                "BA", 2023),
    (11, "UFV Futura II",      "Solar",        "Fotovoltaica", 342.0,  "Juazeiro",                "BA", 2024),
    (12, "UTE Fortaleza",      "Termelétrica", "Gás Natural", 327.0,  "Caucaia",                 "CE", 2003),
    (13, "UTE Azulão",         "Termelétrica", "Gás Natural", 295.0,  "Silves",                  "AM", 2022),
    (14, "UFV Serra do Mel",   "Solar",        "Fotovoltaica", 180.0,  "Serra do Mel",           "RN", 2024),
    (15, "UTE Manauara",       "Termelétrica", "Gás Natural", 85.0,   "Manaus",                  "AM", 2019),
]

schema_usinas = StructType([
    StructField("id_usina", IntegerType(), False),
    StructField("nome_usina", StringType(), False),
    StructField("fonte", StringType(), False),
    StructField("combustivel", StringType(), False),
    StructField("potencia_instalada_mw", DoubleType(), False),
    StructField("municipio", StringType(), False),
    StructField("uf", StringType(), False),
    StructField("ano_operacao", IntegerType(), False),
])

df_usinas = spark.createDataFrame(usinas, schema=schema_usinas)
df_usinas.write.mode("overwrite").saveAsTable(f"{catalog_name}.raw.dim_usinas")
print(f"Tabela dim_usinas criada com {df_usinas.count()} registros!")
df_usinas.show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Dimensão: Unidades Geradoras
# MAGIC
# MAGIC Cada usina é composta por várias **unidades geradoras** (motores a gás, turbinas a
# MAGIC vapor ou inversores solares). É no nível da unidade que a geração é medida.

# COMMAND ----------

import random
random.seed(42)

# Configuração de unidades por tipo de usina
# (fabricante, tecnologia, faixa de potencia por unidade)
tecnologia_por_fonte = {
    "Gás Natural": [
        ("Wärtsilä", "Motor de Combustão Interna"),
        ("GE", "Turbina a Gás"),
        ("Siemens Energy", "Turbina a Gás"),
    ],
    "Carvão Mineral": [
        ("Mitsubishi Power", "Turbina a Vapor"),
        ("Doosan", "Turbina a Vapor"),
    ],
    "Fotovoltaica": [
        ("Huawei", "Inversor Solar"),
        ("Sungrow", "Inversor Solar"),
    ],
}

unidades = []
uid = 1
for u in usinas:
    id_usina, nome_usina, fonte, combustivel, pot_total, *_ = u
    # Número de unidades proporcional ao porte da usina
    if combustivel == "Fotovoltaica":
        n_unidades = random.randint(6, 10)
    elif combustivel == "Carvão Mineral":
        n_unidades = random.randint(1, 2)
    else:  # Gás Natural
        n_unidades = random.randint(3, 8)

    fabricante, tecnologia = random.choice(tecnologia_por_fonte[combustivel])
    pot_unidade = round(pot_total / n_unidades, 1)

    for seq in range(1, n_unidades + 1):
        codigo = f"UG-{id_usina:02d}-{seq:02d}"
        # Ano de instalação da unidade (>= ano de operação da usina)
        ano_instalacao = u[7] + random.randint(0, 2)
        unidades.append((
            uid, codigo, id_usina, tecnologia, fabricante,
            pot_unidade, ano_instalacao
        ))
        uid += 1

schema_unidades = StructType([
    StructField("id_unidade", IntegerType(), False),
    StructField("codigo_unidade", StringType(), False),
    StructField("id_usina", IntegerType(), False),
    StructField("tecnologia", StringType(), False),
    StructField("fabricante", StringType(), False),
    StructField("potencia_nominal_mw", DoubleType(), False),
    StructField("ano_instalacao", IntegerType(), False),
])

df_unidades = spark.createDataFrame(unidades, schema=schema_unidades)
df_unidades.write.mode("overwrite").saveAsTable(f"{catalog_name}.raw.dim_unidades_geradoras")
print(f"Tabela dim_unidades_geradoras criada com {df_unidades.count()} registros!")
df_unidades.show(15, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Enriquecimento: Municípios
# MAGIC
# MAGIC Tabela usada no **Lab 2** para enriquecer a dimensão de usinas com **região**,
# MAGIC **submercado do SIN** (Sistema Interligado Nacional) e **população**.

# COMMAND ----------

# (municipio, uf, regiao, submercado_sin, populacao)
municipios = [
    ("Santo Antônio dos Lopes", "MA", "Nordeste", "Norte",          16000),
    ("Boa Vista",               "RR", "Norte",    "Norte",          436000),
    ("São Luís",                "MA", "Nordeste", "Nordeste",       1108000),
    ("São Gonçalo do Amarante", "CE", "Nordeste", "Nordeste",       48000),
    ("Juazeiro",                "BA", "Nordeste", "Nordeste",       218000),
    ("Caucaia",                 "CE", "Nordeste", "Nordeste",       368000),
    ("Silves",                  "AM", "Norte",    "Norte",          9000),
    ("Serra do Mel",            "RN", "Nordeste", "Nordeste",       11000),
    ("Manaus",                  "AM", "Norte",    "Manaus (Isolado)", 2063000),
]

schema_municipios = StructType([
    StructField("municipio", StringType(), False),
    StructField("uf", StringType(), False),
    StructField("regiao", StringType(), False),
    StructField("submercado_sin", StringType(), False),
    StructField("populacao", IntegerType(), False),
])

df_municipios = spark.createDataFrame(municipios, schema=schema_municipios)
df_municipios.write.mode("overwrite").saveAsTable(f"{catalog_name}.raw.enriquecimento_municipios")
print(f"Tabela enriquecimento_municipios criada com {df_municipios.count()} registros!")
df_municipios.show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Enriquecimento: Fabricantes
# MAGIC
# MAGIC Tabela usada no **Lab 2** para enriquecer a dimensão de unidades geradoras com
# MAGIC **país de origem**, **eficiência nominal** e **fator de disponibilidade de referência**.

# COMMAND ----------

# (fabricante, pais_origem, eficiencia_nominal_pct, fator_disponibilidade_ref, ano_fundacao)
fabricantes = [
    ("Wärtsilä",         "Finlândia", 47.5, 0.96, 1834),
    ("GE",               "Estados Unidos", 43.0, 0.94, 1892),
    ("Siemens Energy",   "Alemanha", 44.2, 0.95, 2020),
    ("Mitsubishi Power", "Japão", 41.0, 0.93, 1884),
    ("Doosan",           "Coreia do Sul", 40.0, 0.92, 1896),
    ("Huawei",           "China", 98.6, 0.99, 1987),
    ("Sungrow",          "China", 98.9, 0.99, 1997),
]

schema_fabricantes = StructType([
    StructField("fabricante", StringType(), False),
    StructField("pais_origem", StringType(), False),
    StructField("eficiencia_nominal_pct", DoubleType(), False),
    StructField("fator_disponibilidade_ref", DoubleType(), False),
    StructField("ano_fundacao", IntegerType(), False),
])

df_fabricantes = spark.createDataFrame(fabricantes, schema=schema_fabricantes)
df_fabricantes.write.mode("overwrite").saveAsTable(f"{catalog_name}.raw.enriquecimento_fabricantes")
print(f"Tabela enriquecimento_fabricantes criada com {df_fabricantes.count()} registros!")
df_fabricantes.show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação Final

# COMMAND ----------

print(f"\n{'='*60}")
print(f"DADOS CADASTRAIS GERADOS COM SUCESSO!")
print(f"{'='*60}")
print(f"\nCatálogo: {catalog_name}")
print(f"\nTabelas criadas (schema raw):")
tabelas = [
    "dim_usinas",
    "dim_unidades_geradoras",
    "enriquecimento_municipios",
    "enriquecimento_fabricantes",
]
for tabela in tabelas:
    count = spark.table(f"{catalog_name}.raw.{tabela}").count()
    print(f"  - {catalog_name}.raw.{tabela}: {count} registros")
print(f"\n{'='*60}")
print(f"Próximo passo: Execute o Lab 1 - Ingestão")
print(f"Abra o notebook '01a_gerador_geracao_streaming'")
print(f"{'='*60}")
