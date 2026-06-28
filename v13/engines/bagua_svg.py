"""Bagua chart SVG generators — Python port of Codex JS.

Source: codex-bagua-chart-kit/src/baguaCharts.js + geometry.js
Approved fixture: codexBaguaFixture (labels hardcoded, no OCR, no MD coords).
"""
from __future__ import annotations
import math, re

# ── Geometry helpers ──────────────────────────────────────────

def _round(value: float, places: int = 2) -> float:
    factor = 10 ** places
    return math.floor(float(value) * factor + 0.5) / factor


def poly_points(points: list) -> str:
    return " ".join(f"{_round(x)},{_round(y)}" for x, y in points)


def polar_point(center: dict, angle_deg: float, radius_x: float, radius_y: float | None = None) -> list:
    if radius_y is None:
        radius_y = radius_x
    rad = math.radians(angle_deg)
    return [_round(center["x"] + math.cos(rad) * radius_x),
            _round(center["y"] + math.sin(rad) * radius_y)]


def regular_polygon(center: dict, radius: float, sides: int, start_angle_deg: float = -112.5) -> list:
    return [polar_point(center, start_angle_deg + i * (360 / sides), radius) for i in range(sides)]


def rect_side_guide_points(rect: dict, ratios: list | None = None) -> dict:
    if ratios is None:
        ratios = [1/3, 2/3]
    a, b = ratios
    right  = rect["x"] + rect["w"]
    bottom = rect["y"] + rect["h"]
    xA = rect["x"] + rect["w"] * a
    xB = rect["x"] + rect["w"] * b
    yA = rect["y"] + rect["h"] * a
    yB = rect["y"] + rect["h"] * b
    return {
        "center": [_round(rect["x"] + rect["w"] / 2), _round(rect["y"] + rect["h"] / 2)],
        1: [_round(xA), _round(rect["y"])],
        2: [_round(xB), _round(rect["y"])],
        3: [_round(right), _round(yA)],
        4: [_round(right), _round(yB)],
        5: [_round(xB), _round(bottom)],
        6: [_round(xA), _round(bottom)],
        7: [_round(rect["x"]), _round(yB)],
        8: [_round(rect["x"]), _round(yA)],
    }


def rect_side_guide_lines(rect: dict, ratios: list | None = None) -> list:
    if ratios is None:
        ratios = [1/3, 2/3]
    points = rect_side_guide_points(rect, ratios)
    return [
        {"from": f, "to": t, "line": points[f] + points[t]}
        for f, t in [(1, 5), (2, 6), (8, 4), (7, 3)]
    ]


def line_passes_through_point(line: list, point: list, tolerance: float = 0.5) -> bool:
    x1, y1, x2, y2 = line
    px, py = point
    dx, dy = x2 - x1, y2 - y1
    cross_val = abs((px - x1) * dy - (py - y1) * dx)
    length = math.hypot(dx, dy) or 1
    within_x = min(x1, x2) - tolerance <= px <= max(x1, x2) + tolerance
    within_y = min(y1, y2) - tolerance <= py <= max(y1, y2) + tolerance
    return (cross_val / length) <= tolerance and within_x and within_y


# ── Palette ───────────────────────────────────────────────────

PALETTE = {
    "bg":       "#101821",
    "cyan":     "#21e7ff",
    "cyanSoft": "#75f6ff",
    "green":    "#74ff91",
    "pink":     "#ff91aa",
    "yellow":   "#fff0a6",
    "white":    "#f8fbff",
    "blue":     "#35a6ff",
    "violet":   "#d6a4ff",
    "gray":     "#aeb7bc",
    "ink":      "#09131d",
}

_LABEL_COLOR = {
    "great":     PALETTE["cyanSoft"],
    "good":      PALETTE["green"],
    "bad":       PALETTE["pink"],
    "element":   PALETTE["yellow"],
    "neutral":   PALETTE["white"],
    "direction": PALETTE["cyan"],
    "water":     PALETTE["blue"],
    "wood":      PALETTE["green"],
    "metal":     PALETTE["white"],
    "earth":     PALETTE["yellow"],
    "violet":    PALETTE["violet"],
    "gray":      PALETTE["gray"],
}


# ── Fixture (approved Codex labels — no OCR, no MD coords) ────

