"""BaZi extractor — 4 pilar table + transformasi + yong/xi shen."""
import re
from canonical_model import BaZi, Pilar, HzTerm
from lookups.hanzi_universal import GAN_INDO, ZHI_INDO, GAN_ELEMEN, ZHI_ELEMEN, TENGOD_INDO
from extractors.md_utils import strip_md_bold


# Row label patterns — multiple MD variants
TIAN_GAN_PAT = re.compile(r"\bbatang\s*langit\b|\b天干\b", re.IGNORECASE)
DI_ZHI_PAT = re.compile(r"\bcabang\s*bumi\b|\b地支\b", re.IGNORECASE)
TEN_GOD_PAT = re.compile(r"\bten\s*god\b|\b十神\b|\bhubungan\b", re.IGNORECASE)


def _extract_pilar_chars(cell: str):
    """From a cell like '乙 (Yi/Kayu Yin)' or '甲' return the leading Hanzi."""
    cell = strip_md_bold(cell).strip()
    m = re.match(r"^([一-鿿])", cell)
    return m.group(1) if m else ""


def _has_pilar_table(lines):
    """Check if these lines contain a 4-pillar BaZi table."""
    for line in lines:
        if "|" in line and (TIAN_GAN_PAT.search(line) or DI_ZHI_PAT.search(line)):
            return True
    return False


