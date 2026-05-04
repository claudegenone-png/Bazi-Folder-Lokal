"""V4.8 Component Primitives — building blocks for all page templates.

All primitives produce HTML strings using design system classes.
Tokens come from design_system/tokens.css.
"""
import re
import html as _html
from lookups.hanzi_universal import gloss, gloss_pinyin


def _esc(s):
    return _html.escape(s or "", quote=False)


# ─────────────────────────────────────────────────────────────────────────
# HanziGloss — Hanzi with Indo translation underneath (or inline)
# ─────────────────────────────────────────────────────────────────────────

def hz_gloss(hz: str, indo: str = None, inline: bool = False) -> str:
    """Render Hanzi + Indo gloss. Auto-lookup if indo not provided."""
    if not hz:
        return _esc(indo or "")
    if indo is None:
        indo = gloss(hz) or ""
    if inline:
        suffix = f' <em class="tt-inline">({_esc(indo)})</em>' if indo else ""
        return f'<span class="hz">{_esc(hz)}</span>{suffix}'
    if not indo:
        return f'<span class="hz">{_esc(hz)}</span>'
    return (
        f'<span class="hz-tt">'
        f'<span class="hz">{_esc(hz)}</span>'
        f'<span class="tt">{_esc(indo)}</span>'
        f'</span>'
    )


def gloss_text(text: str) -> str:
    """Auto-gloss every recognized Hanzi term in a text. Returns HTML.
    Tokenizes to keep <strong>/<em> HTML intact (don't escape these tags).
    """
    if not text:
        return ""
    # Convert **bold** and *italic* to HTML tags BEFORE char-level processing
    text = re.sub(r"\*\*([^*]+)\*\*", r"<<<S>>>\1<<</S>>>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<<<E>>>\1<<</E>>>", text)
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        # Sentinel-tag passthrough (don't escape)
        if text[i:i+5] == "<<<S>>>" or text[i:i+5] == "<<<E>>>" or text[i:i+6] == "<<</S>>>" or text[i:i+6] == "<<</E>>>":
            pass
        if text.startswith("<<<S>>>", i):
            out.append("<strong>"); i += 7; continue
        if text.startswith("<<</S>>>", i):
            out.append("</strong>"); i += 8; continue
        if text.startswith("<<<E>>>", i):
            out.append("<em>"); i += 7; continue
        if text.startswith("<<</E>>>", i):
            out.append("</em>"); i += 8; continue
        if "一" <= ch <= "鿿":
            matched = None
            for L in (4, 3, 2, 1):
                if i + L <= n:
                    cand = text[i:i+L]
                    g = gloss(cand)
                    if g:
                        matched = (cand, g, L)
                        break
            if matched:
                cand, g, L = matched
                out.append(hz_gloss(cand, g))
                i += L
            else:
                out.append(f'<span class="hz">{ch}</span>')
                i += 1
        else:
            out.append(_esc(ch))
            i += 1
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────
# Card — generic content container with variants
# ─────────────────────────────────────────────────────────────────────────

def card(body: str, *, variant: str = "default", title: str = None,
         hz: str = None, icon: str = None, klass: str = "") -> str:
    """variant: default | primary | gold | muted | success | warn | danger"""
    head = ""
    if title or hz or icon:
        icon_html = f'<span class="card-icon">{_esc(icon)}</span>' if icon else ""
        title_html = f'<span class="card-title-id">{_esc(title)}</span>' if title else ""
        hz_html = f'<span class="card-title-hz">{_esc(hz)}</span>' if hz else ""
        head = f'<div class="card-head">{icon_html}{title_html}{hz_html}</div>'
    return f'<div class="card v-{variant} {klass}">{head}<div class="card-body">{body}</div></div>'


# ─────────────────────────────────────────────────────────────────────────
# KeyValue list — definition list-like rows
# ─────────────────────────────────────────────────────────────────────────

def kv_row(label: str, value_html: str, hz_label: str = None) -> str:
    hz = f'<span class="kv-label-hz">{_esc(hz_label)}</span>' if hz_label else ""
    return (
        f'<div class="kv-row">'
        f'<div class="kv-label">{_esc(label)}{hz}</div>'
        f'<div class="kv-value">{value_html}</div>'
        f'</div>'
    )


def kv_list(items: list, *, columns: int = 1) -> str:
    """items: [(label, value_html, hz_label?)] tuples or dicts"""
    rows = []
    for it in items:
        if isinstance(it, dict):
            rows.append(kv_row(it.get("label", ""), it.get("value", ""), it.get("hz_label")))
        else:
            label, value = it[0], it[1]
            hz_label = it[2] if len(it) > 2 else None
            rows.append(kv_row(label, value, hz_label))
    cls = f"kv-list cols-{columns}"
    return f'<div class="{cls}">{"".join(rows)}</div>'