CODEX_BAGUA_FIXTURE = {
    "rectSkeleton": {
        "viewBox":     {"w": 1000, "h": 760},
        "frame":       {"x": 105, "y": 90, "w": 790, "h": 500},
        "guideRatios": [1/3, 2/3],
        "labels": [
            {"sector": 1, "x": 500, "y": 30,  "text": "Depan Rumah",        "color": "good",     "size": 16},
            {"sector": 1, "x": 500, "y": 76,  "text": "Baik Kecil",         "color": "direction","size": 16},
            {"sector": 1, "x": 500, "y": 122, "text": "Bantuan",            "color": "direction","size": 14},
            {"sector": 1, "x": 500, "y": 172, "text": "Posisi Tenang",      "color": "direction","size": 14},
            {"sector": 1, "x": 600, "y": 128, "text": "Kayu",               "color": "wood",     "size": 18},
            {"sector": 8, "x": 210, "y": 168, "text": "Baik Sedang",        "color": "direction","size": 14},
            {"sector": 8, "x": 325, "y": 140, "text": "Tanah",              "color": "earth",    "size": 17},
            {"sector": 8, "x": 205, "y": 208, "text": "Panjang Umur",       "color": "direction","size": 13},
            {"sector": 8, "x": 250, "y": 252, "text": "Melodi Perang",      "color": "direction","size": 13},
            {"sector": 8, "x": 358, "y": 188, "text": "Timur Kayu",         "color": "wood",     "size": 14},
            {"sector": 8, "x": 420, "y": 252, "text": "Gua Xun",            "color": "direction","size": 14},
            {"sector": 2, "x": 755, "y": 148, "text": "Sangat Baik",        "color": "great",    "size": 18},
            {"sector": 2, "x": 705, "y": 190, "text": "Pintu Besar",        "color": "neutral",  "size": 15},
            {"sector": 2, "x": 650, "y": 232, "text": "Dokter Langit",      "color": "direction","size": 14},
            {"sector": 2, "x": 812, "y": 218, "text": "Logam",              "color": "metal",    "size": 16},
            {"sector": 2, "x": 560, "y": 272, "text": "Api Selatan",        "color": "bad",      "size": 15},
            {"sector": 2, "x": 642, "y": 306, "text": "Api Li",             "color": "bad",      "size": 15},
            {"sector": 3, "x": 720, "y": 340, "text": "Barat Daya",         "color": "direction","size": 14},
            {"sector": 3, "x": 722, "y": 385, "text": "Tanah Kun",          "color": "earth",    "size": 15},
            {"sector": 3, "x": 855, "y": 350, "text": "Integritas",         "color": "bad",      "size": 14},
            {"sector": 3, "x": 830, "y": 430, "text": "Bahaya Celaka",      "color": "bad",      "size": 13},
            {"sector": 3, "x": 940, "y": 395, "text": "Buruk Besar",        "color": "bad",      "size": 16},
            {"sector": 3, "x": 835, "y": 478, "text": "Api",                "color": "bad",      "size": 17},
            {"sector": 4, "x": 625, "y": 492, "text": "Qian Logam",         "color": "metal",    "size": 15},
            {"sector": 4, "x": 720, "y": 524, "text": "Barat Laut",         "color": "neutral",  "size": 14},
            {"sector": 4, "x": 825, "y": 538, "text": "Enam Sha",           "color": "bad",      "size": 14},
            {"sector": 4, "x": 888, "y": 576, "text": "Melodi Sastra",      "color": "bad",      "size": 13},
            {"sector": 4, "x": 780, "y": 648, "text": "Simpan Berkah",      "color": "bad",      "size": 13},
            {"sector": 4, "x": 874, "y": 676, "text": "Buruk Kecil",        "color": "bad",      "size": 15},
            {"sector": 4, "x": 665, "y": 672, "text": "Tanah",              "color": "earth",    "size": 17},
            {"sector": 5, "x": 500, "y": 520, "text": "Qian Logam",         "color": "metal",    "size": 15},
            {"sector": 5, "x": 500, "y": 572, "text": "Air Kan",            "color": "water",    "size": 16},
            {"sector": 5, "x": 500, "y": 612, "text": "Utara Air",          "color": "violet",   "size": 15},
            {"sector": 5, "x": 500, "y": 650, "text": "Energi Hidup",       "color": "direction","size": 14},
            {"sector": 5, "x": 500, "y": 676, "text": "Serigala Hasrat",    "color": "direction","size": 13},
            {"sector": 6, "x": 105, "y": 368, "text": "Buruk Besar",        "color": "bad",      "size": 16},
            {"sector": 6, "x": 205, "y": 440, "text": "Putus Nasib",        "color": "bad",      "size": 14},
            {"sector": 6, "x": 300, "y": 385, "text": "Pasukan Penghancur", "color": "bad",      "size": 12},
            {"sector": 6, "x": 300, "y": 338, "text": "Tanah Gen",          "color": "earth",    "size": 14},
            {"sector": 6, "x": 360, "y": 430, "text": "Utara Utama",        "color": "direction","size": 14},
            {"sector": 7, "x": 185, "y": 510, "text": "Kayu",               "color": "wood",     "size": 18},
            {"sector": 7, "x": 205, "y": 582, "text": "Energi Hidup",       "color": "direction","size": 14},
            {"sector": 7, "x": 328, "y": 536, "text": "Air Kan",            "color": "water",    "size": 15},
            {"sector": 7, "x": 244, "y": 626, "text": "Baik Atas",          "color": "direction","size": 14},
            {"sector": 7, "x": 382, "y": 596, "text": "Tanah",              "color": "earth",    "size": 16},
            {"sector": 0, "x": 500, "y": 334, "text": "Selatan Utama",      "color": "direction","size": 13},
            {"sector": 0, "x": 500, "y": 414, "text": "Utara-Barat",        "color": "neutral",  "size": 13},
            {"sector": 0, "x": 392, "y": 358, "text": "Timur",              "color": "direction","size": 14},
            {"sector": 0, "x": 590, "y": 370, "text": "Selatan",            "color": "direction","size": 13},
        ],
    },
    "octagonSkeleton": {
        "viewBox":    {"w": 1000, "h": 760},
        "center":     {"x": 500, "y": 372},
        "radii":      [320, 252, 184, 116, 50],
        "sides":      8,
        "startAngle": -112.5,
        "labels": [
            {"sector": 1, "x": 500, "y": 90,  "text": "Sangat Baik",        "color": "great",    "size": 20},
            {"sector": 1, "x": 440, "y": 145, "text": "Pintu Besar",        "color": "neutral",  "size": 16},
            {"sector": 1, "x": 560, "y": 145, "text": "Logam",              "color": "metal",    "size": 16},
            {"sector": 1, "x": 440, "y": 188, "text": "Dokter Langit",      "color": "direction","size": 15},
            {"sector": 1, "x": 520, "y": 228, "text": "Api Selatan",        "color": "bad",      "size": 15},
            {"sector": 1, "x": 520, "y": 265, "text": "Api Li",             "color": "bad",      "size": 15},
            {"sector": 2, "x": 748, "y": 120, "text": "Buruk Besar",        "color": "bad",      "size": 17},
            {"sector": 2, "x": 690, "y": 170, "text": "Integritas",         "color": "bad",      "size": 15},
            {"sector": 2, "x": 740, "y": 215, "text": "Bahaya Celaka",      "color": "bad",      "size": 13},
            {"sector": 2, "x": 650, "y": 255, "text": "Api",                "color": "bad",      "size": 17},
            {"sector": 2, "x": 610, "y": 292, "text": "Kun Monyet",         "color": "direction","size": 15},
            {"sector": 3, "x": 880, "y": 320, "text": "Buruk Sedang",       "color": "bad",      "size": 17},
            {"sector": 3, "x": 750, "y": 352, "text": "Enam Sha",           "color": "bad",      "size": 15},
            {"sector": 3, "x": 780, "y": 400, "text": "Melodi Sastra",      "color": "bad",      "size": 13},
            {"sector": 3, "x": 654, "y": 372, "text": "Barat Logam",        "color": "metal",    "size": 15},
            {"sector": 3, "x": 620, "y": 428, "text": "Dui Logam",          "color": "element",  "size": 14},
            {"sector": 4, "x": 790, "y": 612, "text": "Buruk Kecil",        "color": "bad",      "size": 16},
            {"sector": 4, "x": 710, "y": 550, "text": "Simpan Berkah",      "color": "bad",      "size": 13},
            {"sector": 4, "x": 645, "y": 510, "text": "Qian Logam",         "color": "metal",    "size": 14},
            {"sector": 4, "x": 635, "y": 615, "text": "Anjing Babi",        "color": "neutral",  "size": 13},
            {"sector": 4, "x": 560, "y": 470, "text": "Tanah",              "color": "earth",    "size": 16},
            {"sector": 5, "x": 500, "y": 710, "text": "Baik Atas",          "color": "neutral",  "size": 17},
            {"sector": 5, "x": 430, "y": 660, "text": "Energi Hidup",       "color": "direction","size": 14},
            {"sector": 5, "x": 560, "y": 660, "text": "Serigala Hasrat",    "color": "direction","size": 13},
            {"sector": 5, "x": 455, "y": 590, "text": "Air Kan",            "color": "water",    "size": 16},
            {"sector": 5, "x": 540, "y": 610, "text": "Utara Air",          "color": "violet",   "size": 15},
            {"sector": 6, "x": 215, "y": 610, "text": "Buruk Besar",        "color": "bad",      "size": 16},
            {"sector": 6, "x": 300, "y": 565, "text": "Pasukan Penghancur", "color": "bad",      "size": 12},
            {"sector": 6, "x": 365, "y": 525, "text": "Putus Nasib",        "color": "bad",      "size": 14},
            {"sector": 6, "x": 300, "y": 475, "text": "Gen Tanah",          "color": "earth",    "size": 15},
            {"sector": 6, "x": 410, "y": 480, "text": "Kerbau Harimau",     "color": "neutral",  "size": 13},
            {"sector": 7, "x": 135, "y": 365, "text": "Baik Sedang",        "color": "direction","size": 16},
            {"sector": 7, "x": 220, "y": 330, "text": "Panjang Umur",       "color": "direction","size": 13},
            {"sector": 7, "x": 210, "y": 405, "text": "Melodi Perang",      "color": "direction","size": 13},
            {"sector": 7, "x": 330, "y": 350, "text": "Timur Kayu",         "color": "wood",     "size": 15},
            {"sector": 7, "x": 350, "y": 430, "text": "Utara Utama",        "color": "direction","size": 14},
            {"sector": 8, "x": 255, "y": 120, "text": "Baik Kecil",         "color": "good",     "size": 16},
            {"sector": 8, "x": 325, "y": 170, "text": "Bantuan",            "color": "direction","size": 14},
            {"sector": 8, "x": 245, "y": 215, "text": "Posisi Tenang",      "color": "direction","size": 13},
            {"sector": 8, "x": 360, "y": 240, "text": "Kayu",               "color": "wood",     "size": 17},
            {"sector": 8, "x": 420, "y": 275, "text": "Gua Xun",            "color": "direction","size": 14},
        ],
    },
}


