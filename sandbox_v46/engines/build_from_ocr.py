"""Sandbox1 V4.3 - Auto-build subject.json from {id}.ocr.json + native pillar compute.

Pipeline (called by cli.py after OCR step):
  1. Load data/subjects/{id}.ocr.json (merged OCR output)
  2. Resolve identity (name, hanzi, gender, birth_date, birth_time, age)
  3. Native compute pillars (compute_pillars.py) — saves OCR tokens, validated
  4. Cross-check OCR pillars vs native (warn if mismatch, prefer native)
  5. Synthesize wuxing %, yong/ji shen blocks, format, mantra fallback
  6. Generate da_yun cycles via build_subject.build_da_yun + 5 evenly-split seasons
  7. Infer marriage relationship_hz per branch (six classical relations)
  8. Yang Zhai gua + 6 zones (zones=Michele defaults if not OCR'd)
  9. Zi Wei center info from OCR
  10. Write data/subjects/{id}.json (LinRuYi defaults remain for any missing fields)
"""
from __future__ import annotations
import json, sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "subjects"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lookups import STEMS, BRANCHES, BRANCH_ORDER, TRIGRAMS
from build_subject import build_da_yun, compute_wuxing_percentages, _ten_god_pair
from compute_pillars import compute_pillars, da_yun_direction, da_yun_start_age
# V4.6: interpret.py NOT imported. Narrative MUST come from photo OCR; if missing, raise.
# interpret.py preserved in repo as reference only — see TASK 3 in audit notes.


# ============== relationship rules ==============
PAIR_MAP = {  # 六合
    "子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯",
    "辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午",
}
TRIPLE_GROUPS = [{"申","子","辰"},{"巳","酉","丑"},{"寅","午","戌"},{"亥","卯","未"}]
HARM_MAP = {  # 六害
    "子":"未","未":"子","丑":"午","午":"丑","寅":"巳","巳":"寅",
    "卯":"辰","辰":"卯","申":"亥","亥":"申","酉":"戌","戌":"酉",
}
PUNISH_MAP = {  # 三刑 (simplified pairwise)
    "寅":["巳","申"],"巳":["寅","申"],"申":["寅","巳"],
    "丑":["戌","未"],"戌":["丑","未"],"未":["丑","戌"],
    "子":["卯"],"卯":["子"],
    "辰":["辰"],"午":["午"],"酉":["酉"],"亥":["亥"],
}
BREAK_MAP = {  # 破
    "子":"酉","酉":"子","午":"卯","卯":"午","申":"巳","巳":"申",
    "寅":"亥","亥":"寅","辰":"丑","丑":"辰","戌":"未","未":"戌",
}
# id labels
REL_ID = {"三合":"TRIPLE","六合":"PAIR","六沖":"BENTROK","六害":"MENGHAMBAT","三刑":"GESEKAN","破":"MERETAKKAN"}
COCOK_REASON = {
    "三合":"Triple harmony.",
    "六合":"Pair harmony.",
}
HINDARI_REASON = {
    "六沖":"Bentrok langsung.",
    "六害":"Halangan halus.",
    "三刑":"Hukuman.",
    "破":"Pemecah.",
}


def infer_relationship(self_hz: str, other_hz: str) -> str | None:
    """Return one of 三合/六合/六沖/六害/三刑/破 or None if no relation."""
    if other_hz == self_hz:
        return None
    # 六沖 = opposite (idx + 6)
    si = BRANCH_ORDER.index(self_hz)
    oi = BRANCH_ORDER.index(other_hz)
    if (oi - si) % 12 == 6:
        return "六沖"
    # 三合
    for grp in TRIPLE_GROUPS:
        if self_hz in grp and other_hz in grp:
            return "三合"
    if PAIR_MAP.get(self_hz) == other_hz:
        return "六合"
    if HARM_MAP.get(self_hz) == other_hz:
        return "六害"
    if other_hz in PUNISH_MAP.get(self_hz, []):
        return "三刑"
    if BREAK_MAP.get(self_hz) == other_hz:
        return "破"
    return None


