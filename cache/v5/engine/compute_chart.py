# -*- coding: utf-8 -*-
"""V5 Unified Chart Producer — input nama+tanggal+jam+gender → chart.json.

Output JSON contains all fields needed for PDF report:
- BaZi: 4 pillars 干支, 藏干, 十神, 命宮干支, 大運 cycles, 五行 旺相死囚休, 旺度 score, 體檢, 卦格, 喜用神
- Zi Wei: 12 palace + 14 main star + brightness + 副星 + 神煞 + 大限 + 流年 + 命主/身主/五行局/四化

Usage:
    python compute_chart.py "Nama" "1995-07-22" "14:00" "F"
    python compute_chart.py --json '{"name":"...","date":"...","time":"...","sex":"F"}'
"""
from __future__ import annotations
import sys, json, argparse
sys.stdout.reconfigure(encoding="utf-8")

from lunar_python import Solar
from py_iztro import Astro

import bazi_minggong as bmg
import scoring as sc

# Simplified→Traditional star name mapping
S2T = {
    "贪狼":"貪狼","巨门":"巨門","禄存":"祿存","破军":"破軍",
    "廉贞":"廉貞","天机":"天機","天梁":"天梁","天相":"天相",
    "天同":"天同","文昌":"文昌","文曲":"文曲","火星":"火星",
    "紫微":"紫微","天府":"天府","太阳":"太陽","太阴":"太陰",
    "武曲":"武曲","七杀":"七殺","陀罗":"陀羅","左辅":"左輔",
    "右弼":"右弼","擎羊":"擎羊","铃星":"鈴星","地空":"地空",
    "地劫":"地劫","天魁":"天魁","天钺":"天鉞","天马":"天馬",
    "禄":"祿","权":"權","科":"科","忌":"忌",
}
# Palace name simp→trad
PNAME = {
    "命宫":"命宮","兄弟":"兄弟","夫妻":"夫妻","子女":"子女",
    "财帛":"財帛","疾厄":"疾厄","迁移":"遷移","仆役":"僕役",
    "官禄":"官祿","田宅":"田宅","福德":"福德","父母":"父母",
}
# Mutagen (sihua) simp→trad
MUTAGEN = {"禄":"祿","权":"權","科":"科","忌":"忌"}

def t(s):
    """Translate simp→trad, fallback to original."""
    return S2T.get(s, s)

def hour_to_idx(h, m=0):
    """py-iztro hour index 0-12. Standard 子時 = 23-01."""
    if h == 23 or h == 0: return 0
    return (h + 1) // 2