# ── SVG helpers ───────────────────────────────────────────────

def _esc(value: object) -> str:
    s = str(value) if value is not None else ""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def _text_lines(text: str, max_len: int = 13) -> list:
    raw = str(text) if text is not None else ""
    if "\n" in raw:
        return raw.split("\n")
    if len(raw) <= max_len:
        return [raw]
    words, lines, cur = raw.split(), [], ""
    for word in words:
        nxt = f"{cur} {word}" if cur else word
        if len(nxt) > max_len:
            if cur:
                lines.append(cur)
            cur = word
        else:
            cur = nxt
    if cur:
        lines.append(cur)
    return lines[:3]


def _label_el(item: dict, center: dict) -> str:
    x    = item.get("x", center["x"])
    y    = item.get("y", center["y"])
    size = item.get("size", 16)
    lines = _text_lines(item.get("text", ""), item.get("max", 13))
    fill  = _LABEL_COLOR.get(item.get("color", ""), PALETTE["cyan"])
    ink   = PALETTE["ink"]
    tspans = "".join(
        f'<tspan x="{x}" dy="{0 if i == 0 else _round(size * 1.08)}">{_esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{fill}" '
        f'font-weight="800" paint-order="stroke" stroke="{ink}" '
        f'stroke-width="3.2" stroke-linejoin="round">{tspans}</text>'
    )


def _label_box(item: dict, center: dict) -> dict:
    x    = item.get("x", center["x"])
    y    = item.get("y", center["y"])
    size = item.get("size", 16)
    lines = _text_lines(item.get("text", ""), item.get("max", 13))
    width  = max(len(line) for line in lines) * size * 0.58 + 10
    height = len(lines) * size * 1.08 + 8
    return {
        "text":   item.get("text", ""),
        "sector": item.get("sector", 0),
        "left":   _round(x - width / 2),
        "right":  _round(x + width / 2),
        "top":    _round(y - size),
        "bottom": _round(y - size + height),
    }