def _build_marriage(self_branch_hz: str, cocok_list: list[str], hindari_list: list[str]) -> dict:
    cocok = []
    for b in cocok_list:
        rel = infer_relationship(self_branch_hz, b) or "三合"
        cocok.append({
            "branch_hz": b,
            "id": BRANCHES[b]["shio_id"],
            "relationship_hz": rel,
            "relationship_id": REL_ID.get(rel, "TRIPLE"),
            "reason_id": COCOK_REASON.get(rel, "Selaras."),
        })
    hindari = []
    for b in hindari_list:
        rel = infer_relationship(self_branch_hz, b) or "六沖"
        hindari.append({
            "branch_hz": b,
            "id": BRANCHES[b]["shio_id"],
            "relationship_hz": rel,
            "relationship_id": REL_ID.get(rel, "BENTROK"),
            "reason_id": HINDARI_REASON.get(rel, "Bentrok."),
        })
    return {
        "self_branch_index": BRANCH_ORDER.index(self_branch_hz),
        "cocok": cocok,
        "hindari": hindari,
    }


# ============== element helpers ==============
EL_HZ_TO_KEY = {"金":"jin","水":"shui","木":"mu","火":"huo","土":"tu"}
EL_HZ_TO_LABEL = {"金":"Logam","水":"Air","木":"Kayu","火":"Api","土":"Tanah"}
EL_HZ_TO_SCLASS = {"金":"s-jin","水":"s-shui","木":"s-mu","火":"s-huo","土":"s-tu"}


def _stem_to_dm_block(stem_hz: str, strength_id: str = "Kuat") -> dict:
    s = STEMS[stem_hz]
    label_map = {
        "甲":"Pohon Besar","乙":"Pohon Kecil",
        "丙":"Api Matahari","丁":"Api Lilin",
        "戊":"Tanah Gunung","己":"Tanah Sawah",
        "庚":"Logam Pedang","辛":"Logam Halus",
        "壬":"Air Sungai","癸":"Air Hujan",
    }
    return {
        "stem_hz": stem_hz,
        "stem_element_hz": s["el_hz"],
        "stem_element_id": s["el_id"],
        "polarity_id": s["polarity_id"],
        "label_id": label_map.get(stem_hz, s["el_id"]),
        "label_long_id": s["el_id"],
        "pinyin": f"{s['pinyin']} {s['el_hz']}",
        "strength_id": strength_id,
        "strength_hz": "旺" if strength_id == "Kuat" else "弱",
    }


def _shio_block(branch_hz: str) -> dict:
    b = BRANCHES[branch_hz]
    return {
        "branch_hz": branch_hz,
        "branch_pinyin": b["pinyin"],
        "id": b["shio_id"],
        "id_upper": b["shio_id"].upper(),
        "svg_red": f"{b['shio_id']}-Merah.svg",
        "svg_black": f"{b['shio_id']}-Hitam.svg",
    }


def _yong_ji_block(elements_hz: str, label_id: str) -> dict:
    parts = elements_hz.split() if isinstance(elements_hz, str) else elements_hz
    elements_id = " & ".join(EL_HZ_TO_LABEL.get(p, p) for p in parts)
    return {
        "elements_hz": " ".join(parts),
        "elements_id": elements_id,
        "label_id": label_id,
    }


def _seasons_from_dayun(da_yun: dict) -> list:
    """Build 5 seasons (5 pairs of 10-yr cycles). V4.6: generic name by index +
    age range — NO synthesized poetic name. If photo provides season label, builder
    overrides via subject.json post-build."""
    cycles = da_yun["cycles"]
    cur_idx = da_yun.get("current_index", 0)
    cur_season_idx = cur_idx // 2
    seasons = []
    for i in range(5):
        c1 = cycles[i*2]
        c2 = cycles[i*2 + 1] if i*2 + 1 < len(cycles) else c1
        el_class = c1["element_class"]
        el_hz = STEMS[c1["stem_hz"]]["el_hz"]
        s = {
            "el_class": el_class.replace("el-", "s-"),
            "el_hz": el_hz,
            "name_id": f"Fase {i+1}",
            "age_start": c1["age_start"],
            "age_end": c2["age_end"],
        }
        if i == cur_season_idx:
            s["is_current"] = True
        seasons.append(s)
    return seasons


