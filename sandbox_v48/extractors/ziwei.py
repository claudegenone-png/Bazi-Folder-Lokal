"""ZiWei extractor — 12 palaces + 4 transformations + data inti.

Adaptive across MD patterns:
  MD1 (Lin Ruyi): "PETA BINTANG ZIWEI" + "### Struktur Dua Belas Istana" (12 palaces table)
  MD2 (Li Yuanxiang): "PETA NASIB — PAPAN ZIWEI DOUSHU" + "### Data Inti Peta" + "### Empat Transformasi"
  MD3 (Lin Wen Han): "BAB 1: PETA NASIB" + "### 🔑 Transformasi Bintang"
"""
import re
from canonical_model import ZiWei, Transformasi, Palace, HzTerm, KeyValue
from extractors.md_utils import strip_md_bold, split_hz_indo


ZIWEI_TITLE_KW = ["PETA BINTANG ZIWEI", "PETA NASIB", "PAPAN ZIWEI", "ZIWEI DOUSHU",
                  "ZI WEI DOU SHU", "紫微", "MING PAN", "命盤"]


def _find_section(sections):
    """Find ZiWei H2 section. Prefer one with sub-sections (richest content)."""
    matches = []
    for s in sections:
        t = s["title"].upper()
        if any(k in t for k in ZIWEI_TITLE_KW):
            matches.append(s)
    if not matches: return None
    # Prefer section with most useful subs (data inti / transformasi / palaces)
    def _score(s):
        n_sub = len(s.get("sub") or [])
        n_lines = len(s.get("lines") or [])
        # Penalize meta-only sections (only software sub)
        for sub in s.get("sub") or []:
            if re.search(r"\bsoftware\b", sub.get("title",""), re.IGNORECASE):
                return n_sub * 1 + n_lines * 0.05
        return n_sub * 10 + n_lines * 0.1
    matches.sort(key=_score, reverse=True)
    return matches[0]


def _parse_table_rows_in_sub(sub_lines):
    """Parse first markdown pipe table in sub-section lines. Return list of rows."""
    rows = []
    in_table = False
    for line in sub_lines:
        if "|" not in line:
            if in_table and rows: break
            continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line):
            in_table = True
            continue
        if in_table:
            cells = [strip_md_bold(c.strip()) for c in line.strip().strip("|").split("|")]
            if cells and cells[0]:
                rows.append(cells)
    return rows


def _find_sub(section, title_re):
    """Find first H3 sub-section whose title matches regex."""
    for sub in section.get("sub", []) or []:
        if title_re.search(sub.get("title", "")):
            return sub
    return None


# ─────────────────────────────────────────────────────────────────────────
# Sub-extractors
# ─────────────────────────────────────────────────────────────────────────

DATA_INTI_RE = re.compile(r"\b(data\s+inti|informasi\s+dasar|elemen\s+inti|inti\s+peta)\b", re.IGNORECASE)
TRANSFORMASI_RE = re.compile(r"\b(transformasi\s+bintang|empat\s+transformasi|transformasi.*?\(?四化|si\s*hua|四化|化星)\b", re.IGNORECASE)
ISTANA_RE = re.compile(r"\b(struktur\s+dua\s+belas|dua\s+belas\s+istana|ringkasan\s+12\s+istana|12\s+istana|十二宮|istana[-\s]+istana)\b", re.IGNORECASE)


def _extract_data_inti(section):
    """Parse Data Inti table → list of KeyValue."""
    sub = _find_sub(section, DATA_INTI_RE)
    if not sub: return []
    rows = _parse_table_rows_in_sub(sub["lines"])
    out = []
    for r in rows:
        if len(r) < 2: continue
        # Skip header row
        if r[0].lower() in ("elemen", "keterangan", "data", "kategori", "key"): continue
        key = r[0]
        val = r[1] if len(r) > 1 else ""
        # Extract Hanzi from key
        hz = ""
        m = re.search(r"([一-鿿]+)", key)
        if m: hz = m.group(1)
        out.append(KeyValue(key=key, value=val, hz=hz, indo=val))
    return out


