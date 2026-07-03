#!/usr/bin/env python3
"""
Gera os dados sintéticos do Workshop Eneva em CSV e XLSX.

Produz 5 arquivos (1 fato + 2 dimensões + 2 de enriquecimento), cada um em .csv e
.xlsx, prontos para upload manual no Databricks (Catalog > Create table > Upload files).

Não depende de bibliotecas externas: o XLSX é escrito com um mini-writer baseado
apenas na biblioteca padrão (zipfile + xml).

Uso:  python3 gerar_dados.py
"""

import csv
import os
import random
import datetime
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(42)


# ─────────────────────────────────────────────────────────────────────────────
# Mini-writer de XLSX (somente biblioteca padrão)
# ─────────────────────────────────────────────────────────────────────────────

def _col_ref(idx):
    """0 -> A, 1 -> B, ... 26 -> AA."""
    s = ""
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        s = chr(65 + rem) + s
    return s


def write_xlsx(path, header, rows):
    """Escreve um .xlsx de uma única planilha. Números viram células numéricas."""
    def cell(c, r, value):
        ref = f"{_col_ref(c)}{r}"
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, (int, float)):
            return f'<c r="{ref}"><v>{value}</v></c>'
        return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(value))}</t></is></c>'

    sheet_rows = []
    # header (linha 1)
    cells = "".join(cell(c, 1, h) for c, h in enumerate(header))
    sheet_rows.append(f'<row r="1">{cells}</row>')
    # dados
    for ri, row in enumerate(rows, start=2):
        cells = "".join(cell(c, ri, v) for c, v in enumerate(row))
        sheet_rows.append(f'<row r="{ri}">{cells}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Dados" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def salvar(nome, header, rows):
    csv_path = os.path.join(HERE, f"{nome}.csv")
    xlsx_path = os.path.join(HERE, f"{nome}.xlsx")
    write_csv(csv_path, header, rows)
    write_xlsx(xlsx_path, header, rows)
    print(f"  {nome}: {len(rows)} linhas  ->  {nome}.csv + {nome}.xlsx")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Dimensão: Usinas
# ─────────────────────────────────────────────────────────────────────────────

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
HDR_USINAS = ["id_usina", "nome_usina", "fonte", "combustivel",
              "potencia_instalada_mw", "municipio", "uf", "ano_operacao"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Dimensão: Unidades Geradoras
# ─────────────────────────────────────────────────────────────────────────────

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
    id_usina, nome_usina, fonte, combustivel, pot_total = u[0], u[1], u[2], u[3], u[4]
    if combustivel == "Fotovoltaica":
        n_unidades = random.randint(6, 10)
    elif combustivel == "Carvão Mineral":
        n_unidades = random.randint(1, 2)
    else:
        n_unidades = random.randint(3, 8)
    fabricante, tecnologia = random.choice(tecnologia_por_fonte[combustivel])
    pot_unidade = round(pot_total / n_unidades, 1)
    for seq in range(1, n_unidades + 1):
        codigo = f"UG-{id_usina:02d}-{seq:02d}"
        ano_instalacao = u[7] + random.randint(0, 2)
        unidades.append((uid, codigo, id_usina, tecnologia, fabricante,
                         pot_unidade, ano_instalacao))
        uid += 1
HDR_UNIDADES = ["id_unidade", "codigo_unidade", "id_usina", "tecnologia",
                "fabricante", "potencia_nominal_mw", "ano_instalacao"]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Enriquecimento: Municípios
# ─────────────────────────────────────────────────────────────────────────────

municipios = [
    ("Santo Antônio dos Lopes", "MA", "Nordeste", "Norte",             16000),
    ("Boa Vista",               "RR", "Norte",    "Norte",             436000),
    ("São Luís",                "MA", "Nordeste", "Nordeste",          1108000),
    ("São Gonçalo do Amarante", "CE", "Nordeste", "Nordeste",          48000),
    ("Juazeiro",                "BA", "Nordeste", "Nordeste",          218000),
    ("Caucaia",                 "CE", "Nordeste", "Nordeste",          368000),
    ("Silves",                  "AM", "Norte",    "Norte",             9000),
    ("Serra do Mel",            "RN", "Nordeste", "Nordeste",          11000),
    ("Manaus",                  "AM", "Norte",    "Manaus (Isolado)",  2063000),
]
HDR_MUNICIPIOS = ["municipio", "uf", "regiao", "submercado_sin", "populacao"]


# ─────────────────────────────────────────────────────────────────────────────
# 4. Enriquecimento: Fabricantes
# ─────────────────────────────────────────────────────────────────────────────

fabricantes = [
    ("Wärtsilä",         "Finlândia",      47.5, 0.96, 1834),
    ("GE",               "Estados Unidos", 43.0, 0.94, 1892),
    ("Siemens Energy",   "Alemanha",       44.2, 0.95, 2020),
    ("Mitsubishi Power", "Japão",          41.0, 0.93, 1884),
    ("Doosan",           "Coreia do Sul",  40.0, 0.92, 1896),
    ("Huawei",           "China",          98.6, 0.99, 1987),
    ("Sungrow",          "China",          98.9, 0.99, 1997),
]
HDR_FABRICANTES = ["fabricante", "pais_origem", "eficiencia_nominal_pct",
                   "fator_disponibilidade_ref", "ano_fundacao"]


# ─────────────────────────────────────────────────────────────────────────────
# 5. FATO: Geração horária (tabela plana)
# ─────────────────────────────────────────────────────────────────────────────

HORAS = 72   # 3 dias de leituras horárias
HDR_FATO = ["id_leitura", "id_unidade", "id_usina", "data_hora",
            "geracao_mwh", "consumo_combustivel", "disponibilidade", "temperatura_c"]

fato = []
leitura_id = 1
# mapa auxiliar: id_unidade -> (id_usina, potencia, fonte, combustivel)
usina_info = {u[0]: (u[2], u[3]) for u in usinas}  # id_usina -> (fonte, combustivel)
hora_base = datetime.datetime(2025, 6, 1, 0, 0, 0)

for h in range(HORAS):
    timestamp = hora_base + datetime.timedelta(hours=h)
    hora = timestamp.hour
    for un in unidades:
        id_unidade, _, id_usina, _, _, pot_nominal, _ = un
        fonte, combustivel = usina_info[id_usina]

        if fonte == "Solar":
            if 6 <= hora <= 18:
                fc = max(0.0, 1.0 - abs(hora - 12) / 7.0) * random.uniform(0.75, 0.98)
            else:
                fc = 0.0
        else:
            fc = random.uniform(0.70, 0.97)

        geracao_mwh = round(pot_nominal * fc, 3)

        if fonte == "Solar":
            consumo = 0.0
        elif combustivel == "Gás Natural":
            consumo = round(geracao_mwh * random.uniform(0.17, 0.21), 3)
        else:
            consumo = round(geracao_mwh * random.uniform(0.38, 0.45), 3)

        disponibilidade = round(random.uniform(0.90, 1.0), 4)
        temperatura = round(random.uniform(35, 95), 1) if fonte != "Solar" else round(random.uniform(25, 60), 1)

        fato.append((leitura_id, id_unidade, id_usina,
                     timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                     geracao_mwh, consumo, disponibilidade, temperatura))
        leitura_id += 1


def main():
    print("Gerando dados do Workshop Eneva (CSV + XLSX)...")
    salvar("dim_usinas", HDR_USINAS, usinas)
    salvar("dim_unidades_geradoras", HDR_UNIDADES, unidades)
    salvar("enriquecimento_municipios", HDR_MUNICIPIOS, municipios)
    salvar("enriquecimento_fabricantes", HDR_FABRICANTES, fabricantes)
    salvar("fato_geracao", HDR_FATO, fato)
    print(f"\nConcluído! {len(fato)} leituras de geração ({HORAS}h x {len(unidades)} unidades).")
    print(f"Arquivos salvos em: {HERE}")


if __name__ == "__main__":
    main()
