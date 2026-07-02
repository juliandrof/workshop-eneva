#!/usr/bin/env python3
"""Generate an AI/BI dashboard layout mockup for Workshop Eneva.

All charts are drawn directly in data coordinates on a single axis so the
mock widgets always stay inside their panels (no fragile add_axes overlays).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Wedge
import numpy as np
import os

FIG_W, FIG_H = 20, 12
DPI = 200

NAVY = "#0B3D2E"
ORANGE = "#FF7033"
RED = "#FF3621"
YELLOW = "#FBB300"
PURPLE = "#5E35B1"
TEAL = "#00838F"
BROWN = "#8B4513"
GRAY = "#6B7B8D"
LIGHT = "#F4F6F5"


def panel(ax, x, y, w, h, title, accent):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                 facecolor="white", edgecolor="#D6DCD9",
                                 linewidth=1.5, zorder=2))
    ax.add_patch(Rectangle((x, y+h-0.12), w, 0.12, facecolor=accent,
                            edgecolor="none", zorder=3))
    ax.text(x+0.25, y+h-0.45, title, fontsize=13, fontweight="bold",
            color=NAVY, ha="left", va="center", zorder=4)


def hbars(ax, x, y, w, h, labels, vals, color):
    """Horizontal bars inside region (x,y,w,h) in data coords."""
    n = len(labels)
    vmax = max(vals)
    pad = 0.15
    bar_h = (h - pad*2) / n * 0.7
    gap = (h - pad*2) / n
    label_w = 1.7
    bx0 = x + label_w
    bw_max = w - label_w - 0.6
    for i, (lab, v) in enumerate(zip(labels, vals)):
        cy = y + pad + gap*(n-1-i) + gap/2
        bw = bw_max * (v / vmax)
        ax.add_patch(Rectangle((bx0, cy-bar_h/2), bw, bar_h, facecolor=color,
                                edgecolor="none", zorder=4))
        ax.text(x+0.2, cy, lab, fontsize=9.5, color=NAVY, ha="left", va="center", zorder=5)
        ax.text(bx0+bw+0.1, cy, f"{v:,}".replace(",", "."), fontsize=8.5,
                color=GRAY, ha="left", va="center", zorder=5)


def vbars(ax, x, y, w, h, labels, series, colors, legend=None):
    """Grouped vertical bars inside region (x,y,w,h)."""
    n = len(labels)
    ng = len(series)
    pad = 0.2
    region_w = w - pad*2
    slot = region_w / n
    group_w = slot * 0.7
    bw = group_w / ng
    vmax = max(max(s) for s in series)
    bh_max = h - 0.9
    for i, lab in enumerate(labels):
        gx = x + pad + slot*i + (slot-group_w)/2
        for j, s in enumerate(series):
            bh = bh_max * (s[i]/vmax)
            ax.add_patch(Rectangle((gx+bw*j, y+0.5), bw, bh, facecolor=colors[j],
                                    edgecolor="none", zorder=4))
        ax.text(x+pad+slot*i+slot/2, y+0.28, lab, fontsize=8.5, color=NAVY,
                ha="center", va="center", zorder=5)
    if legend:
        for k, (name, c) in enumerate(legend):
            ly = y + h - 0.5 - k*0.35
            ax.add_patch(Rectangle((x+w-2.0, ly-0.08), 0.2, 0.16, facecolor=c, zorder=5))
            ax.text(x+w-1.7, ly, name, fontsize=8.5, color=NAVY, ha="left", va="center", zorder=5)


def pie(ax, cx, cy, r, vals, labels, colors):
    total = sum(vals)
    start = 90
    for v, lab, c in zip(vals, labels, colors):
        ang = v/total*360
        ax.add_patch(Wedge((cx, cy), r, start-ang, start, facecolor=c,
                           edgecolor="white", linewidth=1.5, zorder=4))
        mid = np.radians(start - ang/2)
        ax.text(cx+r*0.6*np.cos(mid), cy+r*0.6*np.sin(mid), f"{v/total*100:.0f}%",
                fontsize=9, color="white", fontweight="bold",
                ha="center", va="center", zorder=5)
        start -= ang
    # legend
    for k, (lab, c) in enumerate(zip(labels, colors)):
        ly = cy + r - k*0.4
        ax.add_patch(Rectangle((cx+r+0.3, ly-0.08), 0.2, 0.16, facecolor=c, zorder=5))
        ax.text(cx+r+0.6, ly, lab, fontsize=9, color=NAVY, ha="left", va="center", zorder=5)


def main():
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor(LIGHT)
    ax.set_facecolor(LIGHT)
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    ax.axis("off")

    # Header bar
    ax.add_patch(Rectangle((0, FIG_H-1.0), FIG_W, 1.0, facecolor=NAVY, zorder=1))
    ax.text(0.5, FIG_H-0.5, "Dashboard Geração Eneva", fontsize=22,
            fontweight="bold", color="white", ha="left", va="center", zorder=2)
    ax.text(FIG_W-0.5, FIG_H-0.5, "AI/BI Dashboard  •  Databricks", fontsize=12,
            color="#9DBBB0", ha="right", va="center", zorder=2)

    top = FIG_H - 1.4

    # Row 1: 4 KPI counters
    kpis = [
        ("Geração Total", "48.230 MWh", ORANGE),
        ("Usinas Ativas", "15", TEAL),
        ("Disponibilidade Média", "94,6%", YELLOW),
        ("Combustível Consumido", "6.812", PURPLE),
    ]
    kw = (FIG_W - 0.5*5) / 4
    for i, (t, v, c) in enumerate(kpis):
        x = 0.5 + i*(kw+0.5)
        y = top - 1.8
        ax.add_patch(FancyBboxPatch((x, y), kw, 1.8, boxstyle="round,pad=0.05",
                                     facecolor="white", edgecolor="#D6DCD9",
                                     linewidth=1.5, zorder=2))
        ax.add_patch(Rectangle((x, y), 0.12, 1.8, facecolor=c, edgecolor="none", zorder=3))
        ax.text(x+kw/2, y+1.15, v, fontsize=26, fontweight="bold", color=NAVY,
                ha="center", va="center", zorder=4)
        ax.text(x+kw/2, y+0.45, t, fontsize=12, color=GRAY,
                ha="center", va="center", zorder=4)

    # Row 2: Pie (fonte) + Bar (ranking usinas)
    r2h = 3.6
    r2y = top - 1.8 - 0.5 - r2h
    pw = (FIG_W - 0.5*3) * 0.38
    bw = (FIG_W - 0.5*3) * 0.62
    panel(ax, 0.5, r2y, pw, r2h, "Geração por Fonte", TEAL)
    pie(ax, 0.5+pw*0.36, r2y+r2h*0.42, 1.05,
        [62, 25, 13], ["Gás Natural", "Carvão", "Solar"], [ORANGE, BROWN, YELLOW])

    panel(ax, 0.5+pw+0.5, r2y, bw, r2h, "Ranking de Usinas (MWh)", ORANGE)
    hbars(ax, 0.5+pw+0.5+0.3, r2y+0.2, bw-0.6, r2h-1.0,
          ["Parnaíba I", "Futura I", "Pecém II", "Itaqui", "Parnaíba II", "Parnaíba V"],
          [8200, 7400, 6100, 5900, 5200, 4300], ORANGE)

    # Row 3: Bar (submercado) + Bar (turno) + Table (disponibilidade)
    r3y = 0.5
    r3h = 3.2
    cw = (FIG_W - 0.5*4) / 3
    panel(ax, 0.5, r3y, cw, r3h, "Geração por Submercado", RED)
    vbars(ax, 0.5+0.2, r3y, cw-0.4, r3h-0.5,
          ["Nordeste", "Norte", "Manaus"], [[31000, 12000, 5200]], [RED])

    panel(ax, 0.5+cw+0.5, r3y, cw, r3h, "Geração por Turno", PURPLE)
    vbars(ax, 0.5+cw+0.5+0.2, r3y, cw-0.4, r3h-0.5,
          ["Madr.", "Manhã", "Tarde", "Noite"],
          [[9.0, 9.5, 9.2, 8.8], [0.0, 3.1, 4.0, 0.0]], [PURPLE, YELLOW],
          legend=[("Térmica", PURPLE), ("Solar", YELLOW)])

    panel(ax, 0.5+2*(cw+0.5), r3y, cw, r3h, "Disponibilidade por Usina", YELLOW)
    tx = 0.5+2*(cw+0.5)+0.25
    rows = [("Parnaíba I", "97,2%"), ("Jaguatirica II", "96,1%"),
            ("Pecém II", "95,3%"), ("Itaqui", "94,0%"), ("Azulão", "92,8%")]
    ry = r3y + r3h - 0.9
    for name, val in rows:
        ax.text(tx, ry, name, fontsize=10.5, color=NAVY, ha="left", va="center", zorder=4)
        ax.text(tx+cw-0.5, ry, val, fontsize=10.5, color=GRAY, ha="right", va="center", zorder=4)
        ax.plot([tx, tx+cw-0.5], [ry-0.24, ry-0.24], color="#E5E9E7", lw=0.8, zorder=3)
        ry -= 0.48

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_layout.png")
    fig.savefig(out, dpi=DPI, facecolor=LIGHT, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
