"""Ringkasan page — Profil hero + Kekuatan/Tantangan visual + Saran grid + Kalender timeline.

Auto-paginate: 1-3 halaman tergantung kepadatan konten.
Visual-led: 70% visualisasi (icon cards, chip grid, year timeline) / 30% teks.
"""
import html as _html
import re
from templates.page_shell import page_shell
from templates.primitives import card, callout, section_h2, gloss_text
from canonical_model import Ringkasan


def _esc(s):
    return _html.escape(s or "", quote=False)


# Icon mapping for saran bidang — Indonesian-friendly emoji
BIDANG_ICONS = [
    (re.compile(r"karir|karier|bisnis|wirausaha|profesi|pekerjaan", re.I), "💼"),
    (re.compile(r"keuangan|finansial|uang|investasi|properti", re.I),     "💰"),
    (re.compile(r"asmara|cinta|hubungan|jodoh|pasangan|pernikahan", re.I), "💕"),
    (re.compile(r"rumah|feng\s*shui|tempat\s+tinggal", re.I),              "🏠"),
    (re.compile(r"kesehatan|fisik|tubuh|olahraga", re.I),                  "🏥"),
    (re.compile(r"kalender|tahun|waktu", re.I),                            "📅"),
    (re.compile(r"warna", re.I),                                           "🎨"),
    (re.compile(r"angka", re.I),                                           "🔢"),
    (re.compile(r"arah", re.I),                                            "🧭"),
    (re.compile(r"keluarga|orang\s*tua|saudara|anak", re.I),               "👨‍👩‍👧"),
    (re.compile(r"siklus|periode|usia|fase", re.I),                        "🌊"),
    (re.compile(r"spiritual|batin|mental|jiwa", re.I),                     "✨"),
    (re.compile(r"pendidikan|belajar|ilmu|keahlian", re.I),                "📚"),
]
DEFAULT_ICON = "❖"


def _icon_for(bidang):
    if not bidang: return DEFAULT_ICON
    for pat, ic in BIDANG_ICONS:
        if pat.search(bidang):
            return ic
    return DEFAULT_ICON


def _clean_bidang_label(s):
    if not s: return ""
    s = re.sub(r"^[\W_\s]+", "", s)              # leading emoji/symbols
    s = re.sub(r":\s*$", "", s)                  # trailing colon
    s = re.sub(r"\s*:\s*$", "", s)
    return s.strip()


# Saran type classification.
# BIDANG_HEAD: cleaned-key MUST START with a bidang keyword (not just contain it).
# This prevents thematic titles like "Pilih Pasangan dengan Bijak" from being
# misclassified as a bidang card.
BIDANG_HEAD = re.compile(
    r"^(saran\s+)?(karir|karier|bisnis|wirausaha|profesi|pekerjaan|"
    r"keuangan|finansial|uang|investasi|"
    r"asmara|cinta|hubungan|jodoh|pernikahan|"
    r"rumah|feng\s*shui|tempat\s+tinggal|properti|"
    r"kesehatan|fisik|tubuh|"
    r"kalender|tahun|warna|angka|arah|"
    r"keluarga|spiritual|batin|mental|jiwa|pendidikan|umum)\b",
    re.IGNORECASE,
)
# Periode pattern: "Siklus 甲申" / "Periode 1" / ganzhi alone / age-range value
GANZHI_PAT = re.compile(r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]")
PERIODE_KEY_PAT = re.compile(r"^(?:siklus|periode|fase)\b", re.IGNORECASE)
AGE_RANGE_PAT = re.compile(r"\b\d{2}\s*[-–—]\s*\d{2}\b")


def _classify_saran_type(kv):
    key = kv.key or ""
    val = kv.value or ""
    # Periode: explicit "Siklus" prefix OR ganzhi in key OR age-range value
    if PERIODE_KEY_PAT.search(key) or GANZHI_PAT.search(key) or (
        GANZHI_PAT.search(val[:30]) and AGE_RANGE_PAT.search(val[:30])
    ):
        return "periode"
    # Bidang: short key starting with bidang keyword OR emoji-prefix
    has_emoji = bool(re.match(r"^[^\w\sA-Za-z]", key.strip()))
    cleaned = _clean_bidang_label(key)
    if has_emoji:
        return "bidang"
    if BIDANG_HEAD.match(cleaned) and len(cleaned) <= 35:
        return "bidang"
    # Tematik: anything else (long thematic title like "Pilih Pasangan dengan Bijak")
    return "tematik"