def extract_bazi(sections, all_lines):
    """Find BaZi section by content (table presence) + topic keyword.

    `sections`: deep H2 sections (each with `lines` containing all H3 sub-content)
    `all_lines`: list[str] of full MD (for cross-section lookups)
    """
    # Strategy 1: section with title keyword AND has pillar table
    bazi_sec = None
    for s in sections:
        t = s["title"].upper()
        has_kw = any(k in t for k in ["BA ZI", "BAZI", "EMPAT PILAR", "四柱", "八字", "SI ZHU"])
        if has_kw and _has_pilar_table(s["lines"]):
            bazi_sec = s; break
    # Strategy 2: any section that has the pillar table
    if not bazi_sec:
        for s in sections:
            if _has_pilar_table(s["lines"]):
                bazi_sec = s; break

    if not bazi_sec:
        return None

    bazi = BaZi()
    lines = bazi_sec["lines"]

    # Parse pillar table rows
    gans = ["", "", "", ""]
    zhis = ["", "", "", ""]
    ten_gods = ["", "", "", ""]
    for line in lines:
        if "|" not in line: continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5: continue
        label = strip_md_bold(cells[0])
        # Detect row type
        if TIAN_GAN_PAT.search(label):
            for i in range(4):
                gans[i] = _extract_pilar_chars(cells[1+i])
        elif DI_ZHI_PAT.search(label):
            for i in range(4):
                zhis[i] = _extract_pilar_chars(cells[1+i])
        elif TEN_GOD_PAT.search(label):
            for i in range(4):
                tg_cell = strip_md_bold(cells[1+i])
                # Extract first known ten-god compound
                for tg_hz in sorted(TENGOD_INDO.keys(), key=lambda x: -len(x)):
                    if tg_hz in tg_cell:
                        ten_gods[i] = tg_hz
                        break

    # Variant aliases for OCR-typo cases
    TENGOD_ALIASES = {
        "令主": "命主",     # Lin Wen Han: 令主 (Ling Zhu) typo for 命主
        "正時": "正官",     # Lin Wen Han: 正時 (Zheng Shi) typo for 正官
        "Hari Utama": "命主",  # Lin Ruyi: text-only "Hari Utama"
    }

    # Re-scan ten god row for textual aliases (English/Indonesian fallback)
    for line in lines:
        if "|" not in line: continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5: continue
        label = strip_md_bold(cells[0])
        if not TEN_GOD_PAT.search(label): continue
        for i in range(4):
            if ten_gods[i]: continue  # already extracted
            tg_cell = strip_md_bold(cells[1+i])
            for alias, canonical in TENGOD_ALIASES.items():
                if alias in tg_cell:
                    ten_gods[i] = canonical
                    break

    # Build Pilar list (4 pilar standard)
    POSISI = [("Tahun","年"), ("Bulan","月"), ("Hari","日"), ("Jam","時")]
    for i, (pos, pos_hz) in enumerate(POSISI):
        if not (gans[i] or zhis[i]):
            continue
        gan_term = None
        if gans[i]:
            gan_term = HzTerm(hz=gans[i], indo=GAN_INDO.get(gans[i], ""))
        zhi_term = None
        if zhis[i]:
            zhi_term = HzTerm(hz=zhis[i], indo=ZHI_INDO.get(zhis[i], ""))
        elem = GAN_ELEMEN.get(gans[i], "")
        is_dm = (i == 2)
        # Default DM ten god to 命主 (Hari Utama) — convention regardless of MD content
        if is_dm and not ten_gods[i]:
            ten_gods[i] = "命主"
        ten_god = None
        if ten_gods[i]:
            ten_god = HzTerm(hz=ten_gods[i], indo=TENGOD_INDO.get(ten_gods[i], ""))
        bazi.pilar.append(Pilar(
            posisi=pos, posisi_hz=pos_hz,
            gan=gan_term, zhi=zhi_term, elem=elem,
            ten_god=ten_god, is_day_master=is_dm,
        ))

    # Yong / Xi / Ji shen from any 喜用神 section/table
    # Pattern: row "用神" → value containing 木/火/etc with description
    text = "\n".join(all_lines)
    YS_PAT = re.compile(r"\*\*\s*用神[^*]*\*\*\s*\|?\s*([^\n|]+)", re.MULTILINE)
    XS_PAT = re.compile(r"\*\*\s*喜神[^*]*\*\*\s*\|?\s*([^\n|]+)", re.MULTILINE)
    JS_PAT = re.compile(r"\*\*\s*忌神[^*]*\*\*\s*\|?\s*([^\n|]+)", re.MULTILINE)
    def _parse_shen(pat):
        m = pat.search(text)
        if not m: return None
        v = m.group(1).strip()
        hz_m = re.search(r"([一-鿿])", v)
        # Indo: try to grab inside parens "(Kayu)" etc
        indo_m = re.search(r"\(([^)]+)\)", v)
        return HzTerm(hz=hz_m.group(1) if hz_m else "",
                      indo=indo_m.group(1).strip() if indo_m else v.strip())
    bazi.yong_shen = _parse_shen(YS_PAT)
    bazi.xi_shen = _parse_shen(XS_PAT)
    bazi.ji_shen = _parse_shen(JS_PAT)

    # Compute Wu Xing distribution from pilar gan + zhi
    elem_count = {"Kayu": 0, "Api": 0, "Tanah": 0, "Logam": 0, "Air": 0}
    for p in bazi.pilar:
        if p.gan and p.gan.hz in GAN_ELEMEN:
            elem_count[GAN_ELEMEN[p.gan.hz]] += 1
        if p.zhi and p.zhi.hz in ZHI_ELEMEN:
            elem_count[ZHI_ELEMEN[p.zhi.hz]] += 1
    bazi.wuxing_count = elem_count

    # Extract interpretasi (Indonesian intro) from BaZi section
    bazi.interpretasi = _extract_interpretasi(bazi_sec["lines"])

    return bazi if bazi.pilar else None


_GENERIC_INTRO = re.compile(r"^[\W_]*apa\s+itu\b", re.IGNORECASE)
_WARN_META = re.compile(r"^[⚠📌🗓⚠️📌🗓️\s]*(catatan|warning|note|sumber|laporan ini|data terbaca)\b", re.IGNORECASE)
_SUBJECT_INTERP_KW = re.compile(r"\b(makna\s+praktis|tips\s+praktis|interpretasi|saran|tafsir|penjelasan|ringkasan|kesimpulan|wajah|gambaran|profil)\b", re.IGNORECASE)


def _is_skip_intro(text):
    """Skip generic 'Apa itu X?' educational intros + warnings/meta lines."""
    if not text: return True
    t = text.strip()
    if _GENERIC_INTRO.search(t[:60]): return True
    if _WARN_META.match(t): return True
    if t.startswith(("⚠", "📌", "🗓")): return True
    return False


