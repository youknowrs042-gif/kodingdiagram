#!/usr/bin/env python3
"""Generate ATLAS.ti-style Network View Diagram as SVG.

Uses only Python standard library (no external dependencies).
Produces a professional qualitative research network diagram.
"""

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
import math

# ============================================================
# DATA: Themes → Axial Codes → Open Codes
# ============================================================

themes = [
    {
        "id": "T1",
        "name": "Keterbatasan Sistem\nPencatatan Perilaku Siswa\nyang Berjalan",
        "color": "#4472C4",
        "bg": "#DAE3F3",
        "axial": [
            {
                "id": "A1",
                "name": "Pencatatan perilaku\nberbasis manual",
                "open": [
                    "Pencatatan manual (KS, WK6, WK2)",
                    "Buku absensi/jurnal (KS)",
                    "Buku anekdot (KS, WK6)",
                    "Data perilaku belum digital (OS)",
                    "Guru kelas penanggung jawab (KS)",
                ]
            },
            {
                "id": "A2",
                "name": "Format pencatatan\ntidak terstandar",
                "open": [
                    "Format tidak seragam (KS, WK6)",
                    "Bergantung kebiasaan guru (KS)",
                    "Keterlambatan belum detail (KS, WK2)",
                    "Belum ada pengelompokan (OS)",
                ]
            },
            {
                "id": "A3",
                "name": "Keterbatasan dokumentasi\nperilaku positif & prestasi",
                "open": [
                    "Fokus pelanggaran (KS)",
                    "Perilaku positif belum tercatat (KS, WK6)",
                    "Pencatatan harus seimbang (WK6)",
                    "Potensi siswa belum terdokumentasi (KS)",
                    "Penguatan positif penting (WK2)",
                ]
            },
            {
                "id": "A4",
                "name": "Kesulitan pengelolaan\ndan pencarian data",
                "open": [
                    "Data sulit dicari kembali (KS)",
                    "Data rawan hilang/rusak (KS, OS)",
                    "Data tersebar/tidak terpusat (KS, OS)",
                    "Rekapitulasi memakan waktu (KS)",
                    "Keterbatasan waktu pencatatan (WK6, WK2)",
                ]
            },
        ]
    },
    {
        "id": "T2",
        "name": "Ketidakefisienan Alur\nPelaporan dan Komunikasi",
        "color": "#2E75B6",
        "bg": "#D6E8F7",
        "axial": [
            {
                "id": "A5",
                "name": "Alur pelaporan\ntidak efisien",
                "open": [
                    "Alur pelaporan konvensional (KS)",
                    "Pengawasan manajerial kurang praktis (KS)",
                    "Pelaporan situasional (WK6)",
                ]
            },
            {
                "id": "A6",
                "name": "Komunikasi dengan orang tua\nbersifat insidental",
                "open": [
                    "Komunikasi orang tua manual (KS, WK6)",
                    "Informasi terlambat ke orang tua (KS)",
                    "Komunikasi via WhatsApp (WK2)",
                    "Notifikasi perlu diatur (WK6, WK2)",
                    "Peran orang tua besar di kelas rendah (WK2)",
                    "Kendala komunikasi orang tua (WK2)",
                ]
            },
        ]
    },
    {
        "id": "T3",
        "name": "Penghargaan dan Pembinaan\nKarakter Belum Terdokumentasi\nsecara Sistematis",
        "color": "#ED7D31",
        "bg": "#FBE5D6",
        "axial": [
            {
                "id": "A7",
                "name": "Penghargaan belum terstruktur\ndan terdokumentasi",
                "open": [
                    "Penghargaan sederhana (KS)",
                    "Penghargaan belum terdokumentasi (KS)",
                    "Apresiasi lisan (KS)",
                    "Reward spontan (WK2, WK6)",
                    "Pencatatan reward belum direkap (WK2)",
                    "Penghargaan terstruktur belum berjalan (WK6)",
                ]
            },
            {
                "id": "A8",
                "name": "Proses pembinaan karakter\nmelalui pembiasaan harian",
                "open": [
                    "Teguran bertahap (KS)",
                    "Tindak lanjut belum terdokumentasi (KS)",
                    "Rekam jejak pembinaan penting (KS)",
                    "Pembinaan karakter harian (WK6)",
                    "Dokumentasi pembinaan belum tertata (WK6)",
                    "Pembinaan melalui pembiasaan (WK2)",
                    "Pencatatan membantu pemahaman guru (WK2)",
                ]
            },
        ]
    },
    {
        "id": "T4",
        "name": "Kebutuhan Fitur dan Fungsi\nSistem Informasi\nBerbasis Website",
        "color": "#70AD47",
        "bg": "#E2EFDA",
        "axial": [
            {
                "id": "A9",
                "name": "Kebutuhan fitur dan\nfungsi sistem informasi",
                "open": [
                    "Kebutuhan fitur lengkap (KS)",
                    "Kebutuhan rekap otomatis (KS, WK6, WK2)",
                    "Sistem harus ringan & mobile (KS, OS)",
                    "Kebutuhan pencatatan cepat (WK6, WK2)",
                    "Kebutuhan sistem poin (WK6, WK2)",
                    "Kebutuhan fitur pencarian (OS)",
                    "Kebutuhan laporan otomatis (OS)",
                    "Kebutuhan pembagian akses (OS)",
                    "Kebutuhan keamanan data (OS)",
                    "Tampilan sederhana & ringkas (OS)",
                    "Kebutuhan pemantauan menyeluruh (KS)",
                    "Sistem poin perilaku otomatis (OS)",
                    "Kebutuhan data komprehensif (OS)",
                    "Kebutuhan digitalisasi data (OS)",
                    "Laporan disesuaikan audiens (WK2)",
                ]
            },
        ]
    },
    {
        "id": "T5",
        "name": "Kesiapan, Tantangan,\ndan Dukungan\nImplementasi Sistem",
        "color": "#7030A0",
        "bg": "#E8D5F5",
        "axial": [
            {
                "id": "A10",
                "name": "Ketersediaan infrastruktur\ndan kesiapan teknis",
                "open": [
                    "Internet tersedia tapi fluktuatif (OS)",
                    "Perangkat tersedia (OS)",
                    "Literasi teknologi guru bervariasi (OS)",
                    "Belum pernah pakai aplikasi khusus (WK6, WK2)",
                ]
            },
            {
                "id": "A11",
                "name": "Kekhawatiran dan potensi\nhambatan implementasi",
                "open": [
                    "Kekhawatiran kesiapan guru (KS)",
                    "Kekhawatiran jaringan internet (KS)",
                    "Kekhawatiran sistem rumit (WK6, WK2)",
                    "Kebutuhan pelatihan & pendampingan (WK2, OS)",
                    "Hambatan kebiasaan manual (OS)",
                    "Kemampuan teknologi tidak merata (OS)",
                ]
            },
            {
                "id": "A12",
                "name": "Dukungan dan\nkesiapan sekolah",
                "open": [
                    "Dukungan terhadap sistem website (KS)",
                    "Dukungan sekolah (KS)",
                    "Implementasi bertahap (KS, OS)",
                    "Sistem diterima jika sederhana (OS)",
                    "Dukungan teknis operator (OS)",
                    "Membantu pengawasan kepala sekolah (OS)",
                    "Manfaat untuk guru (OS)",
                ]
            },
        ]
    },
]