def _collision_report(labels: list, center: dict) -> dict:
    boxes = [_label_box(item, center) for item in labels]
    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            pad = 3
            if (a["right"] + pad > b["left"] and b["right"] + pad > a["left"] and
                    a["bottom"] + pad > b["top"] and b["bottom"] + pad > a["top"]):
                hits.append({"a": a["text"], "b": b["text"],
                              "sectorA": a["sector"], "sectorB": b["sector"]})
    return {"count": len(hits), "collisions": hits}


def _line_el(coords: list, attrs: str = "") -> str:
    x1, y1, x2, y2 = coords
    return (f'<line x1="{_round(x1)}" y1="{_round(y1)}" '
            f'x2="{_round(x2)}" y2="{_round(y2)}" {attrs}/>')


def _polygon_el(points: list, attrs: str = "") -> str:
    return f'<polygon points="{poly_points(points)}" {attrs}/>'


# ── Public API ────────────────────────────────────────────────

def render_bagua_rect_svg(data: dict | None = None) -> str:
    """Port of renderBaguaRectSkeleton(). Returns complete inline SVG string."""
    if data is None:
        data = CODEX_BAGUA_FIXTURE
    r      = data["rectSkeleton"]
    pts    = rect_side_guide_points(r["frame"], r["guideRatios"])
    lines  = rect_side_guide_lines(r["frame"], r["guideRatios"])
    center = {"x": pts["center"][0], "y": pts["center"][1]}
    vb     = r["viewBox"]
    cy, cx = PALETTE["cyan"], PALETTE["ink"]

    defs = (
        '<defs><filter id="cyanGlowRect" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="0.55" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter></defs>'
    )
    frame = r["frame"]
    geo_g = (
        f'<g filter="url(#cyanGlowRect)" fill="none" stroke="{PALETTE["cyan"]}" '
        f'stroke-linecap="square" stroke-linejoin="miter" vector-effect="non-scaling-stroke">'
        f'<rect x="{frame["x"]}" y="{frame["y"]}" width="{frame["w"]}" height="{frame["h"]}" stroke-width="2.6"/>'
        + "".join(_line_el(gl["line"], 'stroke-width="2.2" opacity="0.9"') for gl in lines)
        + f'<circle cx="{pts["center"][0]}" cy="{pts["center"][1]}" r="4.5" fill="{PALETTE["cyan"]}" stroke="none"/>'
        + '</g>'
    )
    font    = "Inter, 'Segoe UI', Arial, sans-serif"
    label_g = (
        f'<g font-family="{font}">'
        + "".join(_label_el(item, center) for item in r["labels"])
        + '</g>'
    )
    bg = f'<rect width="{vb["w"]}" height="{vb["h"]}" fill="{PALETTE["bg"]}"/>'

    return (
        f'<svg class="bagua-svg bagua-rect-skeleton" '
        f'viewBox="0 0 {vb["w"]} {vb["h"]}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Bagua rectangular skeleton">\n'
        f'{defs}\n{bg}\n{geo_g}\n{label_g}\n</svg>'
    )


def render_bagua_octagon_svg(data: dict | None = None) -> str:
    """Port of renderBaguaOctagonSkeleton(). Returns complete inline SVG string."""
    if data is None:
        data = CODEX_BAGUA_FIXTURE
    o      = data["octagonSkeleton"]
    center = o["center"]
    vb     = o["viewBox"]
    rings  = [regular_polygon(center, r, o["sides"], o["startAngle"]) for r in o["radii"]]
    outer  = rings[0]
    spokes = [[center["x"], center["y"], pt[0], pt[1]] for pt in outer]

    defs = (
        '<defs><filter id="cyanGlowOct" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="0.55" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter></defs>'
    )
    bg = f'<rect width="{vb["w"]}" height="{vb["h"]}" fill="{PALETTE["bg"]}"/>'

    ring_els = "".join(
        _polygon_el(ring, f'stroke-width="{"2.7" if i == 0 else "1.8"}" opacity="{"0.96" if i == 0 else "0.78"}"')
        for i, ring in enumerate(rings)
    )
    spoke_els = "".join(_line_el(s, 'stroke-width="1.65" opacity="0.72"') for s in spokes)
    cx, cy_val = center["x"], center["y"]

    geo_g = (
        f'<g filter="url(#cyanGlowOct)" fill="none" stroke="{PALETTE["cyan"]}" '
        f'stroke-linecap="square" stroke-linejoin="miter" vector-effect="non-scaling-stroke">'
        + ring_els + spoke_els
        + f'<circle cx="{cx}" cy="{cy_val}" r="4.5" fill="{PALETTE["cyan"]}" stroke="none"/>'
        + '</g>'
    )
    font    = "Inter, 'Segoe UI', Arial, sans-serif"
    label_g = (
        f'<g font-family="{font}">'
        + "".join(_label_el(item, center) for item in o["labels"])
        + '</g>'
    )

    return (
        f'<svg class="bagua-svg bagua-octagon-skeleton" '
        f'viewBox="0 0 {vb["w"]} {vb["h"]}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Bagua octagon skeleton">\n'
        f'{defs}\n{bg}\n{geo_g}\n{label_g}\n</svg>'
    )


# ── V11 design constants ─────────────────────────────────────────

_V11_FRAME     = "#1A237E"   # dark navy frame
_V11_LINE      = "#283593"   # guide lines
_V11_DOT       = "#C9A961"   # gold center dot
_V11_BG        = "#FFFEF8"   # page cream (bg stroke for text legibility)
_V11_DARK_TEXT = "#2C2416"   # body text

# Ba Zhai star element (Hanzi) → display color
_EL_HZ_COLOR = {
    "火": "#B71C1C",   # fire  → dark red
    "土": "#BF6C00",   # earth → amber
    "金": "#455A64",   # metal → blue-grey
    "水": "#1565C0",   # water → dark blue
    "木": "#2E7D32",   # wood  → forest green
}