def _normalize_saran(saran_items):
    """Merge consecutive same-key entries into one (bullets joined),
    then classify into bidang / tematik / periode buckets.
    """
    if not saran_items: return [], [], []
    # Step 1: merge same-key consecutive
    merged = []
    for kv in saran_items:
        if merged and _clean_bidang_label(merged[-1].key) == _clean_bidang_label(kv.key):
            prev = merged[-1]
            joined = (prev.value or "").rstrip()
            new_val = (kv.value or "").lstrip()
            if joined and new_val:
                # Normalize: ensure each line treated as bullet
                p_lines = [l.strip().lstrip("•").lstrip("-").strip() for l in joined.split("\n") if l.strip()]
                n_lines = [l.strip().lstrip("•").lstrip("-").strip() for l in new_val.split("\n") if l.strip()]
                merged[-1] = type(kv)(key=prev.key, value="\n".join(p_lines + n_lines))
            else:
                merged[-1] = type(kv)(key=prev.key, value=joined or new_val)
        else:
            merged.append(kv)
    # Step 2: classify
    bidang, tematik, periode = [], [], []
    for kv in merged:
        t = _classify_saran_type(kv)
        if t == "bidang": bidang.append(kv)
        elif t == "periode": periode.append(kv)
        else: tematik.append(kv)
    return bidang, tematik, periode


# ─────────────────────────────────────────────────────────────────────────
# Profil hero
# ─────────────────────────────────────────────────────────────────────────

SUBJECT_PROFIL_OVERRIDE = {
    "Li Yuan Xiang":
        "Lin Wen Xiang adalah pribadi jujur, mandiri, dan mudah dipercaya, "
        "namun cenderung memendam perasaan dan rezeki tidak datang mudah "
        "sehingga disarankan menyimpan uang dalam bentuk aset nyata. "
        "Karier terbaiknya ada di bidang yang memberi kebebasan tinggi seperti "
        "konsultan, seni, atau pekerjaan dengan mobilitas. "
        "Ke depannya, 2026–2028 cukup positif dengan bantuan dari orang sekitar "
        "dan peluang yang terbuka, namun 2029 menjadi tahun paling berat — "
        "penuh ketidakstabilan dan perlu ekstra hati-hati dalam setiap keputusan besar.",
}


def _hero_profil_html(profil_text, subject_name):
    # Per-subject hardcoded profil override (user-requested)
    if subject_name in SUBJECT_PROFIL_OVERRIDE:
        profil_text = SUBJECT_PROFIL_OVERRIDE[subject_name]
    text = (profil_text or "").strip()
    # Strip leading meta-prefixes left by extractor (loop until none match):
    # "Pola Hubungan...:", "Interpretasi:", "💡 Interpretasi:", "✨ Interpretasi:",
    # "Gambaran besar kehidupan X:", "Catatan:", etc.
    PREFIX_PAT = re.compile(
        r"^[\W_\s]*(?:"
        r"pola\s+[^:]+?:|"
        r"interpretasi[^:]*:|"
        r"gambaran\s+[^:]+?:|"
        r"catatan[^:]*:|"
        r"ringkasan\s+[^:]+?:"
        r")\s*",
        re.IGNORECASE,
    )
    while True:
        new_text = PREFIX_PAT.sub("", text, count=1)
        if new_text == text: break
        text = new_text
    if not text:
        return ""
    name = _esc(subject_name or "Anda")

    # Always render as a single narrative paragraph (bullets folded into prose).
    # Reference style: Lin Ruyi paragraph (flowing sentences, italic-friendly,
    # centered max-width). For MD containing bullet markers (Li Yuanxiang style),
    # convert each bullet to a sentence and join with intro.
    narrative = _to_narrative_paragraph(text)
    if not narrative:
        return ""
    body_html = gloss_text(narrative)

    return f'''<div class="rk-hero">
  <div class="rk-hero-orn-l">❝</div>
  <div class="rk-hero-orn-r">❞</div>
  <div class="rk-hero-eyebrow">KESIMPULAN · 結 語</div>
  <div class="rk-hero-name">{name}</div>
  <div class="rk-hero-text">{body_html}</div>
  <div class="rk-hero-foot">— Distilasi keseluruhan ramalan —</div>
</div>'''


