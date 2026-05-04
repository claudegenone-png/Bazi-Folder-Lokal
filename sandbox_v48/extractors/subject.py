"""Subject identitas extractor.

Multi-strategy: tries multiple section heading patterns + multiple field key aliases.
Always returns a Subject model (never None); fields may be None when absent.
"""
import re
from canonical_model import Subject, HzTerm
from extractors.md_utils import (
    split_sections, parse_kv_table, strip_md_bold, split_hz_indo,
    find_section_by_keyword
)


SUBJECT_HEADING_KEYWORDS = [
    "IDENTITAS PEMILIK", "IDENTITAS SUBJEK", "IDENTITAS KLIEN",
    "DATA PEMILIK", "DATA SUBJEK", "DATA KLIEN", "DATA IDENTITAS",
    "PROFIL SUBJEK", "PROFIL KLIEN", "PROFIL PEMILIK",
    "INFORMASI DASAR", "IDENTITAS",
]


# Field aliases — multiple MD use different key labels for same data
NAMA_ALIASES = ["nama", "姓名", "name"]
GENDER_ALIASES = ["jenis kelamin", "性別", "gender"]
SHIO_ALIASES = ["shio", "生肖", "zodiac"]
LAHIR_TGL_ALIASES = [
    "tanggal lahir", "tanggal lahir (nasional)", "tanggal lahir masehi",
    "tanggal lahir (gregorian)", "hari lahir (gregorian)", "tanggal lahir (masehi)",
    "國曆生日",
]
LUNAR_ALIASES = [
    "tanggal lahir (lunar)", "tanggal lunar", "tanggal lahir lunar",
    "agama lunar", "農曆生日", "kalender lunar", "tanggal lahir (imlek)",
    "tanggal lahir (tionghoa)",
]
JAM_ALIASES = ["jam lahir", "生時", "waktu lahir"]
HARI_ALIASES = ["hari lahir", "hari", "星期"]
TAHUN_ALIASES = ["tahun masehi", "tahun lahir (masehi)", "tahun nasional", "西元"]
KAL_NAS_ALIASES = ["kalender nasional", "tanggal nasional", "國曆生年", "民國"]
YIN_YANG_ALIASES = ["yin/yang", "yin-yang", "陰陽"]
LIMA_UNSUR_ALIASES = ["lima unsur", "lima elemen", "五行"]
MING_ZHU_ALIASES = ["bintang utama jiwa", "bintang utama kehidupan", "命主"]
SHEN_ZHU_ALIASES = ["bintang tubuh", "身主"]
MING_GONG_ALIASES = ["istana jiwa", "istana kehidupan", "命宮"]
SHEN_GONG_ALIASES = ["istana tubuh", "身宮"]


def _normalize_key(raw_key):
    """Normalize a row key: strip md-bold, lower, strip parens, strip Hanzi."""
    k = strip_md_bold(raw_key).lower().strip()
    k_no_parens = re.sub(r"\(.*?\)", "", k).strip(" :")
    k_no_hz = re.sub(r"[一-鿿]+", "", k).strip(" :()-—–").strip()
    return k, k_no_parens, k_no_hz


def _key_matches(raw_key, aliases, exact=False):
    """Match raw_key against aliases. exact=True requires alias == any normalized form."""
    forms = _normalize_key(raw_key)
    forms = {f for f in forms if f}
    for alias in aliases:
        a = alias.lower().strip()
        if exact:
            if a in forms: return True
        else:
            # word-boundary substring check
            for f in forms:
                if a == f: return True
                # word-boundary regex: alias must appear as full word(s) in form
                if re.search(r"\b" + re.escape(a) + r"\b", f): return True
    return False


def _find_value(rows, aliases):
    """Find value matching aliases. Two-pass: exact match first, then fuzzy."""
    # Pass 1: exact normalized match
    for k, v in rows:
        if _key_matches(k, aliases, exact=True):
            return strip_md_bold(v).strip()
    # Pass 2: word-boundary fuzzy match
    for k, v in rows:
        if _key_matches(k, aliases, exact=False):
            return strip_md_bold(v).strip()
    return None


