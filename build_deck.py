#!/usr/bin/env python3
"""
Build the slide deck for Workshop Hands-On Databricks — Eneva.

Creates a fresh Google Slides presentation (via the Slides API) and builds all
slides programmatically on BLANK layouts, drawing headers/cards/code blocks with
the Databricks palette + an energy-green primary color.

Requires: gcloud application-default credentials (ADC).
Run:  python3 build_deck.py
"""

import json
import subprocess
import uuid

PRES_ID = None  # set after creation

# Google Slides' native widescreen page is 10 x 5.625" (16:9). We author the
# layout in the more spacious 13.33 x 7.50" (PowerPoint 16:9) coordinate system
# and scale everything down uniformly so it maps exactly onto the real canvas.
SLIDE_W = 13.33
SLIDE_H = 7.50
INCH = 914400
SCALE = 10.0 / 13.333  # 0.75 — maps 13.33" layout onto the 10" page

# Palette — energy green primary + Databricks accents
GREEN = {"red": 0.043, "green": 0.239, "blue": 0.180}       # deep energy green (primary)
DARK_GREEN = {"red": 0.027, "green": 0.149, "blue": 0.114}
RED = {"red": 1.0, "green": 0.212, "blue": 0.129}
ORANGE = {"red": 1.0, "green": 0.439, "blue": 0.200}
YELLOW = {"red": 0.984, "green": 0.702, "blue": 0.0}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
LIGHT_GRAY = {"red": 0.965, "green": 0.969, "blue": 0.967}
MEDIUM_GRAY = {"red": 0.6, "green": 0.6, "blue": 0.6}
DARK_GRAY = {"red": 0.2, "green": 0.2, "blue": 0.2}
CODE_BG = {"red": 0.12, "green": 0.15, "blue": 0.13}
GOOD_GREEN = {"red": 0.18, "green": 0.7, "blue": 0.4}
LIGHT_GREEN = {"red": 0.9, "green": 0.97, "blue": 0.93}
LIGHT_RED = {"red": 1.0, "green": 0.92, "blue": 0.9}
TEAL = {"red": 0.0, "green": 0.514, "blue": 0.561}
PURPLE = {"red": 0.369, "green": 0.208, "blue": 0.694}

RAW = "https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images"


def get_token():
    return subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True, text=True
    ).stdout.strip()


def api_call(method, url, data=None):
    token = get_token()
    cmd = ["curl", "-s", "-X", method, url,
           "-H", f"Authorization: Bearer {token}",
           "-H", "Content-Type: application/json",
           "-H", "x-goog-user-project: gcp-dev-field-eng-aiapiquota"]
    if data:
        cmd += ["-d", json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        resp = json.loads(result.stdout)
        if "error" in resp:
            print(f"  API Error: {resp['error'].get('message', resp['error'])}")
            raise Exception(resp['error'].get('message', 'Unknown'))
        return resp
    except json.JSONDecodeError:
        return {}


def batch_update(requests):
    url = f"https://slides.googleapis.com/v1/presentations/{PRES_ID}:batchUpdate"
    return api_call("POST", url, {"requests": requests})


def uid(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def emu(inches):
    return int(inches * SCALE * INCH)


# ---- Low-level helpers ----

def mk_shape(sid, oid, stype, x, y, w, h):
    return {"createShape": {"objectId": oid, "shapeType": stype,
        "elementProperties": {"pageObjectId": sid,
            "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": emu(x), "translateY": emu(y), "unit": "EMU"}}}}


def mk_fill(oid, color):
    return {"updateShapeProperties": {"objectId": oid,
        "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": color}}},
            "outline": {"propertyState": "NOT_RENDERED"}}, "fields": "shapeBackgroundFill,outline"}}


def mk_text(oid, content, idx=0, cell=None):
    r = {"insertText": {"objectId": oid, "text": content, "insertionIndex": idx}}
    if cell:
        r["insertText"]["cellLocation"] = cell
    return r


def mk_style(oid, bold=False, sz=12, color=None, font="Inter", italic=False, rt="ALL", s=None, e=None):
    tr = {"type": rt}
    if s is not None:
        tr["startIndex"] = s
    if e is not None:
        tr["endIndex"] = e
    st = {"bold": bold, "italic": italic, "fontSize": {"magnitude": round(sz * SCALE, 1), "unit": "PT"},
          "fontFamily": font, "weightedFontFamily": {"fontFamily": font, "weight": 700 if bold else 400}}
    flds = "bold,italic,fontSize,fontFamily,weightedFontFamily"
    if color:
        st["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}
        flds += ",foregroundColor"
    return {"updateTextStyle": {"objectId": oid, "textRange": tr, "style": st, "fields": flds}}


def mk_para(oid, align="START", sp=150, above=0, below=0):
    return {"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
        "style": {"alignment": align, "lineSpacing": sp,
            "spaceAbove": {"magnitude": above, "unit": "PT"},
            "spaceBelow": {"magnitude": below, "unit": "PT"}},
        "fields": "alignment,lineSpacing,spaceAbove,spaceBelow"}}


def mk_image(sid, oid, url, x, y, w, h):
    return {"createImage": {"objectId": oid, "url": url,
        "elementProperties": {"pageObjectId": sid,
            "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": emu(x), "translateY": emu(y), "unit": "EMU"}}}}


def mk_table(sid, oid, rows, cols, x, y, w, h):
    return {"createTable": {"objectId": oid, "rows": rows, "columns": cols,
        "elementProperties": {"pageObjectId": sid,
            "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": emu(x), "translateY": emu(y), "unit": "EMU"}}}}


