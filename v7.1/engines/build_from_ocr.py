"""V4.5 FULL-MD MODE: build subject.json from ocr_data MD-source pull only.

All compute zones removed. Engine no longer derives pillars, da yun direction/start age,
wuxing %, DM strength, yong/ji shen, format, marriage relations, yang zhai gua,
Zi Wei chart, or shen sha. All values come from MD (parse_md.py output).

Preserved (non-compute logic):
- Ten gods deterministic mapping (via build_subject.build_da_yun → _ten_god_pair)
- Identity enrichment (age = current_year - birth_year, weekday name from date)
- Lunar date conversion (display only, via sxtwl)
- Element class, shio static lookups
- Wuxing percentage math (% calc from MD raw values, not stem-counting)

MD null → subject.json field is Python None (render layer converts None → "—").
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
from build_subject import build_da_yun, compute_wuxing_percentages, _ten_god_pair, _element_class


# ============== element helpers ==============
EL_HZ_TO_KEY = {"金":"jin","水":"shui","木":"mu","火":"huo","土":"tu"}
EL_HZ_TO_LABEL = {"金":"Logam","水":"Air","木":"Kayu","火":"Api","土":"Tanah"}
EL_HZ_TO_SCLASS = {"金":"s-jin","水":"s-shui","木":"s-mu","火":"s-huo","土":"s-tu"}


def _stem_to_dm_block(stem_hz: str, strength_id=None, strength_hz=None, label_md=None) -> dict:
    """label_md: optional override dari MD field `dm_label_id`. Kalau MD provide,
    pakai itu. Fallback ke hardcoded translation table (Indonesian poetic naming)."""
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
        "label_id": label_md or label_map.get(stem_hz, s["el_id"]),
        "label_long_id": s["el_id"],
        "pinyin": f"{s['pinyin']} {s['el_hz']}",
        "strength_id": strength_id,
        "strength_hz": strength_hz,
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


def _yong_ji_block(elements_hz, label_id: str):
    if not elements_hz:
        return None
    parts = elements_hz.split() if isinstance(elements_hz, str) else elements_hz
    elements_id = " & ".join(EL_HZ_TO_LABEL.get(p, p) for p in parts)
    return {
        "elements_hz": " ".join(parts),
        "elements_id": elements_id,
        "label_id": label_id,
    }


def _seasons_from_dayun(da_yun: dict) -> list:
    """Build 5 seasons from da_yun cycles: pair (1-2)(3-4)(5-6)(7-8)(9-10), 20yr each."""
    cycles = da_yun["cycles"]
    cur_idx = da_yun.get("current_index", 0)
    cur_season_idx = cur_idx // 2
    seasons = []
    season_names = ["Pemurnian Awal","Belajar & Mentor","Berbagi Panggung","Berkarya Tenang","Memetik Rezeki"]
    for i in range(5):
        if i*2 >= len(cycles):
            break
        c1 = cycles[i*2]
        c2 = cycles[i*2 + 1] if i*2 + 1 < len(cycles) else c1
        el_class = c1["element_class"]
        el_hz = STEMS[c1["stem_hz"]]["el_hz"]
        s = {
            "el_class": el_class.replace("el-", "s-"),
            "el_hz": el_hz,
            "name_id": season_names[i],
            "age_start": c1["age_start"],
            "age_end": c2["age_end"],
        }
        if i == cur_season_idx:
            s["is_current"] = True
        seasons.append(s)
    return seasons


# ============== da yun narrative fallback ==============
_TEN_GOD_TONE = {
    "比肩": ("Pundak Sama", "membangun kemandirian", "Sekutu Sebanding"),
    "劫財": ("Perampok Harta", "uji solidaritas & finansial", "Saudara & Tekanan"),
    "食神": ("Pencipta", "mengalirkan ide jadi karya", "Output Mekar"),
    "傷官": ("Kritikus Tajam", "berekspresi tajam & memberontak halus", "Suara Berani"),
    "正財": ("Rezeki Tetap", "membangun aset & komitmen panjang", "Wealth Mantap"),
    "偏財": ("Rezeki Bisnis", "menjajaki peluang & jaringan", "Wealth Lincah"),
    "正官": ("Otoritas", "memikul tanggung jawab & jabatan", "Disiplin & Posisi"),
    "七殺": ("Pemurnian", "menempa diri lewat tekanan", "Tantangan Tegas"),
    "偏官": ("Pemurnian", "menempa diri lewat tekanan", "Tantangan Tegas"),
    "正印": ("Pelajaran", "menyerap ilmu & dukungan tetua", "Belajar Tenang"),
    "偏印": ("Mentor Bayangan", "intuisi & jalur tidak konvensional", "Hikmat Diam"),
}
_EL_TONE = {"木":"Kayu · pertumbuhan","火":"Api · ekspresi","土":"Tanah · stabil","金":"Logam · ketegasan","水":"Air · adaptasi"}

_WEEKDAY_ID = {0:"Minggu",1:"Senin",2:"Selasa",3:"Rabu",4:"Kamis",5:"Jumat",6:"Sabtu"}

def _indo_period(hour: int) -> str:
    if 5 <= hour < 11: return "pagi"
    if 11 <= hour < 15: return "siang"
    if 15 <= hour < 18: return "sore"
    return "malam"

_HOUR_BRANCH = ["子","丑","丑","寅","寅","卯","卯","辰","辰","巳","巳","午","午","未","未","申","申","酉","酉","戌","戌","亥","亥","子"]

def _hour_branch_hz(h: int) -> str:
    return _HOUR_BRANCH[h % 24]

_STEM_PY = {"甲":"Jia","乙":"Yi","丙":"Bing","丁":"Ding","戊":"Wu","己":"Ji","庚":"Geng","辛":"Xin","壬":"Ren","癸":"Gui"}
_BRANCH_PY = {"子":"Zi","丑":"Chou","寅":"Yin","卯":"Mao","辰":"Chen","巳":"Si","午":"Wu","未":"Wei","申":"Shen","酉":"You","戌":"Xu","亥":"Hai"}

def _lunar_pinyin_pair(stem_hz, branch_hz) -> str:
    return f"{_STEM_PY.get(stem_hz, stem_hz or '?')} {_BRANCH_PY.get(branch_hz, branch_hz or '?')}"


def _inject_dayun_narrative_fallback(da_yun: dict, dm_stem: str, name_id: str) -> None:
    cycles = da_yun.get("cycles") or []
    if not cycles:
        return
    cur_idx = da_yun.get("current_index", 0)
    cur = cycles[max(0, min(cur_idx, len(cycles)-1))]
    nxt = cycles[cur_idx+1] if cur_idx+1 < len(cycles) else None

    tg_hz = cur.get("ten_god_hz", "")
    tg_id, tg_focus, tg_combo = _TEN_GOD_TONE.get(tg_hz, (cur.get("ten_god_id","Fase"), "menjalani fase ini", "Kombinasi"))
    el_hz = STEMS[cur["stem_hz"]]["el_hz"]
    el_tone = _EL_TONE.get(el_hz, f"{el_hz} · arus")
    dm_el = STEMS[dm_stem]["el_hz"]

    if "spotlight_headline_html" not in da_yun:
        da_yun["spotlight_headline_html"] = (
            f'Fase <span class="hz">{tg_hz}</span> ({tg_id}), periode utama untuk {tg_focus}'
        )
    if "spotlight_tag_tone_html" not in da_yun:
        da_yun["spotlight_tag_tone_html"] = el_tone
    if "spotlight_tag_combo_html" not in da_yun:
        da_yun["spotlight_tag_combo_html"] = tg_combo
    if "spotlight_tag_combo_pair" not in da_yun:
        da_yun["spotlight_tag_combo_pair"] = [cur["stem_hz"], cur["branch_hz"]]
    if "spotlight_bullets_html" not in da_yun:
        bullets = [
            f'<strong>Fokus utama</strong>, pilar <span class="hz">{tg_hz}</span> mendorong Anda untuk {tg_focus}. Selaraskan agenda 10 tahun ini ke arah tersebut.',
            f'<strong>Energi {el_hz}</strong>, batang <span class="hz">{cur["stem_hz"]}</span> ({el_hz}) berinteraksi dengan Day Master <span class="hz">{dm_stem}</span> ({dm_el}); tone fase: {el_tone}.',
            f'<strong>Cabang <span class="hz">{cur["branch_hz"]}</span></strong> menentukan medan harian, kebiasaan, lingkungan, dan relasi yang dibangun di rentang umur {cur["age_start"]}–{cur["age_end"]} akan jadi pondasi fase berikutnya.',
        ]
        if nxt:
            bullets.append(
                f'<strong>Setelah {cur["age_end"]}</strong> masuk <span class="hz">{nxt["stem_hz"]}{nxt["branch_hz"]} ({nxt["ten_god_hz"]})</span>, {_TEN_GOD_TONE.get(nxt["ten_god_hz"], (nxt.get("ten_god_id",""), "fase berikutnya", ""))[1]}. Siapkan transisi sekarang.'
            )
        da_yun["spotlight_bullets_html"] = bullets

    if "footer_caption_html" not in da_yun:
        da_yun["footer_caption_html"] = (
            f'{name_id} sedang di fase <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">{tg_hz}</span> '
            f'({cur["age_start"]}–{cur["age_end"]}), {tg_focus}. '
            f'Periode {cur["age_start"]}–{(nxt["age_end"] if nxt else cur["age_end"])} adalah jendela kunci membentuk kebiasaan, jaringan, dan arah karir.'
        )


def build_subject_from_ocr(subject_id: str,
                            name_id: str | None = None,
                            name_hanzi: str | None = None,
                            gender_id: str | None = None,
                            birth_date: str | None = None,
                            birth_time: str | None = None,
                            ) -> dict:
    """V4.5 FULL-MD: convert ocr_data MD-pull into subject.json. No compute."""
    ocr_path = DATA_DIR / f"{subject_id}.ocr.json"
    if not ocr_path.exists():
        raise FileNotFoundError(f"Run OCR first: missing {ocr_path}")
    ocr = json.loads(ocr_path.read_text(encoding="utf-8"))

    # ---- Identity ----
    name_id = name_id or ocr.get("name_id") or subject_id.title()
    name_hanzi = name_hanzi or ocr.get("name_hanzi") or ""
    gender_id = gender_id or _normalize_gender(ocr.get("gender_hz") or ocr.get("gender_id"))
    birth_date = birth_date or _normalize_birth_solar(ocr.get("birth_solar"))
    birth_time = birth_time or _normalize_birth_time(ocr.get("birth_solar"))

    if not (birth_date and birth_time):
        raise ValueError(f"Need birth_date + birth_time (OCR gave: {ocr.get('birth_solar')!r})")

    print(f"[BUILD] identity: {name_id} {name_hanzi} · {gender_id} · {birth_date} {birth_time}")

    y, mo, d = map(int, birth_date.split("-"))
    h, mi = map(int, birth_time.split(":"))

    # ---- Pillars (Zone 1: MD pull, no sxtwl compute) ----
    ocr_pillars = ocr.get("pillars") or {}
    pillars = {}
    for k in ["year", "month", "day", "hour"]:
        p = (ocr_pillars.get(k) if isinstance(ocr_pillars, dict) else None) or {}
        pillars[k] = {
            "stem_hz": p.get("stem_hz"),
            "branch_hz": p.get("branch_hz"),
        }
    dm_stem = pillars["day"]["stem_hz"]
    self_branch = pillars["day"]["branch_hz"]
    pillars_complete = all(pillars[k]["stem_hz"] and pillars[k]["branch_hz"] for k in ["year","month","day","hour"])
    if pillars_complete:
        print(f"[BUILD] MD pillars: {''.join(pillars[k]['stem_hz']+pillars[k]['branch_hz'] for k in ['year','month','day','hour'])}")
    else:
        print(f"[BUILD][WARN] MD pillars incomplete — downstream blocks may be None")

    # ---- Da Yun direction & start age (Zones 2, 3: MD pull) ----
    direction = ocr.get("da_yun_arah_id")
    start_age = ocr.get("da_yun_start_age")
    print(f"[BUILD] da yun: dir={direction} start_age={start_age}")

    # Age at report (preserved: identity enrichment)
    today = date.today()
    bdt = date(y, mo, d)
    # 虛歲 (Chinese traditional age) = year_now - year_born + 1. Match foto NCC convention
    # (BaZi software always uses 虛歲 for 流年/大運 forecasting). Foto lijialing 2026 = 39 歲.
    age_at_report = today.year - bdt.year + 1

    # ---- Da yun cycles + seasons (FULL-MD: cycles dari MD list langsung, BUKAN
    # recompute dari month_pillar). Engine hanya add ten_god labels per cycle
    # (deterministic 5-element mapping, sama di semua software BaZi). ----
    da_yun = None
    md_dayun_list = ocr.get("da_yun")  # list of {age_start, age_end, stem_hz, branch_hz}
    if isinstance(md_dayun_list, list) and md_dayun_list and dm_stem:
        try:
            # Use MD cycles directly — only enrich with ten_god + n index.
            cycles = []
            for i, cyc in enumerate(md_dayun_list[:10]):
                stem = cyc.get("stem_hz")
                branch = cyc.get("branch_hz")
                age_s = cyc.get("age_start")
                age_e = cyc.get("age_end") if cyc.get("age_end") is not None else (age_s + 9 if age_s is not None else None)
                if not stem or not branch:
                    continue
                # Ten god: prefer MD `ten_god_hz_md` (foto-source) → fallback deterministic
                ten_god_md = cyc.get("ten_god_hz_md")
                if ten_god_md:
                    ten_god_hz = ten_god_md
                    # Indonesian label lookup — canonical mapping (match build_subject.py)
                    _TENGOD_HZ_TO_ID = {
                        "比肩": "Pundak Sama", "劫財": "Saudara Sebanding",
                        "食神": "Pencipta", "傷官": "Kritikus Tajam",
                        "偏財": "Rezeki Bisnis", "正財": "Rezeki Tetap",
                        "七殺": "Pemurnian", "正官": "Otoritas",
                        "偏印": "Mentor", "正印": "Pelajaran",
                    }
                    ten_god_id = _TENGOD_HZ_TO_ID.get(ten_god_md, ten_god_md)
                else:
                    # Fallback: deterministic 5-element mapping (sama di semua software)
                    ten_god_hz, ten_god_id = _ten_god_pair(dm_stem, stem)
                cycles.append({
                    "n": i + 1,
                    "age_start": age_s,
                    "age_end": age_e,
                    "stem_hz": stem,
                    "branch_hz": branch,
                    "ten_god_hz": ten_god_hz,
                    "ten_god_id": ten_god_id,
                    "element_class": _element_class(stem),
                })
            if cycles:
                # Determine current cycle by age_at_report
                cur_idx = 0
                for i, cyc in enumerate(cycles):
                    if cyc["age_start"] is not None and cyc["age_end"] is not None:
                        if cyc["age_start"] <= age_at_report <= cyc["age_end"]:
                            cur_idx = i
                            break
                cycles[cur_idx]["is_current"] = True
                # Axis marks: start ages of each cycle + final age (cycles[-1].age_end + 1)
                first_age = cycles[0]["age_start"] or 0
                axis = [c["age_start"] for c in cycles] + [(cycles[-1]["age_end"] or first_age + 99) + 1]
                da_yun = {
                    "start_age": first_age,
                    "direction_id": direction,  # informational only (from MD)
                    "current_index": cur_idx,
                    "axis_marks": axis[:11],
                    "cycles": cycles,
                }
                da_yun["seasons"] = _seasons_from_dayun(da_yun)
                _inject_dayun_narrative_fallback(da_yun, dm_stem, name_id)
        except Exception as e:
            print(f"[BUILD][WARN] da_yun build skipped: {e}")
            da_yun = None

    # ---- Wu Xing % (Zone 4: BaZi-derived from 4 pillars, total=8) ----
    # Source priority: (1) BaZi 4-pillar count [4 stems + 4 branches main element]
    # (2) MD foto explicit wuxing dict (legacy xiantian sum) — kept for backwards compat
    # BaZi formula uses TAHUN-Year stem/branch convention per software.
    STEM_EL = {"甲":"mu","乙":"mu","丙":"huo","丁":"huo","戊":"tu","己":"tu",
                "庚":"jin","辛":"jin","壬":"shui","癸":"shui"}
    BRANCH_EL = {"寅":"mu","卯":"mu","巳":"huo","午":"huo","辰":"tu","戌":"tu",
                  "丑":"tu","未":"tu","申":"jin","酉":"jin","亥":"shui","子":"shui"}
    wx = None
    if pillars_complete:
        counts = {"jin":0,"shui":0,"mu":0,"huo":0,"tu":0}
        for k in ["year","month","day","hour"]:
            stem = pillars[k]["stem_hz"]
            br = pillars[k]["branch_hz"]
            if stem in STEM_EL:
                counts[STEM_EL[stem]] += 1
            if br in BRANCH_EL:
                counts[BRANCH_EL[br]] += 1
        try:
            wx_values = {k: float(counts[k]) for k in ["jin","shui","mu","huo","tu"]}
            wx = compute_wuxing_percentages(wx_values)
            if dm_stem and dm_stem in STEMS:
                dm_el_key = EL_HZ_TO_KEY[STEMS[dm_stem]["el_hz"]]
                wx["self_value"] = wx_values[dm_el_key]
            print(f"[BUILD] wuxing (BaZi 4-pillar): {counts}, total={sum(counts.values())}")
        except Exception as e:
            print(f"[BUILD][WARN] wuxing BaZi calc skipped: {e}")
            wx = None
    # Legacy fallback (only if pillars incomplete AND MD has explicit wuxing dict)
    if wx is None:
        wx_raw = ocr.get("wuxing")
        if isinstance(wx_raw, dict) and all(
                k in wx_raw and wx_raw[k] is not None for k in ["jin","shui","mu","huo","tu"]):
            try:
                wx_values = {k: float(wx_raw[k]) for k in ["jin","shui","mu","huo","tu"]}
                wx = compute_wuxing_percentages(wx_values)
                if dm_stem and dm_stem in STEMS:
                    dm_el_key = EL_HZ_TO_KEY[STEMS[dm_stem]["el_hz"]]
                    wx["self_value"] = wx_values[dm_el_key]
                print(f"[BUILD] wuxing (legacy MD xiantian sum): {wx_values}")
            except Exception as e:
                print(f"[BUILD][WARN] wuxing legacy calc skipped: {e}")
                wx = None

    # ---- DM strength (Zone 5: MD pull, threshold ≥25% REMOVED) ----
    strength_id = ocr.get("dm_strength_label_id")  # "Kuat"/"Lemah"/"Seimbang" or None
    strength_hz = ocr.get("dm_strength_hz")        # "旺"/"弱"/"平" or None
    if wx is not None:
        wx["self_strength_id"] = strength_id.upper() if strength_id else None

    # Day master block. label_id prefer MD `dm_label_id` if foto/MD provide custom label.
    day_master = None
    if dm_stem and dm_stem in STEMS:
        day_master = _stem_to_dm_block(dm_stem, strength_id, strength_hz, ocr.get("dm_label_id"))

    # ---- Yong Shen / Ji Shen (Zone 6: MD pull, 5-element heuristic REMOVED) ----
    ys_hz = ocr.get("yong_shen_hz")
    js_hz = ocr.get("ji_shen_hz")
    yong_block = _yong_ji_block(ys_hz, "Penopang & Pengarah")
    ji_block = _yong_ji_block(js_hz, "Pelumat & Pemicu")

    # ---- Format (Zone 7: MD pull, default "正官格" REMOVED) ----
    fmt_hz = ocr.get("format_hz")
    fmt_block = None
    if fmt_hz:
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
        # Prefer MD `format_label_id` if foto/extraction provides custom Indonesian label
        fl = ocr.get("format_label_id") or fl
        fmt_block = {"hz": fmt_hz, "pinyin": fp, "label_id": fl}

    # ---- Marriage (Zone 8: 100% MD/foto. Wheel visualization:
    #   - Center = subject's shio (from MD shio_hz, no fallback)
    #   - Cocok shios from MD → generic "cocok" label for gold-pair styling
    #   - Hindari shios from MD → generic "hindari" label for red-clash styling
    # NO classical rule derivation (三合/六合/六沖/六害/三刑/破). NO fake Hanzi label
    # (engine tidak claim 六合/六沖 kalau foto tidak categorize — itu misleading).
    # If MD provides explicit `marriage_*_relationships` (foto group), use that instead. ----
    marriage_md = ocr.get("marriage") or {}
    cocok_md = marriage_md.get("cocok_branches") if isinstance(marriage_md, dict) else None
    hindari_md = marriage_md.get("hindari_branches") if isinstance(marriage_md, dict) else None
    cocok_rel_md = marriage_md.get("cocok_relationships") if isinstance(marriage_md, dict) else None
    hindari_rel_md = marriage_md.get("hindari_relationships") if isinstance(marriage_md, dict) else None
    # Hanzi → Indonesian display label. Foto-categorized values come from MD.
    # `cocok`/`hindari` are generic placeholders untuk subject yang foto-nya tidak categorize.
    REL_HZ_TO_ID = {"三合": "Tiga Harmoni", "六合": "Pasangan", "六沖": "Bentrok",
                     "六害": "Saling Lukai", "三刑": "Hukuman", "破": "Pecah", "大吉": "Sangat Cocok", "吉凶相半": "Cukup Cocok", "次吉": "Cocok Umum",
                     "cocok": "Cocok", "hindari": "Hindari"}
    marriage = None
    if cocok_md is not None or hindari_md is not None:
        def _wrap(branches, rel_map_md, is_cocok):
            rel_map_md = rel_map_md or {}
            # Default: generic placeholder (no fake Hanzi). MD override jika foto group.
            default_rel = "cocok" if is_cocok else "hindari"
            out = []
            for b in (branches or []):
                if b in BRANCHES:
                    rel_hz = rel_map_md.get(b) or default_rel
                    out.append({
                        "branch_hz": b,
                        "id": BRANCHES[b]["shio_id"],
                        "relationship_hz": rel_hz,
                        "relationship_id": REL_HZ_TO_ID.get(rel_hz),
                        "reason_id": None,
                    })
            return out
        # self_branch_index points to the shio center. Render uses subject.shio.branch_hz
        # directly (computed later), so this index is informational only.
        # Derive from MD shio_hz (FULL-MD) or fallback to year_branch (definitional lookup).
        _SHIO_HZ_BRANCH_LOOKUP = {"鼠":"子","牛":"丑","虎":"寅","兔":"卯","龍":"辰","蛇":"巳",
                                    "馬":"午","羊":"未","猴":"申","雞":"酉","狗":"戌","豬":"亥"}
        _shio_md = ocr.get("shio_hz")
        if _shio_md and _shio_md in _SHIO_HZ_BRANCH_LOOKUP:
            self_shio_branch = _SHIO_HZ_BRANCH_LOOKUP[_shio_md]
        else:
            self_shio_branch = pillars["year"]["branch_hz"]  # fallback (definitional)
        self_idx = BRANCH_ORDER.index(self_shio_branch) if self_shio_branch in BRANCH_ORDER else None
        marriage = {
            "self_branch_index": self_idx,
            "cocok": _wrap(cocok_md, cocok_rel_md, True),
            "hindari": _wrap(hindari_md, hindari_rel_md, False),
        }

    # ---- Yang Zhai (Zone 9: MD pull, Ba Zhai sexagenary digit-sum formula REMOVED) ----
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
        }
        # Pull zones data from foto (yang_zhai_zones_foto) if MD provides — foto-authoritative
        yz_zones_foto = ocr.get("yang_zhai_zones_foto") or {}
        if yz_zones_foto:
            yang_zhai["zones"] = yz_zones_foto

    # ---- Zi Wei (Zone 10: MD pull, py-iztro engine REMOVED) ----
    zw_in = ocr.get("zi_wei")
    zw_out = None
    if isinstance(zw_in, dict) and zw_in:
        ming = zw_in.get("ming_gong_branch_hz")
        shen = zw_in.get("shen_gong_branch_hz")
        sj = zw_in.get("shi_jun_hz")
        branch_id_map = {b: BRANCHES[b]["shio_id"] for b in BRANCHES}
        zw_out = {
            "ming_zhu_hz": zw_in.get("ming_zhu_hz"),
            "shen_zhu_hz": zw_in.get("shen_zhu_hz"),
            "ming_gong_hz": ming,
            "shen_gong_hz": shen,
            "wu_xing_ju_hz": zw_in.get("wu_xing_ju_hz"),
            "shi_jun_hz": sj,
            "palaces": zw_in.get("palaces"),
            "ming_gong_id": f"Istana Hidup · {branch_id_map.get(ming)}" if ming in branch_id_map else None,
            "shen_gong_id": f"Istana Tubuh · {branch_id_map.get(shen)}" if shen in branch_id_map else None,
            "shi_jun_id":   f"Penguasa Waktu · {branch_id_map.get(sj)}" if sj in branch_id_map else None,
            "ming_zhu_id":  "Penguasa Hidup" if zw_in.get("ming_zhu_hz") else None,
            "shen_zhu_id":  "Penguasa Tubuh" if zw_in.get("shen_zhu_hz") else None,
        }
        wxj_map = {"水二局":"Aliran Air Dua","木三局":"Aliran Kayu Tiga","金四局":"Aliran Logam Empat","土五局":"Aliran Tanah Lima","火六局":"Aliran Api Enam"}
        wxj = zw_out["wu_xing_ju_hz"]
        zw_out["wu_xing_ju_id"] = wxj_map.get(wxj, wxj) if wxj else None

    # ---- Shen Sha (Zone 11: MD pull, 8-formula auto-compute REMOVED) ----
    shen_sha_list = ocr.get("shen_sha_list")  # list of {"hanzi":..., "pillar":...} or None

    # ---- Identity enrichment (preserved: lunar display via sxtwl) ----
    weekday_id = _WEEKDAY_ID.get(bdt.weekday() if bdt.weekday() != 6 else 0) if False else None
    # date.weekday(): Mon=0..Sun=6 ; map to dict (0=Sun..6=Sat) used by _WEEKDAY_ID
    # Use sxtwl for getWeek() when available (Sunday=0); fallback to Python weekday() conversion.
    period_id = _indo_period(h)
    # Hour branch: pull dari MD pillars.hour.branch_hz (foto-source). Fallback hitung
    # dari hour number HANYA kalau MD null. Edge case 子時 23-1 bisa beda konvensi
    # (foto: konvensi NCC vs engine: 24-slot lookup).
    hour_branch = (pillars.get("hour") or {}).get("branch_hz") or _hour_branch_hz(h)
    period_label = f"{period_id} · {hour_branch}時"

    lunar_year_pillar_hz = None
    lunar_pinyin = None
    lunar_date_text_new = None
    lunar_republic_text = None
    try:
        import sxtwl as _sx
        _d = _sx.fromSolar(y, mo, d)
        lunar_y = _d.getLunarYear()
        lunar_m = _d.getLunarMonth()
        lunar_d = _d.getLunarDay()
        weekday_id = _WEEKDAY_ID[_d.getWeek()]
        if pillars["year"]["stem_hz"] and pillars["year"]["branch_hz"]:
            lunar_year_pillar_hz = pillars["year"]["stem_hz"] + pillars["year"]["branch_hz"]
            lunar_pinyin = _lunar_pinyin_pair(pillars["year"]["stem_hz"], pillars["year"]["branch_hz"])
            lunar_date_text_new = (
                f"tanggal {lunar_d} bulan {lunar_m} tahun {lunar_year_pillar_hz} "
                f"({lunar_pinyin} · {lunar_y})"
            )
        else:
            lunar_date_text_new = f"tanggal {lunar_d} bulan {lunar_m} ({lunar_y})"
        roc_year = lunar_y - 1911
        lunar_republic_text = f"民國 {roc_year} 年 {lunar_m} 月 {lunar_d} 日"
    except Exception as e:
        print(f"[BUILD][WARN] lunar conversion skipped: {e}")
        # Fallback weekday from Python date
        py_wd = bdt.weekday()  # Mon=0..Sun=6
        weekday_id = _WEEKDAY_ID[(py_wd + 1) % 7]  # convert to Sun=0..Sat=6

    # Shio block: FULL-MD strict — ONLY from MD `shio_hz` (foto eksplisit).
    # No fallback to year_branch lookup. If MD missing → shio = None (PDF shows "—").
    SHIO_HZ_TO_BRANCH = {"鼠":"子","牛":"丑","虎":"寅","兔":"卯","龍":"辰","蛇":"巳",
                          "馬":"午","羊":"未","猴":"申","雞":"酉","狗":"戌","豬":"亥"}
    shio_md_hz = ocr.get("shio_hz")
    if shio_md_hz and shio_md_hz in SHIO_HZ_TO_BRANCH:
        shio_branch = SHIO_HZ_TO_BRANCH[shio_md_hz]
        shio = _shio_block(shio_branch) if shio_branch in BRANCHES else None
    else:
        shio = None  # FULL-MD strict: no derivation

    # ---- Final assembly ----
    out = {
        "subject_id": subject_id,
        "_built_by": "build_from_ocr.py V4.5 FULL-MD",
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
            "lunar_year_pillar_hz": lunar_year_pillar_hz,
            "lunar_republic_text": lunar_republic_text,
            "age_at_report": age_at_report,
        },
        "shio": shio,
        "ti_xiang": ocr.get("ti_xiang"),  # 5-element seasonal status (foto-source)
        "day_master": day_master,
        "pillars": pillars,
        "wuxing": wx,
        "yong_shen": yong_block,
        "ji_shen": ji_block,
        "format": fmt_block,
        "da_yun": da_yun,
        "marriage": marriage,
        "yang_zhai": yang_zhai,
        "zi_wei": zw_out,
        "shen_sha_list": shen_sha_list,
        "kesimpulan_narrative": ocr.get("kesimpulan_narrative"),
        # NEW V4.5 passthrough fields
        "dm_pos_score": ocr.get("dm_pos_score"),
        "dm_neg_score": ocr.get("dm_neg_score"),
        "xiantian_per_stem": ocr.get("xiantian_per_stem"),
        "wangdu_per_stem": ocr.get("wangdu_per_stem"),
        "wangdu_total": ocr.get("wangdu_total"),
        "nayin_per_pillar": ocr.get("nayin_per_pillar"),
        "canggan_per_pillar": ocr.get("canggan_per_pillar"),
        # V7 Page 04 enrichment passthrough
        "canggan_shi_shen": ocr.get("canggan_shi_shen"),
        "chang_sheng_per_pilar": ocr.get("chang_sheng_per_pilar"),
        "kong_wang": ocr.get("kong_wang"),
        "ming_gong_bazi": ocr.get("ming_gong_bazi"),
        "bone_weight": ocr.get("bone_weight"),
        # V7 Phase 2A — 流年 prediksi tahunan
        "liu_nian_predictions": ocr.get("liu_nian_predictions"),
        # V7 Phase 3 — 宿命 quote-box (Zi Wei overview)
        "ziwei_su_ming": ocr.get("ziwei_su_ming"),
        # V7 Phase 3B — Full minor stars per palace (foto-source)
        "ziwei_stars": ocr.get("ziwei_stars"),
        # V7 Phase 4 — Full industri list dari foto 事業
        "shiye_favorable_full": ocr.get("shiye_favorable_full"),
        "shiye_supportive_full": ocr.get("shiye_supportive_full"),
        # V7 Phase 4B — 適業 1-line dari 先天論命
        "shiye_short": ocr.get("shiye_short"),
        # V7 Phase 5 — Shen Sha tafsir per bintang (foto-direct)
        "shen_sha_detail": ocr.get("shen_sha_detail"),
        # V7 Phase 7 — Marriage tafsir 宜/忌 prose (foto-direct)
        "marriage_cocok_tafsir": ocr.get("marriage_cocok_tafsir"),
        "marriage_hindari_tafsir": ocr.get("marriage_hindari_tafsir"),
        # V7 Phase 8 — Lampiran Klasik (古書云 + 凶年; bone_weight already above)
        "gushu_quotes": ocr.get("gushu_quotes"),
        "xiongnian_list": ocr.get("xiongnian_list"),
        # v7.4 — 先天論命 supplementary pages
        "xing_qing_poem_hz": ocr.get("xing_qing_poem_hz"),
        "xing_qing_poem_id": ocr.get("xing_qing_poem_id"),
        "xing_qing_prose_id": ocr.get("xing_qing_prose_id"),
        "fulu_body_id": ocr.get("fulu_body_id"),
        "mingyun_body_id": ocr.get("mingyun_body_id"),
        "qinshu_tou_main_id": ocr.get("qinshu_tou_main_id"),
        "qinshu_tou_youyue_id": ocr.get("qinshu_tou_youyue_id"),
        "qinshu_zhong_main_id": ocr.get("qinshu_zhong_main_id"),
        "qinshu_zhong_youyue_id": ocr.get("qinshu_zhong_youyue_id"),
        "qinshu_mo_main_id": ocr.get("qinshu_mo_main_id"),
        "qinshu_mo_youyue_id": ocr.get("qinshu_mo_youyue_id"),
        # V7.1 Kesehatan (page 16) — 疾厄 ZiWei narrative
        "jie_e_palace_hz": ocr.get("jie_e_palace_hz"),
        "jie_e_palace_id": ocr.get("jie_e_palace_id"),
        "jie_e_organ_focus_id": ocr.get("jie_e_organ_focus_id"),
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
