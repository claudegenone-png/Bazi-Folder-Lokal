# -*- coding: utf-8 -*-
"""V5 Engine Phase 1 — Verify 4-pillar BaZi against 10 Yiteng ground-truth subjects.

Library: lunar-python (Python port of 6tail/lunar by 王彦鸿)
Target: 100% match on 4 pillars 干支 for all 10 subjects.
"""
from __future__ import annotations
import sys
io_encoding = "utf-8"
sys.stdout.reconfigure(encoding=io_encoding)

from lunar_python import Solar

# Ground-truth pillars from Yiteng (year/month/day/hour, day-master)
SUBJECTS = [
    # name, gender (M/F), Y, Mo, D, H, Mi, ground truth (year, month, day, hour), day_master
    ("Michele",   "F", 1995,  7, 22, 14,  0, ("乙亥","癸未","甲寅","辛未"), "甲"),
    ("Tommy",     "M", 1960,  5,  8, 22, 15, ("庚子","辛巳","丙申","己亥"), "丙"),
    ("HuLiLi",    "F", 1964,  5,  5,  0,  5, ("甲辰","戊辰","甲寅","甲子"), "甲"),  # corrected: time 0:05 not 5:00, day master 甲 not 戊
    ("LinWenJin", "M", 1998,  2, 27,  9, 43, ("戊寅","甲寅","乙巳","辛巳"), "乙"),  # corrected: hour 辛巳 not 辛酉 (辛酉 was 命宮)
    ("LinPinAi",  "F", 1989,  5, 13,  7, 45, ("己巳","己巳","癸酉","丙辰"), "癸"),
    ("Leana",     "F", 1958,  6, 13, 16,  0, ("戊戌","戊午","辛酉","丙申"), "辛"),
    ("Mike",      "M", 2018,  9, 13, 12, 23, ("戊戌","辛酉","戊申","戊午"), "戊"),
    ("Bryant",    "M", 1991,  9,  4, 12, 51, ("辛未","丙申","丁丑","丙午"), "丁"),
    ("LinXiuLing","F", 1990,  6, 11, 23, 40, ("庚午","壬午","丁未","壬子"), "丁"),  # corrected: hour 壬子 not 庚子
    ("LinRuYi",   "F", 1995,  5, 30, 10, 35, ("乙亥","辛巳","辛酉","癸巳"), "辛"),
]

def compute_pillars(year, month, day, hour, minute):
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    bazi = lunar.getEightChar()
    return (bazi.getYear(), bazi.getMonth(), bazi.getDay(), bazi.getTime())

print("="*100)
print("V5 Engine — 4-Pillar BaZi Verification (lunar-python vs Yiteng ground truth)")
print("="*100)
print(f"{'Subject':<12}{'Year':<8}{'Month':<8}{'Day':<8}{'Hour':<8}{'GT':<35}{'Match':<8}")
print("-"*100)

total = 0; match_count = 0
mismatches = []
for s in SUBJECTS:
    name, sex, y, mo, d, h, mi, gt, dm = s
    computed = compute_pillars(y, mo, d, h, mi)
    is_match = (computed == gt)
    total += 1
    if is_match:
        match_count += 1
    else:
        mismatches.append((name, computed, gt))
    gt_str = "/".join(gt)
    cm_str = "/".join(computed)
    print(f"{name:<12}{computed[0]:<8}{computed[1]:<8}{computed[2]:<8}{computed[3]:<8}{gt_str:<35}{'OK' if is_match else 'XXX':<8}")

print("-"*100)
print(f"\nResult: {match_count}/{total} pillars match ({100*match_count/total:.1f}%)")
if mismatches:
    print("\nMismatches:")
    for name, computed, gt in mismatches:
        print(f"  {name}: computed={computed} vs gt={gt}")