# ---- Composite helpers ----

def code_block(sid, x, y, w, h, code, label=None, label_color=None):
    reqs = []
    if label:
        lb = uid("lb")
        reqs += [mk_shape(sid, lb, "RECTANGLE", x, y - 0.4, w, 0.38), mk_fill(lb, label_color or GREEN)]
        lt = uid("lt")
        reqs += [mk_shape(sid, lt, "TEXT_BOX", x + 0.12, y - 0.38, w - 0.24, 0.34),
                 mk_text(lt, label), mk_style(lt, bold=True, sz=11, color=WHITE)]
    bg = uid("bg")
    reqs += [mk_shape(sid, bg, "ROUND_RECTANGLE", x, y, w, h), mk_fill(bg, CODE_BG)]
    ct = uid("ct")
    reqs += [mk_shape(sid, ct, "TEXT_BOX", x + 0.15, y + 0.1, w - 0.3, h - 0.2),
             mk_text(ct, code),
             mk_style(ct, sz=9, color={"red": 0.85, "green": 0.95, "blue": 0.88}, font="Roboto Mono"),
             mk_para(ct, "START", 130)]
    return reqs


def vs_badge(sid, x, y):
    reqs = []
    bg = uid("vs")
    reqs += [mk_shape(sid, bg, "ELLIPSE", x, y, 0.6, 0.6), mk_fill(bg, ORANGE)]
    t = uid("vt")
    reqs += [mk_shape(sid, t, "TEXT_BOX", x, y + 0.1, 0.6, 0.4),
             mk_text(t, "VS"), mk_style(t, bold=True, sz=14, color=WHITE), mk_para(t, "CENTER")]
    return reqs


def benefit_card(sid, x, y, w, h, title, desc, accent):
    reqs = []
    c = uid("bc")
    reqs += [mk_shape(sid, c, "ROUND_RECTANGLE", x, y, w, h), mk_fill(c, LIGHT_GRAY)]
    b = uid("bb")
    reqs += [mk_shape(sid, b, "RECTANGLE", x, y, w, 0.07), mk_fill(b, accent)]
    t = uid("bt")
    reqs += [mk_shape(sid, t, "TEXT_BOX", x + 0.15, y + 0.2, w - 0.3, 0.55),
             mk_text(t, title), mk_style(t, bold=True, sz=13, color=GREEN), mk_para(t, "START", 120)]
    d = uid("bd")
    reqs += [mk_shape(sid, d, "TEXT_BOX", x + 0.15, y + 0.75, w - 0.3, h - 0.95),
             mk_text(d, desc), mk_style(d, sz=10, color=DARK_GRAY), mk_para(d, "START", 140)]
    return reqs


def comparison_column(sid, x, y, w, h, title, items, is_good, header_color):
    reqs = []
    bg_color = LIGHT_GREEN if is_good else LIGHT_RED
    marker = "✓" if is_good else "✗"
    marker_color = GOOD_GREEN if is_good else RED
    bg = uid("cbg")
    reqs += [mk_shape(sid, bg, "ROUND_RECTANGLE", x, y, w, h), mk_fill(bg, bg_color)]
    bar = uid("cbar")
    reqs += [mk_shape(sid, bar, "RECTANGLE", x, y, w, 0.07), mk_fill(bar, header_color)]
    tt = uid("ct")
    reqs += [mk_shape(sid, tt, "TEXT_BOX", x + 0.2, y + 0.15, w - 0.4, 0.45),
             mk_text(tt, title), mk_style(tt, bold=True, sz=16, color=header_color)]
    for i, (item_title, item_desc) in enumerate(items):
        iy = y + 0.7 + i * 0.85
        m = uid("m")
        reqs += [mk_shape(sid, m, "TEXT_BOX", x + 0.2, iy, 0.35, 0.3),
                 mk_text(m, marker), mk_style(m, bold=True, sz=16, color=marker_color)]
        it = uid("it")
        reqs += [mk_shape(sid, it, "TEXT_BOX", x + 0.55, iy, 2.0, 0.3),
                 mk_text(it, item_title), mk_style(it, bold=True, sz=11, color=DARK_GRAY)]
        id_ = uid("id")
        reqs += [mk_shape(sid, id_, "TEXT_BOX", x + 0.55, iy + 0.28, w - 0.75, 0.5),
                 mk_text(id_, item_desc), mk_style(id_, sz=9, color=DARK_GRAY), mk_para(id_, "START", 125)]
    return reqs


def content_slide(sid, title, subtitle=""):
    reqs = []
    tb = uid("tb")
    reqs += [mk_shape(sid, tb, "RECTANGLE", 0, 0, SLIDE_W, 1.1), mk_fill(tb, GREEN)]
    tt = uid("tt")
    reqs += [mk_shape(sid, tt, "TEXT_BOX", 0.7, 0.2, SLIDE_W - 1.4, 0.65),
             mk_text(tt, title), mk_style(tt, bold=True, sz=24, color=WHITE)]
    if subtitle:
        st = uid("st")
        reqs += [mk_shape(sid, st, "TEXT_BOX", 0.7, 0.72, SLIDE_W - 1.4, 0.32),
                 mk_text(st, subtitle), mk_style(st, sz=12, color=ORANGE)]
    ac = uid("ac")
    reqs += [mk_shape(sid, ac, "RECTANGLE", 0, 1.1, SLIDE_W, 0.05), mk_fill(ac, ORANGE)]
    return reqs


