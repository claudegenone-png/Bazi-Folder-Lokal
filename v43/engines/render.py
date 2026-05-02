"""Sandbox1 Render Engine — JSON → 23 HTML pages → PDF.

Strategy: Templates = verbatim copies of Michele V3 pages.
Reference values = Michele's actual data baked into engine constants.
For each subject, build (reference_string → subject_string) substitutions, apply
across all templates, then concat → master → PDF.

Validation: Michele JSON renders identically to V3 Michele PDF (zero substitution).
"""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

from lookups import STEMS, BRANCHES, BRANCH_ORDER, WHEEL_POSITIONS, TRIGRAMS, COMPASS_POSITIONS, stem_pillar_text, branch_pillar_text

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data" / "subjects"
BUILD_DIR = ROOT / "_build"
ONEDRIVE = Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan")

PAGE_ORDER = [
    "page_01_cover.html","page_02_toc.html","page_03_intro.html",
    "page_profile.html","page_05_bazi_opener.html","page_06_daymaster.html",
    "page_marriage.html","page_08_xingqing.html","page_09_family.html",
    "page_10_shensha.html","page_11_caifu.html","page_career.html",
    "page_yangzhai.html","page_dayun.html","page_15_ziwei_opener.html",
    "page_ziwei.html","page_17_palace1.html","page_18_palace2.html",
    "page_19_palace3.html","page_20_kesimpulan.html","page_synthesis.html",
    "page_22_glossary.html","page_23_disclaimer.html"
]

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

# ============================================================
# MICHELE REFERENCE — exact values pulled from cache/michele templates
# ============================================================
MICHELE = {  # name kept for backward compat; this is now LinRuYi reference
    "name_id": "Lin Ru Yi",
    "name_hanzi": "林如意",
    "gender_id": "Wanita",
    "birth_date_text": "30 Mei 1995",
    "birth_day_name": "Selasa",
    "birth_time": "10:35",
    "birth_period_id": "pagi",
    "birth_hour_branch_hz": "巳",
    "birth_hour_period_label": "pagi · 巳時",
    "lunar_date_text_new": "tanggal 2 bulan 5 tahun 乙亥 (Yi Hai · 1995)",
    "lunar_year_pillar_hz": "乙亥",
    "lunar_republic": "民國 84 年 5 月 2 日",
    "age_at_report": 30,
    "shio_branch_hz": "亥",
    "shio_id": "Babi",
    "shio_id_upper": "BABI",
    "shio_svg_red": "Babi-Merah.svg",
    "dm_stem_hz": "辛",
    "dm_element_hz": "金",
    "dm_label_id": "Logam Halus",
    "pillars": {
        "year":  ("乙", "亥"),
        "month": ("辛", "巳"),
        "day":   ("辛", "酉"),
        "hour":  ("癸", "巳"),
    },
    "wuxing": {
        "jin":  {"value": 4.0, "percent": 28.6},
        "shui": {"value": 4.0, "percent": 28.6},
        "tu":   {"value": 3.0, "percent": 21.4},
        "mu":   {"value": 2.0, "percent": 14.3},
        "huo":  {"value": 1.0, "percent": 7.1},
        "total": 14,
        "self_value": 4.0,
        "self_el_hz": "金",
        "fav_hz": "金 水",
        "unfav_hz": "火 木",
        "axis_max": "14 Total",
        "insight_id": "<strong>Logam &amp; Air dominan</strong> (金 28.6% · 水 28.6%) didukung Tanah (土 21.4%). Penguasa Hari 辛金 cenderung lemah karena ditekan dua 巳 火 — energinya perlu sokongan <strong>金 水</strong> (logam menopang, air meredam api), hindari tambahan <strong>火 木</strong>.",
    },
    "format": {
        "hz": "正官格",
        "glyph_hz": "正官",
        "pinyin": "Zheng Guan Ge",
        "label_id": "Penjaga Disiplin",
    },
    "yong_shen": {
        "elements_hz": "金 水",
        "glyph_hz": "金<span style=\"opacity:0.5\">·</span>水",
        "name_id": "Logam &amp; Air",
        "desc_id": "Penopang &amp; peredam",
    },
    "ji_shen": {
        "elements_hz": "火 木",
        "glyph_hz": "火<span style=\"opacity:0.5\">·</span>木",
        "name_id": "Api &amp; Kayu",
        "desc_id": "Pelumat &amp; pemicu",
    },
    "mantra": {
        "hz": "文武相濟",
        "pinyin": "Wén Wǔ Xiāng Jì",
    },
    "zi_wei": {
        "ming_zhu_hz": "貪狼",   "ming_zhu_id": "Penguasa Hidup · Hasrat",
        "shen_zhu_hz": "天機",   "shen_zhu_id": "Penguasa Tubuh · Strategi",
        "ming_gong_hz": "子",    "ming_gong_id": "Istana Hidup · Tikus",
        "shen_gong_hz": "寅",    "shen_gong_id": "Istana Tubuh · Harimau",
        "wu_xing_ju_hz": "火六局","wu_xing_ju_id": "Aliran Api Enam",
        "shi_jun_hz": "寅",      "shi_jun_id": "Penguasa Waktu · Harimau",
    },
}

# ============================================================
# SUBSTITUTION HELPERS
# ============================================================

def html_amp(s: str) -> str:
    """Escape ' & ' → ' &amp; ' (only standalone ampersand+space, won't double-encode)."""
    return s.replace(" & ", " &amp; ")


def fmt_ys_glyph(elements_hz: str) -> str:
    """e.g. '火 金' → '火<span style=\"opacity:0.5\">·</span>金'."""
    parts = elements_hz.split()
    return '<span style="opacity:0.5">·</span>'.join(parts)


def fmt_birth_date_id(iso: str) -> str:
    months = ["", "Januari","Februari","Maret","April","Mei","Juni",
              "Juli","Agustus","September","Oktober","November","Desember"]
    y, m, d = iso.split("-")
    return f"{int(d)} {months[int(m)]} {int(y)}"


def gregorian_to_lunar_republic_label(iso: str, lunar_md: tuple[int,int,int] | None = None) -> str:
    """ROC year = Gregorian year - 1911. lunar_md = (lunar_y, lunar_m, lunar_d).
    If lunar_md not given, fallback to placeholder format using gregorian m/d.
    """
    y = int(iso.split("-")[0])
    roc = y - 1911
    if lunar_md:
        ly, lm, ld = lunar_md
        return f"民國 {roc} 年 {lm} 月 {ld} 日"
    # fallback: return ROC year only
    return f"民國 {roc} 年"


def build_pillar_pairs(michele_pillar, subject_pillar):
    """Single multi-line block sub per pillar."""
    m_stem, m_branch = michele_pillar
    s_stem = subject_pillar["stem_hz"]
    s_branch = subject_pillar["branch_hz"]
    if m_stem == s_stem and m_branch == s_branch:
        return []
    m_s = STEMS[m_stem]; s_s = STEMS[s_stem]
    m_b = BRANCHES[m_branch]; s_b = BRANCHES[s_branch]
    NL = chr(10)
    parts_m = [
        f'<div class="t-hanzi stem">{m_stem}</div>',
        f'          <div class="t-pill"><span class="hz">{m_s["el_hz"]}</span>{m_s["el_id"]} {m_s["polarity_id"]}</div>',
        '        </div>',
        '        <div class="t-divider"></div>',
        '        <div class="t-block">',
        f'          <div class="t-hanzi branch">{m_branch}</div>',
        f'          <div class="t-pill"><span class="hz">{m_b["shio_radical_hz"]}</span>{m_b["shio_id"]}</div>',
    ]
    parts_s = [
        f'<div class="t-hanzi stem">{s_stem}</div>',
        f'          <div class="t-pill"><span class="hz">{s_s["el_hz"]}</span>{s_s["el_id"]} {s_s["polarity_id"]}</div>',
        '        </div>',
        '        <div class="t-divider"></div>',
        '        <div class="t-block">',
        f'          <div class="t-hanzi branch">{s_branch}</div>',
        f'          <div class="t-pill"><span class="hz">{s_b["shio_radical_hz"]}</span>{s_b["shio_id"]}</div>',
    ]
    return [(NL.join(parts_m), NL.join(parts_s))]


