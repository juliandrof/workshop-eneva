#!/usr/bin/env python3
"""Generate SVG headers for Workshop Eneva and render them to PNG via rsvg-convert."""

import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Databricks brand palette + energy accent
BG_TOP = "#0B3D2E"      # deep green (energy/sustentabilidade)
BG_BOT = "#07261D"
RED = "#FF3621"          # Databricks red
ORANGE = "#FF7033"
YELLOW = "#FBB300"
GREEN = "#2ECC71"
SUB = "#7FB3A0"

DATABRICKS_ICON = (
    '<path fill="white" d="M.95 14.184L12 20.403l9.919-5.55v2.21L12 22.662l-10.484-5.96'
    '-.565.308v.77L12 24l11.05-6.218v-4.317l-.515-.309L12 19.118l-9.867-5.653v-2.21L12 '
    '16.805l11.05-6.218V6.32l-.515-.308L12 11.974 2.647 6.681 12 1.388l7.76 4.368.668-.411'
    'v-.566L12 0 .95 6.27v.72L12 13.207l9.919-5.55v2.26L12 15.52 1.516 9.56l-.565.308Z"/>'
)


def main_header():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{BG_TOP};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{BG_BOT};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="1200" height="300" fill="url(#bg)"/>
  <rect width="1200" height="6" fill="{RED}"/>
  <rect x="0" y="294" width="400" height="6" fill="{ORANGE}"/>
  <rect x="400" y="294" width="400" height="6" fill="{RED}"/>
  <rect x="800" y="294" width="400" height="6" fill="{YELLOW}"/>
  <g transform="translate(1070,30) scale(3.5)" opacity="0.12">{DATABRICKS_ICON}</g>
  <text x="60" y="105" font-family="Inter, Helvetica, Arial, sans-serif" font-size="46" font-weight="700" fill="white">Workshop Hands-On</text>
  <text x="60" y="165" font-family="Inter, Helvetica, Arial, sans-serif" font-size="46" font-weight="700" fill="white">Databricks</text>
  <rect x="60" y="182" width="120" height="4" rx="2" fill="{RED}"/>
  <text x="60" y="218" font-family="Inter, Helvetica, Arial, sans-serif" font-size="28" font-weight="400" fill="{ORANGE}">Eneva &#183; Data + AI Platform</text>
  <text x="60" y="265" font-family="Inter, Helvetica, Arial, sans-serif" font-size="15" font-weight="400" fill="{SUB}">Ingest&#227;o &#183; LakeFlow Designer &#183; Genie &#183; AI/BI Dashboards</text>
</svg>'''


def lab_header(tag, title, subtitle):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="200" viewBox="0 0 1200 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{BG_TOP};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{BG_BOT};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="1200" height="200" fill="url(#bg)"/>
  <rect width="1200" height="5" fill="{RED}"/>
  <rect x="0" y="195" width="1200" height="5" fill="{ORANGE}"/>
  <g transform="translate(1080,25) scale(2.6)" opacity="0.12">{DATABRICKS_ICON}</g>
  <text x="60" y="70" font-family="Inter, Helvetica, Arial, sans-serif" font-size="20" font-weight="700" fill="{ORANGE}">{tag}</text>
  <text x="60" y="120" font-family="Inter, Helvetica, Arial, sans-serif" font-size="40" font-weight="700" fill="white">{title}</text>
  <rect x="60" y="135" width="90" height="4" rx="2" fill="{RED}"/>
  <text x="60" y="170" font-family="Inter, Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="{SUB}">{subtitle}</text>
</svg>'''


HEADERS = {
    "header_workshop_eneva": main_header(),
    "header_setup": lab_header("SETUP", "Configura&#231;&#227;o Inicial",
                               "Cat&#225;logo Unity Catalog &#183; Dados sint&#233;ticos do parque gerador"),
    "header_lab1": lab_header("LAB 01", "Ingest&#227;o de Dados",
                              "Upload manual de CSV/XLSX &#183; Camada Bronze"),
    "header_lab2": lab_header("LAB 02", "Transforma&#231;&#227;o &#8212; LakeFlow Designer",
                              "Silver &amp; Gold &#183; 4 transforma&#231;&#245;es low-code"),
    "header_lab3": lab_header("LAB 03", "Genie Space",
                              "Consumindo dados em linguagem natural"),
    "header_lab4": lab_header("LAB 04", "AI/BI Dashboards",
                              "Visualiza&#231;&#245;es interativas da gera&#231;&#227;o"),
}


def main():
    for name, svg in HEADERS.items():
        svg_path = os.path.join(HERE, f"{name}.svg")
        png_path = os.path.join(HERE, f"{name}.png")
        with open(svg_path, "w") as f:
            f.write(svg)
        subprocess.run(["rsvg-convert", svg_path, "-o", png_path], check=True)
        print(f"Saved: {png_path}")


if __name__ == "__main__":
    main()