def _to_narrative_paragraph(text):
    """Adaptive: convert mixed intro+bullets MD content into a single flowing
    narrative paragraph. Joins each bullet as a sentence (with period if missing).
    If MD already a paragraph (no bullet markers), returns it cleaned.
    """
    if not text: return ""
    s = text.strip()

    # Detect bullets — either inline " - " markers OR explicit newline bullets
    has_inline_bullets = bool(re.search(r"\s+[-•]\s+", s))
    has_nl_bullets = "\n" in s and any(
        re.match(r"^[-•]\s+", l.strip()) for l in s.split("\n")
    )

    if not (has_inline_bullets or has_nl_bullets):
        # Plain paragraph — collapse any internal newlines into spaces
        return re.sub(r"\s*\n+\s*", " ", s).strip()

    # Has bullets → split + recombine as narrative
    parts = []
    if has_nl_bullets:
        intro_lines = []
        for ln in s.split("\n"):
            ls = ln.strip()
            if not ls: continue
            mb = re.match(r"^[-•]\s+(.+)$", ls)
            if mb:
                parts.append(mb.group(1).strip())
            else:
                if not parts:                   # before any bullet → intro
                    intro_lines.append(ls)
                else:                            # after bullets → trailing prose
                    parts.append(ls)
        intro_text = " ".join(intro_lines).strip()
    else:
        # Inline " - " markers
        m = re.search(r"\s+[-•]\s+", s)
        intro_text = s[:m.start()].strip()
        rest = s[m.start():]
        for p in re.split(r"\s+[-•]\s+", rest):
            p = p.strip()
            if p: parts.append(p)

    # Strip "Label:" prefix from each bullet item — fold label into sentence
    cleaned = []
    for p in parts:
        ml = re.match(r"^([^:]{2,40}):\s*(.+)$", p)
        if ml and not _is_predominantly_hanzi(ml.group(1)):
            cleaned.append(f"{ml.group(2).strip()} (terkait {ml.group(1).strip().lower()})")
        else:
            cleaned.append(p)

    # Build narrative: intro + ". " + each sentence with proper terminator
    def end_punct(t):
        return t if re.search(r"[.!?]$", t) else t + "."

    sentences = []
    if intro_text:
        # Intro often ends with ":" — change to "."
        intro_text = re.sub(r":\s*$", "", intro_text)
        sentences.append(end_punct(intro_text))
    for c in cleaned:
        sentences.append(end_punct(c))

    return " ".join(sentences)


def _split_intro_and_bullets(text):
    """Adaptive parser: split a 'kesimpulan' text into (intro_paragraph, [(label, text), ...]).
    Handles three patterns we see in MD:
      (1) "Intro: - bullet 1 - bullet 2 ..."  (dash markers in single line, Li Yuanxiang)
      (2) "Intro:\\n- bullet 1\\n- bullet 2"  (real newlines)
      (3) "Intro paragraph. Label: text. Label2: text2..." (colon-key inline)
      (4) Plain paragraph (no bullets)
    Returns (intro_str, bullets_list). Either may be empty.
    """
    if not text: return "", []
    s = text.strip()

    # Pattern: contains " - " markers → split intro + bullets
    # Look for first " - " position (dash bullet marker, with surrounding spaces)
    m = re.search(r"\s+[-•]\s+", s)
    if m:
        intro = s[:m.start()].strip().rstrip(":").strip()
        rest = s[m.start():]
        # Split into bullet items
        parts = re.split(r"\s+[-•]\s+", rest)
        parts = [p.strip() for p in parts if p.strip()]
        bullets = []
        for p in parts:
            # Try "Label: text"
            m2 = re.match(r"^([^:]{2,40}):\s*(.+)$", p)
            if m2 and not _is_predominantly_hanzi(m2.group(1)):
                bullets.append((m2.group(1).strip(), m2.group(2).strip()))
            else:
                bullets.append((None, p))
        return intro, bullets

    # Pattern: real newlines with bullets
    if "\n" in s:
        lines = [l.strip() for l in s.split("\n") if l.strip()]
        intro_lines = []
        bullets = []
        in_bullets = False
        for ln in lines:
            mb = re.match(r"^[-•]\s+(.+)$", ln)
            if mb:
                in_bullets = True
                content = mb.group(1).strip()
                m2 = re.match(r"^([^:]{2,40}):\s*(.+)$", content)
                if m2 and not _is_predominantly_hanzi(m2.group(1)):
                    bullets.append((m2.group(1).strip(), m2.group(2).strip()))
                else:
                    bullets.append((None, content))
            elif not in_bullets:
                intro_lines.append(ln)
        intro = " ".join(intro_lines).rstrip(":").strip()
        if bullets:
            return intro, bullets

    # Plain paragraph
    return s, []


def _is_predominantly_hanzi(text):
    if not text: return False
    han = sum(1 for c in text if "一" <= c <= "鿿")
    latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return han > 0 and han > latn * 1.5


# ─────────────────────────────────────────────────────────────────────────
# Kekuatan / Tantangan visual chips
# ─────────────────────────────────────────────────────────────────────────

def _trait_card_html(b, mood):
    label = (b.label or "").strip()
    text = (b.text or "").strip()
    icon = "✓" if mood == "good" else "!"
    if label and text:
        body = f'<div class="rk-tc-label">{_esc(label)}</div><div class="rk-tc-text">{gloss_text(text)}</div>'
    elif label:
        body = f'<div class="rk-tc-label">{_esc(label)}</div>'
    else:
        body = f'<div class="rk-tc-text">{gloss_text(text)}</div>'
    return f'<div class="rk-tc mood-{mood}"><div class="rk-tc-icon">{icon}</div><div class="rk-tc-body">{body}</div></div>'


def _trait_grid_html(items, mood):
    if not items: return ""
    cards = "".join(_trait_card_html(b, mood) for b in items)
    return f'<div class="rk-tc-grid">{cards}</div>'


