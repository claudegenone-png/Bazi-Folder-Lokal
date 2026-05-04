"""Karakter extractor — adaptive untuk 3 pola MD berbeda:

  Pola A (Li Yuanxiang): H2 → H3 'Transkripsi Asli' (skip) + H3 'Interpretasi' →
                        body has **Lapisan N — Title:** \\n paragraph (3 lapisan)
  Pola B (Lin Ruyi):    H2 'ANALISIS KARAKTER MENDALAM' → 4 H3 children, only the
                        first '性情 — Kepribadian & Watak' is karakter; others
                        (神煞/全局/宿命) are different topics.
  Pola C (Lin Wen Han): H2 'KARAKTER & SIFAT' (no subs, flat lines) →
                        **Lima Pola Kepribadian:** then 5 ①②③④⑤ numbered patterns
                        with sub-bullets each.

Output: Karakter(intro, kekuatan=List[Bullet]).
  - Each Bullet.label = aspek/lapisan/pola title (e.g. "Lapisan 1 — Jiwa Pragmatis")
  - Each Bullet.text = combined description (paragraph + sub-bullets joined)
  - kelemahan only populated if explicit pos/neg headers are detected
"""
import re
from canonical_model import Karakter, Bullet
from extractors.md_utils import strip_md_bold


KARAKTER_KW = ["KARAKTER", "KEPRIBADIAN", "WATAK", "SIFAT", "性情"]
KARAKTER_SUB_KW = re.compile(r"\b(性情|kepribadian|watak|sifat\s+karakter|karakter\s+&\s+sifat)\b", re.IGNORECASE)
SKIP_SUB_KW = re.compile(r"\b(transkripsi|verbatim|software|raw)\b", re.IGNORECASE)

KEKUATAN_LBL = re.compile(r"\b(kekuatan|sifat\s+positif|kelebihan)\b", re.IGNORECASE)
KELEMAHAN_LBL = re.compile(r"\b(kelemahan|sifat\s+negatif|kekurangan|tantangan|area\s+(?:perlu\s+)?perhatian|hal.*diwaspadai)\b", re.IGNORECASE)

# Lapisan/Pola/Aspek headers — flexible label patterns
# Standalone-line patterns (whole line is label only)
APSEK_HEADER_PATS = [
    re.compile(r"^\*\*\s*(Lapisan\s+[\w\d]+(?:\s*[—–\-]\s*[^*]+|\s*\([^)]+\))?)\s*:?\s*\*\*\s*$", re.IGNORECASE),
    re.compile(r"^\*\*\s*([①-⑩⓪]\s*[^*]+)\s*\*\*(?:\s*\([^)]+\))?\s*$"),  # allow trailing (Indo)
    re.compile(r"^\*\*\s*((?:Aspek|Pola|Pattern|Pilar)\s+[\w\d]+[^*]*)\s*\*\*\s*$", re.IGNORECASE),
    re.compile(r"^\*\*\s*([^*]+?)\s*\*\*\s*$"),
]

# Inline-label patterns (label + body on SAME line: "**Lapisan Pertama (X):** body...")
APSEK_INLINE_PATS = [
    # **Lapisan {ord} ({Title}):** {body}
    re.compile(r"^\*\*\s*(Lapisan\s+[\w\d]+(?:\s*[—–\-]\s*[^*]+|\s*\([^)]+\))?)\s*:?\s*\*\*\s*[:]?\s*(.+)$", re.IGNORECASE),
    # **Aspek/Pola N — Title:** body
    re.compile(r"^\*\*\s*((?:Aspek|Pola|Pattern|Pilar)\s+[\w\d]+(?:\s*[—–\-]\s*[^*]+|\s*\([^)]+\))?)\s*:?\s*\*\*\s*[:]?\s*(.+)$", re.IGNORECASE),
]


def _is_predominantly_hanzi(text):
    if not text: return False
    han = sum(1 for c in text if "一" <= c <= "鿿")
    latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return han > 4 and han > latn * 1.5


# Headers that are SECTION-HEADERS for the interpretasi block (not aspek cards).
# These should switch context to "intro mode" — collect body until a real Lapisan begins.
SECTION_HEADER_LBL = re.compile(
    r"^\W*\s*("
    r"interpretasi|tafsir|penjelasan|gambaran\s+umum|"
    r"(?:tiga|empat|lima|enam|tujuh|\d+)\s+(?:pola|lapisan|aspek|sifat)\s+(?:kepribadian|karakter|sifat|utama)?"
    r")\b",
    re.IGNORECASE,
)


def _match_aspek_header(line):
    """Returns (label, inline_body_or_None) or special marker.
    Returns 'INTRO_HEADER' string sentinel if line is a section-header for intro."""
    s = line.strip()
    # Try inline patterns first (label + body on same line)
    for pat in APSEK_INLINE_PATS:
        m = pat.match(s)
        if m:
            label = m.group(1).strip()
            body = m.group(2).strip()
            if KEKUATAN_LBL.search(label) or KELEMAHAN_LBL.search(label): return None
            if SKIP_SUB_KW.search(label): return None
            if SECTION_HEADER_LBL.search(label): return ("__INTRO__", body)  # promote body to intro
            return (label, body)
    # Standalone label patterns
    for pat in APSEK_HEADER_PATS:
        m = pat.match(s)
        if m:
            label = m.group(1).strip()
            if KEKUATAN_LBL.search(label) or KELEMAHAN_LBL.search(label): return None
            if SKIP_SUB_KW.search(label): return None
            # Section-header labels (Interpretasi, Lima Pola, dst) → switch to intro mode
            if SECTION_HEADER_LBL.search(label):
                return ("__INTRO__", None)
            # For ①Hanzi pattern, extract trailing (Indo) from raw line if present
            indo_m = re.search(r"\*\*\s*\(([^)]+)\)\s*$", s)
            if indo_m and re.match(r"^[①-⑩⓪]", label):
                label = f"{label} ({indo_m.group(1).strip()})"
            return (label, None)
    return None


