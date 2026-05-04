"""Kecocokan Shio extractor — adaptive untuk 3 pola MD.

Pola A (MD1): H3 sub `### 3.4 【婚配】 — Kecocokan Shio Pasangan` di BAGIAN III.
              Tabel: Shio Pasangan | Status | Catatan (✅/❌ + Hanzi label).
Pola B (MD2): H2 `## BAB XX — KECOCOKAN PERNIKAHAN (婚配)`.
              Tabel: Shio | Kecocokan | Catatan (⭐ rating).
Pola C (MD3): H2 `## BAB 8: PERNIKAHAN & PASANGAN — 婚配`.
              Pantangan blockquote + Tabel cocok-only + Saran blockquote.
"""
import re
from canonical_model import KecocokanShio, ShioMatch
from extractors.md_utils import strip_md_bold


SHIO_KW = ["KECOCOKAN SHIO", "KECOCOKAN PERNIKAHAN", "PERNIKAHAN & PASANGAN", "婚配"]

# Indo shio lookup
SHIO_INDO = {
    "鼠": "Tikus", "牛": "Kerbau", "虎": "Macan", "兔": "Kelinci",
    "龍": "Naga",  "蛇": "Ular",   "馬": "Kuda",  "羊": "Kambing",
    "猴": "Monyet","雞": "Ayam",   "狗": "Anjing","豬": "Babi",
}
SHIO_HZ = {v: k for k, v in SHIO_INDO.items()}
ALL_SHIO_INDO = ["Tikus", "Kerbau", "Macan", "Kelinci", "Naga", "Ular",
                  "Kuda", "Kambing", "Monyet", "Ayam", "Anjing", "Babi"]


def _find_section(sections):
    """Find shio compatibility section (H2 or H3 nested)."""
    # Strategy 1: direct H2 with KECOCOKAN/PERNIKAHAN keyword
    candidates = []
    for s in sections:
        t = s["title"].upper()
        if any(k in t for k in SHIO_KW):
            # Must contain table or mention shio
            content = "\n".join(s.get("lines", []))
            if "Shio" in content or "shio" in content or "婚配" in content:
                candidates.append(s)
    if candidates:
        # Prefer the one with most content
        candidates.sort(key=lambda x: len(x.get("lines", [])), reverse=True)
        return candidates[0]
    # Strategy 2: H3 sub inside another H2 (MD1 style — 3.4 inside BAGIAN III)
    for s in sections:
        for sub in s.get("sub", []) or []:
            t_raw = sub.get("raw_title", "") + " " + sub.get("title", "")
            if "婚配" in t_raw or "kecocokan shio" in t_raw.lower():
                return sub
    return None


def _detect_shio_in_cell(cell):
    """Find shio Indo or Hanzi in cell. Return (shio_id, shio_hz, is_other)."""
    cell_clean = strip_md_bold(cell).strip()
    # "Shio lain" / "Shio lainnya" / "Lainnya" → generic row
    if re.search(r"\bshio\s+lain", cell_clean, re.IGNORECASE) or "Lainnya" in cell_clean:
        return ("Lainnya", "", True)
    # Hanzi single char
    for hz, indo in SHIO_INDO.items():
        if hz in cell_clean:
            return (indo, hz, False)
    # Indo name
    for indo in ALL_SHIO_INDO:
        if re.search(r"\b" + indo + r"\b", cell_clean, re.IGNORECASE):
            return (indo, SHIO_HZ.get(indo, ""), False)
    return (None, None, False)


def _classify_status(text):
    """Determine rating + mood from status cell text."""
    t = strip_md_bold(text).lower()
    # Star count
    star_count = text.count("★") + text.count("⭐")
    if star_count >= 5: return 5, "good"
    if star_count == 4: return 4, "good"
    if star_count == 3: return 3, "neutral"
    if star_count == 2: return 2, "warn"
    if star_count == 1: return 1, "bad"
    # Keywords
    if any(k in t for k in ["sangat baik", "sangat cocok", "大吉"]): return 5, "good"
    if any(k in t for k in ["baik", "吉", "harmonis"]): return 4, "good"
    if any(k in t for k in ["lumayan", "次吉", "sedang", "biasa", "cukup"]): return 3, "neutral"
    if any(k in t for k in ["pantang", "hindari", "忌", "❌", "⚠"]): return 1, "bad"
    return 3, "neutral"


def _parse_shio_table(lines):
    """Parse markdown table → list of ShioMatch."""
    matches = []
    in_table = False
    rows = []
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

    for r in rows:
        # Skip header
        if r[0].lower() in ("shio", "shio pasangan", "no", "no."): continue
        shio_id, shio_hz, is_other = _detect_shio_in_cell(r[0])
        if not shio_id: continue
        # Status cell (col 2)
        status_cell = r[1] if len(r) > 1 else ""
        rating, mood = _classify_status(status_cell)
        # Note cell (col 3)
        note_cell = r[2] if len(r) > 2 else ""
        note = strip_md_bold(note_cell).strip() if note_cell else None
        matches.append(ShioMatch(
            shio_id=shio_id, shio_hz=shio_hz or "",
            rating=rating, mood=mood, note=note,
            is_other=is_other,
        ))
    return matches


def _parse_pantangan_blockquote(lines):
    """Find > **Pantangan (忌):** Hindari pasangan dengan Shio X, Y, Z
    Return (pantang_shio_list, full_text)."""
    pantang_shios = []
    full_text = None
    for line in lines:
        s = line.strip()
        if not s.startswith(">"): continue
        text = re.sub(r"^>\s*", "", s)
        text_low = text.lower()
        if "pantang" in text_low or "忌" in text:
            full_text = strip_md_bold(text).strip()
            for indo in ALL_SHIO_INDO:
                if re.search(r"\b" + indo + r"\b", text, re.IGNORECASE):
                    pantang_shios.append(indo)
            break
    return pantang_shios, full_text


def _extract_interpretasi(lines):
    """Find subject-specific interpretasi/saran blockquote."""
    NOTE_KW = re.compile(r"^[💡💼❤️✦🌟🔮]?\s*\*\*\s*(Saran|Tips|Makna|Catatan|Pesan|Rekomendasi)\b[^*]*\*\*\s*:?\s*(.+)$", re.IGNORECASE)
    for line in lines:
        s = line.strip()
        if not s.startswith(">"): continue
        text = re.sub(r"^>\s*", "", s)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()
        # Skip pantangan and "Apa itu" intros
        if "pantang" in text.lower(): continue
        if text.lower().startswith("apa itu"): continue
        # Subject keyword detection
        if re.search(r"\b(saran|tips|makna|catatan|pesan|rekomendasi)\b", text[:50], re.IGNORECASE):
            return text
    return None


def extract_kecocokan_shio(sections):
    sec = _find_section(sections)
    if not sec: return None
    lines = sec["lines"]

    matches = _parse_shio_table(lines)
    pantang_shios, pantang_full = _parse_pantangan_blockquote(lines)

    # If MD has pantangan blockquote (MD3 style) but no negative entries in table,
    # synthesize them from the blockquote
    table_shios = {m.shio_id for m in matches if not m.is_other}
    for sh in pantang_shios:
        if sh not in table_shios:
            matches.append(ShioMatch(
                shio_id=sh, shio_hz=SHIO_HZ.get(sh, ""),
                rating=1, mood="bad",
                note="Pantangan — hindari pasangan dengan shio ini",
            ))

    interp = _extract_interpretasi(lines) or pantang_full

    if not matches and not interp:
        return None

    return KecocokanShio(
        matches=matches,
        interpretasi=interp,
        pantangan_summary=pantang_full,
    )