def build_substitutions(subject: dict) -> list[tuple[str,str]]:
    """Build comprehensive (search, replace) pairs from Michele→subject.

    Order matters: longer/more-specific patterns first.
    """
    iden = subject["identity"]
    shio = subject["shio"]
    dm = subject["day_master"]
    pillars = subject["pillars"]

    pairs: list[tuple[str,str]] = []

    # ============ COVER (LinRuYi dual-date format) ============
    # Cover row 1: Tanggal Lahir (Indonesia)
    s_birth_date = fmt_birth_date_id(iden["birth_date"])
    s_day_name = iden.get("birth_day_name", "")
    pairs.append((
        f'<span class="val">{MICHELE["birth_date_text"]} <em>({MICHELE["birth_day_name"]})</em></span>',
        f'<span class="val">{s_birth_date} <em>({s_day_name})</em></span>'
    ))
    # Cover row 2: Tanggal Lahir (Tionghoa) — substitute the prefix "tanggal X bulan Y" only;
    # the year hz <span> + (Yi Hai · YYYY) <em> handled via shared lunar_year_pillar_hz sub
    # Michele template prefix: "tanggal 2 bulan 5"
    s_lunar_new = iden.get("lunar_date_text_new", "")
    if s_lunar_new:
        # Extract prefix before "tahun " from both
        m_prefix = MICHELE["lunar_date_text_new"].split(" tahun ")[0]  # "tanggal 2 bulan 5"
        s_prefix = s_lunar_new.split(" tahun ")[0]
        if m_prefix != s_prefix:
            pairs.append((m_prefix, s_prefix))
        # Year label part "(Yi Hai · 1995)" — extract from inside <em>...</em>
        # Format: "tanggal X bulan Y tahun ZZ (Yi Hai · YYYY)"
        if "(" in s_lunar_new and "(" in MICHELE["lunar_date_text_new"]:
            m_paren = "(" + MICHELE["lunar_date_text_new"].split("(", 1)[1]  # "(Yi Hai · 1995)"
            s_paren = "(" + s_lunar_new.split("(", 1)[1]
            if m_paren != s_paren:
                pairs.append((m_paren, s_paren))
    # Cover row 3: Waktu Lahir
    s_period_label = iden.get("birth_hour_period_label", iden.get("birth_period_id", "siang"))
    pairs.append((
        f'pukul {MICHELE["birth_time"]} <em>({MICHELE["birth_hour_period_label"]})</em>',
        f'pukul {iden["birth_time"]} <em>({s_period_label})</em>'
    ))
    # Subject-detail raw time (page profile)
    pairs.append((f"· {MICHELE['birth_time']} ·", f"· {iden['birth_time']} ·"))
    # Lunar year pillar hz
    pairs.append((MICHELE["lunar_year_pillar_hz"], pillars["year"]["stem_hz"]+pillars["year"]["branch_hz"]))

    # Cover shio badge: '亥 · BABI'
    pairs.append((f"'{MICHELE['shio_branch_hz']} · {MICHELE['shio_id_upper']}'",
                  f"'{shio['branch_hz']} · {shio['id_upper']}'"))

    # ============ NAME ============
    if iden.get("name_hanzi") and iden["name_hanzi"] != MICHELE["name_hanzi"]:
        pairs.append((MICHELE["name_hanzi"], iden["name_hanzi"]))
    pairs.append((MICHELE["name_id"], iden["name_id"]))

    # ============ GENDER ============
    if iden.get("gender_id") and iden["gender_id"] != MICHELE["gender_id"]:
        pairs.append((MICHELE["gender_id"], iden["gender_id"]))

    # Raw birth_date_text (subject-detail in subject-bar)
    if iden["birth_date"] != "1995-05-30":  # differ from LinRuYi
        pairs.append((MICHELE["birth_date_text"], fmt_birth_date_id(iden["birth_date"])))

    # ============ AGE ============
    pairs.append((f"Umur {MICHELE['age_at_report']} tahun",
                  f"Umur {iden['age_at_report']} tahun"))

    # ============ SUBJECT-BAR LUNAR REPUBLIC ============
    # Michele: "民國 84 年 6 月 25 日"
    # Best-effort: subject may not provide lunar_md; fallback derives ROC year only
    s_lunar = iden.get("lunar_republic_text")
    if not s_lunar:
        s_lunar = gregorian_to_lunar_republic_label(iden["birth_date"])
    pairs.append((MICHELE["lunar_republic"], s_lunar))

    # ============ SHIO (subject-bar text) ============
    # 亥 Babi → 子 Tikus
    pairs.append((f"{MICHELE['shio_branch_hz']} {MICHELE['shio_id']}",
                  f"{shio['branch_hz']} {shio['id']}"))
    # Cover info-panel: <span class="hz">亥</span> Babi
    pairs.append((f'<span class="hz">{MICHELE["shio_branch_hz"]}</span> {MICHELE["shio_id"]}',
                  f'<span class="hz">{shio["branch_hz"]}</span> {shio["id"]}'))
    # SVG image
    pairs.append((MICHELE["shio_svg_red"], shio["svg_red"]))
    pairs.append((f'alt="{MICHELE["shio_id"]}"', f'alt="{shio["id"]}"'))

    # ============ DAY MASTER STEM+ELEMENT compound ============
    # Subject-bar value: "辛金 · Logam Halus" → "甲木 · Pohon Besar"
    pairs.append((f"{MICHELE['dm_stem_hz']}{MICHELE['dm_element_hz']} · {MICHELE['dm_label_id']}",
                  f"{dm['stem_hz']}{dm['stem_element_hz']} · {dm['label_id']}"))
    # Cover row Penguasa Hari: "Logam Halus <span class=\"hz\">辛金</span>" → "Pohon Besar 甲木"
    pairs.append((f'{MICHELE["dm_label_id"]} <span class="hz">{MICHELE["dm_stem_hz"]}{MICHELE["dm_element_hz"]}</span>',
                  f'{dm["label_id"]} <span class="hz">{dm["stem_hz"]}{dm["stem_element_hz"]}</span>'))
    # Standalone label (catches "Logam Halus" elsewhere)
    if dm['label_id'] != MICHELE['dm_label_id']:
        pairs.append((MICHELE['dm_label_id'], dm['label_id']))
    # Standalone "辛金" → "甲木"
    pairs.append((f"{MICHELE['dm_stem_hz']}{MICHELE['dm_element_hz']}",
                  f"{dm['stem_hz']}{dm['stem_element_hz']}"))

    # DM long label "(Logam Yin)" → "(Kayu Yang)" — used in footer captions
    m_dm_long = f"({STEMS[MICHELE['dm_stem_hz']]['el_id']} {STEMS[MICHELE['dm_stem_hz']]['polarity_id']})"
    s_dm_long = f"({STEMS[dm['stem_hz']]['el_id']} {STEMS[dm['stem_hz']]['polarity_id']})"
    if m_dm_long != s_dm_long:
        pairs.append((m_dm_long, s_dm_long))

    # Generic format hz substitution (catches footer captions outside fmt-name div)
    fmt = subject.get("format")
    if fmt and fmt.get("hz") and fmt["hz"] != MICHELE["format"]["hz"]:
        pairs.append((MICHELE["format"]["hz"], fmt["hz"]))

    # ============ 4 PILLARS (page_profile) ============
    for slot in ["hour", "day", "month", "year"]:
        pairs.extend(build_pillar_pairs(MICHELE["pillars"][slot], pillars[slot]))

    # ============ WUXING (page_profile) ============
    # Skip simple field subs — handled via block replacement in apply_blocks().
    pass

    # ============ FORMAT card (page_profile) ============
    fmt = subject.get("format")
    if fmt:
        m_f = MICHELE["format"]
        # glyph
        pairs.append((f'<div class="fmt-glyph">{m_f["glyph_hz"]}</div>',
                      f'<div class="fmt-glyph">{fmt["hz"][:2]}</div>'))
        # name (e.g. 傷官格 → 正財格)
        pairs.append((f'<div class="fmt-name">{m_f["hz"]}</div>',
                      f'<div class="fmt-name">{fmt["hz"]}</div>'))
        # pinyin label
        pairs.append((f'<div class="fmt-pinyin">{m_f["pinyin"]} — "{m_f["label_id"]}"</div>',
                      f'<div class="fmt-pinyin">{fmt["pinyin"]} — "{fmt["label_id"]}"</div>'))

    # ============ YONG SHEN card ============
    ys = subject.get("yong_shen")
    if ys:
        m_ys = MICHELE["yong_shen"]
        pairs.append((f'<div class="ys-glyph">{m_ys["glyph_hz"]}</div>',
                      f'<div class="ys-glyph">{fmt_ys_glyph(ys["elements_hz"])}</div>'))
        pairs.append((f'<div class="ys-name">{m_ys["name_id"]}</div>',
                      f'<div class="ys-name">{html_amp(ys["elements_id"])}</div>'))
        pairs.append((f'<div class="ys-desc">{m_ys["desc_id"]}</div>',
                      f'<div class="ys-desc">{html_amp(ys["label_id"])}</div>'))

    # ============ JI SHEN card ============
    js = subject.get("ji_shen")
    if js:
        m_js = MICHELE["ji_shen"]
        pairs.append((f'<div class="ys-glyph">{m_js["glyph_hz"]}</div>',
                      f'<div class="ys-glyph">{fmt_ys_glyph(js["elements_hz"])}</div>'))
        pairs.append((f'<div class="ys-name">{m_js["name_id"]}</div>',
                      f'<div class="ys-name">{html_amp(js["elements_id"])}</div>'))
        pairs.append((f'<div class="ys-desc">{m_js["desc_id"]}</div>',
                      f'<div class="ys-desc">{html_amp(js["label_id"])}</div>'))

    # ============ MANTRA ============
    mt = subject.get("mantra")
    if mt:
        m_mt = MICHELE["mantra"]
        pairs.append((m_mt["hz"], mt["hz"]))
        pairs.append((m_mt["pinyin"], mt["pinyin"]))

    # ============ COVER row Elemen Utama ============
    # Pattern: ">{name_id} <span class="hz">{elements_hz}</span><"
    if ys:
        m_ys = MICHELE["yong_shen"]
        old_eu = f'>{m_ys["name_id"]} <span class="hz">{m_ys["elements_hz"]}</span><'
        new_eu = f'>{html_amp(ys["elements_id"])} <span class="hz">{ys["elements_hz"]}</span><'
        if old_eu != new_eu:
            pairs.append((old_eu, new_eu))

    # ============ ZI WEI center info ============
    zw = subject.get("zi_wei")
    if zw:
        m_zw = MICHELE["zi_wei"]
        # Each row: <div class="val">{HZ}<span class="id">{ID}</span></div>
        # Need to handle each unique pair carefully (some HZ may repeat e.g., 寅 in shen_gong + shi_jun)
        # Approach: replace the FULL "{HZ}<span..>{ID}</span>" string
        for key in ["ming_zhu", "shen_zhu", "ming_gong", "shen_gong", "wu_xing_ju", "shi_jun"]:
            m_hz = m_zw[f"{key}_hz"]
            m_id = m_zw[f"{key}_id"]
            s_hz = zw.get(f"{key}_hz", m_hz)
            s_id = zw.get(f"{key}_id", m_id)
            old = f'>{m_hz}<span class="id">{m_id}</span>'
            new = f'>{s_hz}<span class="id">{s_id}</span>'
            if old != new:
                # Use replace with count=1 since lookup is unique per ID text
                pairs.append((old, new))

        # Subject-detail: "五行局: <strong style="color:var(--red)">火六局</strong>"
        if zw.get("wu_xing_ju_hz") and zw["wu_xing_ju_hz"] != m_zw["wu_xing_ju_hz"]:
            pairs.append((
                f'五行局: <strong style="color:var(--red)">{m_zw["wu_xing_ju_hz"]}</strong>',
                f'五行局: <strong style="color:var(--red)">{zw["wu_xing_ju_hz"]}</strong>'
            ))

    return pairs