# ---- Individual slide builders ----

def build_agenda(sid):
    reqs = content_slide(sid, "Agenda", "Workshop Hands-On Databricks — Eneva")
    tid = uid("tbl")
    reqs.append(mk_table(sid, tid, 8, 3, 0.8, 1.5, 11.7, 5.4))
    items = [
        ("00", "15 min", "Setup — Catálogo Unity Catalog e dados sintéticos"),
        ("—", "15 min", "Teoria — Data + AI Platform & Arquitetura Medallion"),
        ("01", "30 min", "Lab 1 — Ingestão de Dados (upload CSV/XLSX)"),
        ("02", "40 min", "Lab 2 — Transformação com LakeFlow Designer"),
        ("03", "30 min", "Lab 3 — Genie Space (linguagem natural)"),
        ("04", "30 min", "Lab 4 — AI/BI Dashboards"),
        ("—", "15 min", "Resumo & Encerramento"),
    ]
    header = ["Lab", "Duração", "Tópico"]
    for c, v in enumerate(header):
        reqs.append(mk_text(tid, v, 0, {"rowIndex": 0, "columnIndex": c}))
        reqs.append({"updateTableCellProperties": {"objectId": tid,
            "tableRange": {"location": {"rowIndex": 0, "columnIndex": c}, "rowSpan": 1, "columnSpan": 1},
            "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": GREEN}}}},
            "fields": "tableCellBackgroundFill"}})
        reqs.append({"updateTextStyle": {"objectId": tid,
            "cellLocation": {"rowIndex": 0, "columnIndex": c}, "textRange": {"type": "ALL"},
            "style": {"bold": True, "fontSize": {"magnitude": round(13 * SCALE, 1), "unit": "PT"}, "fontFamily": "Inter",
                "weightedFontFamily": {"fontFamily": "Inter", "weight": 700},
                "foregroundColor": {"opaqueColor": {"rgbColor": WHITE}}},
            "fields": "bold,fontSize,fontFamily,weightedFontFamily,foregroundColor"}})
    for i, (lab, dur, desc) in enumerate(items):
        r = i + 1
        is_lab = lab.isdigit() and lab != "00"
        bg = {"red": 0.92, "green": 0.96, "blue": 0.94} if is_lab else LIGHT_GRAY
        for c, v in enumerate([lab, dur, desc]):
            reqs.append(mk_text(tid, v, 0, {"rowIndex": r, "columnIndex": c}))
            reqs.append({"updateTableCellProperties": {"objectId": tid,
                "tableRange": {"location": {"rowIndex": r, "columnIndex": c}, "rowSpan": 1, "columnSpan": 1},
                "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": bg}}}},
                "fields": "tableCellBackgroundFill"}})
            reqs.append({"updateTextStyle": {"objectId": tid,
                "cellLocation": {"rowIndex": r, "columnIndex": c}, "textRange": {"type": "ALL"},
                "style": {"bold": c < 2, "fontSize": {"magnitude": round(12 * SCALE, 1), "unit": "PT"}, "fontFamily": "Inter",
                    "weightedFontFamily": {"fontFamily": "Inter", "weight": 700 if c < 2 else 400},
                    "foregroundColor": {"opaqueColor": {"rgbColor": GREEN if c < 2 else DARK_GRAY}}},
                "fields": "bold,fontSize,fontFamily,weightedFontFamily,foregroundColor"}})
    return reqs


def build_setup(sid):
    reqs = content_slide(sid, "Setup Inicial  (15 min)")
    steps = [
        ("1", "Widget", "Preencha nome_participante\n(sem espaços, minúsculo)"),
        ("2", "Schema", "Execute 00_configuracao_catalogo\nCatálogo workshop_eneva + seu schema"),
        ("3", "Dados", "Baixe os arquivos da pasta dados/\n5 tabelas em CSV e XLSX"),
        ("4", "Pronto", "No Lab 1 você fará o upload\nmanual para a camada Bronze"),
    ]
    for i, (num, title, desc) in enumerate(steps):
        x = 0.4 + i * 3.15
        c = uid("c"); reqs += [mk_shape(sid, c, "ROUND_RECTANGLE", x, 1.6, 2.9, 4.4), mk_fill(c, LIGHT_GRAY)]
        nb = uid("nb"); reqs += [mk_shape(sid, nb, "ELLIPSE", x + 0.95, 1.9, 0.9, 0.9), mk_fill(nb, ORANGE)]
        nt = uid("nt"); reqs += [mk_shape(sid, nt, "TEXT_BOX", x + 0.95, 2.0, 0.9, 0.7),
                                  mk_text(nt, num), mk_style(nt, bold=True, sz=28, color=WHITE), mk_para(nt, "CENTER")]
        tt = uid("tt"); reqs += [mk_shape(sid, tt, "TEXT_BOX", x + 0.15, 3.1, 2.6, 0.5),
                                  mk_text(tt, title), mk_style(tt, bold=True, sz=18, color=GREEN), mk_para(tt, "CENTER")]
        dt = uid("dt"); reqs += [mk_shape(sid, dt, "TEXT_BOX", x + 0.15, 3.7, 2.6, 1.8),
                                  mk_text(dt, desc), mk_style(dt, sz=12, color=DARK_GRAY), mk_para(dt, "CENTER", 150)]
    return reqs


