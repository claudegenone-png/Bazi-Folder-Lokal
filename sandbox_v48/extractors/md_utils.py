"""Shared MD parsing utilities."""
import re

H_PAT = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def split_sections(md_text):
    """Split MD into [{level, title, lines, raw_title}] respecting H2 boundaries.
    Returns flat list of H2/H3 sections (each section's `lines` ends at next heading)."""
    lines = md_text.split("\n")
    sections = []
    cur = None
    for line in lines:
        m = H_PAT.match(line)
        if m and len(m.group(1)) <= 3:
            if cur:
                sections.append(cur)
            cur = {
                "level": len(m.group(1)),
                "raw_title": m.group(2).strip(),
                "title": clean_heading(m.group(2)),
                "lines": [],
            }
        elif cur is not None:
            cur["lines"].append(line)
    if cur:
        sections.append(cur)
    return sections


def split_sections_deep(md_text):
    """Split MD only at H2 boundaries — each H2 section keeps ALL H3 sub-content.
    Returns: list[{level: 2, title, raw_title, lines, sub: [list of H3 sub-sections]}]."""
    lines = md_text.split("\n")
    sections = []
    cur = None
    cur_sub = None
    for line in lines:
        m = H_PAT.match(line)
        if m:
            level = len(m.group(1))
            if level == 1:
                continue  # H1 (doc title) — skip
            if level == 2:
                # Close current sub + section
                if cur_sub: cur["sub"].append(cur_sub); cur_sub = None
                if cur: sections.append(cur)
                cur = {
                    "level": 2,
                    "raw_title": m.group(2).strip(),
                    "title": clean_heading(m.group(2)),
                    "lines": [],
                    "sub": [],
                }
                continue
            if level == 3 and cur is not None:
                if cur_sub: cur["sub"].append(cur_sub)
                cur_sub = {
                    "level": 3,
                    "raw_title": m.group(2).strip(),
                    "title": clean_heading(m.group(2)),
                    "lines": [],
                }
                continue
        # Content line
        if cur is not None:
            cur["lines"].append(line)
            if cur_sub is not None:
                cur_sub["lines"].append(line)
    if cur_sub and cur:
        cur["sub"].append(cur_sub)
    if cur:
        sections.append(cur)
    return sections


def clean_heading(raw):
    """Strip emoji, BAB/BAGIAN N prefix, sub-numbering — return pure topic title."""
    t = raw
    # Strip leading emoji/symbols (any non-word, non-Hanzi at start)
    t = re.sub(r"^[^\w一-鿿]+\s*", "", t)
    # Strip BAGIAN/BAB/CHAPTER/PART/Section + number (Roman or Arabic)
    t = re.sub(r"^(?:BAGIAN|BAB|CHAPTER|PART|SECTION)\s+([IVXLCDM]+|\d+)\s*[—–\-:.]?\s*", "", t, flags=re.IGNORECASE)
    # Strip "1." / "1.2" / "I." / "A." / "3.1" etc sub-numbering
    t = re.sub(r"^([IVXLCDM]+|\d+(?:\.\d+)?|[A-Z])\s*[.\-—–:]\s*", "", t)
    # Strip trailing emojis/separators
    t = re.sub(r"\s*[^\w\s\(\)一-鿿·\-—–:]+\s*$", "", t)
    return t.strip()


def parse_kv_table(lines, start_idx=0):
    """Parse a markdown pipe table into list of [key, value] pairs.
    Returns rows after the separator row. Skips header row."""
    rows = []
    in_table = False
    for line in lines[start_idx:]:
        if "|" not in line:
            if in_table: break
            continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line):
            in_table = True
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2:
            # Skip header "Keterangan|Data" / "Data|Keterangan"
            if (cells[0].lower() in ("keterangan", "data", "field", "atribut", "key") and
                cells[1].lower() in ("data", "keterangan", "value", "nilai", "isi")):
                continue
            rows.append(cells)
    return rows


def strip_md_bold(s):
    """Remove **bold** markers but keep content."""
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", s)


def split_hz_indo(text):
    """Split a string like '林如意 (Lin Ruyi)' or '女 (Perempuan)' into (hanzi, indo).
    Returns (hanzi_str, indo_str). Either may be empty."""
    if not text:
        return "", ""
    text = strip_md_bold(text).strip()
    # Pattern: "{Hanzi} ({Latin})" or "{Hanzi}/{Latin}"
    m = re.match(r"^([一-鿿\s]+)\s*\(\s*(.+?)\s*\)\s*$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m = re.match(r"^([一-鿿\s]+)\s*[—\-/]\s*(.+?)$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # Pattern: "{Latin} ({Hanzi})"
    m = re.match(r"^([A-Za-z][^()]+?)\s*\(\s*([一-鿿]+)\s*\)\s*$", text)
    if m:
        return m.group(2).strip(), m.group(1).strip()
    # Hanzi only
    if re.match(r"^[一-鿿\s]+$", text):
        return text.strip(), ""
    return "", text


def find_section_by_keyword(sections, keywords, level=2):
    """Find first section whose title matches any keyword (case-insensitive)."""
    for s in sections:
        if s["level"] != level: continue
        title_upper = s["title"].upper()
        for kw in keywords:
            if kw.upper() in title_upper:
                return s
    return None


def find_all_sections_by_keyword(sections, keywords, level=None):
    """Find all sections matching keywords."""
    out = []
    for s in sections:
        if level is not None and s["level"] != level: continue
        title_upper = s["title"].upper()
        for kw in keywords:
            if kw.upper() in title_upper:
                out.append(s); break
    return out