# ─────────────────────────────────────────────────────────────────────────
# Saran bidang grid
# ─────────────────────────────────────────────────────────────────────────

def _saran_card_html(kv):
    bidang = _clean_bidang_label(kv.key)
    icon = _icon_for(bidang)
    val = (kv.value or "").strip()
    # Detect multi-line value with bullet markers (• or leading dash)
    parts = re.split(r"\n+", val)
    bullets = []
    for p in parts:
        p = p.strip().lstrip("•").lstrip("-").strip()
        if p: bullets.append(p)
    if len(bullets) > 1:
        body = '<ul class="rk-saran-bullets">' + "".join(f"<li>{gloss_text(b)}</li>" for b in bullets) + '</ul>'
    else:
        body = f'<div class="rk-saran-text">{gloss_text(bullets[0] if bullets else val)}</div>'
    return f'''<div class="rk-saran-card">
  <div class="rk-saran-head">
    <span class="rk-saran-icon">{icon}</span>
    <span class="rk-saran-bidang">{_esc(bidang)}</span>
  </div>
  {body}
</div>'''


def _saran_grid_html(items, columns=2):
    if not items: return ""
    cards = "".join(_saran_card_html(kv) for kv in items)
    return f'<div class="rk-saran-grid cols-{columns}">{cards}</div>'


# ─────────────────────────────────────────────────────────────────────────
# Saran tematik (longer-form advice cards, full-width)
# ─────────────────────────────────────────────────────────────────────────

# Auto-icon for tematik based on key keywords
TEMATIK_ICONS = [
    (re.compile(r"pasangan|jodoh|pernikahan|hubungan|asmara|cinta", re.I), "💕"),
    (re.compile(r"keahlian|fokus|investasikan", re.I), "🎯"),
    (re.compile(r"properti|rumah|aset|kekayaan", re.I), "🏠"),
    (re.compile(r"karir|wirausaha|profesi|tampil|peran", re.I), "💼"),
    (re.compile(r"kesehatan|jaga|tubuh|pencernaan|pernapasan", re.I), "🏥"),
    (re.compile(r"keuangan|uang|properti", re.I), "💰"),
]


def _tematik_icon(key):
    for pat, ic in TEMATIK_ICONS:
        if pat.search(key or ""): return ic
    return "✦"


def _tematik_card_html(kv, idx):
    key = (kv.key or "").strip()
    val = (kv.value or "").strip()
    ic = _tematik_icon(key)
    # For tematik, the value is typically a paragraph (no bullet split)
    text_html = gloss_text(val)
    return f'''<div class="rk-tematik-card">
  <div class="rk-tematik-num">{idx:02d}</div>
  <div class="rk-tematik-body">
    <div class="rk-tematik-head">
      <span class="rk-tematik-icon">{ic}</span>
      <span class="rk-tematik-title">{_esc(key)}</span>
    </div>
    <div class="rk-tematik-text">{text_html}</div>
  </div>
</div>'''


def _tematik_list_html(items):
    if not items: return ""
    cards = "".join(_tematik_card_html(kv, i+1) for i, kv in enumerate(items))
    return f'<div class="rk-tematik-stack">{cards}</div>'


# ─────────────────────────────────────────────────────────────────────────
# Periode timeline — horizontal life-cycle visualization
# ─────────────────────────────────────────────────────────────────────────

def _periode_node_html(kv):
    key = (kv.key or "").strip()  # e.g. "Siklus 甲申"
    val = (kv.value or "").strip()
    # Try to split value into "23-32 — Description"
    m = re.match(r"^\s*(\d{2}\s*[-–—]\s*\d{2})\s*[-–—]\s*(.+)$", val)
    age_html = ""
    desc = val
    if m:
        age_html = f'<div class="rk-pd-age">{_esc(m.group(1))}</div>'
        desc = m.group(2).strip()
    # Hanzi gloss for ganzhi in key
    key_html = gloss_text(key)
    return f'''<div class="rk-pd-node">
  <div class="rk-pd-key">{key_html}</div>
  {age_html}
  <div class="rk-pd-dot">●</div>
  <div class="rk-pd-text">{gloss_text(desc)}</div>
</div>'''


def _periode_timeline_html(items):
    if not items: return ""
    nodes = "".join(_periode_node_html(kv) for kv in items)
    return f'''<div class="rk-pd-wrap">
  <div class="rk-pd-head">
    <span class="rk-pd-head-icon">🌊</span>
    <span class="rk-pd-head-id">Perkiraan Nasib per Periode</span>
    <span class="rk-pd-head-hz">大 運</span>
  </div>
  <div class="rk-pd-line"></div>
  <div class="rk-pd-track">{nodes}</div>
</div>'''


# ─────────────────────────────────────────────────────────────────────────
# Kalender Waspada — horizontal year timeline
# ─────────────────────────────────────────────────────────────────────────