def build_architecture(sid):
    reqs = content_slide(sid, "Arquitetura Medallion")
    layers = [
        ("Arquivos\nCSV/XLSX", 0.3, TEAL, 2.0),
        ("Bronze", 2.9, {"red": 0.8, "green": 0.5, "blue": 0.2}, 2.0),
        ("Silver", 5.5, {"red": 0.22, "green": 0.56, "blue": 0.24}, 2.0),
        ("Gold", 8.1, YELLOW, 2.0),
        ("Genie\n+ AI/BI", 10.7, PURPLE, 2.0),
    ]
    for label, x, color, w in layers:
        b = uid("b"); reqs += [mk_shape(sid, b, "ROUND_RECTANGLE", x, 2.2, w, 2.0), mk_fill(b, color)]
        t = uid("t"); reqs += [mk_shape(sid, t, "TEXT_BOX", x, 2.5, w, 1.4),
                                mk_text(t, label), mk_style(t, bold=True, sz=18, color=WHITE), mk_para(t, "CENTER")]
    for i in range(4):
        a = uid("a"); ax = 2.3 + i * 2.6
        reqs += [mk_shape(sid, a, "RIGHT_ARROW", ax, 2.8, 0.7, 0.7), mk_fill(a, MEDIUM_GRAY)]
    descs = [("Dados prontos\n(pasta dados/)", 0.3), ("Upload manual\n(Create table)", 2.9),
             ("Transformação\nLakeFlow Designer", 5.5), ("Agregações\nprontas p/ BI", 8.1),
             ("Linguagem natural\n+ Dashboards", 10.7)]
    for d, x in descs:
        dt = uid("d"); reqs += [mk_shape(sid, dt, "TEXT_BOX", x, 4.5, 2.0, 0.9),
                                 mk_text(dt, d), mk_style(dt, sz=11, color=DARK_GRAY), mk_para(dt, "CENTER", 135)]
    ft = uid("ft"); reqs += [mk_shape(sid, ft, "TEXT_BOX", 0.5, 5.8, 12.3, 0.5),
                              mk_text(ft, "LakeFlow  •  Unity Catalog  •  Delta Lake  •  Serverless"),
                              mk_style(ft, bold=False, sz=13, color=GREEN), mk_para(ft, "CENTER")]
    return reqs


def build_teoria_plataforma(sid):
    reqs = content_slide(sid, "Data + AI Platform", "Uma plataforma única, do dado bruto à decisão")
    cards = [
        ("Ingestão", "Traga planilhas e extrações\n(CSV/Excel) com upload\nmanual no Catalog\n\n• Create table\n• Inferência de schema\n• Sem código", TEAL),
        ("Transformação", "Modele os dados de forma\nvisual com o LakeFlow\nDesigner (low-code)\n\n• Silver / Gold\n• Data Quality\n• Linhagem automática", ORANGE),
        ("Consumo & IA", "Consuma em linguagem\nnatural (Genie) e crie\nDashboards AI/BI\n\n• Self-service\n• Governança única\n• Zero cópia de dados", PURPLE),
    ]
    for i, (t, d, c) in enumerate(cards):
        x = 0.3 + i * 4.25
        reqs += benefit_card(sid, x, 1.5, 3.95, 4.9, t, d, c)
    nt = uid("nt"); reqs += [mk_shape(sid, nt, "TEXT_BOX", 0.5, 6.6, 12.3, 0.35),
                              mk_text(nt, "Tudo governado pelo Unity Catalog — um único ponto de acesso, segurança e linhagem"),
                              mk_style(nt, sz=11, color=MEDIUM_GRAY, italic=True), mk_para(nt, "CENTER")]
    return reqs


def build_teoria_ingestao(sid):
    reqs = content_slide(sid, "Teoria: Ingestão por Upload de Arquivos")
    cards = [
        ("Create table", "Suba CSV e Excel direto\npelo Catalog Explorer\n\n• Drag & drop\n• Sem escrever código\n• Ideal para planilhas", TEAL),
        ("Inferência de Schema", "A UI detecta colunas\ne tipos automaticamente\n\n• First row = header\n• Ajuste os tipos\n• Prévia antes de criar", {"red": 0.8, "green": 0.5, "blue": 0.2}),
        ("Seu schema", "As tabelas criadas ficam\nem workshop_eneva.<nome>\n\n• Fato + dimensões\n• Enriquecimento\n• Base para o Lab 2", ORANGE),
    ]
    for i, (t, d, c) in enumerate(cards):
        x = 0.3 + i * 4.25
        reqs += benefit_card(sid, x, 1.5, 3.95, 4.8, t, d, c)
    nt = uid("nt"); reqs += [mk_shape(sid, nt, "TEXT_BOX", 0.5, 6.6, 12.3, 0.35),
                              mk_text(nt, "No workshop: suba os 5 arquivos da pasta dados/ para o seu schema (workshop_eneva.<nome>)"),
                              mk_style(nt, sz=11, color=MEDIUM_GRAY, italic=True), mk_para(nt, "CENTER")]
    return reqs


