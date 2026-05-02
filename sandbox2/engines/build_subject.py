"""Sandbox1 build_subject - Convert OCR data + manual identity inputs into full subject.json.

Maps deterministic fields (pillars, da_yun stems/branches, gua) and computes derived
(ten gods, element classes, shio labels, wuxing percentages) from a small core set.

For narrative tafsir text (footer captions, mantra meaning, spotlight bullets), leaves
fields BLANK if not overridden - render engine will fall back to Michele's template text.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engines"))

from lookups import STEMS, BRANCHES, BRANCH_ORDER, TRIGRAMS

DATA_DIR = ROOT / "data" / "subjects"

# Ten Gods table — 10 stems x 10 stems
# Index: [day_master_stem][other_stem] = ten_god label
def _ten_god_pair(dm_stem_hz: str, other_stem_hz: str) -> tuple[str, str]:
    """Return (ten_god_hz, ten_god_id) for given day master vs other stem."""
    dm_el = STEMS[dm_stem_hz]["el_hz"]
    dm_pol = STEMS[dm_stem_hz]["polarity_id"]
    o_el = STEMS[other_stem_hz]["el_hz"]
    o_pol = STEMS[other_stem_hz]["polarity_id"]
    same_pol = dm_pol == o_pol

    # 5-element relationships
    sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # produces
    ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}        # controls

    if o_el == dm_el:
        # same element
        if same_pol:
            return ("比肩", "Pundak Sama")
        return ("劫財", "Saudara Sebanding")
    if sheng.get(dm_el) == o_el:
        # DM produces other (output)
        if same_pol:
            return ("食神", "Pencipta")
        return ("傷官", "Kritikus Tajam")
    if ke.get(dm_el) == o_el:
        # DM controls other (wealth)
        if same_pol:
            return ("偏財", "Rezeki Bisnis")
        return ("正財", "Rezeki Tetap")
    if ke.get(o_el) == dm_el:
        # other controls DM (officer)
        if same_pol:
            return ("七殺", "Pemurnian")
        return ("正官", "Otoritas")
    if sheng.get(o_el) == dm_el:
        # other produces DM (resource)
        if same_pol:
            return ("偏印", "Mentor")
        return ("正印", "Pelajaran")
    return ("?", "?")


def _element_class(stem_hz: str) -> str:
    el_hz = STEMS[stem_hz]["el_hz"]
    return {"木": "el-mu", "水": "el-shui", "土": "el-tu", "火": "el-huo", "金": "el-jin"}[el_hz]


def build_da_yun(start_age: int, direction: str, month_pillar: dict, day_master_stem: str) -> list:
    """Generate 10 da yun cycles. direction='forward' or 'backward'."""
    stems = list(STEMS.keys())  # 甲乙丙丁戊己庚辛壬癸
    branches = BRANCH_ORDER     # 子丑寅卯辰巳午未申酉戌亥

    y_stem_idx = stems.index(month_pillar["stem_hz"])
    y_branch_idx = branches.index(month_pillar["branch_hz"])

    cycles = []
    for i in range(10):
        if direction == "forward":
            s_idx = (y_stem_idx + 1 + i) % 10
            b_idx = (y_branch_idx + 1 + i) % 12
        else:
            s_idx = (y_stem_idx - 1 - i) % 10
            b_idx = (y_branch_idx - 1 - i) % 12
        stem = stems[s_idx]
        branch = branches[b_idx]
        ten_god_hz, ten_god_id = _ten_god_pair(day_master_stem, stem)
        cycles.append({
            "n": i + 1,
            "age_start": start_age + i * 10,
            "age_end": start_age + i * 10 + 9,
            "stem_hz": stem,
            "branch_hz": branch,
            "ten_god_hz": ten_god_hz,
            "ten_god_id": ten_god_id,
            "element_class": _element_class(stem),
        })
    return cycles


def compute_wuxing_percentages(values: dict) -> dict:
    """Add percent values to a wuxing dict containing raw element values."""
    total = sum(v for v in values.values())
    out = {}
    label_map = {"jin": "Logam", "shui": "Air", "mu": "Kayu", "huo": "Api", "tu": "Tanah"}
    for el in ["jin", "shui", "mu", "huo", "tu"]:
        v = values.get(el, 0.0)
        pct = round(v / total * 100, 1) if total > 0 else 0.0
        out[el] = {"value": v, "percent": pct, "label_id": label_map[el]}
    out["total"] = round(total, 1)
    return out


def gregorian_to_lunar_republic(iso: str, lunar_md: tuple = None) -> str:
    y = int(iso.split("-")[0])
    roc = y - 1911
    if lunar_md:
        ly, lm, ld = lunar_md
        return f"民國 {roc} 年 {lm} 月 {ld} 日"
    return f"民國 {roc} 年"


def shio_block(branch_hz: str) -> dict:
    b = BRANCHES[branch_hz]
    return {
        "branch_hz": branch_hz,
        "branch_pinyin": b["pinyin"],
        "id": b["shio_id"],
        "id_upper": b["shio_id"].upper(),
        "svg_red": f"{b['shio_id']}-Merah.svg",
        "svg_black": f"{b['shio_id']}-Hitam.svg",
    }


def stem_to_dm_block(stem_hz: str, label_id: str = None, strength_id: str = "Kuat") -> dict:
    s = STEMS[stem_hz]
    return {
        "stem_hz": stem_hz,
        "stem_element_hz": s["el_hz"],
        "stem_element_id": s["el_id"],
        "polarity_id": s["polarity_id"],
        "label_id": label_id or f"{s['el_id']} Pohon Besar",  # generic fallback
        "label_long_id": label_id or s["el_id"],
        "pinyin": f"{s['pinyin']} {{el_pinyin}}",
        "strength_id": strength_id,
        "strength_hz": "旺" if strength_id == "Kuat" else "弱",
    }


def build_subject(core: dict) -> dict:
    """Build full subject.json from a small core spec.

    core: {
        subject_id, name_id, name_hanzi, gender_id, birth_date, birth_time,
        birth_day_name, birth_period_id, age_at_report,
        pillars: {year, month, day(=DM), hour},
        wuxing: {jin, shui, mu, huo, tu},  // raw values
        yong_shen_hz, ji_shen_hz,
        format_hz, format_pinyin, format_label_id,
        mantra_hz, mantra_pinyin,
        da_yun_start_age, da_yun_direction,
        marriage_cocok_branches, marriage_hindari_branches,  // [hz, ...]
        yang_zhai_gua_hz, yang_zhai_zones,
        zi_wei: {ming_zhu_hz, shen_zhu_hz, ming_gong_hz, shen_gong_hz, wu_xing_ju_hz, shi_jun_hz}
    }
    """
    pillars = core["pillars"]
    dm_stem = pillars["day"]["stem_hz"]
    dm_block = stem_to_dm_block(dm_stem, core.get("dm_label_id"), core.get("dm_strength", "Kuat"))

    return {
        "subject_id": core["subject_id"],
        "identity": {
            "name_id": core["name_id"],
            "name_hanzi": core["name_hanzi"],
            "gender_id": core["gender_id"],
            "birth_date": core["birth_date"],
            "birth_time": core["birth_time"],
            "birth_day_name": core.get("birth_day_name", ""),
            "birth_period_id": core.get("birth_period_id", "siang"),
            "lunar_date_text": core.get("lunar_date_text", ""),
            "lunar_republic_text": core.get("lunar_republic_text",
                                             gregorian_to_lunar_republic(core["birth_date"])),
            "age_at_report": core["age_at_report"],
        },
        "shio": shio_block(pillars["year"]["branch_hz"]),
        "day_master": dm_block,
        "pillars": pillars,
        "wuxing": compute_wuxing_percentages(core["wuxing"]),
        "yong_shen": core.get("yong_shen", {}),
        "ji_shen": core.get("ji_shen", {}),
        "format": core.get("format", {}),
        "mantra": core.get("mantra", {}),
        "da_yun": _build_da_yun_block(core),
        "marriage": core.get("marriage", {}),
        "yang_zhai": core.get("yang_zhai", {}),
        "zi_wei": core.get("zi_wei", {}),
    }


def _build_da_yun_block(core: dict) -> dict:
    cycles = build_da_yun(
        core["da_yun_start_age"],
        core.get("da_yun_direction", "forward"),
        core["pillars"]["month"],
        core["pillars"]["day"]["stem_hz"]
    )
    cur_idx = core.get("da_yun_current_index", 0)
    if 0 <= cur_idx < len(cycles):
        cycles[cur_idx]["is_current"] = True

    start = core["da_yun_start_age"]
    return {
        "start_age": start,
        "direction_id": core.get("da_yun_direction", "forward"),
        "current_index": cur_idx,
        "axis_marks": [start + i * 10 for i in range(11)],
        "cycles": cycles,
    }


if __name__ == "__main__":
    print("This is a library module. Import and use build_subject(core_dict).")