YEAR_PAT = re.compile(r"^(?:\*\*)?(\d{4})(?:\*\*)?\s*[:：]\s*(.+)$")


def _parse_kalender(text):
    """Return list of (year, mood, text) tuples. mood: warn|info."""
    if not text: return []
    out = []
    for line in text.split("\n"):
        s = line.strip().lstrip("•").lstrip("-").strip()
        if not s: continue
        m = YEAR_PAT.match(s)
        if m:
            year = int(m.group(1))
            txt = m.group(2).strip()
            mood = "warn" if re.search(r"waspada|jaga|hindari|kurangi|prioritas|hati|ekstra", txt, re.I) else "info"
            out.append((year, mood, txt))
    return out


def _kalender_timeline_html(text):
    items = _parse_kalender(text)
    if not items:
        # Fallback to plain card
        if not text: return ""
        return card(
            body=f'<div class="rk-cal-fallback">{gloss_text(text)}</div>',
            variant='warn', icon='📅', title='Kalender Waspada', hz='注 意 月 份',
        )
    nodes = "".join(
        f'<div class="rk-cal-node mood-{mood}"><div class="rk-cal-year">{y}</div>'
        f'<div class="rk-cal-dot">●</div>'
        f'<div class="rk-cal-text">{gloss_text(t)}</div></div>'
        for (y, mood, t) in items
    )
    return f'''<div class="rk-cal-wrap">
  <div class="rk-cal-head">
    <span class="rk-cal-head-icon">📅</span>
    <span class="rk-cal-head-id">Kalender Tahun Penting</span>
    <span class="rk-cal-head-hz">注 意 年 份</span>
  </div>
  <div class="rk-cal-line"></div>
  <div class="rk-cal-track">{nodes}</div>
</div>'''


# ─────────────────────────────────────────────────────────────────────────
# Page render — auto-paginate
# ─────────────────────────────────────────────────────────────────────────

SECTION_LABEL = "RINGKASAN · 總評"


def render_ringkasan_pages(start_num: int, ringkasan: Ringkasan, subject_name: str = ""):
    """Auto-paginate: 1-3 halaman.
       Page A: Profil hero + Kekuatan + Tantangan
       Page B: Saran bidang grid
       Page C (optional): Kalender timeline (kalau saran sudah penuh)
    """
    if not ringkasan or not (ringkasan.profil or ringkasan.kekuatan or ringkasan.kelemahan
                             or ringkasan.saran_per_bidang or ringkasan.kalender_waspada):
        body = callout("Data ringkasan tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        html = page_shell(start_num, "Kesimpulan & Saran Praktis", "綜 合 總 評",
                          SECTION_LABEL, body, subject_name)
        return [html], start_num + 1

    # ─── Build all content blocks first, then pack into pages by density ───
    # Page A blocks: hero + kekuatan + kelemahan
    blocks_a = []  # primary blocks (hero, traits)
    if ringkasan.profil:
        blocks_a.append(("hero", _hero_profil_html(ringkasan.profil, subject_name)))
    if ringkasan.kekuatan:
        blocks_a.append((
            "kekuatan",
            section_h2("Kekuatan Diri", "優 勢") + _trait_grid_html(ringkasan.kekuatan, "good")
        ))
    if ringkasan.kelemahan:
        blocks_a.append((
            "kelemahan",
            section_h2("Hal Yang Perlu Diperhatikan", "需 注 意") + _trait_grid_html(ringkasan.kelemahan, "warn")
        ))

    # ─── Saran content classification ───
    bidang, tematik, periode = _normalize_saran(ringkasan.saran_per_bidang or [])
    has_cal = bool(ringkasan.kalender_waspada)

    intro_callout = callout(
        "Distilasi seluruh laporan ke saran-saran konkret. Pilih yang paling relevan dengan situasi Anda saat ini.",
        variant="info", icon="💡",
    )

    blocks_b = []  # saran blocks
    if bidang:
        blocks_b.append((
            "bidang",
            section_h2("Saran Praktis per Bidang", "建 議") + _saran_grid_html(bidang, columns=2)
        ))
    if tematik:
        blocks_b.append((
            "tematik",
            section_h2("Saran Holistik", "全 局 建 議") + _tematik_list_html(tematik)
        ))
    if periode:
        blocks_b.append((
            "periode",
            section_h2("Perkiraan Nasib per Periode", "大 運") + _periode_timeline_html(periode)
        ))
    if has_cal:
        blocks_b.append((
            "kalender",
            section_h2("Kalender Tahun Penting", "注 意 年 份") + _kalender_timeline_html(ringkasan.kalender_waspada)
        ))

    if not (blocks_a or blocks_b):
        return [], start_num

    # ─── Pack blocks into pages with character budget per page ───
    BUDGET = 5400          # chars/page (leaves room for header/footer)
    HERO_BUDGET_BIAS = -800  # hero content visually denser; reduce remaining budget
    pages_blocks = [[]]   # list of page-block-lists
    cur_len = 0
    intro_used = False

    def page_budget(blocks_in_page):
        b = BUDGET
        if any(t == "hero" for t, _ in blocks_in_page):
            b += HERO_BUDGET_BIAS
        return b

    # Pass 1: place primary blocks (hero + trait grids); never overflow.
    for tag, html in blocks_a:
        bl = len(html)
        if pages_blocks[-1] and cur_len + bl > page_budget(pages_blocks[-1]):
            pages_blocks.append([]); cur_len = 0
        pages_blocks[-1].append((tag, html))
        cur_len += bl

    # Pass 2: place saran blocks. Prefix intro callout when transitioning into saran.
    for tag, html in blocks_b:
        # Try to fit into current page
        bl = len(html)
        intro_extra = 0 if intro_used else len(intro_callout)
        if pages_blocks[-1] and cur_len + bl + intro_extra > page_budget(pages_blocks[-1]):
            pages_blocks.append([]); cur_len = 0
            # intro_used stays as-is; we'll re-add intro on the new page if not yet shown
        if not intro_used:
            pages_blocks[-1].append(("intro", intro_callout))
            cur_len += len(intro_callout)
            intro_used = True
        pages_blocks[-1].append((tag, html))
        cur_len += bl

    # ─── Render pages — title pinned to "Kesimpulan & Saran Praktis" / "(lanjutan)" ───
    pages = []
    for idx, blocks in enumerate(pages_blocks):
        if not blocks: continue
        title_id = "Kesimpulan & Saran Praktis" if idx == 0 else "Kesimpulan & Saran Praktis (lanjutan)"
        title_hz = "綜 合 總 評"
        body = "\n".join(html for _, html in blocks)
        pages.append(page_shell(
            start_num + len(pages),
            title_id, title_hz, SECTION_LABEL, body, subject_name,
        ))

    return pages, start_num + len(pages)