inter_theme_relations = [
    ("T1", "T2", "is cause of"),
    ("T1", "T3", "is associated with"),
    ("T1", "T4", "motivates"),
    ("T2", "T4", "motivates"),
    ("T4", "T5", "is addressed by"),
    ("T3", "T5", "is associated with"),
]

# ============================================================
# SVG GENERATION
# ============================================================

W = 2800  # canvas width
H = 2200  # canvas height

# Layout zones for each theme (x_center, y_theme)
theme_positions = {
    "T1": (420, 250),
    "T2": (1200, 250),
    "T3": (2050, 250),
    "T4": (700, 1350),
    "T5": (1950, 1350),
}


def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def multiline_text(parent, x, y, text, font_size=11, font_weight="normal", fill="#333333", anchor="middle"):
    """Add multiline text as tspan elements."""
    lines = text.split("\n")
    text_el = SubElement(parent, "text", attrib={
        "x": str(x), "y": str(y),
        "text-anchor": anchor,
        "font-family": "Segoe UI, Arial, sans-serif",
        "font-size": str(font_size),
        "font-weight": font_weight,
        "fill": fill,
    })
    for i, line in enumerate(lines):
        tspan = SubElement(text_el, "tspan", attrib={
            "x": str(x),
            "dy": str(0 if i == 0 else font_size + 2),
        })
        tspan.text = escape_xml(line)
    return text_el


