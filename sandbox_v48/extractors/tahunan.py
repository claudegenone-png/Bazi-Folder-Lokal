"""Tahunan extractor — per-year forecast cards."""
import re
from canonical_model import Tahun, Bullet, HzTerm
from extractors.md_utils import strip_md_bold


# Year header patterns — adaptive across MD variants.
# Captures: (stars_optional, year, age_optional, ganzhi_optional)
YEAR_HEADER_PATTERNS = [
    # Most permissive: any content before "Tahun YYYY ... Usia NN"
    re.compile(r"^###\s+.*?\bTahun\s+(\d{4}).*?Usia[:\s]*(\d+)", re.IGNORECASE),
    # With stars after year (MD4)
    re.compile(r"^###\s+.*?\bTahun\s+(\d{4}).*?(★+☆*)", re.IGNORECASE),
    # Simple "Tahun YYYY" fallback
    re.compile(r"^###\s+.*?\bTahun\s+(\d{4})\b", re.IGNORECASE),
]


def _parse_year_header(line):
    """Return (year, age, stars, ganzhi, ganzhi_indo) — fields may be None."""
    for pat in YEAR_HEADER_PATTERNS:
        m = pat.match(line)
        if m:
            year = int(m.group(1))
            # Try age (group 2 if numeric)
            age = None
            try:
                if len(m.groups()) >= 2 and m.group(2) and m.group(2).isdigit():
                    age = int(m.group(2))
            except Exception: pass
            # Stars (★)
            stars = line.count("★") if "★" in line else None
            # Ganzhi pattern in line
            gz_m = re.search(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*年?", line)
            ganzhi = gz_m.group(1) if gz_m else None
            # Ganzhi Indo "(Kuda Api)"
            gi_m = re.search(r"\(([^)]+)\)", line)
            ganzhi_indo = gi_m.group(1).strip() if gi_m else None
            return year, age, stars, ganzhi, ganzhi_indo
    return None


def _classify_year_mood(stars):
    if stars is None: return None
    if stars >= 4: return "good"
    if stars >= 3: return "neutral"
    if stars >= 2: return "warn"
    return "bad"


# Sub-section labels in year body
TEMA_LBL = re.compile(r"\*\*\s*Tema(?:\s+Tahun)?\s*:?\s*\*\*\s*(.+?)(?=\n\s*\n|\n\s*\*\*|\n\s*###|$)", re.DOTALL | re.IGNORECASE)
SARAN_LBL = re.compile(r"\*\*\s*(?:💡\s*)?Saran\s*:?\s*\*\*\s*(.+?)(?=\n\s*\n|\n\s*\*\*|\n\s*###|$)", re.DOTALL | re.IGNORECASE)
POS_LBL = re.compile(r"^\*\*[^*]*?\b(hal\s+positif|kondisi\s+umum|positif)[^*]*\*\*\s*:?\s*$", re.IGNORECASE)
WARN_LBL = re.compile(r"^\*\*[^*]*?\b(yang\s+perlu\s+diwaspadai|hal\s+yang\s+perlu\s+diwaspadai|diwaspadai|negatif|tantangan)[^*]*\*\*\s*:?\s*$", re.IGNORECASE)
BINTANG_LBL = re.compile(r"^\*\*\s*Bintang\s+(?:Aktif|Masuk)[^*]*\*\*\s*:?\s*$", re.IGNORECASE)
RINGKASAN_BQ = re.compile(r"^>\s*\*\*\s*Ringkasan\s*:\s*\*\*\s*(.+)$", re.IGNORECASE)


def _parse_bullet(line):
    m = re.match(r"^\s*[-*]\s+(.+)$", line)
    if not m: return None
    content = m.group(1).strip()
    mb = re.match(r"^\*\*([^*]+)\*\*\s*[—–\-]\s*(.+)$", content)
    if mb:
        return Bullet(label=mb.group(1).strip(), text=mb.group(2).strip())
    return Bullet(text=strip_md_bold(content))


STAR_TEMA_LINE = re.compile(r"^\s*\*\*\s*([★☆]{3,5})\s*[—–\-:]\s*([^*]+?)\s*\*\*\s*$")
INTERPRETASI_HDR = re.compile(r"^\s*\*\*\s*[^*]*?Interpretasi[^*]*\*\*\s*:?\s*$", re.IGNORECASE)
INLINE_POS = re.compile(r"^\s*[✅✔]\s*\*\*\s*([^*:]+)\s*:?\s*\*\*\s*(.+?)\s*$")
INLINE_WARN = re.compile(r"^\s*[⚠❗⛔]\s*\*\*\s*([^*:]+)\s*:?\s*\*\*\s*(.+?)\s*$")
INLINE_BINTANG = re.compile(r"^\s*[🌟✨⭐]\s*\*\*\s*([^*:]+)\s*:?\s*\*\*\s*(.+?)\s*$")


def _parse_year_block(lines):
    """Parse single year block lines into Tahun (without year/age, set externally)."""
    tahun = Tahun()
    body = "\n".join(lines)

    # Stars + tema combo line: "**★★★★☆ — Tahun Baik untuk Berpikir**"
    for ln in lines:
        m = STAR_TEMA_LINE.match(ln)
        if m:
            tahun.stars_rating = m.group(1).count("★")
            tahun.tema = m.group(2).strip()
            break

    # Tema
    m = TEMA_LBL.search(body)
    if m and not tahun.tema:
        tema_raw = m.group(1).strip()
        # Strip leading * and italic markers
        tema_raw = re.sub(r"^\*\s*", "", tema_raw)
        tema_raw = re.sub(r"\*([^*]+)\*", r"\1", tema_raw)
        tahun.tema = tema_raw

    # Saran
    m = SARAN_LBL.search(body)
    if m:
        tahun.saran = strip_md_bold(m.group(1)).strip()

    # Ringkasan blockquote (V4.6 format)
    if not tahun.saran:
        for ln in lines:
            mb = RINGKASAN_BQ.match(ln.strip())
            if mb:
                tahun.saran = strip_md_bold(mb.group(1)).strip()
                break

    # Hal Positif / Yang Perlu Diwaspadai / Bintang Aktif buckets
    pos_bullets = []
    warn_bullets = []
    bintang_bullets = []
    toplevel_bullets = []
    cur = None
    for line in lines:
        s = line.strip()
        if not s: continue
        if POS_LBL.match(s): cur = "pos"; continue
        if WARN_LBL.match(s): cur = "warn"; continue
        if BINTANG_LBL.match(s): cur = "bintang"; continue
        # Inline emoji-prefixed paragraphs: ✅ **Peluang:** xxx → pos bullet
        m_p = INLINE_POS.match(s)
        if m_p:
            pos_bullets.append(Bullet(label=strip_md_bold(m_p.group(1)).strip(),
                                      text=strip_md_bold(m_p.group(2)).strip()))
            cur = None; continue
        m_w = INLINE_WARN.match(s)
        if m_w:
            warn_bullets.append(Bullet(label=strip_md_bold(m_w.group(1)).strip(),
                                       text=strip_md_bold(m_w.group(2)).strip()))
            cur = None; continue
        m_b = INLINE_BINTANG.match(s)
        if m_b:
            bintang_bullets.append(Bullet(label=strip_md_bold(m_b.group(1)).strip(),
                                          text=strip_md_bold(m_b.group(2)).strip()))
            cur = None; continue
        if re.match(r"^\*\*[^*]+\*\*", s) or s.startswith("###") or s == "---":
            cur = None; continue
        if re.match(r"^[-*]\s+", s):
            b = _parse_bullet(line)
            if not b: continue
            if cur == "pos": pos_bullets.append(b)
            elif cur == "warn": warn_bullets.append(b)
            elif cur == "bintang": bintang_bullets.append(b)
            else: toplevel_bullets.append(b)

    # Fallback: if no explicit pos/warn → toplevel goes to pos, bintang summarized as warn
    if not pos_bullets and not warn_bullets:
        pos_bullets = toplevel_bullets
        warn_bullets = bintang_bullets[:2]
    elif bintang_bullets and not warn_bullets:
        warn_bullets = bintang_bullets[:2]

    tahun.hal_positif = pos_bullets[:5]
    tahun.hal_diwaspadai = warn_bullets[:4]

    # Bintang aktif raw HzTerm list (just first 3 mentioned)
    BINTANG_HZ_PAT = re.compile(r"\*\*\s*Bintang\s+Aktif\s*:?\s*\*\*\s*([^\n]+)", re.IGNORECASE)
    m = BINTANG_HZ_PAT.search(body)
    if m:
        raw = m.group(1)
        for hz in re.findall(r"([一-鿿]{2,4})", raw)[:3]:
            tahun.bintang_aktif.append(HzTerm(hz=hz))

    # Narasi: paragraph immediately after **Interpretasi** header (subject 2 style),
    # else first plain paragraph that is NOT predominantly Hanzi (not a Transkripsi).
    cap_next = False
    for ln in lines:
        s = ln.strip()
        if INTERPRETASI_HDR.match(s):
            cap_next = True; continue
        if cap_next and s and not s.startswith(("**", "-", "*", "#", ">", "---", "✅", "⚠", "🌟", "✨", "❗")):
            han = sum(1 for c in s if "一" <= c <= "鿿")
            latn = sum(1 for c in s if c.isalpha() and ord(c) < 128)
            if han <= latn * 1.5:
                tahun.narasi = strip_md_bold(s); break
            cap_next = False
    if not tahun.narasi:
        for ln in lines:
            s = ln.strip()
            if not s or s.startswith(("**", "-", "*", "#", ">", "---", "✅", "⚠", "🌟", "✨", "❗")): continue
            han = sum(1 for c in s if "一" <= c <= "鿿")
            latn = sum(1 for c in s if c.isalpha() and ord(c) < 128)
            if han > latn * 1.5: continue  # skip raw Hanzi transcription
            tahun.narasi = strip_md_bold(s); break

    return tahun


def _count_year_h3(lines):
    """Count how many `### Tahun YYYY` style headers in lines."""
    cnt = 0
    for line in lines:
        if line.startswith("### "):
            for pat in YEAR_HEADER_PATTERNS:
                if pat.match(line): cnt += 1; break
    return cnt


def _year_sub_count(sec):
    """For deep-mode sections: count H3 subs whose title matches year pattern."""
    cnt = 0
    for sub in sec.get("sub", []) or []:
        if re.match(r"^.*?\bTahun\s+\d{4}\b", sub.get("title", ""), re.IGNORECASE):
            cnt += 1
    return cnt


def extract_tahunan(sections):
    """Find Tahunan section by H3 year-header count + topic keyword."""
    tahunan_sec = None
    is_deep = any("sub" in s for s in sections)

    # Strategy 1: title keyword + has year H3
    for s in sections:
        t = s["title"].upper()
        if "TABEL" in t: continue  # exclude tabel-tahunan-detail
        has_kw = any(k in t for k in ["RAMALAN TAHUNAN", "BESAR NASIB", "ANALISIS TAHUN", "TAHUN-TAHUN"])
        cnt = _year_sub_count(s) if is_deep else _count_year_h3(s["lines"])
        if has_kw and cnt >= 2:
            tahunan_sec = s; break
    # Strategy 2: any section with multiple year H3s
    if not tahunan_sec:
        best = None; best_cnt = 0
        for s in sections:
            if "TABEL" in s["title"].upper(): continue
            cnt = _year_sub_count(s) if is_deep else _count_year_h3(s["lines"])
            if cnt > best_cnt: best = s; best_cnt = cnt
        if best_cnt >= 2: tahunan_sec = best
    if not tahunan_sec:
        return []

    # In deep mode: build year_blocks directly from .sub entries
    if is_deep and tahunan_sec.get("sub"):
        out = []
        for sub in tahunan_sec["sub"]:
            title = sub.get("title", "")
            # Reconstruct a synthetic ### header line so existing patterns work
            synth = "### " + title
            parsed = _parse_year_header(synth)
            if not parsed: continue
            tahun = _parse_year_block(sub.get("lines", []))
            year, age, stars, ganzhi, ganzhi_indo = parsed
            tahun.year = year
            tahun.age = age
            # _parse_year_block may have set stars from body; only overwrite if header had them
            if stars is not None:
                tahun.stars_rating = stars
            tahun.ganzhi = ganzhi
            tahun.ganzhi_indo = ganzhi_indo
            tahun.mood = _classify_year_mood(tahun.stars_rating)
            out.append(tahun)
        return out

    lines = tahunan_sec["lines"]
    # Split per H3 year header
    year_blocks = []
    cur_block = None
    cur_meta = None
    for line in lines:
        if line.startswith("### "):
            parsed = _parse_year_header(line)
            if parsed:
                if cur_block and cur_meta:
                    year_blocks.append((cur_meta, cur_block))
                cur_meta = parsed
                cur_block = []
                continue
            else:
                # Non-year H3 inside tahunan section (e.g. "Tabel Besar Nasib") — close current
                if cur_block and cur_meta:
                    year_blocks.append((cur_meta, cur_block))
                    cur_meta = None; cur_block = None
                continue
        if cur_block is not None:
            cur_block.append(line)
    if cur_block and cur_meta:
        year_blocks.append((cur_meta, cur_block))

    out = []
    for meta, block_lines in year_blocks:
        year, age, stars, ganzhi, ganzhi_indo = meta
        tahun = _parse_year_block(block_lines)
        tahun.year = year
        tahun.age = age
        tahun.stars_rating = stars
        tahun.ganzhi = ganzhi
        tahun.ganzhi_indo = ganzhi_indo
        tahun.mood = _classify_year_mood(stars)
        out.append(tahun)
    return out