# V4.6: _TEN_GOD_TONE & _EL_TONE deleted — synthesized narrative tables removed.

# Indonesian weekday + period helpers
_WEEKDAY_ID = {0:"Minggu",1:"Senin",2:"Selasa",3:"Rabu",4:"Kamis",5:"Jumat",6:"Sabtu"}

def _indo_period(hour: int) -> str:
    if 5 <= hour < 11: return "pagi"
    if 11 <= hour < 15: return "siang"
    if 15 <= hour < 18: return "sore"
    return "malam"

# Hour branch by clock hour (子=23-1, 丑=1-3, ..., 亥=21-23)
_HOUR_BRANCH = ["子","丑","丑","寅","寅","卯","卯","辰","辰","巳","巳","午","午","未","未","申","申","酉","酉","戌","戌","亥","亥","子"]

def _hour_branch_hz(h: int) -> str:
    return _HOUR_BRANCH[h % 24]

# Year stem+branch pinyin for lunar text
_STEM_PY = {"甲":"Jia","乙":"Yi","丙":"Bing","丁":"Ding","戊":"Wu","己":"Ji","庚":"Geng","辛":"Xin","壬":"Ren","癸":"Gui"}
_BRANCH_PY = {"子":"Zi","丑":"Chou","寅":"Yin","卯":"Mao","辰":"Chen","巳":"Si","午":"Wu","未":"Wei","申":"Shen","酉":"You","戌":"Xu","亥":"Hai"}

def _lunar_pinyin_pair(stem_hz: str, branch_hz: str) -> str:
    return f"{_STEM_PY.get(stem_hz, stem_hz)} {_BRANCH_PY.get(branch_hz, branch_hz)}"


# V4.6: NO _inject_dayun_narrative_v46 — synthesized narrative removed.
# Da Yun current-cycle text comes from OCR.dayun_per_cycle (per cycle), wired below.


def _pillars_match(p1: dict, p2: dict) -> bool:
    for k in ["year","month","day","hour"]:
        if p1[k]["stem_hz"]+p1[k]["branch_hz"] != p2[k]["stem_hz"]+p2[k]["branch_hz"]:
            return False
    return True