def draw_rounded_rect(parent, x, y, w, h, rx=6, fill="#fff", stroke="#333", stroke_width=1.5, opacity=1.0):
    """Draw a rounded rectangle."""
    attribs = {
        "x": str(x), "y": str(y),
        "width": str(w), "height": str(h),
        "rx": str(rx), "ry": str(rx),
        "fill": fill, "stroke": stroke,
        "stroke-width": str(stroke_width),
    }
    if opacity < 1.0:
        attribs["opacity"] = str(opacity)
    return SubElement(parent, "rect", attrib=attribs)


def draw_arrow(parent, x1, y1, x2, y2, color="#595959", width=1.2, dashed=False, marker="url(#arrowhead)"):
    """Draw a line with arrowhead."""
    attribs = {
        "x1": str(x1), "y1": str(y1),
        "x2": str(x2), "y2": str(y2),
        "stroke": color,
        "stroke-width": str(width),
        "marker-end": marker,
    }
    if dashed:
        attribs["stroke-dasharray"] = "6,4"
    return SubElement(parent, "line", attrib=attribs)


def draw_relation_label(parent, x1, y1, x2, y2, label, color="#595959"):
    """Draw a relation label at midpoint of a line."""
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    # Background
    lw = len(label) * 5.5 + 8
    draw_rounded_rect(parent, mx - lw/2, my - 8, lw, 16, rx=3, fill="white", stroke="none", stroke_width=0)
    multiline_text(parent, mx, my + 4, label, font_size=9, fill=color, font_weight="normal")


# Create SVG root
svg = Element("svg", attrib={
    "xmlns": "http://www.w3.org/2000/svg",
    "width": str(W),
    "height": str(H),
    "viewBox": f"0 0 {W} {H}",
})

# Defs (arrowheads)
defs = SubElement(svg, "defs")
# Solid arrowhead
marker = SubElement(defs, "marker", attrib={
    "id": "arrowhead", "markerWidth": "8", "markerHeight": "6",
    "refX": "8", "refY": "3", "orient": "auto",
})
SubElement(marker, "polygon", attrib={"points": "0 0, 8 3, 0 6", "fill": "#595959"})

# Dashed arrowhead
marker2 = SubElement(defs, "marker", attrib={
    "id": "arrowhead-gray", "markerWidth": "8", "markerHeight": "6",
    "refX": "8", "refY": "3", "orient": "auto",
})
SubElement(marker2, "polygon", attrib={"points": "0 0, 8 3, 0 6", "fill": "#888888"})

# Drop shadow filter
filt = SubElement(defs, "filter", attrib={"id": "shadow", "x": "-2%", "y": "-2%", "width": "104%", "height": "104%"})
SubElement(filt, "feDropShadow", attrib={"dx": "1", "dy": "2", "stdDeviation": "2", "flood-opacity": "0.15"})

# Background
SubElement(svg, "rect", attrib={"width": str(W), "height": str(H), "fill": "#FAFBFC"})