_GRADE_COLOR = {
    "大吉": "#1B5E20", "中吉": "#2E7D32", "小吉": "#558B2F", "上吉": "#1B5E20",
    "小凶": "#E65100", "中凶": "#C62828", "大凶": "#B71C1C",
}
_GRADE_BG = {
    "大吉": "#E8F5E9", "中吉": "#F1F8E9", "小吉": "#F9FBE7", "上吉": "#E8F5E9",
    "小凶": "#FFF3E0", "中凶": "#FBE9E7", "大凶": "#FFEBEE",
}

# direction → (trigram_name, number, hanzi_el, id_el, element_color)
_DIR_INFO = {
    "Selatan":    ("Li",   9, "火", "Api",   "#B71C1C"),
    "Barat Daya": ("Kun",  2, "土", "Tanah", "#BF6C00"),
    "Barat":      ("Dui",  7, "金", "Logam", "#455A64"),
    "Barat Laut": ("Qian", 6, "金", "Logam", "#455A64"),
    "Utara":      ("Kan",  1, "水", "Air",   "#1565C0"),
    "Timur Laut": ("Gen",  8, "土", "Tanah", "#BF6C00"),
    "Timur":      ("Zhen", 3, "木", "Kayu",  "#2E7D32"),
    "Tenggara":   ("Xun",  4, "木", "Kayu",  "#2E7D32"),
}
_DIR_MEANING = {
    "Selatan": "Reputasi · Ketenaran",   "Barat Daya": "Cinta · Pernikahan",
    "Barat":   "Anak-anak · Kreativitas","Barat Laut":  "Pembimbing · Dukungan",
    "Utara":   "Karir · Jalan Hidup",    "Timur Laut":  "Pengetahuan · Keilmuan",
    "Timur":   "Keluarga · Kesehatan",   "Tenggara":    "Kekayaan · Kelimpahan",
}
# Clockwise from South-at-top
_SECTOR_ORDER = ["Selatan","Barat Daya","Barat","Barat Laut","Utara","Timur Laut","Timur","Tenggara"]

# Outer label: (x, y_start, text-anchor)
# viewBox=1100×880, frame x=235 y=145 w=630 h=590 → right=865, bottom=735, center=(550,440)
# Each position is centered in its corner/side strip of the viewBox.
# y_start: top strip y=28 (last line @128<145), bottom strip y=755 (last line @855<880)
# Side positions: y=408 = center_y - 32 (so 3 lines fall at 408,442,462 — centered on 435≈440)
_OUTER_POS = [
    (550,  28, "middle"),   # S  — top strip center  (x=550, midpoint of frame width)
    (982,  28, "end"),      # SW — top-right corner  (x=982, center of right 235px strip)
    (982, 408, "middle"),   # W  — right strip       (x=982, center of right strip)
    (982, 755, "end"),      # NW — bottom-right      (last line @855<880)
    (550, 778, "middle"),   # N  — bottom strip (y=778 → top of text ~750, clear of frame bottom=735)
    (118, 755, "start"),    # NE — bottom-left corner
    (118, 408, "middle"),   # E  — left strip        (x=118, center of left 235px strip)
    (118,  28, "start"),    # SE — top-left corner
]


def _txt(x, y, size, fill, weight, anchor, text, stroke=_V11_BG, sw=2) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" '
        f'font-weight="{weight}" paint-order="stroke" stroke="{stroke}" stroke-width="{sw}">'
        f'{_esc(text)}</text>'
    )


