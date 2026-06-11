#!/usr/bin/env python3
"""Generate ATLAS.ti-style Network View Diagram as SVG.

Faithfully replicates ATLAS.ti network editor visual style:
- Compact rectangular nodes with colored headers
- Straight-line links with relation labels on the line
- Organic/free-form layout (not rigid hierarchy)
- Clean white background
- Minimal, professional look
"""

import math
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

# ============================================================
# DATA
# ============================================================

# Themes (main concepts) with their axial codes
data = {
    "themes": [
        {"id": "T1", "label": "Keterbatasan Sistem\nPencatatan Perilaku Siswa\nyang Berjalan", "color": "#4472C4"},
        {"id": "T2", "label": "Ketidakefisienan Alur\nPelaporan dan Komunikasi", "color": "#2E75B6"},
        {"id": "T3", "label": "Penghargaan dan Pembinaan\nKarakter Belum Terdokumentasi\nsecara Sistematis", "color": "#ED7D31"},
        {"id": "T4", "label": "Kebutuhan Fitur dan Fungsi\nSistem Informasi\nBerbasis Website", "color": "#70AD47"},
        {"id": "T5", "label": "Kesiapan, Tantangan, dan\nDukungan Implementasi\nSistem", "color": "#7030A0"},
    ],
    "axial": [
        {"id": "A1", "label": "Pencatatan perilaku\nberbasis manual", "parent": "T1"},
        {"id": "A2", "label": "Format pencatatan\ntidak terstandar", "parent": "T1"},
        {"id": "A3", "label": "Keterbatasan dokumentasi\nperilaku positif & prestasi", "parent": "T1"},
        {"id": "A4", "label": "Kesulitan pengelolaan\ndan pencarian data", "parent": "T1"},
        {"id": "A5", "label": "Alur pelaporan\ntidak efisien", "parent": "T2"},
        {"id": "A6", "label": "Komunikasi dengan\norang tua bersifat\ninsidental", "parent": "T2"},
        {"id": "A7", "label": "Penghargaan belum\nterstruktur dan\nterdokumentasi", "parent": "T3"},
        {"id": "A8", "label": "Proses pembinaan\nkarakter melalui\npembiasaan harian", "parent": "T3"},
        {"id": "A9", "label": "Kebutuhan fitur dan\nfungsi sistem informasi", "parent": "T4"},
        {"id": "A10", "label": "Ketersediaan infrastruktur\ndan kesiapan teknis", "parent": "T5"},
        {"id": "A11", "label": "Kekhawatiran dan potensi\nhambatan implementasi", "parent": "T5"},
        {"id": "A12", "label": "Dukungan dan\nkesiapan sekolah", "parent": "T5"},
    ],
    "links_theme": [
        ("T1", "T2", "is cause of"),
        ("T1", "T3", "is associated with"),
        ("T1", "T4", "motivates"),
        ("T2", "T4", "motivates"),
        ("T4", "T5", "is addressed by"),
        ("T3", "T5", "is associated with"),
    ],
}

# ============================================================
# ATLAS.ti-style LAYOUT (organic, free-form positions)
# ============================================================

# Manual positioning to resemble ATLAS.ti organic layout
# Themes are scattered, axial codes orbit around their parent theme

positions = {
    # Themes - spread out organically
    "T1": (480, 360),
    "T2": (1380, 280),
    "T3": (2180, 380),
    "T4": (900, 1100),
    "T5": (1900, 1100),
    # Axial codes - orbiting their parent themes
    "A1": (180, 200),
    "A2": (520, 130),
    "A3": (800, 300),
    "A4": (320, 570),
    "A5": (1150, 480),
    "A6": (1580, 500),
    "A7": (1950, 180),
    "A8": (2420, 540),
    "A9": (700, 1350),
    "A10": (1620, 1350),
    "A11": (2000, 1380),
    "A12": (2300, 1150),
}

# ============================================================
# SVG CONSTANTS (ATLAS.ti style)
# ============================================================

W = 2700
H = 1650
NODE_RX = 3  # very slight rounding like ATLAS.ti
THEME_W = 220
THEME_H = 62
AXIAL_W = 190
AXIAL_H = 52