# ============================================================
# BLOCK REPLACEMENT — for structures that need regeneration
# ============================================================

ELEMENT_HZ = {"mu":"木", "shui":"水", "tu":"土", "huo":"火", "jin":"金"}


def regen_wuxing_stack(wx: dict) -> str:
    """Generate <div class=\"wux-stack\">...</div> with segments sorted by value desc.
    Format matches Michele's template: padding spaces BETWEEN class attr and style attr.
    """
    items = sorted(
        [(el, wx[el]["value"], wx[el]["percent"]) for el in ELEMENT_HZ],
        key=lambda x: -x[1]
    )
    lines = ['<div class="wux-stack">']
    for el, val, pct in items:
        # Pad after closing quote of class attr to align style= column
        # Michele: class="seg el-mu"<spaces>style="..."  where total width post-class fixed
        cls = f"el-{el}"
        pad = " " * (9 - len(cls))
        # value e.g., 3.0, 0.0, 2.5
        v_str = f"{val:g}" if val != int(val) else f"{int(val)}.0"
        # percent: 35.3% or 0% (integer percent if 0 → no decimal)
        if pct == int(pct):
            p_str = f"{int(pct)}%" if pct == 0 else f"{int(pct)}.0%"
        else:
            p_str = f"{pct}%"
        lines.append(f'          <div class="seg {cls}"{pad}style="flex:{v_str}"><span class="hz">{ELEMENT_HZ[el]}</span><span class="pct">{p_str}</span></div>')
    lines.append('        </div>')
    return '\n'.join(lines)


def replace_block(content: str, open_tag_pattern: str, new_inner: str, count: int = 1) -> str:
    """Replace contents between matching <div ...> and its </div> closer.

    open_tag_pattern: regex matching the opening tag (e.g., r'<div class="wux-stack">').
    new_inner: replacement HTML (without the opening/closing div).
    Uses a balanced-counting algorithm rather than greedy regex.
    """
    m = re.search(open_tag_pattern, content)
    if not m:
        return content
    start = m.start()
    after_open = m.end()
    # Find matching close — balance count of <div and </div
    depth = 1
    pos = after_open
    while depth > 0 and pos < len(content):
        next_open = content.find("<div", pos)
        next_close = content.find("</div>", pos)
        if next_close == -1:
            return content  # malformed
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + 6
    # pos now points just after the matching </div>
    end = pos
    return content[:start] + new_inner + content[end:]


def regen_lifeline(da_yun: dict) -> str:
    """Generate <div class=\"lifeline\">...</div> with 10 cells."""
    lines = ['<div class="lifeline">']
    for c in da_yun["cycles"]:
        cls_parts = ["ll-cell"]
        if c.get("is_current"):
            cls_parts.append("current")
        elif c["age_end"] < c.get("_anchor", 0):
            # not used
            pass
        # past = before current
        cls_parts.append(c["element_class"])
        # past detection: cycle index < current_index
        current_idx = da_yun.get("current_index", 0)
        if c["n"] - 1 < current_idx:
            cls_parts.insert(1, "past")
        cls = " ".join(cls_parts)
        lines.append(f'        <div class="{cls}">')
        lines.append(f'          <div class="age">{c["age_start"]}–{c["age_end"]}</div>')
        lines.append(f'          <div class="gz"><span class="s">{c["stem_hz"]}</span><span class="b">{c["branch_hz"]}</span></div>')
        lines.append(f'          <div class="ss">{c["ten_god_hz"]}</div>')
        lines.append(f'          <div class="ss-id">{c["ten_god_id"]}</div>')
        lines.append(f'        </div>')
    lines.append('      </div>')
    return '\n'.join(lines)


def regen_lifeline_axis(da_yun: dict) -> str:
    """Generate <div class=\"ll-axis\">...</div>."""
    marks = da_yun["axis_marks"]
    # Michele format: 5 spans on one line, 6 spans on another
    line1 = ''.join(f'<span>{m}</span>' for m in marks[:5])
    line2 = ''.join(f'<span>{m}</span>' for m in marks[5:])
    return (
        '<div class="ll-axis">\n'
        f'        {line1}\n'
        f'        {line2}\n'
        '      </div>'
    )


def regen_spotlight(da_yun: dict, dm: dict) -> str:
    """Generate <div class=\"spotlight\">...</div>.

    Subject JSON must provide rich HTML strings for spotlight content:
      spotlight_tag_tone_html (e.g., 'Api · ekspresif' or 'Api · kolaboratif')
      spotlight_tag_combo_html (e.g., 'Output Mekar' or 'Sekutu &amp; Tekanan')
      spotlight_headline_html (with <span class="hz">...</span>)
      spotlight_bullets_html (list of HTML strings with <strong>, <span>, etc)
    """
    cur_idx = da_yun.get("current_index", 0)
    cur = da_yun["cycles"][cur_idx]
    el_hz = STEMS[cur["stem_hz"]]["el_hz"]
    el_id = STEMS[cur["stem_hz"]]["el_id"]
    el_class = cur.get("element_class", "el-mu").replace("el-", "s-")
    bullets = da_yun.get("spotlight_bullets_html", da_yun.get("spotlight_bullets", []))
    bullets_html = '\n'.join(
        '          <div class="sp-bullet">\n'
        f'            <div class="num">{i+1}</div>\n'
        f'            <div class="txt">{b}</div>\n'
        '          </div>'
        for i, b in enumerate(bullets)
    )
    headline = da_yun.get("spotlight_headline_html",
                          da_yun.get("spotlight_headline_id", ""))
    ten_god_pinyin = TEN_GOD_PINYIN.get(cur["ten_god_hz"], "")
    tag_tone = da_yun.get("spotlight_tag_tone_html", f"{el_id} · ekspresif")
    tag_combo = da_yun.get("spotlight_tag_combo_html", "Kombinasi")
    # Combo references which 2nd char? Michele's pattern: 丙+甲 (stem+DM_stem). Tommy's: 丁+亥 (stem+branch).
    # We provide subject control via spotlight_tag_combo_pair (default: stem+branch).
    combo_pair = da_yun.get("spotlight_tag_combo_pair", [cur["stem_hz"], cur["branch_hz"]])

    return (
        '<div class="spotlight">\n'
        '\n'
        '      <div class="sp-left">\n'
        f'        <div class="sp-eyebrow">FASE {cur["n"]} · SEKARANG</div>\n'
        f'        <div class="sp-gz"><span>{cur["stem_hz"]}</span><span>{cur["branch_hz"]}</span></div>\n'
        f'        <div class="sp-element-disc {el_class}">{el_hz}</div>\n'
        f'        <div class="sp-age">Umur <span class="now">{cur["age_start"]} — {cur["age_end"]}</span></div>\n'
        '      </div>\n'
        '\n'
        '      <div class="sp-right">\n'
        '        <div class="sp-tags">\n'
        f'          <span class="sp-tag primary"><span class="hz">{cur["ten_god_hz"]}</span>{ten_god_pinyin} · {cur["ten_god_id"]}</span>\n'
        f'          <span class="sp-tag"><span class="hz">{el_hz}</span>{tag_tone}</span>\n'
        f'          <span class="sp-tag"><span class="hz">{combo_pair[0]}</span>+<span class="hz">{combo_pair[1]}</span>{tag_combo}</span>\n'
        '        </div>\n'
        '\n'
        '        <div class="sp-headline">\n'
        f'          {headline}\n'
        '        </div>\n'
        '\n'
        '        <div class="sp-bullets">\n'
        f'{bullets_html}\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>'
    )


def regen_seasons_bar(da_yun: dict) -> str:
    """Generate <div class=\"seasons-bar\">...</div>."""
    seasons = da_yun.get("seasons", [])
    flex = 100 // max(len(seasons), 1) if seasons else 20
    flex = 20  # always 20 to match Michele
    lines = ['<div class="seasons-bar">']
    for s in seasons:
        cls = f's-{s["el_class"][2:] if s["el_class"].startswith("s-") else s["el_class"][3:]}'
        # Above logic: if "s-mu" → "s-mu", if "el-mu" → "s-mu". simplify:
        if s["el_class"].startswith("s-"):
            cls = s["el_class"]
        else:
            cls = "s-" + s["el_class"].split("-",1)[1]
        if s.get("is_current"):
            cls += " current"
        lines.append(f'        <div class="season {cls}" style="flex:{flex}">')
        lines.append(f'          <div class="s-hz">{s["el_hz"]}</div>')
        lines.append(f'          <div class="s-name">{html_amp(s["name_id"])}</div>')
        lines.append(f'          <div class="s-age">{s["age_start"]}–{s["age_end"]}</div>')
        lines.append(f'        </div>')
    lines.append('      </div>')
    return '\n'.join(lines)


def regen_seasons_axis(da_yun: dict) -> str:
    """Generate <div class=\"seasons-axis\">...</div>.

    Marks: [season1.start, season2.start, ..., seasonN.start, seasonN.end].
    """
    seasons = da_yun.get("seasons", [])
    if not seasons:
        return '<div class="seasons-axis"></div>'
    marks = [s["age_start"] for s in seasons] + [seasons[-1]["age_end"]]
    spans = ''.join(f'<span>{m}</span>' for m in marks)
    return f'<div class="seasons-axis">\n        {spans}\n      </div>'