def compute(name, year, month, day, hour, minute, sex):
    """Compute full chart. sex: 'M' or 'F'."""
    # ─── BaZi side via lunar-python ───
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    bazi = lunar.getEightChar()
    pillars = (bazi.getYear(), bazi.getMonth(), bazi.getDay(), bazi.getTime())
    day_master = pillars[2][0]
    year_stem = pillars[0][0]

    # 命宮 (custom 子平 formula)
    ming_gong = bmg.compute_bazi_minggong(year, month, day, hour, minute)
    # 胎元: 月柱 + 1 stem and 月支 + 3 branch positions
    tai_yuan_stem = bmg.STEMS[(bmg.STEMS.index(pillars[1][0]) + 1) % 10]
    tai_yuan_branch = bmg.BRANCHES[(bmg.B_IDX[pillars[1][1]] + 3) % 12]
    tai_yuan = tai_yuan_stem + tai_yuan_branch

    # 大運 cycles
    yun = bazi.getYun(1 if sex == "M" else 0)
    qi_yun_offset = (yun.getStartYear(), yun.getStartMonth(), yun.getStartDay())
    da_yun_list = []
    for i, dy in enumerate(yun.getDaYun(11)):
        if dy.getGanZhi():
            da_yun_list.append({
                "cycle": i,
                "start_age": dy.getStartAge(),
                "start_year": dy.getStartYear(),
                "ganzhi": dy.getGanZhi(),
                "ten_god": sc.get_relation(dy.getGanZhi()[0], day_master),
            })

    # Pillar details (藏干 + 十神 per stem/hidden)
    pillar_detail = []
    for pos, gz in zip(["year","month","day","hour"], pillars):
        stem = gz[0]; branch = gz[1]
        hidden = bmg.B_IDX  # placeholder ref
        pd = {
            "position": pos,
            "ganzhi": gz,
            "stem": stem,
            "branch": branch,
            "stem_ten_god": "命主" if pos == "day" else sc.get_relation(stem, day_master),
            "hidden_stems": [
                {"stem": h, "ten_god": sc.get_relation(h, day_master)}
                for h in sc.HIDDEN_STEMS[branch]
            ],
        }
        pillar_detail.append(pd)

    # Numeric scoring
    plus, minus = sc.compute_wangdu(pillars, day_master)
    organs_raw = sc.compute_organ_scores(pillars)
    organs = [
        {"stem": s, "organ": sc.stem_organ(s), "score": organs_raw[s]}
        for s in sc.STEMS
    ]
    wuxing = sc.compute_wuxing_status(pillars[1][1], sc.STEM_ELEM[day_master])
    yongshen = sc.compute_yongshen(day_master, pillars[1][1])
    guage = sc.compute_guage(pillars, day_master, plus + minus)

    # ─── Zi Wei side via py-iztro ───
    astro = Astro()
    zw_chart = astro.by_solar(f"{year:04d}-{month:02d}-{day:02d}", hour_to_idx(hour, minute), "male" if sex == "M" else "female", True)

    palaces = []
    for p in zw_chart.palaces:
        palaces.append({
            "index": p.index,
            "name": PNAME.get(p.name, p.name),
            "ganzhi": (p.heavenly_stem or "") + (p.earthly_branch or ""),
            "stem": p.heavenly_stem,
            "branch": p.earthly_branch,
            "is_body": p.is_body_palace,
            "is_origin": p.is_original_palace,
            "major_stars": [
                {"name": t(s.name), "brightness": s.brightness or "", "mutagen": MUTAGEN.get(s.mutagen, "") if s.mutagen else ""}
                for s in (p.major_stars or [])
            ],
            "minor_stars": [
                {"name": t(s.name), "brightness": s.brightness or "", "mutagen": MUTAGEN.get(s.mutagen, "") if s.mutagen else ""}
                for s in (p.minor_stars or [])
            ],
            "adjective_stars": [t(s.name) for s in (p.adjective_stars or [])],
            "changsheng12": p.changsheng12,
            "boshi12": p.boshi12,
            "jiangqian12": p.jiangqian12,
            "suiqian12": p.suiqian12,
            "decadal": {
                "range": list(p.decadal.range) if p.decadal else None,
                "ganzhi": (p.decadal.heavenly_stem + p.decadal.earthly_branch) if p.decadal else None,
            },
            "ages": list(p.ages) if p.ages else [],
        })

    chart = {
        "input": {
            "name": name,
            "sex": sex,
            "solar_date": f"{year:04d}-{month:02d}-{day:02d}",
            "time": f"{hour:02d}:{minute:02d}",
        },
        "calendar": {
            "solar": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
            "lunar": zw_chart.lunar_date,
            "chinese_date": zw_chart.chinese_date,
            "weekday": solar.getWeekInChinese(),
            "zodiac": zw_chart.zodiac,
            "time_branch_label": zw_chart.time,
            "time_range": zw_chart.time_range,
        },
        "bazi": {
            "pillars": pillar_detail,
            "day_master": day_master,
            "ming_gong": ming_gong,
            "tai_yuan": tai_yuan,
            "wangdu": {"plus": plus, "minus": minus, "net": plus + minus},
            "wuxing_status": wuxing,
            "organs": organs,
            "yongshen": yongshen,
            "guage": guage,
            "da_yun": {
                "qi_yun_offset_y_m_d": list(qi_yun_offset),
                "qi_yun_age": qi_yun_offset[0],
                "direction": "順" if ((year_stem in "甲丙戊庚壬") == (sex == "M")) else "逆",
                "cycles": da_yun_list,
            },
        },
        "ziwei": {
            "ming_branch": zw_chart.earthly_branch_of_soul_palace,
            "shen_branch": zw_chart.earthly_branch_of_body_palace,
            "soul_star": t(zw_chart.soul),
            "body_star": t(zw_chart.body),
            "wuxing_ju": zw_chart.five_elements_class,
            "palaces": palaces,
        },
    }
    return chart


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="Subject name")
    ap.add_argument("date", help="Solar date YYYY-MM-DD")
    ap.add_argument("time", help="HH:MM")
    ap.add_argument("sex", choices=["M","F"], help="Gender M or F")
    ap.add_argument("--out", help="Output JSON file (default: stdout)")
    args = ap.parse_args()

    y, mo, d = map(int, args.date.split("-"))
    h, mi = map(int, args.time.split(":"))
    chart = compute(args.name, y, mo, d, h, mi, args.sex)

    out_str = json.dumps(chart, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"Wrote {args.out}")
    else:
        print(out_str)

if __name__ == "__main__":
    main()