def build_subject_from_ocr(subject_id: str,
                            name_id: str | None = None,
                            name_hanzi: str | None = None,
                            gender_id: str | None = None,
                            birth_date: str | None = None,
                            birth_time: str | None = None,
                            ) -> dict:
    """Convert merged OCR JSON + identity to full subject.json. Identity overrides OCR."""
    ocr_path = DATA_DIR / f"{subject_id}.ocr.json"
    if not ocr_path.exists():
        raise FileNotFoundError(f"Run OCR first: missing {ocr_path}")
    ocr = json.loads(ocr_path.read_text(encoding="utf-8"))

    # ---- Identity ----
    name_id = name_id or ocr.get("name_id") or subject_id.title()
    name_hanzi = name_hanzi or ocr.get("name_hanzi") or "?"
    gender_id = gender_id or _normalize_gender(ocr.get("gender_hz") or ocr.get("gender_id"))
    birth_date = birth_date or _normalize_birth_solar(ocr.get("birth_solar"))
    birth_time = birth_time or _normalize_birth_time(ocr.get("birth_solar"))

    if not (birth_date and birth_time):
        raise ValueError(f"Need birth_date + birth_time (OCR gave: {ocr.get('birth_solar')!r})")

    print(f"[BUILD] identity: {name_id} {name_hanzi} · {gender_id} · {birth_date} {birth_time}")

    # ---- Pillars (Phase 4 native, save tokens) ----
    y, mo, d = map(int, birth_date.split("-"))
    h, mi = map(int, birth_time.split(":"))
    pillars = compute_pillars(y, mo, d, h, mi)
    print(f"[BUILD] native pillars: {''.join(pillars[k]['stem_hz']+pillars[k]['branch_hz'] for k in ['year','month','day','hour'])}")

    # Cross-check vs OCR pillars (if available)
    ocr_pillars = ocr.get("pillars")
    if ocr_pillars and isinstance(ocr_pillars, dict) and all(k in ocr_pillars for k in ["year","month","day","hour"]):
        try:
            ocr_pn = {k: {"stem_hz": ocr_pillars[k]["stem_hz"], "branch_hz": ocr_pillars[k]["branch_hz"]} for k in ["year","month","day","hour"]}
            if not _pillars_match(pillars, ocr_pn):
                print(f"[BUILD][WARN] OCR pillars differ from native — using native compute")
                for k in ["year","month","day","hour"]:
                    n = pillars[k]["stem_hz"] + pillars[k]["branch_hz"]
                    o = ocr_pillars[k].get("stem_hz","?") + ocr_pillars[k].get("branch_hz","?")
                    if n != o:
                        print(f"        {k}: native={n} ocr={o}")
        except Exception as e:
            print(f"[BUILD][WARN] OCR pillars unparseable: {e}")

    dm_stem = pillars["day"]["stem_hz"]
    year_stem = pillars["year"]["stem_hz"]
    direction = da_yun_direction(year_stem, gender_id)
    start_age = da_yun_start_age(y, mo, d, h, gender_id, year_stem)
    print(f"[BUILD] da yun: dir={direction} start_age={start_age}")

    # Age at report
    today = date.today()
    bdt = date(y, mo, d)
    age_at_report = today.year - bdt.year - ((today.month, today.day) < (bdt.month, bdt.day))

    # Current da yun cycle index
    age_into_dy = age_at_report - start_age
    cur_idx = max(0, min(9, age_into_dy // 10)) if age_into_dy >= 0 else 0

    # ---- Da yun cycles + seasons ----
    cycles = build_da_yun(start_age, direction, pillars["month"], dm_stem)
    if 0 <= cur_idx < len(cycles):
        cycles[cur_idx]["is_current"] = True
    da_yun = {
        "start_age": start_age,
        "direction_id": direction,
        "current_index": cur_idx,
        "axis_marks": [start_age + i*10 for i in range(11)],
        "cycles": cycles,
    }
    da_yun["seasons"] = _seasons_from_dayun(da_yun)
    # narrative injection moved below — needs wuxing + strength

    # ---- Wu Xing ----
    wx_raw = ocr.get("wuxing") or {}
    if all(k in wx_raw for k in ["jin","shui","mu","huo","tu"]):
        wx_values = {k: float(wx_raw[k]) for k in ["jin","shui","mu","huo","tu"]}
    else:
        # Fallback: count from pillars (rough, 1.0 each stem + 0.5 each branch hidden)
        wx_values = {"jin":0.0,"shui":0.0,"mu":0.0,"huo":0.0,"tu":0.0}
        for k in ["year","month","day","hour"]:
            s = STEMS[pillars[k]["stem_hz"]]["el_hz"]
            wx_values[EL_HZ_TO_KEY[s]] += 1.0
        print(f"[BUILD][WARN] no OCR wuxing — using crude stem-count fallback")
    wx = compute_wuxing_percentages(wx_values)
    dm_el_key = EL_HZ_TO_KEY[STEMS[dm_stem]["el_hz"]]
    wx["self_value"] = wx_values[dm_el_key]

    # V4.6: day_master strength HARUS dari foto (raw_hz). Tidak hitung 25% threshold.
    dm_strength_block = ocr.get("day_master_strength")
    if not dm_strength_block or not dm_strength_block.get("raw_hz"):
        raise ValueError(
            "day_master_strength missing — re-shoot foto 日主旺度 (label 旺/相/休/囚/死/強/弱) "
            "lalu re-run OCR (--force)."
        )
    raw_hz = dm_strength_block["raw_hz"]
    # Map Hanzi label → Indo: 旺/相/強 = Kuat, 休/囚/死/弱 = Lemah
    is_strong = raw_hz in ("旺", "相", "強") or dm_strength_block.get("is_strong") is True
    strength_id = "Kuat" if is_strong else "Lemah"
    wx["self_strength_id"] = "KUAT" if is_strong else "LEMAH"
    wx["dm_strength_raw_hz"] = raw_hz
    wx["dm_strength_pos_score"] = dm_strength_block.get("pos_score")
    wx["dm_strength_neg_score"] = dm_strength_block.get("neg_score")

    # ---- Yong/Ji Shen 5-role (V4.6) ----
    yong_ji_shen = ocr.get("yong_ji_shen") or []
    if not yong_ji_shen:
        raise ValueError(
            "yong_ji_shen missing — re-shoot foto 用神/喜神/閒神/仇神/忌神 "
            "(yong_ji_shen 5-role array) lalu re-run OCR (--force)."
        )
    # Backward compat: derive yong_block + ji_block from array (for templates that
    # still reference single yong_shen + ji_shen blocks). Render adapt → 5-card.
    yong_role = next((r for r in yong_ji_shen if r.get("role") == "用神"), None)
    ji_role   = next((r for r in yong_ji_shen if r.get("role") == "忌神"), None)
    ys_hz = " ".join(yong_role["elements_hz"]) if yong_role else ""
    js_hz = " ".join(ji_role["elements_hz"]) if ji_role else ""
    yong_block = _yong_ji_block(ys_hz, "Penopang & Pengarah") if ys_hz else None
    ji_block = _yong_ji_block(js_hz, "Pelumat & Pemicu") if js_hz else None

    # ---- Format (multi-format array) ----
    formats_array = ocr.get("formats") or []
    if not formats_array:
        # Backward compat: kalau OCR hanya kasih format_hz tunggal, bungkus jadi array
        legacy_fmt = ocr.get("format_hz")
        if legacy_fmt:
            formats_array = [{"hz": legacy_fmt, "glyph": legacy_fmt.replace("格", ""), "is_primary": True}]
        else:
            raise ValueError("formats array missing — re-shoot foto 格局 lalu re-run OCR (--force).")
    primary_fmt = next((f for f in formats_array if f.get("is_primary")), formats_array[0])
    fmt_hz = primary_fmt.get("hz")
    fmt_pinyin_map = {
        "正官格":("Zheng Guan Ge","Penjaga Disiplin"),
        "七殺格":("Qi Sha Ge","Pemurnian"),
        "正財格":("Zheng Cai Ge","Pengelola Disiplin"),
        "偏財格":("Pian Cai Ge","Pengusaha Lincah"),
        "正印格":("Zheng Yin Ge","Pelajar Tekun"),
        "偏印格":("Pian Yin Ge","Mentor Bayangan"),
        "食神格":("Shi Shen Ge","Pencipta Lembut"),
        "傷官格":("Shang Guan Ge","Kritikus Tajam"),
        "比肩格":("Bi Jian Ge","Pundak Sama"),
        "劫財格":("Jie Cai Ge","Saudara Sebanding"),
    }
    fp, fl = fmt_pinyin_map.get(fmt_hz, ("Ge","Format"))
    # OCR can override label_id (format_label_id) if photo shows different label
    fmt_block = {"hz": fmt_hz, "pinyin": fp, "label_id": ocr.get("format_label_id") or fl}

    # ---- Da Yun narrative ----
    # V4.6: ONLY photo OCR. No synthesizer fallback. Cycles without OCR narrative
    # remain blank — render.py raises error if those cycles' narrative is referenced.
    ocr_dayun = ocr.get("dayun_per_cycle") or []
    for ocr_cyc in ocr_dayun:
        age_s = ocr_cyc.get("age_start")
        for cyc in da_yun["cycles"]:
            if cyc["age_start"] == age_s:
                if ocr_cyc.get("hz"): cyc["narrative_hz"] = ocr_cyc["hz"]
                if ocr_cyc.get("id"): cyc["narrative_id"] = ocr_cyc["id"]
                cyc["_source"] = "photo"
                break
    cur_idx = da_yun["current_index"]
    cur = da_yun["cycles"][cur_idx]
    if cur.get("narrative_id"):
        da_yun["spotlight_bullets_html"] = [cur["narrative_id"]]
        da_yun["footer_caption_html"] = (
            f'{name_id} · fase <span class="hz">{cur.get("ten_god_hz","")}</span> '
            f'({cur["age_start"]}–{cur["age_end"]})'
        )
        da_yun["_spotlight_source"] = "photo"
    else:
        da_yun["_spotlight_source"] = "missing"

    # ---- Marriage ----
    self_branch = pillars["year"]["branch_hz"]
    mar = ocr.get("marriage") or {}
    cocok_branches = mar.get("cocok_branches") or []
    hindari_branches = mar.get("hindari_branches") or []
    marriage = _build_marriage(self_branch, cocok_branches, hindari_branches) if (cocok_branches or hindari_branches) else None

    # ---- Yang Zhai ----
    gua_hz = ocr.get("yang_zhai_gua_hz")
    yang_zhai = None
    if gua_hz and gua_hz in TRIGRAMS:
        t = TRIGRAMS[gua_hz]
        opp = {"N":"南","S":"北","E":"西","W":"東","NE":"西南","SW":"東北","NW":"東南","SE":"西北"}[t["pos"]]
        opp_abbr = {"N":"S","S":"U","E":"B","W":"T","NE":"BD","SW":"TL","NW":"TG","SE":"BL"}[t["pos"]]
        yang_zhai = {
            "gua_hz": gua_hz,
            "gua_pinyin": t["pinyin"],
            "gua_label_id": t["label_id"],
            "gua_direction_id": t["dir_id"],
            "gua_direction_abbr": t["dir_abbr"],
            "group_id": t["group"],
            "sumbu_hoki_hz": f"{t['dir_cn']}↔{opp}",
            "sumbu_hoki_id": f"{t['dir_abbr']} ↔ {opp_abbr}",
            "trigram_symbol": t["symbol"],
            "zones": ocr.get("yang_zhai_zones") or [],  # V4.6 pass-through
        }

    # ---- Zi Wei (V4.6: NO fallback defaults — None kalau OCR kosong) ----
    zw_in = ocr.get("zi_wei") or {}
    branch_id_map = {b: BRANCHES[b]["shio_id"] for b in BRANCHES}
    zw_out = {}
    for src, dst in [
        ("ming_zhu_hz","ming_zhu_hz"),
        ("shen_zhu_hz","shen_zhu_hz"),
        ("ming_gong_branch_hz","ming_gong_hz"),
        ("shen_gong_branch_hz","shen_gong_hz"),
        ("wu_xing_ju_hz","wu_xing_ju_hz"),
        ("shi_jun_hz","shi_jun_hz"),
    ]:
        zw_out[dst] = zw_in.get(src)  # None kalau missing
    zw_out["ming_gong_id"] = f"Istana Hidup · {branch_id_map.get(zw_out['ming_gong_hz'], '?')}" if zw_out["ming_gong_hz"] else None
    zw_out["shen_gong_id"] = f"Istana Tubuh · {branch_id_map.get(zw_out['shen_gong_hz'], '?')}" if zw_out["shen_gong_hz"] else None
    zw_out["shi_jun_id"]   = f"Penguasa Waktu · {branch_id_map.get(zw_out['shi_jun_hz'], '?')}" if zw_out["shi_jun_hz"] else None
    zw_out["ming_zhu_id"]  = "Penguasa Hidup" if zw_out["ming_zhu_hz"] else None
    zw_out["shen_zhu_id"]  = "Penguasa Tubuh" if zw_out["shen_zhu_hz"] else None
    wxj = zw_out["wu_xing_ju_hz"]
    wxj_map = {"水二局":"Aliran Air Dua","木三局":"Aliran Kayu Tiga","金四局":"Aliran Logam Empat","土五局":"Aliran Tanah Lima","火六局":"Aliran Api Enam"}
    zw_out["wu_xing_ju_id"] = wxj_map.get(wxj, wxj) if wxj else None
    zw_out["si_hua"] = zw_in.get("si_hua") or {}
    # TASK 2/3 pass-through: 12 palaces + overall narrative
    zw_out["palaces"] = ocr.get("zi_wei_palaces") or []
    zw_out["overall_narrative"] = ocr.get("ziwei_overall_narrative")

    # ---- Identity enrichment for cover/profile substitutions ----
    import sxtwl as _sx
    _d = _sx.fromSolar(y, mo, d)
    lunar_y = _d.getLunarYear()
    lunar_m = _d.getLunarMonth()
    lunar_d = _d.getLunarDay()
    weekday_id = _WEEKDAY_ID[_d.getWeek()]
    period_id = _indo_period(h)
    hour_branch = _hour_branch_hz(h)
    period_label = f"{period_id} · {hour_branch}時"
    year_stem_branch = pillars["year"]["stem_hz"] + pillars["year"]["branch_hz"]
    lunar_pinyin = _lunar_pinyin_pair(pillars["year"]["stem_hz"], pillars["year"]["branch_hz"])
    lunar_date_text_new = (
        f"tanggal {lunar_d} bulan {lunar_m} tahun {year_stem_branch} "
        f"({lunar_pinyin} · {lunar_y})"
    )
    roc_year = lunar_y - 1911
    lunar_republic_text = f"民國 {roc_year} 年 {lunar_m} 月 {lunar_d} 日"

    # ---- Narrative blocks from OCR (V4.6) ----
    # Each section has {hz: ..., id: ...} extracted verbatim from photo. id is the
    # Indonesian translation that goes into the PDF. Provenance tracked separately.
    # V4.6 FINAL: detail_sections is a flexible Hanzi-keyed dict directly from OCR.
    detail_sections = ocr.get("detail_sections") or {}
    shen_sha_stars = ocr.get("shen_sha_stars") or []
    liu_nian_per_year = ocr.get("liu_nian_per_year") or []
    xingqing_paragraph = ocr.get("xingqing_paragraph")  # single para; fallback to detail "性情"
    if not xingqing_paragraph:
        for k in ("性情", "命格", "個性"):
            if k in detail_sections:
                xingqing_paragraph = detail_sections[k]
                break

    def _hz_keys(*hz_labels):
        """True if ANY of given Hanzi labels exists in detail_sections with non-empty content."""
        for lbl in hz_labels:
            blk = detail_sections.get(lbl)
            if isinstance(blk, dict) and (blk.get("hz") or blk.get("id_summary")):
                return True
        return False

    # ---- _page_status: AUTO from data presence (V4.6 FINAL Section D) ----
    page_status = {
        "profile":         True,  # identity + pillars always present
        "daymaster":       bool(wx),
        "marriage_compat": marriage is not None,
        "xingqing":        bool(xingqing_paragraph) or _hz_keys("性情", "命格"),
        "family":          _hz_keys("父母", "兄弟", "子女"),
        "shensha":         bool(shen_sha_stars) or _hz_keys("神煞"),
        "caifu":           _hz_keys("財富", "財帛", "田宅"),
        "career":          _hz_keys("官祿", "事業"),
        "yangzhai":        _hz_keys("陽宅") or bool(yang_zhai and yang_zhai.get("zones")),
        "dayun":           bool(da_yun.get("cycles")) and bool(liu_nian_per_year),
        "ziwei_opener":    bool(zw_out.get("palaces")),
        "ziwei_chart":     bool(zw_out.get("palaces")),
        "palace_marriage": _hz_keys("夫妻"),
        "palace_fortune":  _hz_keys("福德", "疾厄", "遷移"),
        "kesimpulan":      _hz_keys("全局總論"),
        "synthesis":       True,  # always — auto-summary from active sections
    }

    # ---- TASK 7: Coverage report (no raise) ----
    print(f"\n[V4.6] === Coverage report subject {subject_id} ===")
    print(f"{'SECTION_HZ':<14} {'SOURCE':<10} {'CHARS_HZ':>10}")
    if detail_sections:
        for hz_label, blk in detail_sections.items():
            if isinstance(blk, dict):
                chars = len(blk.get("hz","")) if blk.get("hz") else 0
                print(f"{hz_label:<14} {'photo':<10} {chars:>10}")
    else:
        print("(no detail_sections extracted)")
    if shen_sha_stars:
        print(f"  shen_sha_stars: {len(shen_sha_stars)}")
    if liu_nian_per_year:
        print(f"  liu_nian_per_year: {len(liu_nian_per_year)}")
    n_active = sum(1 for v in page_status.values() if v)
    n_total = len(page_status)
    skipped = [k for k, v in page_status.items() if not v]
    print(f"\n[V4.6] PDF akan render: {n_active}/{n_total} page kandidat ({len(skipped)} dibuang).")
    if skipped:
        print(f"[V4.6] Halaman dibuang: {', '.join(skipped)}")

    # ---- Final assembly ----
    out = {
        "subject_id": subject_id,
        "_built_by": "build_from_ocr.py V4.6 FINAL",
        "identity": {
            "name_id": name_id,
            "name_hanzi": name_hanzi,
            "gender_id": gender_id,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_day_name": weekday_id,
            "birth_period_id": period_id,
            "birth_hour_branch_hz": hour_branch,
            "birth_hour_period_label": period_label,
            "lunar_date_text_new": lunar_date_text_new,
            "lunar_year_pillar_hz": year_stem_branch,
            "lunar_republic_text": lunar_republic_text,
            "age_at_report": age_at_report,
        },
        "shio": _shio_block(self_branch),
        "day_master": _stem_to_dm_block(dm_stem, strength_id),
        "pillars": pillars,
        "wuxing": wx,
        "yong_shen": yong_block,
        "ji_shen": ji_block,
        "format": fmt_block,
        "da_yun": da_yun,
        "marriage": marriage,
        "yang_zhai": yang_zhai,
        "zi_wei": zw_out,
        # V4.6 FINAL: flexible Hanzi-keyed sections + new pass-throughs
        "detail_sections": detail_sections,
        "shen_sha_stars": shen_sha_stars,
        "liu_nian_per_year": liu_nian_per_year,
        "xingqing_paragraph": xingqing_paragraph,
        "yong_ji_shen": yong_ji_shen,           # 5-role array
        "formats": formats_array,                # multi-format array
        "_page_status": page_status,
    }

    out_path = DATA_DIR / f"{subject_id}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[BUILD] -> {out_path}")
    return out


def _normalize_gender(g):
    if not g: return None
    g = str(g).strip()
    if g in ("陽男","陰男","男","Pria","pria","M","male","Male"): return "Pria"
    if g in ("陽女","陰女","女","Wanita","wanita","F","female","Female"): return "Wanita"
    return g


def _normalize_birth_solar(s):
    """Return ISO YYYY-MM-DD from a 'YYYY-MM-DD HH:MM' or 'YYYY/M/D ...' string."""
    if not s: return None
    s = str(s).replace("/", "-").strip()
    parts = s.split()
    date_part = parts[0]
    if "-" in date_part:
        y,m,d = date_part.split("-")
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    return None


def _normalize_birth_time(s):
    if not s: return None
    s = str(s).strip()
    parts = s.split()
    if len(parts) >= 2:
        t = parts[1]
        if ":" in t:
            h,mi = t.split(":")[:2]
            return f"{int(h):02d}:{int(mi):02d}"
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_from_ocr.py <subject_id> "
              "[--name X --hanzi 漢字 --gender Pria/Wanita --date YYYY-MM-DD --time HH:MM]")
        sys.exit(1)
    sid = sys.argv[1]
    kw = {}
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == "--name" and i+1 < len(args): kw["name_id"] = args[i+1]
        elif a == "--hanzi" and i+1 < len(args): kw["name_hanzi"] = args[i+1]
        elif a == "--gender" and i+1 < len(args): kw["gender_id"] = args[i+1]
        elif a == "--date" and i+1 < len(args): kw["birth_date"] = args[i+1]
        elif a == "--time" and i+1 < len(args): kw["birth_time"] = args[i+1]
    build_subject_from_ocr(sid, **kw)
