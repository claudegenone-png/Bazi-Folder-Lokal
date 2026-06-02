"""V4.5, Parse subject MD (from Web Claude) into ocr.json data + tafsir blocks.

Input: data/subjects/{id}.md  (markdown with ## DATA + ## TAFSIR + ## CATATAN)
Output:
  - ocr_data: dict compatible with build_from_ocr.py expected schema
  - tafsir_blocks: {section_slug: html_string} ready to inject into templates

Section slugs (14 + footer + dayun-sub):
  kepribadian, family, shensha, caifu, career, daymaster,
  yangzhai, dayun_spotlight, dayun_seasons, dayun_footer,
  palace1, palace2, palace3, kesimpulan, sintesis
"""
from __future__ import annotations
import re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ============== SECTION NAME → SLUG ==============
SECTION_SLUGS = {
    "kepribadian": "kepribadian",
    "keluarga & pasangan": "family",
    "shen sha (bintang pelengkap)": "shensha",
    "shen sha": "shensha",
    "rezeki & caifu": "caifu",
    "karir & industri": "career",
    "day master & wu xing": "daymaster",
    "yang zhai (feng shui hunian)": "yangzhai",
    "yang zhai": "yangzhai",
    "da yun, spotlight (fase sekarang)": "dayun_spotlight",
    "da yun, spotlight": "dayun_spotlight",
    "da yun, 5 seasons": "dayun_seasons",
    "da yun, footer caption": "dayun_footer",
    "palace detail 1": "palace1",
    "palace detail 2": "palace2",
    "palace detail 3": "palace3",
    "kesimpulan": "kesimpulan",
    "sintesis & mantra": "sintesis",
    "sintesis & saran aksi": "sintesis",
    "sintesis": "sintesis",
}

# Word budgets for warnings (max words per section/sub-element)
BUDGETS = {
    "kepribadian": 90, "family": 90, "shensha": 90, "caifu": 90,
    "daymaster": 70, "yangzhai": 100, "ziwei_general": 100,
    "palace1": 140, "palace2": 140, "palace3": 140,
    "dayun_footer": 40,
}


# ============== MARKDOWN HELPERS ==============

def hanzi_to_span(s: str) -> str:
    """[[漢字]] → <span class="hz">漢字</span>"""
    return re.sub(r"\[\[([^\]]+)\]\]", r'<span class="hz">\1</span>', s)


def md_inline(s: str) -> str:
    """Convert inline MD (bold/italic) + [[Hanzi]] + escape HTML special chars
    (preserve our own tags). Order matters: escape first, then unescape Hanzi spans."""
    # 1) escape raw <, >, &, but not inside [[...]] (those are pure Hanzi anyway)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # 2) bold + italic (bold first, since ** > *)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*])\*([^*\n]+)\*(?![*])", r"<em>\1</em>", s)
    # 3) [[Hanzi]] → span (after escape, since [[ ]] don't have & < >)
    s = hanzi_to_span(s)
    return s.strip()


def split_paragraphs(text: str) -> list[str]:
    """Split prose into paragraphs by blank lines. Strip placeholder '(tulis di sini)'."""
    paras = []
    for p in re.split(r"\n\s*\n", text.strip()):
        p = p.strip()
        if not p or p == "(tulis di sini)":
            continue
        # Single-line collapse (join multiple lines into one paragraph)
        p = re.sub(r"\s*\n\s*", " ", p)
        paras.append(p)
    return paras


def word_count(s: str) -> int:
    """Strip HTML tags, count words."""
    s = re.sub(r"<[^>]+>", "", s)
    return len(s.split())


# ============== SECTION PARSER ==============

