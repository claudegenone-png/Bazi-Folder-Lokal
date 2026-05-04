"""Generic section template — catchall for life areas (karir/keuangan/dst)
and UNKNOWN topics.

Visual-led: lead callout, sectioned cards with icons, mood-aware bullet
lists (saran/kewaspadaan), rating/stat detection, table styling, drop-cap
on first paragraph. Auto-paginate when content overflows.
"""
import re
import html as _html
from templates.page_shell import page_shell
from templates.primitives import (
    callout, bullet_list, section_h3, divider,
    quote_block, gloss_text,
)


def _esc(s):
    return _html.escape(s or "", quote=False)


# ─────────────────────────────────────────────────────────────────────────
# Heuristic patterns for visual upgrades
# ─────────────────────────────────────────────────────────────────────────

STAR_INLINE = re.compile(r"([★]{1,5})\s*([☆]{0,5})")
RATING_KEY = re.compile(r"^([A-Za-zÀ-ſ][\w\s/&\-]+?)\s*[:：]\s*([★]{1,5}[☆]{0,5})\s*(.*)$")

# Bold-label → mini-card/heading mood inference
LABEL_GOOD = re.compile(r"\b(positif|kekuatan|peluang|saran|rekomendasi|harapan|kelebihan|kunci\s+sukses)\b", re.I)
LABEL_WARN = re.compile(r"\b(waspada|kewaspadaan|tantangan|kelemahan|negatif|hindari|risiko|peringatan|hati[-\s]?hati)\b", re.I)
LABEL_INFO = re.compile(r"\b(profil|interpretasi|gambaran|ringkasan|catatan|info|kondisi|tema)\b", re.I)
LABEL_FACT = re.compile(r"\b(fakta|kunci|profesi|bidang|usia|tahun|elemen|pasangan|warna|arah)\b", re.I)

LABEL_ICON = [
    (re.compile(r"\b(saran|rekomendasi)\b", re.I), "💡"),
    (re.compile(r"\b(kewaspadaan|waspada|hindari)\b", re.I), "⚠"),
    (re.compile(r"\b(positif|kekuatan|peluang|harapan)\b", re.I), "✓"),
    (re.compile(r"\b(tantangan|negatif|kelemahan|risiko)\b", re.I), "!"),
    (re.compile(r"\b(profil|gambaran|ringkasan|catatan)\b", re.I), "✦"),
    (re.compile(r"\b(interpretasi|tafsir)\b", re.I), "🔍"),
    (re.compile(r"\b(profesi|karir|bisnis)\b", re.I), "💼"),
    (re.compile(r"\b(keuangan|finansial)\b", re.I), "💰"),
    (re.compile(r"\b(asmara|hubungan|pasangan)\b", re.I), "💕"),
    (re.compile(r"\b(rumah|feng\s*shui)\b", re.I), "🏠"),
    (re.compile(r"\b(kesehatan|fisik)\b", re.I), "🏥"),
    (re.compile(r"\b(elemen|wuxing|wu\s*xing)\b", re.I), "✦"),
    (re.compile(r"\b(bintang)\b", re.I), "⭐"),
    (re.compile(r"\b(tema|gambaran)\b", re.I), "🎯"),
]


def _icon_for_label(text):
    if not text: return "❖"
    for pat, ic in LABEL_ICON:
        if pat.search(text):
            return ic
    return "❖"


def _mood_for_label(text):
    if not text: return None
    if LABEL_WARN.search(text): return "warn"
    if LABEL_GOOD.search(text): return "good"
    if LABEL_INFO.search(text): return "info"
    return None


def _stars_html(stars_on_str, stars_off_str=""):
    on_n = len(stars_on_str)
    off_n = len(stars_off_str) or max(0, 5 - on_n)
    return (
        '<span class="gs-stars">'
        + "".join('<span class="gs-star on">★</span>' for _ in range(on_n))
        + "".join('<span class="gs-star off">★</span>' for _ in range(off_n))
        + '</span>'
    )


# ─────────────────────────────────────────────────────────────────────────
# Block renderers
# ─────────────────────────────────────────────────────────────────────────

def _try_rating_line(s):
    """If line is "Profesi Cocok: ★★★★☆ extra...", render as KV-card with stars.
    Returns HTML string or None.
    """
    m = RATING_KEY.match(s)
    if not m:
        # Standalone "★★★★☆" style → return inline stars block
        m2 = STAR_INLINE.search(s)
        if m2 and m2.start() <= 2:
            return None  # let normal paragraph handle inline
        return None
    key = m.group(1).strip()
    on = m.group(2)
    extra = m.group(3).strip()
    on_count = on.count("★")
    extra_html = f'<div class="gs-rating-extra">{gloss_text(extra)}</div>' if extra else ""
    stars_html = _stars_html("★" * on_count, "☆" * (5 - on_count))
    return (
        f'<div class="gs-rating"><div class="gs-rating-key">{_esc(key)}</div>'
        f'{stars_html}'
        f'{extra_html}'
        f'</div>'
    )