def _extract_transformasi(section):
    """Parse Empat Transformasi table → list of Transformasi."""
    sub = _find_sub(section, TRANSFORMASI_RE)
    if not sub: return []
    rows = _parse_table_rows_in_sub(sub["lines"])
    out = []
    for r in rows:
        if len(r) < 2: continue
        if r[0].lower() in ("bintang", "star", "no.", "no", "name"): continue
        # Star: "**武曲 (Wuqu)**"
        star_hz, star_indo = split_hz_indo(r[0])
        # Role: "化祿 (Jadi Rezeki)"
        role_cell = r[1]
        role_hz, role_indo = split_hz_indo(role_cell)
        if not role_hz:
            # Maybe role inline like "化祿 — Rezeki"
            m = re.match(r"^([一-鿿]+)\s*[—\-:(]\s*(.+?)\)?$", role_cell)
            if m:
                role_hz = m.group(1)
                role_indo = m.group(2).strip().rstrip(")")
        makna = r[2] if len(r) > 2 else None
        if star_hz:
            out.append(Transformasi(
                star_hz=star_hz, star_indo=star_indo or None,
                role_hz=role_hz or "", role_indo=role_indo or None,
                makna=makna,
            ))
    return out


# Mapping istana Hanzi → Indo (canonical names for grid order)
PALACE_HZ_INDO = [
    ("命宮",   "Istana Nasib"),
    ("兄弟宮", "Istana Saudara"),
    ("兄弟",   "Istana Saudara"),
    ("夫妻宮", "Istana Pasangan"),
    ("夫妻",   "Istana Pasangan"),
    ("子女宮", "Istana Anak"),
    ("子女",   "Istana Anak"),
    ("財帛宮", "Istana Keuangan"),
    ("財帛",   "Istana Keuangan"),
    ("疾厄宮", "Istana Kesehatan"),
    ("疾厄",   "Istana Kesehatan"),
    ("遷移宮", "Istana Perpindahan"),
    ("遷移",   "Istana Perpindahan"),
    ("僕役宮", "Istana Bawahan"),
    ("僕役",   "Istana Bawahan"),
    ("官祿宮", "Istana Karier"),
    ("官祿",   "Istana Karier"),
    ("田宅宮", "Istana Properti"),
    ("田宅",   "Istana Properti"),
    ("福德宮", "Istana Kebahagiaan"),
    ("福德",   "Istana Kebahagiaan"),
    ("父母宮", "Istana Orang Tua"),
    ("父母",   "Istana Orang Tua"),
]


def _extract_palaces(section):
    """Parse 12 Istana table → list of Palace.
    Headers vary: MD1 = [Istana, Nama Mandarin, Arti, Cabang Bumi]
                  MD3 = [No., Istana, Bintang Utama, Rentang Usia, Sayap]
    """
    sub = _find_sub(section, ISTANA_RE)
    if not sub: return []
    rows = _parse_table_rows_in_sub(sub["lines"])
    out = []
    for r in rows:
        if len(r) < 2: continue
        # Detect header row
        first = r[0].lower()
        if first in ("istana", "no.", "no", "palace", "name", "nama"): continue

        # Strategy: find Hanzi istana name in any cell
        nama_hz = ""
        nama_id = ""
        for cell in r[:3]:
            m = re.search(r"([一-鿿]{2,3}宮?)", cell)
            if m:
                nama_hz = m.group(1)
                # Lookup canonical Indo name
                for hz, indo in PALACE_HZ_INDO:
                    if hz == nama_hz or hz in nama_hz:
                        nama_id = indo
                        break
                if nama_id: break

        if not nama_hz: continue

        # Bintang utama: cell 2-3 with Hanzi star names
        bintang = []
        for cell in r[1:]:
            stars_in_cell = re.findall(r"([一-鿿]{2,3})", cell)
            for st in stars_in_cell:
                if st == nama_hz: continue
                # Skip if same as palace or already added
                if any(b.hz == st for b in bintang): continue
                bintang.append(HzTerm(hz=st))
                if len(bintang) >= 3: break
            if bintang: break

        # Age range
        age_range = None
        for cell in r:
            m = re.search(r"(\d{2,3})\s*[-–—]\s*(\d{2,3})", cell)
            if m: age_range = f"{m.group(1)}-{m.group(2)}"; break

        # Cabang Bumi (ganzhi)
        ganzhi = None
        for cell in r:
            m = re.search(r"\b([子丑寅卯辰巳午未申酉戌亥])\b", cell)
            if m: ganzhi = m.group(1); break

        out.append(Palace(
            nama_id=nama_id or nama_hz,
            nama_hz=nama_hz,
            bintang_utama=bintang,
            age_range=age_range,
            ganzhi=ganzhi,
        ))
    return out


