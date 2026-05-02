# -*- coding: utf-8 -*-
"""V5 — Verify Zi Wei core (命宮 branch, 身宮, 命主, 身主, 五行局) via py-iztro vs Yiteng GT.

Note: py-iztro uses simplified Chinese star names; Yiteng uses traditional. Need mapping.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from py_iztro import Astro

# GT from extracts: (ming_branch, shen_branch, soul_traditional, body_traditional, ju)
ZIWEI_GT = {
    "Michele":   ("子", "寅", "貪狼", "天機", "火六局"),
    "Tommy":     ("午", "辰", "破軍", "火星", "木三局"),
    "HuLiLi":    ("辰", "辰", "廉貞", "文昌", "木三局"),
    "Leana":     ("酉", "丑", "文曲", "文昌", "木三局"),
    "Bryant":    ("寅", "寅", "祿存", "天相", "木三局"),
    "LinRuYi":   ("丑", "亥", "巨門", "天機", "火六局"),
}

# Simplified→Traditional mapping for stars (py-iztro returns simplified)
S2T = {
    "贪狼":"貪狼", "巨门":"巨門", "禄存":"祿存", "破军":"破軍",
    "廉贞":"廉貞", "天机":"天機", "天梁":"天梁", "天相":"天相",
    "天同":"天同", "文昌":"文昌", "文曲":"文曲", "火星":"火星",
    "紫微":"紫微", "天府":"天府", "太阳":"太陽", "太阴":"太陰",
    "武曲":"武曲", "七杀":"七殺",
}

SUBJECTS_DT = {
    "Michele":    ("1995-07-22", 14, "female"),
    "Tommy":      ("1960-05-08", 22, "male"),
    "HuLiLi":     ("1964-05-05",  0, "female"),
    "LinWenJin":  ("1998-02-27",  9, "male"),
    "LinPinAi":   ("1989-05-13",  7, "female"),
    "Leana":      ("1958-06-13", 16, "female"),
    "Mike":       ("2018-09-13", 12, "male"),
    "Bryant":     ("1991-09-04", 12, "male"),
    "LinXiuLing": ("1990-06-11", 23, "female"),
    "LinRuYi":    ("1995-05-30", 10, "female"),
}

def hour_to_idx(h):
    """Convert 0-23 hour to py-iztro time index 0-12 (子=0, 丑=1, ..., 亥=11; 早子=0 / 晚子=12 might exist)"""
    # py-iztro index: 0=23:00-01:00 = 子. (00 falls in 0)
    # 0-1 → 0; 1-3 → 1; ...; 23 → 0
    if h == 23 or h == 0: return 0
    return (h + 1) // 2

print("="*100)
print("V5 — Zi Wei core verification (py-iztro)")
print("="*100)
print(f"{'Subject':<12}{'命宮':<10}{'GT命宮':<10}{'身宮':<10}{'GT身宮':<10}{'命主':<10}{'GT命主':<10}{'身主':<10}{'GT身主':<10}{'局':<10}{'GT局':<10}{'Match'}")
print("-"*120)

astro = Astro()
ok_count = 0; total = 0
for name, (date, hour, gender) in SUBJECTS_DT.items():
    if name not in ZIWEI_GT:
        continue
    gt_mb, gt_sb, gt_soul, gt_body, gt_ju = ZIWEI_GT[name]
    h_idx = hour_to_idx(hour)
    chart = astro.by_solar(date, h_idx, gender, True)
    mb = chart.earthly_branch_of_soul_palace
    sb = chart.earthly_branch_of_body_palace
    soul_simp = chart.soul
    body_simp = chart.body
    soul = S2T.get(soul_simp, soul_simp)
    body = S2T.get(body_simp, body_simp)
    ju_simp = chart.five_elements_class
    # convert simp ju to traditional
    ju = ju_simp.replace("木","木").replace("火","火").replace("土","土").replace("金","金").replace("水","水")

    mb_ok = mb == gt_mb
    sb_ok = sb == gt_sb
    soul_ok = soul == gt_soul
    body_ok = body == gt_body
    ju_ok = ju == gt_ju
    all_ok = mb_ok and sb_ok and soul_ok and body_ok and ju_ok
    if all_ok: ok_count += 1
    total += 1
    flag = "OK" if all_ok else "DIFF"
    print(f"{name:<12}{mb:<10}{gt_mb:<10}{sb:<10}{gt_sb:<10}{soul:<10}{gt_soul:<10}{body:<10}{gt_body:<10}{ju:<10}{gt_ju:<10}{flag}")

print("-"*120)
print(f"\nZi Wei core: {ok_count}/{total} subjects 100% match")