def render_bagua_rect_svg_v11(sectors: dict | None = None) -> str:
    """Data-driven Ba Zhai rect chart — v11 light theme, square frame, no label overflow.

    ViewBox 1100×880 gives 235px breathing room on all sides for outer direction labels.
    Inner labels use compact Hanzi (2 chars) to stay within each sector's width.
    sectors: dict from subject["bagua_sectors"].
    """
    dir_map: dict = {}
    for sd in (sectors or {}).values():
        d = sd.get("direction_id", "")
        if d:
            dir_map[d] = sd

    VW, VH = 1100, 880
    # Frame centered in viewBox: 235px breathing room on all sides
    frame = {"x": 235, "y": 145, "w": 630, "h": 590}  # ratio 1.07:1, nearly square
    ratios = [1/3, 2/3]

    pts = rect_side_guide_points(frame, ratios)
    gls = rect_side_guide_lines(frame, ratios)
    cx, cy = pts["center"]  # (550, 440)

    # Sector centroids: average of two guide-point vertices + center
    _pairs = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,1)]
    centroids = [
        (_round((pts[a][0]+pts[b][0]+cx)/3), _round((pts[a][1]+pts[b][1]+cy)/3))
        for a,b in _pairs
    ]

    font = "Noto Serif TC, 'Noto Serif', serif"
    out  = [f'<svg class="bagua-svg bagua-rect-v11" viewBox="0 0 {VW} {VH}" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="{font}">']

    # ── Sector fill triangles (grade color, drawn first so lines sit on top) ──
    for i, direction in enumerate(_SECTOR_ORDER):
        a, b = _pairs[i]
        ax, ay = pts[a]; bx, by = pts[b]
        sd = dir_map.get(direction, {})
        grade_hz = sd.get("grade_hz", "")
        bg = _GRADE_BG.get(grade_hz, "none")
        if bg != "none":
            out.append(f'<polygon points="{cx},{cy} {ax},{ay} {bx},{by}" '
                       f'fill="{bg}" opacity="0.55"/>')

    # ── Frame + guide lines (drawn on top of fills) ──
    out.append(f'<g fill="none" stroke="{_V11_FRAME}" stroke-linecap="square">')
    out.append(f'<rect x="{frame["x"]}" y="{frame["y"]}" '
               f'width="{frame["w"]}" height="{frame["h"]}" stroke-width="2.4"/>')
    for gl in gls:
        x1,y1,x2,y2 = gl["line"]
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                   f'stroke="{_V11_LINE}" stroke-width="1.6" opacity="0.88"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{_V11_DOT}" stroke="none"/>')
    out.append('</g>')

    # ── 8 sector labels — Ba Zhai star data inside, directional info outside ──
    for i, direction in enumerate(_SECTOR_ORDER):
        scx, scy = centroids[i]
        sd = dir_map.get(direction, {})
        grade_hz   = sd.get("grade_hz", "")
        label_hz   = sd.get("label_hz", "")    # Ba Zhai type (天醫, 生氣 …)
        star_hz    = sd.get("star_hz", "")     # Ba Zhai star name (巨門, 貪狼 …)
        el_hz_s    = sd.get("element_hz", "")  # star's element Hanzi (金, 木 …)
        el_id_s    = sd.get("element_id", "")  # star's element Indo (Logam, Kayu …)
        el_color_s = _EL_HZ_COLOR.get(el_hz_s, _V11_DARK_TEXT)

        gc = _GRADE_COLOR.get(grade_hz, _V11_DARK_TEXT)
        di = _DIR_INFO.get(direction, ("?","?","?","?", _V11_DARK_TEXT))
        tri_name, tri_num, _, _, _ = di   # directional trigram kept for outer label

        # ── INNER: Ba Zhai star data (subject-specific, not directional) ──
        # Line 1: Star's element — e.g. "金 Logam"
        out.append(_txt(scx, scy-46, 20, el_color_s, "600", "middle",
                        f"{el_hz_s} {el_id_s}"))
        # Line 2: Ba Zhai star name — e.g. "巨門"
        if star_hz:
            out.append(_txt(scx, scy-16, 28, gc, "800", "middle", star_hz))
        # Line 3: Ba Zhai type — e.g. "天醫"
        if label_hz:
            out.append(_txt(scx, scy+14, 22, gc, "700", "middle", label_hz))
        # Line 4: Grade badge
        if grade_hz:
            out.append(_txt(scx, scy+38, 18, gc, "600", "middle", f"【{grade_hz}】"))

        # ── OUTER: directional info + grade (outside frame) ──
        ox, oy, anchor = _OUTER_POS[i]
        dir_words = direction.split(" ", 1)
        out.append(_txt(ox, oy, 34, gc, "800", anchor, dir_words[0]))
        if len(dir_words) > 1:
            out.append(_txt(ox, oy+36, 34, gc, "800", anchor, dir_words[1]))
            oy2 = oy + 72
        else:
            oy2 = oy + 36
        # Directional trigram · element
        di_el_id = _DIR_INFO.get(direction, ("","","","", ""))[3]
        out.append(_txt(ox, oy2, 22, gc, "600", anchor,
                        f"{tri_name} {tri_num} · {di_el_id}"))
        # Grade · short meaning
        meaning_short = _DIR_MEANING.get(direction, "").split(" · ")[0]
        if grade_hz:
            out.append(_txt(ox, oy2+26, 20, gc, "600", anchor,
                            f"{grade_hz} · {meaning_short}"))

    out.append('</svg>')
    return "\n".join(out)


# ── V11 Octagon chart ─────────────────────────────────────────