def build_teoria_lakeflow(sid):
    reqs = content_slide(sid, "Teoria: LakeFlow Designer", "Transformação de dados sem escrever código")
    # left: what it is
    gb = uid("gb"); reqs += [mk_shape(sid, gb, "ROUND_RECTANGLE", 0.3, 1.5, 6.0, 5.4), mk_fill(gb, LIGHT_GRAY)]
    gbar = uid("gr"); reqs += [mk_shape(sid, gbar, "RECTANGLE", 0.3, 1.5, 6.0, 0.07), mk_fill(gbar, ORANGE)]
    gt = uid("gt"); reqs += [mk_shape(sid, gt, "TEXT_BOX", 0.6, 1.7, 5.4, 0.5),
                              mk_text(gt, "O que é"), mk_style(gt, bold=True, sz=20, color=GREEN)]
    gd = uid("gd"); reqs += [mk_shape(sid, gd, "TEXT_BOX", 0.6, 2.3, 5.4, 4.4),
        mk_text(gd, "Experiência visual (no-code)\npara construir pipelines de\ntransformação.\n\n• Arraste blocos: Join,\n  Aggregate, Filter, Window\n• Gera SDP por baixo\n• Data Quality em cada etapa\n• Linhagem (lineage) automática\n\nAcessível a perfis de negócio,\nnão apenas engenheiros de dados."),
        mk_style(gd, sz=12, color=DARK_GRAY), mk_para(gd, "START", 150)]
    # right: 4 transformations
    rt = uid("rt"); reqs += [mk_shape(sid, rt, "TEXT_BOX", 7.0, 1.5, 6.0, 0.45),
                              mk_text(rt, "As 4 transformações do Lab"), mk_style(rt, bold=True, sz=18, color=GREEN)]
    steps = [("1", "Limpeza + Tempo", "Cast de tipos + ano/mês/\ndia/turno + Data Quality", TEAL),
             ("2", "Enriquecer Usinas", "Join com municípios →\nregião + submercado SIN", ORANGE),
             ("3", "Fator de Capacidade", "Join com fabricantes →\ncálculo vs referência", RED),
             ("4", "Ranking (Window)", "Agrega por usina →\nranking + % participação", YELLOW)]
    for i, (n, t, d, c) in enumerate(steps):
        y = 2.15 + i * 1.15
        nb = uid("nb"); reqs += [mk_shape(sid, nb, "ELLIPSE", 7.0, y, 0.5, 0.5), mk_fill(nb, c)]
        nt = uid("nt"); reqs += [mk_shape(sid, nt, "TEXT_BOX", 7.0, y + 0.07, 0.5, 0.4),
                                  mk_text(nt, n), mk_style(nt, bold=True, sz=14, color=WHITE), mk_para(nt, "CENTER")]
        tt = uid("tt"); reqs += [mk_shape(sid, tt, "TEXT_BOX", 7.7, y, 5.2, 0.35),
                                  mk_text(tt, t), mk_style(tt, bold=True, sz=13, color=GREEN)]
        dd = uid("dd"); reqs += [mk_shape(sid, dd, "TEXT_BOX", 7.7, y + 0.38, 5.2, 0.7),
                                  mk_text(dd, d), mk_style(dd, sz=10, color=DARK_GRAY), mk_para(dd, "START", 130)]
    return reqs


def build_teoria_genie(sid):
    reqs = content_slide(sid, "Teoria: Genie — Linguagem Natural")
    gb = uid("gb"); reqs += [mk_shape(sid, gb, "ROUND_RECTANGLE", 0.3, 1.5, 6.0, 5.4), mk_fill(gb, LIGHT_GRAY)]
    gbar = uid("gr"); reqs += [mk_shape(sid, gbar, "RECTANGLE", 0.3, 1.5, 6.0, 0.07), mk_fill(gbar, TEAL)]
    gt = uid("gt"); reqs += [mk_shape(sid, gt, "TEXT_BOX", 0.6, 1.7, 5.4, 0.5),
                              mk_text(gt, "Como funciona"), mk_style(gt, bold=True, sz=20, color=GREEN)]
    gd = uid("gd"); reqs += [mk_shape(sid, gd, "TEXT_BOX", 0.6, 2.3, 5.4, 4.4),
        mk_text(gd, "Pergunte aos dados em português\ne o Genie gera o SQL por você.\n\n• Conectado às tabelas Gold\n• Usa comentários como contexto\n• Instruções customizadas\n  ensinam o domínio do negócio\n• Sample Questions guiam o uso\n\nQuem cura o Genie faz toda a\ndiferença na qualidade das\nrespostas."),
        mk_style(gd, sz=12, color=DARK_GRAY), mk_para(gd, "START", 150)]
    rt = uid("rt"); reqs += [mk_shape(sid, rt, "TEXT_BOX", 7.0, 1.5, 6.0, 0.45),
                              mk_text(rt, "Exemplos de perguntas"), mk_style(rt, bold=True, sz=18, color=GREEN)]
    perguntas = [
        "Qual usina gerou mais energia no período?",
        "Qual a participação de cada fonte na matriz?",
        "Compare gás natural com carvão mineral",
        "Qual submercado do SIN concentra mais geração?",
        "Como varia a geração solar ao longo do dia?",
    ]
    for i, p in enumerate(perguntas):
        y = 2.2 + i * 0.9
        bl = uid("bl"); reqs += [mk_shape(sid, bl, "ROUND_RECTANGLE", 7.0, y, 5.9, 0.7), mk_fill(bl, LIGHT_GREEN)]
        lt = uid("lt"); reqs += [mk_shape(sid, lt, "TEXT_BOX", 7.2, y + 0.15, 5.6, 0.45),
                                  mk_text(lt, f"“{p}”"), mk_style(lt, sz=12, color=GREEN, italic=True)]
    return reqs


