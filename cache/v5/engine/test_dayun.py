# -*- coding: utf-8 -*-
"""V5 — Verify 大運 干支 sequence vs Yiteng GT.
Most critical: even if start-age differs by 1 year, the 10-cycle ganzhi sequence must be 100% correct."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from lunar_python import Solar

# 大運 GT from extracts (10 cycles, ages and ganzhi)
DAYUN_GT = {
    "Tommy":     [(10,"壬午"),(20,"癸未"),(30,"甲申"),(40,"乙酉"),(50,"丙戌"),(60,"丁亥"),(70,"戊子"),(80,"己丑"),(90,"庚寅"),(100,"辛卯")],
    "HuLiLi":    [(11,"丁卯"),(21,"丙寅"),(31,"乙丑"),(41,"甲子"),(51,"癸亥"),(61,"壬戌"),(71,"辛酉"),(81,"庚申"),(91,"己未"),(101,"戊午")],
    "LinWenJin": [(3,"乙卯"),(13,"丙辰"),(23,"丁巳"),(33,"戊午"),(43,"己未"),(53,"庚申"),(63,"辛酉"),(73,"壬戌"),(83,"癸亥"),(93,"甲子")],
    "LinPinAi":  [(9,"庚午"),(19,"辛未"),(29,"壬申"),(39,"癸酉"),(49,"甲戌"),(59,"乙亥"),(69,"丙子"),(79,"丁丑"),(89,"戊寅"),(99,"己卯")],
    "Leana":     [(3,"丁巳"),(13,"丙辰"),(23,"乙卯"),(33,"甲寅"),(43,"癸丑"),(53,"壬子"),(63,"辛亥"),(73,"庚戌"),(83,"己酉"),(93,"戊申")],
    "Mike":      [(10,"壬戌"),(20,"癸亥"),(30,"甲子"),(40,"乙丑"),(50,"丙寅"),(60,"丁卯"),(70,"戊辰"),(80,"己巳"),(90,"庚午"),(100,"辛未")],
    "Bryant":    [(10,"乙未"),(20,"甲午"),(30,"癸巳"),(40,"壬辰"),(50,"辛卯"),(60,"庚寅"),(70,"己丑"),(80,"戊子"),(90,"丁亥"),(100,"丙戌")],
    "LinXiuLing":[(3,"辛巳"),(13,"庚辰"),(23,"己卯"),(33,"戊寅"),(43,"丁丑"),(53,"丙子"),(63,"乙亥"),(73,"甲戌"),(83,"癸酉"),(93,"壬申")],
    "LinRuYi":   [(3,"壬午"),(13,"癸未"),(23,"甲申"),(33,"乙酉"),(43,"丙戌"),(53,"丁亥"),(63,"戊子"),(73,"己丑"),(83,"庚寅"),(93,"辛卯")],
}

SUBJECTS = [
    ("Tommy",     "M", 1960,  5,  8, 22, 15),
    ("HuLiLi",    "F", 1964,  5,  5,  0,  5),
    ("LinWenJin", "M", 1998,  2, 27,  9, 43),
    ("LinPinAi",  "F", 1989,  5, 13,  7, 45),
    ("Leana",     "F", 1958,  6, 13, 16,  0),
    ("Mike",      "M", 2018,  9, 13, 12, 23),
    ("Bryant",    "M", 1991,  9,  4, 12, 51),
    ("LinXiuLing","F", 1990,  6, 11, 23, 40),
    ("LinRuYi",   "F", 1995,  5, 30, 10, 35),
]

def compute_dayun(y, mo, d, h, mi, sex):
    s = Solar.fromYmdHms(y, mo, d, h, mi, 0)
    b = s.getLunar().getEightChar()
    yun = b.getYun(1 if sex == "M" else 0)
    dy = yun.getDaYun(11)
    # dy[0] is 童年 (pre-DaYun), skip if empty ganzhi
    cycles = []
    for d in dy:
        gz = d.getGanZhi()
        if gz:
            cycles.append((d.getStartAge(), gz))
    return cycles[:10]

print("="*100)
print("V5 — 大運 ganzhi sequence verification")
print("="*100)

total_match = 0; total_check = 0; subj_match = 0
for name, sex, y, mo, d, h, mi in SUBJECTS:
    if name not in DAYUN_GT: continue
    computed = compute_dayun(y, mo, d, h, mi, sex)
    gt = DAYUN_GT[name]
    # compare ganzhi sequence (ages may differ by 1 due to rounding)
    matches = sum(1 for c, g in zip(computed, gt) if c[1] == g[1])
    total_match += matches
    total_check += len(gt)
    pct = 100*matches/len(gt)
    match_full = matches == len(gt)
    if match_full: subj_match += 1
    flag = "OK" if match_full else f"{matches}/{len(gt)}"
    # show first 3 cycles
    cm = " ".join(f"{a}{g}" for a,g in computed[:5])
    gm = " ".join(f"{a}{g}" for a,g in gt[:5])
    print(f"\n{name} [{flag}]")
    print(f"  computed: {cm} ...")
    print(f"  GT:       {gm} ...")
    if not match_full:
        for i,(c,g) in enumerate(zip(computed, gt)):
            if c[1] != g[1]:
                print(f"  DIFF cycle {i}: computed={c} vs gt={g}")

print("="*100)
print(f"Subject-level: {subj_match}/{len(DAYUN_GT)} subjects 100% match")
print(f"Cycle-level:   {total_match}/{total_check} cycles match ({100*total_match/total_check:.1f}%)")