def render_bagua_octagon_svg_v11(sectors: dict | None = None) -> str:
    """Data-driven Ba Zhai octagon chart — v11 light theme, 5-ring skeleton.

    VH=880, center shifted to (500,440) so 440px above and below center,
    giving outer labels at r_tip=355 room to render without clipping.
    Text anchor auto-computed from sector angle:
      near-vertical → middle, right-half → start, left-half → end.
    Inner labels use label_hz (2 Hanzi chars) — compact, no overflow.
    """
    dir_map: dict = {}
    for sd in (sectors or {}).values():
        d = sd.get("direction_id", "")
        if d:
            dir_map[d] = sd

    VW, VH = 1000, 880
    cx, cy = 500, 440          # center shifted down 40px so top Selatan label fits
    radii  = [310, 244, 178, 112, 52]
    sides  = 8
    start  = -112.5
    _OCT_SECTOR_ORDER = ["Selatan","Barat Daya","Barat","Barat Laut",
                         "Utara","Timur Laut","Timur","Tenggara"]

    center_dict = {"x": cx, "y": cy}
    rings  = [regular_polygon(center_dict, r, sides, start) for r in radii]
    outer  = rings[0]
    spokes = [[cx, cy, pt[0], pt[1]] for pt in outer]

    font = "Noto Serif TC, 'Noto Serif', serif"
    out  = [f'<svg class="bagua-svg bagua-oct-v11" viewBox="0 0 {VW} {VH}" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="{font}">']

    # ── Sector fills ──
    for i, direction in enumerate(_OCT_SECTOR_ORDER):
        sd = dir_map.get(direction, {})
        bg = _GRADE_BG.get(sd.get("grade_hz", ""), "#F5F5F5")
        a_pt, b_pt = outer[i], outer[(i+1) % 8]
        out.append(f'<polygon points="{cx},{cy} {a_pt[0]},{a_pt[1]} {b_pt[0]},{b_pt[1]}" '
                   f'fill="{bg}" opacity="0.65"/>')

    # ── Rings + spokes ──
    out.append(f'<g fill="none" stroke="{_V11_FRAME}" stroke-linecap="square">')
    for i, ring in enumerate(rings):
        sw = "2.4" if i == 0 else "1.4"
        op = "0.9" if i == 0 else "0.6"
        out.append(f'<polygon points="{poly_points(ring)}" stroke-width="{sw}" opacity="{op}"/>')
    for sp in spokes:
        out.append(f'<line x1="{sp[0]}" y1="{sp[1]}" x2="{sp[2]}" y2="{sp[3]}" '
                   f'stroke="{_V11_LINE}" stroke-width="1.2" opacity="0.55"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{_V11_DOT}" stroke="none"/>')
    out.append('</g>')

    # ── Labels per sector ──
    r_label = (radii[1] + radii[2]) / 2   # ring1-ring2 band (blue circle position)
    r_tip   = radii[0] + 50               # outer tip (clear of outer ring)

    for i, direction in enumerate(_OCT_SECTOR_ORDER):
        sd = dir_map.get(direction, {})
        grade_hz = sd.get("grade_hz", "")
        label_hz = sd.get("label_hz", "")  # 2-char Hanzi — compact, no overflow
        gc = _GRADE_COLOR.get(grade_hz, _V11_DARK_TEXT)
        di = _DIR_INFO.get(direction, ("?","?","?","?", _V11_DARK_TEXT))
        tri_name, tri_num, el_hz, el_id, el_color = di

        mid_angle = start + (i + 0.5) * (360 / sides)
        mid_rad   = math.radians(mid_angle)
        sin_v, cos_v = math.sin(mid_rad), math.cos(mid_rad)

        # Auto text-anchor: near-vertical → middle; right → start; left → end
        if abs(sin_v) > 0.5:
            anchor = "middle"
        elif cos_v > 0:
            anchor = "start"
        else:
            anchor = "end"

        # ── Outer tip: direction name + grade ──
        tx = _round(cx + cos_v * r_tip)
        ty = _round(cy + sin_v * r_tip)
        dir_words = direction.split(" ", 1)
        out.append(_txt(tx, ty - 18, 28, gc, "800", anchor, dir_words[0]))
        if len(dir_words) > 1:
            out.append(_txt(tx, ty + 12, 28, gc, "800", anchor, dir_words[1]))
            out.append(_txt(tx, ty + 38, 20, gc, "600", anchor, grade_hz))
        else:
            out.append(_txt(tx, ty + 12, 20, gc, "600", anchor, grade_hz))

        # ── Inner band: Ba Zhai star data (subject-specific) ──
        lx = _round(cx + cos_v * r_label)
        ly = _round(cy + sin_v * r_label)
        star_hz_s  = sd.get("star_hz", "")
        el_hz_s    = sd.get("element_hz", "")
        el_id_s    = sd.get("element_id", "")
        el_color_s = _EL_HZ_COLOR.get(el_hz_s, _V11_DARK_TEXT)
        # Line 1: star element (e.g. "金 Logam")
        out.append(_txt(lx, ly - 24, 20, el_color_s, "600", "middle",
                        f"{el_hz_s} {el_id_s}"))
        # Line 2: Ba Zhai star name (e.g. "巨門")
        if star_hz_s:
            out.append(_txt(lx, ly, 26, gc, "800", "middle", star_hz_s))
        # Line 3: Ba Zhai type (e.g. "天醫")
        if label_hz:
            out.append(_txt(lx, ly + 24, 22, gc, "700", "middle", label_hz))

    # ── Center ──
    out.append(_txt(cx, cy - 12, 22, _V11_DARK_TEXT, "600", "middle", "八宅"))
    out.append(_txt(cx, cy + 10, 18, _V11_DOT,       "700", "middle", "Ba Zhai"))

    out.append('</svg>')
    return "\n".join(out)


# ── Panel inject helpers (shared by build_fengshui_pdf + render) ─

EM_DASH = "—"

_GUA_NAMES = {
    "乾": "Qian · Langit / Barat Laut",
    "兌": "Dui · Rawa / Barat",
    "離": "Li · Api / Selatan",
    "震": "Zhen · Petir / Timur",
    "巽": "Xun · Angin / Tenggara",
    "坎": "Kan · Air / Utara",
    "艮": "Gen · Gunung / Timur Laut",
    "坤": "Kun · Bumi / Barat Daya",
}

_MONTHS_ID = ["","Januari","Februari","Maret","April","Mei","Juni",
               "Juli","Agustus","September","Oktober","November","Desember"]


def _inject_bagua_rect_panel(content: str, subject: dict) -> str:
    """Fill {{BR_*}} placeholders in page_bagua_rect.html with subject data."""
    iden    = subject.get("identity") or {}
    shio    = subject.get("shio") or {}
    dm      = subject.get("day_master") or {}
    pillars = subject.get("pillars") or {}
    EM      = EM_DASH

    content = content.replace("{{BR_NAME_HZ}}",    iden.get("name_hanzi") or "")
    content = content.replace("{{BR_NAME_ID}}",    iden.get("name_id") or EM)
    content = content.replace("{{BR_GENDER_ID}}",  iden.get("gender_id") or EM)
    content = content.replace("{{BR_SHIO_HZ}}",    shio.get("branch_hz") or EM)
    content = content.replace("{{BR_SHIO_ID}}",    shio.get("id") or EM)

    bd = iden.get("birth_date") or "1900-01-01"
    try:
        y, m, d = bd.split("-")
        birth_date_id = f"{int(d)} {_MONTHS_ID[int(m)]} {int(y)}"
        birth_year    = y
    except Exception:
        birth_date_id, birth_year = EM, EM
    yr_p   = pillars.get("year") or {}
    yr_hz  = (yr_p.get("stem_hz") or "") + (yr_p.get("branch_hz") or "")
    lunar  = iden.get("lunar_date_text_new") or EM
    lunar_short = re.sub(r'\s*\(.*?\)', "", lunar).strip()

    content = content.replace("{{BR_BIRTH_YEAR}}",      birth_year)
    content = content.replace("{{BR_BIRTH_DATE_ID}}",   birth_date_id)
    content = content.replace("{{BR_YEAR_PILLAR_HZ}}",  yr_hz)
    content = content.replace("{{BR_LUNAR_DATE_ID}}",   lunar_short)
    content = content.replace("{{BR_BIRTH_TIME}}",      iden.get("birth_time") or EM)
    content = content.replace("{{BR_BIRTH_PERIOD_ID}}", iden.get("birth_period_id") or EM)

    content = content.replace("{{BR_LIFE_TYPE_HZ}}", subject.get("bagua_life_type_hz") or EM)
    content = content.replace("{{BR_LIFE_TYPE_ID}}", subject.get("bagua_life_type_id") or EM)
    gua_hz  = (subject.get("yang_zhai") or {}).get("gua_hz") or ""
    content = content.replace("{{BR_GUA_HZ}}",       gua_hz)
    content = content.replace("{{BR_GUA_ID}}",       _GUA_NAMES.get(gua_hz, gua_hz))
    content = content.replace("{{BR_NAYIN_HZ}}",     subject.get("bagua_nayin_hz") or EM)
    content = content.replace("{{BR_NAYIN_ID}}",     subject.get("bagua_nayin_id") or EM)
    content = content.replace("{{BR_DM_HZ}}",        dm.get("stem_hz") or EM)
    content = content.replace("{{BR_DM_LABEL_ID}}",  dm.get("label_id") or EM)

    sectors = subject.get("bagua_sectors") or {}
    lucky   = [
        sd.get("direction_id", "")
        for sd in sectors.values()
        if sd.get("grade_hz") in ("大吉", "中吉", "小吉", "上吉")
        and sd.get("direction_id")
    ]
    if lucky:
        chips = "".join(f'<div class="br-dir-chip">{d}</div>' for d in lucky)
    else:
        chips = f'<span style="font-size:7pt;color:var(--text-muted);">{EM}</span>'
    content = content.replace("{{BR_LUCKY_DIRS_HTML}}", chips)

    note = subject.get("bagua_warning_id") or subject.get("bagua_note_id") or EM
    content = content.replace("{{BR_NOTE_ID}}", note)
    return content