def _is_subject_specific(text):
    """True if blockquote has subject-specific analysis emoji or keyword."""
    if not text: return False
    t = text.strip()
    # Subject analysis emojis + label patterns
    if t.startswith(("💡", "❤️", "👥", "💼", "🌟", "💎", "🎯", "✦", "📜", "🔮")):
        return True
    if _SUBJECT_INTERP_KW.search(t[:80]):
        return True
    return False


def _collect_blockquote(lines, start_idx):
    """Collect contiguous > lines starting at start_idx, return (text, end_idx)."""
    buf = []
    j = start_idx
    while j < len(lines) and lines[j].strip().startswith(">"):
        buf.append(re.sub(r"^>\s*", "", lines[j].strip()))
        j += 1
    text = " ".join(buf)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return strip_md_bold(text).strip(), j


def _extract_interpretasi(lines):
    """Extract subject-specific Indonesian interpretasi from section.
    Strategy priority:
      1. Subject-specific blockquote (💡 Makna Praktis, 💡 Tips Praktis, dll) — PREFER
      2. "### Interpretasi" / "### 🖊 Interpretasi" sub-section content
      3. Any non-skip blockquote (not "Apa itu", not Catatan/Warning)
      4. First plain paragraph (non-skip)
    Returns string or None.
    """
    # Strategy 1: subject-specific blockquote (anywhere in section, not just top)
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith(">"):
            text, j = _collect_blockquote(lines, i)
            if text and _is_subject_specific(text) and not _is_skip_intro(text):
                return text
            i = j
        else:
            i += 1

    # Strategy 2: "### Interpretasi" sub-section
    in_interp = False
    interp_buf = []
    for line in lines:
        s = line.strip()
        if re.match(r"^####?\s+[\W_]*\s*(interpretasi|tafsir|penjelasan|makna|saran)\b", s, re.IGNORECASE):
            in_interp = True; continue
        if in_interp:
            if s.startswith("##"): break
            if s.startswith(("|", "-", "*", "**", ">")): continue
            if s and s != "---":
                interp_buf.append(strip_md_bold(s))
    if interp_buf:
        text = " ".join(interp_buf)
        if not _is_skip_intro(text): return text

    # Strategy 3: any non-skip blockquote (fallback — even generic "Apa itu" if nothing else)
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith(">"):
            text, j = _collect_blockquote(lines, i)
            if text and not _is_skip_intro(text) and len(text) > 40:
                return text
            i = j
        else:
            i += 1

    # Strategy 4: first plain paragraph (last resort)
    para_buf = []
    for line in lines[:80]:
        s = line.strip()
        if not s:
            if para_buf:
                text = " ".join(para_buf)
                if not _is_skip_intro(text) and len(text) > 40: return text
                para_buf = []
            continue
        if s.startswith(("#", "|", "-", "*", ">", "**")) or s == "---": continue
        para_buf.append(strip_md_bold(s))
    if para_buf:
        text = " ".join(para_buf)
        if not _is_skip_intro(text) and len(text) > 40: return text

    return None


def derive_penguasa_hari(bazi: BaZi):
    """Return (indo, hanzi) tuple for cover Penguasa Hari row, or None."""
    if not bazi or len(bazi.pilar) < 3: return None
    dm = bazi.pilar[2]
    if not dm.gan: return None
    indo = GAN_INDO.get(dm.gan.hz, "")
    hz_full = dm.gan.hz + (dm.elem and {"Kayu":"木","Api":"火","Tanah":"土","Logam":"金","Air":"水"}.get(dm.elem, "") or "")
    return (indo, hz_full)


def derive_elemen_utama(bazi: BaZi):
    """Return list of (indo, hanzi) for Yong+Xi shen, or None."""
    if not bazi: return None
    out = []
    if bazi.yong_shen and bazi.yong_shen.hz:
        out.append((bazi.yong_shen.indo or "", bazi.yong_shen.hz))
    if bazi.xi_shen and bazi.xi_shen.hz:
        out.append((bazi.xi_shen.indo or "", bazi.xi_shen.hz))
    return out or None
