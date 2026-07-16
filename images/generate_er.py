#!/usr/bin/env python3
"""Generate ER diagram for Workshop Eneva Databricks data model."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

FIG_W, FIG_H = 48, 36
DPI = 200
TITLE = "Modelo de Dados — Workshop Eneva"

FONT_LAYER = 36
FONT_TABLE = 25
FONT_COL = 19
FONT_TAG = 16

LAYERS = [
    ("ARQUIVOS (CSV/XLSX)", "#EAF2FB", "#2979FF", [
        ("fato_geracao", [
            ("id_leitura", "PK"), ("id_unidade", "FK"), ("id_usina", "FK"),
            ("data_hora", ""), ("geracao_mwh", ""), ("consumo_combustivel", ""),
            ("disponibilidade", ""), ("temperatura_c", ""),
        ]),
        ("dim_usinas", [
            ("id_usina", "PK"), ("nome_usina", ""), ("fonte", ""),
            ("combustivel", ""), ("potencia_instalada_mw", ""),
            ("municipio", ""), ("uf", ""), ("ano_operacao", ""),
        ]),
        ("dim_unidades_geradoras", [
            ("id_unidade", "PK"), ("codigo_unidade", ""), ("id_usina", "FK"),
            ("tecnologia", ""), ("fabricante", ""), ("potencia_nominal_mw", ""),
        ]),
        ("enriquecimento_municipios / _fabricantes", [
            ("municipio / fabricante", "PK"), ("regiao / pais_origem", ""),
            ("submercado_sin", ""), ("eficiencia_nominal_pct", ""),
        ]),
    ]),
    ("BRONZE  (upload manual)", "#FFF0E0", "#EF6C00", [
        ("fato_geracao", [
            ("id_leitura", "PK"), ("id_unidade", "FK"), ("id_usina", "FK"),
            ("data_hora", ""), ("geracao_mwh", ""), ("consumo_combustivel", ""),
            ("disponibilidade", ""), ("temperatura_c", ""),
        ]),
        ("dim_usinas", [
            ("id_usina", "PK"), ("nome_usina", ""), ("fonte", ""),
            ("combustivel", ""), ("municipio", ""), ("uf", ""),
        ]),
        ("dim_unidades_geradoras", [
            ("id_unidade", "PK"), ("id_usina", "FK"), ("fabricante", ""),
            ("tecnologia", ""), ("potencia_nominal_mw", ""),
        ]),
        ("enriquecimento_municipios / _fabricantes", [
            ("municipio / fabricante", "PK"), ("regiao / pais_origem", ""),
            ("submercado_sin", ""), ("eficiencia_nominal_pct", ""),
        ]),
    ]),
    ("SILVER", "#E8F5E9", "#388E3C", [
        ("silver_geracao  (FATO)", [
            ("id_leitura", "PK"), ("id_unidade", "FK"), ("id_usina", "FK"),
            ("data_hora", ""), ("ano/mes/dia/hora", ""), ("turno", ""),
            ("geracao_mwh", ""), ("consumo_combustivel", ""),
            ("disponibilidade", ""), ("temperatura_c", ""),
        ]),
        ("silver_usinas", [
            ("id_usina", "PK"), ("nome_usina", ""), ("fonte", ""),
            ("municipio", ""), ("regiao", ""), ("submercado_sin", ""),
            ("populacao", ""), ("idade_anos", ""),
        ]),
        ("silver_desempenho_unidades", [
            ("id_unidade", "FK"), ("id_usina", "FK"), ("fabricante", ""),
            ("geracao_media_mwh", ""), ("fator_capacidade", ""),
            ("gap_vs_referencia", ""),
        ]),
    ]),
    ("GOLD", "#FFFDE7", "#F9A825", [
        ("gold_geracao_por_usina", [
            ("id_usina", ""), ("nome_usina", ""), ("fonte", ""),
            ("geracao_total_mwh", ""), ("disponibilidade_media", ""),
            ("ranking", ""), ("pct_participacao", ""),
        ]),
        ("gold_geracao_por_fonte", [
            ("fonte", ""), ("combustivel", ""), ("geracao_total_mwh", ""),
            ("num_usinas", ""), ("disponibilidade_media", ""),
        ]),
        ("gold_geracao_por_submercado", [
            ("submercado_sin", ""), ("regiao", ""), ("geracao_total_mwh", ""),
            ("num_usinas", ""), ("num_estados", ""),
        ]),
    ]),
]

STACKED_DEFS = [
    ("GENIE", "#E0F7FA", "#00838F", [
        ("Genie Agent", [
            ("Linguagem natural", ""), ("Tabelas Gold + views", ""),
            ("Instruções customizadas", ""),
        ]),
    ]),
    ("AI/BI", "#EDE7F6", "#5E35B1", [
        ("Dashboard", [
            ("KPIs de geração", ""), ("Por fonte / submercado", ""),
            ("Ranking de usinas", ""), ("Perfil por turno", ""),
        ]),
    ]),
]

TW = 6.2
RH = 0.65
HH = 0.9
TG = 0.5
LPX = 0.7
LPY = 0.8
LHH = 1.3
LG = 1.2


def th(cols):
    return HH + len(cols) * RH + 0.3


def layout():
    result = {}
    x = 1.5
    for lname, bg, border, tables in LAYERS:
        heights = [th(c) for _, c in tables]
        total = sum(heights) + TG * (len(tables) - 1)
        lw = TW + 2 * LPX
        lh = total + 2 * LPY + LHH
        ly = (FIG_H - lh) / 2 - 0.5
        layer = {"x": x, "y": ly, "w": lw, "h": lh,
                 "bg": bg, "border": border, "name": lname, "tables": []}
        ty = ly + lh - LHH - LPY
        tx = x + LPX
        for (tn, cols), h in zip(tables, heights):
            ty_top = ty - h
            layer["tables"].append({"name": tn, "cols": cols,
                                     "x": tx, "y": ty_top, "w": TW, "h": h})
            ty = ty_top - TG
        result[lname] = layer
        x += lw + LG

    sx = x
    lw = TW + 2 * LPX
    infos = []
    for lname, bg, border, tables in STACKED_DEFS:
        heights = [th(c) for _, c in tables]
        total = sum(heights) + TG * (len(tables) - 1)
        lh = total + 2 * LPY + LHH
        infos.append((lname, bg, border, tables, heights, lh))
    total_sh = sum(i[5] for i in infos) + LG
    cy = (FIG_H - total_sh) / 2 - 0.5 + total_sh
    for lname, bg, border, tables, heights, lh in infos:
        ly = cy - lh
        layer = {"x": sx, "y": ly, "w": lw, "h": lh,
                 "bg": bg, "border": border, "name": lname, "tables": []}
        ty = ly + lh - LHH - LPY
        tx = sx + LPX
        for (tn, cols), h in zip(tables, heights):
            ty_top = ty - h
            layer["tables"].append({"name": tn, "cols": cols,
                                     "x": tx, "y": ty_top, "w": TW, "h": h})
            ty = ty_top - TG
        result[lname] = layer
        cy = ly - LG
    return result


def draw_table(ax, t, bc):
    x, y, w, h = t["x"], t["y"], t["w"], t["h"]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                 facecolor="white", edgecolor=bc, linewidth=3, zorder=3))
    ax.add_patch(FancyBboxPatch((x+0.06, y+h-HH-0.05), w-0.12, HH,
                                 boxstyle="round,pad=0.06", facecolor=bc,
                                 edgecolor="none", alpha=0.10, zorder=4))
    ax.text(x+w/2, y+h-HH/2-0.03, t["name"], ha="center", va="center",
            fontsize=FONT_TABLE, fontweight="bold", color="#000",
            fontfamily="monospace", zorder=5)
    sy = y + h - HH - 0.08
    ax.plot([x+0.2, x+w-0.2], [sy, sy], color="#BBB", lw=1.5, zorder=4)
    cy = sy - RH * 0.65
    for cn, tag in t["cols"]:
        if tag == "PK":
            ax.text(x+0.3, cy, "●", fontsize=FONT_TAG, color="#E65100",
                    fontweight="bold", ha="left", va="center", zorder=5)
            ax.text(x+0.8, cy, cn, fontsize=FONT_COL, color="#000",
                    fontweight="bold", fontfamily="monospace",
                    ha="left", va="center", zorder=5)
            ax.text(x+w-0.3, cy, "PK", fontsize=FONT_TAG, color="#E65100",
                    fontweight="bold", ha="right", va="center", zorder=5)
        elif tag == "FK":
            ax.text(x+0.8, cy, cn, fontsize=FONT_COL, color="#000",
                    fontfamily="monospace", fontstyle="italic",
                    ha="left", va="center", zorder=5)
            ax.text(x+w-0.3, cy, "FK", fontsize=FONT_TAG, color="#757575",
                    ha="right", va="center", zorder=5)
        else:
            ax.text(x+0.8, cy, cn, fontsize=FONT_COL, color="#000",
                    fontfamily="monospace", ha="left", va="center", zorder=5)
        cy -= RH


def draw_layer(ax, L):
    x, y, w, h = L["x"], L["y"], L["w"], L["h"]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                                 facecolor=L["bg"], edgecolor=L["border"],
                                 linewidth=3.5, linestyle="--", alpha=0.7, zorder=1))
    ax.text(x+w/2, y+h-LHH/2+0.12, L["name"], ha="center", va="center",
            fontsize=FONT_LAYER, fontweight="bold", color=L["border"], zorder=5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=L["border"], linewidth=3, alpha=0.95))


def main():
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.text(FIG_W/2, FIG_H - 1.5, TITLE, ha="center", va="center",
            fontsize=48, fontweight="bold", color="#000", zorder=10)

    L = layout()
    all_names = [n for n, *_ in LAYERS] + [n for n, *_ in STACKED_DEFS]
    for n in all_names:
        li = L[n]
        draw_layer(ax, li)
        for t in li["tables"]:
            draw_table(ax, t, li["border"])

    order = [n for n, *_ in LAYERS]
    for i in range(len(order)-1):
        s, d = L[order[i]], L[order[i+1]]
        ax.annotate("", xy=(d["x"]-0.08, d["y"]+d["h"]/2),
                    xytext=(s["x"]+s["w"]+0.08, s["y"]+s["h"]/2),
                    arrowprops=dict(arrowstyle="-|>", color="#333", lw=4,
                                    mutation_scale=40), zorder=2)

    g = L["GOLD"]
    gx, gy = g["x"]+g["w"], g["y"]+g["h"]/2
    for dn in ["GENIE", "AI/BI"]:
        d = L[dn]
        ax.annotate("", xy=(d["x"]-0.08, d["y"]+d["h"]/2),
                    xytext=(gx+0.08, gy),
                    arrowprops=dict(arrowstyle="-|>", color="#333", lw=4,
                                    mutation_scale=40), zorder=2)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_er.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="white", pad_inches=0.2)
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
