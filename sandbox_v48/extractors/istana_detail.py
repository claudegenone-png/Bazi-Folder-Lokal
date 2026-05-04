"""Istana Detail extractor — parses MD1-style 'INTERPRETASI DETAIL SETIAP ISTANA'
H2 collection with 12 sub-sections per istana. Each sub has Interpretasi + Saran.

Falls back to scanning ALL sections for individual istana topics if no collection
section found (MD2/MD3 style — each istana is own BAB).
"""
import re
from canonical_model import Palace, HzTerm
from extractors.md_utils import strip_md_bold


COLLECTION_TITLE_KW = [
    "INTERPRETASI DETAIL SETIAP ISTANA", "INTERPRETASI ISTANA",
    "DETAIL SETIAP ISTANA", "DETAIL ISTANA", "SETIAP ISTANA",
    "RINGKASAN 12 ISTANA", "12 ISTANA", "RINGKASAN ISTANA",
]

# Map istana Hanzi → canonical Indo name
ISTANA_HZ_INDO = {
    "命宮":   "Istana Nasib",       "兄弟宮": "Istana Saudara",
    "夫妻宮": "Istana Pasangan",     "子女宮": "Istana Anak",
    "財帛宮": "Istana Keuangan",     "疾厄宮": "Istana Kesehatan",
    "遷移宮": "Istana Perpindahan",  "僕役宮": "Istana Bawahan",
    "官祿宮": "Istana Karier",       "田宅宮": "Istana Properti",
    "福德宮": "Istana Kebahagiaan",  "父母宮": "Istana Orang Tua",
    "婚配":   "Kecocokan Shio",
    # also without 宮 suffix
    "命":     "Istana Nasib",       "兄弟": "Istana Saudara",
    "夫妻":   "Istana Pasangan",     "子女": "Istana Anak",
    "財帛":   "Istana Keuangan",     "疾厄": "Istana Kesehatan",
    "遷移":   "Istana Perpindahan",  "僕役": "Istana Bawahan",
    "官祿":   "Istana Karier",       "田宅": "Istana Properti",
    "福德":   "Istana Kebahagiaan",  "父母": "Istana Orang Tua",
}


def _find_collection_section(sections):
    """Find H2 with collection title + has 6+ sub-sections."""
    for s in sections:
        t = s["title"].upper()
        if any(k in t for k in COLLECTION_TITLE_KW):
            if len(s.get("sub", []) or []) >= 6:
                return s
    return None


def _parse_istana_title(raw_title):
    """Parse '🏠 3.1 【命宮】 — Istana Nasib (Kepribadian & Penampilan)' into
    (nama_hz, nama_id). Returns (None, None) if not istana title."""
    if not raw_title: return None, None
    # Find Hanzi inside 【】 brackets first
    m = re.search(r"【\s*([一-鿿]+宮?)\s*】", raw_title)
    if m:
        hz = m.group(1)
        # Find Indo after — separator
        m2 = re.search(r"[—–\-]\s*Istana\s+(.+?)(?:\s*\(|$)", raw_title)
        indo = ISTANA_HZ_INDO.get(hz, "")
        if m2 and not indo: indo = "Istana " + m2.group(1).strip()
        return hz, indo or hz
    # Fallback: find Hanzi 2-3 chars + maybe 宮
    m = re.search(r"([一-鿿]{2,3}宮?)", raw_title)
    if m:
        hz = m.group(1)
        indo = ISTANA_HZ_INDO.get(hz, "")
        return hz, indo or hz
    return None, None


def _parse_meta_line(line):
    """Parse '*Cabang Bumi: 丑 (Chou/Sapi) | Bintang Utama: 巨門 (Ju Men)*'
    Returns (ganzhi, bintang_hz, bintang_indo)."""
    if not line: return None, None, None
    s = line.strip().strip("*").strip()
    ganzhi = None; bintang_hz = None; bintang_indo = None
    # Cabang Bumi
    m = re.search(r"[Cc]abang\s+[Bb]umi[:：]\s*([子丑寅卯辰巳午未申酉戌亥])", s)
    if m: ganzhi = m.group(1)
    # Bintang Utama
    m = re.search(r"[Bb]intang(?:\s+[Uu]tama)?[:：]\s*([一-鿿]{2,4})\s*(?:\(([^)]+)\))?", s)
    if m:
        bintang_hz = m.group(1)
        bintang_indo = m.group(2).strip() if m.group(2) else None
    return ganzhi, bintang_hz, bintang_indo