def _parse_lapisan_block(lines):
    """Walk lines, group by lapisan/pola/aspek headers.
    Returns (intro_text, list_of_(label, text)).
    Skips predominantly-Hanzi paragraphs (raw transkripsi).
    """
    intro_paras = []
    aspeks = []           # list of (label, paragraphs, sub_bullets)
    cur_label = None
    cur_paras = []
    cur_bullets = []

    def flush_aspek():
        nonlocal cur_label, cur_paras, cur_bullets
        if cur_label is not None:
            text_parts = []
            if cur_paras:
                text_parts.append(" ".join(cur_paras).strip())
            if cur_bullets:
                text_parts.append("\n".join(f"• {b}" for b in cur_bullets))
            aspeks.append((cur_label, "\n".join(t for t in text_parts if t)))
        cur_label = None
        cur_paras = []
        cur_bullets = []

    for raw in lines:
        s = raw.strip()
        if not s: continue
        if s == "---": continue
        # Skip blockquote (often raw verses)
        if s.startswith(">"):
            continue
        # Skip Hanzi-prefix raw transkripsi paragraphs
        if s.startswith("◎") or _is_predominantly_hanzi(s):
            continue

        # Aspek/Lapisan header (returns (label, body) or ("__INTRO__", body) for section-headers)
        match = _match_aspek_header(raw)
        if match:
            label, inline_body = match
            if label == "__INTRO__":
                # Switch context to intro mode — flush current aspek, no new label
                flush_aspek()
                cur_label = None
                if inline_body:
                    intro_paras.append(strip_md_bold(inline_body))
                continue
            flush_aspek()
            cur_label = label
            if inline_body:
                cur_paras.append(strip_md_bold(inline_body))
            continue
        # Standalone **bold** line that didn't match → skip (likely meta header that got filtered)
        if re.match(r"^\*\*[^*]+\*\*\s*:?\s*$", s):
            continue

        # Bullet
        m_b = re.match(r"^[-*]\s+(.+)$", s)
        if m_b:
            content = m_b.group(1).strip()
            content = strip_md_bold(content)
            if cur_label is None:
                # Bullet without aspek context → treat as standalone aspek (label-text format if has label)
                # Try parse "Label: Description"
                m_lbl = re.match(r"^([^:]{2,40}):\s*(.+)$", content)
                if m_lbl and not _is_predominantly_hanzi(m_lbl.group(1)):
                    aspeks.append((m_lbl.group(1).strip(), m_lbl.group(2).strip()))
                else:
                    aspeks.append((None, content))
            else:
                cur_bullets.append(content)
            continue

        # Paragraph
        clean = strip_md_bold(s)
        if cur_label is not None:
            cur_paras.append(clean)
        else:
            intro_paras.append(clean)

    flush_aspek()

    intro = " ".join(intro_paras) if intro_paras else None
    return intro, aspeks


def _pick_karakter_content(section):
    """Given an H2 section (deep or flat), return the lines that contain
    actual karakter content (skip Transkripsi/non-karakter sub-sections)."""
    subs = section.get("sub", []) or []
    if subs:
        # Prefer sub matching karakter keywords
        primary = None
        for sub in subs:
            if SKIP_SUB_KW.search(sub.get("title", "")):
                continue
            if KARAKTER_SUB_KW.search(sub.get("title", "")):
                primary = sub; break
        if primary is None:
            # Fallback: first non-skip sub
            for sub in subs:
                if not SKIP_SUB_KW.search(sub.get("title", "")):
                    primary = sub; break
        if primary is None:
            primary = subs[0]
        # Within primary, drop any "Transkripsi" content (already happens in parse via Hanzi filter
        # since primary doesn't have its own subs — its lines are flat)
        return primary["lines"]
    # Flat
    return section["lines"]


def extract_karakter(sections):
    # Pick best karakter H2 section
    candidates = []
    for s in sections:
        t = s["title"].upper()
        if any(k in t for k in KARAKTER_KW):
            # score: total non-empty lines (deeper sections preferred for parent-style structure)
            n = sum(1 for ln in s.get("lines", []) if ln.strip())
            candidates.append((n, s))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    sec = candidates[0][1]

    lines = _pick_karakter_content(sec)
    intro, aspeks = _parse_lapisan_block(lines)

    if not (intro or aspeks):
        return None

    # Convert aspeks into Bullets. All go to kekuatan (these are
    # personality aspects/layers, not pos/neg traits).
    kek_bullets = [Bullet(label=lbl, text=txt) for (lbl, txt) in aspeks]

    return Karakter(intro=intro, kekuatan=kek_bullets, kelemahan=[])