def build_teoria_aibi(sid):
    reqs = content_slide(sid, "Teoria: AI/BI Dashboards")
    cards = [
        ("Self-Service", "Qualquer pessoa cria e\nexplora dashboards, sem\ndepender do time de dados\n\n• Datasets em SQL\n• Widgets interativos", ORANGE),
        ("Visualizações", "KPIs, gráficos e tabelas\nsobre as tabelas Gold\n\n• Counter, Bar, Pie, Table\n• Filtros dinâmicos\n• Cross-filtering", PURPLE),
        ("Governança Única", "Mesmas permissões do\nUnity Catalog. Zero cópia\nde dados para BI externo\n\n• Um ponto de acesso\n• Dados em tempo real", GOOD_GREEN),
    ]
    for i, (t, d, c) in enumerate(cards):
        x = 0.3 + i * 4.25
        reqs += benefit_card(sid, x, 1.5, 3.95, 4.8, t, d, c)
    nt = uid("nt"); reqs += [mk_shape(sid, nt, "TEXT_BOX", 0.5, 6.6, 12.3, 0.35),
                              mk_text(nt, "Genie e Dashboards convivem: linguagem natural para explorar, dashboards para acompanhar"),
                              mk_style(nt, sz=11, color=MEDIUM_GRAY, italic=True), mk_para(nt, "CENTER")]
    return reqs


def build_lab_handson(sid, num, title, dur, steps):
    reqs = content_slide(sid, f"Lab {num}: {title}  ({dur})")
    # Distribute steps evenly across the usable band (below header, above footer),
    # centering each step's content within its row so the slide fills nicely.
    top, bottom = 1.55, 7.05
    band = (bottom - top) / len(steps)
    for i, (st, sd) in enumerate(steps):
        y = top + i * band          # row top
        cy = y + band / 2           # row vertical center
        cb = uid("cb"); reqs += [mk_shape(sid, cb, "ELLIPSE", 0.6, cy - 0.32, 0.64, 0.64), mk_fill(cb, ORANGE)]
        cn = uid("cn"); reqs += [mk_shape(sid, cn, "TEXT_BOX", 0.6, cy - 0.27, 0.64, 0.5),
                                  mk_text(cn, str(i + 1)), mk_style(cn, bold=True, sz=20, color=WHITE), mk_para(cn, "CENTER")]
        tt = uid("tt"); reqs += [mk_shape(sid, tt, "TEXT_BOX", 1.55, cy - 0.42, 11.0, 0.42),
                                  mk_text(tt, st), mk_style(tt, bold=True, sz=16, color=GREEN)]
        dt = uid("dt"); reqs += [mk_shape(sid, dt, "TEXT_BOX", 1.55, cy + 0.02, 11.2, 0.7),
                                  mk_text(dt, sd), mk_style(dt, sz=12, color=DARK_GRAY), mk_para(dt, "START", 140)]
        if i < len(steps) - 1:
            sp = uid("sp"); reqs += [mk_shape(sid, sp, "RECTANGLE", 0.6, y + band - 0.02, 12.1, 0.012),
                                     mk_fill(sp, {"red": 0.9, "green": 0.9, "blue": 0.9})]
    return reqs


def build_resumo(sid):
    reqs = content_slide(sid, "Resumo & Próximos Passos")
    lt = uid("lt"); reqs += [mk_shape(sid, lt, "TEXT_BOX", 0.5, 1.4, 6.0, 0.45),
                              mk_text(lt, "O que aprendemos"), mk_style(lt, bold=True, sz=18, color=GREEN)]
    labs = [("Lab 1 — Ingestão", "Upload manual (CSV/XLSX) → Bronze", TEAL),
            ("Lab 2 — Transformação", "LakeFlow Designer: 4 transformações", ORANGE),
            ("Lab 3 — Genie", "Consumo em linguagem natural", RED),
            ("Lab 4 — AI/BI", "Dashboards interativos", PURPLE)]
    for i, (n, d, c) in enumerate(labs):
        y = 2.0 + i * 1.15
        b = uid("b"); reqs += [mk_shape(sid, b, "RECTANGLE", 0.5, y, 0.08, 0.85), mk_fill(b, c)]
        nt = uid("nt"); reqs += [mk_shape(sid, nt, "TEXT_BOX", 0.8, y, 5.5, 0.35),
                                  mk_text(nt, n), mk_style(nt, bold=True, sz=14, color=GREEN)]
        dt = uid("dt"); reqs += [mk_shape(sid, dt, "TEXT_BOX", 0.8, y + 0.38, 5.5, 0.5),
                                  mk_text(dt, d), mk_style(dt, sz=12, color=DARK_GRAY)]
    rt = uid("rt"); reqs += [mk_shape(sid, rt, "TEXT_BOX", 7.0, 1.4, 6.0, 0.45),
                              mk_text(rt, "Próximos passos"), mk_style(rt, bold=True, sz=18, color=GREEN)]
    nb = uid("nb"); reqs += [mk_shape(sid, nb, "ROUND_RECTANGLE", 7.0, 2.0, 5.8, 4.2), mk_fill(nb, LIGHT_GRAY)]
    next_steps = "→  Aplicar os conceitos nos dados reais da Eneva\n\n→  Automatizar a ingestão (LakeFlow / conectores)\n\n→  Unity Catalog para governança de ponta a ponta\n\n→  Databricks Assistant p/ produtividade\n\n→  Serverless compute p/ economia"
    ns = uid("ns"); reqs += [mk_shape(sid, ns, "TEXT_BOX", 7.3, 2.3, 5.2, 3.6),
                              mk_text(ns, next_steps), mk_style(ns, sz=14, color=DARK_GRAY), mk_para(ns, "START", 150)]
    return reqs