def _extract_interpretasi_and_saran(lines):
    """From sub-section lines, extract:
       - interpretasi: text after '**✨ Interpretasi:**' / '**Interpretasi**' label
                       (skip blockquotes Hanzi raw, skip Transkripsi block)
       - saran: text from '> 💼 Saran:' / '> 👥 Saran:' subject-specific blockquote
       Returns (interpretasi, saran, saran_icon).
    """
    interpretasi_buf = []
    saran = None
    saran_icon = None
    saran_label = None

    in_interp = False
    seen_interp_label = False
    in_transkripsi = False

    INTERP_LBL = re.compile(r"\*\*[\W_]*\s*Interpretasi[^*]*\*\*\s*:?\s*$", re.IGNORECASE)
    TRANSKRIPSI_LBL = re.compile(r"\*\*[\W_]*\s*Transkripsi[^*]*\*\*\s*:?\s*$", re.IGNORECASE)
    # Subject-specific note keyword
    NOTE_KW = r"(Saran|Catatan|Tips|Note|Info|Pesan|Rekomendasi|Peringatan|Pengingat|Anjuran)"
    # Pattern A: blockquote `> 💼 **Saran:** body`
    SARAN_BQ = re.compile(r"^>\s*(\S+?)\s*\*\*\s*" + NOTE_KW + r"\b[^*]*\*\*\s*:?\s*(.*)$", re.IGNORECASE)
    SARAN_BQ_NO_ICON = re.compile(r"^>\s*\*\*\s*" + NOTE_KW + r"\b[^*]*\*\*\s*:?\s*(.*)$", re.IGNORECASE)
    # Pattern B: paragraph-level `**Saran:** body` (MD2/MD3 style, no blockquote)
    SARAN_INLINE = re.compile(r"^\*\*\s*" + NOTE_KW + r"\b[^*]*\*\*\s*:?\s*(.+)$", re.IGNORECASE)
    # Pattern C: standalone label `**Peringatan Penting:**` then bullets follow (multi-line)
    SARAN_STANDALONE = re.compile(r"^\*\*\s*" + NOTE_KW + r"\b[^*]*\*\*\s*:?\s*$", re.IGNORECASE)

    saran_extra_bullets = []  # for multi-line saran blockquote

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1; continue
        # Skip horizontal rule
        if s == "---":
            i += 1; continue

        # Saran blockquote (priority)
        if not saran:
            m = SARAN_BQ.match(s)
            if m:
                saran_icon = m.group(1)
                saran_label = m.group(2).capitalize()
                inline_body = strip_md_bold(m.group(3)).strip()
                # Collect multi-line saran continuation
                i += 1
                cont_bullets = []
                cont_paras = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    cont = re.sub(r"^>\s*", "", lines[i].strip())
                    cont = strip_md_bold(cont)
                    if re.match(r"^[-*]\s+", cont):
                        cont_bullets.append(re.sub(r"^[-*]\s+", "", cont))
                    elif cont:
                        cont_paras.append(cont)
                    i += 1
                # Build saran: inline body OR first cont paragraph as main; rest as bullets
                if inline_body:
                    saran = inline_body
                    saran_extra_bullets.extend(cont_bullets)
                    saran_extra_bullets.extend(cont_paras)  # rare
                elif cont_paras:
                    saran = cont_paras[0]
                    saran_extra_bullets.extend(cont_paras[1:])
                    saran_extra_bullets.extend(cont_bullets)
                elif cont_bullets:
                    # No body — use bullets directly. Make a generic main
                    saran = "Beberapa hal yang perlu diperhatikan:"
                    saran_extra_bullets.extend(cont_bullets)
                continue
            # Pattern B: inline paragraph-level `**Saran:** body` (MD2/MD3 style)
            m = SARAN_INLINE.match(s)
            if m:
                saran_icon = "💡"
                saran_label = m.group(1).capitalize()
                saran = strip_md_bold(m.group(2)).strip()
                i += 1
                continue
            # Pattern C: standalone `**Peringatan Penting:**` + bullets follow
            m = SARAN_STANDALONE.match(s)
            if m:
                saran_label = m.group(1).capitalize()
                saran_icon = "⚠" if saran_label.lower().startswith(("peringat", "pengingat")) else "💡"
                i += 1
                # Collect following bullet lines + maybe paragraph
                bullets = []
                while i < len(lines):
                    ns = lines[i].strip()
                    if not ns: i += 1; continue
                    if re.match(r"^[-*]\s+", ns):
                        bullets.append(re.sub(r"^[-*]\s+", "", ns))
                        i += 1
                        continue
                    break  # non-bullet ends collection
                if bullets:
                    # First bullet as main, rest as extras
                    saran = strip_md_bold(bullets[0])
                    for b in bullets[1:]:
                        saran_extra_bullets.append(strip_md_bold(b))
                continue
            m = SARAN_BQ_NO_ICON.match(s)
            if m:
                saran_icon = "💡"
                saran_label = m.group(1).capitalize()
                inline_body = strip_md_bold(m.group(2)).strip()
                i += 1
                cont_bullets = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    cont = re.sub(r"^>\s*", "", lines[i].strip())
                    cont = strip_md_bold(cont)
                    if re.match(r"^[-*]\s+", cont):
                        cont_bullets.append(re.sub(r"^[-*]\s+", "", cont))
                    elif cont:
                        cont_bullets.append(cont)  # treat as bullet too
                    i += 1
                saran = inline_body or (cont_bullets[0] if cont_bullets else "")
                if inline_body and cont_bullets:
                    saran_extra_bullets.extend(cont_bullets)
                elif not inline_body and len(cont_bullets) > 1:
                    saran_extra_bullets.extend(cont_bullets[1:])
                continue

        # Transkripsi label
        if TRANSKRIPSI_LBL.match(s):
            in_transkripsi = True
            in_interp = False
            i += 1; continue

        # Interpretasi label
        if INTERP_LBL.match(s):
            in_interp = True
            in_transkripsi = False
            seen_interp_label = True
            i += 1; continue

        # Hanzi blockquotes / non-saran blockquotes → skip
        if s.startswith(">"):
            i += 1; continue

        # Skip ◎/●/○ markers
        if s.startswith(("◎", "●", "○")):
            i += 1; continue

        # Italic meta lines
        m_meta = re.match(r"^\*([^*]+)\*$", s)
        if m_meta:
            meta_text = m_meta.group(1).lower()
            if any(k in meta_text for k in ["cabang", "bintang", "juga merupakan", "shen gong",
                                              "ming gong", "rentang usia", "宮", "star"]):
                i += 1; continue

        # Under transkripsi mode, skip Hanzi
        if in_transkripsi:
            han = sum(1 for c in s if "一" <= c <= "鿿")
            latn = sum(1 for c in s if c.isalpha() and ord(c) < 128)
            if han > 5 and han > latn * 1.5:
                i += 1; continue
            in_transkripsi = False

        # Under interpretasi mode — collect paragraphs AND bullets
        if in_interp or not seen_interp_label:
            han = sum(1 for c in s if "一" <= c <= "鿿")
            latn = sum(1 for c in s if c.isalpha() and ord(c) < 128)
            if han > 5 and han > latn * 1.5:
                i += 1; continue
            # Skip standalone bold-label
            if re.match(r"^\*\*[^*]+\*\*\s*:?\s*$", s):
                i += 1; continue
            # Bullet → preserve with • prefix
            if re.match(r"^[-*]\s+", s):
                content = re.sub(r"^[-*]\s+", "", s)
                interpretasi_buf.append("• " + strip_md_bold(content))
                in_interp = True
                i += 1; continue
            interpretasi_buf.append(strip_md_bold(s))
            in_interp = True
            i += 1; continue

        i += 1

    # Attach saran multi-line bullets (each prefixed with • for template parser)
    if saran and saran_extra_bullets:
        saran = saran + "\n" + "\n".join("• " + b for b in saran_extra_bullets)

    # Join interp_buf — preserve newlines for bullets, space for paragraphs
    interpretasi = "\n".join(interpretasi_buf).strip() or None
    return interpretasi, saran, saran_icon, saran_label


