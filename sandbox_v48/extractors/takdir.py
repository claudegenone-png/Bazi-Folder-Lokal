"""Takdir & Misi Hidup (宿命) extractor — adaptive 2-strategy.

Strategy A: H2 section with topic="takdir" (Li Yuanxiang BAB XVII NASIB UMUM 宿命)
Strategy B: H3 sub-section matching '宿命' / 'Takdir Akhir' inside any H2
            (Lin Ruyi 4.4 【宿命】 inside BAGIAN IV)

Output shape (LifeArea):
  - intro: opening Indo paragraph
  - raw_quotes[0]: Hanzi transcription (Transkripsi Asli)
  - raw_paragraphs: Indo body paragraphs after Interpretasi
  - rekomendasi: "**Kunci nasib...:**" or bold-prefixed callouts
"""
import re
from canonical_model import LifeArea, Bullet
from extractors.md_utils import strip_md_bold
from lookups.topic_taxonomy import detect_topic


HZ_RE = re.compile(r"[一-鿿]")
TAKDIR_H3_RE = re.compile(r"宿命|takdir\s+akhir|nasib\s+akhir|nasib\s+bawaan", re.IGNORECASE)


def _is_hanzi_dominant(text):
    han = sum(1 for c in text if "一" <= c <= "鿿")
    latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return han > 8 and han > latn * 1.2


def _find_h3_block(section):
    """Look in section['sub'] for H3 matching takdir, return its lines."""
    for sub in section.get("sub") or []:
        if TAKDIR_H3_RE.search(sub.get("raw_title", "")) or TAKDIR_H3_RE.search(sub.get("title", "")):
            return sub.get("lines") or []
    return None


def _parse_block(lines):
    """Parse takdir block lines → (transkripsi_hz, intro_indo, paragraphs, kunci_bullets)."""
    transkripsi = None
    intro = None
    paragraphs = []
    kunci = []

    state = "init"  # init / collecting_hz / collecting_indo
    buf = []

    def flush_buf():
        nonlocal buf
        if not buf: return
        text = " ".join(buf).strip()
        buf = []
        if not text: return
        # Classify
        m = re.match(r"\*\*(Kunci [^:*]+|Pesan [^:*]+|Inti [^:*]+):\*\*\s*(.+)", text)
        if m:
            kunci.append(Bullet(label=strip_md_bold(m.group(1)), text=strip_md_bold(m.group(2))))
            return
        if _is_hanzi_dominant(text):
            return  # already captured
        paragraphs.append(strip_md_bold(text))

    for raw in lines:
        s = raw.strip()
        if not s:
            flush_buf()
            continue
        if s == "---":
            flush_buf()
            continue
        if re.match(r"^#+\s", s):
            continue
        # Strip blockquote prefix
        if s.startswith(">"):
            s = re.sub(r"^>\s*", "", s).strip()
        if not s:
            continue
        # Hanzi-dominant transcription line
        if _is_hanzi_dominant(s) and not transkripsi:
            transkripsi = strip_md_bold(s)
            continue
        # Section markers
        low = s.lower()
        if re.match(r"\*\*?(transkripsi|original|asli)", low):
            flush_buf()
            state = "collecting_hz"
            continue
        if re.match(r".*?(interpretasi|✨|🔍|makna)", low) and ("**" in s or s.startswith(("✨", "🔍"))):
            flush_buf()
            state = "collecting_indo"
            continue
        # Strip leading icon
        s_clean = re.sub(r"^[✨🔍🌅⭐•·\-]+\s*", "", s).strip()
        if not s_clean:
            continue
        buf.append(s_clean)

    flush_buf()

    if paragraphs:
        intro = paragraphs[0]
        rest = paragraphs[1:]
    else:
        rest = []

    return transkripsi, intro, rest, kunci


def extract_takdir(sections):
    """Try Strategy A (H2 takdir topic) then Strategy B (H3 inside any H2)."""
    # Strategy A
    for s in sections:
        if detect_topic(s["title"]) == "takdir":
            transkripsi, intro, paragraphs, kunci = _parse_block(s["lines"])
            if intro or transkripsi or paragraphs:
                la = LifeArea()
                la.intro = intro
                la.raw_paragraphs = paragraphs
                la.rekomendasi = kunci
                if transkripsi:
                    la.raw_quotes = [transkripsi]
                return la
            return None

    # Strategy B: scan H3 inside H2
    for s in sections:
        block = _find_h3_block(s)
        if block is None:
            continue
        transkripsi, intro, paragraphs, kunci = _parse_block(block)
        if intro or transkripsi or paragraphs:
            la = LifeArea()
            la.intro = intro
            la.raw_paragraphs = paragraphs
            la.rekomendasi = kunci
            if transkripsi:
                la.raw_quotes = [transkripsi]
            return la

    return None