def _inject_bagua_oct_panel(content: str, subject: dict) -> str:
    """Fill {{BOC_*}} placeholders in page_bagua_octagon.html."""
    sectors = subject.get("bagua_sectors") or {}
    EM = EM_DASH

    _grade_order = {"大吉":0,"中吉":1,"小吉":2,"上吉":0,"小凶":3,"中凶":4,"大凶":5}
    sorted_sds = sorted(
        sectors.values(),
        key=lambda sd: _grade_order.get(sd.get("grade_hz",""), 9)
    )
    rows_html = ""
    for sd in sorted_sds:
        grade_hz = sd.get("grade_hz", "")
        grade_id = sd.get("grade_id", "")
        dir_id   = sd.get("direction_id", "") or EM
        label_id = sd.get("label_id", "") or EM
        star_hz  = sd.get("star_hz", "") or ""
        mts_hz   = sd.get("mountains_hz", "") or ""
        is_ji    = grade_hz in ("大吉","中吉","小吉","上吉")
        gc = "grade-ji" if is_ji else "grade-xiong"
        rows_html += (
            f'<div class="bco-sector-row {gc}">'
            f'<div class="bco-grade {gc}">{grade_hz}</div>'
            f'<div class="bco-info">'
            f'<div class="bco-name">{dir_id} · {label_id}</div>'
            f'<div class="bco-star">{star_hz} · {mts_hz}</div>'
            f'</div>'
            f'<div class="bco-grade-id">{grade_id}</div>'
            f'</div>'
        )
    content = content.replace("{{BOC_SECTOR_ROWS}}", rows_html)

    iden = subject.get("identity") or {}
    content = content.replace("{{BOC_NAME_ID}}",    iden.get("name_id") or EM)
    content = content.replace("{{BOC_LIFE_TYPE_HZ}}", subject.get("bagua_life_type_hz") or EM)
    content = content.replace("{{BOC_LIFE_TYPE_ID}}", subject.get("bagua_life_type_id") or EM)
    gua_hz = (subject.get("yang_zhai") or {}).get("gua_hz") or ""
    content = content.replace("{{BOC_GUA_HZ}}",     gua_hz)
    content = content.replace("{{BOC_NAYIN_HZ}}",   subject.get("bagua_nayin_hz") or EM)
    content = content.replace("{{BOC_NAYIN_ID}}",   subject.get("bagua_nayin_id") or EM)
    content = content.replace("{{BOC_WARNING_ID}}", subject.get("bagua_warning_id") or EM)
    content = content.replace("{{BOC_VIRTUE_ID}}",  subject.get("bagua_virtue_id") or EM)
    return content


def get_bagua_geometry_report(data: dict | None = None) -> dict:
    """Port of getBaguaGeometryReport(). Used for QA acceptance checks."""
    if data is None:
        data = CODEX_BAGUA_FIXTURE
    rect  = data["rectSkeleton"]
    r_pts = rect_side_guide_points(rect["frame"], rect["guideRatios"])
    r_lines = rect_side_guide_lines(rect["frame"], rect["guideRatios"])
    r_center = {"x": r_pts["center"][0], "y": r_pts["center"][1]}
    r_col = _collision_report(rect["labels"], r_center)

    oct_  = data["octagonSkeleton"]
    rings = [regular_polygon(oct_["center"], r, oct_["sides"], oct_["startAngle"])
             for r in oct_["radii"]]
    o_col = _collision_report(oct_["labels"], oct_["center"])

    return {
        "rectSkeleton": {
            "frame":                   rect["frame"],
            "center":                  r_pts["center"],
            "guidePointCount":         8,
            "guidePairs":              [f"{gl['from']}-{gl['to']}" for gl in r_lines],
            "guideLineCount":          len(r_lines),
            "allGuideLinesPassCenter": all(
                line_passes_through_point(gl["line"], r_pts["center"])
                for gl in r_lines
            ),
            "labelCount":              len(rect["labels"]),
            "labelCollisionCount":     r_col["count"],
        },
        "octagonSkeleton": {
            "ringCount":           len(rings),
            "sidesPerRing":        [len(ring) for ring in rings],
            "labelCount":          len(oct_["labels"]),
            "labelCollisionCount": o_col["count"],
            "center":              oct_["center"],
        },
    }
