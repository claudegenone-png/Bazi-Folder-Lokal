"""Feng Shui Rumah extractor — adaptive untuk 3 pola MD.

Pattern (semua MD):
  - H2 title contains "FENG SHUI" / "陽宅" / "ARAH RUMAH"
  - Tabel dengan kolom: Elemen Rumah/Aspek | Arah/Posisi
  - Trigram blockquote (`> Trigram: 坤卦` atau `○坤卦` raw)
  - Saran/Catatan blockquote
"""
import re
from canonical_model import FengShuiRumah, FengShuiElement
from extractors.md_utils import strip_md_bold


FENG_SHUI_KW = ["FENG SHUI", "陽宅", "YANG ZHAI", "ARAH RUMAH"]

# Aspek → icon mapping
ASPEK_ICON = [
    (re.compile(r"orientasi|坐向", re.I), "🧭"),
    (re.compile(r"pintu|門路|門", re.I), "🚪"),
    (re.compile(r"dapur|kompor|爐灶|灶", re.I), "🔥"),
    (re.compile(r"tempat\s+tidur|床位|床", re.I), "🛌"),
    (re.compile(r"kamar\s+tidur|房間|房", re.I), "🛏"),
    (re.compile(r"altar|sembahyang|dewa|神位", re.I), "🕯"),
    (re.compile(r"toilet|kamar\s+mandi|wc|坑廁", re.I), "🚽"),
]


def _icon_for(aspek):
    if not aspek: return "✦"
    for pat, ic in ASPEK_ICON:
        if pat.search(aspek):
            return ic
    return "✦"


def _aspek_hz(aspek):
    """Extract Hanzi suffix from aspek if present, e.g. 'Orientasi (坐向)' → '坐向'."""
    m = re.search(r"\(([一-鿿]+)\)", aspek)
    if m: return m.group(1)
    m = re.search(r"\b([一-鿿]+)\b", aspek)
    if m: return m.group(1)
    return None


def _aspek_clean(aspek):
    """Strip Hanzi parens from aspek display label."""
    s = strip_md_bold(aspek)
    s = re.sub(r"\s*\([一-鿿/\s]+\)\s*", "", s)
    s = re.sub(r"\s+[一-鿿]+\s*$", "", s)
    return s.strip()


def _find_section(sections):
    for s in sections:
        t = s["title"].upper()
        if any(k in t for k in FENG_SHUI_KW):
            return s
    return None


def _parse_table(lines):
    """Return list of (aspek, arah) tuples from first table."""
    rows = []
    in_table = False
    for line in lines:
        if "|" not in line:
            if in_table and rows: break
            continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line):
            in_table = True
            continue
        if not in_table: continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2: continue
        rows.append(cells)
    out = []
    for r in rows:
        if r[0].lower() in ("elemen rumah", "aspek", "elemen", "no."): continue
        aspek = strip_md_bold(r[0])
        arah = strip_md_bold(r[1] if len(r) > 1 else "")
        if aspek and arah:
            out.append((aspek, arah))
    return out


def _extract_trigram(lines):
    """Find trigram Hanzi + Indo description.
    Patterns:
      - `○坎卦` / `●坤卦` raw (Hanzi only)
      - `> **Trigram Rumah:** 坤卦 (Kun/Tanah) — melambangkan...`
      - `> 🏠 **Catatan:** Rumah dengan Trigram 坎卦 (Kan Gua) — ...`
    Returns (hz, indo, meaning) or (None, None, None).
    """
    trigram_hz = None
    trigram_indo = None
    meaning = None

    # Try blockquote with **Trigram**
    for line in lines:
        s = line.strip()
        if not s.startswith(">"): continue
        text = re.sub(r"^>\s*", "", s)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        m = re.search(r"[Tt]rigram[^:]*:\s*([一-鿿]+卦?)\s*\(([^)]+)\)\s*[—\-]?\s*(.*)", text)
        if m:
            trigram_hz = m.group(1)
            trigram_indo = m.group(2).strip()
            meaning = m.group(3).strip() if m.group(3) else None
            return trigram_hz, trigram_indo, meaning
        # Variant: "Catatan: Rumah dengan Trigram 坎卦 (Kan Gua) — ..."
        m = re.search(r"[Tt]rigram\s+([一-鿿]+卦)\s*\(([^)]+)\)\s*[—\-]?\s*(.*)", text)
        if m:
            trigram_hz = m.group(1)
            trigram_indo = m.group(2).strip()
            meaning = m.group(3).strip() if m.group(3) else None
            return trigram_hz, trigram_indo, meaning

    # Fallback: raw `○坎卦` or `●坤卦` lines
    for line in lines[:15]:
        s = line.strip()
        m = re.match(r"^[○●◎]([一-鿿]+卦)\s*$", s)
        if m:
            trigram_hz = m.group(1)
            return trigram_hz, None, None
    return None, None, None


def _extract_interpretasi(lines):
    """Find subject-specific Saran/Catatan blockquote."""
    for line in lines:
        s = line.strip()
        if not s.startswith(">"): continue
        text = re.sub(r"^>\s*", "", s)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()
        if not text: continue
        # Skip Hanzi-dominant raw OCR
        han = sum(1 for c in text if "一" <= c <= "鿿")
        latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        if han > 5 and han > latn * 1.5: continue
        # Subject keywords
        if re.search(r"\b(saran|tips|makna|catatan|pesan|rekomendasi|trigram\s+rumah)\b", text[:60], re.IGNORECASE):
            return text
    return None


def extract_fengshui(sections):
    sec = _find_section(sections)
    if not sec: return None
    lines = sec["lines"]

    # Parse table
    rows = _parse_table(lines)
    elements = []
    for aspek, arah in rows:
        elements.append(FengShuiElement(
            aspek=_aspek_clean(aspek),
            aspek_hz=_aspek_hz(aspek),
            arah=arah,
            icon=_icon_for(aspek),
        ))

    trigram_hz, trigram_indo, trigram_meaning = _extract_trigram(lines)
    interpretasi = _extract_interpretasi(lines)

    if not elements and not interpretasi and not trigram_hz:
        return None

    return FengShuiRumah(
        elements=elements,
        trigram_hz=trigram_hz,
        trigram_indo=trigram_indo,
        trigram_meaning=trigram_meaning,
        interpretasi=interpretasi,
    )