def build_closing(sid):
    reqs = [{"updatePageProperties": {"objectId": sid,
        "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": DARK_GREEN}}}},
        "fields": "pageBackgroundFill"}}]
    ab = uid("ab"); reqs += [mk_shape(sid, ab, "RECTANGLE", 0, 0, SLIDE_W, 0.08), mk_fill(ab, ORANGE)]
    tt = uid("tt"); reqs += [mk_shape(sid, tt, "TEXT_BOX", 1.5, 2.0, 10.3, 1.2),
                              mk_text(tt, "Obrigado!"), mk_style(tt, bold=True, sz=52, color=WHITE), mk_para(tt, "CENTER")]
    st = uid("st"); reqs += [mk_shape(sid, st, "TEXT_BOX", 1.5, 3.2, 10.3, 0.7),
                              mk_text(st, "Workshop Hands-On Databricks — Eneva"),
                              mk_style(st, sz=22, color=ORANGE), mk_para(st, "CENTER")]
    ct = uid("ct"); reqs += [mk_shape(sid, ct, "TEXT_BOX", 1.5, 4.4, 10.3, 0.5),
                              mk_text(ct, "Dúvidas? Fale com seu time Databricks!"),
                              mk_style(ct, sz=16, color=MEDIUM_GRAY), mk_para(ct, "CENTER")]
    reqs.append(mk_image(sid, uid("ij"), f"{RAW}/juliandro_circle.png", 4.7, 5.0, 1.0, 1.0))
    reqs.append(mk_image(sid, uid("jn"), f"{RAW}/jean_circle.png", 7.6, 5.0, 1.0, 1.0))
    jn = uid("jn"); reqs += [mk_shape(sid, jn, "TEXT_BOX", 4.0, 6.1, 2.3, 0.6),
        mk_text(jn, "Juliandro Figueiró\nSolutions Architect"), mk_style(jn, sz=9, color=MEDIUM_GRAY), mk_para(jn, "CENTER", 130)]
    je = uid("je"); reqs += [mk_shape(sid, je, "TEXT_BOX", 6.9, 6.1, 2.3, 0.6),
        mk_text(je, "Jean Ertzogue\nAccount Executive"), mk_style(je, sz=9, color=MEDIUM_GRAY), mk_para(je, "CENTER", 130)]
    bb = uid("bb"); reqs += [mk_shape(sid, bb, "RECTANGLE", 0, SLIDE_H - 0.08, SLIDE_W, 0.08), mk_fill(bb, ORANGE)]
    return reqs


def build_cover():
    reqs = [{"updatePageProperties": {"objectId": "s_cover",
        "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": DARK_GREEN}}}},
        "fields": "pageBackgroundFill"}}]
    ab = uid("ab"); reqs += [mk_shape("s_cover", ab, "RECTANGLE", 0, 0, SLIDE_W, 0.08), mk_fill(ab, ORANGE)]
    tt = uid("tt"); reqs += [mk_shape("s_cover", tt, "TEXT_BOX", 1.0, 1.5, 11.3, 1.8),
                              mk_text(tt, "Workshop Hands-On\nDatabricks"), mk_style(tt, bold=True, sz=44, color=WHITE)]
    st = uid("st"); reqs += [mk_shape("s_cover", st, "TEXT_BOX", 1.0, 3.4, 11.3, 0.7),
                              mk_text(st, "Eneva"), mk_style(st, sz=26, color=ORANGE)]
    at = uid("at"); reqs += [mk_shape("s_cover", at, "TEXT_BOX", 1.0, 4.3, 11.3, 0.5),
        mk_text(at, "Data + AI Platform  |  Ingestão  |  LakeFlow Designer  |  Genie  |  AI/BI"),
        mk_style(at, sz=16, color=MEDIUM_GRAY)]
    reqs.append(mk_image("s_cover", uid("dl"), f"{RAW}/databricks_logo_white.png", 1.0, 5.6, 2.4, 0.4))
    bb = uid("bb"); reqs += [mk_shape("s_cover", bb, "RECTANGLE", 0, SLIDE_H - 0.08, SLIDE_W, 0.08), mk_fill(bb, ORANGE)]
    return reqs


def section_divider(sid, title):
    reqs = [{"updatePageProperties": {"objectId": sid,
        "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": GREEN}}}},
        "fields": "pageBackgroundFill"}}]
    ab = uid("ab"); reqs += [mk_shape(sid, ab, "RECTANGLE", 0, 0, SLIDE_W, 0.08), mk_fill(ab, ORANGE)]
    tt = uid("tt"); reqs += [mk_shape(sid, tt, "TEXT_BOX", 1.0, 3.0, 11.3, 1.4),
                              mk_text(tt, title), mk_style(tt, bold=True, sz=36, color=WHITE), mk_para(tt, "CENTER")]
    bb = uid("bb"); reqs += [mk_shape(sid, bb, "RECTANGLE", 0, SLIDE_H - 0.08, SLIDE_W, 0.08), mk_fill(bb, ORANGE)]
    return reqs