# ─────────────────────────────────────────────────────────────────────────
# Interpretasi (subject-specific blockquote near top)
# ─────────────────────────────────────────────────────────────────────────

def _extract_interpretasi(lines):
    """Find subject-specific blockquote (💡 etc.) — same strategy as BaZi."""
    GENERIC = re.compile(r"^[\W_]*apa\s+itu\b", re.IGNORECASE)
    META = re.compile(r"^[⚠📌🗓\s]*(catatan|warning|note|sumber|laporan)\b", re.IGNORECASE)
    SUBJ = re.compile(r"\b(makna|tips|interpretasi|saran|tafsir|penjelasan|gambaran|inti|temuan)\b", re.IGNORECASE)
    EMOJI = ("💡","💼","❤️","✦","🔮","🎯","💎","🌟","📜")

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s*", "", lines[i].strip()))
                i += 1
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", " ".join(buf)).strip()
            if not text or len(text) < 30: continue
            if GENERIC.search(text[:60]) or META.match(text): continue
            if any(text.startswith(e) for e in EMOJI) or SUBJ.search(text[:80]):
                return text
        else:
            i += 1
    return None


# ─────────────────────────────────────────────────────────────────────────
# Main extractor
# ─────────────────────────────────────────────────────────────────────────

def _synthesize_interpretasi(zw):
    """Fallback: synthesize narrative from extracted structured data when MD has no
    subject-specific blockquote. NOT fabrication — just rephrase data we already have.
    """
    parts = []
    # From Data Inti: 命主 + 身主
    ming_zhu = ""
    shen_zhu = ""
    for kv in zw.data_inti:
        key = kv.key.lower()
        if "命主" in kv.key or "penguasa nasib" in key or "penguasa kehidupan" in key:
            ming_zhu = kv.value
        elif "身主" in kv.key or "penguasa tubuh" in key:
            shen_zhu = kv.value
    if ming_zhu or shen_zhu:
        seg = "Bagan Anda dipimpin oleh"
        if ming_zhu: seg += f" Penguasa Nasib (命主) {ming_zhu}"
        if ming_zhu and shen_zhu: seg += " dan"
        if shen_zhu: seg += f" Penguasa Tubuh (身主) {shen_zhu}"
        parts.append(seg + ".")

    # From Transformasi
    if zw.transformasi:
        roles = {"化祿": "rezeki", "化權": "kekuasaan", "化科": "ketenaran/akademik", "化忌": "hambatan"}
        trans_parts = []
        for t in zw.transformasi:
            role_label = roles.get(t.role_hz, t.role_indo or "")
            if t.star_hz and role_label:
                trans_parts.append(f"{t.star_hz} ({t.star_indo or ''}) membawa {role_label}")
        if trans_parts:
            parts.append("Empat transformasi bintang: " + "; ".join(trans_parts) + ".")

    # From palaces (if no data_inti, summarize palace count)
    if not zw.data_inti and zw.palaces:
        palace_with_stars = [p for p in zw.palaces if p.bintang_utama]
        if palace_with_stars:
            sample = palace_with_stars[0]
            star = sample.bintang_utama[0].hz if sample.bintang_utama else ""
            parts.append(f"Terdapat {len(zw.palaces)} istana hidup yang masing-masing memengaruhi satu dimensi kehidupan Anda. Contohnya, Istana Nasib dihuni bintang {star}.")
        else:
            parts.append(f"Terdapat {len(zw.palaces)} istana hidup yang masing-masing memengaruhi satu dimensi kehidupan Anda.")

    if not parts: return None
    return " ".join(parts)


def extract_ziwei(sections):
    sec = _find_section(sections)
    if not sec: return None

    zw = ZiWei()
    zw.data_inti = _extract_data_inti(sec)
    zw.transformasi = _extract_transformasi(sec)
    zw.palaces = _extract_palaces(sec)
    zw.interpretasi = _extract_interpretasi(sec["lines"])
    # Fallback: synthesize from extracted data when no MD blockquote
    if not zw.interpretasi:
        zw.interpretasi = _synthesize_interpretasi(zw)

    # If nothing extracted, return None
    if not (zw.data_inti or zw.transformasi or zw.palaces or zw.interpretasi):
        return None
    return zw
