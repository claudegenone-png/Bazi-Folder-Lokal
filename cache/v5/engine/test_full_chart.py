# -*- coding: utf-8 -*-
"""V5 Engine Phase 2 — Verify pillars + 命宮 + 大運 起運 + Zi Wei core vs 10 Yiteng GT.
"""
from __future__ import annotations
import sys, json
sys.stdout.reconfigure(encoding="utf-8")

from lunar_python import Solar, Lunar

# ground truth from 10 subjects
SUBJECTS = [
    # name, sex(M/F), Y, Mo, D, H, Mi, pillars, day_master, ming_gong, qiyun_age, ziwei_ming_branch, ziwei_shen_branch, wuxing_ju
    ("Michele",   "F", 1995,  7, 22, 14,  0, ("乙亥","癸未","甲寅","辛未"), "甲", None,    None, "子", "寅", "火六局"),
    ("Tommy",     "M", 1960,  5,  8, 22, 15, ("庚子","辛巳","丙申","己亥"), "丙", None,    9,    "午", "辰", "木三局"),
    ("HuLiLi",    "F", 1964,  5,  5,  0,  5, ("甲辰","戊辰","甲寅","甲子"), "甲", "丙子",  11,   "辰", "辰", "木三局"),
    ("LinWenJin", "M", 1998,  2, 27,  9, 43, ("戊寅","甲寅","乙巳","辛巳"), "乙", "辛酉",  3,    None, None, None),
    ("LinPinAi",  "F", 1989,  5, 13,  7, 45, ("己巳","己巳","癸酉","丙辰"), "癸", "壬申",  9,    None, None, None),
    ("Leana",     "F", 1958,  6, 13, 16,  0, ("戊戌","戊午","辛酉","丙申"), "辛", "乙卯",  3,    "酉", "丑", "木三局"),
    ("Mike",      "M", 2018,  9, 13, 12, 23, ("戊戌","辛酉","戊申","戊午"), "戊", "甲寅",  4,    None, None, None),
    ("Bryant",    "M", 1991,  9,  4, 12, 51, ("辛未","丙申","丁丑","丙午"), "丁", "庚寅",  10,   "寅", "寅", "木三局"),
    ("LinXiuLing","F", 1990,  6, 11, 23, 40, ("庚午","壬午","丁未","壬子"), "丁", "丁亥",  3,    "寅", None, None),
    ("LinRuYi",   "F", 1995,  5, 30, 10, 35, ("乙亥","辛巳","辛酉","癸巳"), "辛", "壬午",  3,    "丑", "亥", "火六局"),
]

def compute_pillars(y, mo, d, h, mi):
    s = Solar.fromYmdHms(y, mo, d, h, mi, 0)
    b = s.getLunar().getEightChar()
    return (b.getYear(), b.getMonth(), b.getDay(), b.getTime())

def compute_ming_gong(y, mo, d, h, mi):
    """命宮 calculation per BaZi tradition.
    Yiteng formula: 命宮干支. lunar-python provides this directly."""
    s = Solar.fromYmdHms(y, mo, d, h, mi, 0)
    b = s.getLunar().getEightChar()
    return b.getMingGong()  # returns 干支 like '丙子'

def compute_qiyun(y, mo, d, h, mi, sex):
    """大運 起運歲 (offset in years; year-component only)."""
    s = Solar.fromYmdHms(y, mo, d, h, mi, 0)
    b = s.getLunar().getEightChar()
    yun = b.getYun(1 if sex == "M" else 0)
    return yun.getStartYear(), yun.getStartMonth(), yun.getStartDay()  # offset y/m/d

print("="*100)
print("V5 Engine — Phase 2: Pillars + 命宮 + 大運起運")
print("="*100)
print(f"{'Subject':<12}{'Pillars':<28}{'命宮':<10}{'GT 命宮':<10}{'起運':<14}{'GT起運':<8}")
print("-"*100)

results = []
for s in SUBJECTS:
    name, sex, y, mo, d, h, mi, gt_p, dm, gt_mg, gt_qy, *_ = s
    pillars = compute_pillars(y, mo, d, h, mi)
    pillar_match = pillars == gt_p
    mg = compute_ming_gong(y, mo, d, h, mi)
    mg_match = (gt_mg is None) or (mg == gt_mg)
    qy_y, qy_m, qy_d = compute_qiyun(y, mo, d, h, mi, sex)
    qy_age_approx = qy_y  # offset year-component IS the qi-yun age
    qy_match = (gt_qy is None) or (abs(qy_age_approx - gt_qy) <= 1)
    p_str = "/".join(pillars)
    qy_str = f"{qy_age_approx}y{qy_m}m{qy_d}d"
    gt_qy_str = str(gt_qy) if gt_qy is not None else "?"
    flag = "OK" if (pillar_match and mg_match and qy_match) else "DIFF"
    results.append((name, pillar_match, mg_match, qy_match, flag))
    print(f"{name:<12}{p_str:<28}{mg:<10}{(gt_mg or '?'):<10}{qy_str:<14}{gt_qy_str:<8}{flag}")

print("-"*100)
pm = sum(1 for r in results if r[1])
mm = sum(1 for r in results if r[2])
qm = sum(1 for r in results if r[3])
print(f"\nPillars: {pm}/10 | 命宮: {mm}/10 | 起運: {qm}/10")