def parse_md(md_path: Path) -> tuple[dict, dict, list[str]]:
    """Returns (ocr_data, tafsir_blocks, warnings).

    ocr_data: dict with keys matching V4.5 .ocr.json schema (build_from_ocr.py input).
    tafsir_blocks: dict {slug: html_content_string}.
    warnings: list of strings (budget exceeded, missing fields, etc.).
    """
    text = md_path.read_text(encoding="utf-8")
    warnings: list[str] = []

    # Strip code-fence wrapper if Web Claude wrapped output in ```markdown ... ```
    text = re.sub(r"^```\w*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)

    # ----- Split into top-level sections (## headings) -----
    sections: dict[str, str] = {}
    # Heading 1: # name → grab name from there
    m_h1 = re.search(r"^#\s+(.+?)$", text, re.M)
    h1 = m_h1.group(1).strip() if m_h1 else ""

    # Find ## sections
    sec_pattern = re.compile(r"^##\s+(.+?)$", re.M)
    matches = list(sec_pattern.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections[name.upper()] = text[start:end].strip()

    data_text = sections.get("DATA", "")
    tafsir_text = sections.get("TAFSIR", "")

    # ----- Parse DATA -----
    ocr_data = parse_data_section(data_text, h1, warnings)

    # ----- Parse TAFSIR sub-sections (### headings) -----
    tafsir_blocks = parse_tafsir_section(tafsir_text, warnings)

    return ocr_data, tafsir_blocks, warnings


def parse_data_section(data_text: str, h1: str, warnings: list[str]) -> dict:
    """Convert MD DATA bullets → ocr.json schema dict."""
    raw: dict[str, str] = {}
    for line in data_text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        # Remove trailing comments (after #)
        val = re.sub(r"\s+#.*$", "", val)
        # Strip [[..]] wrap if present
        val = re.sub(r"\[\[([^\]]+)\]\]", r"\1", val)
        if val.lower() in ("null", "", "none"):
            continue
        raw[key] = val

    out: dict = {}

    # Identity
    out["name_id"] = raw.get("nama") or h1.split()[0] if h1 else ""
    if "hanzi" in raw:
        out["name_hanzi"] = raw["hanzi"]
    # Gender — prefer MD field `gender_hz` (foto label like 陽女/陰女) if provided.
    # Fallback: just store Indonesian "Pria"/"Wanita" as raw — engine sets exact 陽/陰
    # variant later from year stem polarity (definitional mapping, not BaZi rule).
    gender_hz_md = raw.get("gender_hz", "").strip()
    GENDER_HZ_VALID = {"陽男", "陰男", "陽女", "陰女"}
    if gender_hz_md and gender_hz_md in GENDER_HZ_VALID:
        out["gender_hz"] = gender_hz_md
    else:
        # Store Indonesian as-is; build_from_ocr.py derives 陽/陰 prefix from year stem
        g = raw.get("gender", "")
        if g.lower().startswith("p"):
            out["gender_hz"] = "Pria"  # placeholder, build derives 陽男/陰男
        elif g.lower().startswith("w"):
            out["gender_hz"] = "Wanita"  # placeholder, build derives 陽女/陰女
        else:
            out["gender_hz"] = g

    # Birth
    date = raw.get("lahir_tanggal", "")
    time_str = raw.get("lahir_jam", "")
    # Strip "(24-jam)" or other notes
    time_str = re.sub(r"\s*\(.*\)$", "", time_str).strip()
    if date and time_str:
        out["birth_solar"] = f"{date} {time_str}"

    # Pillars: pilar_tahun: 戊/子 → {stem_hz: 戊, branch_hz: 子}
    pillars = {}
    for slot_md, slot_out in [("pilar_tahun","year"),("pilar_bulan","month"),
                                ("pilar_hari","day"),("pilar_jam","hour")]:
        v = raw.get(slot_md, "")
        if "/" in v:
            stem, branch = [x.strip() for x in v.split("/", 1)]
            if stem and branch:
                pillars[slot_out] = {"stem_hz": stem, "branch_hz": branch}
    if pillars:
        out["pillars"] = pillars

    # Wuxing: 5 keys
    wx = {}
    for k_md, k_out in [("wuxing_jin","jin"),("wuxing_shui","shui"),
                          ("wuxing_mu","mu"),("wuxing_huo","huo"),("wuxing_tu","tu")]:
        v = raw.get(k_md)
        if v is not None:
            try:
                wx[k_out] = float(v)
            except ValueError:
                pass
    if len(wx) == 5:
        out["wuxing"] = wx

    # Yong/Ji shen + extended 5-kategori + format. Foto NCC main grid biasanya
    # tampilkan 5: 喜用神 / 用神 / 閒神 / 仇神 / 忌神 — semua dari foto, NO derive.
    if "yong_shen" in raw: out["yong_shen_hz"] = raw["yong_shen"]
    if "ji_shen" in raw:   out["ji_shen_hz"]  = raw["ji_shen"]
    if "xi_yong_shen" in raw: out["xi_yong_shen_hz"] = raw["xi_yong_shen"]
    if "xian_shen" in raw:    out["xian_shen_hz"]    = raw["xian_shen"]
    if "chou_shen" in raw:    out["chou_shen_hz"]    = raw["chou_shen"]
    if "format" in raw:    out["format_hz"]    = raw["format"]
    if "format_label_id" in raw: out["format_label_id"] = raw["format_label_id"]
    if "dm_label_id" in raw:     out["dm_label_id"]     = raw["dm_label_id"]

    # 十神 per pilar (foto NCC main grid label di atas tiap pillar stem)
    shi_shen_pp = {}
    for k_md, k_out in [("shi_shen_per_pilar_tahun", "year"),
                         ("shi_shen_per_pilar_bulan", "month"),
                         ("shi_shen_per_pilar_hari", "day"),
                         ("shi_shen_per_pilar_jam", "hour")]:
        v = raw.get(k_md)
        if v:
            shi_shen_pp[k_out] = v
    if shi_shen_pp:
        out["shi_shen_per_pilar"] = shi_shen_pp

    # 命宮 BaZi (life palace stem-branch dari foto main grid)
    if "ming_gong_bazi" in raw:
        out["ming_gong_bazi"] = raw["ming_gong_bazi"]

    # 體相 (5-element seasonal status) — 5 fields → dict {mu/huo/tu/jin/shui}
    # Source: foto Main BaZi grid kolom 體相. NO derive dari month branch.
    TIXIANG_VALID = {"旺", "相", "休", "囚", "死"}
    tx = {}
    for k_md, k_out in [("ti_xiang_mu", "mu"), ("ti_xiang_huo", "huo"),
                         ("ti_xiang_tu", "tu"), ("ti_xiang_jin", "jin"),
                         ("ti_xiang_shui", "shui")]:
        v = raw.get(k_md, "")
        if v and v in TIXIANG_VALID:
            tx[k_out] = v
    if tx:
        out["ti_xiang"] = tx

    # Da yun: "5:癸丑, 15:壬子, 25:辛亥, ..."
    # Da yun format: "10:丙辰, 20:乙卯, ..." OR with ten god "10:丙辰:正官, 20:乙卯:偏印, ..."
    # Ten god per cycle from foto (NCC main BaZi grid 大運 row labels), optional.
    da_yun_raw = raw.get("da_yun", "")
    if da_yun_raw:
        cycles = []
        # Pattern: age:stem branch (optional :ten_god 1-2 hanzi)
        for entry in da_yun_raw.split(","):
            entry = entry.strip()
            # Try with ten_god: "age:stem branch:ten_god" (ten_god 1-2 hanzi)
            m = re.match(r"(\d+)\s*:\s*([一-鿿])\s*([一-鿿])\s*:\s*([一-鿿]{1,2})", entry)
            if m:
                age = int(m.group(1))
                cycles.append({
                    "age_start": age,
                    "age_end": age + 9,
                    "stem_hz": m.group(2),
                    "branch_hz": m.group(3),
                    "ten_god_hz_md": m.group(4),  # foto-source label
                })
                continue
            # Fallback: without ten_god
            m = re.match(r"(\d+)\s*:\s*([一-鿿])\s*([一-鿿])", entry)
            if m:
                age = int(m.group(1))
                cycles.append({
                    "age_start": age,
                    "age_end": age + 9,
                    "stem_hz": m.group(2),
                    "branch_hz": m.group(3),
                })
        if cycles:
            out["da_yun"] = cycles

    # Marriage cocok/hindari (variable count, dari layar 婚配 — FULL-MD: ikuti foto persis)
    mar = {}
    BRANCHES_12 = set("子丑寅卯辰巳午未申酉戌亥")
    # Shio↔branch deterministic notation conversion (same entity, different writing).
    # NOT a BaZi derivation — equivalent to "Wanita"↔"女性". Foto remains authoritative.
    SHIO_TO_BRANCH = {"鼠":"子","牛":"丑","虎":"寅","兔":"卯","龍":"辰","蛇":"巳",
                       "馬":"午","羊":"未","猴":"申","雞":"酉","狗":"戌","豬":"亥"}
    for k_md, k_out in [("marriage_cocok","cocok_branches"),
                         ("marriage_hindari","hindari_branches")]:
        v = raw.get(k_md, "")
        if v:
            tokens = [x.strip() for x in v.split(",") if x.strip()]
            # Accept either branches (子丑寅...) or shio names (鼠牛虎...) — auto-map shio→branch
            branches = []
            for t in tokens:
                if t in BRANCHES_12:
                    branches.append(t)
                elif t in SHIO_TO_BRANCH:
                    branches.append(SHIO_TO_BRANCH[t])
            if branches:
                mar[k_out] = branches  # FULL-MD: no cap, ikuti foto (could be 2/3/4/5 entries)
    # Marriage relationship labels per branch (FULL-MD: from foto if 婚配 layar group;
    # else null. Engine does NOT derive label itself — strict no-rumus.)
    REL_VALID = {"三合", "六合", "六沖", "六害", "三刑", "破"}
    for k_md, k_out in [("marriage_cocok_relationships", "cocok_relationships"),
                         ("marriage_hindari_relationships", "hindari_relationships")]:
        v = raw.get(k_md, "")
        if v and v.lower() not in ("null", "none", ""):
            rel_map = {}
            # Format: "branch:label, branch:label, ..."
            for entry in v.split(","):
                entry = entry.strip()
                if ":" in entry:
                    b, _, lbl = entry.partition(":")
                    b = b.strip()
                    lbl = lbl.strip()
                    if b in BRANCHES_12 and lbl in REL_VALID:
                        rel_map[b] = lbl
            if rel_map:
                mar[k_out] = rel_map
    if mar:
        out["marriage"] = mar

    # Shio (屬) — eksplisit dari foto label, prefer MD value (FULL-MD).
    # Fallback ke year_branch lookup di build_from_ocr.py kalau MD null.
    shio_md = raw.get("shio_hz", "")
    SHIO_HZ_VALID = set("鼠牛虎兔龍蛇馬羊猴雞狗豬")
    if shio_md and shio_md in SHIO_HZ_VALID:
        out["shio_hz"] = shio_md

    # Yang Zhai gua
    if "yang_zhai_gua" in raw:
        out["yang_zhai_gua_hz"] = raw["yang_zhai_gua"]

    # Zi Wei
    zw = {}
    for k_md, k_out in [
        ("ziwei_ming_zhu","ming_zhu_hz"),
        ("ziwei_shen_zhu","shen_zhu_hz"),
        ("ziwei_ming_gong","ming_gong_branch_hz"),
        ("ziwei_shen_gong","shen_gong_branch_hz"),
        ("ziwei_wu_xing_ju","wu_xing_ju_hz"),
        ("ziwei_shi_jun","shi_jun_hz"),
    ]:
        if k_md in raw:
            zw[k_out] = raw[k_md]
    if zw:
        out["zi_wei"] = zw

    # ===== FULL-MD MODE fields =====

    # Day Master strength
    if "dm_strength" in raw:
        out["dm_strength_hz"] = raw["dm_strength"]
    else:
        out["dm_strength_hz"] = None
    if "dm_strength_label_id" in raw:
        out["dm_strength_label_id"] = raw["dm_strength_label_id"]
    else:
        out["dm_strength_label_id"] = None
    for k_md, k_out in [("dm_pos_score", "dm_pos_score"),
                          ("dm_neg_score", "dm_neg_score")]:
        v = raw.get(k_md)
        if v is None:
            out[k_out] = None
        else:
            try:
                out[k_out] = float(v)
            except ValueError:
                out[k_out] = None

    # Xiantian per-stem (10 fields → dict[str,int])
    XIANTIAN_STEMS = ("jia","yi","bing","ding","wu","ji","geng","xin","ren","gui")
    xiantian = {}
    for stem in XIANTIAN_STEMS:
        v = raw.get(f"xiantian_{stem}")
        if v is not None:
            try:
                xiantian[stem] = int(float(v))
            except ValueError:
                pass
    out["xiantian_per_stem"] = xiantian if xiantian else None
    # Sum sanity-check: 4-pillar BaZi visible+hidden stems usually total 12-15.
    # Sum way outside this range strongly suggests photo misread. Warn only — don't fail.
    if xiantian and len(xiantian) >= 8:
        total = sum(xiantian.values())
        if total < 10 or total > 18:
            import sys
            print(f"⚠ xiantian sum = {total} (expected 12-15 for 4-pillar BaZi). Cek ulang foto 先天體檢.", file=sys.stderr)

    # Wangdu per-stem (10 fields → dict[str,float])
    WANGDU_STEMS = ("jia_mu","yi_mu","bing_huo","ding_huo","wu_tu",
                    "ji_tu","geng_jin","xin_jin","ren_shui","gui_shui")
    wangdu = {}
    for stem in WANGDU_STEMS:
        v = raw.get(f"wangdu_{stem}")
        if v is not None:
            try:
                wangdu[stem] = float(v)
            except ValueError:
                pass
    out["wangdu_per_stem"] = wangdu if wangdu else None

    # Wangdu total (5 elements → dict[str,float])
    WANGDU_TOTAL = ("mu","huo","tu","jin","shui")
    wangdu_total = {}
    for el in WANGDU_TOTAL:
        v = raw.get(f"wangdu_total_{el}")
        if v is not None:
            try:
                wangdu_total[el] = float(v)
            except ValueError:
                pass
    out["wangdu_total"] = wangdu_total if wangdu_total else None

    # Da Yun arah (順行→forward, 逆行→backward)
    arah_raw = raw.get("da_yun_arah")
    if arah_raw is None:
        out["da_yun_arah_id"] = None
    elif "順" in arah_raw or arah_raw.lower() == "forward":
        out["da_yun_arah_id"] = "forward"
    elif "逆" in arah_raw or arah_raw.lower() == "backward":
        out["da_yun_arah_id"] = "backward"
    else:
        out["da_yun_arah_id"] = None

    # Da Yun start age
    sa_raw = raw.get("da_yun_start_age")
    if sa_raw is None:
        out["da_yun_start_age"] = None
    else:
        try:
            out["da_yun_start_age"] = int(float(sa_raw))
        except ValueError:
            out["da_yun_start_age"] = None

    # Shen Sha list ("天乙貴人@日, 文昌@月" → list of {hanzi, pillar})
    ss_raw = raw.get("shen_sha_list")
    if not ss_raw:
        out["shen_sha_list"] = None
    else:
        items = []
        for entry in ss_raw.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if "@" in entry:
                hz, _, pl = entry.partition("@")
                hz = hz.strip()
                pl = pl.strip()
                if hz:
                    items.append({"hanzi": hz, "pillar": pl or None})
            elif entry:
                items.append({"hanzi": entry, "pillar": None})
        out["shen_sha_list"] = items if items else None

    # Nayin per pillar
    NAYIN_MAP = [("nayin_tahun","year"),("nayin_bulan","month"),
                 ("nayin_hari","day"),("nayin_jam","hour")]
    nayin = {}
    for k_md, k_out in NAYIN_MAP:
        v = raw.get(k_md)
        if v is not None:
            nayin[k_out] = v
    out["nayin_per_pillar"] = nayin if nayin else None

    # Canggan per pillar
    CANGGAN_MAP = [("canggan_tahun","year"),("canggan_bulan","month"),
                   ("canggan_hari","day"),("canggan_jam","hour")]
    canggan = {}
    for k_md, k_out in CANGGAN_MAP:
        v = raw.get(k_md)
        if v is not None:
            canggan[k_out] = v
    out["canggan_per_pillar"] = canggan if canggan else None

    # Source marker
    out["_source"] = "MD via Web Claude (parse_md.py)"

    # Sanity warnings
    for required in ("name_id", "birth_solar"):
        if not out.get(required):
            warnings.append(f"DATA: missing required field {required}")

    return out


def parse_tafsir_section(tafsir_text: str, warnings: list[str]) -> dict[str, str]:
    """Parse ### sub-sections under ## TAFSIR.

    Returns dict {slug: html_content}. Each section's content is converted to HTML
    based on its known structure (paragraph / bullet list / structured).
    """
    blocks: dict[str, str] = {}
    if not tafsir_text:
        return blocks

    # Find ### sub-sections
    sub_pattern = re.compile(r"^###\s+(.+?)$", re.M)
    matches = list(sub_pattern.finditer(tafsir_text))
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(tafsir_text)
        body = tafsir_text[start:end].strip()
        # Remove HTML comments (budget hints) at the top
        body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()

        # Normalize separator: em-dash (—), en-dash (–), or " - " hyphen → ", "
        # so headings like "Da Yun — Spotlight" match SECTION_SLUGS keys ("da yun, spotlight").
        name_norm = re.sub(r"\s*[—–]\s*", ", ", name.lower())
        name_norm = re.sub(r"\s+-\s+", ", ", name_norm)
        # Collapse multiple spaces
        name_norm = re.sub(r"\s+", " ", name_norm).strip()
        slug = SECTION_SLUGS.get(name_norm)
        if not slug:
            warnings.append(f"TAFSIR: unknown section '{name}', skipped")
            continue

        # Render body based on section type
        html = render_tafsir_block(slug, body, warnings)
        blocks[slug] = html
        # Special: daymaster section may have ji_shen_body sub-field for Ji Shen card
        if slug == "daymaster":
            ji_body = _extract_paragraf_field_named(body, "ji_shen_body")
            if ji_body:
                blocks["_jishen_body"] = md_inline(ji_body)
        # Special: also expose Kepribadian's structured sub-fields for engine
        if slug == "kepribadian":
            blocks["_kepribadian_struct"] = parse_kepribadian_struct(body)
        if slug == "family":
            blocks["_family_struct"] = parse_family_struct(body)
        if slug == "shensha":
            blocks["_shensha_struct"] = parse_shensha_struct(body)
        if slug == "caifu":
            blocks["_caifu_struct"] = parse_caifu_struct(body)
        if slug == "career":
            blocks["_career_struct"] = parse_career_struct(body)
        if slug == "yangzhai":
            blocks["_yangzhai_struct"] = parse_yangzhai_struct(body)
        if slug == "palace1":
            blocks["_palace1_struct"] = parse_palace_struct(body, ("ming_gong","xiongdi","fuqi","zinu"))
        if slug == "palace2":
            blocks["_palace2_struct"] = parse_palace_struct(body, ("caibo","jie_e","qianyi","puyi"))
        if slug == "palace3":
            blocks["_palace3_struct"] = parse_palace_struct(body, ("guanlu","tianzhai","fude","fumu"))
        if slug == "kesimpulan":
            blocks["_kesimpulan_struct"] = parse_kesimpulan_struct(body)
        if slug == "sintesis":
            blocks["_sintesis_struct"] = parse_synthesis_struct(body)

    return blocks


def _extract_paragraf_field(body: str) -> str:
    """Extract the `paragraf: ...` field from new-structure section body.
    Returns empty string if absent."""
    m = re.search(r"^paragraf\s*:\s*(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
    if not m:
        return ""
    txt = m.group(1).strip()
    if not txt or "(tulis di sini)" in txt:
        return ""
    paras = split_paragraphs(txt)
    return paras[0] if paras else ""


def _extract_paragraf_field_named(body: str, name: str) -> str:
    """Extract a custom-named paragraf field (e.g., `ji_shen_body: ...`)."""
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
    if not m:
        return ""
    txt = m.group(1).strip()
    if not txt or "(tulis di sini)" in txt:
        return ""
    paras = split_paragraphs(txt)
    return paras[0] if paras else ""


def render_tafsir_block(slug: str, body: str, warnings: list[str]) -> str:
    """Convert TAFSIR section body (raw MD) → HTML snippet ready to inject.

    Each slug has a tailored renderer based on the prose structure expected.
    """
    # Strip placeholders
    body = body.replace("(tulis di sini)", "").strip()
    if not body:
        return ""

    # Specialized renderers for structured sections:
    if slug == "kepribadian":
        return _render_kepribadian(body, warnings)
    if slug == "career":
        return _render_career(body, warnings)
    if slug == "dayun_spotlight":
        return _render_dayun_spotlight(body, warnings)
    if slug == "dayun_seasons":
        return _render_dayun_seasons(body, warnings)
    if slug == "dayun_footer":
        return _render_dayun_footer(body, warnings)
    if slug == "kesimpulan":
        return _render_kesimpulan(body, warnings)
    if slug == "sintesis":
        return _render_sintesis(body, warnings)
    if slug in ("palace1","palace2","palace3"):
        return _render_palace(body, warnings)

    # Default for sections with paragraf: structured prefix (Shen Sha, Caifu, Yang Zhai, etc):
    paragraf = _extract_paragraf_field(body)
    if paragraf:
        return md_inline(paragraf)

    # Legacy: treat whole body as paragraphs
    paras = split_paragraphs(body)
    if not paras:
        return ""
    html = "<br><br>".join(md_inline(p) for p in paras)
    # Budget warning
    budget = BUDGETS.get(slug)
    if budget:
        wc = sum(word_count(p) for p in paras)
        if wc > budget * 1.2:
            warnings.append(f"TAFSIR[{slug}]: {wc} words > budget {budget} (+20% margin)")
    return html


# ----- Specialized renderers for structured sections -----

def _extract_field(body: str, key: str) -> str:
    """Extract `key: value` line from body."""
    m = re.search(rf"^{re.escape(key)}\s*:\s*(.+?)$", body, re.M)
    return m.group(1).strip() if m else ""


def _extract_bullets(body: str, prefix: str = "") -> list[str]:
    """Extract '- item' lines (optionally those matching `^- {prefix}`)."""
    items = []
    for line in body.splitlines():
        line = line.rstrip()
        m = re.match(r"^\s*-\s+(.+)$", line)
        if not m: continue
        v = m.group(1).strip()
        if prefix and not v.startswith(prefix):
            continue
        items.append(v[len(prefix):].strip() if prefix else v)
    return items


def parse_palace_struct(body: str, keys: tuple) -> dict:
    """Parse palace block: each key has {star, insight, action}."""
    out: dict = {}
    for key in keys:
        m = re.search(rf"^{key}\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
        if not m:
            continue
        sub = m.group(1)
        d = {}
        for f in ("star", "insight", "action"):
            mf = re.search(rf"^\s*-\s*{f}\s*:\s*(.+?)$", sub, re.M)
            if mf:
                v = mf.group(1).strip()
                if v and not v.startswith("{") and v.lower() != "null":
                    d[f] = v
        if d:
            out[key] = d
    return out


def parse_yangzhai_struct(body: str) -> dict:
    """Parse Yang Zhai zones[], list of {label, headline, pills, note}."""
    out: dict = {}
    zones_section = re.search(r"^zones\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
    if zones_section:
        items = []
        for line in zones_section.group(1).splitlines():
            m = re.match(r"^\s*-\s+(.+)$", line)
            if not m:
                continue
            entry = m.group(1).strip()
            d = {}
            for part in entry.split(";"):
                if ":" in part:
                    k, _, v = part.partition(":")
                    d[k.strip().lower()] = v.strip().strip('"')
            if d.get("label"):
                items.append(d)
        if items:
            out["zones"] = items
    return out


def parse_career_struct(body: str) -> dict:
    """Parse Karir & Industri: tags{fav,unfav}, industri[5]."""
    out: dict = {}
    # tags: 4 entries fav_1, fav_2, unfav_1, unfav_2
    tags_section = re.search(r"^tags\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
    if tags_section:
        sub = tags_section.group(1)
        tags = {}
        for k in ("fav_1", "fav_2", "unfav_1", "unfav_2"):
            m = re.search(rf"^\s*-\s*{k}\s*:\s*hz\s*:\s*(\S+);\s*label\s*:\s*(.+?)$", sub, re.M)
            if m:
                tags[k] = (m.group(1).strip(), m.group(2).strip())
        if tags:
            out["tags"] = tags
    # industri: 5 lines
    ind_section = re.search(r"^industri\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M | re.I)
    if ind_section:
        items = []
        for line in ind_section.group(1).splitlines():
            m = re.match(r"^\s*-\s+(.+)$", line)
            if not m:
                continue
            entry = m.group(1).strip()
            d = {}
            for part in entry.split(";"):
                if ":" in part:
                    k, _, v = part.partition(":")
                    d[k.strip().lower()] = v.strip()
            if d.get("nama"):
                items.append(d)
        if items:
            out["industri"] = items[:5]
    return out


def parse_caifu_struct(body: str) -> dict:
    """Parse Caifu structured fields: zheng_cai, pian_cai, rules[4]."""
    out: dict = {}
    for key in ("zheng_cai", "pian_cai"):
        m = re.search(rf"^{key}\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
        if not m:
            continue
        sub = m.group(1)
        card = {}
        for f in ("label", "percent", "body"):
            mf = re.search(rf"^\s*-\s*{f}\s*:\s*(.+?)$", sub, re.M)
            if mf:
                v = mf.group(1).strip().strip('"')
                if v and not v.startswith("{") and v.lower() != "null":
                    card[f] = v
        if card:
            out[key] = card
    # rules: list of "- title: X; context: Y; tone: Z"
    rules_section = re.search(r"^rules\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
    if rules_section:
        rules = []
        for line in rules_section.group(1).splitlines():
            m = re.match(r"^\s*-\s+(.+)$", line)
            if not m:
                continue
            entry = m.group(1).strip()
            d = {}
            for part in entry.split(";"):
                if ":" in part:
                    k, _, v = part.partition(":")
                    d[k.strip().lower()] = v.strip().strip('"')
            if d.get("title"):
                rules.append(d)
        if rules:
            out["rules"] = rules[:4]
    return out


def parse_shensha_struct(body: str) -> dict:
    """Parse Shen Sha structured fields: dominant_star{hanzi,pinyin,label_id,active_label} + strip."""
    out: dict = {}
    # dominant_star block
    m = re.search(r"^dominant_star\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
    if m:
        sub = m.group(1)
        ds = {}
        for k in ("hanzi", "pinyin", "label_id", "active_label"):
            mf = re.search(rf"^\s*-\s*{k}\s*:\s*(.+?)$", sub, re.M)
            if mf:
                v = mf.group(1).strip()
                if v and not v.startswith("{") and v.lower() != "null":
                    ds[k] = v
        if ds:
            out["dominant_star"] = ds
    # strip text, single-line content after "strip:"
    m = re.search(r"^strip\s*:\s*(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
    if m:
        v = m.group(1).strip()
        if v and "(tulis di sini)" not in v and v.lower() != "null":
            paras = split_paragraphs(v)
            if paras:
                out["strip"] = paras[0]
    return out


def parse_family_struct(body: str) -> dict:
    """Parse Keluarga & Pasangan section into 4 sub-cards.
    Returns: {pasangan: {vibe, headline, body}, anak: {...}, saudari: {...}, kepemimpinan: {...}}
    Missing/null sub-card → key absent. Engine fallback ke template default.
    """
    out: dict = {}
    for key in ("pasangan", "anak", "saudara", "saudari", "kepemimpinan"):
        # Each sub-card starts with "{key}:" and contains lines like "- vibe: X", "- headline: X", "- body: X"
        m = re.search(rf"^{key}\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
        if not m:
            continue
        sub_body = m.group(1)
        card = {}
        for field in ("vibe", "headline", "body"):
            mf = re.search(rf"^\s*-\s*{field}\s*:\s*(.+?)$", sub_body, re.M)
            if mf:
                v = mf.group(1).strip()
                if v and not v.startswith("{") and v.lower() != "null":
                    card[field] = v
        if card:
            out[key] = card
    return out


def parse_kepribadian_struct(body: str) -> dict:
    """Parse expanded Kepribadian section into structured fields.

    Returns: {paragraf, radar_traits[(hz,pinyin,label,score)], motto:{hanzi,nama,archetype,tag},
              power[bullets], shadow[bullets], optimum[bullets]}
    Each may be missing → engine falls back to per-stem default.
    """
    out: dict = {}
    # paragraf
    m = re.search(r"^paragraf\s*:\s*(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
    if m:
        para = m.group(1).strip()
        # Strip placeholder
        if para and "(tulis di sini)" not in para:
            paras = split_paragraphs(para)
            if paras:
                out["paragraf"] = paras[0]

    # radar_traits
    radar_section = re.search(r"^radar_traits\s*:\s*\n(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
    if radar_section:
        traits = []
        for line in radar_section.group(1).splitlines():
            m = re.match(r"^\s*-\s*([^/]+?)\s*/\s*([^/]+?)\s*/\s*([^:]+?)\s*:\s*(\d+(?:\.\d+)?)", line)
            if m:
                hz = m.group(1).strip()
                py = m.group(2).strip()
                lid = m.group(3).strip()
                score = float(m.group(4))
                if hz and not hz.startswith("{"):
                    traits.append((hz, py, lid, score))
        if len(traits) == 6:
            out["radar_traits"] = traits

    # motto
    motto_section = re.search(r"^motto\s*:\s*\n(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
    if motto_section:
        motto = {}
        for k in ("hanzi","nama","archetype","tag"):
            mm = re.search(rf"^\s*-\s*{k}\s*:\s*(.+?)$", motto_section.group(1), re.M)
            if mm:
                v = mm.group(1).strip()
                if v and not v.startswith("{"):
                    motto[k] = v
        if len(motto) == 4:
            out["motto"] = (motto["hanzi"], motto["nama"], motto["archetype"], motto["tag"])

    # power / shadow / optimum (bullet lists)
    for key in ("power", "shadow", "optimum"):
        sect = re.search(rf"^{key}\s*:\s*\n(.+?)(?=^[a-z_]+\s*:|\Z)", body, re.M | re.S)
        if sect:
            bullets = []
            for line in sect.group(1).splitlines():
                m = re.match(r"^\s*-\s+(.+)$", line)
                if m:
                    v = m.group(1).strip()
                    if v and not v.startswith("{"):
                        bullets.append(v)
            if len(bullets) >= 3:
                out[key] = bullets[:4]
    return out


def _render_kepribadian(body: str, warnings: list[str]) -> str:
    """Render kepribadian paragraf as the inner xqm-quote (the rest is consumed
    by build_pdf.py via parse_kepribadian_struct → engine substitution)."""
    s = parse_kepribadian_struct(body)
    para = s.get("paragraf", "")
    if not para:
        # Fallback: treat entire body as paragraph (legacy)
        ps = split_paragraphs(body)
        para = ps[0] if ps else ""
    if not para:
        return ""
    wc = word_count(para)
    if wc > 110:
        warnings.append(f"TAFSIR[kepribadian]: {wc} words > 90 budget")
    return md_inline(para)


def _render_career(body: str, warnings: list[str]) -> str:
    intro = _extract_field(body, "intro")
    industri_section = body.split("industri:")[-1] if "industri:" in body else ""
    industri = _extract_bullets(industri_section)
    parts = []
    if intro:
        parts.append(f'<p>{md_inline(intro)}</p>')
    if industri:
        items_html = []
        for entry in industri:
            # Format: "nama: X; unsur: Y; alasan: Z"
            d = {}
            for part in entry.split(";"):
                if ":" in part:
                    k, _, v = part.partition(":")
                    d[k.strip().lower()] = v.strip()
            nama = d.get("nama","")
            unsur = d.get("unsur","")
            alasan = d.get("alasan","")
            items_html.append(
                f'<li><strong>{md_inline(nama)}</strong> '
                f'(unsur {md_inline(unsur)}), {md_inline(alasan)}</li>'
            )
        parts.append("<ul>" + "".join(items_html) + "</ul>")
    return "".join(parts)



def _render_dayun_spotlight(body: str, warnings: list[str]) -> str:
    headline = _extract_field(body, "headline")
    bullets = []
    for n in range(1, 6):
        v = _extract_field(body, f"bullet {n}")
        if v: bullets.append(v)
    parts = []
    if headline:
        parts.append(f'<div class="sp-headline">{md_inline(headline)}</div>')
    if bullets:
        parts.append("<ul class='sp-bullets'>" +
                     "".join(f"<li>{md_inline(b)}</li>" for b in bullets) + "</ul>")
    return "".join(parts)


def _render_dayun_seasons(body: str, warnings: list[str]) -> str:
    items = _extract_bullets(body)
    if not items:
        return ""
    return "<ol class='dy-seasons'>" + \
           "".join(f"<li>{md_inline(x)}</li>" for x in items) + "</ol>"


def _render_dayun_footer(body: str, warnings: list[str]) -> str:
    paras = split_paragraphs(body)
    if not paras:
        return ""
    return md_inline(paras[0])


def _render_kesimpulan(body: str, warnings: list[str]) -> str:
    """Returns just the quote (kept simple). Detailed struct extracted via parse_kesimpulan_struct."""
    quote = _extract_field(body, "quote").strip('"\'')
    if quote:
        return md_inline(quote)
    return ""


def parse_kesimpulan_struct(body: str) -> dict:
    """Parse Kesimpulan structured fields:
    - quote (single line)
    - stats: { format_desc, yong_desc, dayun_desc, umur_desc, kompat_desc }
    - life_map: { lalu, sekarang, berikutnya }
    """
    out: dict = {}
    quote = _extract_field(body, "quote").strip('"\'')
    if quote:
        out["quote"] = quote
    # stats block
    m = re.search(r"^stats\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
    if m:
        sub = m.group(1)
        s = {}
        for k in ("format_desc","yong_desc","dayun_desc","umur_desc","kompat_desc"):
            mf = re.search(rf"^\s*-\s*{k}\s*:\s*(.+?)$", sub, re.M)
            if mf:
                v = mf.group(1).strip()
                if v and v.lower() != "null":
                    s[k] = v
        if s:
            out["stats"] = s
    # life_map block
    m = re.search(r"^life_map\s*:\s*\n((?:^\s*-.*\n?)+)", body, re.M)
    if m:
        sub = m.group(1)
        lm = {}
        for k in ("lalu","sekarang","berikutnya"):
            mf = re.search(rf"^\s*-\s*{k}\s*:\s*(.+?)$", sub, re.M)
            if mf:
                v = mf.group(1).strip()
                if v and v.lower() != "null":
                    lm[k] = v
        if lm:
            out["life_map"] = lm
    return out


def _render_sintesis(body: str, warnings: list[str]) -> str:
    """Renders only the `opening` paragraph for the headline-quote anchor.
    Trio cards + actions are emitted by engine via parse_synthesis_struct.
    """
    m = re.search(r"^opening\s*:\s*\n?(.+?)(?=^\s*(?:trio|actions)\s*:|\Z)",
                  body, re.M | re.S)
    opening = m.group(1).strip() if m else _extract_field(body, "opening")
    if not opening:
        return ""
    paras = split_paragraphs(opening)
    text = paras[0] if paras else opening
    return md_inline(text)


def parse_synthesis_struct(body: str) -> dict:
    """Parse Sintesis structured fields:
    - opening (single paragraph)
    - trio: { kekuatan: {hanzi, pinyin, body}, tantangan: {...}, tindakan: {...} }
    - actions: [ {title, context, tag} x 5 ]
    """
    out: dict = {}
    opening = _extract_field(body, "opening")
    # opening can be multi-line; capture until next blank-line + key
    m = re.search(r"^opening\s*:\s*\n?(.+?)(?=^\s*(?:trio|actions)\s*:|\Z)", body, re.M | re.S)
    if m:
        op = m.group(1).strip()
        if op:
            out["opening"] = op
    elif opening:
        out["opening"] = opening

    # trio block: from "trio:" to "actions:" (or end)
    m = re.search(r"^trio\s*:\s*\n(.+?)(?=^actions\s*:|\Z)", body, re.M | re.S)
    if m:
        trio_body = m.group(1)
        trio: dict = {}
        for key in ("kekuatan", "tantangan", "tindakan"):
            mk = re.search(
                rf"^{key}\s*:\s*\n((?:^\s*-.*\n?)+)",
                trio_body, re.M
            )
            if not mk:
                continue
            sub = mk.group(1)
            d: dict = {}
            for f in ("hanzi", "pinyin", "arti", "body"):
                mf = re.search(rf"^\s*-\s*{f}\s*:\s*(.+?)$", sub, re.M)
                if mf:
                    v = mf.group(1).strip()
                    if v and v.lower() != "null":
                        d[f] = v
            if d:
                trio[key] = d
        if trio:
            out["trio"] = trio

    # actions: list of "- title: ...; context: ...; tag: ..."
    m = re.search(r"^actions\s*:\s*\n(.+?)\Z", body, re.M | re.S)
    if m:
        sub = m.group(1)
        items = []
        for line in sub.splitlines():
            line = line.strip()
            mb = re.match(r"^-\s+(.+)$", line)
            if not mb:
                continue
            row = mb.group(1)
            d: dict = {}
            for part in row.split(";"):
                p = part.strip()
                mk = re.match(r"^(title|context|tag)\s*:\s*(.+)$", p)
                if mk:
                    d[mk.group(1)] = mk.group(2).strip()
            if d.get("title"):
                items.append(d)
        if items:
            out["actions"] = items
    return out


def _render_palace(body: str, warnings: list[str]) -> str:
    """Palace sections have 4 sub-paragraphs (one per palace), separated by blank lines."""
    paras = split_paragraphs(body)
    if not paras:
        return ""
    return "".join(f"<p>{md_inline(p)}</p>" for p in paras)


# ============== CLI ==============

if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python parse_md.py <md_path>")
        sys.exit(1)
    md_path = Path(sys.argv[1])
    ocr, tafsir, warns = parse_md(md_path)
    print("=== OCR DATA ===")
    print(json.dumps(ocr, ensure_ascii=False, indent=2))
    print(f"\n=== TAFSIR BLOCKS ({len(tafsir)} sections) ===")
    for slug in tafsir:
        wc = word_count(tafsir[slug])
        print(f"  [{slug}] {wc}w · {len(tafsir[slug])}chars")
    if warns:
        print("\n=== WARNINGS ===")
        for w in warns:
            print(f"  ⚠ {w}")