_ISTANA_TOPIC_KW = {
    # Hanzi → canonical istana key
    "命宮": "命宮", "兄弟": "兄弟宮", "夫妻": "夫妻宮", "子女": "子女宮",
    "財帛": "財帛宮", "疾厄": "疾厄宮", "遷移": "遷移宮", "僕役": "僕役宮",
    "官祿": "官祿宮", "田宅": "田宅宮", "福德": "福德宮", "父母": "父母宮",
}


def _detect_istana_h2(section):
    """Check if H2 section title matches an istana. Return (canonical_hz, indo_name) or None.
    Skip non-istana topics like 婚配 (kecocokan shio), 性情 (karakter), etc.
    """
    raw = section.get("raw_title", "") or section.get("title", "")
    upper = raw.upper()
    # Exclude non-istana topics that may contain palace Hanzi
    if any(kw in upper for kw in ["KECOCOKAN", "婚配", "KEPRIBADIAN", "WATAK", "性情",
                                    "BINTANG", "神煞", "TAKDIR", "宿命",
                                    "KARAKTER", "RAMALAN", "SARAN", "RINGKASAN",
                                    "KESIMPULAN", "HIKMAT", "古書", "GAMBARAN"]):
        return None
    for hz_kw, canonical_hz in _ISTANA_TOPIC_KW.items():
        if hz_kw in raw:
            indo = ISTANA_HZ_INDO.get(canonical_hz, canonical_hz)
            return canonical_hz, indo
    return None