def extract_subject(md_text):
    """Extract Subject model. Always returns a Subject (may have empty fields)."""
    sections = split_sections(md_text)

    # Strategy 1: H2 with subject heading keyword
    sec = find_section_by_keyword(sections, SUBJECT_HEADING_KEYWORDS, level=2)

    # Strategy 2: H3 within H2 like "## I. DATA IDENTITAS" → "### A. Informasi Dasar"
    if not sec:
        # Look for any H3 with informasi/data keyword
        for s in sections:
            if s["level"] == 3 and any(k in s["title"].upper() for k in ["INFORMASI DASAR", "DATA DASAR"]):
                sec = s; break

    # Strategy 3: any heading with Identitas keyword (more relaxed)
    if not sec:
        for s in sections:
            if "IDENTITAS" in s["title"].upper() or "PROFIL" in s["title"].upper():
                sec = s; break

    if not sec:
        return Subject()

    # Parse pipe table from section lines
    rows = parse_kv_table(sec["lines"])
    rows_pairs = [(r[0], r[1]) for r in rows if len(r) >= 2]

    subj = Subject()

    # Nama
    nama_raw = _find_value(rows_pairs, NAMA_ALIASES)
    if nama_raw:
        hz, latin = split_hz_indo(nama_raw)
        if hz and latin:
            subj.nama_hanzi = hz
            subj.nama = latin
        elif hz:
            # Hanzi-only nama → still need an Indo equivalent for cover; use Hanzi as-is
            subj.nama_hanzi = hz
            subj.nama = hz
        else:
            subj.nama = latin or nama_raw

    # Per-subject display normalization (user-requested formatting)
    NAMA_NORMALIZE = {
        "Li Yuanxiang": "Li Yuan Xiang",
    }
    if subj.nama in NAMA_NORMALIZE:
        subj.nama = NAMA_NORMALIZE[subj.nama]

    # Gender — normalize to "Pria"/"Perempuan" + extract Yin/Yang separately
    g = _find_value(rows_pairs, GENDER_ALIASES)
    if g:
        hz, latin = split_hz_indo(g)
        # Normalize "Pria Yin" / "Wanita Yin" / "陰女 (Wanita Yin)" etc
        text_lower = (latin or g).lower()
        if "pria" in text_lower or "男" in (hz or g) or "laki" in text_lower:
            subj.gender = "Pria"
        elif "wanita" in text_lower or "perempuan" in text_lower or "女" in (hz or g):
            subj.gender = "Perempuan"
        else:
            subj.gender = latin or g
        # Extract yin/yang
        if "陰" in (hz or g) or "yin" in text_lower:
            subj.yin_yang = "Yin"
        elif "陽" in (hz or g) or "yang" in text_lower:
            subj.yin_yang = "Yang"

    # Yin-Yang explicit (override if separate field)
    yy = _find_value(rows_pairs, YIN_YANG_ALIASES)
    if yy:
        if "陰" in yy or "yin" in yy.lower(): subj.yin_yang = "Yin"
        elif "陽" in yy or "yang" in yy.lower(): subj.yin_yang = "Yang"

    # Shio
    s = _find_value(rows_pairs, SHIO_ALIASES)
    if s:
        hz, latin = split_hz_indo(s)
        subj.shio_hz = hz or None
        subj.shio = latin or s

    # Lahir tanggal
    subj.lahir_tanggal = _find_value(rows_pairs, LAHIR_TGL_ALIASES)
    subj.lahir_lunar = _find_value(rows_pairs, LUNAR_ALIASES)
    subj.lahir_jam = _find_value(rows_pairs, JAM_ALIASES)
    subj.hari_lahir = _find_value(rows_pairs, HARI_ALIASES)
    subj.kalender_nasional = _find_value(rows_pairs, KAL_NAS_ALIASES)
    subj.tahun_masehi = _find_value(rows_pairs, TAHUN_ALIASES)
    subj.lima_unsur = _find_value(rows_pairs, LIMA_UNSUR_ALIASES)

    # Normalize tahun_masehi: extract last 4-digit year from verbose value
    if subj.tahun_masehi:
        years = re.findall(r"(?:19|20)\d{2}", subj.tahun_masehi)
        if years: subj.tahun_masehi = years[-1]
    # If still missing, derive from any date field
    if not subj.tahun_masehi:
        for src in (subj.lahir_tanggal, subj.lahir_lunar, subj.kalender_nasional):
            if src:
                m = re.search(r"(?:19|20)\d{2}", src)
                if m: subj.tahun_masehi = m.group(0); break

    # If lahir_tanggal absent but kalender_nasional contains Indonesian date, use it
    if not subj.lahir_tanggal and subj.kalender_nasional:
        # Common indicator: contains a month name in Indo or "/" with year
        if re.search(r"\d+\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}", subj.kalender_nasional):
            subj.lahir_tanggal = subj.kalender_nasional

    # ZiWei core (optional in identitas)
    def _hzterm(raw):
        if not raw: return None
        hz, latin = split_hz_indo(raw)
        return HzTerm(hz=hz or "", indo=latin or "")

    subj.ming_zhu = _hzterm(_find_value(rows_pairs, MING_ZHU_ALIASES))
    subj.shen_zhu = _hzterm(_find_value(rows_pairs, SHEN_ZHU_ALIASES))
    subj.ming_gong = _hzterm(_find_value(rows_pairs, MING_GONG_ALIASES))
    subj.shen_gong = _hzterm(_find_value(rows_pairs, SHEN_GONG_ALIASES))

    return subj