# ============================================================
# MARRIAGE WHEEL SVG — 12 cells + relationship lines
# ============================================================

# Relationship → wheel cell styling
WHEEL_STYLE = {
    "self": {
        "r": 30, "fill": "#FFF8E1", "stroke": "#8B1A1A", "sw": 2,
        "img_size": 52, "img_color": "Merah", "img_opacity": None,
        "text_color": "#8B1A1A", "text_weight": 700, "text_size": 15,
    },
    "triple": {
        "r": 24, "fill": "#E8F0EA", "stroke": "#2D6A4F", "sw": 2,
        "img_size": 40, "img_color": "Merah", "img_opacity": None,
        "text_color": "#2D6A4F", "text_weight": 700, "text_size": 14,
    },
    "pair": {
        "r": 22, "fill": "#FFF8E1", "stroke": "#C9A961", "sw": 1.8,
        "img_size": 38, "img_color": "Merah", "img_opacity": None,
        "text_color": "#C9A961", "text_weight": 700, "text_size": 13,
    },
    "clash": {
        "r": 22, "fill": "#F4DCDC", "stroke": "#A03434", "sw": 1.8,
        "img_size": 38, "img_color": "Merah", "img_opacity": None,
        "text_color": "#A03434", "text_weight": 600, "text_size": 13,
    },
    "harm": {
        "r": 22, "fill": "#F8EFD4", "stroke": "#B8860B", "sw": 1.8,
        "img_size": 38, "img_color": "Merah", "img_opacity": None,
        "text_color": "#B8860B", "text_weight": 600, "text_size": 13,
    },
    "punish": {  # 三刑 — use clash-style red
        "r": 22, "fill": "#F4DCDC", "stroke": "#A03434", "sw": 1.5,
        "img_size": 38, "img_color": "Merah", "img_opacity": None,
        "text_color": "#A03434", "text_weight": 600, "text_size": 13,
    },
    "break": {  # 破 — use clash-style red
        "r": 22, "fill": "#F4DCDC", "stroke": "#A03434", "sw": 1.5,
        "img_size": 38, "img_color": "Merah", "img_opacity": None,
        "text_color": "#A03434", "text_weight": 600, "text_size": 13,
    },
    "neutral": {
        "r": 20, "fill": "#F5EBD0", "stroke": "#D8C896", "sw": 0.8,
        "img_size": 34, "img_color": "Hitam", "img_opacity": "0.6",
        "text_color": "#6B5B3F", "text_weight": None, "text_size": 13,
    },
}

REL_HZ_TO_KEY = {
    "三合": "triple",
    "六合": "pair",
    "六沖": "clash",
    "六害": "harm",
    "三刑": "punish",
    "破": "break",
}


def _wheel_cell_svg(idx: int, branch_hz: str, rel_key: str, comment_label: str) -> str:
    """Generate one <g>...</g> SVG group for a wheel cell."""
    cx, cy, lx, ly = WHEEL_POSITIONS[idx]
    style = WHEEL_STYLE[rel_key]
    shio_id = BRANCHES[branch_hz]["shio_id"]
    img_file = f"{shio_id}-{style['img_color']}.svg"
    half = style["img_size"] / 2

    img_attrs = f'href="{img_file}" x="{cx - half:g}" y="{cy - half:g}" width="{style["img_size"]}" height="{style["img_size"]}"'
    if style["img_opacity"]:
        img_attrs += f' opacity="{style["img_opacity"]}"'

    # Text element — weight optional
    text_attrs = f'x="{lx}" y="{ly}" text-anchor="middle" font-family="Noto Serif TC,serif" font-size="{style["text_size"]}" fill="{style["text_color"]}"'
    if style["text_weight"]:
        text_attrs += f' font-weight="{style["text_weight"]}"'

    return (
        f'          <!-- {comment_label} -->\n'
        f'          <g>\n'
        f'            <circle cx="{cx:g}" cy="{cy:g}" r="{style["r"]:g}" fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style["sw"]:g}"/>\n'
        f'            <image {img_attrs}/>\n'
        f'            <text {text_attrs}>{branch_hz}</text>\n'
        f'          </g>'
    )


def regen_wheel_svg(subject: dict) -> str:
    """Generate the inner SVG for marriage wheel (everything inside <svg>...</svg>)."""
    marriage = subject["marriage"]
    self_hz = subject["shio"]["branch_hz"]
    self_idx = BRANCH_ORDER.index(self_hz)

    # Build relationship map: branch_idx → rel_key
    rel_map = {}
    rel_map[self_idx] = "self"
    cocok_branches = []  # for triple polygon
    pair_branches = []
    clash_branches = []
    harm_branches = []
    punish_branches = []
    break_branches = []
    for item in marriage.get("cocok", []):
        b_hz = item["branch_hz"]
        idx = BRANCH_ORDER.index(b_hz)
        key = REL_HZ_TO_KEY.get(item["relationship_hz"], "neutral")
        rel_map[idx] = key
        if key == "triple": cocok_branches.append(idx)
        elif key == "pair": pair_branches.append(idx)
    for item in marriage.get("hindari", []):
        b_hz = item["branch_hz"]
        idx = BRANCH_ORDER.index(b_hz)
        key = REL_HZ_TO_KEY.get(item["relationship_hz"], "neutral")
        rel_map[idx] = key
        if key == "clash": clash_branches.append(idx)
        elif key == "harm": harm_branches.append(idx)
        elif key == "punish": punish_branches.append(idx)
        elif key == "break": break_branches.append(idx)

    # Build relationship lines (drawn before cells)
    self_cx, self_cy, _, _ = WHEEL_POSITIONS[self_idx]
    line_svg = []

    # Triple harmony: polygon if exactly 2 triple branches
    if len(cocok_branches) >= 2:
        pts = [(self_cx, self_cy)]
        for idx in cocok_branches[:2]:
            cx, cy, _, _ = WHEEL_POSITIONS[idx]
            pts.append((cx, cy))
        # Format like "亥-卯-未"
        triple_label = "-".join([self_hz] + [BRANCH_ORDER[i] for i in cocok_branches[:2]])
        pts_str = " ".join(f"{x:g},{y:g}" for x, y in pts)
        line_svg.append(
            f'          <!-- Triple harmony {triple_label} (green triangle) -->\n'
            f'          <polygon points="{pts_str}"\n'
            f'            fill="rgba(45,106,79,0.06)" stroke="#2D6A4F" stroke-width="1.2" stroke-dasharray="4,3"/>'
        )

    # Pair: gold solid line
    for idx in pair_branches:
        cx, cy, _, _ = WHEEL_POSITIONS[idx]
        line_svg.append(
            f'          <!-- Pair {self_hz}-{BRANCH_ORDER[idx]} (gold solid) -->\n'
            f'          <line x1="{self_cx:g}" y1="{self_cy:g}" x2="{cx:g}" y2="{cy:g}"\n'
            f'            stroke="#C9A961" stroke-width="1.5"/>'
        )

    # Clash: red dashed
    for idx in clash_branches:
        cx, cy, _, _ = WHEEL_POSITIONS[idx]
        line_svg.append(
            f'          <!-- Clash {self_hz}-{BRANCH_ORDER[idx]} (red dashed) -->\n'
            f'          <line x1="{self_cx:g}" y1="{self_cy:g}" x2="{cx:g}" y2="{cy:g}"\n'
            f'            stroke="#A03434" stroke-width="1.5" stroke-dasharray="6,3"/>'
        )

    # Harm: yellow dotted
    for idx in harm_branches:
        cx, cy, _, _ = WHEEL_POSITIONS[idx]
        line_svg.append(
            f'          <!-- Harm {self_hz}-{BRANCH_ORDER[idx]} (yellow dotted) -->\n'
            f'          <line x1="{self_cx:g}" y1="{self_cy:g}" x2="{cx:g}" y2="{cy:g}"\n'
            f'            stroke="#B8860B" stroke-width="1.2" stroke-dasharray="2,3"/>'
        )

    # Punish: red dashed (extra)
    for idx in punish_branches:
        cx, cy, _, _ = WHEEL_POSITIONS[idx]
        line_svg.append(
            f'          <!-- Punish {self_hz}-{BRANCH_ORDER[idx]} (red short-dashed) -->\n'
            f'          <line x1="{self_cx:g}" y1="{self_cy:g}" x2="{cx:g}" y2="{cy:g}"\n'
            f'            stroke="#A03434" stroke-width="1.2" stroke-dasharray="3,2"/>'
        )

    # Break: red dotted (extra)
    for idx in break_branches:
        cx, cy, _, _ = WHEEL_POSITIONS[idx]
        line_svg.append(
            f'          <!-- Break {self_hz}-{BRANCH_ORDER[idx]} (red dotted) -->\n'
            f'          <line x1="{self_cx:g}" y1="{self_cy:g}" x2="{cx:g}" y2="{cy:g}"\n'
            f'            stroke="#A03434" stroke-width="1.2" stroke-dasharray="1,3"/>'
        )

    # 12 cells
    cell_svg = []
    # Comment label format matches Michele: "i=N branch_hz shio_id (TYPE — self_hz-branch_hz rel_hz)"
    rel_label_map = {
        "self": "DIRI",
        "triple": "TRIPLE",
        "pair": "PAIR",
        "clash": "CLASH",
        "harm": "HARM",
        "punish": "PUNISH",
        "break": "BREAK",
        "neutral": "neutral",
    }
    rel_hz_map = {
        "triple": "三合",
        "pair": "六合",
        "clash": "六沖",
        "harm": "六害",
        "punish": "三刑",
        "break": "破",
    }
    # Triple branches share a single label across all triple cells (e.g., "亥-卯-未")
    triple_full_label = "-".join([self_hz] + [BRANCH_ORDER[i] for i in cocok_branches[:2]]) if len(cocok_branches) >= 2 else ""
    for idx in range(12):
        b_hz = BRANCH_ORDER[idx]
        key = rel_map.get(idx, "neutral")
        if key == "self":
            comment = f"i={idx} {b_hz} {BRANCHES[b_hz]['shio_id']} (DIRI)"
        elif key == "neutral":
            comment = f"i={idx} {b_hz} {BRANCHES[b_hz]['shio_id']} (neutral)"
        elif key == "triple":
            comment = f"i={idx} {b_hz} {BRANCHES[b_hz]['shio_id']} (TRIPLE — {triple_full_label} 三合)"
        else:
            rel_hz = rel_hz_map.get(key, "")
            comment = f"i={idx} {b_hz} {BRANCHES[b_hz]['shio_id']} ({rel_label_map[key]} — {self_hz}-{b_hz} {rel_hz})"
        cell_svg.append(_wheel_cell_svg(idx, b_hz, key, comment))

    # Note: This regen function returns the inner content of the wheel-svg's
    # <svg>...</svg> (everything between the svg open and close).
    # The BG circles + cross axes are NOT part of regen — they're static.
    # Only relationship lines + center label + 12 cells are regenerated.

    # Center label
    center_svg = (
        '          <!-- Pusat -->\n'
        '          <circle cx="200" cy="200" r="22" fill="#FFFEF8" stroke="#C9A961" stroke-width="1"/>\n'
        '          <text x="200" y="194" text-anchor="middle" font-family="Noto Serif TC,serif" font-size="11" fill="#8B1A1A" font-weight="600">本命</text>\n'
        '          <text x="200" y="208" text-anchor="middle" font-family="Inter,sans-serif" font-size="6.5" fill="#6B5B3F" letter-spacing="1">ANDA</text>'
    )

    # Static BG (must match Michele exactly)
    bg = (
        '          <!-- Lingkaran latar -->\n'
        '          <circle cx="200" cy="200" r="180" fill="none" stroke="#E5D3A1" stroke-width="0.5"/>\n'
        '          <circle cx="200" cy="200" r="170" fill="#FFFEF8" stroke="#E5D3A1" stroke-width="0.5"/>\n'
        '          <circle cx="200" cy="200" r="115" fill="none" stroke="#E5D3A1" stroke-width="0.4" stroke-dasharray="2,2"/>\n'
        '\n'
        '          <!-- Salib kompas -->\n'
        '          <line x1="200" y1="30" x2="200" y2="370" stroke="#E5D3A1" stroke-width="0.3" stroke-dasharray="1,3"/>\n'
        '          <line x1="30" y1="200" x2="370" y2="200" stroke="#E5D3A1" stroke-width="0.3" stroke-dasharray="1,3"/>\n'
        '\n'
        '          <!-- Relationship lines (drawn before badges) -->'
    )

    # Compose
    return (
        '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">\n'
        + bg + '\n'
        + '\n'.join(line_svg) + '\n'
        + '\n'
        + center_svg + '\n'
        + '\n'
        + '          <!-- 12 badge shio -->\n'
        + '\n'.join(cell_svg) + '\n'
        + '        </svg>'
    )