def _extract_h3_subsection_content(sub_lines):
    """Walk sub_lines, return interpretasi+saran tuple — same logic as collection sub."""
    return _extract_interpretasi_and_saran(sub_lines)


def _palace_from_h2_section(s):
    """Convert H2 istana BAB (MD2/MD3 style, no parent collection) → Palace."""
    detected = _detect_istana_h2(s)
    if not detected: return None
    nama_hz, nama_id = detected

    # Find meta line in lines
    ganzhi = None; bintang_hz = None; bintang_indo = None
    for line in s.get("lines", [])[:8]:
        if line.strip().startswith("*") and "Bintang" in line:
            ganzhi, bintang_hz, bintang_indo = _parse_meta_line(line)
            break

    # For MD2/MD3, content is split into Transkripsi + Interpretasi sub-H3.
    # Use full lines (deep mode keeps all sub content) for extraction.
    interp, saran, saran_icon, saran_label = _extract_interpretasi_and_saran(s["lines"])

    bintang_list = []
    if bintang_hz:
        bintang_list.append(HzTerm(hz=bintang_hz, indo=bintang_indo or ""))

    return Palace(
        nama_id=nama_id, nama_hz=nama_hz,
        bintang_utama=bintang_list, ganzhi=ganzhi,
        interpretasi=interp, saran=saran, saran_icon=saran_icon,
        saran_label=saran_label,
    )


def extract_istana_details(sections):
    """Extract list of Palace with full details. Two strategies:
       A. MD1-style collection (one H2 with 6+ istana sub-sections)
       B. MD2/MD3-style scattered (4+ individual istana H2 BABs synthesized into collection)
    Returns (list[Palace], collection_section_h2_title) or (None, None).
    Also returns set of H2 titles consumed (so v48.py can skip them from generic).
    """
    # Strategy A: collection
    sec = _find_collection_section(sections)
    if sec:
        palaces = []
        for sub in sec.get("sub", []) or []:
            nama_hz, nama_id = _parse_istana_title(sub.get("raw_title", ""))
            if not nama_hz: continue
            if nama_hz == "婚配": continue

            ganzhi = None; bintang_hz = None; bintang_indo = None
            for line in sub["lines"][:5]:
                if line.strip().startswith("*") and "Bintang" in line:
                    ganzhi, bintang_hz, bintang_indo = _parse_meta_line(line)
                    break

            interp, saran, saran_icon, saran_label = _extract_interpretasi_and_saran(sub["lines"])

            bintang_list = []
            if bintang_hz:
                bintang_list.append(HzTerm(hz=bintang_hz, indo=bintang_indo or ""))

            palaces.append(Palace(
                nama_id=nama_id, nama_hz=nama_hz,
                bintang_utama=bintang_list, ganzhi=ganzhi,
                interpretasi=interp, saran=saran, saran_icon=saran_icon,
                saran_label=saran_label,
            ))
        if palaces:
            return palaces, sec["title"]

    # Strategy B: scattered H2 BABs synthesis (MD2/MD3)
    palaces = []
    for s in sections:
        p = _palace_from_h2_section(s)
        if p and (p.interpretasi or p.saran):
            palaces.append(p)

    if len(palaces) >= 4:
        return palaces, "INTERPRETASI 12 ISTANA (synthesized)"
    return None, None


def get_consumed_h2_titles(sections):
    """Return set of H2 raw_titles that get rendered as istana_detail (so caller skips them)."""
    sec = _find_collection_section(sections)
    if sec:
        # MD1: only the collection H2 itself is consumed
        return {sec.get("raw_title", "")}
    # MD2/MD3 synthesis: each istana H2 BAB is consumed
    consumed = set()
    for s in sections:
        if _detect_istana_h2(s):
            p = _palace_from_h2_section(s)
            if p and (p.interpretasi or p.saran):
                consumed.add(s.get("raw_title", ""))
    return consumed if len(consumed) >= 4 else set()