# ─────────────────────────────────────────────────────────────────────────
# Bullet list — styled with ◆ marker, supports {label, text} or plain str
# ─────────────────────────────────────────────────────────────────────────

def bullet_list(items: list, *, mood: str = "neutral", icon: str = "◆") -> str:
    """items: list of strings OR list of {label, text} dicts/Bullet."""
    if not items:
        return ""
    out = []
    for it in items:
        if hasattr(it, 'label'):  # Bullet dataclass
            label = it.label or ""
            text = it.text or ""
        elif isinstance(it, dict):
            label = it.get("label", "")
            text = it.get("text", "")
        else:
            label = ""
            text = str(it)
        if label:
            out.append(f'<li><strong>{_esc(label)}</strong> — {_esc(text)}</li>')
        else:
            out.append(f'<li>{_esc(text)}</li>')
    return f'<ul class="bullet-list mood-{mood}" data-icon="{_esc(icon)}">{"".join(out)}</ul>'


# ─────────────────────────────────────────────────────────────────────────
# MoodChip — colored tag (good/warn/bad/neutral)
# ─────────────────────────────────────────────────────────────────────────

def mood_chip(text: str, mood: str = "neutral", hz: str = None) -> str:
    hz_html = f' <span class="hz">{_esc(hz)}</span>' if hz else ""
    return f'<span class="mood-chip m-{mood}">{_esc(text)}{hz_html}</span>'


# ─────────────────────────────────────────────────────────────────────────
# Section divider with ornament
# ─────────────────────────────────────────────────────────────────────────