# ============================================================
# COMPAT GRID — cocok + hindari rows
# ============================================================

REL_BADGE_LABEL = {
    "三合": "三合 · BESAR JAYA",
    "六合": "六合 · COCOK",
    "六沖": "六沖 · BENTROK",
    "六害": "六害 · MENGHAMBAT",
    "三刑": "三刑 · GESEKAN",
    "破":   "破 · MERETAKKAN",
}


def regen_compat_card(card_type: str, items: list[dict], title_color: str, badge_text: str) -> str:
    """card_type: 'good' | 'bad'."""
    rows = []
    for item in items:
        b_hz = item["branch_hz"]
        shio_id = BRANCHES[b_hz]["shio_id"]
        img_file = f"{shio_id}-Merah.svg"
        rel_label = REL_BADGE_LABEL.get(item["relationship_hz"],
                                         f"{item['relationship_hz']} · {item.get('relationship_id', '')}")
        reason = html_amp(item["reason_id"])
        rows.append(
            f'          <div class="shio-row">\n'
            f'            <div class="icon"><img src="{img_file}" alt="{shio_id}"></div>\n'
            f'            <div class="info">\n'
            f'              <div class="name"><span class="hz">{b_hz}</span>{shio_id}<span class="tag">{rel_label}</span></div>\n'
            f'              <div class="reason">{reason}</div>\n'
            f'            </div>\n'
            f'          </div>'
        )

    return (
        f'<div class="compat-card {card_type}">\n'
        f'        <div class="compat-title">\n'
        f'          <span class="badge">{badge_text}</span>\n'
        f'          <span style="color:{title_color};">{"Pasangan Selaras" if card_type == "good" else "Berisiko Bentrok"}</span>\n'
        f'        </div>\n'
        f'        <div class="shio-list">\n'
        + '\n'.join(rows) + '\n'
        + f'        </div>\n'
        + f'      </div>'
    )


# ============================================================
# DAY MASTER — radar polygon + 5 element cards
# ============================================================

# Radar axis endpoints at scale=3 (max). Order: 金(top), 水(TR), 火(BR), 土(BL), 木(TL).
# Direction vectors from center (200,200):
RADAR_AXES = {
    "jin":  ("金", 200, 60,  "#8B1A1A", 200, 40,  "Logam"),
    "shui": ("水", 333, 157, "#3A6B8C", 358, 148, "Air"),
    "huo":  ("火", 282, 313, "#8C3535", 305, 338, "Api"),
    "tu":   ("土", 118, 313, "#8C6E47", 95,  338, "Tanah"),
    "mu":   ("木", 67,  157, "#4D7A3A", 42,  148, "Kayu"),
}
RADAR_CENTER = (200, 200)
RADAR_MAX = 3  # scale 3 = full axis


def _radar_vertex(el: str, value: float) -> tuple[float, float]:
    """Compute (x, y) of polygon vertex for element at given value."""
    cx, cy = RADAR_CENTER
    _, ex, ey, _, _, _, _ = RADAR_AXES[el]
    t = value / RADAR_MAX
    return (cx + (ex - cx) * t, cy + (ey - cy) * t)


def regen_radar_polygon(wx: dict) -> str:
    """Generate the SVG snippet replacing Michele's polygon + 5 vertex dots."""
    # Polygon vertex order: 金 → 水 → 火 → 土 → 木
    pts = []
    for el in ["jin", "shui", "huo", "tu", "mu"]:
        x, y = _radar_vertex(el, wx[el]["value"])
        pts.append((x, y))
    pts_str = " ".join(f"{x:g},{y:g}" for x, y in pts)
    poly = (
        f'          <polygon points="{pts_str}"\n'
        f'            fill="rgba(139,26,26,0.18)" stroke="#8B1A1A" stroke-width="1.5"/>'
    )
    # Vertex dots (color from RADAR_AXES vertex_color but Michele uses element gradient end)
    dot_colors = {"jin": "#A89358", "shui": "#3A6B8C", "huo": "#8C3535", "tu": "#8C6E47", "mu": "#4D7A3A"}
    dots = []
    for el, (x, y) in zip(["jin","shui","huo","tu","mu"], pts):
        # Match Michele's spacing: 1 trailing space for shui (291,170), 2 for jin (200,166), etc
        # Use simple format
        dots.append(f'          <circle cx="{x:g}" cy="{y:g}" r="3" fill="{dot_colors[el]}"/>')
    return poly + '\n' + '\n'.join(dots)


def regen_radar_labels(wx: dict, dm_element_class: str) -> str:
    """Generate the 5 element label texts inside the <g font-family="Noto Serif TC,serif"> group."""
    # Order matches Michele: 金 top, 水 right, 火 LR, 土 LL, 木 left
    parts = []
    for el in ["jin", "shui", "huo", "tu", "mu"]:
        hz, ex, ey, color, lx, ly, label_id = RADAR_AXES[el]
        v = wx[el]["value"]
        # Format value: 3.0, 2.5, 0.8, 0.0
        v_str = f"{v:g}" if v != int(v) else f"{int(v)}.0"
        # DM star: append " ★" if element matches DM
        star = " ★" if el == dm_element_class else ""
        comment_pos = {
            "jin": "金 top", "shui": "水 right", "huo": "火 lower-right",
            "tu": "土 lower-left", "mu": "木 left"
        }
        comment = f"<!-- {comment_pos[el]} -->"
        if el == dm_element_class:
            comment = f"<!-- {comment_pos[el]} — Penguasa Hari ★ -->"
        parts.append(
            f'            {comment}\n'
            f'            <text x="{lx}" y="{ly}" text-anchor="middle" font-size="18" fill="{color}" font-weight="700">{hz}</text>\n'
            f'            <text x="{lx}" y="{ly + 12}" text-anchor="middle" font-size="7" fill="#6B5B3F" font-style="italic">{label_id} · {v_str}{star}</text>'
        )
    return '          <g font-family="Noto Serif TC,serif">\n' + '\n'.join(parts) + '\n          </g>'