# ─────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────

RINGKASAN_PAGE_CSS = """
/* === RINGKASAN PAGE === */

/* --- Hero profil --- */
.rk-hero {
  position: relative;
  margin: 0 0 var(--sp-3) 0;
  padding: var(--sp-4) var(--sp-5) var(--sp-3) var(--sp-5);
  background: linear-gradient(135deg, #FBF7F0 0%, #F4E8CC 100%);
  border: var(--bw-thin) solid var(--color-gold);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-soft);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  text-align: center;
}
.rk-hero-orn-l, .rk-hero-orn-r {
  position: absolute; font-family: var(--font-display); font-size: 36pt;
  color: var(--color-gold); line-height: 1; opacity: 0.55;
}
.rk-hero-orn-l { top: 1mm; left: 3mm; }
.rk-hero-orn-r { bottom: -2mm; right: 3mm; }
.rk-hero-eyebrow {
  font-family: var(--font-display); font-size: 8pt; letter-spacing: 4px;
  color: var(--color-gold-deep); font-weight: 700; text-transform: uppercase;
  margin-bottom: var(--sp-1);
}
.rk-hero-name {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 1px; margin-bottom: var(--sp-2);
}
.rk-hero-text {
  font-size: 9.5pt; line-height: 1.7; color: var(--color-ink);
  text-align: justify; text-justify: inter-word;
  max-width: 145mm; margin: 0 auto;
}
.rk-hero-text strong { color: var(--color-red); font-weight: 600; }

.rk-hero-intro {
  font-size: 9.5pt; line-height: 1.65; color: var(--color-ink);
  font-style: italic;
  max-width: 150mm; margin: 0 auto var(--sp-2) auto;
  text-align: center;
}
.rk-hero-intro strong { color: var(--color-red); font-weight: 600; font-style: normal; }
.rk-hero-bullets {
  list-style: none; margin: 0 auto var(--sp-1) auto; padding: 0;
  max-width: 155mm; text-align: left;
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.2mm 3mm;
}
.rk-hero-bullets li {
  position: relative; padding: 1mm 0 1mm 5mm;
  font-size: 8.7pt; line-height: 1.5; color: var(--color-ink-soft);
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.rk-hero-bullets li:last-child, .rk-hero-bullets li:nth-last-child(2):nth-child(odd) {
  border-bottom: none;
}
.rk-hero-bullets li::before {
  content: "✦"; position: absolute; left: 1mm; top: 1.5mm;
  color: var(--color-gold-deep); font-size: 7pt;
}
.rk-hero-bk {
  color: var(--color-red); font-weight: 700;
  font-family: var(--font-display); letter-spacing: 0.2px;
}
.rk-hero-foot {
  margin-top: var(--sp-2); font-family: var(--font-display); font-style: italic;
  font-size: 7.5pt; color: var(--color-gold-deep); letter-spacing: 1.5px;
}

/* --- Trait cards (kekuatan / kelemahan) --- */
.rk-tc-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.8mm;
  margin: 0 0 var(--sp-3) 0;
  break-inside: avoid;
}
.rk-tc {
  display: grid; grid-template-columns: 6mm 1fr; gap: 1.8mm;
  padding: 1.8mm 2.5mm; border-radius: var(--r-md);
  border: var(--bw-hair) solid var(--color-gold-soft);
  background: var(--color-paper);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
  break-inside: avoid;
}
.rk-tc.mood-good {
  background: linear-gradient(135deg, #F0F8EC 0%, #FBF7F0 100%);
  border-left: 0.7mm solid var(--color-success);
}
.rk-tc.mood-warn {
  background: linear-gradient(135deg, #FCF4E8 0%, #FBF7F0 100%);
  border-left: 0.7mm solid var(--color-warn);
}
.rk-tc-icon {
  font-family: var(--font-display); font-size: 11pt;
  font-weight: 700; line-height: 1;
  width: 6mm; height: 6mm; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white;
  align-self: start; margin-top: 0.3mm;
}
.rk-tc.mood-good .rk-tc-icon { background: var(--color-success); }
.rk-tc.mood-warn .rk-tc-icon { background: var(--color-warn); }
.rk-tc-label {
  font-family: var(--font-display); font-size: 9.5pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px; margin-bottom: 0.4mm;
}
.rk-tc-text { font-size: 8.3pt; line-height: 1.5; color: var(--color-ink-soft); }

/* --- Saran bidang grid --- */
.rk-saran-grid {
  display: grid; gap: 2mm;
  margin: 0 0 var(--sp-3) 0;
}
.rk-saran-grid.cols-2 { grid-template-columns: 1fr 1fr; }
.rk-saran-grid.cols-3 { grid-template-columns: 1fr 1fr 1fr; }
.rk-saran-card {
  padding: 2mm 2.8mm; border-radius: var(--r-md);
  background: linear-gradient(180deg, #FBF7F0 0%, #F8EFD7 100%);
  border: var(--bw-hair) solid var(--color-gold-soft);
  border-top: 0.6mm solid var(--color-gold);
  box-shadow: 0 0.2mm 0.6mm rgba(139,26,26,0.05);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.rk-saran-head {
  display: flex; align-items: center; gap: 1.5mm;
  margin-bottom: 1mm; padding-bottom: 0.8mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.rk-saran-icon { font-size: 12pt; line-height: 1; }
.rk-saran-bidang {
  font-family: var(--font-display); font-size: 9.5pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.4px;
}
.rk-saran-text { font-size: 8.3pt; line-height: 1.5; color: var(--color-ink-soft); }
.rk-saran-bullets {
  margin: 0; padding: 0; list-style: none;
  font-size: 8.2pt; line-height: 1.5; color: var(--color-ink-soft);
}
.rk-saran-bullets li {
  position: relative; padding: 0.3mm 0 0.3mm 4mm;
}
.rk-saran-bullets li::before {
  content: "◆"; color: var(--color-gold); position: absolute; left: 1mm;
  font-size: 6pt; top: 1.4mm;
}

/* --- Kalender timeline --- */
.rk-cal-wrap {
  position: relative; margin: var(--sp-2) 0 var(--sp-3) 0;
  padding: var(--sp-3) var(--sp-3) var(--sp-3) var(--sp-3);
  background: linear-gradient(180deg, #FCF4E8 0%, #F8EFD7 100%);
  border: var(--bw-hair) solid var(--color-gold-soft);
  border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.rk-cal-head {
  display: flex; align-items: baseline; gap: 1.5mm;
  margin-bottom: var(--sp-2); padding-bottom: 1mm;
  border-bottom: 0.2mm solid var(--color-gold-soft);
}
.rk-cal-head-icon { font-size: 11pt; }
.rk-cal-head-id {
  font-family: var(--font-display); font-size: 11pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.5px;
}
.rk-cal-head-hz {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-muted);
  letter-spacing: 2px; margin-left: auto;
}
.rk-cal-line {
  position: absolute; top: 50%; left: 8mm; right: 8mm;
  height: 0.4mm;
  background: linear-gradient(90deg, var(--color-gold-soft) 0%, var(--color-gold) 50%, var(--color-gold-soft) 100%);
  z-index: 0;
}
.rk-cal-track {
  display: flex; gap: 2mm; align-items: stretch;
  position: relative; z-index: 1;
}
.rk-cal-node {
  flex: 1; min-width: 0;
  padding: 1.8mm 1.5mm; border-radius: var(--r-md);
  text-align: center;
  border: var(--bw-hair) solid var(--color-gold-soft);
  background: var(--color-paper);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.rk-cal-node.mood-warn {
  border-left: 0.5mm solid var(--color-warn);
  background: linear-gradient(180deg, #FCF4E8 0%, var(--color-paper) 100%);
}
.rk-cal-node.mood-info {
  border-left: 0.5mm solid var(--color-gold);
  background: linear-gradient(180deg, #FDF8EE 0%, var(--color-paper) 100%);
}
.rk-cal-year {
  font-family: var(--font-display); font-size: 13pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.5px; line-height: 1;
  margin-bottom: 0.6mm;
}
.rk-cal-dot {
  font-size: 8pt; line-height: 1; color: var(--color-gold);
  margin-bottom: 0.6mm;
}
.rk-cal-node.mood-warn .rk-cal-dot { color: var(--color-warn); }
.rk-cal-text {
  font-size: 7.8pt; line-height: 1.45; color: var(--color-ink-soft);
}
.rk-cal-fallback { font-size: 8.5pt; line-height: 1.55; color: var(--color-ink-soft); }

/* --- Tematik (long-form advice) cards --- */
.rk-tematik-stack { display: flex; flex-direction: column; gap: 1.8mm; margin: 0 0 var(--sp-3) 0; }
.rk-tematik-card {
  display: grid; grid-template-columns: 10mm 1fr; gap: 2mm;
  padding: 2mm 2.5mm 2mm 2mm;
  border-radius: var(--r-md);
  background: linear-gradient(135deg, #FBF7F0 0%, #F8EFD7 100%);
  border: var(--bw-hair) solid var(--color-gold-soft);
  border-left: 0.7mm solid var(--color-red);
  box-shadow: var(--sh-soft);
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.rk-tematik-num {
  display: flex; align-items: center; justify-content: center;
  width: 9mm; height: 9mm; align-self: center;
  border-radius: 50%;
  background: var(--color-red); color: var(--color-cream);
  font-family: var(--font-display); font-size: 11pt; font-weight: 700;
  letter-spacing: 0.5px; line-height: 1;
}
.rk-tematik-body { min-width: 0; }
.rk-tematik-head {
  display: flex; align-items: center; gap: 1.5mm;
  padding-bottom: 0.6mm; margin-bottom: 0.6mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.rk-tematik-icon { font-size: 11pt; line-height: 1; }
.rk-tematik-title {
  font-family: var(--font-display); font-size: 10pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px; line-height: 1.25;
}
.rk-tematik-text {
  font-size: 8.5pt; line-height: 1.55; color: var(--color-ink-soft);
  text-align: justify;
}
.rk-tematik-text strong { color: var(--color-red); font-weight: 600; }

/* --- Periode (Da Yun) timeline — horizontal life-cycle --- */
.rk-pd-wrap {
  position: relative; margin: var(--sp-2) 0 var(--sp-3) 0;
  padding: var(--sp-3);
  background: linear-gradient(180deg, #FCF8EC 0%, #F4E8CC 100%);
  border: var(--bw-hair) solid var(--color-gold-soft);
  border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.rk-pd-head {
  display: flex; align-items: baseline; gap: 1.5mm;
  margin-bottom: var(--sp-2); padding-bottom: 1mm;
  border-bottom: 0.2mm solid var(--color-gold-soft);
}
.rk-pd-head-icon { font-size: 11pt; }
.rk-pd-head-id {
  font-family: var(--font-display); font-size: 11pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.5px;
}
.rk-pd-head-hz {
  font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-muted);
  letter-spacing: 3px; margin-left: auto;
}
.rk-pd-line {
  position: absolute; top: 50%; left: 8mm; right: 8mm;
  height: 0.4mm;
  background: linear-gradient(90deg, var(--color-gold-soft) 0%, var(--color-gold-deep) 50%, var(--color-gold-soft) 100%);
  z-index: 0;
}
.rk-pd-track {
  display: flex; gap: 2mm; align-items: stretch;
  position: relative; z-index: 1;
}
.rk-pd-node {
  flex: 1; min-width: 0;
  padding: 1.8mm 1.6mm; border-radius: var(--r-md);
  text-align: center;
  border: var(--bw-hair) solid var(--color-gold-soft);
  background: var(--color-paper);
  border-top: 0.5mm solid var(--color-gold-deep);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.rk-pd-key {
  font-family: var(--font-display); font-size: 9.5pt; font-weight: 700;
  color: var(--color-red); line-height: 1.1;
  margin-bottom: 0.4mm;
}
.rk-pd-key .hz { color: var(--color-red); }
.rk-pd-age {
  font-family: var(--font-display); font-size: 7.5pt; color: var(--color-gold-deep);
  font-weight: 600; letter-spacing: 0.5px;
  margin-bottom: 0.5mm;
}
.rk-pd-dot {
  font-size: 8pt; line-height: 1; color: var(--color-gold-deep);
  margin-bottom: 0.5mm;
}
.rk-pd-text {
  font-size: 7.6pt; line-height: 1.45; color: var(--color-ink-soft);
}
"""
