# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_lab1.png" width="100%"/>
# MAGIC
# MAGIC **Gerador de dados de geração em streaming**
# MAGIC
# MAGIC Este notebook simula os medidores das unidades geradoras: a cada intervalo, grava
# MAGIC um arquivo JSON no Volume com as leituras horárias de geração (MWh), consumo de
# MAGIC combustível, disponibilidade e temperatura do equipamento.
# MAGIC
# MAGIC > **Deixe este notebook rodando** durante o Lab 1 — ele alimenta o pipeline de ingestão.

# COMMAND ----------

dbutils.widgets.text("nome_participante", "", "Seu Nome (sem espaços/acentos)")
dbutils.widgets.text("num_ciclos", "30", "Número de ciclos de geração")
dbutils.widgets.text("intervalo_segundos", "20", "Intervalo entre ciclos (segundos)")

# COMMAND ----------

nome = dbutils.widgets.get("nome_participante").strip().lower().replace(" ", "_")
assert nome != "", "Por favor, preencha seu nome no widget acima!"
catalog_name = f"workshop_eneva_{nome}"
volume_path = f"/Volumes/{catalog_name}/raw/geracao_json"
print(f"Catálogo: {catalog_name}")
print(f"Volume de destino: {volume_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Carregar unidades geradoras cadastradas

# COMMAND ----------

unidades = (
    spark.table(f"{catalog_name}.raw.dim_unidades_geradoras")
    .join(spark.table(f"{catalog_name}.raw.dim_usinas"), "id_usina", "inner")
    .select(
        "id_unidade", "id_usina", "potencia_nominal_mw",
        "fonte", "combustivel"
    )
    .collect()
)
print(f"{len(unidades)} unidades geradoras carregadas para simulação.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Loop de geração de leituras
# MAGIC
# MAGIC Cada ciclo simula 1 hora de operação e grava 1 arquivo JSON por usina, contendo as
# MAGIC leituras de todas as suas unidades geradoras.

# COMMAND ----------

import json
import random
import time
import datetime

random.seed()

num_ciclos = int(dbutils.widgets.get("num_ciclos"))
intervalo = int(dbutils.widgets.get("intervalo_segundos"))

# Agrupar unidades por usina
usinas_map = {}
for u in unidades:
    usinas_map.setdefault(u["id_usina"], []).append(u)

# Data/hora inicial da simulação (retroage algumas horas para gerar histórico)
hora_base = datetime.datetime.now() - datetime.timedelta(hours=num_ciclos)
leitura_id = int(time.time() * 100)

for ciclo in range(num_ciclos):
    timestamp = hora_base + datetime.timedelta(hours=ciclo)
    hora = timestamp.hour

    for id_usina, lista_unidades in usinas_map.items():
        leituras = []
        for u in lista_unidades:
            fonte = u["fonte"]
            pot_nominal = u["potencia_nominal_mw"]

            # Fator de capacidade depende da fonte e da hora do dia
            if fonte == "Solar":
                # Geração solar só durante o dia, com pico ao meio-dia
                if 6 <= hora <= 18:
                    fc = max(0.0, 1.0 - abs(hora - 12) / 7.0) * random.uniform(0.75, 0.98)
                else:
                    fc = 0.0
            else:
                # Térmica: fator de capacidade alto e mais estável
                fc = random.uniform(0.70, 0.97)

            geracao_mwh = round(pot_nominal * fc, 3)

            # Consumo de combustível (só térmicas) — proporcional à geração
            if fonte == "Solar":
                consumo_combustivel = 0.0
            elif u["combustivel"] == "Gás Natural":
                consumo_combustivel = round(geracao_mwh * random.uniform(0.17, 0.21), 3)  # mil m³
            else:  # Carvão
                consumo_combustivel = round(geracao_mwh * random.uniform(0.38, 0.45), 3)  # toneladas

            # Disponibilidade e temperatura do equipamento
            disponibilidade = round(random.uniform(0.90, 1.0), 4)
            temperatura_c = round(random.uniform(35, 95), 1) if fonte != "Solar" else round(random.uniform(25, 60), 1)

            leitura_id += 1
            leituras.append({
                "id_leitura": leitura_id,
                "id_unidade": u["id_unidade"],
                "id_usina": id_usina,
                "geracao_mwh": geracao_mwh,
                "consumo_combustivel": consumo_combustivel,
                "disponibilidade": disponibilidade,
                "temperatura_c": temperatura_c,
            })

        registro = {
            "id_usina": id_usina,
            "data_hora": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "leituras": leituras,
        }

        arquivo = f"{volume_path}/usina_{id_usina:02d}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        dbutils.fs.put(arquivo, json.dumps(registro), overwrite=True)

    print(f"Ciclo {ciclo+1}/{num_ciclos} — {timestamp.strftime('%Y-%m-%d %H:%M')} — "
          f"{len(usinas_map)} usinas gravadas")
    if ciclo < num_ciclos - 1:
        time.sleep(intervalo)

print(f"\n{'='*60}")
print(f"GERAÇÃO CONCLUÍDA! {num_ciclos} ciclos gravados em {volume_path}")
print(f"{'='*60}")