def make_svg():
    svg = Element("svg", attrib={
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(W), "height": str(H),
        "viewBox": f"0 0 {W} {H}",
    })

    # Defs
    defs = SubElement(svg, "defs")
    # Arrowhead marker (ATLAS.ti uses small solid triangles)
    marker = SubElement(defs, "marker", attrib={
        "id": "arr", "markerWidth": "10", "markerHeight": "7",
        "refX": "10", "refY": "3.5", "orient": "auto", "markerUnits": "strokeWidth",
    })
    SubElement(marker, "polygon", attrib={"points": "0 0, 10 3.5, 0 7", "fill": "#555555"})

    # White background
    SubElement(svg, "rect", attrib={"width": str(W), "height": str(H), "fill": "white"})

    # Title bar (ATLAS.ti shows title at top)
    SubElement(svg, "rect", attrib={
        "x": "0", "y": "0", "width": str(W), "height": "45",
        "fill": "#f0f0f0", "stroke": "#cccccc", "stroke-width": "1"
    })
    t = SubElement(svg, "text", attrib={
        "x": "20", "y": "28",
        "font-family": "Segoe UI, Tahoma, sans-serif", "font-size": "13",
        "font-weight": "bold", "fill": "#333333"
    })
    t.text = "Network View: Hasil Koding Wawancara Kualitatif — Sistem Informasi Pemantauan Perilaku Siswa"

    # ================================================================
    # DRAW INTER-THEME LINKS (dashed, with relation label on the line)
    # ================================================================
    for src, dst, rel in data["links_theme"]:
        sx, sy = positions[src]
        dx, dy = positions[dst]
        # Offset from center to border
        angle = math.atan2(dy - sy, dx - sx)
        sx2 = sx + (THEME_W / 2 + 2) * math.cos(angle)
        sy2 = sy + (THEME_H / 2 + 2) * math.sin(angle)
        dx2 = dx - (THEME_W / 2 + 2) * math.cos(angle)
        dy2 = dy - (THEME_H / 2 + 2) * math.sin(angle)

        SubElement(svg, "line", attrib={
            "x1": str(sx2), "y1": str(sy2),
            "x2": str(dx2), "y2": str(dy2),
            "stroke": "#888888", "stroke-width": "1.3",
            "stroke-dasharray": "7,4",
            "marker-end": "url(#arr)",
        })
        # Relation label on line
        mx = (sx2 + dx2) / 2
        my = (sy2 + dy2) / 2
        # Background rect for text
        lbl_w = len(rel) * 6.5 + 10
        SubElement(svg, "rect", attrib={
            "x": str(mx - lbl_w / 2), "y": str(my - 8),
            "width": str(lbl_w), "height": "16", "rx": "2",
            "fill": "white", "stroke": "none",
        })
        lbl = SubElement(svg, "text", attrib={
            "x": str(mx), "y": str(my + 4),
            "text-anchor": "middle",
            "font-family": "Segoe UI, Tahoma, sans-serif",
            "font-size": "9", "font-style": "italic", "fill": "#666666",
        })
        lbl.text = rel

    # ================================================================
    # DRAW AXIAL → THEME LINKS (solid, "is part of" label)
    # ================================================================
    for ax in data["axial"]:
        aid = ax["id"]
        pid = ax["parent"]
        sx, sy = positions[aid]
        dx, dy = positions[pid]
        angle = math.atan2(dy - sy, dx - sx)
        sx2 = sx + (AXIAL_W / 2 + 2) * math.cos(angle)
        sy2 = sy + (AXIAL_H / 2 + 2) * math.sin(angle)
        dx2 = dx - (THEME_W / 2 + 2) * math.cos(angle)
        dy2 = dy - (THEME_H / 2 + 2) * math.sin(angle)

        SubElement(svg, "line", attrib={
            "x1": str(sx2), "y1": str(sy2),
            "x2": str(dx2), "y2": str(dy2),
            "stroke": "#555555", "stroke-width": "1.1",
            "marker-end": "url(#arr)",
        })
        # "is part of" label
        mx = (sx2 + dx2) / 2
        my = (sy2 + dy2) / 2
        SubElement(svg, "rect", attrib={
            "x": str(mx - 28), "y": str(my - 7),
            "width": "56", "height": "14", "rx": "2",
            "fill": "white", "stroke": "none",
        })
        lbl = SubElement(svg, "text", attrib={
            "x": str(mx), "y": str(my + 4),
            "text-anchor": "middle",
            "font-family": "Segoe UI, Tahoma, sans-serif",
            "font-size": "8", "fill": "#777777",
        })
        lbl.text = "is part of"

    # ================================================================
    # DRAW THEME NODES (ATLAS.ti style: colored header bar + white body)
    # ================================================================
    for theme in data["themes"]:
        tid = theme["id"]
        cx, cy = positions[tid]
        color = theme["color"]
        x = cx - THEME_W / 2
        y = cy - THEME_H / 2
        lines = theme["label"].split("\n")
        h = max(THEME_H, len(lines) * 15 + 20)

        # Main box (white body)
        SubElement(svg, "rect", attrib={
            "x": str(x), "y": str(y),
            "width": str(THEME_W), "height": str(h),
            "rx": str(NODE_RX), "ry": str(NODE_RX),
            "fill": "white", "stroke": color, "stroke-width": "2",
        })
        # Colored header bar
        SubElement(svg, "rect", attrib={
            "x": str(x), "y": str(y),
            "width": str(THEME_W), "height": "18",
            "rx": str(NODE_RX), "ry": str(NODE_RX),
            "fill": color, "stroke": "none",
        })
        # Fix bottom corners of header (cover rounded bottom)
        SubElement(svg, "rect", attrib={
            "x": str(x), "y": str(y + 14),
            "width": str(THEME_W), "height": "5",
            "fill": color, "stroke": "none",
        })
        # Node type label in header
        hdr = SubElement(svg, "text", attrib={
            "x": str(cx), "y": str(y + 13),
            "text-anchor": "middle",
            "font-family": "Segoe UI, Tahoma, sans-serif",
            "font-size": "9", "font-weight": "bold", "fill": "white",
        })
        hdr.text = f"● {tid} [Tema]"

        # Body text
        text_y = y + 30
        for i, line in enumerate(lines):
            lt = SubElement(svg, "text", attrib={
                "x": str(cx), "y": str(text_y + i * 14),
                "text-anchor": "middle",
                "font-family": "Segoe UI, Tahoma, sans-serif",
                "font-size": "10", "font-weight": "bold", "fill": "#222222",
            })
            lt.text = line

    # ================================================================
    # DRAW AXIAL CODE NODES (ATLAS.ti style: yellow-ish header + white body)
    # ================================================================
    axial_color = "#D4A017"
    axial_bg = "#FFF9E6"

    for ax in data["axial"]:
        aid = ax["id"]
        cx, cy = positions[aid]
        lines = ax["label"].split("\n")
        h = max(AXIAL_H, len(lines) * 13 + 22)
        x = cx - AXIAL_W / 2
        y = cy - h / 2

        # Main box
        SubElement(svg, "rect", attrib={
            "x": str(x), "y": str(y),
            "width": str(AXIAL_W), "height": str(h),
            "rx": str(NODE_RX), "ry": str(NODE_RX),
            "fill": axial_bg, "stroke": axial_color, "stroke-width": "1.5",
        })
        # Header bar
        SubElement(svg, "rect", attrib={
            "x": str(x), "y": str(y),
            "width": str(AXIAL_W), "height": "16",
            "rx": str(NODE_RX), "ry": str(NODE_RX),
            "fill": axial_color, "stroke": "none",
        })
        SubElement(svg, "rect", attrib={
            "x": str(x), "y": str(y + 12),
            "width": str(AXIAL_W), "height": "5",
            "fill": axial_color, "stroke": "none",
        })
        # Header text
        hdr = SubElement(svg, "text", attrib={
            "x": str(cx), "y": str(y + 12),
            "text-anchor": "middle",
            "font-family": "Segoe UI, Tahoma, sans-serif",
            "font-size": "8", "font-weight": "bold", "fill": "white",
        })
        hdr.text = f"○ {aid} [Axial Code]"

        # Body text
        text_y = y + 27
        for i, line in enumerate(lines):
            lt = SubElement(svg, "text", attrib={
                "x": str(cx), "y": str(text_y + i * 12),
                "text-anchor": "middle",
                "font-family": "Segoe UI, Tahoma, sans-serif",
                "font-size": "9", "fill": "#333333",
            })
            lt.text = line

    # ================================================================
    # LEGEND (bottom-right, ATLAS.ti style)
    # ================================================================
    lg_x = W - 380
    lg_y = H - 90
    SubElement(svg, "rect", attrib={
        "x": str(lg_x), "y": str(lg_y),
        "width": "360", "height": "75", "rx": "3",
        "fill": "#fafafa", "stroke": "#cccccc", "stroke-width": "0.8",
    })
    lt = SubElement(svg, "text", attrib={
        "x": str(lg_x + 10), "y": str(lg_y + 15),
        "font-family": "Segoe UI, Tahoma, sans-serif",
        "font-size": "9", "font-weight": "bold", "fill": "#333",
    })
    lt.text = "LEGENDA"

    # Theme example
    SubElement(svg, "rect", attrib={
        "x": str(lg_x + 10), "y": str(lg_y + 22),
        "width": "50", "height": "18", "rx": "2",
        "fill": "white", "stroke": "#4472C4", "stroke-width": "1.5",
    })
    SubElement(svg, "rect", attrib={
        "x": str(lg_x + 10), "y": str(lg_y + 22),
        "width": "50", "height": "8", "rx": "2",
        "fill": "#4472C4",
    })
    lt2 = SubElement(svg, "text", attrib={
        "x": str(lg_x + 70), "y": str(lg_y + 35),
        "font-family": "Segoe UI, Tahoma, sans-serif", "font-size": "9", "fill": "#333",
    })
    lt2.text = "= Tema (Theme)"

    # Axial example
    SubElement(svg, "rect", attrib={
        "x": str(lg_x + 10), "y": str(lg_y + 47),
        "width": "50", "height": "18", "rx": "2",
        "fill": "#FFF9E6", "stroke": "#D4A017", "stroke-width": "1.2",
    })
    SubElement(svg, "rect", attrib={
        "x": str(lg_x + 10), "y": str(lg_y + 47),
        "width": "50", "height": "8", "rx": "2",
        "fill": "#D4A017",
    })
    lt3 = SubElement(svg, "text", attrib={
        "x": str(lg_x + 70), "y": str(lg_y + 60),
        "font-family": "Segoe UI, Tahoma, sans-serif", "font-size": "9", "fill": "#333",
    })
    lt3.text = "= Axial Code (Kategori)"

    # Link legends
    SubElement(svg, "line", attrib={
        "x1": str(lg_x + 180), "y1": str(lg_y + 32),
        "x2": str(lg_x + 220), "y2": str(lg_y + 32),
        "stroke": "#555", "stroke-width": "1.2", "marker-end": "url(#arr)",
    })
    lt4 = SubElement(svg, "text", attrib={
        "x": str(lg_x + 225), "y": str(lg_y + 35),
        "font-family": "Segoe UI, Tahoma, sans-serif", "font-size": "9", "fill": "#333",
    })
    lt4.text = "= is part of"

    SubElement(svg, "line", attrib={
        "x1": str(lg_x + 180), "y1": str(lg_y + 55),
        "x2": str(lg_x + 220), "y2": str(lg_y + 55),
        "stroke": "#888", "stroke-width": "1.2",
        "stroke-dasharray": "7,4", "marker-end": "url(#arr)",
    })
    lt5 = SubElement(svg, "text", attrib={
        "x": str(lg_x + 225), "y": str(lg_y + 58),
        "font-family": "Segoe UI, Tahoma, sans-serif", "font-size": "9", "fill": "#333",
    })
    lt5.text = "= relasi antar tema"

    # Source label
    src = SubElement(svg, "text", attrib={
        "x": str(W - 20), "y": str(H - 10),
        "text-anchor": "end",
        "font-family": "Segoe UI, Tahoma, sans-serif",
        "font-size": "8", "fill": "#aaaaaa",
    })
    src.text = "Sumber: KS, WK6, WK2, OS | Analisis Tematik Braun & Clarke (2006)"

    return svg


# ============================================================
# GENERATE AND WRITE
# ============================================================
svg = make_svg()
ET.indent(svg, space="  ")
tree = ET.ElementTree(svg)
out = "/projects/sandbox/kodingdiagram/outputs/network_view_diagram.svg"
tree.write(out, encoding="unicode", xml_declaration=True)
print(f"✓ ATLAS.ti-style Network View written to: {out}")
print(f"  Canvas: {W}x{H}")
print(f"  Themes: {len(data['themes'])}")
print(f"  Axial Codes: {len(data['axial'])}")
print(f"  Inter-theme relations: {len(data['links_theme'])}")
