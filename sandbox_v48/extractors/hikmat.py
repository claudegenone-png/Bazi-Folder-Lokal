"""Hikmat Klasik (古書云) extractor — adaptive.

Pattern across MDs:
  H2: contains 古書云 / RUJUKAN KLASIK / PUISI RAMALAN KUNO / HIKMAT
  Body:
    - optional disclaimer / catatan line (italic / blockquote)
    - "**Transkripsi:**" or "### Transkripsi Asli" heading
    - Hanzi verse paragraphs — each starts with citation prefix
        (詩曰 / 詩云 / 滴天髓云 / 三命通會註 / 青龍伏形 / 滿天龍 / etc.)
        or is a standalone classical line
    - "**✨ Interpretasi:**" or "### 🔍 Interpretasi" heading
    - Intro paragraph
    - Bullet list of explanations
"""
import re
from canonical_model import HikmatBundle, HikmatVerse
from extractors.md_utils import strip_md_bold
from lookups.topic_taxonomy import detect_topic


CITATION_PATTERNS = [
    (re.compile(r"^三命通會註?[：:]"), "三命通會", "San Ming Tong Hui"),
    (re.compile(r"^滴天髓云?[：:]"), "滴天髓", "Di Tian Sui"),
    (re.compile(r"^青龍伏形[，,]?\s*詩曰[：:]?"), "青龍伏形", "Qing Long Fu Xing"),
    (re.compile(r"^滿天龍[：:]"), "滿天龍", "Man Tian Long"),
    (re.compile(r"^詩曰[：:]"), "詩曰", "Shī Yuē (Pepatah)"),
    (re.compile(r"^詩云[：:]"), "詩云", "Shī Yún (Pepatah)"),
    (re.compile(r"^經云[：:]"), "經云", "Jīng Yún (Kitab)"),
    (re.compile(r"^賦曰[：:]"), "賦曰", "Fù Yuē (Naskah)"),
]


def _is_hanzi_dominant(text):
    han = sum(1 for c in text if "一" <= c <= "鿿")
    latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return han > 5 and han > latn


def _classify_verse(text):
    """Return (sumber, sumber_indo, hanzi_body) tuple."""
    for pat, src, src_indo in CITATION_PATTERNS:
        m = pat.match(text)
        if m:
            body = text[m.end():].strip()
            return src, src_indo, body
    # Standalone classical verse — no explicit citation
    return None, None, text


def _split_verse_segments(line):
    """A single Hanzi line may contain multiple cited verses concatenated.
    Split on citation prefixes when found mid-line.
    """
    # Find all citation match positions
    splits = [0]
    pat_combined = re.compile(
        r"(三命通會註?[：:]|滴天髓云?[：:]|青龍伏形[，,]?\s*詩曰[：:]?|滿天龍[：:]|詩曰[：:]|詩云[：:]|經云[：:]|賦曰[：:])"
    )
    for m in pat_combined.finditer(line):
        if m.start() > splits[-1] + 2:
            splits.append(m.start())
    splits.append(len(line))
    out = []
    for i in range(len(splits) - 1):
        seg = line[splits[i]:splits[i+1]].strip()
        if seg:
            out.append(seg)
    return out


def _strip_quote(text):
    s = re.sub(r"^>\s*", "", text)
    return strip_md_bold(s)


def _is_meta_marker(s):
    low = s.lower()
    return bool(re.search(r"^(transkripsi|original|asli|interpretasi|✨|🔍|makna|ringkasan)\b", low) and ("**" in s or s.startswith(("✨", "🔍", "###"))))


def extract_hikmat(sections):
    target = None
    for s in sections:
        if detect_topic(s["title"]) == "hikmat_klasik":
            target = s
            break
    if target is None:
        return None

    verses = []
    intro_paragraphs = []
    bullets = []
    catatan = None
    state = "init"  # init / hz / indo

    for raw in target["lines"]:
        s = raw.strip()
        if not s or s == "---":
            continue
        if re.match(r"^#+\s", s):
            # Heading line — switch state based on title
            head = re.sub(r"^#+\s+", "", s).lower()
            if "transkripsi" in head or "asli" in head or "kuno" in head:
                state = "hz"
            elif "interpretasi" in head or "ringkasan" in head or "makna" in head:
                state = "indo"
            continue
        # Strip blockquote
        if s.startswith(">"):
            inner = _strip_quote(s)
            # Italic note? store as catatan
            if re.match(r"^\*?\(?(bagian ini|catatan|note)", inner.lower()):
                if not catatan:
                    catatan = re.sub(r"^[*\(]+|[*\)]+$", "", inner).strip()
                continue
            if _is_hanzi_dominant(inner):
                for seg in _split_verse_segments(inner):
                    src, src_indo, body = _classify_verse(seg)
                    verses.append(HikmatVerse(sumber=src, sumber_indo=src_indo, hanzi=body))
                state = "hz"
                continue
            # Else fall through as Indo content
            s = inner
        # State-aware bold-prefixed labels
        if re.match(r"^\*\*(Transkripsi|Original|Asli)", s, re.IGNORECASE):
            state = "hz"
            continue
        if re.match(r"^\*?\*?(✨\s*)?(Interpretasi|Ringkasan|Makna)", s, re.IGNORECASE) and "**" in s:
            state = "indo"
            continue
        # Italic note bracketed
        if re.match(r"^\*\(?(bagian ini|catatan|note)", s.lower()):
            if not catatan:
                catatan = re.sub(r"^[*\(]+|[*\)]+$", "", s).strip()
            continue
        # Bullet
        if re.match(r"^[\-•*]\s+", s):
            text = re.sub(r"^[\-•*]\s+", "", s)
            bullets.append(strip_md_bold(text))
            state = "indo"
            continue
        # Hanzi-dominant standalone line → verse
        if _is_hanzi_dominant(s):
            for seg in _split_verse_segments(s):
                src, src_indo, body = _classify_verse(seg)
                verses.append(HikmatVerse(sumber=src, sumber_indo=src_indo, hanzi=body))
            state = "hz"
            continue
        # Indo paragraph
        if state == "indo" or not _is_hanzi_dominant(s):
            cleaned = strip_md_bold(s)
            if cleaned:
                intro_paragraphs.append(cleaned)

    if not verses and not intro_paragraphs:
        return None

    intro = " ".join(intro_paragraphs).strip() if intro_paragraphs else None
    return HikmatBundle(
        verses=verses,
        synthesis_intro=intro,
        synthesis_bullets=bullets,
        catatan=catatan,
    )