def _para_html(text, *, is_lead=False):
    """Style a paragraph. is_lead=True → drop-cap + larger leading."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    klass = "gs-para gs-lead" if is_lead else "gs-para"
    return f'<div class="{klass}">{gloss_text(text) if "<strong>" not in text else text}</div>'


def _label_card_html(label, items, mood):
    """Render a labeled bullet group as a mood-coded card."""
    icon = _icon_for_label(label)
    mood = mood or "info"
    if not items:
        return ""
    lis = "".join(
        f'<li><strong>{_esc(it.get("label",""))}</strong> — {gloss_text(it.get("text",""))}</li>'
        if it.get("label") else
        f'<li>{gloss_text(it.get("text",""))}</li>'
        for it in items
    )
    return (
        f'<div class="gs-labeled-card v-{mood}">'
        f'<div class="gs-lc-head"><span class="gs-lc-icon">{icon}</span>'
        f'<span class="gs-lc-label">{_esc(label)}</span></div>'
        f'<ul class="gs-lc-list">{lis}</ul>'
        f'</div>'
    )


def _label_callout_html(label, paragraph_text, mood):
    """Bold-label line followed by single paragraph → mood-coded callout."""
    icon = _icon_for_label(label)
    mood = mood or "info"
    return (
        f'<div class="gs-labeled-call v-{mood}">'
        f'<div class="gs-lc-head"><span class="gs-lc-icon">{icon}</span>'
        f'<span class="gs-lc-label">{_esc(label)}</span></div>'
        f'<div class="gs-lc-text">{gloss_text(paragraph_text)}</div>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────
# Main MD-to-HTML walker
# ─────────────────────────────────────────────────────────────────────────

def render_generic_lines(lines):
    out = []
    i = 0
    n = len(lines)
    cur_para = []
    para_count = [0]
    pending_label = None  # (label_text, mood)

    def flush_para():
        if not cur_para: return
        text = " ".join(cur_para).strip()
        if not text:
            cur_para.clear(); return
        para_count[0] += 1
        # If pending_label exists → render as labeled callout
        nonlocal pending_label
        if pending_label is not None:
            label, mood = pending_label
            out.append(_label_callout_html(label, text, mood))
            pending_label = None
        else:
            out.append(_para_html(text, is_lead=(para_count[0] == 1)))
        cur_para.clear()

    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            flush_para()
            i += 1; continue

        # Skip horizontal rule
        if s == "---":
            flush_para()
            out.append(divider())
            i += 1; continue

        # H3 / H4 → section heading (forces label flush)
        if s.startswith("### ") or s.startswith("#### "):
            flush_para()
            pending_label = None
            head = re.sub(r"^#{3,4}\s+", "", s).strip()
            head = re.sub(r"^[\W_]+\s*", "", head)
            m = re.match(r"^(.+?)\s*\(\s*([^)]+)\s*\)\s*$", head)
            if m:
                title, hz_part = m.group(1).strip(), m.group(2).strip()
            else:
                m = re.match(r"^(.+?)\s*[—–\-]\s*(.+)$", head)
                if m:
                    title, hz_part = m.group(1).strip(), m.group(2).strip()
                else:
                    title, hz_part = head, None
            out.append(section_h3(title, hz_part))
            i += 1; continue

        # Blockquote
        if s.startswith(">"):
            flush_para()
            qbuf = []
            while i < n and lines[i].strip().startswith(">"):
                qbuf.append(re.sub(r"^>\s*", "", lines[i].strip()))
                i += 1
            text = " ".join(qbuf)
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
            # Skip predominantly-Hanzi blockquote (raw transkripsi)
            han = sum(1 for c in text if "一" <= c <= "鿿")
            latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
            if han > latn * 1.5:
                continue
            out.append(quote_block(text))
            continue

        # Bullets (consecutive)
        if re.match(r"^[-*]\s+", s):
            flush_para()
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                content = re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()
                mb = re.match(r"^\*\*([^*]+)\*\*\s*[—–\-:]\s*(.+)$", content)
                if mb:
                    buf.append({"label": mb.group(1).strip(), "text": mb.group(2).strip()})
                else:
                    buf.append({"text": re.sub(r"\*\*([^*]+)\*\*", r"\1", content)})
                i += 1
            # If pending_label → render as labeled-card; else as plain bullet list with mood
            if pending_label is not None:
                label, mood = pending_label
                out.append(_label_card_html(label, buf, mood))
                pending_label = None
            else:
                # Plain bullet group — try to infer mood from item content keywords
                joined = " ".join(it.get("text", "") + " " + it.get("label", "") for it in buf)
                mood = "good" if LABEL_GOOD.search(joined) else \
                       "warn" if LABEL_WARN.search(joined) else "neutral"
                out.append(bullet_list(buf, mood=mood))
            continue

        # Bold-label only line → defer; if next non-empty is bullets/paragraph, render as group head
        m_lbl = re.match(r"^\*\*([^*]+?)\*\*\s*:?\s*$", s)
        if m_lbl:
            flush_para()
            label = m_lbl.group(1).strip()
            label = re.sub(r"^[\W_]+\s*", "", label)  # strip leading emoji
            label = re.sub(r"\s*:\s*$", "", label)
            mood = _mood_for_label(label)
            pending_label = (label, mood)
            i += 1; continue

        # Inline rating line: "Profesi Cocok: ★★★★☆ ..."
        rating_html = _try_rating_line(s)
        if rating_html:
            flush_para()
            out.append(rating_html)
            i += 1; continue

        # Pipe table
        if "|" in s and i + 1 < n and re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", lines[i+1]):
            flush_para()
            tbuf = []
            while i < n and "|" in lines[i]:
                tbuf.append(lines[i]); i += 1
            rows = []
            for tl in tbuf:
                if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", tl): continue
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                rows.append(cells)
            if rows:
                th = "".join(f"<th>{gloss_text(c)}</th>" for c in rows[0])
                body = "".join(
                    "<tr>" + "".join(f"<td>{gloss_text(c)}</td>" for c in r) + "</tr>"
                    for r in rows[1:]
                )
                out.append(f'<table class="gs-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>')
            continue

        # Inline ✅/⚠/🌟 prefixed paragraph (subject 2 style) → mini callout
        if re.match(r"^[✅✔]\s*", s):
            flush_para()
            text = re.sub(r"^[✅✔]\s*", "", s)
            out.append(_label_callout_html("Peluang", text, "good"))
            i += 1; continue
        if re.match(r"^[⚠❗]\s*", s):
            flush_para()
            text = re.sub(r"^[⚠❗]\s*", "", s)
            out.append(_label_callout_html("Tantangan", text, "warn"))
            i += 1; continue
        if re.match(r"^[🌟⭐✨]\s*", s):
            flush_para()
            text = re.sub(r"^[🌟⭐✨]\s*", "", s)
            out.append(_label_callout_html("Bintang", text, "info"))
            i += 1; continue

        # Skip predominantly-Hanzi paragraph (raw OCR transkripsi)
        han = sum(1 for c in s if "一" <= c <= "鿿")
        latn = sum(1 for c in s if c.isalpha() and ord(c) < 128)
        if han > 5 and han > latn * 1.5:
            i += 1; continue

        # Plain paragraph → accumulate
        cur_para.append(s)
        i += 1

    flush_para()
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────────
# Page renderer (single-page; caller advances pn += 1)
# ─────────────────────────────────────────────────────────────────────────

def _density_class(body_html):
    """Return density modifier class for ps-content scaling when content is dense."""
    n = len(body_html)
    if n > 6000: return "gs-density-tight"
    if n > 4500: return "gs-density-mid"
    return ""


# ─────────────────────────────────────────────────────────────────────────
# Interpretasi extraction — subject-specific blockquote at top of section
# (rule: setiap bab wajib interpretasi Indo dari MD di paling atas)
# ─────────────────────────────────────────────────────────────────────────

_GS_GENERIC_INTRO = re.compile(r"^[\W_]*apa\s+itu\b", re.IGNORECASE)
_GS_WARN_META = re.compile(r"^[⚠📌🗓⚠️📌🗓️\s]*(catatan|warning|note|sumber|laporan ini|data terbaca|software)\b", re.IGNORECASE)
_GS_SUBJECT_KW = re.compile(r"\b(makna\s+praktis|tips\s+praktis|interpretasi|saran|tafsir|penjelasan|ringkasan|kesimpulan|gambaran|profil|temuan|inti)\b", re.IGNORECASE)
_GS_SUBJECT_EMOJI = ("💡", "💼", "❤️", "❤", "👥", "💕", "🌟", "🔮", "✦", "🎯", "💎", "🏠", "🏥", "📜", "🌸", "🌿")


_INTERP_HDR = re.compile(r"^####?\s+[\W_]*\s*(interpretasi|tafsir|penjelasan|🔍\s*interpretasi|🖊\s*interpretasi|panduan|rekomendasi)\b", re.IGNORECASE)


def _extract_interpretasi(lines):
    """Find subject-specific interpretasi text near top of section.
    Strategy:
      1. Subject-specific blockquote (💡, 💼, ❤️, ✦, dst) — non-warning
      2. First paragraph under "### 🔍 Interpretasi" / "### Tafsir" sub-section
      3. (Skip) Generic "Apa itu X?" intros, "⚠ Catatan", meta lines
    Returns (text, line_range_to_skip_in_render) or (None, None).
    """
    n = len(lines)

    # Strategy 1: subject-specific blockquote
    i = 0
    while i < n:
        s = lines[i].strip()
        if s.startswith(">"):
            start = i
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s*", "", lines[i].strip()))
                i += 1
            text = " ".join(buf)
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
            text = re.sub(r"\*([^*]+)\*", r"\1", text).strip()
            if not text or len(text) < 30: continue
            if _GS_GENERIC_INTRO.search(text[:60]): continue
            if _GS_WARN_META.match(text): continue
            is_emoji = any(text.startswith(e) for e in _GS_SUBJECT_EMOJI)
            is_kw = bool(_GS_SUBJECT_KW.search(text[:80]))
            if is_emoji or is_kw:
                return text, (start, i)
        else:
            i += 1

    # Strategy 2: paragraph under "### Interpretasi" / "### Tafsir" sub-header (when MD has it explicit)
    i = 0
    while i < n:
        s = lines[i].strip()
        if _INTERP_HDR.match(s):
            hdr_idx = i
            i += 1
            while i < n and not lines[i].strip(): i += 1
            buf = []
            while i < n:
                ls = lines[i].strip()
                if not ls: break
                if ls.startswith(("#", "|", "-", "*", ">", "**")) or ls == "---": break
                buf.append(ls)
                i += 1
            content_end = i
            text = " ".join(buf)
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()
            if text and len(text) > 30 and not _GS_WARN_META.match(text):
                return text, (hdr_idx, content_end)
            continue
        i += 1

    # Strategy 3: first plain non-Hanzi paragraph (skip blockquotes, raw OCR, bullets, labels, tables)
    i = 0
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1; continue
        if s.startswith(("#", "|", "-", "*", ">", "**")) or s == "---":
            i += 1; continue
        # Skip Hanzi-dominant raw transkripsi (line-level, fast reject)
        han = sum(1 for c in s if "一" <= c <= "鿿")
        latn = sum(1 for c in s if c.isalpha() and ord(c) < 128)
        if han > 4 and han > max(latn, 1) * 1.2:
            i += 1; continue
        # Skip "(Berlanjut...)" continuation markers
        if re.match(r"^\([Bb]erlanjut", s):
            i += 1; continue
        # Skip ●/◎ marker lines (raw OCR style)
        if s.startswith(("●", "◎", "○")):
            i += 1; continue
        # Skip warnings/meta
        if _GS_WARN_META.match(s):
            i += 1; continue
        if _GS_GENERIC_INTRO.search(s[:60]):
            i += 1; continue
        # Collect paragraph (until blank/break)
        start = i
        buf = []
        while i < n:
            ls = lines[i].strip()
            if not ls: break
            if ls.startswith(("#", "|", "-", "*", ">", "**")) or ls == "---": break
            if ls.startswith(("●", "◎", "○")): break
            buf.append(ls)
            i += 1
        text = " ".join(buf)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()
        # Final paragraph-level Hanzi check (might have absorbed mixed content)
        han = sum(1 for c in text if "一" <= c <= "鿿")
        latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        if han > 8 and han > latn * 1.2:
            continue  # absorb-Hanzi → skip, advance to next
        # Skip caption-style lines (ending with ":") — they're table/list intros, not interpretasi
        if re.search(r":\s*$", text):
            continue
        if text and len(text) > 50:
            return text, (start, i)
    return None, None


# ─────────────────────────────────────────────────────────────────────────
# Tabel Aliran Tahunan — special-case renderer (Hanzi-friendly for Indo readers)
# ─────────────────────────────────────────────────────────────────────────

# 12 Long Sheng (12 fase hidup) → mood + Indo gloss
_TWELVE_PHASE = {
    "長生": ("Tumbuh Awal",     "good"),
    "沐浴": ("Pembersihan",     "neutral"),
    "冠帶": ("Persiapan",       "good"),
    "臨官": ("Mendekati Puncak","good"),
    "帝旺": ("Puncak Kekuatan", "good"),
    "衰":   ("Mulai Menurun",   "warn"),
    "病":   ("Lemah",           "warn"),
    "死":   ("Titik Mati",      "warn"),
    "墓":   ("Tertahan",        "warn"),
    "絕":   ("Terputus",        "warn"),
    "胎":   ("Mengandung",      "neutral"),
    "養":   ("Memelihara",      "neutral"),
}

# Da Yun (10-year period) tema narratives — canonical meanings of Ten Gods
# applied to a multi-year cycle. Not fabricated: these are standard BaZi readings.
_DAYUN_NARRATIVE = {
    "比肩": "Periode kebersamaan dan persaingan dengan sesama. Banyak interaksi sosial, kolaborasi, namun juga rivalitas. Cocok untuk membangun jaringan & partner.",
    "劫財": "Periode persaingan ketat dan ujian keuangan. Hati-hati pengeluaran tak terduga atau pesaing yang merugikan, namun juga periode bertumbuh karena interaksi intens.",
    "食神": "Periode kreatif, produktif, dan menikmati hidup. Cocok untuk berkarya, menulis, mengajar, dan hal-hal yang melibatkan ekspresi diri.",
    "傷官": "Periode ekspresi diri kuat dan kemungkinan gesekan dengan otoritas. Bakat keluar, tapi perlu hati-hati menjaga relasi.",
    "正財": "Periode pemasukan stabil dari kerja keras. Cocok untuk membangun karir, properti, dan tabungan jangka panjang.",
    "偏財": "Periode rejeki tak terduga, peluang bisnis sampingan, atau investasi. Lebih dinamis daripada 正財.",
    "正官": "Periode wewenang, posisi resmi, dan tanggung jawab. Cocok untuk promosi karir atau memikul peran penting.",
    "七殺": "Periode tantangan dan tekanan keras. Banyak ujian, namun yang bertahan akan tumbuh kuat. Hati-hati konflik & stress.",
    "正印": "Periode mendapat perlindungan, bantuan dari senior/mentor, dan kemudahan akademik. Cocok untuk belajar atau mengakar lebih dalam.",
    "偏印": "Periode bantuan tak terduga, intuisi tajam, dan minat pada hal-hal mendalam (spiritual, riset). Lebih soliter daripada 正印.",
}


# Sepuluh Dewa → Indo + tema singkat
_TEN_GODS = {
    "比肩": ("Saudara Setara",   "neutral", "Sesama, sahabat, pesaing"),
    "劫財": ("Perampas Harta",   "warn",    "Pesaing keras, biaya tak terduga"),
    "食神": ("Dewa Makanan",     "good",    "Kreatif, menikmati hidup"),
    "傷官": ("Dewa Cedera",      "neutral", "Ekspresi diri, tantangan otoritas"),
    "正財": ("Harta Tetap",      "good",    "Pendapatan stabil, hasil kerja"),
    "偏財": ("Harta Sampingan",  "good",    "Rejeki tak terduga"),
    "正官": ("Pejabat Resmi",    "good",    "Wewenang, tanggung jawab"),
    "七殺": ("Tujuh Pembunuh",   "warn",    "Tekanan, tantangan keras"),
    "正印": ("Segel Resmi",      "good",    "Pelindung, ilmu, mentor"),
    "偏印": ("Segel Tersembunyi","neutral", "Bantuan tak terduga, intuisi"),
}

# Bintang Khusus (神煞) → Indo + mood
_SHENSHA_HINT = {
    "龍德": ("Dewa Naga",        "good"),
    "天德": ("Berkah Surga",     "good"),
    "天乙": ("Pertolongan Mulia","good"),
    "將星": ("Bintang Jenderal", "good"),
    "千祿": ("Rejeki Ribu",      "good"),
    "金輿": ("Kereta Emas",      "good"),
    "文昌": ("Bintang Cendekia", "good"),
    "華蓋": ("Bintang Seni",     "neutral"),
    "桃花": ("Bintang Asmara",   "neutral"),
    "驛馬": ("Kuda Pos",         "neutral"),
    "紅鸞": ("Burung Merah",     "neutral"),
    "天喜": ("Sukacita Surga",   "good"),
    "白虎": ("Macan Putih",      "warn"),
    "天掃": ("Sapu Surga",       "warn"),
    "羊刃": ("Pisau Domba",      "warn"),
    "劫煞": ("Bencana Rampas",   "warn"),
    "煞":   ("Bencana",          "warn"),
    "寡宿": ("Bintang Janda",    "warn"),
    "孤辰": ("Bintang Sepi",     "warn"),
    "災煞": ("Bencana",          "warn"),
}


def _gloss_phase(hz):
    """Return (indo, mood) for a 12-phase term. Fallback: ('', 'neutral')."""
    hz = (hz or "").strip()
    if hz in _TWELVE_PHASE: return _TWELVE_PHASE[hz]
    return ("", "neutral")


def _gloss_tg(hz):
    """Return (indo, mood, tema) for a Ten God. Fallback ('', 'neutral', '')."""
    hz = (hz or "").strip()
    if hz in _TEN_GODS: return _TEN_GODS[hz]
    return ("", "neutral", "")


def _gloss_shensha(hz):
    """Return (indo, mood) for a single Shensha. Fallback ('', 'neutral')."""
    hz = (hz or "").strip()
    if hz in _SHENSHA_HINT: return _SHENSHA_HINT[hz]
    return ("", "neutral")


_PERIODE_HDR_PAT = re.compile(
    r"^\*\*\s*(Periode|Siklus(?:\s+Besar)?(?:\s+Saat\s+Ini|\s+Sebelumnya)?)\s*"
    r"(?:Sebelumnya|Saat\s+Ini)?\s*"
    r"[:：]?\s*"
    r"(?:\(?\s*([一-鿿]{2,3})(?:\s*\(([^)]+)\))?\s*\)?)?"
    r"(?:\s*[—–\-]?\s*(?:大運\s*[:：]\s*([^/]+?)\s*/\s*([^—–\-]+?)\s*[—–\-]\s*([一-鿿]{2}))?)?"
    r"(?:\s*[—–\-]\s*Usia\s*[:：]?\s*(\d+\s*[-–—]\s*\d+))?"
    r".*\*\*\s*$",
    re.IGNORECASE,
)


def _parse_periode_header(line):
    """Best-effort parse of periode header like:
      **Periode 59–68 (大運: 劫財 / Perampas Harta — 甲子)**
      **Siklus Besar Saat Ini: 乙酉 (Yi You) — Usia 33–42**
    Returns dict with: usia_range, ganzhi, ganzhi_pinyin, ten_god_hz, ten_god_indo, label
    Empty fields fallback to None.
    """
    s = line.strip()
    out = {"label": "", "usia_range": None, "ganzhi": None, "ganzhi_pinyin": None,
           "ten_god_hz": None, "ten_god_indo": None, "is_current": False}
    if "saat ini" in s.lower(): out["is_current"] = True
    # Strip ** markers
    inner = re.sub(r"^\*\*\s*|\s*\*\*$", "", s)
    out["label"] = inner
    # Extract usia range: "59-68" / "Usia 33-42"
    m_usia = re.search(r"(?:usia\s+)?(\d+\s*[-–—]\s*\d+)", inner, re.IGNORECASE)
    if m_usia: out["usia_range"] = m_usia.group(1).replace(" ", "")
    # Extract ganzhi (2 Hanzi chars, often after 大運 or after :)
    # Prefer ganzhi inside parens with pinyin: "(Yi You)" → ganzhi just before
    m_gz_py = re.search(r"([一-鿿]{2})\s*\(\s*([A-Za-zĀ-ž][\w\s]*)\s*\)", inner)
    if m_gz_py:
        out["ganzhi"] = m_gz_py.group(1)
        out["ganzhi_pinyin"] = m_gz_py.group(2).strip()
    else:
        # Bare 2-Hanzi after dash/em-dash
        m_gz = re.search(r"[—–\-]\s*([一-鿿]{2})(?:\s|$|\))", inner)
        if m_gz: out["ganzhi"] = m_gz.group(1)
    # Extract ten god: 大運: 劫財 / Perampas Harta
    m_tg = re.search(r"大運\s*[:：]\s*([一-鿿]{2})\s*/\s*([^—–\-]+?)\s*(?:[—–\-]|$)", inner)
    if m_tg:
        out["ten_god_hz"] = m_tg.group(1).strip()
        out["ten_god_indo"] = m_tg.group(2).strip()
    return out


def _parse_tabel_md(lines):
    """Walk lines, find periode-header + table rows. Returns list of periodes:
      [{header_dict, rows: [{usia, tahun, ganzhi, ten_god, status, bintang}]}]
    """
    periodes = []
    cur_periode = None
    cur_rows = []
    in_table = False
    headers_seen = False
    col_idx = {}  # column-name → index

    def flush_periode():
        nonlocal cur_periode, cur_rows, in_table, headers_seen, col_idx
        if cur_periode is not None:
            periodes.append({"header": cur_periode, "rows": cur_rows})
        cur_periode = None
        cur_rows = []
        in_table = False
        headers_seen = False
        col_idx = {}

    for raw in lines:
        s = raw.strip()
        if not s or s == "---":
            continue
        # H3 sub-header (Lin Ruyi style "### Siklus Besar Saat Ini ...")
        if s.startswith("### "):
            flush_periode()
            head = re.sub(r"^###\s+", "", s).strip()
            cur_periode = _parse_periode_header(f"**{head}**")
            continue
        # Bold-only periode header (Li Yuanxiang "**Periode 59-68 ...**")
        if re.match(r"^\*\*[^*]+\*\*\s*$", s):
            flush_periode()
            cur_periode = _parse_periode_header(s)
            continue
        # Pipe table line
        if "|" in s:
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            # Separator row (---|---|---)
            if re.match(r"^[\s\-:|]+$", "|".join(cells)):
                in_table = True
                continue
            # Header row detection — header rows have specific column-name words
            # in the FIRST cell (e.g. "Usia"). Data rows have number/age in cell[0].
            # Avoid false positives like "Dewa Makanan" in row content.
            first = cells[0].lower().strip("*").strip() if cells else ""
            is_header_row = first in ("usia", "umur", "age", "tahun")
            if is_header_row:
                # If we were already in a table → new periode boundary (Lin Ruyi case)
                if in_table or headers_seen:
                    # Flush current periode rows under placeholder if no header captured
                    if cur_rows:
                        if cur_periode is None:
                            cur_periode = {"label": f"Periode {len(periodes) + 1}",
                                           "usia_range": None, "ganzhi": None,
                                           "ganzhi_pinyin": None, "ten_god_hz": None,
                                           "ten_god_indo": None, "is_current": False}
                        flush_periode()
                col_idx = {}
                for idx, cell in enumerate(cells):
                    cl = cell.lower()
                    if "usia" in cl or "umur" in cl: col_idx["usia"] = idx
                    elif "tahun" in cl: col_idx["tahun"] = idx
                    elif "ganzhi" in cl or "batang" in cl or "branch" in cl: col_idx["ganzhi"] = idx
                    elif "dewa" in cl or "sepuluh" in cl: col_idx["ten_god"] = idx
                    elif "status" in cl or "fase" in cl or "siklus" in cl or "phase" in cl: col_idx["status"] = idx
                    elif "bintang" in cl or "khusus" in cl: col_idx["bintang"] = idx
                headers_seen = True
                in_table = False  # waiting for separator
                continue
            if in_table:
                row = {
                    "usia":    cells[col_idx["usia"]] if "usia" in col_idx and col_idx["usia"] < len(cells) else "",
                    "tahun":   cells[col_idx["tahun"]] if "tahun" in col_idx and col_idx["tahun"] < len(cells) else "",
                    "ganzhi":  cells[col_idx["ganzhi"]] if "ganzhi" in col_idx and col_idx["ganzhi"] < len(cells) else "",
                    "ten_god": cells[col_idx["ten_god"]] if "ten_god" in col_idx and col_idx["ten_god"] < len(cells) else "",
                    "status":  cells[col_idx["status"]] if "status" in col_idx and col_idx["status"] < len(cells) else "",
                    "bintang": cells[col_idx["bintang"]] if "bintang" in col_idx and col_idx["bintang"] < len(cells) else "",
                }
                cur_rows.append(row)
            continue
        # Other content (skip — likely periode prose between tables)

    # End of loop — capture any orphan rows under placeholder periode
    if cur_rows:
        if cur_periode is None:
            cur_periode = {"label": f"Periode {len(periodes) + 1}",
                           "usia_range": None, "ganzhi": None,
                           "ganzhi_pinyin": None, "ten_god_hz": None,
                           "ten_god_indo": None, "is_current": False}
        flush_periode()
    return periodes


def _render_tt_glossary():
    """Render universal glossary at top — explains Sepuluh Dewa, Status, Bintang Khusus."""
    # Compact glossary chips
    tg_items = "".join(
        f'<div class="tt-gl-item"><span class="tt-gl-hz">{hz}</span>'
        f'<span class="tt-gl-indo">{indo}</span>'
        f'<span class="tt-gl-tema">{tema}</span></div>'
        for hz, (indo, _, tema) in _TEN_GODS.items()
    )
    phase_items = "".join(
        f'<div class="tt-gl-phase mood-{mood}"><span class="tt-gl-hz">{hz}</span>'
        f'<span class="tt-gl-indo">{indo}</span></div>'
        for hz, (indo, mood) in _TWELVE_PHASE.items()
    )
    return f'''<div class="tt-glossary">
  <div class="tt-gl-eyebrow">PANDUAN BACA TABEL · 解 讀 表 格</div>
  <div class="tt-gl-intro">
    Tabel di bawah merangkum dinamika nasib per tahun. Tiap baris = 1 tahun usia.
    Karena banyak istilah Hanzi, gunakan glossary ini sebagai panduan cepat.
  </div>
  <div class="tt-gl-block">
    <div class="tt-gl-h">① Sepuluh Dewa <span class="tt-gl-hzh">十神</span> — corak energi tahun (relasi terhadap "Tuan Hari" Anda)</div>
    <div class="tt-gl-grid tt-gl-grid-tg">{tg_items}</div>
  </div>
  <div class="tt-gl-block">
    <div class="tt-gl-h">② Status <span class="tt-gl-hzh">十二長生</span> — kekuatan vital di tahun itu (12 fase siklus hidup)</div>
    <div class="tt-gl-grid tt-gl-grid-phase">{phase_items}</div>
  </div>
  <div class="tt-gl-block">
    <div class="tt-gl-h">③ Bintang Khusus <span class="tt-gl-hzh">神煞</span> — energi khusus yang aktif tahun itu</div>
    <div class="tt-gl-mood-row">
      <span class="tt-gl-chip mood-good">Hijau = Pelindung/Berkah (mis. 龍德, 天乙, 文昌)</span>
      <span class="tt-gl-chip mood-warn">Oranye = Perlu Waspada (mis. 白虎, 羊刃, 寡宿)</span>
      <span class="tt-gl-chip mood-neutral">Abu = Tema Khusus (mis. 桃花, 驛馬, 華蓋)</span>
    </div>
  </div>
</div>'''


def _render_tt_periode_header(hdr):
    """Render periode header card: Da Yun context + usia range + ten god."""
    if not hdr: return ""
    parts = []
    if hdr.get("usia_range"):
        parts.append(f'<span class="tt-ph-usia">Usia {hdr["usia_range"]}</span>')
    if hdr.get("ganzhi"):
        py = f' ({hdr["ganzhi_pinyin"]})' if hdr.get("ganzhi_pinyin") else ""
        parts.append(f'<span class="tt-ph-gz">Ganzhi: <strong>{hdr["ganzhi"]}</strong>{py}</span>')
    if hdr.get("ten_god_hz"):
        indo = hdr.get("ten_god_indo") or _gloss_tg(hdr["ten_god_hz"])[0]
        parts.append(f'<span class="tt-ph-tg">Tema Da Yun: <strong>{hdr["ten_god_hz"]}</strong> — {indo}</span>')
    badge = '<span class="tt-ph-now">SAAT INI</span>' if hdr.get("is_current") else ""
    return f'''<div class="tt-periode-head">
  <div class="tt-ph-icon">🌊</div>
  <div class="tt-ph-body">
    <div class="tt-ph-title">Periode Besar (大運 / Da Yun){badge}</div>
    <div class="tt-ph-meta">{"".join(parts)}</div>
  </div>
</div>'''


def _strip_inline_paren(s):
    """Remove trailing parenthesized gloss like '衰 (Shuai — Melemah)' → '衰'.
    Also strips wrapping ** markdown bold."""
    if not s: return ""
    s = s.strip()
    s = re.sub(r"^\*\*\s*|\s*\*\*$", "", s)
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    return s


def _split_hanzi_terms(cell):
    """Split a cell containing one or more Hanzi terms separated by + / 、,。
    Returns list of bare Hanzi tokens (stripped of parentheticals).
    Example: '七殺+偏印 (Tujuh Pembunuh + Harta Menyimpang)' → ['七殺', '偏印']
             '羊刃+亡神 (Yang Ren + Wang Shen) / 病符 (Bing Fu)' → ['羊刃','亡神','病符']
    """
    if not cell: return []
    # First strip parentheticals (Indo glosses) — keep only Hanzi-rich part
    no_paren = re.sub(r"\([^)]*\)", "", cell)
    # Split by separators
    tokens = re.split(r"[+/、,，\s·]+", no_paren)
    out = []
    for t in tokens:
        t = t.strip().strip("()*").strip()
        if not t: continue
        # Take only contiguous Hanzi prefix (drop trailing ASCII)
        m = re.match(r"^([一-鿿]+)", t)
        if m:
            out.append(m.group(1))
    return out


def _render_tt_row(row):
    # Status mood — extract bare Hanzi from "衰 (Shuai — Melemah)"
    st_raw = row.get("status", "")
    st_hz = _strip_inline_paren(st_raw)
    st_hz = re.match(r"^([一-鿿]+)", st_hz).group(1) if re.match(r"^([一-鿿]+)", st_hz) else st_hz
    st_indo, st_mood = _gloss_phase(st_hz)
    # Ten God
    tg_tokens = _split_hanzi_terms(row.get("ten_god", ""))
    tg_parts = []
    for tg_token in tg_tokens:
        indo, mood, _ = _gloss_tg(tg_token)
        if indo:
            tg_parts.append(f'<span class="tt-tg-chip mood-{mood}"><span class="hz">{tg_token}</span><span class="tt-tg-indo">{indo}</span></span>')
        else:
            tg_parts.append(f'<span class="tt-tg-chip mood-neutral"><span class="hz">{tg_token}</span></span>')
    # Bintang chips
    bx_tokens = _split_hanzi_terms(row.get("bintang", ""))
    bx_parts = []
    if not bx_tokens and "[" in row.get("bintang", ""):
        bx_parts.append('<span class="tt-bx-chip mood-neutral">[?]</span>')
    for hz in bx_tokens:
        indo, mood = _gloss_shensha(hz)
        if indo:
            bx_parts.append(f'<span class="tt-bx-chip mood-{mood}"><span class="hz">{hz}</span><span class="tt-bx-indo">{indo}</span></span>')
        else:
            bx_parts.append(f'<span class="tt-bx-chip mood-neutral"><span class="hz">{hz}</span></span>')

    usia = re.sub(r"\*\*", "", row.get("usia", "")).strip()
    tahun = re.sub(r"\*\*", "", row.get("tahun", "")).strip()
    # Tahun cell often has bare ganzhi (e.g. "丁未") instead of year number
    tahun_is_ganzhi = bool(re.match(r"^[一-鿿]{2,3}$", tahun))
    tahun_html = ""
    if tahun and tahun != "—":
        if tahun_is_ganzhi:
            tahun_html = f'<span class="tt-yc-gz hz">{_esc(tahun)}</span>'
        else:
            tahun_html = f'<span class="tt-yc-tahun">{_esc(tahun)}</span>'

    tg_chips = "".join(tg_parts) or '<span class="tt-yc-empty">—</span>'
    bx_chips = "".join(bx_parts) or '<span class="tt-yc-empty">—</span>'
    st_hz_html = _esc(st_hz) or "—"
    st_indo_html = _esc(st_indo) or "—"
    tg_block = (
        f'<div class="tt-yc-section"><div class="tt-yc-lbl">① Sepuluh Dewa <span class="tt-yc-lbl-hz">十神</span></div>'
        f'<div class="tt-yc-chips">{tg_chips}</div></div>'
    )
    st_block = (
        f'<div class="tt-yc-section"><div class="tt-yc-lbl">② Status <span class="tt-yc-lbl-hz">十二長生</span></div>'
        f'<div class="tt-yc-chips">'
        f'<span class="tt-st-chip mood-{st_mood}"><span class="hz">{st_hz_html}</span>'
        f'<span class="tt-st-indo">{st_indo_html}</span></span>'
        f'</div></div>'
    )
    bx_block = (
        f'<div class="tt-yc-section"><div class="tt-yc-lbl">③ Bintang Khusus <span class="tt-yc-lbl-hz">神煞</span></div>'
        f'<div class="tt-yc-chips">{bx_chips}</div></div>'
    )

    return f'''<div class="tt-yc mood-{st_mood}">
  <div class="tt-yc-head">
    <div class="tt-yc-usia"><span class="tt-yc-usia-lbl">USIA</span><strong class="tt-yc-usia-num">{_esc(usia)}</strong></div>
    {tahun_html}
  </div>
  {tg_block}
  {st_block}
  {bx_block}
</div>'''


def _row_mood(row):
    """Compute mood for a row by combining Status (12-fase) + Bintang Khusus + Sepuluh Dewa.
    Priority: Status > Bintang > Ten God. Returns 'good' | 'warn' | 'neutral'."""
    # Status mood
    st_raw = row.get("status", "")
    st_hz_match = re.match(r"^[一-鿿]+", _strip_inline_paren(st_raw))
    st_hz = st_hz_match.group(0) if st_hz_match else ""
    _, st_mood = _gloss_phase(st_hz)
    # Aggregate bintang mood
    bx_tokens = _split_hanzi_terms(row.get("bintang", ""))
    bx_moods = [_gloss_shensha(hz)[1] for hz in bx_tokens]
    bx_warn = sum(1 for m in bx_moods if m == "warn")
    bx_good = sum(1 for m in bx_moods if m == "good")
    # Aggregate ten god mood
    tg_tokens = _split_hanzi_terms(row.get("ten_god", ""))
    tg_moods = [_gloss_tg(hz)[1] for hz in tg_tokens]
    tg_warn = sum(1 for m in tg_moods if m == "warn")
    tg_good = sum(1 for m in tg_moods if m == "good")
    # Final score
    score = 0
    if st_mood == "good": score += 2
    elif st_mood == "warn": score -= 2
    score += bx_good - bx_warn
    score += (tg_good - tg_warn) * 0.5
    if score >= 1.5: return "good"
    if score <= -1.5: return "warn"
    return "neutral"


def _row_brief(row):
    """Generate 1-line brief tema for a row from its mood signals — deterministic
    composition from Status + dominant Ten God + dominant Bintang Khusus.
    Anti-fabrication: combines lookup-derived terms only."""
    parts = []
    # Dominant ten god
    tg_tokens = _split_hanzi_terms(row.get("ten_god", ""))
    if tg_tokens:
        indo, _, _ = _gloss_tg(tg_tokens[0])
        if indo: parts.append(indo)
    # Status
    st_match = re.match(r"^[一-鿿]+", _strip_inline_paren(row.get("status", "")))
    if st_match:
        st_indo, _ = _gloss_phase(st_match.group(0))
        if st_indo: parts.append(st_indo)
    # Notable bintang
    bx_tokens = _split_hanzi_terms(row.get("bintang", ""))
    notable = []
    for hz in bx_tokens:
        indo, mood = _gloss_shensha(hz)
        if indo and mood in ("good", "warn"):
            notable.append((hz, indo))
            if len(notable) >= 2: break
    if notable:
        parts.append("/".join(f"{hz} {indo}" for hz, indo in notable))
    return " · ".join(parts) if parts else "—"


def _pick_highlights(rows, limit=3):
    """Select the most extreme rows by mood: top warn + top good.
    Returns up to `limit` rows in original (chronological) order."""
    if not rows: return []
    # Score each row: positive = good, negative = warn
    scored = []
    for r in rows:
        st_match = re.match(r"^[一-鿿]+", _strip_inline_paren(r.get("status", "")))
        st_hz = st_match.group(0) if st_match else ""
        _, st_mood = _gloss_phase(st_hz)
        bx_tokens = _split_hanzi_terms(r.get("bintang", ""))
        bx_moods = [_gloss_shensha(hz)[1] for hz in bx_tokens]
        score = (3 if st_mood == "good" else (-3 if st_mood == "warn" else 0))
        score += sum(2 if m == "good" else (-2 if m == "warn" else 0) for m in bx_moods)
        scored.append((abs(score), score, r))
    # Take top by absolute extremity
    scored.sort(key=lambda x: -x[0])
    picked = [s[2] for s in scored[:limit]]
    # Reorder by usia (chronological)
    def usia_int(r):
        m = re.search(r"\d+", r.get("usia", ""))
        return int(m.group(0)) if m else 0
    picked.sort(key=usia_int)
    return picked


def _render_tt_timeline(rows):
    """Mini horizontal timeline — one chip per usia, color-coded by mood."""
    if not rows: return ""
    items = "".join(
        f'<div class="tt-tl-item mood-{_row_mood(r)}">'
        f'<span class="tt-tl-usia">{_esc(re.sub(r"[*]+","",r.get("usia","")).strip())}</span>'
        f'</div>'
        for r in rows
    )
    return f'''<div class="tt-tl-wrap">
  <div class="tt-tl-lbl">Mood Tahun-per-Usia</div>
  <div class="tt-tl-track">{items}</div>
</div>'''


def _render_tt_highlight_card(row):
    """Card for one highlight year — full Hanzi+Indo expansion."""
    mood = _row_mood(row)
    icon = {"good": "✓", "warn": "⚠", "neutral": "✦"}[mood]
    usia = re.sub(r"\*\*", "", row.get("usia", "")).strip()
    tahun = re.sub(r"\*\*", "", row.get("tahun", "")).strip()
    tahun_html = ""
    if tahun:
        if re.match(r"^[一-鿿]{2,3}$", tahun):
            tahun_html = f' <span class="tt-hl-gz hz">{_esc(tahun)}</span>'
        else:
            tahun_html = f' <span class="tt-hl-tahun">{_esc(tahun)}</span>'
    brief = _row_brief(row)
    return f'''<div class="tt-hl mood-{mood}">
  <div class="tt-hl-icon">{icon}</div>
  <div class="tt-hl-body">
    <div class="tt-hl-head"><strong class="tt-hl-usia">Usia {_esc(usia)}</strong>{tahun_html}</div>
    <div class="tt-hl-brief">{brief}</div>
  </div>
</div>'''


def _aggregate_periode_stats(rows):
    """Compute aggregated insights for a periode that support the Da Yun theme:
    - mood distribution (good/warn/neutral counts)
    - top-3 most frequent ten gods + bintang (with Indo gloss)
    - dominant 12-fase tendency
    Returns dict for template use.
    """
    if not rows: return {}
    moods = [_row_mood(r) for r in rows]
    mood_count = {"good": moods.count("good"), "warn": moods.count("warn"),
                  "neutral": moods.count("neutral")}
    # Frequency of ten gods + bintang
    from collections import Counter
    tg_freq = Counter()
    bx_freq = Counter()
    phase_freq = Counter()
    for r in rows:
        for hz in _split_hanzi_terms(r.get("ten_god", "")):
            tg_freq[hz] += 1
        for hz in _split_hanzi_terms(r.get("bintang", "")):
            bx_freq[hz] += 1
        st_match = re.match(r"^[一-鿿]+", _strip_inline_paren(r.get("status", "")))
        if st_match:
            phase_freq[st_match.group(0)] += 1
    top_tg = [(hz, cnt) for hz, cnt in tg_freq.most_common(3) if cnt >= 2]
    top_bx = [(hz, cnt) for hz, cnt in bx_freq.most_common(3) if cnt >= 2]
    return {
        "mood_count": mood_count,
        "top_tg": top_tg,
        "top_bx": top_bx,
        "phase_freq": phase_freq,
    }


def _render_tt_stats(stats, total_years):
    """Render aggregated stats panel for the periode."""
    if not stats: return ""
    mc = stats["mood_count"]
    # Mood distribution bar
    def pct(n): return round((n / max(total_years, 1)) * 100)
    bar_html = (
        f'<div class="tt-bar-wrap">'
        f'<div class="tt-bar-seg mood-good" style="flex: {mc["good"] or 0.001};"><span>{mc["good"]}</span></div>'
        f'<div class="tt-bar-seg mood-neutral" style="flex: {mc["neutral"] or 0.001};"><span>{mc["neutral"]}</span></div>'
        f'<div class="tt-bar-seg mood-warn" style="flex: {mc["warn"] or 0.001};"><span>{mc["warn"]}</span></div>'
        f'</div>'
        f'<div class="tt-bar-legend">'
        f'<span class="tt-bar-key mood-good">● Tahun Baik {pct(mc["good"])}%</span>'
        f'<span class="tt-bar-key mood-neutral">● Tahun Stabil {pct(mc["neutral"])}%</span>'
        f'<span class="tt-bar-key mood-warn">● Tahun Hati-hati {pct(mc["warn"])}%</span>'
        f'</div>'
    )
    # Top recurring terms (supports Da Yun thematic depth)
    tg_chips = ""
    if stats["top_tg"]:
        chips = "".join(
            f'<span class="tt-freq-chip mood-{_gloss_tg(hz)[1] or "neutral"}">'
            f'<span class="hz">{hz}</span>'
            f'<span class="tt-freq-indo">{_gloss_tg(hz)[0] or "—"}</span>'
            f'<span class="tt-freq-cnt">×{cnt}</span></span>'
            for hz, cnt in stats["top_tg"]
        )
        tg_chips = f'<div class="tt-freq-row"><span class="tt-freq-lbl">Sepuluh Dewa yang Sering Muncul:</span>{chips}</div>'
    bx_chips = ""
    if stats["top_bx"]:
        chips = "".join(
            f'<span class="tt-freq-chip mood-{_gloss_shensha(hz)[1] or "neutral"}">'
            f'<span class="hz">{hz}</span>'
            f'<span class="tt-freq-indo">{_gloss_shensha(hz)[0] or "—"}</span>'
            f'<span class="tt-freq-cnt">×{cnt}</span></span>'
            for hz, cnt in stats["top_bx"]
        )
        bx_chips = f'<div class="tt-freq-row"><span class="tt-freq-lbl">Bintang Khusus Berulang:</span>{chips}</div>'
    return f'''<div class="tt-stats">
  <div class="tt-stats-h">Profil Periode — Distribusi Mood {total_years} Tahun</div>
  {bar_html}
  {tg_chips}
  {bx_chips}
</div>'''


def _render_tt_periode_table(periode):
    """Periode summary card: header + Da Yun narrative + stats + timeline + 2-3 highlight years."""
    hdr = periode.get("header") or {}
    rows = periode.get("rows", [])
    # Da Yun narrative from ten god
    tg_hz = hdr.get("ten_god_hz") or ""
    da_yun_narrative = _DAYUN_NARRATIVE.get(tg_hz, "")
    narrative_html = ""
    if da_yun_narrative:
        tg_indo = hdr.get("ten_god_indo") or _gloss_tg(tg_hz)[0]
        # Convert "Periode X..." → "X..." (lowercase first letter) and prepend usia range
        body_text = re.sub(r"^Periode\s+", "", da_yun_narrative).strip()
        if body_text:
            body_text = body_text[0].lower() + body_text[1:]
        usia_range = hdr.get("usia_range") or ""
        m_usia = re.match(r"(\d+)\s*[-–—]\s*(\d+)", usia_range)
        if m_usia:
            prefix = f"Usia <strong>{m_usia.group(1)}</strong> sampai <strong>{m_usia.group(2)}</strong> adalah "
        else:
            prefix = "Periode ini adalah "
        narrative_html = f'''<div class="tt-narr">
  <div class="tt-narr-h">Arti — <span class="hz">{_esc(tg_hz)}</span> ({_esc(tg_indo)})</div>
  <div class="tt-narr-body">{prefix}{_esc(body_text)}</div>
</div>'''
    # Aggregated stats supporting the Da Yun theme
    stats = _aggregate_periode_stats(rows)
    stats_html = _render_tt_stats(stats, len(rows))
    # Highlights
    highlights = _pick_highlights(rows, limit=3)
    hl_html = ""
    if highlights:
        hl_cards = "".join(_render_tt_highlight_card(r) for r in highlights)
        hl_html = f'''<div class="tt-hl-section">
  <div class="tt-hl-eyebrow">Tahun-Tahun Penting dalam Periode Ini</div>
  <div class="tt-hl-grid">{hl_cards}</div>
</div>'''
    return f'''{_render_tt_periode_header(hdr)}
{narrative_html}
{stats_html}
{_render_tt_timeline(rows)}
{hl_html}'''


# ─────────────────────────────────────────────────────────────────────────
# KECOCOKAN SHIO — visual matchmaker (special-case renderer)
# ─────────────────────────────────────────────────────────────────────────

# Hanzi shio → (Indo name, canonical Hanzi for SVG seal)
_SHIO_MAP = {
    "鼠": ("Tikus", "鼠"),     "Tikus": ("Tikus", "鼠"),
    "牛": ("Kerbau", "牛"),    "Kerbau": ("Kerbau", "牛"),
    "虎": ("Macan", "虎"),     "Macan": ("Macan", "虎"), "Harimau": ("Macan", "虎"),
    "兔": ("Kelinci", "兔"),   "Kelinci": ("Kelinci", "兔"),
    "龍": ("Naga", "龍"),      "Naga": ("Naga", "龍"), "龙": ("Naga", "龍"),
    "蛇": ("Ular", "蛇"),      "Ular": ("Ular", "蛇"),
    "馬": ("Kuda", "馬"),      "Kuda": ("Kuda", "馬"), "马": ("Kuda", "馬"),
    "羊": ("Kambing", "羊"),   "Kambing": ("Kambing", "羊"), "Domba": ("Kambing", "羊"),
    "猴": ("Monyet", "猴"),    "Monyet": ("Monyet", "猴"),
    "雞": ("Ayam", "雞"),      "Ayam": ("Ayam", "雞"), "鸡": ("Ayam", "雞"),
    "狗": ("Anjing", "狗"),    "Anjing": ("Anjing", "狗"),
    "豬": ("Babi", "豬"),      "Babi": ("Babi", "豬"), "猪": ("Babi", "豬"),
}


import os as _os

# SVG Shio asset folder (V2 lightweight ~8.9KB per file)
_SVG_SHIO_DIR = r"C:\Users\sukam\OneDrive\Documents\Ramalan\SVG Shio\V2"
_SVG_CACHE = {}

# Indo name → file basename. Note: "Macan" file is "Harimau" — alias.
_SHIO_FILE_BASE = {
    "Macan": "Harimau", "Harimau": "Harimau",
    "Tikus": "Tikus", "Kerbau": "Kerbau",
    "Kelinci": "Kelinci", "Naga": "Naga", "Ular": "Ular",
    "Kuda": "Kuda", "Kambing": "Kambing", "Monyet": "Monyet",
    "Ayam": "Ayam", "Anjing": "Anjing", "Babi": "Babi",
}


def _load_shio_svg(indo_name, mood="neutral"):
    """Load + cache shio SVG. mood='good' → Merah, else → Hitam.
    Returns inline SVG markup with class for sizing."""
    base = _SHIO_FILE_BASE.get(indo_name)
    if not base:
        return '<div class="ks-shio-fallback">?</div>'
    color = "Merah" if mood == "good" else "Hitam"
    cache_key = (base, color)
    if cache_key in _SVG_CACHE:
        return _SVG_CACHE[cache_key]
    path = _os.path.join(_SVG_SHIO_DIR, f"{base}-{color}.svg")
    if not _os.path.isfile(path):
        _SVG_CACHE[cache_key] = '<div class="ks-shio-fallback">?</div>'
        return _SVG_CACHE[cache_key]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        _SVG_CACHE[cache_key] = '<div class="ks-shio-fallback">?</div>'
        return _SVG_CACHE[cache_key]
    # Strip XML declaration / DOCTYPE
    content = re.sub(r'<\?xml[^>]+\?>', '', content)
    content = re.sub(r'<!DOCTYPE[^>]+>', '', content).strip()
    # Inject class for sizing/styling
    content = re.sub(r'<svg([^>]*)>', r'<svg\1 class="ks-shio-svg">', content, count=1)
    _SVG_CACHE[cache_key] = content
    return content


def _resolve_shio(label):
    """From a cell like '🐑 **Kambing**' or '牛 Kerbau' or 'Shio lain', return
    (hanzi, indo_name, is_generic). is_generic=True if 'Shio lain'/'lainnya'."""
    if not label: return ("", "", False)
    s = re.sub(r"\*\*", "", label).strip()
    if re.search(r"\b(lain|lainnya|other)\b", s, re.IGNORECASE):
        return ("", "Shio Lainnya", True)
    # Strip leading emoji (we replace with seal SVG)
    s = re.sub(r"^[\s\U0001F400-\U0001F43F🐉]+\s*", "", s)
    # Find Hanzi or Indo word
    m_hz = re.search(r"([一-鿿])", s)
    m_indo = re.search(r"\b(Tikus|Kerbau|Macan|Harimau|Kelinci|Naga|Ular|Kuda|Kambing|Domba|Monyet|Ayam|Anjing|Babi)\b", s, re.IGNORECASE)
    if m_hz and m_hz.group(1) in _SHIO_MAP:
        indo, hz = _SHIO_MAP[m_hz.group(1)]
        return (hz, indo, False)
    if m_indo:
        key = m_indo.group(1).capitalize()
        if key in _SHIO_MAP:
            indo, hz = _SHIO_MAP[key]
            return (hz, indo, False)
    return ("", s.strip("*").strip(), False)


def _classify_shio_row(row_cells):
    """Returns dict with: hz, name, stars, is_avoid, label, note, mood."""
    if len(row_cells) < 2: return None
    hz, name, is_generic = _resolve_shio(row_cells[0])
    rating_cell = row_cells[1] if len(row_cells) > 1 else ""
    note = row_cells[2] if len(row_cells) > 2 else ""
    is_avoid = bool(re.search(r"⚠|hindari|jangan|pantang", rating_cell, re.IGNORECASE))
    stars = rating_cell.count("⭐") + rating_cell.count("★")
    label = re.sub(r"^[\s⭐★⚠️!️]+", "", rating_cell).strip()
    if is_avoid: mood = "warn"
    elif stars >= 4: mood = "good"
    elif stars >= 3: mood = "neutral"
    else: mood = "neutral"
    return {
        "hz": hz, "name": name, "is_generic": is_generic,
        "stars": stars, "is_avoid": is_avoid,
        "label": label, "note": note, "mood": mood,
    }


_PANTANGAN_PAT = re.compile(r"\b(pantangan|hindari|忌)\b", re.IGNORECASE)


def _parse_shio_table(lines):
    """Find pipe table + blockquote pantangan. Returns (ideals, avoids, others)."""
    rows = []
    in_table = False
    blockquote_buf = []
    in_quote = False
    blockquote_lines = []  # list of full blockquote texts
    for ln in lines:
        s = ln.strip()
        # Blockquote collection
        if s.startswith(">"):
            blockquote_buf.append(re.sub(r"^>\s*", "", s))
            in_quote = True
            continue
        elif in_quote:
            if blockquote_buf:
                blockquote_lines.append(" ".join(blockquote_buf))
            blockquote_buf = []
            in_quote = False
        # Table parsing
        if "|" not in s: continue
        cells = [c.strip() for c in s.strip().strip("|").split("|")]
        if re.match(r"^[\s\-:|]+$", "|".join(cells)):
            in_table = True; continue
        if not in_table: continue
        info = _classify_shio_row(cells)
        if info: rows.append(info)
    if blockquote_buf:
        blockquote_lines.append(" ".join(blockquote_buf))

    ideals = [r for r in rows if r["stars"] >= 4 and not r["is_avoid"]]
    avoids = [r for r in rows if r["is_avoid"]]
    others = [r for r in rows if r not in ideals and r not in avoids]

    # Also parse blockquote pantangan: extract shio names mentioned after "Hindari/Pantangan/忌"
    for bq in blockquote_lines:
        if not _PANTANGAN_PAT.search(bq): continue
        # Find all shio mentions (Hanzi or Indo)
        found_shio = []
        for hz_or_indo in re.findall(r"([一-鿿])|\b(Tikus|Kerbau|Macan|Harimau|Kelinci|Naga|Ular|Kuda|Kambing|Domba|Monyet|Ayam|Anjing|Babi)\b", bq, re.IGNORECASE):
            key = hz_or_indo[0] or hz_or_indo[1].capitalize()
            if key in _SHIO_MAP:
                indo, em = _SHIO_MAP[key]
                if not any(a["name"] == indo for a in avoids) and not any(f["name"] == indo for f in found_shio):
                    found_shio.append({
                        "hz": em, "name": indo, "is_generic": False,
                        "stars": 0, "is_avoid": True,
                        "label": "Hindari", "note": "", "mood": "warn",
                    })
        avoids.extend(found_shio)
    return ideals, avoids, others


def _render_shio_card(info, mood_override=None):
    mood = mood_override or info["mood"]
    stars_html = ""
    if info["stars"] > 0 and not info["is_avoid"]:
        on = info["stars"]; off = max(0, 5 - on)
        stars_html = (
            '<span class="ks-stars">'
            + "".join('<span class="ks-star on">★</span>' for _ in range(on))
            + "".join('<span class="ks-star off">★</span>' for _ in range(off))
            + '</span>'
        )
    label = info["label"] or ("Hindari" if info["is_avoid"] else "")
    note_html = f'<div class="ks-note">{gloss_text(info["note"])}</div>' if info["note"] else ""
    label_html = f'<div class="ks-label">{_esc(label)}</div>' if label else ""
    shio_img = _load_shio_svg(info["name"], mood=mood)
    return f'''<div class="ks-card mood-{mood}">
  <div class="ks-seal-wrap">{shio_img}</div>
  <div class="ks-body">
    <div class="ks-name">{_esc(info["name"])}</div>
    {stars_html}
    {label_html}
    {note_html}
  </div>
</div>'''


def _render_kecocokan_shio_section(lines):
    """Special renderer for KECOCOKAN PERNIKAHAN/SHIO sections.
    Returns HTML or None if no shio table found."""
    ideals, avoids, others = _parse_shio_table(lines)
    if not (ideals or avoids):
        return None
    parts = []
    parts.append('''<div class="ks-intro">
  <div class="ks-pi-icon">💕</div>
  <div class="ks-pi-body">
    <div class="ks-pi-eyebrow">PANDUAN JODOH · 婚 配 指 引</div>
    <div class="ks-pi-text">
      Bagian ini menunjukkan <strong>shio pasangan</strong> mana yang paling selaras dengan energi Anda
      (untuk pernikahan & hubungan jangka panjang) dan mana yang sebaiknya dihati-hati.
      Petunjuk ini bersifat <em>kecenderungan</em> — bukan vonis. Komunikasi & komitmen tetap penentu utama.
    </div>
  </div>
</div>''')

    if ideals:
        cards = "".join(_render_shio_card(r, "good") for r in ideals)
        parts.append(f'''<div class="ks-block ks-good">
  <div class="ks-block-h"><span class="ks-block-icon">✓</span><span class="ks-block-id">Shio Pasangan Ideal</span><span class="ks-block-hz">宜 配 (Yi Pei)</span></div>
  <div class="ks-grid">{cards}</div>
</div>''')

    if avoids:
        cards = "".join(_render_shio_card(r, "warn") for r in avoids)
        parts.append(f'''<div class="ks-block ks-warn">
  <div class="ks-block-h"><span class="ks-block-icon">⚠</span><span class="ks-block-id">Shio yang Sebaiknya Dihindari</span><span class="ks-block-hz">忌 配 (Ji Pei)</span></div>
  <div class="ks-grid">{cards}</div>
</div>''')

    if others:
        chips_specific = []
        chip_generic = ""
        for r in others:
            if r.get("is_generic"):
                # "Shio lain" catch-all: explain what it means
                chip_generic = (
                    f'<span class="ks-other-chip ks-oc-generic">'
                    f'🌐 <strong>Shio lainnya</strong> (yang tidak tersebut di atas) · '
                    f'{_esc(r["label"] or "Kecocokan Biasa")}</span>'
                )
            else:
                chips_specific.append(
                    f'<span class="ks-other-chip">'
                    f'<span class="ks-oc-hz hz">{r.get("hz","")}</span>'
                    f'<strong>{_esc(r["name"])}</strong> · {_esc(r["label"] or "Sedang")}</span>'
                )
        chips_html = "".join(chips_specific) + chip_generic
        parts.append(f'''<div class="ks-others-block">
  <div class="ks-others-h">
    <span class="ks-others-icon">◐</span>
    <span class="ks-others-id">Shio Netral</span>
    <span class="ks-others-hz">中 配 (Zhong Pei)</span>
  </div>
  <div class="ks-others-desc">Tidak terlalu cocok, tidak juga buruk — kecocokan tergantung faktor pribadi (komunikasi, komitmen, kompatibilitas BaZi).</div>
  <div class="ks-others-chips">{chips_html}</div>
</div>''')

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────
# KARIR & PROFESI — visual bidang cards + ranked priority list
# ─────────────────────────────────────────────────────────────────────────

# Keyword → emoji icon for profession/industry
_BIDANG_ICONS = [
    (re.compile(r"pendidikan|guru|akademik|pengajar|sastra|tulis|jurnal|reporter|literasi|akademisi|peneliti", re.I), "📚"),
    (re.compile(r"seni|musik|musisi|artis|penyanyi|lukis|desain|kreatif|teater|drama|sirkus|pertunjuk|hiburan|film|fotograf|optik|kecantikan|salon", re.I), "🎨"),
    (re.compile(r"hukum|pengacara|advokat|notaris|legal", re.I), "⚖"),
    (re.compile(r"keuangan|akuntan|bank|investasi|finansial", re.I), "💰"),
    (re.compile(r"wirausaha|bisnis|usaha|entrepreneur|mandiri|konsultan", re.I), "💼"),
    (re.compile(r"teknologi|mesin|mekanik|otomotif|engineering|insinyur|industri", re.I), "⚙"),
    (re.compile(r"kesehatan|dokter|perawat|medis|klinik|rumah\s+sakit|pengobatan", re.I), "🏥"),
    (re.compile(r"perdagangan|sales|trading|niaga|toko|ekspor|impor|pedagang|penjual|makelar|perantara", re.I), "🛒"),
    (re.compile(r"marketing|periklanan|promosi|public\s+relation", re.I), "📢"),
    (re.compile(r"agama|spiritual|rohani|religius", re.I), "🙏"),
    (re.compile(r"olahraga|atlet|sports", re.I), "🏃"),
    (re.compile(r"maritim|kapal|pelaut|nelayan|perikanan|pelayaran|pelabuhan|kelautan", re.I), "⚓"),
    (re.compile(r"makanan|kuliner|minuman|restoran|warung|cafe", re.I), "🍱"),
    (re.compile(r"konstruksi|bangunan|properti|real\s+estate|kontraktor|arsitek", re.I), "🏗"),
    (re.compile(r"transportasi|pemandu\s+wisata|travel|logistik|kurir", re.I), "🧭"),
    (re.compile(r"keamanan|kebersihan|pemadam|militer|polisi|tentara|protokoler", re.I), "🛡"),
    (re.compile(r"penerbangan|pilot", re.I), "✈"),
    (re.compile(r"pertambangan|logam|baja|tambang", re.I), "⛏"),
    (re.compile(r"agrikultur|pertanian|peternakan|kebun", re.I), "🌾"),
    (re.compile(r"teknologi\s+informasi|komputer|software|programmer|developer", re.I), "💻"),
]


def _bidang_icon(text):
    for pat, ic in _BIDANG_ICONS:
        if pat.search(text or ""): return ic
    return "✦"


def _parse_karir_md(lines):
    """Parse karir MD content. Returns dict with:
      - priority_rows: [(stars, bidang, alasan)] from "Prioritas|Bidang|Alasan" tables
      - category_rows: [(kategori, bidang_str)] from "Kategori|Bidang" tables
      - bullet_groups: [(group_label, [items])] from `**Group:**` + bullets
      - label_sections: [(label, text)] from `**Label:** body` paragraphs (Karir cocok/Potensi besar/Peringatan)
      - free_paragraphs: leftover plain paragraphs (non-Hanzi)
    """
    out = {
        "priority_rows": [], "category_rows": [],
        "bullet_groups": [], "label_sections": [],
        "free_paragraphs": [],
    }
    # First pass: find pipe-tables, classify by header
    i = 0
    n = len(lines)
    consumed = [False] * n
    while i < n:
        ln = lines[i]
        if "|" in ln and i+1 < n and re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", lines[i+1]):
            # Detect table type by header
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            header_lower = [h.lower() for h in header]
            is_priority = any("prioritas" in h or "rating" in h for h in header_lower)
            is_category = any("kategori" in h or "category" in h for h in header_lower)
            consumed[i] = True
            consumed[i+1] = True
            j = i + 2
            while j < n and "|" in lines[j]:
                cells = [re.sub(r"\*\*", "", c).strip() for c in lines[j].strip().strip("|").split("|")]
                consumed[j] = True
                if is_priority and len(cells) >= 2:
                    stars = cells[0].count("⭐") + cells[0].count("★")
                    bidang = cells[1] if len(cells) > 1 else ""
                    alasan = cells[2] if len(cells) > 2 else ""
                    out["priority_rows"].append((stars, bidang, alasan))
                elif is_category and len(cells) >= 2:
                    kategori = cells[0]
                    bidang_str = " | ".join(cells[1:])
                    out["category_rows"].append((kategori, bidang_str))
                j += 1
            i = j
            continue
        i += 1
    # Second pass: bullet groups + label sections + paragraphs
    cur_group = None
    cur_bullets = []
    pending_label = None
    para_buf = []

    def flush_group():
        nonlocal cur_group, cur_bullets
        if cur_group and cur_bullets:
            out["bullet_groups"].append((cur_group, list(cur_bullets)))
        cur_group, cur_bullets = None, []

    def flush_para():
        nonlocal para_buf, pending_label
        if not para_buf: return
        text = " ".join(para_buf).strip()
        if text:
            if pending_label:
                out["label_sections"].append((pending_label, text))
                pending_label = None
            else:
                # Skip Hanzi-dominant
                han = sum(1 for c in text if "一" <= c <= "鿿")
                latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
                if han > 4 and han > latn * 1.5:
                    para_buf = []; return
                # Skip caption-style lines (ending with ":") — likely intro for a
                # table/list that's already been consumed elsewhere.
                if re.search(r":\s*$", text):
                    para_buf = []; return
                out["free_paragraphs"].append(text)
        para_buf = []

    for idx, ln in enumerate(lines):
        if consumed[idx]: continue
        s = ln.strip()
        if not s or s == "---":
            flush_para()
            continue
        if s.startswith(">"):
            flush_para()
            continue  # skip blockquote (raw transkripsi typically)
        if s.startswith("###") or s.startswith("####"):
            flush_para(); flush_group()
            continue
        if s.startswith("◎") or _is_predominantly_hanzi_local(s):
            continue
        # Bold-label headers
        m_lbl = re.match(r"^\*\*([^*]+?)\*\*\s*:?\s*$", s)
        if m_lbl:
            flush_para(); flush_group()
            label = m_lbl.group(1).strip()
            label = re.sub(r"^[\W_]+\s*", "", label)
            label = re.sub(r":\s*$", "", label)
            # Distinguish: bullet-group label (will have bullets next) vs body label (paragraph next)
            cur_group = label
            pending_label = label
            continue
        # Bullet
        mb = re.match(r"^[-*]\s+(.+)$", s)
        if mb:
            flush_para()
            content = re.sub(r"\*\*([^*]+)\*\*", r"\1", mb.group(1).strip())
            if cur_group:
                cur_bullets.append(content)
                pending_label = None
            else:
                # bullet without group → standalone
                out["bullet_groups"].append((None, [content]))
            continue
        # Inline label "**Label:** body"
        m_inline = re.match(r"^\*\*([^*]+?)\*\*\s*[:：]\s*(.+)$", s)
        if m_inline:
            flush_para(); flush_group()
            out["label_sections"].append((m_inline.group(1).strip(), m_inline.group(2).strip()))
            continue
        # Plain paragraph
        para_buf.append(re.sub(r"\*\*([^*]+)\*\*", r"\1", s))
    flush_para(); flush_group()
    return out


def _is_predominantly_hanzi_local(text):
    han = sum(1 for c in text if "一" <= c <= "鿿")
    latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return han > 4 and han > latn * 1.5


def _render_priority_card(rank_idx, stars, bidang, alasan):
    on = stars; off = max(0, 5 - on)
    star_html = (
        '<span class="kr-stars">'
        + "".join('<span class="kr-star on">★</span>' for _ in range(on))
        + "".join('<span class="kr-star off">★</span>' for _ in range(off))
        + '</span>'
    )
    icon = _bidang_icon(bidang)
    mood = "good" if stars >= 4 else ("neutral" if stars >= 3 else "warn")
    alasan_html = f'<div class="kr-pri-alasan">{gloss_text(alasan)}</div>' if alasan else ""
    return f'''<div class="kr-pri-card mood-{mood}">
  <div class="kr-pri-rank">{rank_idx:02d}</div>
  <div class="kr-pri-icon">{icon}</div>
  <div class="kr-pri-body">
    <div class="kr-pri-bidang">{gloss_text(bidang)}</div>
    {star_html}
    {alasan_html}
  </div>
</div>'''


def _render_category_card(kategori, bidang_str):
    icon = _bidang_icon(kategori + " " + bidang_str)
    # Split bidang by common separators
    bidang_items = [b.strip() for b in re.split(r"[,;|、，]", bidang_str) if b.strip()]
    chips = "".join(
        f'<span class="kr-cat-chip">{_bidang_icon(b)} {gloss_text(b)}</span>'
        for b in bidang_items
    )
    kategori_clean = re.sub(r"\*\*", "", kategori)
    kategori_html = gloss_text(kategori_clean)
    return f'''<div class="kr-cat-card">
  <div class="kr-cat-head">
    <span class="kr-cat-icon">{icon}</span>
    <span class="kr-cat-name">{kategori_html}</span>
  </div>
  <div class="kr-cat-chips">{chips}</div>
</div>'''


def _render_bidang_chip_grid(items):
    """Generic bidang list (no category) → icon chip grid."""
    chips = "".join(
        f'<div class="kr-chip"><span class="kr-chip-icon">{_bidang_icon(it)}</span>'
        f'<span class="kr-chip-text">{gloss_text(it)}</span></div>'
        for it in items
    )
    return f'<div class="kr-chip-grid">{chips}</div>'


def _render_label_callout(label, text):
    low = label.lower()
    if any(k in low for k in ("peringatan", "waspada", "hindari", "hati", "risiko")):
        mood, icon = "warn", "⚠"
    elif any(k in low for k in ("potensi", "kekuatan", "kelebihan", "saran", "rekomendasi", "cocok", "ideal", "terbaik")):
        mood, icon = "good", "✓"
    else:
        mood, icon = "info", "💡"
    return f'''<div class="kr-call mood-{mood}">
  <div class="kr-call-h"><span class="kr-call-icon">{icon}</span><span class="kr-call-label">{_esc(label)}</span></div>
  <div class="kr-call-text">{gloss_text(text)}</div>
</div>'''


def _find_istana_karir_interpretasi(all_sections):
    """Look for sister section ISTANA PEKERJAAN (官祿宮) — Zi Wei palace context for karir."""
    if not all_sections: return ""
    for s in all_sections:
        t = (s.get("title") or "").upper()
        if "ISTANA" in t and ("PEKERJAAN" in t or "KARIR" in t or "KARIER" in t):
            for sub in s.get("sub", []):
                if "INTERPRETASI" in (sub.get("title") or "").upper():
                    text, _ = _extract_interpretasi(sub.get("lines", []))
                    if text: return text
            text, _ = _extract_interpretasi(s.get("lines", []))
            if text: return text
        if "官祿" in (s.get("title") or ""):
            for sub in s.get("sub", []):
                if "INTERPRETASI" in (sub.get("title") or "").upper():
                    text, _ = _extract_interpretasi(sub.get("lines", []))
                    if text: return text
    return ""


def _render_karir_section(lines, all_sections=None):
    """Render KARIR / PROFESI page with visual bidang cards + ranked priority + callouts."""
    parsed = _parse_karir_md(lines)
    has_data = bool(parsed["priority_rows"] or parsed["category_rows"]
                    or parsed["bullet_groups"] or parsed["label_sections"])
    if not has_data: return None

    parts = []

    # Page intro
    parts.append('''<div class="kr-page-intro">
  <div class="kr-pi-icon">💼</div>
  <div class="kr-pi-body">
    <div class="kr-pi-eyebrow">PANDUAN KARIR · 事 業 指 引</div>
    <div class="kr-pi-text">
      Bagian ini merangkum <strong>profesi & bidang yang paling selaras</strong> dengan elemen kelahiran, bintang istana karir, dan kekuatan alami Anda.
      Petunjuk ini bersifat <em>kecenderungan kosmik</em> — pilihan akhir tetap di tangan Anda.
    </div>
  </div>
</div>''')

    # Priority ranking (Lin Ruyi style — table prioritas)
    if parsed["priority_rows"]:
        cards = "".join(
            _render_priority_card(i+1, *row)
            for i, row in enumerate(parsed["priority_rows"])
        )
        parts.append(f'''<div class="kr-pri-section">
  <div class="kr-h"><span class="kr-h-icon">🎯</span><span class="kr-h-id">Bidang Karir Berdasarkan Prioritas</span></div>
  <div class="kr-pri-stack">{cards}</div>
</div>''')

    # Category cards (Li Yuanxiang style — table kategori)
    if parsed["category_rows"]:
        cards = "".join(_render_category_card(k, b) for k, b in parsed["category_rows"])
        parts.append(f'''<div class="kr-cat-section">
  <div class="kr-h"><span class="kr-h-icon">📂</span><span class="kr-h-id">Kategori Profesi Cocok</span></div>
  <div class="kr-cat-grid">{cards}</div>
</div>''')

    # Bullet groups (e.g. "Kelompok Pertama:" + bullets)
    if parsed["bullet_groups"]:
        for label, items in parsed["bullet_groups"]:
            if not items: continue
            head = ""
            if label and not (KEKUATAN_LBL_KARIR.search(label) if False else False):
                head = (f'<div class="kr-h kr-h-sub">'
                        f'<span class="kr-h-icon">▸</span>'
                        f'<span class="kr-h-id">{_esc(label)}</span></div>')
            parts.append(f'''<div class="kr-bidang-block">{head}{_render_bidang_chip_grid(items)}</div>''')

    # Label sections (Karir cocok / Potensi besar / Peringatan)
    if parsed["label_sections"]:
        callouts = "".join(_render_label_callout(l, t) for l, t in parsed["label_sections"])
        parts.append(f'<div class="kr-call-stack">{callouts}</div>')

    # Free paragraphs
    if parsed["free_paragraphs"]:
        for p in parsed["free_paragraphs"]:
            parts.append(f'<div class="gs-para">{gloss_text(p)}</div>')

    return "\n".join(parts)


KEKUATAN_LBL_KARIR = re.compile(r"\b(kekuatan|kelebihan)\b", re.I)


# ─────────────────────────────────────────────────────────────────────────
# BINTANG KHUSUS (神煞 — ShenSha) — visual cards per bintang
# ─────────────────────────────────────────────────────────────────────────

_BX_TITLE_HEAD_PAT = re.compile(
    r"^[【\[]?\s*([一-鿿]+)\s*[】\]]?\s*[\(（]\s*([^—–\-)）]+?)\s*[—–\-]\s*([^)）]+?)\s*[\)）]\s*$"
)


def _parse_bintang_title(title):
    """Parse bintang sub title like '驛馬】 (Yima — Kuda Pengantar Pesan)'.
    Returns (hanzi, pinyin, indo)."""
    if not title: return ("", "", "")
    s = title.strip()
    m = _BX_TITLE_HEAD_PAT.match(s)
    if m:
        return (m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
    # Fallback: just extract Hanzi prefix
    m_hz = re.match(r"^[【\[]?\s*([一-鿿]+)", s)
    hz = m_hz.group(1) if m_hz else ""
    rest = s[m_hz.end():] if m_hz else s
    # Try to split rest by — or -
    rest = rest.strip("】]) (（）—–-").strip()
    parts = re.split(r"\s*[—–\-]\s*", rest, maxsplit=1)
    pinyin = parts[0].strip() if parts else ""
    indo = parts[1].strip() if len(parts) > 1 else ""
    return (hz, pinyin, indo)


def _parse_bintang_body(lines):
    """Walk a bintang sub's body lines, classify as interpretasi paragraph + bullets + makna blockquote.
    Returns dict: {interp: str, bullets: [str], makna: str}."""
    out = {"interp": "", "bullets": [], "makna": ""}
    interp_buf = []
    pending_interp = False
    bq_buf = []
    in_quote = False

    def flush_interp():
        nonlocal interp_buf, pending_interp
        if interp_buf and pending_interp:
            out["interp"] = " ".join(interp_buf).strip()
        interp_buf = []
        pending_interp = False

    for ln in lines:
        s = ln.strip()
        if not s or s == "---": continue
        # Skip Hanzi-dominant raw transkripsi
        if _is_predominantly_hanzi_local(s): continue
        # Blockquote (often "💡 Makna:" closing)
        if s.startswith(">"):
            in_quote = True
            bq_buf.append(re.sub(r"^>\s*", "", s))
            continue
        elif in_quote:
            in_quote = False
            text = " ".join(bq_buf)
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()
            text = re.sub(r"^[\W_]*(makna|💡)[^:]*:?\s*", "", text, flags=re.IGNORECASE).strip()
            if text and not _is_predominantly_hanzi_local(text):
                out["makna"] = text
            bq_buf = []
        # Inline **Interpretasi:** body
        m_inline = re.match(r"^\*\*\s*(?:🔍\s*)?(?:interpretasi|tafsir|makna|penjelasan)[^*]*\*\*\s*:?\s*(.+)$", s, re.IGNORECASE)
        if m_inline:
            out["interp"] = re.sub(r"\*\*([^*]+)\*\*", r"\1", m_inline.group(1).strip())
            pending_interp = False
            continue
        # Standalone **Interpretasi:** label → next paragraphs are interpretasi
        m_lbl = re.match(r"^\*\*\s*(?:🔍\s*)?(?:interpretasi|tafsir|makna|penjelasan)[^*]*\*\*\s*:?\s*$", s, re.IGNORECASE)
        if m_lbl:
            pending_interp = True
            continue
        # Bullet
        mb = re.match(r"^[-*]\s+(.+)$", s)
        if mb:
            content = re.sub(r"\*\*([^*]+)\*\*", r"\1", mb.group(1)).strip()
            out["bullets"].append(content)
            continue
        # Paragraph
        if pending_interp or not out["interp"]:
            interp_buf.append(re.sub(r"\*\*([^*]+)\*\*", r"\1", s))
            pending_interp = True
    if in_quote and bq_buf:
        text = " ".join(bq_buf)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()
        text = re.sub(r"^[\W_]*(makna|💡)[^:]*:?\s*", "", text, flags=re.IGNORECASE).strip()
        if text and not _is_predominantly_hanzi_local(text):
            out["makna"] = text
    flush_interp()
    return out


def _shensha_seal_svg(hz, mood):
    """Lightweight SVG seal for shensha — circular border + Hanzi character."""
    if not hz:
        return '<div class="bx-seal-fallback">✦</div>'
    return (
        f'<svg viewBox="0 0 40 40" class="bx-seal-svg" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="20" cy="20" r="18" fill="currentColor" opacity="0.10"/>'
        f'<circle cx="20" cy="20" r="17" fill="none" stroke="currentColor" stroke-width="1.2"/>'
        f'<circle cx="20" cy="20" r="13.5" fill="none" stroke="currentColor" stroke-width="0.4" opacity="0.5"/>'
        f'<text x="20" y="28" text-anchor="middle" font-family="Noto Serif TC,serif" '
        f'font-size="20" font-weight="700" fill="currentColor">{hz}</text>'
        f'</svg>'
    )


def _render_bintang_card(idx, sub):
    title = sub.get("title", "")
    hz, pinyin, indo = _parse_bintang_title(title)
    _, mood = _gloss_shensha(hz)
    if not mood: mood = "neutral"
    body = _parse_bintang_body(sub.get("lines", []))

    # Body content
    interp_html = ""
    if body["interp"]:
        interp_html = f'<div class="bx-interp">{gloss_text(body["interp"])}</div>'
    bullets_html = ""
    if body["bullets"]:
        items = "".join(f"<li>{gloss_text(b)}</li>" for b in body["bullets"])
        bullets_html = f'<ul class="bx-bullets">{items}</ul>'
    makna_html = ""
    if body["makna"]:
        makna_html = (f'<div class="bx-makna"><span class="bx-makna-icon">💡</span>'
                      f'<span class="bx-makna-text">{gloss_text(body["makna"])}</span></div>')

    seal = _shensha_seal_svg(hz, mood)
    pinyin_html = f'<span class="bx-pinyin">{_esc(pinyin)}</span>' if pinyin else ""
    indo_html = f'<span class="bx-indo">{_esc(indo)}</span>' if indo else ""
    return f'''<div class="bx-card mood-{mood}">
  <div class="bx-head">
    <div class="bx-rank">{idx:02d}</div>
    <div class="bx-seal-wrap">{seal}</div>
    <div class="bx-name">
      <span class="bx-hz hz">{_esc(hz)}</span>
      {pinyin_html}
      {indo_html}
    </div>
  </div>
  <div class="bx-body">
    {interp_html}
    {bullets_html}
    {makna_html}
  </div>
</div>'''


def _render_bintang_khusus_section(lines, subs):
    """Render BINTANG KHUSUS / SHENSHA section. Each H3 sub = one bintang card."""
    if not subs: return None
    parts = []
    parts.append('''<div class="bx-page-intro">
  <div class="bx-pi-icon">⭐</div>
  <div class="bx-pi-body">
    <div class="bx-pi-eyebrow">PANDUAN BINTANG KHUSUS · 神 煞 指 引</div>
    <div class="bx-pi-text">
      <strong>Bintang Khusus (神煞 — Shen Sha)</strong> adalah energi/pengaruh khusus dari peta langit yang
      memberi corak unik pada hidup Anda. Bisa berupa <em>pelindung</em> (mis. 龍德, 天乙),
      <em>tema khusus</em> (mis. 桃花 pesona, 驛馬 mobilitas), atau <em>peringatan</em> (mis. 白虎, 羊刃).
      Berikut bintang-bintang yang aktif dalam bagan kelahiran Anda.
    </div>
  </div>
</div>''')
    cards = "".join(_render_bintang_card(i+1, sub) for i, sub in enumerate(subs))
    parts.append(f'<div class="bx-stack">{cards}</div>')
    return "\n".join(parts)


_BX_TITLE_PAT = re.compile(r"\b(bintang\s+(khusus|spiritual)|shen\s*sha|神煞)\b", re.IGNORECASE)


def _is_bintang_khusus(title_id, title_hz):
    combined = f"{title_id or ''} {title_hz or ''}"
    return bool(_BX_TITLE_PAT.search(combined))


_KR_TITLE_PAT = re.compile(r"\b(karir|karier|profesi|pekerjaan|事業|官祿|rekomendasi\s+karier)\b", re.IGNORECASE)


def _is_karir_page(title_id, title_hz):
    combined = f"{title_id or ''} {title_hz or ''}"
    if not _KR_TITLE_PAT.search(combined): return False
    # Exclude ISTANA-only Zi Wei palace pages (keep palace renderer for those)
    if "ISTANA" in combined.upper(): return False
    return True


_KS_TITLE_PAT = re.compile(r"\b(kecocokan|pernikahan|pasangan|jodoh|婚配)\b", re.IGNORECASE)


def _is_kecocokan_shio(title_id, title_hz, lines):
    combined = f"{title_id or ''} {title_hz or ''}"
    if not _KS_TITLE_PAT.search(combined):
        return False
    # Also require a shio table (heuristic) — at least 1 line with emoji + star or ⚠
    for ln in lines:
        if "|" in ln and ("⭐" in ln or "★" in ln or "⚠" in ln):
            return True
    return False


def _find_pernikahan_interpretasi(all_sections):
    """Look for sister section PERNIKAHAN (夫妻宮 / 婚姻) — separate from KECOCOKAN —
    that often contains rich Indo interpretasi (Tanlang/profil pasangan/peringatan).
    Returns (text, profil_bullets, peringatan_bullets) — fallback empty."""
    if not all_sections: return ("", [], [])
    for s in all_sections:
        t = (s.get("title") or "").upper()
        if "KECOCOKAN" in t: continue
        if not (("PERNIKAHAN" in t) or ("夫妻" in (s.get("title") or "")) or ("ASMARA" in t)):
            continue
        # Walk subs first (Interpretasi sub takes priority)
        target_lines = None
        for sub in s.get("sub", []):
            if "INTERPRETASI" in (sub.get("title") or "").upper():
                target_lines = sub.get("lines", []); break
        if target_lines is None:
            target_lines = s.get("lines", [])
        # Extract opening paragraph (skip Hanzi-dominant)
        text, _ = _extract_interpretasi(target_lines)
        # Extract bullets under bold-label headers (Profil Pasangan Ideal / Peringatan Penting)
        profil, peringatan = [], []
        cur_bucket = None
        for ln in target_lines:
            ls = ln.strip()
            if not ls: continue
            m_lbl = re.match(r"^\*\*([^*]+?)\*\*\s*:?\s*$", ls)
            if m_lbl:
                lab = m_lbl.group(1).strip().lower()
                if "profil" in lab and "pasangan" in lab: cur_bucket = "profil"
                elif "peringatan" in lab or "waspada" in lab or "hati" in lab: cur_bucket = "peringatan"
                else: cur_bucket = None
                continue
            mb = re.match(r"^[-*]\s+(.+)$", ls)
            if mb and cur_bucket:
                content = re.sub(r"\*\*([^*]+)\*\*", r"\1", mb.group(1)).strip()
                if cur_bucket == "profil": profil.append(content)
                elif cur_bucket == "peringatan": peringatan.append(content)
        return (text or "", profil, peringatan)
    return ("", [], [])


def _render_pernikahan_interp_card(text, profil, peringatan):
    """Render merged interpretasi card for shio page (when MD has separate PERNIKAHAN section)."""
    if not (text or profil or peringatan):
        return ""
    text_html = f'<div class="ks-pmi-text">{gloss_text(text)}</div>' if text else ""
    profil_html = ""
    if profil:
        items = "".join(f"<li>{gloss_text(p)}</li>" for p in profil)
        profil_html = (
            f'<div class="ks-pmi-block ks-pmi-good">'
            f'<div class="ks-pmi-h"><span class="ks-pmi-icon">💕</span>Profil Pasangan Ideal</div>'
            f'<ul>{items}</ul></div>'
        )
    peringatan_html = ""
    if peringatan:
        items = "".join(f"<li>{gloss_text(p)}</li>" for p in peringatan)
        peringatan_html = (
            f'<div class="ks-pmi-block ks-pmi-warn">'
            f'<div class="ks-pmi-h"><span class="ks-pmi-icon">⚠</span>Peringatan Penting</div>'
            f'<ul>{items}</ul></div>'
        )
    cols_html = ""
    if profil_html or peringatan_html:
        cols_html = f'<div class="ks-pmi-cols">{profil_html}{peringatan_html}</div>'
    return f'''<div class="ks-pernikahan-merge">
  <div class="ks-pmi-eyebrow">INTERPRETASI PERNIKAHAN · 夫 妻 宮</div>
  {text_html}
  {cols_html}
</div>'''


_TT_TITLE_PAT = re.compile(r"\b(tabel\s+(aliran|nasib)\s+tahunan|tabel.*流年|流年鑑易)", re.IGNORECASE)


def _is_tabel_tahunan(title_id, title_hz):
    combined = f"{title_id or ''} {title_hz or ''}"
    return bool(_TT_TITLE_PAT.search(combined))


_TT_GENERIC_INTRO = '''<div class="tt-page-intro">
  <div class="tt-pi-icon">📅</div>
  <div class="tt-pi-body">
    <div class="tt-pi-eyebrow">TENTANG TABEL INI · 關 於 此 表</div>
    <div class="tt-pi-text">
      Tabel ini memetakan <strong>nasib Anda per tahun</strong> dengan menggabungkan dua siklus:
      <strong>Periode Besar (大運 — Da Yun)</strong> yang berdurasi 10 tahun, dan
      <strong>Tahunan (流年 — Liu Nian)</strong> yang berganti tiap tahun.
      Setiap baris = 1 tahun usia. Untuk membantu pembacaan, kami sajikan
      <em>tema periode</em>, <em>distribusi mood 10 tahun</em>, <em>linimasa per usia</em>,
      dan <em>3 tahun paling penting</em> di setiap periode.
    </div>
  </div>
</div>'''


def _render_tabel_tahunan_page(num, title_id, title_hz, section_label, lines, subject_name):
    periodes = _parse_tabel_md(lines)
    if not periodes:
        body = callout("Data tabel tahunan tidak terbaca dari sumber MD.", variant="warn", icon="⚠")
        return page_shell(num, title_id, title_hz, section_label, body, subject_name)

    # Per rule: setiap bab kalau MD ada interpretasi, tulis di paling atas
    interp_text, _ = _extract_interpretasi(lines)
    interp_html = ""
    if interp_text:
        interp_html = f'''<div class="gs-interp">
  <div class="gs-interp-icon">💡</div>
  <div class="gs-interp-body">
    <div class="gs-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div>
    <div class="gs-interp-text">{_esc(interp_text)}</div>
  </div>
</div>'''

    parts = []
    if interp_html: parts.append(interp_html)
    parts.append(_TT_GENERIC_INTRO)
    for p in periodes:
        parts.append(_render_tt_periode_table(p))
    body = "\n".join(parts)
    return page_shell(num, title_id, title_hz, section_label, body, subject_name)


def render_generic_page(num: int, title_id: str, title_hz: str, section_label: str,
                        lines, subject_name: str = "", all_sections=None, section=None) -> str:
    """Generic page for any section topic — life area, unknown, etc.
    `all_sections`: full deep_sections list for cross-section enrichment.
    `section`: this section's full deep dict (with 'sub' array) — used for bintang cards.
    """
    # Special-case: TABEL ALIRAN TAHUNAN → custom Indo-friendly renderer with glossary
    if _is_tabel_tahunan(title_id, title_hz):
        return _render_tabel_tahunan_page(num, title_id, title_hz, section_label, lines, subject_name)

    # Special-case: BINTANG KHUSUS / SHENSHA → cards per bintang
    if _is_bintang_khusus(title_id, title_hz):
        subs = section.get("sub", []) if section else []
        bx_html = _render_bintang_khusus_section(lines, subs)
        if bx_html:
            interp_text, _ = _extract_interpretasi(lines)
            interp_html = ""
            if interp_text:
                interp_html = f'<div class="gs-interp"><div class="gs-interp-icon">💡</div><div class="gs-interp-body"><div class="gs-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div><div class="gs-interp-text">{_esc(interp_text)}</div></div></div>'
            body = "\n".join(p for p in [interp_html, bx_html] if p)
            return page_shell(num, title_id, title_hz, section_label, body, subject_name)

    # Special-case: KARIR / PROFESI → visual bidang grid + ranked priority
    if _is_karir_page(title_id, title_hz):
        kr_html = _render_karir_section(lines, all_sections=all_sections)
        if kr_html:
            interp_text, _skip = _extract_interpretasi(lines)
            if not interp_text:
                interp_text = _find_istana_karir_interpretasi(all_sections)
            interp_html = ""
            if interp_text:
                interp_html = f'<div class="gs-interp"><div class="gs-interp-icon">💡</div><div class="gs-interp-body"><div class="gs-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div><div class="gs-interp-text">{_esc(interp_text)}</div></div></div>'
            body = "\n".join(p for p in [interp_html, kr_html] if p)
            return page_shell(num, title_id, title_hz, section_label, body, subject_name)

    # Special-case: KECOCOKAN PERNIKAHAN/SHIO → visual matchmaker
    if _is_kecocokan_shio(title_id, title_hz, lines):
        ks_html = _render_kecocokan_shio_section(lines)
        if ks_html:
            # Filter from generic flow:
            # 1) ALL pipe-tables (header+separator+rows) — shio data already in cards
            # 2) Blockquotes whose body is just the shio category label (Pantangan / Shio yang Cocok / 宜 / 忌)
            #    — already consumed by parser → would duplicate
            # Keep informational blockquotes (Saran / 💡) and paragraph sections (Risiko/Berkah bullets)
            filtered = []
            i = 0
            n = len(lines)
            _CONSUMED_BQ_PAT = re.compile(
                r"\b(pantangan|shio\s+yang\s+cocok|shio\s+ideal|宜\b|忌\b|hindari\s+pasangan)\b",
                re.IGNORECASE,
            )
            _KEEP_BQ_PAT = re.compile(r"\b(saran|💡|tips|nasihat|catatan)\b", re.IGNORECASE)
            while i < n:
                ln = lines[i]
                # Pipe-table start: header → separator pattern
                if "|" in ln and i+1 < n and re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", lines[i+1]):
                    i += 2
                    while i < n and "|" in lines[i]:
                        i += 1
                    continue
                # Blockquote: read all consecutive `> ` lines, decide drop vs keep
                if ln.lstrip().startswith(">"):
                    bq_start = i
                    bq_buf = []
                    while i < n and lines[i].lstrip().startswith(">"):
                        bq_buf.append(re.sub(r"^>\s*", "", lines[i].strip()))
                        i += 1
                    bq_text = " ".join(bq_buf)
                    bq_clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", bq_text).strip()
                    # Drop if it's a consumed label and NOT actionable advice
                    if _CONSUMED_BQ_PAT.search(bq_clean) and not _KEEP_BQ_PAT.search(bq_clean):
                        continue
                    # Keep — replay original blockquote lines
                    filtered.extend(lines[bq_start:i])
                    continue
                filtered.append(ln)
                i += 1
            # Optional: also extract interpretasi if exists in this section
            interp_text, _skip = _extract_interpretasi(filtered)
            interp_html = ""
            if interp_text:
                interp_html = f'<div class="gs-interp"><div class="gs-interp-icon">💡</div><div class="gs-interp-body"><div class="gs-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div><div class="gs-interp-text">{_esc(interp_text)}</div></div></div>'
            # Merge interpretasi from sister PERNIKAHAN section if available
            pmi_text, pmi_profil, pmi_peringatan = _find_pernikahan_interpretasi(all_sections)
            pmi_html = _render_pernikahan_interp_card(pmi_text, pmi_profil, pmi_peringatan)
            extra = render_generic_lines(filtered)
            body = "\n".join(p for p in [interp_html, pmi_html, ks_html, extra] if p)
            return page_shell(num, title_id, title_hz, section_label, body, subject_name)

    interp_text, skip_range = _extract_interpretasi(lines)
    interp_html = ""
    if interp_text:
        interp_html = f'''<div class="gs-interp">
  <div class="gs-interp-icon">💡</div>
  <div class="gs-interp-body">
    <div class="gs-interp-eyebrow">INTERPRETASI RAMALAN · 解 釋</div>
    <div class="gs-interp-text">{_esc(interp_text)}</div>
  </div>
</div>'''
        # Remove extracted lines from rendering source to avoid duplicate
        if skip_range:
            s, e = skip_range
            lines = lines[:s] + lines[e:]

    body = render_generic_lines(lines)
    if not body.strip() and not interp_html:
        body = callout("Konten tidak tersedia di sumber MD.", variant="warn", icon="⚠")
        return page_shell(num, title_id, title_hz, section_label, body, subject_name)
    density = _density_class(body)
    if density:
        body = f'<div class="{density}">{body}</div>'
    return page_shell(num, title_id, title_hz, section_label, interp_html + body, subject_name)


GENERIC_PAGE_CSS = """
/* === GENERIC SECTION === */