def regen_dm_element_cards(subject: dict) -> str:
    """Generate <div class="dm-elements">...</div> with 5 cards sorted by value desc."""
    wx = subject["wuxing"]
    dm_el = _wuxing_class_from_dm(subject["day_master"])  # e.g., 'mu', 'huo'
    yong_shen_el_hz = subject["yong_shen"]["elements_hz"]  # e.g., "火 金"
    ji_shen_el_hz = subject["ji_shen"]["elements_hz"]      # e.g., "水 木"
    yong_set = set(yong_shen_el_hz.split())
    ji_set = set(ji_shen_el_hz.split())

    items = sorted(
        [(el, wx[el]["value"], wx[el]["percent"], wx[el]["label_id"]) for el in ELEMENT_HZ],
        key=lambda x: -x[1]
    )
    pinyin_map = {"mu": "Mù", "shui": "Shuǐ", "tu": "Tǔ", "huo": "Huǒ", "jin": "Jīn"}
    cards = []
    for el, val, pct, label in items:
        v_str = f"{val:g}" if val != int(val) else f"{int(val)}.0"
        # Bar width: value / RADAR_MAX (3) * 100, integer
        width_pct = round(val / RADAR_MAX * 100)
        # Role badge logic
        is_dm = (el == dm_el)
        hz = ELEMENT_HZ[el]
        role_html = ""
        if is_dm:
            tag_html = f'<span class="dme-tag-self">★ DIRI</span>'
            role_html = '<div class="dme-role">Penguasa Hari</div>'
            val_html = f'{v_str} {tag_html}'
        else:
            val_html = v_str
            if hz in yong_set:
                role_html = '<div class="dme-role" style="background:rgba(45,106,79,0.7);">喜 Mendukung</div>'
            elif hz in ji_set:
                role_html = '<div class="dme-role" style="background:rgba(160,52,52,0.5);">忌 Kurang Mendukung</div>'
            else:
                role_html = '<div class="dme-role">Netral</div>'

        cards.append(
            f'      <div class="dme dme-card el-{el}">\n'
            f'        <div class="dme-hz">{hz}</div>\n'
            f'        <div class="dme-name">{label} · {pinyin_map[el]}</div>\n'
            f'        <div class="dme-val">{val_html}</div>\n'
            f'        <div class="dme-bar"><div class="dme-bar-fill" style="width:{width_pct}%"></div></div>\n'
            f'        {role_html}\n'
            f'      </div>'
        )
    return '<div class="dm-elements">\n' + '\n'.join(cards) + '\n    </div>'


def _wuxing_class_from_dm(dm: dict) -> str:
    """Map DM element_hz to css element class key (mu/shui/tu/huo/jin)."""
    hz_to_key = {"木": "mu", "水": "shui", "土": "tu", "火": "huo", "金": "jin"}
    return hz_to_key[dm["stem_element_hz"]]


# ============================================================
# YANG ZHAI — compass + zone matrix
# ============================================================

def _compass_axis_endpoints(self_pos: str) -> tuple[tuple[float,float], tuple[float,float]]:
    """Return ((x1,y1),(x2,y2)) for the gold axis line through self gua and its opposite."""
    opp = {"N":"S","S":"N","E":"W","W":"E","NE":"SW","SW":"NE","NW":"SE","SE":"NW"}[self_pos]
    cx1, cy1 = COMPASS_POSITIONS[self_pos]
    cx2, cy2 = COMPASS_POSITIONS[opp]
    # Project to outer edge: extend the line through both points to the bounding circle r=178
    # For simplicity use the badge centers' diametrically-opposite extensions.
    # Michele's pattern uses (200,22)-(200,378) for N-S so points are projected to outer.
    # Use the outer ring at r=178 from center (200,200): just hardcode by axis.
    if self_pos in ("N","S"):
        return (200, 22), (200, 378)
    if self_pos in ("E","W"):
        return (22, 200), (378, 200)
    if self_pos in ("NE","SW"):
        # NE-SW diagonal
        return (302.5, 97.5), (97.5, 302.5)
    # NW-SE
    return (97.5, 97.5), (302.5, 302.5)


def regen_compass_svg(yang_zhai: dict, dm: dict) -> str:
    """Generate the inner SVG for Yang Zhai compass — bg + axis line + 8 badges + center + corner labels."""
    self_gua = yang_zhai["gua_hz"]
    self_t = TRIGRAMS[self_gua]
    self_pos = self_t["pos"]

    # Axis
    (ax1, ay1), (ax2, ay2) = _compass_axis_endpoints(self_pos)
    # Direction abbreviation pair for comment label
    axis_pair_label = {
        "N": "N-S", "S": "N-S", "E": "E-W", "W": "E-W",
        "NE": "NE-SW", "SW": "NE-SW", "NW": "NW-SE", "SE": "NW-SE",
    }[self_pos]
    axis_svg = (
        f'          <!-- Subject\'s {axis_pair_label} axis ({self_gua}卦 line) -->\n'
        f'          <line x1="{ax1:g}" y1="{ay1:g}" x2="{ax2:g}" y2="{ay2:g}"\n'
        f'            stroke="#C9A961" stroke-width="1.5" stroke-dasharray="6,3" opacity="0.7"/>'
    )

    # 8 badges
    badge_svg = []
    for gua_hz, t in TRIGRAMS.items():
        cx, cy = COMPASS_POSITIONS[t["pos"]]
        if gua_hz == self_gua:
            # Self badge — r=36, red border, ★ TRIGRAM ANDA badge
            badge_svg.append(
                f'          <!-- {t["pos"]} {gua_hz} (SELF — TRIGRAM ANDA) -->\n'
                f'          <g>\n'
                f'            <circle cx="{cx:g}" cy="{cy:g}" r="36" fill="#FFF8E1" stroke="#8B1A1A" stroke-width="2"/>\n'
                f'            <text x="{cx:g}" y="{cy-10:g}" text-anchor="middle" class="dir-trigram" font-size="15" fill="#8B1A1A">{t["symbol"]}</text>\n'
                f'            <text x="{cx:g}" y="{cy+6:g}" text-anchor="middle" class="dir-label-cn" font-size="14" fill="#8B1A1A" font-weight="700">{t["dir_cn"]}</text>\n'
                f'            <text x="{cx:g}" y="{cy+19:g}" text-anchor="middle" class="dir-label-id" font-size="6.5" fill="#8B1A1A" font-style="italic" font-weight="600">{t["dir_abbr"]} · {t["pinyin"]} · {t["label_id"].upper()}</text>\n'
                f'            <text x="{cx:g}" y="{cy+45:g}" text-anchor="middle" font-size="6" fill="#8B1A1A" font-weight="700" letter-spacing="1">★ TRIGRAM ANDA ★</text>\n'
                f'          </g>'
            )
        elif t["group"] == self_t["group"]:
            # Same group — green border (East Group → green if self also East)
            badge_svg.append(
                f'          <!-- {t["pos"]} {gua_hz} -->\n'
                f'          <g>\n'
                f'            <circle cx="{cx:g}" cy="{cy:g}" r="30" fill="#E8F0EA" stroke="#2D6A4F" stroke-width="1.2"/>\n'
                f'            <text x="{cx:g}" y="{cy-7:g}" text-anchor="middle" class="dir-trigram" font-size="13" fill="#2D6A4F">{t["symbol"]}</text>\n'
                f'            <text x="{cx:g}" y="{cy+7:g}" text-anchor="middle" class="dir-label-cn" font-size="13" fill="#2D6A4F" font-weight="700">{t["dir_cn"]}</text>\n'
                f'            <text x="{cx:g}" y="{cy+19:g}" text-anchor="middle" class="dir-label-id" font-size="6" fill="#2D6A4F" font-style="italic">{t["dir_abbr"]} · {t["pinyin"]} · {t["label_id"]}</text>\n'
                f'          </g>'
            )
        else:
            # Other group — neutral cream
            badge_svg.append(
                f'          <!-- {t["pos"]} {gua_hz} -->\n'
                f'          <g>\n'
                f'            <circle cx="{cx:g}" cy="{cy:g}" r="30" fill="#FFFEF8" stroke="#D8C896" stroke-width="0.6"/>\n'
                f'            <text x="{cx:g}" y="{cy-7:g}" text-anchor="middle" class="dir-trigram" font-size="13" fill="#6B5B3F">{t["symbol"]}</text>\n'
                f'            <text x="{cx:g}" y="{cy+7:g}" text-anchor="middle" class="dir-label-cn" font-size="13" fill="#2C2416">{t["dir_cn"]}</text>\n'
                f'            <text x="{cx:g}" y="{cy+19:g}" text-anchor="middle" class="dir-label-id" font-size="6" fill="#6B5B3F" font-style="italic">{t["dir_abbr"]} · {t["pinyin"]} · {t["label_id"]}</text>\n'
                f'          </g>'
            )

    # Static parts
    bg = (
        '          <!-- Ornamen luar -->\n'
        '          <circle cx="200" cy="200" r="186" fill="none" stroke="#E5D3A1" stroke-width="0.6"/>\n'
        '          <circle cx="200" cy="200" r="178" fill="#FFFEF8" stroke="#C9A961" stroke-width="0.4"/>\n'
        '          <circle cx="200" cy="200" r="118" fill="none" stroke="#E5D3A1" stroke-width="0.4" stroke-dasharray="2,3"/>\n'
        '\n'
        '          <!-- Garis sumbu utama -->\n'
        '          <line x1="200" y1="22" x2="200" y2="378" stroke="#E5D3A1" stroke-width="0.3" stroke-dasharray="2,3"/>\n'
        '          <line x1="22" y1="200" x2="378" y2="200" stroke="#E5D3A1" stroke-width="0.3" stroke-dasharray="2,3"/>'
    )

    center_svg = (
        '          <!-- Center marker: house + axis -->\n'
        '          <g>\n'
        '            <circle cx="200" cy="200" r="32" fill="#FFFEF8" stroke="#C9A961" stroke-width="1.2"/>\n'
        '            <!-- house icon -->\n'
        '            <path d="M 184 208 L 200 192 L 216 208 L 216 218 L 184 218 Z"\n'
        '              fill="none" stroke="#8B1A1A" stroke-width="1.2" stroke-linejoin="round"/>\n'
        '            <rect x="195" y="211" width="6" height="7" fill="#8B1A1A"/>\n'
        '            <text x="200" y="232" text-anchor="middle" font-size="7" fill="#6B5B3F" font-style="italic" letter-spacing="1">RUMAH</text>\n'
        '          </g>\n'
        '\n'
        '          <!-- Axis label (top-right) -->\n'
        '          <text x="376" y="32" text-anchor="end" font-size="6" fill="#C9A961" font-weight="600" letter-spacing="1.5">UTARA · U</text>\n'
        '          <text x="24" y="32" font-size="5.5" fill="#C9A961" font-style="italic">八卦 BĀ GUÀ</text>\n'
        '          <text x="24" y="378" font-size="5.5" fill="#C9A961" font-style="italic">8 ARAH MATA ANGIN</text>'
    )

    return (
        '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">\n'
        + bg + '\n'
        + '\n'
        + axis_svg + '\n'
        + '\n'
        + '          <!-- 8 badge arah -->\n'
        + '\n'.join(badge_svg) + '\n'
        + '\n'
        + center_svg + '\n'
        + '        </svg>'
    )