def divider(glyph: str = "❖") -> str:
    return (
        f'<div class="divider">'
        f'<span class="divider-line"></span>'
        f'<span class="divider-glyph">{_esc(glyph)}</span>'
        f'<span class="divider-line"></span>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────
# Section heading — used inside page content (not page header)
# ─────────────────────────────────────────────────────────────────────────

def section_h2(title: str, hz: str = None, ornament: str = "❖") -> str:
    hz_html = f'<span class="sh-hz">{_esc(hz)}</span>' if hz else ""
    return (
        f'<div class="sh-h2">'
        f'<span class="sh-orn">{_esc(ornament)}</span>'
        f'<span class="sh-id">{_esc(title)}</span>'
        f'{hz_html}'
        f'</div>'
    )


def section_h3(title: str, hz: str = None) -> str:
    hz_html = f' <span class="sh-hz">{_esc(hz)}</span>' if hz else ""
    return f'<div class="sh-h3">{_esc(title)}{hz_html}</div>'


# ─────────────────────────────────────────────────────────────────────────
# Quote / Callout
# ─────────────────────────────────────────────────────────────────────────

def callout(text: str, *, variant: str = "info", icon: str = "💡") -> str:
    """text accepts HTML (callers may pass <strong>X</strong>). Don't double-escape."""
    return (
        f'<div class="callout v-{variant}">'
        f'<span class="co-icon">{_esc(icon)}</span>'
        f'<div class="co-text">{text}</div>'
        f'</div>'
    )


def quote_block(text: str, source: str = None) -> str:
    src = f'<div class="qb-source">— {_esc(source)}</div>' if source else ""
    return (
        f'<blockquote class="quote-block">'
        f'<div class="qb-text">{_esc(text)}</div>'
        f'{src}'
        f'</blockquote>'
    )


def verse_block(hanzi: str, terjemahan: str = None, source: str = None) -> str:
    """Classical Chinese verse with auto-translation underneath."""
    src = f'<div class="vb-source">{_esc(source)}</div>' if source else ""
    tr = f'<div class="vb-tr">({_esc(terjemahan)})</div>' if terjemahan else ""
    return (
        f'<div class="verse-block">'
        f'{src}'
        f'<div class="vb-hz hz">{_esc(hanzi)}</div>'
        f'{tr}'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────
# CSS for primitives (concatenated into final stylesheet)
# ─────────────────────────────────────────────────────────────────────────

PRIMITIVES_CSS = """
/* === Card === */
.card {
  background: var(--color-paper); border-radius: var(--r-md);
  padding: var(--sp-3) var(--sp-4); margin: 0 0 var(--sp-3) 0;
  border: var(--bw-hair) solid var(--color-gold-soft);
  box-shadow: var(--sh-soft);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.card.v-primary { border-left: var(--bw-thick) solid var(--color-red); }
.card.v-gold    { border-left: var(--bw-thick) solid var(--color-gold); }
.card.v-muted   { background: var(--color-gold-tint); }
.card.v-success { background: var(--color-success-bg); border-left: var(--bw-thick) solid var(--color-success); }
.card.v-warn    { background: var(--color-warn-bg);    border-left: var(--bw-thick) solid var(--color-warn); }
.card.v-danger  { background: var(--color-danger-bg);  border-left: var(--bw-thick) solid var(--color-danger); }

.card-head {
  display: flex; align-items: baseline; gap: var(--sp-2);
  margin-bottom: var(--sp-2);
  padding-bottom: var(--sp-1); border-bottom: 0.15mm solid var(--color-gold-soft);
}
.card-icon { font-size: 12pt; }
.card-title-id { font-family: var(--font-display); font-size: 11.5pt; color: var(--color-red); font-weight: 600; letter-spacing: 0.4px; }
.card-title-hz { font-family: var(--font-serif-tc); font-size: 9.5pt; color: var(--color-muted); margin-left: auto; }
.card-body { font-size: var(--type-body); line-height: 1.55; }

/* === Key-value list === */
.kv-list { display: grid; gap: 1mm; }
.kv-list.cols-2 { grid-template-columns: 1fr 1fr; gap: 1mm var(--sp-4); }
.kv-list.cols-3 { grid-template-columns: 1fr 1fr 1fr; gap: 1mm var(--sp-4); }
.kv-row {
  display: grid; grid-template-columns: 50mm 1fr; gap: var(--sp-3);
  padding: 1mm 0; align-items: baseline;
  border-bottom: 0.1mm dashed var(--color-gold-soft);
}
.kv-row:last-child { border-bottom: none; }
.kv-label {
  font-family: var(--font-display); font-size: 8.5pt;
  color: var(--color-gold-deep); font-weight: 600;
  letter-spacing: 1px; text-transform: uppercase;
  display: flex; flex-direction: column;
}
.kv-label-hz { font-family: var(--font-serif-tc); font-size: 8pt; color: var(--color-muted); letter-spacing: 0; text-transform: none; margin-top: 0.3mm; }
.kv-value { font-size: var(--type-body); color: var(--color-ink); line-height: 1.45; }
.kv-value .hz { color: var(--color-red); font-weight: 600; }

/* === Bullet list === */
.bullet-list { margin: 0 0 var(--sp-2) 0; padding: 0; list-style: none; }
.bullet-list li {
  position: relative; padding: 0.6mm 0 0.6mm 5mm;
  margin-bottom: 0.6mm; line-height: 1.5;
  font-size: var(--type-body); color: var(--color-ink);
}
.bullet-list li::before {
  content: "◆"; color: var(--color-gold); position: absolute; left: 1mm;
  font-size: 7pt; top: 1.6mm;
}
.bullet-list.mood-good li::before  { content: "✓"; color: var(--color-success); }
.bullet-list.mood-warn li::before  { content: "!"; color: var(--color-warn); font-weight: 700; }
.bullet-list.mood-bad li::before   { content: "×"; color: var(--color-danger); font-weight: 700; }
.bullet-list li strong { color: var(--color-red); font-weight: 600; }

/* === Mood chip === */
.mood-chip {
  display: inline-flex; align-items: center; gap: 1mm;
  padding: 0.5mm 2mm; border-radius: var(--r-sm);
  font-size: 7.5pt; font-weight: 600; letter-spacing: 0.5px;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.mood-chip.m-good    { background: var(--color-success-bg); color: var(--color-success); }
.mood-chip.m-warn    { background: var(--color-warn-bg);    color: var(--color-warn); }
.mood-chip.m-bad     { background: var(--color-danger-bg);  color: var(--color-danger); }
.mood-chip.m-neutral { background: var(--color-gold-tint);  color: var(--color-gold-deep); }
.mood-chip .hz { font-family: var(--font-serif-tc); font-size: 8.5pt; }

/* === Divider ornament === */
.divider { display: flex; align-items: center; gap: var(--sp-2); margin: var(--sp-3) 0; }
.divider-line {
  flex: 1; height: var(--bw-hair);
  background: linear-gradient(90deg, transparent 0%, var(--color-gold) 50%, transparent 100%);
}
.divider-glyph { color: var(--color-gold); font-size: 10pt; }

/* === Section heading inside content === */
.sh-h2 {
  display: flex; align-items: baseline; gap: var(--sp-2);
  font-family: var(--font-display); color: var(--color-red);
  font-size: 13pt; font-weight: 700; letter-spacing: 0.6px;
  margin: var(--sp-4) 0 var(--sp-2) 0;
  padding-bottom: 1.2mm; border-bottom: 0.3mm solid var(--color-gold-soft);
}
.sh-h2 .sh-orn { color: var(--color-gold); font-size: 10pt; }
.sh-h2 .sh-hz { font-family: var(--font-serif-tc); font-size: 9.5pt; color: var(--color-muted); margin-left: auto; letter-spacing: 2px; }
.sh-h3 {
  font-family: var(--font-display); font-size: 11pt; font-weight: 600;
  color: var(--color-red); margin: var(--sp-3) 0 var(--sp-1) 0;
  letter-spacing: 0.3px;
}
.sh-h3 .sh-hz { font-family: var(--font-serif-tc); font-size: 9pt; color: var(--color-muted); margin-left: var(--sp-1); }

/* === Callout === */
.callout {
  display: grid; grid-template-columns: 8mm 1fr; gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-3); border-radius: var(--r-sm);
  margin: var(--sp-2) 0;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.callout .co-icon { font-size: 11pt; align-self: start; padding-top: 0.4mm; }
.callout .co-text { font-size: var(--type-small); line-height: 1.5; color: var(--color-ink-soft); }
.callout.v-info    { background: var(--color-gold-tint); border-left: var(--bw-med) solid var(--color-gold); }
.callout.v-success { background: var(--color-success-bg); border-left: var(--bw-med) solid var(--color-success); }
.callout.v-warn    { background: var(--color-warn-bg); border-left: var(--bw-med) solid var(--color-warn); }
.callout.v-danger  { background: var(--color-danger-bg); border-left: var(--bw-med) solid var(--color-danger); }

/* === Quote block === */
.quote-block {
  background: linear-gradient(180deg, #FDF8EE 0%, #F8EFD7 100%);
  border-left: 0.8mm solid var(--color-gold);
  padding: var(--sp-3) var(--sp-4) var(--sp-3) var(--sp-6);
  border-radius: 0 var(--r-md) var(--r-md) 0;
  margin: var(--sp-2) 0; position: relative; font-style: italic;
  font-size: var(--type-small); color: var(--color-ink-soft);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.quote-block::before {
  content: "“"; position: absolute; left: 1.5mm; top: 0;
  font-family: var(--font-display); font-size: 22pt;
  color: var(--color-gold); line-height: 1;
}
.qb-source {
  margin-top: var(--sp-1); font-style: normal; font-size: 7.5pt;
  color: var(--color-gold-deep); letter-spacing: 1px; text-transform: uppercase;
}

/* === Verse block (classical Chinese with translation) === */
.verse-block {
  margin: var(--sp-3) 0; text-align: center;
  background: linear-gradient(180deg, #FDF8EE 0%, #F4E8CC 100%);
  border-top: 0.3mm solid var(--color-gold);
  border-bottom: 0.3mm solid var(--color-gold);
  padding: var(--sp-3) var(--sp-5);
  position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.verse-block::before, .verse-block::after {
  content: "❋"; position: absolute; color: var(--color-red); font-size: 9pt;
  top: 50%; transform: translateY(-50%);
}
.verse-block::before { left: 2mm; }
.verse-block::after { right: 2mm; }
.vb-source {
  font-family: var(--font-display); font-size: 8pt;
  color: var(--color-gold-deep); letter-spacing: 2px;
  text-transform: uppercase; font-weight: 700; margin-bottom: var(--sp-1);
}
.vb-hz {
  font-family: var(--font-serif-tc); font-size: 11pt; line-height: 1.85;
  color: #2a1810; letter-spacing: 1.5px; font-weight: 500;
}
.vb-tr {
  margin-top: var(--sp-2); padding-top: 1mm;
  border-top: 0.1mm dashed var(--color-gold-soft);
  font-size: 8pt; line-height: 1.5; color: var(--color-muted);
  font-style: italic; text-align: justify;
}

/* === HanziGloss === */
.hz-tt { display: inline-flex; flex-direction: column; align-items: center; line-height: 1; vertical-align: middle; margin: 0 0.4mm; }
.hz-tt > .hz { font-size: 1em; font-weight: 600; color: var(--color-red); line-height: 1.1; }
.hz-tt > .tt { font-size: 0.6em; line-height: 1.1; color: var(--color-muted); margin-top: 0.4mm; max-width: 18mm; text-align: center; word-break: break-word; }
.tt-inline { color: var(--color-muted); font-style: italic; font-size: 0.85em; }
.hz { font-family: var(--font-serif-tc); }
"""