# Title
multiline_text(svg, W//2, 35, "NETWORK VIEW \u2014 Hasil Koding Wawancara Kualitatif", font_size=20, font_weight="bold", fill="#1a1a1a")
multiline_text(svg, W//2, 60, "Pengembangan Sistem Informasi Pemantauan Perilaku Siswa Berbasis Website dalam Mendukung Manajemen Pembinaan Karakter di Sekolah Dasar", font_size=11, fill="#555555")
multiline_text(svg, W//2, 80, "Sumber Data: KS (Kepala Sekolah) \u2022 WK6 (Wali Kelas 6) \u2022 WK2 (Wali Kelas 2) \u2022 OS (Operator Sekolah)", font_size=10, fill="#777777")

# ============================================================
# DRAW INTER-THEME RELATIONS (behind everything)
# ============================================================
# We draw these first (behind nodes)
relation_group = SubElement(svg, "g", attrib={"id": "relations"})

theme_node_centers = {}  # will be filled when drawing themes

# ============================================================
# DRAW THEMES, AXIAL CODES, OPEN CODES
# ============================================================

THEME_W = 260
THEME_H = 70
AXIAL_W = 220
AXIAL_H = 46
OPEN_W = 200
OPEN_H = 22

node_positions = {}  # id -> (cx, cy)

for theme in themes:
    tid = theme["id"]
    tx, ty = theme_positions[tid]
    tc = theme["color"]
    tbg = theme["bg"]
    
    # Theme node
    theme_x = tx - THEME_W // 2
    theme_y = ty - THEME_H // 2
    draw_rounded_rect(svg, theme_x, theme_y, THEME_W, THEME_H, rx=8, fill=tbg, stroke=tc, stroke_width=2.2)
    
    lines = theme["name"].split("\n")
    text_start_y = ty - (len(lines) - 1) * 7
    for i, line in enumerate(lines):
        multiline_text(svg, tx, text_start_y + i * 14, line, font_size=11, font_weight="bold", fill="#1a1a1a")
    
    node_positions[tid] = (tx, ty)
    theme_node_centers[tid] = (tx, ty)
    
    # Calculate axial positions
    n_axial = len(theme["axial"])
    axial_start_y = ty + THEME_H // 2 + 60
    
    # Spread axial codes horizontally
    if n_axial == 1:
        axial_xs = [tx]
    elif n_axial == 2:
        axial_xs = [tx - 145, tx + 145]
    elif n_axial == 3:
        axial_xs = [tx - 240, tx, tx + 240]
    else:
        spacing = 240
        total_w = (n_axial - 1) * spacing
        axial_xs = [tx - total_w // 2 + i * spacing for i in range(n_axial)]
    
    for ai, axial in enumerate(theme["axial"]):
        aid = axial["id"]
        ax = axial_xs[ai]
        ay = axial_start_y
        
        # Draw arrow from theme to axial
        draw_arrow(svg, tx, ty + THEME_H // 2, ax, ay - AXIAL_H // 2, color=tc, width=1.5)
        
        # Axial node
        axial_x = ax - AXIAL_W // 2
        axial_y = ay - AXIAL_H // 2
        draw_rounded_rect(svg, axial_x, axial_y, AXIAL_W, AXIAL_H, rx=5, fill="#FFF8E1", stroke="#FFC107", stroke_width=1.5)
        
        a_lines = axial["name"].split("\n")
        a_text_y = ay - (len(a_lines) - 1) * 6
        for i, line in enumerate(a_lines):
            multiline_text(svg, ax, a_text_y + i * 12, line, font_size=9, font_weight="bold", fill="#333333")
        
        # Relation label "is part of"
        mid_x = (tx + ax) / 2
        mid_y = (ty + THEME_H // 2 + ay - AXIAL_H // 2) / 2
        
        node_positions[aid] = (ax, ay)
        
        # Open codes
        n_open = len(axial["open"])
        open_start_y = ay + AXIAL_H // 2 + 30
        
        for oi, ocode in enumerate(axial["open"]):
            ox = ax
            oy = open_start_y + oi * (OPEN_H + 6)
            
            # Draw line from axial to open code
            if oi == 0:
                draw_arrow(svg, ax, ay + AXIAL_H // 2, ox, oy - OPEN_H // 2 + 2,
                          color=tc + "99", width=0.8, marker="")
            
            # Open code node
            open_x = ox - OPEN_W // 2
            open_y = oy - OPEN_H // 2
            draw_rounded_rect(svg, open_x, open_y, OPEN_W, OPEN_H, rx=3,
                            fill="white", stroke=tc + "77", stroke_width=0.7)
            
            # Truncate text if needed
            display_text = ocode if len(ocode) <= 38 else ocode[:35] + "..."
            multiline_text(svg, ox, oy + 4, display_text, font_size=8, fill="#444444")
        
        # Draw single connection line from axial to first open code group
        if n_open > 0:
            # Vertical line connecting all open codes
            first_oy = open_start_y - OPEN_H // 2 + 2
            last_oy = open_start_y + (n_open - 1) * (OPEN_H + 6)
            SubElement(svg, "line", attrib={
                "x1": str(ax - OPEN_W // 2 - 5),
                "y1": str(first_oy),
                "x2": str(ax - OPEN_W // 2 - 5),
                "y2": str(last_oy),
                "stroke": tc + "44",
                "stroke-width": "1.5",
            })
            # Connection from axial to the vertical line
            SubElement(svg, "line", attrib={
                "x1": str(ax),
                "y1": str(ay + AXIAL_H // 2),
                "x2": str(ax - OPEN_W // 2 - 5),
                "y2": str(first_oy),
                "stroke": tc + "66",
                "stroke-width": "1",
            })
            # Small dots on each open code connection
            for oi in range(n_open):
                oy = open_start_y + oi * (OPEN_H + 6)
                SubElement(svg, "line", attrib={
                    "x1": str(ax - OPEN_W // 2 - 5),
                    "y1": str(oy),
                    "x2": str(ax - OPEN_W // 2),
                    "y2": str(oy),
                    "stroke": tc + "66",
                    "stroke-width": "0.8",
                })

# ============================================================
# DRAW INTER-THEME RELATIONS (on top with dashed lines)
# ============================================================

for src_id, dst_id, label in inter_theme_relations:
    sx, sy = theme_node_centers[src_id]
    dx, dy = theme_node_centers[dst_id]
    
    # Calculate edge points (from border of theme box)
    angle = math.atan2(dy - sy, dx - sx)
    
    # Start from edge of source
    sx2 = sx + (THEME_W // 2 + 5) * math.cos(angle)
    sy2 = sy + (THEME_H // 2 + 5) * math.sin(angle)
    
    # End at edge of destination
    dx2 = dx - (THEME_W // 2 + 5) * math.cos(angle)
    dy2 = dy - (THEME_H // 2 + 5) * math.sin(angle)
    
    draw_arrow(svg, sx2, sy2, dx2, dy2, color="#888888", width=1.5, dashed=True, marker="url(#arrowhead-gray)")
    draw_relation_label(svg, sx2, sy2, dx2, dy2, label, "#666666")

# ============================================================
# LEGEND
# ============================================================
leg_y = H - 70
leg_x = 100

# Legend background
draw_rounded_rect(svg, leg_x - 20, leg_y - 20, 700, 55, rx=5, fill="white", stroke="#ddd", stroke_width=1)
multiline_text(svg, leg_x + 10, leg_y, "LEGENDA:", font_size=10, font_weight="bold", fill="#333", anchor="start")

# Theme box
draw_rounded_rect(svg, leg_x + 80, leg_y - 12, 60, 22, rx=4, fill="#DAE3F3", stroke="#4472C4", stroke_width=1.5)
multiline_text(svg, leg_x + 110, leg_y + 4, "Tema", font_size=9, font_weight="bold")

# Axial box
draw_rounded_rect(svg, leg_x + 170, leg_y - 12, 80, 22, rx=4, fill="#FFF8E1", stroke="#FFC107", stroke_width=1.5)
multiline_text(svg, leg_x + 210, leg_y + 4, "Axial Code", font_size=9, font_weight="bold")

# Open code box
draw_rounded_rect(svg, leg_x + 280, leg_y - 12, 80, 22, rx=3, fill="white", stroke="#4472C477", stroke_width=0.7)
multiline_text(svg, leg_x + 320, leg_y + 4, "Open Code", font_size=9)

# Arrow solid
draw_arrow(svg, leg_x + 385, leg_y, leg_x + 420, leg_y, color="#595959", width=1.2)
multiline_text(svg, leg_x + 445, leg_y + 4, "is part of", font_size=9, fill="#595959", anchor="start")

# Arrow dashed
draw_arrow(svg, leg_x + 510, leg_y, leg_x + 545, leg_y, color="#888", width=1.2, dashed=True, marker="url(#arrowhead-gray)")
multiline_text(svg, leg_x + 560, leg_y + 4, "relasi antar tema", font_size=9, fill="#666", anchor="start")

# ============================================================
# OUTPUT
# ============================================================
ET.indent(svg, space="  ")
tree = ET.ElementTree(svg)
output_path = "/projects/sandbox/kodingdiagram/outputs/network_view_diagram.svg"
tree.write(output_path, encoding="unicode", xml_declaration=True)
print(f"SVG written to: {output_path}")
print(f"Canvas: {W}x{H}px")