def regen_yz_zone(zone_key: str, hz: str, id_label: str, pinyin_label: str,
                  zone_data: dict, warn: bool = False) -> str:
    """Generate one yz-zone div."""
    pills = []
    pill_class = "yz-pill bad" if warn else "yz-pill"
    dirs_hz = zone_data.get("dirs_hz", [])
    dirs_abbr = zone_data.get("dirs_abbr", [])
    for hz_, abbr in zip(dirs_hz, dirs_abbr):
        pills.append(f'<span class="{pill_class}"><span class="hz">{hz_}</span>{abbr}</span>')
    pills_html = '\n              '.join(pills) if pills else ''
    headline = '⚠ Arah "Penekan"' if warn else '✓ Arah Optimal'
    note = zone_data.get("note_id", "")
    note_html = f'\n            <div class="yz-zone-note">{html_amp(note)}</div>' if note else ''
    cls = "yz-zone warn" if warn else "yz-zone"
    return (
        f'<div class="{cls}">\n'
        f'          <div class="yz-zone-label">\n'
        f'            <div class="yz-zone-hz">{hz}</div>\n'
        f'            <div class="yz-zone-id">{id_label}</div>\n'
        f'            <div class="yz-zone-pinyin">{pinyin_label}</div>\n'
        f'          </div>\n'
        f'          <div class="yz-zone-dirs">\n'
        f'            <div class="yz-zone-headline">{headline}</div>\n'
        f'            <div class="yz-dir-pills">\n'
        f'              {pills_html}\n'
        f'            </div>{note_html}\n'
        f'          </div>\n'
        f'        </div>'
    )


# Ten Gods → Pinyin lookup (for spotlight tag)
TEN_GOD_PINYIN = {
    "比肩": "Bǐ Jiān",     "劫財": "Jié Cái",
    "食神": "Shí Shén",     "傷官": "Shāng Guān",
    "偏財": "Piān Cái",     "正財": "Zhèng Cái",
    "七殺": "Qī Shā",       "正官": "Zhèng Guān",
    "偏印": "Piān Yìn",     "正印": "Zhèng Yìn",
}


def apply_blocks(content: str, subject: dict, fname: str = "") -> str:
    """Block-level regeneration of complex structures.
    fname: source template filename, used to scope page-specific replacements.
    """
    wx = subject.get("wuxing")
    if wx:
        # Wu Xing stack — replace whole <div class="wux-stack">...</div>
        new_stack = regen_wuxing_stack(wx)
        content = replace_block(content, r'<div class="wux-stack">', new_stack)

        # Wu Xing tags
        dm = subject["day_master"]
        ys = subject["yong_shen"]
        js = subject["ji_shen"]
        new_tags = (
            '<div class="wux-tags">\n'
            f'          <span class="wux-tag self"><span class="hz">{dm["stem_element_hz"]}</span>DIRI · {wx["self_value"]}</span>\n'
            f'          <span class="wux-tag fav"><span class="hz">{ys["elements_hz"]}</span>MENDUKUNG</span>\n'
            f'          <span class="wux-tag unfav"><span class="hz">{js["elements_hz"]}</span>KURANG MENDUKUNG</span>\n'
            '        </div>'
        )
        content = replace_block(content, r'<div class="wux-tags">', new_tags)

        # Wu Xing axis max
        content = re.sub(
            r'(<div class="wux-axis-top"><span>0</span><span>2</span><span>4</span><span>6</span><span>)[\d.]+\s*Total(</span></div>)',
            rf'\g<1>{wx["total"]} Total\g<2>',
            content
        )

        # Wu Xing insight (only replace if subject provided one)
        if subject.get("wuxing_insight_id"):
            new_insight = (
                '<div class="wux-insight">\n          '
                + subject["wuxing_insight_id"]
                + '\n        </div>'
            )
            content = replace_block(content, r'<div class="wux-insight">', new_insight)

    # Da Yun blocks
    da_yun = subject.get("da_yun")
    if da_yun:
        # ll-eyebrow "Fase N dari 10"
        cur_idx = da_yun.get("current_index", 0)
        content = re.sub(
            r'<div class="label-meta">Fase \d+ dari 10 · Fase Sekarang</div>',
            f'<div class="label-meta">Fase {cur_idx + 1} dari 10 · Fase Sekarang</div>',
            content
        )
        # Lifeline 10 cells
        content = replace_block(content, r'<div class="lifeline">', regen_lifeline(da_yun))
        # ll-axis
        content = replace_block(content, r'<div class="ll-axis">', regen_lifeline_axis(da_yun))
        # Spotlight
        content = replace_block(content, r'<div class="spotlight">',
                                regen_spotlight(da_yun, subject["day_master"]))
        # Seasons bar
        content = replace_block(content, r'<div class="seasons-bar">', regen_seasons_bar(da_yun))
        # Seasons axis
        content = replace_block(content, r'<div class="seasons-axis">', regen_seasons_axis(da_yun))
        # Seasons-eyebrow label-meta — only update if subject provides override
        if da_yun.get("seasons_label_text"):
            content = re.sub(
                r'(class="label-meta"[^>]*>)100 TAHUN · [^<]+(</div>)',
                rf'\g<1>{da_yun["seasons_label_text"]}\g<2>',
                content
            )
        # Footer caption (page_dayun) — narrative for current cycle
        if da_yun.get("footer_caption_html"):
            content = replace_block(content, r'<div class="footer-caption">',
                                    f'<div class="footer-caption">\n      {da_yun["footer_caption_html"]}\n    </div>')

    # Day Master radar + element cards (page_06_daymaster only)
    if wx and fname == "page_06_daymaster.html":
        dm_el = _wuxing_class_from_dm(subject["day_master"])
        # Replace radar polygon + dots: from "<!-- Michele's polygon (filled)" line through 5 vertex circles
        new_radar = regen_radar_polygon(wx)
        # Find "<polygon points=..." with fill="rgba(139,26,26,0.18)" (Michele's main polygon)
        # then replace through the 5 circles after it.
        pat = re.compile(
            r'<polygon points="[^"]+"\s*\n\s*fill="rgba\(139,26,26,0\.18\)"[^/]*/>'
            r'(\s*\n\s*<circle[^/]*/>){5}',
            re.DOTALL
        )
        content = pat.sub(new_radar.lstrip(), content)
        # Replace the labels group (5 element labels)
        new_labels = regen_radar_labels(wx, dm_el)
        content = re.sub(
            r'<g font-family="Noto Serif TC,serif">.*?</g>',
            new_labels.lstrip(),
            content, count=1, flags=re.DOTALL
        )
        # Replace the 5 element cards block
        new_cards = regen_dm_element_cards(subject)
        content = replace_block(content, r'<div class="dm-elements">', new_cards)

    # Marriage blocks (page_marriage only)
    marriage = subject.get("marriage")
    if marriage and fname == "page_marriage.html":
        # Wheel legend self branch label "本命 亥" → "本命 {self}"
        self_hz = subject["shio"]["branch_hz"]
        if self_hz != "亥":
            content = content.replace("本命 亥", f"本命 {self_hz}")
        # Wheel SVG inside <div class="wheel-svg"><svg>...</svg></div>
        # Find <svg> opening inside wheel-svg and replace whole svg
        new_svg = regen_wheel_svg(subject)
        content = re.sub(
            r'<svg viewBox="0 0 400 400"[^>]*>.*?</svg>',
            new_svg,
            content, count=1, flags=re.DOTALL
        )
        # Cocok grid (good)
        cocok_html = regen_compat_card("good", marriage.get("cocok", []),
                                       "var(--green)", "宜 COCOK")
        content = replace_block(content, r'<div class="compat-card good">', cocok_html)
        # Hindari grid (bad)
        hindari_html = regen_compat_card("bad", marriage.get("hindari", []),
                                         "var(--red-bad)", "忌 HINDARI")
        content = replace_block(content, r'<div class="compat-card bad">', hindari_html)
        # Footer caption (if subject provides override)
        if marriage.get("footer_caption_html"):
            content = replace_block(content, r'<div class="footer-caption">',
                                     f'<div class="footer-caption">\n      {marriage["footer_caption_html"]}\n    </div>')

    # Yang Zhai blocks (page_yangzhai only)
    yang_zhai = subject.get("yang_zhai")
    if yang_zhai and fname == "page_yangzhai.html":
        # Compass SVG
        new_svg = regen_compass_svg(yang_zhai, subject["day_master"])
        content = re.sub(
            r'<svg viewBox="0 0 400 400"[^>]*>.*?</svg>',
            new_svg, content, count=1, flags=re.DOTALL
        )

        # Side panel: trigram symbol
        m_t = TRIGRAMS["坎"]  # Michele's reference
        s_t = TRIGRAMS[yang_zhai["gua_hz"]]
        if yang_zhai["gua_hz"] != "坎":
            content = content.replace(
                f'<div class="yz-trigram">{m_t["symbol"]}</div>',
                f'<div class="yz-trigram">{s_t["symbol"]}</div>'
            )
            content = content.replace(
                f'<div class="yz-gua-name">坎</div>',
                f'<div class="yz-gua-name">{yang_zhai["gua_hz"]}</div>'
            )
            content = content.replace(
                f'Kǎn — "Air"',
                f'{s_t["pinyin"]} — "{s_t["label_id"]}"'
            )

        # Side panel meaning (subject override)
        if yang_zhai.get("meaning_html"):
            content = replace_block(content, r'<div class="yz-gua-meaning">',
                                    f'<div class="yz-gua-meaning">\n          {yang_zhai["meaning_html"]}\n        </div>')

        # Sumbu hoki text
        m_axis_hz = "北↔南"
        s_axis_hz = yang_zhai.get("sumbu_hoki_hz", m_axis_hz)
        if s_axis_hz != m_axis_hz:
            # Original Michele: <span class="hz">北</span>↔<span class="hz">南</span>
            m_parts = m_axis_hz.split("↔")
            s_parts = s_axis_hz.split("↔")
            old = f'<span class="hz">{m_parts[0]}</span>↔<span class="hz">{m_parts[1]}</span>'
            new = f'<span class="hz">{s_parts[0]}</span>↔<span class="hz">{s_parts[1]}</span>'
            content = content.replace(old, new)
            # Also "U ↔ S · garis emas" → "{abbr1} ↔ {abbr2} · garis emas"
            m_abbr = "U ↔ S"
            s_abbr = yang_zhai.get("sumbu_hoki_id", m_abbr)
            content = content.replace(m_abbr, s_abbr)

        # Eyebrow text "坎卦 KǍN GUA · KELOMPOK TIMUR"
        m_eb = f'坎卦 KǍN GUA · KELOMPOK TIMUR'
        s_eb = f'{yang_zhai["gua_hz"]}卦 {s_t["pinyin"].upper()} GUA · KELOMPOK {yang_zhai.get("group_id","Timur").upper()}'
        content = content.replace(m_eb, s_eb)

        # Zones grid (regenerate all 6 zones)
        zones = yang_zhai.get("zones", {})
        if zones:
            zone_specs = [
                ("pintu",       "門", "Pintu Utama",  "Mén · Pintu",            "PINTU",       False),
                ("dapur",       "灶", "Dapur",        "Zào · Tungku",           "DAPUR",       False),
                ("kamar",       "房", "Kamar Tidur",  "Fáng · Kamar",           "KAMAR",       False),
                ("ranjang",     "床", "Ranjang",      "Chuáng · Tempat Tidur",  "RANJANG",     False),
                ("altar",       "神", "Altar",        "Shén · Tempat Sembahyang","ALTAR",      False),
                ("kamar_mandi", "廁", "Kamar Mandi",  "Cè · Kamar Mandi",       "KAMAR MANDI", True),
            ]
            zone_blocks = []
            for key, hz_label, id_label, pinyin_label, comment_id, is_warn in zone_specs:
                if key in zones:
                    comment = f"<!-- {hz_label} {comment_id}{' (warn)' if is_warn else ''} -->"
                    zone_blocks.append(comment + "\n        " +
                                       regen_yz_zone(key, hz_label, id_label, pinyin_label,
                                                     zones[key], warn=is_warn))
            new_grid = (
                '<div class="yz-zones-grid">\n\n'
                '        '
                + '\n\n        '.join(zone_blocks)
                + '\n\n      </div>'
            )
            content = replace_block(content, r'<div class="yz-zones-grid">', new_grid)

        # Footer caption override
        if yang_zhai.get("footer_caption_html"):
            content = replace_block(content, r'<div class="footer-caption">',
                                    f'<div class="footer-caption">\n      {yang_zhai["footer_caption_html"]}\n    </div>')
    return content


