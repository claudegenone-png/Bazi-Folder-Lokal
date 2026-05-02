# -*- coding: utf-8 -*-
"""V5 — Verify 四化 (sihua) placement vs Yiteng GT.
四化 by 年干: 化祿/化權/化科/化忌 each lands on a specific main star."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from py_iztro import Astro

S2T = {
    "贪狼":"貪狼", "巨门":"巨門", "禄存":"祿存", "破军":"破軍",
    "廉贞":"廉貞", "天机":"天機", "天梁":"天梁", "天相":"天相",
    "天同":"天同", "文昌":"文昌", "文曲":"文曲", "火星":"火星",
    "紫微":"紫微", "天府":"天府", "太阳":"太陽", "太阴":"太陰",
    "武曲":"武曲", "七杀":"七殺", "陀罗":"陀羅", "左辅":"左輔", "右弼":"右弼",
}

# (lu_star, quan_star, ke_star, ji_star) per Yiteng
SIHUA_GT = {
    "Michele":   ("天機","天梁","紫微","太陰"),
    "Tommy":     ("太陽","武曲","太陰","天同"),
    "HuLiLi":    ("廉貞","破軍","武曲","太陽"),
    "Bryant":    ("巨門","太陽","文曲","文昌"),
    "LinRuYi":   ("天機","天梁","紫微","太陰"),
    "Leana":     ("貪狼","太陰","右弼","天機"),
}

SUBJECTS_DT = {
    "Michele":    ("1995-07-22", 14, "female"),
    "Tommy":      ("1960-05-08", 22, "male"),
    "HuLiLi":     ("1964-05-05",  0, "female"),
    "Leana":      ("1958-06-13", 16, "female"),
    "Bryant":     ("1991-09-04", 12, "male"),
    "LinRuYi":    ("1995-05-30", 10, "female"),
}

def hour_to_idx(h):
    if h == 23 or h == 0: return 0
    return (h + 1) // 2

# Mutagen tokens used by py-iztro
MUTAGEN = {"禄":"祿", "权":"權", "科":"科", "忌":"忌"}

print("="*100)
print("V5 — 四化 verification")
print("="*100)
print(f"{'Subject':<12}{'祿':<14}{'權':<14}{'科':<14}{'忌':<14}{'Match'}")
print("-"*80)

astro = Astro()
ok = 0
for name, (date, hour, gender) in SUBJECTS_DT.items():
    if name not in SIHUA_GT: continue
    chart = astro.by_solar(date, hour_to_idx(hour), gender, True)
    found = {"祿":None, "權":None, "科":None, "忌":None}
    for p in chart.palaces:
        for star in (p.major_stars or []) + (p.minor_stars or []):
            if star.mutagen:
                key = MUTAGEN.get(star.mutagen, star.mutagen)
                if key in found:
                    found[key] = S2T.get(star.name, star.name)
    gt = SIHUA_GT[name]
    pred = (found["祿"], found["權"], found["科"], found["忌"])
    match = pred == gt
    if match: ok += 1
    pred_str = [f"{a}/{b}" for a, b in zip(pred, gt)]
    flag = "OK" if match else "DIFF"
    print(f"{name:<12}{pred_str[0]:<14}{pred_str[1]:<14}{pred_str[2]:<14}{pred_str[3]:<14}{flag}")
print(f"\n四化: {ok}/{len(SIHUA_GT)} subjects 100% match")
