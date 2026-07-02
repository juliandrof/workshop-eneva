#!/usr/bin/env python3
"""Generate architecture diagram for Workshop Eneva (Medallion + Ingestão/Transformação/Genie/AI-BI)."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FIG_W, FIG_H = 40, 18
DPI = 200

FONT_STAGE = 32
FONT_SUB = 22
FONT_FEAT = 19
FONT_PIPE = 26

PIPELINE_COLOR = "#FF6F00"


def draw_box(ax, x, y, w, h, bg, border, lw=4, ls="-"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                        facecolor=bg, edgecolor=border, linewidth=lw,
                        linestyle=ls, zorder=3)
    ax.add_patch(p)


def draw_stage(ax, x, y, w, h, name, subtitle, bg, border, features):
    draw_box(ax, x, y, w, h, bg, border)
    ny = y + h - 0.9
    ax.text(x + w/2, ny, name, ha="center", va="center",
            fontsize=FONT_STAGE, fontweight="bold", color=border, zorder=5)
    if subtitle:
        sep_y = ny - 1.25
        ax.text(x + w/2, ny - 0.7, subtitle, ha="center", va="center",
                fontsize=FONT_SUB, color="#555", fontstyle="italic", zorder=5)
    else:
        sep_y = ny - 0.6
    if features:
        ax.plot([x+0.3, x+w-0.3], [sep_y, sep_y], color=border, lw=2, alpha=0.4, zorder=4)
        fy = sep_y - 0.6
        for f in features:
            ax.text(x + 0.5, fy, f"• {f}", ha="left", va="center",
                    fontsize=FONT_FEAT, color="#000", zorder=5)
            fy -= 0.65


def arrow(ax, x1, y1, x2, y2, curve=0.0):
    cs = f"arc3,rad={curve}" if curve else "arc3,rad=0.0"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#333", lw=4,
                                mutation_scale=35, connectionstyle=cs), zorder=2)


def main():
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.text(FIG_W/2, FIG_H - 0.8, "Arquitetura — Workshop Eneva",
            ha="center", va="center", fontsize=42, fontweight="bold", color="#000", zorder=10)

    # Source
    sw, sh = 3.2, 2.4
    sx, sy = 0.5, 8.9
    draw_box(ax, sx, sy, sw, sh, "#E8F5E9", "#0B3D2E", lw=4, ls="--")
    ax.text(sx + sw/2, sy + sh/2, "Medidores\ndas Usinas\n(JSON Streaming)",
            ha="center", va="center", fontsize=FONT_SUB, fontweight="bold",
            color="#0B3D2E", zorder=5)

    # Main medallion stages
    stages = [
        ("BRONZE", "Ingestão (Lab 1)", "#FFF0E0", "#EF6C00",
         ["Auto Loader (cloudFiles)", "Leituras de geração",
          "Dimensões + Enriquecimento", "Dados Brutos"]),
        ("SILVER", "Transformação (Lab 2)", "#E8F5E9", "#388E3C",
         ["LakeFlow Designer", "Explode das leituras", "Enriquecimento (join)",
          "Fator de Capacidade", "Data Quality"]),
        ("GOLD", "Agregação (Lab 2)", "#FFFDE7", "#F9A825",
         ["Geração por Usina + Ranking", "Geração por Fonte",
          "Geração por Submercado", "Janelas (window)"]),
    ]

    bw, bh = 6.8, 6.7
    gap = 0.7
    bx = sx + sw + 1.0
    by = 6.8
    pos = {}

    for name, sub, bg, border, feats in stages:
        draw_stage(ax, bx, by, bw, bh, name, sub, bg, border, feats)
        pos[name] = (bx, by, bw, bh)
        bx += bw + gap

    # Fan-out: Genie and AI/BI stacked
    fx = pos["GOLD"][0] + pos["GOLD"][2] + 1.0
    fw = 7.5

    fh1 = 4.5
    fy1 = by + bh - fh1
    draw_stage(ax, fx, fy1, fw, fh1, "GENIE", "Lab 3", "#E0F7FA", "#00838F",
               ["Linguagem Natural (PT)", "Instruções customizadas",
                "Glossário do setor elétrico"])

    fh2 = 4.5
    fy2 = fy1 - 0.6 - fh2
    draw_stage(ax, fx, fy2, fw, fh2, "AI/BI", "Lab 4", "#EDE7F6", "#5E35B1",
               ["Dashboards interativos", "KPIs de geração",
                "Gráficos e tabelas"])

    # Arrows
    arrow(ax, sx + sw, sy + sh/2, pos["BRONZE"][0], pos["BRONZE"][1] + pos["BRONZE"][3]/2)
    for a, b in [("BRONZE", "SILVER"), ("SILVER", "GOLD")]:
        p = pos[a]
        q = pos[b]
        arrow(ax, p[0]+p[2], p[1]+p[3]/2, q[0], q[1]+q[3]/2)

    gp = pos["GOLD"]
    gmid = gp[1] + gp[3]/2
    arrow(ax, gp[0]+gp[2], gmid, fx, fy1 + fh1/2, curve=0.15)
    arrow(ax, gp[0]+gp[2], gmid, fx, fy2 + fh2/2, curve=-0.15)

    # Pipeline bar (LakeFlow)
    pb_y = by - 2.0
    pb_x = pos["BRONZE"][0]
    pb_w = pos["GOLD"][0] + pos["GOLD"][2] - pb_x
    draw_box(ax, pb_x, pb_y, pb_w, 1.3, "#FFF3E0", PIPELINE_COLOR, lw=4)
    ax.text(pb_x + pb_w/2, pb_y + 0.65, "LakeFlow — Spark Declarative Pipelines",
            ha="center", va="center", fontsize=FONT_PIPE, fontweight="bold",
            color=PIPELINE_COLOR, zorder=5)

    for n in ["BRONZE", "SILVER", "GOLD"]:
        cx = pos[n][0] + pos[n][2]/2
        ax.plot([cx, cx], [pb_y + 1.3, pos[n][1]],
                color=PIPELINE_COLOR, lw=2.5, ls=":", alpha=0.5, zorder=2)

    # Governance bar
    wf_y = min(pb_y, fy2) - 1.8
    wf_w = fx + fw - pb_x
    draw_box(ax, pb_x, wf_y, wf_w, 1.2, "#E8F5E9", "#0B3D2E", lw=3)
    ax.text(pb_x + wf_w/2, wf_y + 0.6,
            "Unity Catalog  •  Governança & Linhagem  •  Serverless Compute  •  Delta Lake",
            ha="center", va="center", fontsize=FONT_SUB - 2, fontweight="bold",
            color="#0B3D2E", zorder=5)

    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arquitetura.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="white", pad_inches=0.2)
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