def main():
    global PRES_ID
    import os
    print("Building Workshop Eneva deck...")

    # Reuse an existing presentation if EXISTING_PRES_ID is set (keeps the same
    # URL and sharing); otherwise create a fresh one.
    PRES_ID = os.environ.get("EXISTING_PRES_ID", "").strip()
    if PRES_ID:
        print(f"Reusing presentation: {PRES_ID}")
    else:
        resp = api_call("POST", "https://slides.googleapis.com/v1/presentations",
                        {"title": "Workshop Hands-On Databricks — Eneva"})
        PRES_ID = resp["presentationId"]
        print(f"Created presentation: {PRES_ID}")

    # Existing slides to remove after we add ours (temp holder avoids empty deck)
    info = api_call("GET", f"https://slides.googleapis.com/v1/presentations/{PRES_ID}")
    default_slides = [s["objectId"] for s in info.get("slides", [])]

    slides = [
        ("s_cover", None),
        ("s_agenda", None),
        ("s_setup", None),
        ("s_arch", None),
        ("s_t_plat", None),
        ("s_sec1", "divider"),
        ("s_t_ing", None),
        ("s_lab1", None),
        ("s_sec2", "divider"),
        ("s_t_lf", None),
        ("s_lab2", None),
        ("s_sec3", "divider"),
        ("s_t_genie", None),
        ("s_lab3", None),
        ("s_sec4", "divider"),
        ("s_t_aibi", None),
        ("s_lab4", None),
        ("s_resumo", None),
        ("s_closing", None),
    ]

    # If reusing a deck, delete the old slides first (temp holder keeps deck valid)
    if default_slides:
        batch_update([{"createSlide": {"objectId": "s_temp_hold",
            "slideLayoutReference": {"predefinedLayout": "BLANK"}, "insertionIndex": 0}}])
        for ds in default_slides:
            batch_update([{"deleteObject": {"objectId": ds}}])
        default_slides = ["s_temp_hold"]

    for i, (sid, _) in enumerate(slides):
        batch_update([{"createSlide": {"objectId": sid,
            "slideLayoutReference": {"predefinedLayout": "BLANK"},
            "insertionIndex": i}}])
    print(f"Created {len(slides)} slides")

    # delete default slide(s)
    for ds in default_slides:
        batch_update([{"deleteObject": {"objectId": ds}}])

    # 2. Build content
    print("Building content...")
    batch_update(build_cover())

    builders = [
        ("s_agenda", build_agenda),
        ("s_setup", build_setup),
        ("s_arch", build_architecture),
        ("s_t_plat", build_teoria_plataforma),
        ("s_t_ing", build_teoria_ingestao),
        ("s_t_lf", build_teoria_lakeflow),
        ("s_t_genie", build_teoria_genie),
        ("s_t_aibi", build_teoria_aibi),
        ("s_resumo", build_resumo),
        ("s_closing", build_closing),
    ]
    for sid, fn in builders:
        print(f"  {sid}")
        batch_update(fn(sid))

    # section dividers
    dividers = [
        ("s_sec1", "Lab 1 — Ingestão de Dados  (30 min)"),
        ("s_sec2", "Lab 2 — Transformação com LakeFlow Designer  (40 min)"),
        ("s_sec3", "Lab 3 — Genie Space  (30 min)"),
        ("s_sec4", "Lab 4 — AI/BI Dashboards  (30 min)"),
    ]
    for sid, title in dividers:
        batch_update(section_divider(sid, title))

    # hands-on slides
    batch_update(build_lab_handson("s_lab1", "1", "Ingestão de Dados", "30 min", [
        ("Baixe os arquivos",
         "Pasta dados/ do repositório — 5 tabelas em CSV e XLSX (fato + dimensões + enriquecimento)"),
        ("Suba via Catalog > Create table",
         "Para cada arquivo: Catalog → workshop_eneva → seu schema → Create table → Upload files"),
        ("Valide a camada Bronze",
         "Execute 01b_validacao.py — as 5 tabelas Bronze devem estar populadas"),
    ]))
    batch_update(build_lab_handson("s_lab2", "2", "LakeFlow Designer", "40 min", [
        ("Leia o guia visual",
         "02a_guia_lakeflow_designer.py — passo a passo para montar o pipeline arrastando blocos"),
        ("Monte as 4 transformações",
         "Limpeza + Tempo → Enriquecer Usinas → Fator de Capacidade → Ranking com Window (ou complete 02b)"),
        ("Crie e rode o pipeline",
         "ETL pipeline → pipeline_eneva_<nome> → catalog workshop_eneva, schema <nome> → Serverless → Start"),
    ]))
    batch_update(build_lab_handson("s_lab3", "3", "Genie Space", "30 min", [
        ("Complete os TO-DOs",
         "03a_genie_to_do.py — views, comentários em tabelas e colunas, instruções customizadas"),
        ("Crie a Genie Space",
         "Genie > New > Geração Eneva - <nome> — adicione as tabelas Gold e views"),
        ("Cole as instruções e teste",
         "Contexto Eneva + glossário do setor elétrico. Pergunte: “Qual usina gerou mais energia?”"),
    ]))
    batch_update(build_lab_handson("s_lab4", "4", "AI/BI Dashboards", "30 min", [
        ("Complete os TO-DOs",
         "04a_dashboard_to_do.py — queries de submercado e perfil por turno"),
        ("Crie o Dashboard",
         "Dashboards > Create dashboard > Dashboard Geração Eneva - <nome> — um dataset por query"),
        ("Monte os widgets",
         "Counter (KPIs), Pie (fonte), Bar (ranking/submercado/turno), Table (disponibilidade)"),
    ]))

    print(f"\n✅ Deck pronto!")
    print(f"   URL: https://docs.google.com/presentation/d/{PRES_ID}/edit")


if __name__ == "__main__":
    main()