# ============================================================
# RENDER
# ============================================================

# Pages that are 100%% shared (no per-subject content). Skip substitution.
SHARED_PAGES = {
    "page_02_toc.html",
    "page_03_intro.html",
    "page_05_bazi_opener.html",
    "page_15_ziwei_opener.html",
    "page_22_glossary.html",
    "page_23_disclaimer.html",
}


def render_pages(subject, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    pairs = build_substitutions(subject)

    rendered = []
    for fname in PAGE_ORDER:
        src = TEMPLATES_DIR / fname
        if not src.exists():
            print(f"[WARN] missing template: {fname}")
            continue
        # Shared pages: just copy from template (no read/write of unchanged content)
        dst = out_dir / fname
        if fname in SHARED_PAGES:
            import shutil as _sh
            _sh.copyfile(src, dst)
            rendered.append(dst)
            continue
        content = src.read_text(encoding="utf-8")
        for search, replace in pairs:
            if search and search != replace:
                content = content.replace(search, replace)
        content = apply_blocks(content, subject, fname)
        dst.write_text(content, encoding="utf-8")
        rendered.append(dst)
    return rendered


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Chrome / Edge not found")


def build_master(out_dir: Path, subject: dict) -> Path:
    name = subject["identity"]["name_id"]
    asset_url = "file:///" + str(ASSETS_DIR).replace("\\", "/") + "/"
    css_url = "file:///" + str(out_dir / "style.css").replace("\\", "/")
    shutil.copy(TEMPLATES_DIR / "style.css", out_dir / "style.css")

    styles, bodies = "", ""
    for fname in PAGE_ORDER:
        path = out_dir / fname
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        m_style = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
        if m_style:
            styles += f"\n/* === {fname} === */\n" + m_style.group(1) + "\n"
        m_body = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL)
        if m_body:
            body = m_body.group(1)
            body = re.sub(r'src="([^/"][^":]*\.(svg|png|jpg|jpeg))"',
                          lambda m: f'src="{asset_url}{m.group(1)}"', body)
            body = re.sub(r'href="([^/"][^":]*\.(svg|png|jpg|jpeg))"',
                          lambda m: f'href="{asset_url}{m.group(1)}"', body)
            bodies += body + "\n"

    master = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>{name} Ramalan PDF</title>
<link rel="stylesheet" href="{css_url}">
<style>
{styles}

@page {{ size: A4 portrait; margin: 0; }}
html, body {{ background: white !important; margin: 0 !important; padding: 0 !important; }}
.page {{
  page-break-after: always !important;
  page-break-inside: avoid !important;
  margin: 0 !important;
  box-shadow: none !important;
}}
.page:last-child {{ page-break-after: auto !important; }}
.ind-icon, .toc-row .ico, .pal-action .ico, .dc-item .ico, .xqc-item .ico {{
  font-family: 'Segoe UI Emoji','Segoe UI Symbol','Inter',system-ui,sans-serif !important;
}}
</style>
</head>
<body>
{bodies}
</body>
</html>
"""
    master_path = out_dir / "_master.html"
    master_path.write_text(master, encoding="utf-8")
    return master_path


def run_chrome(master_html: Path, out_pdf: Path) -> Path:
    chrome = find_chrome()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    tmp_pdf = Path(os.environ.get("TEMP", ".")) / f"_pdf_sb1_{os.getpid()}.pdf"
    src_url = "file:///" + str(master_html).replace("\\", "/")
    args = [
        chrome,
        "--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
        "--disable-extensions", "--disable-background-networking",
        "--allow-file-access-from-files",
        "--virtual-time-budget=8000",
        "--run-all-compositor-stages-before-draw",
        "--disable-features=PaintHolding",
        f"--print-to-pdf={tmp_pdf}",
        "--no-pdf-header-footer",
        src_url,
    ]
    subprocess.run(args, capture_output=True, timeout=90)
    if not tmp_pdf.exists():
        raise RuntimeError("Chrome did not produce PDF")
    try:
        shutil.move(str(tmp_pdf), str(out_pdf))
        return out_pdf
    except (PermissionError, OSError):
        alt = out_pdf.with_name(out_pdf.stem + f"_{time.strftime('%H%M%S')}.pdf")
        shutil.move(str(tmp_pdf), str(alt))
        return alt


def render_subject(subject_id: str) -> Path:
    t0 = time.time()
    json_path = DATA_DIR / f"{subject_id}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Missing subject data: {json_path}")
    subject = json.loads(json_path.read_text(encoding="utf-8"))

    out_dir = BUILD_DIR / subject_id
    if out_dir.exists():
        shutil.rmtree(out_dir)

    print(f"[1/4] Rendering pages from {json_path.name}...")
    rendered = render_pages(subject, out_dir)
    print(f"      {len(rendered)} pages rendered")

    print(f"[2/4] Building master HTML...")
    master = build_master(out_dir, subject)
    print(f"      Master: {master.stat().st_size//1024} KB")

    today = time.strftime("%Y-%m-%d")
    name = subject["identity"]["name_id"]
    hanzi = subject["identity"]["name_hanzi"]
    birth = subject["identity"]["birth_date"]
    pdf_name = f"{name}-{hanzi}-{birth}.pdf"
    # V4.3 production: PDFs go straight to OneDrive/Documents/Ramalan/#result/{date}/
    # (sama folder dengan V3 — user pakai V3 atau V4.3 hasilnya satu lokasi)
    out_pdf = ROOT.parent / "#result" / today / pdf_name

    print(f"[3/4] Chrome → PDF...")
    final = run_chrome(master, out_pdf)
    print(f"      PDF: {final.stat().st_size//1024} KB")

    print(f"[4/4] Saved: {final}")
    print(f"\nTotal: {time.time()-t0:.1f}s")
    return final


if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else "michele"
    render_subject(sid)