/* Interpretasi top card (red gradient — subject-specific from MD) */
.gs-interp {
  display: grid; grid-template-columns: 14mm 1fr; gap: var(--sp-3); align-items: start;
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: #FBF7F0; border-radius: var(--r-md);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.25);
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.gs-interp-icon { font-size: 22pt; line-height: 1; text-align: center; align-self: center; }
.gs-interp-body { display: flex; flex-direction: column; gap: 1mm; }
.gs-interp-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; letter-spacing: 4px;
  color: var(--color-gold); text-transform: uppercase; font-weight: 700;
}
.gs-interp-text {
  font-family: var(--font-display); font-size: 9.5pt; line-height: 1.5;
  color: #FBF7F0; font-style: italic;
}

/* Lead paragraph: drop-cap + larger leading */
.gs-para.gs-lead {
  background: linear-gradient(180deg, rgba(251,247,240,0.85) 0%, rgba(244,232,204,0.5) 100%);
  border-left: 0.6mm solid var(--color-red);
  padding: var(--sp-3) var(--sp-3) var(--sp-3) var(--sp-4);
  border-radius: 0 var(--r-md) var(--r-md) 0;
  margin: 0 0 2.5mm 0;
  font-size: 9.6pt; line-height: 1.65;
  color: var(--color-ink); text-align: justify;
  position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.gs-para.gs-lead::first-letter {
  font-family: var(--font-display); font-size: 22pt; font-weight: 700;
  color: var(--color-red); float: left;
  line-height: 0.9; padding: 0 1.5mm 0 0; margin-top: 0.6mm;
}

.gs-para {
  background: linear-gradient(180deg, rgba(251,247,240,0.55) 0%, rgba(248,242,228,0.3) 100%);
  border-left: 0.4mm solid var(--color-gold);
  padding: 1.6mm 2.5mm; border-radius: 0 var(--r-sm) var(--r-sm) 0;
  margin: 0 0 1.6mm 0; font-size: var(--type-body); line-height: 1.55;
  color: var(--color-ink); text-align: justify;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.gs-para .hz { color: var(--color-red); font-weight: 600; }
.gs-para strong { color: var(--color-red); font-weight: 600; }

/* Inline rating block "Profesi Cocok: ★★★★☆ ..." */
.gs-rating {
  display: grid; grid-template-columns: auto auto 1fr; gap: 2mm; align-items: center;
  margin: 1.2mm 0; padding: 1.5mm 2.5mm; border-radius: var(--r-sm);
  background: linear-gradient(90deg, var(--color-gold-tint) 0%, var(--color-cream) 100%);
  border-left: 0.4mm solid var(--color-gold-deep);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.gs-rating-key {
  font-family: var(--font-display); font-size: 9pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
}
.gs-rating-extra { font-size: 8pt; color: var(--color-ink-soft); font-style: italic; }

.gs-stars { display: inline-flex; gap: 0.3mm; line-height: 1; font-size: 10pt; }
.gs-star.on  { color: var(--color-gold-deep); }
.gs-star.off { color: rgba(201,169,97,0.25); }

/* Labeled card (bold-label + bullets) */
.gs-labeled-card, .gs-labeled-call {
  margin: 0 0 1.8mm 0; padding: 1.8mm 2.8mm; border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.gs-labeled-card.v-good, .gs-labeled-call.v-good {
  background: var(--color-success-bg); border-left: 0.5mm solid var(--color-success);
}
.gs-labeled-card.v-warn, .gs-labeled-call.v-warn {
  background: var(--color-warn-bg); border-left: 0.5mm solid var(--color-warn);
}
.gs-labeled-card.v-info, .gs-labeled-call.v-info {
  background: var(--color-gold-tint); border-left: 0.5mm solid var(--color-gold);
}
.gs-lc-head {
  display: flex; align-items: center; gap: 1.5mm;
  padding-bottom: 0.8mm; margin-bottom: 0.8mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.gs-lc-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 4.5mm; height: 4.5mm; border-radius: 50%;
  background: var(--color-paper);
  font-size: 9pt; font-weight: 700;
  color: var(--color-red);
}
.gs-labeled-card.v-good .gs-lc-icon, .gs-labeled-call.v-good .gs-lc-icon {
  background: var(--color-success); color: white;
}
.gs-labeled-card.v-warn .gs-lc-icon, .gs-labeled-call.v-warn .gs-lc-icon {
  background: var(--color-warn); color: white;
}
.gs-lc-label {
  font-family: var(--font-display); font-size: 10pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.4px;
}
.gs-lc-list { margin: 0; padding: 0; list-style: none; }
.gs-lc-list li {
  position: relative; padding: 0.5mm 0 0.5mm 5mm;
  font-size: 8.5pt; line-height: 1.5; color: var(--color-ink-soft);
}
.gs-lc-list li::before {
  content: "◆"; position: absolute; left: 1mm; top: 1.6mm;
  color: var(--color-gold); font-size: 6.5pt;
}
.gs-labeled-card.v-good .gs-lc-list li::before { content: "✓"; color: var(--color-success); }
.gs-labeled-card.v-warn .gs-lc-list li::before { content: "!"; color: var(--color-warn); font-weight: 700; }
.gs-lc-list li strong { color: var(--color-red); font-weight: 600; }

.gs-lc-text { font-size: 9pt; line-height: 1.55; color: var(--color-ink); text-align: justify; }
.gs-lc-text strong { color: var(--color-red); font-weight: 600; }

/* Tables */
.gs-table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  margin: var(--sp-2) 0; font-size: 8.5pt; line-height: 1.45;
  border-radius: var(--r-md); overflow: hidden;
  box-shadow: var(--sh-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.gs-table th, .gs-table td {
  padding: 1.4mm 2mm; text-align: left; vertical-align: top;
  border-bottom: 0.15mm solid var(--color-gold-soft);
}
.gs-table thead th {
  background: linear-gradient(180deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: var(--color-cream); font-weight: 600; font-size: 8pt;
  letter-spacing: 0.4px; text-transform: uppercase;
}
.gs-table tbody tr:nth-child(even) td { background: rgba(244,232,204,0.4); }
.gs-table tbody tr:last-child td { border-bottom: none; }
.gs-table td:first-child { color: var(--color-red); font-weight: 600; background: rgba(201,169,97,0.10); }
.gs-table tbody tr:nth-child(even) td:first-child { background: rgba(201,169,97,0.16); }

/* Auto-fit density modifiers — slightly tighter spacing/font for dense pages */
.gs-density-mid .gs-para { font-size: 9pt; padding: 1.3mm 2.3mm; line-height: 1.5; margin-bottom: 1.3mm; }
.gs-density-mid .gs-para.gs-lead { font-size: 9.2pt; padding: 2mm 2.5mm 2mm 3mm; }
.gs-density-mid .gs-labeled-card, .gs-density-mid .gs-labeled-call { padding: 1.4mm 2.3mm; margin-bottom: 1.4mm; }
.gs-density-mid .gs-lc-list li { font-size: 8.2pt; line-height: 1.45; padding: 0.4mm 0 0.4mm 5mm; }

.gs-density-tight .gs-para { font-size: 8.6pt; padding: 1mm 2mm; line-height: 1.45; margin-bottom: 1mm; }
.gs-density-tight .gs-para.gs-lead { font-size: 8.8pt; padding: 1.5mm 2mm 1.5mm 2.5mm; line-height: 1.5; }
.gs-density-tight .gs-para.gs-lead::first-letter { font-size: 16pt; }
.gs-density-tight .gs-labeled-card, .gs-density-tight .gs-labeled-call { padding: 1.1mm 2mm; margin-bottom: 1mm; }
.gs-density-tight .gs-lc-list li { font-size: 7.9pt; line-height: 1.4; padding: 0.3mm 0 0.3mm 4.5mm; }
.gs-density-tight .gs-lc-label { font-size: 9.5pt; }
.gs-density-tight .gs-table { font-size: 8pt; }
.gs-density-tight .gs-table th, .gs-density-tight .gs-table td { padding: 1mm 1.6mm; }

/* === TABEL ALIRAN TAHUNAN — Indo-friendly Hanzi-glossed table === */
.tt-glossary {
  margin: 0 0 var(--sp-3) 0; padding: var(--sp-3); border-radius: var(--r-md);
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border: var(--bw-thin) solid var(--color-gold);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-gl-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  letter-spacing: 4px; color: var(--color-red); text-transform: uppercase;
  margin-bottom: 1mm;
}
.tt-gl-intro {
  font-size: 8.4pt; line-height: 1.5; color: var(--color-ink-soft);
  margin-bottom: var(--sp-2); padding-bottom: 1mm;
  border-bottom: 0.15mm dashed var(--color-gold-soft);
}
.tt-gl-block { margin-bottom: 1.5mm; }
.tt-gl-block:last-child { margin-bottom: 0; }
.tt-gl-h {
  font-family: var(--font-display); font-size: 8.5pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
  margin-bottom: 0.8mm;
}
.tt-gl-hzh { font-family: var(--font-serif-tc); font-size: 8pt; color: var(--color-muted); margin-left: 1mm; letter-spacing: 1.5px; }
.tt-gl-grid { display: grid; gap: 0.6mm 1.2mm; }
.tt-gl-grid-tg { grid-template-columns: repeat(5, 1fr); }
.tt-gl-grid-phase { grid-template-columns: repeat(6, 1fr); }
.tt-gl-item, .tt-gl-phase {
  padding: 0.8mm 1.2mm; border-radius: var(--r-sm);
  background: var(--color-paper); border: 0.1mm solid var(--color-gold-soft);
  display: flex; flex-direction: column; gap: 0.2mm;
  font-size: 7pt; line-height: 1.2;
  print-color-adjust: exact;
}
.tt-gl-phase.mood-good { background: var(--color-success-bg); border-color: rgba(76,140,73,0.3); }
.tt-gl-phase.mood-warn { background: var(--color-warn-bg);    border-color: rgba(166,89,23,0.3); }
.tt-gl-hz { font-family: var(--font-serif-tc); font-size: 9pt; font-weight: 700; color: var(--color-red); }
.tt-gl-indo { font-size: 6.8pt; color: var(--color-ink); font-weight: 600; }
.tt-gl-tema { font-size: 6.3pt; color: var(--color-muted); font-style: italic; line-height: 1.15; }
.tt-gl-mood-row { display: flex; flex-wrap: wrap; gap: 1.2mm; }
.tt-gl-chip {
  padding: 0.6mm 1.5mm; border-radius: 1mm; font-size: 7.2pt; font-weight: 600;
  print-color-adjust: exact;
}
.tt-gl-chip.mood-good { background: var(--color-success-bg); color: var(--color-success); }
.tt-gl-chip.mood-warn { background: var(--color-warn-bg); color: var(--color-warn); }
.tt-gl-chip.mood-neutral { background: var(--color-gold-tint); color: var(--color-gold-deep); }

/* Periode header card */
.tt-periode-head {
  display: grid; grid-template-columns: 9mm 1fr; gap: var(--sp-2);
  padding: 1.6mm var(--sp-3); margin: var(--sp-2) 0 1mm 0;
  background: linear-gradient(90deg, rgba(139,26,26,0.08) 0%, rgba(201,169,97,0.08) 100%);
  border-left: 0.5mm solid var(--color-red);
  border-radius: 0 var(--r-md) var(--r-md) 0;
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-ph-icon { font-size: 14pt; align-self: center; text-align: center; }
.tt-ph-body { display: flex; flex-direction: column; gap: 0.4mm; min-width: 0; }
.tt-ph-title {
  font-family: var(--font-display); font-size: 9.5pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
  display: flex; align-items: center; gap: 1.5mm;
}
.tt-ph-now {
  font-size: 6.5pt; padding: 0.3mm 1.2mm; border-radius: 0.8mm;
  background: var(--color-red); color: var(--color-cream); font-weight: 700;
  letter-spacing: 1px;
}
.tt-ph-meta { display: flex; flex-wrap: wrap; gap: 1mm 3mm; font-size: 8pt; color: var(--color-ink-soft); }
.tt-ph-meta strong { color: var(--color-red); font-family: var(--font-serif-tc); }

/* === BINTANG KHUSUS (神煞) — visual cards per bintang === */
.bx-page-intro {
  display: grid; grid-template-columns: 12mm 1fr; gap: var(--sp-3);
  padding: var(--sp-3); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border: var(--bw-thin) solid var(--color-gold); border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bx-pi-icon { font-size: 18pt; line-height: 1; align-self: center; text-align: center; color: var(--color-gold-deep); }
.bx-pi-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  letter-spacing: 4px; color: var(--color-red); text-transform: uppercase;
  margin-bottom: 0.8mm;
}
.bx-pi-text { font-size: 8.5pt; line-height: 1.6; color: var(--color-ink-soft); text-align: justify; }
.bx-pi-text strong { color: var(--color-red); font-weight: 700; }
.bx-pi-text em { color: var(--color-gold-deep); font-style: italic; }

.bx-stack { display: flex; flex-direction: column; gap: 2mm; }
.bx-card {
  padding: 2mm 2.5mm; border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bx-card.mood-good {
  background: linear-gradient(135deg, var(--color-success-bg) 0%, var(--color-paper) 70%);
  border-left: 0.7mm solid var(--color-success);
}
.bx-card.mood-warn {
  background: linear-gradient(135deg, var(--color-warn-bg) 0%, var(--color-paper) 70%);
  border-left: 0.7mm solid var(--color-warn);
}
.bx-card.mood-neutral { border-left: 0.5mm solid var(--color-gold); }

.bx-head {
  display: grid; grid-template-columns: 8mm 13mm 1fr; gap: 2.5mm; align-items: center;
  padding-bottom: 1mm; margin-bottom: 1.2mm;
  border-bottom: 0.15mm dashed var(--color-gold-soft);
}
.bx-rank {
  font-family: var(--font-display); font-size: 14pt; font-weight: 700;
  color: var(--color-red); line-height: 1; text-align: center;
  opacity: 0.5;
}
.bx-seal-wrap {
  display: flex; align-items: center; justify-content: center;
  width: 13mm; height: 13mm;
}
.bx-seal-svg { width: 11mm; height: 11mm; }
.bx-card.mood-good .bx-seal-svg { color: var(--color-success); }
.bx-card.mood-warn .bx-seal-svg { color: var(--color-warn); }
.bx-card.mood-neutral .bx-seal-svg { color: var(--color-gold-deep); }
.bx-seal-fallback { font-size: 18pt; color: var(--color-gold-deep); }

.bx-name { display: flex; flex-direction: column; gap: 0.4mm; min-width: 0; }
.bx-hz {
  font-family: var(--font-serif-tc); font-size: 14pt; font-weight: 700;
  color: var(--color-red); line-height: 1; letter-spacing: 1.5px;
}
.bx-pinyin {
  font-family: var(--font-display); font-size: 8pt; font-style: italic;
  color: var(--color-muted);
}
.bx-indo {
  font-family: var(--font-display); font-size: 9pt; font-weight: 700;
  color: var(--color-ink); letter-spacing: 0.3px;
}

.bx-body { display: flex; flex-direction: column; gap: 1.2mm; }
.bx-interp { font-size: 8.5pt; line-height: 1.55; color: var(--color-ink); text-align: justify; }
.bx-interp strong { color: var(--color-red); font-weight: 700; }
.bx-bullets { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 0.4mm; }
.bx-bullets li {
  position: relative; padding: 0.3mm 0 0.3mm 4.5mm;
  font-size: 8.2pt; line-height: 1.45; color: var(--color-ink-soft);
}
.bx-bullets li::before {
  content: "◆"; position: absolute; left: 1mm; top: 1.2mm;
  color: var(--color-gold); font-size: 6.5pt;
}
.bx-bullets li strong { color: var(--color-red); font-weight: 700; }

.bx-makna {
  display: grid; grid-template-columns: 6mm 1fr; gap: 1.5mm; align-items: start;
  padding: 1.4mm 2mm; margin-top: 0.5mm;
  border-radius: var(--r-sm);
  background: var(--color-red-soft);
  border-left: 0.4mm solid var(--color-red);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.bx-makna-icon {
  font-size: 11pt; line-height: 1; text-align: center;
  display: flex; align-items: center; justify-content: center;
  align-self: center;
}
.bx-makna-text {
  font-size: 8.3pt; line-height: 1.55; color: var(--color-ink);
  font-style: italic;
}
.bx-makna-text strong { color: var(--color-red); font-style: normal; font-weight: 700; }

/* === KARIR & PROFESI — visual bidang grid + ranked priority === */
.kr-page-intro {
  display: grid; grid-template-columns: 12mm 1fr; gap: var(--sp-3);
  padding: var(--sp-3); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border: var(--bw-thin) solid var(--color-gold); border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.kr-pi-icon { font-size: 18pt; line-height: 1; align-self: center; text-align: center; }
.kr-pi-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  letter-spacing: 4px; color: var(--color-red); text-transform: uppercase;
  margin-bottom: 0.8mm;
}
.kr-pi-text { font-size: 8.5pt; line-height: 1.6; color: var(--color-ink-soft); text-align: justify; }
.kr-pi-text strong { color: var(--color-red); font-weight: 700; }
.kr-pi-text em { color: var(--color-gold-deep); font-style: italic; }

.kr-h {
  display: flex; align-items: center; gap: 1.5mm;
  margin: var(--sp-2) 0 1.2mm 0; padding-bottom: 0.6mm;
  border-bottom: 0.15mm dashed var(--color-gold-soft);
}
.kr-h.kr-h-sub { margin-top: 1.5mm; padding-bottom: 0.3mm; }
.kr-h-icon { font-size: 11pt; color: var(--color-red); }
.kr-h-id {
  font-family: var(--font-display); font-size: 11pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.4px;
}

/* Priority cards (Lin Ruyi style — ranked list with stars) */
.kr-pri-section, .kr-cat-section, .kr-bidang-block, .kr-call-stack { margin: 0 0 var(--sp-3) 0; }
.kr-pri-stack { display: flex; flex-direction: column; gap: 1.5mm; }
.kr-pri-card {
  display: grid; grid-template-columns: 8mm 9mm 1fr; gap: 2.5mm; align-items: center;
  padding: 1.8mm 2.5mm; border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.kr-pri-card.mood-good {
  background: linear-gradient(135deg, var(--color-success-bg) 0%, var(--color-paper) 70%);
  border-left: 0.7mm solid var(--color-success);
}
.kr-pri-card.mood-neutral { border-left: 0.5mm solid var(--color-gold); }
.kr-pri-card.mood-warn {
  background: linear-gradient(135deg, var(--color-warn-bg) 0%, var(--color-paper) 70%);
  border-left: 0.7mm solid var(--color-warn);
}
.kr-pri-rank {
  font-family: var(--font-display); font-size: 16pt; font-weight: 700;
  color: var(--color-red); line-height: 1; text-align: center;
}
.kr-pri-icon { font-size: 14pt; line-height: 1; text-align: center; }
.kr-pri-body { display: flex; flex-direction: column; gap: 0.4mm; min-width: 0; }
.kr-pri-bidang {
  font-family: var(--font-display); font-size: 10.5pt; font-weight: 700;
  color: var(--color-red); line-height: 1.25;
}
.kr-stars { display: inline-flex; gap: 0.2mm; font-size: 8.5pt; line-height: 1; margin: 0.3mm 0; }
.kr-star.on { color: var(--color-gold-deep); }
.kr-star.off { color: rgba(201,169,97,0.25); }
.kr-pri-alasan { font-size: 8pt; line-height: 1.45; color: var(--color-ink-soft); font-style: italic; }

/* Category cards (Li Yuanxiang style — kategori + bidang chips) */
.kr-cat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2mm; }
.kr-cat-card {
  padding: 1.8mm 2.2mm; border-radius: var(--r-md);
  background: linear-gradient(180deg, var(--color-paper) 0%, var(--color-cream) 100%);
  border: var(--bw-hair) solid var(--color-gold-soft);
  border-top: 0.5mm solid var(--color-gold);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.kr-cat-head {
  display: flex; align-items: center; gap: 1.5mm;
  padding-bottom: 0.8mm; margin-bottom: 0.8mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.kr-cat-icon { font-size: 13pt; line-height: 1; }
.kr-cat-name {
  font-family: var(--font-display); font-size: 10pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
}
.kr-cat-chips { display: flex; flex-wrap: wrap; gap: 1mm; }
.kr-cat-chip {
  display: inline-flex; align-items: center; gap: 0.6mm;
  padding: 0.4mm 1.5mm; border-radius: 1mm;
  font-size: 7.5pt; line-height: 1.3;
  background: var(--color-gold-tint); color: var(--color-ink-soft);
  border: 0.1mm solid var(--color-gold-soft);
  print-color-adjust: exact;
}

/* Generic bidang chip grid (no category) */
.kr-chip-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2mm;
  margin: 0 0 var(--sp-2) 0;
}
.kr-chip {
  display: flex; align-items: center; gap: 1.2mm;
  padding: 1.2mm 1.6mm; border-radius: var(--r-sm);
  background: var(--color-paper); border-left: 0.4mm solid var(--color-gold);
  border-top: 0.1mm solid var(--color-gold-soft);
  font-size: 8pt; line-height: 1.35; color: var(--color-ink-soft);
  break-inside: avoid;
  print-color-adjust: exact;
}
.kr-chip-icon { font-size: 11pt; line-height: 1; flex-shrink: 0; }
.kr-chip-text strong { color: var(--color-red); }

/* Callout stack (Karir cocok / Potensi / Peringatan) */
.kr-call-stack { display: flex; flex-direction: column; gap: 1.5mm; }
.kr-call {
  padding: 1.8mm 2.5mm; border-radius: var(--r-md);
  background: var(--color-paper); border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.kr-call.mood-good { background: var(--color-success-bg); border-left: 0.5mm solid var(--color-success); }
.kr-call.mood-warn { background: var(--color-warn-bg); border-left: 0.5mm solid var(--color-warn); }
.kr-call.mood-info { background: var(--color-gold-tint); border-left: 0.5mm solid var(--color-gold); }
.kr-call-h {
  display: flex; align-items: center; gap: 1.5mm;
  padding-bottom: 0.6mm; margin-bottom: 0.8mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.kr-call-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 4.5mm; height: 4.5mm; border-radius: 50%;
  font-weight: 700; font-size: 9pt; color: white;
}
.kr-call.mood-good .kr-call-icon { background: var(--color-success); }
.kr-call.mood-warn .kr-call-icon { background: var(--color-warn); }
.kr-call.mood-info .kr-call-icon { background: var(--color-gold); }
.kr-call-label {
  font-family: var(--font-display); font-size: 10pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
}
.kr-call.mood-good .kr-call-label { color: var(--color-success); }
.kr-call.mood-warn .kr-call-label { color: var(--color-warn); }
.kr-call-text { font-size: 8.5pt; line-height: 1.55; color: var(--color-ink); text-align: justify; }
.kr-call-text strong { color: var(--color-red); font-weight: 700; }

/* === KECOCOKAN SHIO — visual matchmaker === */
.ks-intro {
  display: grid; grid-template-columns: 12mm 1fr; gap: var(--sp-3);
  padding: var(--sp-3); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border: var(--bw-thin) solid var(--color-gold);
  border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-pi-icon { font-size: 18pt; line-height: 1; align-self: center; text-align: center; }
.ks-pi-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  letter-spacing: 4px; color: var(--color-red); text-transform: uppercase;
  margin-bottom: 0.8mm;
}
.ks-pi-text { font-size: 8.5pt; line-height: 1.6; color: var(--color-ink-soft); text-align: justify; }
.ks-pi-text strong { color: var(--color-red); font-weight: 700; }
.ks-pi-text em { color: var(--color-gold-deep); font-style: italic; }

.ks-block { margin: 0 0 var(--sp-3) 0; padding: var(--sp-3); border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-block.ks-good { background: linear-gradient(180deg, var(--color-success-bg) 0%, var(--color-paper) 70%); border-left: 0.7mm solid var(--color-success); }
.ks-block.ks-warn { background: linear-gradient(180deg, var(--color-warn-bg) 0%, var(--color-paper) 70%); border-left: 0.7mm solid var(--color-warn); }
.ks-block-h {
  display: flex; align-items: center; gap: 1.5mm;
  padding-bottom: 1mm; margin-bottom: 1.5mm;
  border-bottom: 0.15mm dashed var(--color-gold-soft);
}
.ks-block-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 5mm; height: 5mm; border-radius: 50%;
  font-weight: 700; font-size: 9pt; color: white;
}
.ks-block.ks-good .ks-block-icon { background: var(--color-success); }
.ks-block.ks-warn .ks-block-icon { background: var(--color-warn); }
.ks-block-id { font-family: var(--font-display); font-size: 11pt; font-weight: 700; color: var(--color-red); letter-spacing: 0.4px; }
.ks-block-hz { font-family: var(--font-serif-tc); font-size: 8.5pt; color: var(--color-muted); margin-left: auto; letter-spacing: 2px; }

.ks-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.8mm; }
.ks-card {
  display: grid; grid-template-columns: 14mm 1fr; gap: 3.5mm; align-items: center;
  padding: 2mm 2.5mm 2mm 2mm; border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-card.mood-good { border-left: 0.5mm solid var(--color-success); background: linear-gradient(135deg, #F0F8EC 0%, var(--color-paper) 70%); }
.ks-card.mood-warn { border-left: 0.5mm solid var(--color-warn); background: linear-gradient(135deg, #FCF4E8 0%, var(--color-paper) 70%); }
.ks-card.mood-neutral { border-left: 0.5mm solid var(--color-gold-soft); }
.ks-seal-wrap {
  display: flex; align-items: center; justify-content: center;
  width: 14mm; height: 14mm;
  padding: 0.6mm; /* breathing room di sekitar SVG */
}
.ks-seal { width: 12mm; height: 12mm; }
.ks-shio-svg { width: 100%; height: 100%; max-width: 13mm; max-height: 13mm; display: block; }
.ks-shio-fallback {
  width: 11mm; height: 11mm; border: 0.3mm dashed var(--color-gold-soft);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 9pt; color: var(--color-muted);
}
.ks-card.mood-good .ks-seal { color: var(--color-red); }
.ks-card.mood-warn .ks-seal { color: var(--color-ink); }
.ks-card.mood-neutral .ks-seal { color: var(--color-gold-deep); }

/* === Merged PERNIKAHAN interpretasi (when MD has separate 夫妻宮 section) === */
.ks-pernikahan-merge {
  margin: 0 0 var(--sp-3) 0; padding: var(--sp-3);
  border-radius: var(--r-md);
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border: var(--bw-thin) solid var(--color-gold);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-pmi-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 4px; text-transform: uppercase;
  padding-bottom: 0.8mm; margin-bottom: 1.2mm;
  border-bottom: 0.15mm solid var(--color-gold-soft);
}
.ks-pmi-text {
  font-size: 8.7pt; line-height: 1.6; color: var(--color-ink);
  margin-bottom: 1.5mm; text-align: justify;
}
.ks-pmi-text strong { color: var(--color-red); font-weight: 700; }
.ks-pmi-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1.8mm; }
.ks-pmi-block {
  padding: 1.5mm 2mm; border-radius: var(--r-sm);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-pmi-block.ks-pmi-good { background: var(--color-success-bg); border-left: 0.4mm solid var(--color-success); }
.ks-pmi-block.ks-pmi-warn { background: var(--color-warn-bg); border-left: 0.4mm solid var(--color-warn); }
.ks-pmi-h {
  display: flex; align-items: center; gap: 1.2mm;
  font-family: var(--font-display); font-size: 8.5pt; font-weight: 700;
  letter-spacing: 0.3px; margin-bottom: 0.8mm;
}
.ks-pmi-good .ks-pmi-h { color: var(--color-success); }
.ks-pmi-warn .ks-pmi-h { color: var(--color-warn); }
.ks-pmi-icon { font-size: 9pt; }
.ks-pmi-block ul { margin: 0; padding: 0; list-style: none; }
.ks-pmi-block li {
  position: relative; padding: 0.3mm 0 0.3mm 4mm;
  font-size: 7.7pt; line-height: 1.45; color: var(--color-ink-soft);
}
.ks-pmi-block li::before {
  position: absolute; left: 0.8mm; top: 1mm;
  font-weight: 700; font-size: 6pt;
}
.ks-pmi-good li::before { content: "+"; color: var(--color-success); }
.ks-pmi-warn li::before { content: "!"; color: var(--color-warn); }
.ks-oc-hz {
  font-family: var(--font-serif-tc); color: var(--color-red); font-weight: 700;
  margin-right: 0.5mm;
}
.ks-body { display: flex; flex-direction: column; gap: 0.3mm; min-width: 0; }
.ks-name { font-family: var(--font-display); font-size: 11pt; font-weight: 700; color: var(--color-red); line-height: 1; }
.ks-stars { display: inline-flex; gap: 0.2mm; font-size: 7.5pt; line-height: 1; }
.ks-star.on { color: var(--color-gold-deep); }
.ks-star.off { color: rgba(201,169,97,0.25); }
.ks-label { font-family: var(--font-display); font-size: 7.5pt; font-weight: 700; color: var(--color-red); letter-spacing: 0.3px; }
.ks-card.mood-good .ks-label { color: var(--color-success); }
.ks-card.mood-warn .ks-label { color: var(--color-warn); }
.ks-note { font-size: 7.4pt; line-height: 1.4; color: var(--color-ink-soft); font-style: italic; }

.ks-others-block {
  margin: 0 0 var(--sp-3) 0; padding: 1.8mm 2.2mm;
  border-radius: var(--r-md);
  background: linear-gradient(180deg, var(--color-gold-tint) 0%, var(--color-paper) 100%);
  border-left: 0.5mm solid var(--color-gold);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ks-others-h {
  display: flex; align-items: center; gap: 1.5mm;
  padding-bottom: 0.6mm; margin-bottom: 0.8mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.ks-others-icon {
  font-size: 9pt; color: var(--color-gold-deep);
  display: inline-flex; align-items: center; justify-content: center;
  width: 5mm; height: 5mm; border-radius: 50%;
  background: var(--color-paper); border: 0.2mm solid var(--color-gold);
}
.ks-others-id { font-family: var(--font-display); font-size: 10pt; font-weight: 700; color: var(--color-red); letter-spacing: 0.4px; }
.ks-others-hz { font-family: var(--font-serif-tc); font-size: 8.5pt; color: var(--color-muted); margin-left: auto; letter-spacing: 2px; }
.ks-others-desc {
  font-size: 7.8pt; line-height: 1.45; color: var(--color-ink-soft);
  font-style: italic; margin-bottom: 1mm;
}
.ks-others-chips { display: flex; flex-wrap: wrap; gap: 1.2mm; }
.ks-other-chip {
  display: inline-flex; align-items: center; gap: 0.8mm;
  padding: 0.6mm 2mm; border-radius: 1mm;
  background: var(--color-paper); border: 0.15mm solid var(--color-gold-soft);
  color: var(--color-ink-soft); font-size: 7.5pt; line-height: 1.4;
  print-color-adjust: exact;
}
.ks-other-chip strong { color: var(--color-red); font-weight: 700; }
.ks-other-chip.ks-oc-generic {
  background: var(--color-gold-tint); border-style: dashed;
  font-size: 7.3pt; padding: 0.6mm 2mm;
}
.ks-other-chip.ks-oc-generic strong { color: var(--color-gold-deep); }

/* Page intro — generic explainer at very top of Tabel Nasib Tahunan */
.tt-page-intro {
  display: grid; grid-template-columns: 12mm 1fr; gap: var(--sp-3);
  padding: var(--sp-3); margin: 0 0 var(--sp-3) 0;
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border: var(--bw-thin) solid var(--color-gold);
  border-radius: var(--r-md);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-pi-icon { font-size: 18pt; line-height: 1; align-self: center; text-align: center; }
.tt-pi-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  letter-spacing: 4px; color: var(--color-red); text-transform: uppercase;
  margin-bottom: 0.8mm;
}
.tt-pi-text {
  font-size: 8.5pt; line-height: 1.6; color: var(--color-ink-soft);
  text-align: justify;
}
.tt-pi-text strong { color: var(--color-red); font-weight: 700; }
.tt-pi-text em { color: var(--color-gold-deep); font-style: italic; }

/* Da Yun narrative card */
.tt-narr {
  margin: 1mm 0 var(--sp-2) 0; padding: 1.6mm var(--sp-3);
  background: linear-gradient(135deg, var(--color-cream) 0%, var(--color-cream-deep) 100%);
  border-radius: var(--r-md); border-left: 0.5mm solid var(--color-gold);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-narr-h {
  font-family: var(--font-display); font-size: 9pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
  padding-bottom: 0.6mm; margin-bottom: 0.8mm;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.tt-narr-h .hz { font-family: var(--font-serif-tc); color: var(--color-red); }
.tt-narr-body {
  font-size: 8.5pt; line-height: 1.55; color: var(--color-ink-soft);
  text-align: justify;
}

/* Periode stats panel — mood distribution + top recurring terms */
.tt-stats {
  margin: 0 0 var(--sp-2) 0; padding: 1.5mm 2mm;
  border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-stats-h {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  color: var(--color-gold-deep); letter-spacing: 1px; text-transform: uppercase;
  margin-bottom: 1mm;
}
.tt-bar-wrap {
  display: flex; height: 4mm; border-radius: 1mm; overflow: hidden;
  margin-bottom: 0.6mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-bar-seg {
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 8pt; font-weight: 700;
  color: var(--color-cream);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-bar-seg.mood-good { background: var(--color-success); }
.tt-bar-seg.mood-warn { background: var(--color-warn); }
.tt-bar-seg.mood-neutral { background: var(--color-gold); color: var(--color-cream); }
.tt-bar-seg span { line-height: 1; }
.tt-bar-legend {
  display: flex; flex-wrap: wrap; gap: 2mm;
  font-size: 7pt; color: var(--color-ink-soft);
  margin-bottom: 1mm;
}
.tt-bar-key.mood-good { color: var(--color-success); font-weight: 600; }
.tt-bar-key.mood-warn { color: var(--color-warn); font-weight: 600; }
.tt-bar-key.mood-neutral { color: var(--color-gold-deep); font-weight: 600; }

.tt-freq-row {
  display: flex; flex-wrap: wrap; align-items: center; gap: 1.2mm;
  font-size: 7.5pt; margin-top: 0.8mm;
}
.tt-freq-lbl {
  font-family: var(--font-display); font-size: 7pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 0.3px;
}
.tt-freq-chip {
  display: inline-flex; align-items: center; gap: 0.6mm;
  padding: 0.4mm 1.4mm; border-radius: 1mm;
  font-size: 7pt;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-freq-chip.mood-good { background: var(--color-success-bg); color: var(--color-success); border: 0.1mm solid rgba(76,140,73,0.25); }
.tt-freq-chip.mood-warn { background: var(--color-warn-bg); color: var(--color-warn); border: 0.1mm solid rgba(166,89,23,0.25); }
.tt-freq-chip.mood-neutral { background: var(--color-gold-tint); color: var(--color-gold-deep); border: 0.1mm solid var(--color-gold-soft); }
.tt-freq-chip .hz { font-family: var(--font-serif-tc); font-weight: 700; }
.tt-freq-indo { opacity: 0.85; }
.tt-freq-cnt {
  font-family: var(--font-display); font-weight: 700; font-size: 6.5pt;
  margin-left: 0.5mm; opacity: 0.7;
}

/* Mini timeline */
.tt-tl-wrap {
  margin: 0 0 var(--sp-2) 0; padding: 1.5mm 2mm;
  border-radius: var(--r-md); background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-tl-lbl {
  font-family: var(--font-display); font-size: 7pt; font-weight: 700;
  color: var(--color-gold-deep); letter-spacing: 1px; text-transform: uppercase;
  margin-bottom: 0.8mm;
}
.tt-tl-track {
  display: grid; grid-auto-flow: column; grid-auto-columns: 1fr;
  gap: 0.6mm;
}
.tt-tl-item {
  display: flex; align-items: center; justify-content: center;
  padding: 1.2mm 0.5mm; border-radius: 1mm;
  font-family: var(--font-display); font-size: 8.5pt; font-weight: 700;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-tl-item.mood-good {
  background: var(--color-success); color: var(--color-cream);
}
.tt-tl-item.mood-warn {
  background: var(--color-warn); color: var(--color-cream);
}
.tt-tl-item.mood-neutral {
  background: var(--color-gold-tint); color: var(--color-gold-deep);
}
.tt-tl-usia { line-height: 1; }

/* Highlight section */
.tt-hl-section { margin: 0 0 var(--sp-3) 0; }
.tt-hl-eyebrow {
  font-family: var(--font-display); font-size: 7.5pt; font-weight: 700;
  color: var(--color-red); letter-spacing: 1.5px; text-transform: uppercase;
  margin-bottom: 1mm;
  padding-bottom: 0.5mm; border-bottom: 0.15mm solid var(--color-gold-soft);
}
.tt-hl-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2mm;
}
.tt-hl {
  display: grid; grid-template-columns: 7mm 1fr; gap: 1.5mm;
  padding: 1.4mm 2mm; border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-hl.mood-good {
  background: linear-gradient(135deg, var(--color-success-bg) 0%, var(--color-paper) 70%);
  border-left: 0.5mm solid var(--color-success);
}
.tt-hl.mood-warn {
  background: linear-gradient(135deg, var(--color-warn-bg) 0%, var(--color-paper) 70%);
  border-left: 0.5mm solid var(--color-warn);
}
.tt-hl.mood-neutral { border-left: 0.5mm solid var(--color-gold-soft); }
.tt-hl-icon {
  display: flex; align-items: center; justify-content: center;
  width: 6mm; height: 6mm; align-self: center;
  border-radius: 50%; font-weight: 700; font-size: 9pt;
  color: white;
}
.tt-hl.mood-good .tt-hl-icon { background: var(--color-success); }
.tt-hl.mood-warn .tt-hl-icon { background: var(--color-warn); }
.tt-hl.mood-neutral .tt-hl-icon { background: var(--color-gold); }
.tt-hl-body { display: flex; flex-direction: column; gap: 0.3mm; min-width: 0; }
.tt-hl-head { display: flex; align-items: baseline; gap: 1mm; }
.tt-hl-usia {
  font-family: var(--font-display); font-size: 9.5pt; font-weight: 700;
  color: var(--color-red); line-height: 1;
}
.tt-hl-tahun { font-size: 7.5pt; color: var(--color-muted); }
.tt-hl-gz { font-family: var(--font-serif-tc); font-size: 8.5pt; color: var(--color-red); font-weight: 700; }
.tt-hl-brief {
  font-size: 7.4pt; line-height: 1.4; color: var(--color-ink-soft);
}
.tt-hl-brief .hz { font-family: var(--font-serif-tc); color: var(--color-red); font-weight: 600; }

/* Year-card grid (panduan-style — each year = one clean card) */
.tt-yc-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.5mm;
  margin-bottom: var(--sp-2);
}
.tt-yc {
  display: flex; flex-direction: column; gap: 0.8mm;
  padding: 1.5mm 2mm; border-radius: var(--r-md);
  background: var(--color-paper);
  border: var(--bw-hair) solid var(--color-gold-soft);
  break-inside: avoid; page-break-inside: avoid;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.tt-yc.mood-good { background: linear-gradient(135deg, var(--color-success-bg) 0%, var(--color-paper) 60%); border-left: 0.5mm solid var(--color-success); }
.tt-yc.mood-warn { background: linear-gradient(135deg, var(--color-warn-bg) 0%, var(--color-paper) 60%); border-left: 0.5mm solid var(--color-warn); }
.tt-yc.mood-neutral { border-left: 0.5mm solid var(--color-gold-soft); }

.tt-yc-head {
  display: flex; align-items: baseline; gap: 1.5mm;
  padding-bottom: 0.6mm; border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.tt-yc-usia { display: flex; align-items: baseline; gap: 1mm; }
.tt-yc-usia-lbl {
  font-family: var(--font-display); font-size: 6.5pt; font-weight: 700;
  letter-spacing: 1.2px; color: var(--color-gold-deep);
}
.tt-yc-usia-num {
  font-family: var(--font-display); font-size: 14pt; font-weight: 700;
  color: var(--color-red); line-height: 1;
}
.tt-yc-tahun {
  font-family: var(--font-display); font-size: 8pt; color: var(--color-muted);
  margin-left: auto;
}
.tt-yc-gz {
  font-family: var(--font-serif-tc); font-size: 10pt; font-weight: 700;
  color: var(--color-red); margin-left: auto; letter-spacing: 1px;
}

.tt-yc-section { display: flex; flex-direction: column; gap: 0.4mm; }
.tt-yc-lbl {
  font-family: var(--font-display); font-size: 6.5pt; font-weight: 700;
  color: var(--color-gold-deep); letter-spacing: 0.5px; text-transform: uppercase;
}
.tt-yc-lbl-hz {
  font-family: var(--font-serif-tc); font-size: 6.5pt; color: var(--color-muted);
  letter-spacing: 1px; margin-left: 0.5mm;
}
.tt-yc-chips { display: flex; flex-wrap: wrap; gap: 0.8mm; }
.tt-yc-empty { font-size: 7.5pt; color: var(--color-muted); font-style: italic; }

.tt-tg-chip, .tt-st-chip, .tt-bx-chip {
  display: inline-flex; align-items: center; gap: 0.8mm;
  padding: 0.4mm 1.4mm; border-radius: 1mm;
  font-size: 7pt; line-height: 1.25;
  print-color-adjust: exact;
}
.tt-tg-chip.mood-good, .tt-st-chip.mood-good, .tt-bx-chip.mood-good {
  background: var(--color-success-bg); color: var(--color-success);
  border: 0.1mm solid rgba(76,140,73,0.25);
}
.tt-tg-chip.mood-warn, .tt-st-chip.mood-warn, .tt-bx-chip.mood-warn {
  background: var(--color-warn-bg); color: var(--color-warn);
  border: 0.1mm solid rgba(166,89,23,0.25);
}
.tt-tg-chip.mood-neutral, .tt-st-chip.mood-neutral, .tt-bx-chip.mood-neutral {
  background: var(--color-gold-tint); color: var(--color-gold-deep);
  border: 0.1mm solid var(--color-gold-soft);
}
.tt-tg-chip .hz, .tt-st-chip .hz, .tt-bx-chip .hz {
  font-family: var(--font-serif-tc); font-weight: 700; font-size: 8pt;
}
.tt-tg-indo, .tt-st-indo, .tt-bx-indo {
  font-size: 6.5pt; color: inherit; opacity: 0.85;
}
"""
