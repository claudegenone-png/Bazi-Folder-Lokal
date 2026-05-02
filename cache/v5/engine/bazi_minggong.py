# -*- coding: utf-8 -*-
"""BaZi 命宮 計算 (子平 月將 method) — matches Yiteng V2.6.

Formula:
1. 月將 by 中氣 of birth date:
   - 雨水→春分: 亥, 春分→穀雨: 戌, 穀雨→小滿: 酉, 小滿→夏至: 申, 夏至→大暑: 未, 大暑→處暑: 午,
     處暑→秋分: 巳, 秋分→霜降: 辰, 霜降→小雪: 卯, 小雪→冬至: 寅, 冬至→大寒: 丑, 大寒→雨水: 子
2. 命宮支_index = (月將_index + 卯_index - 時支_index) % 12  where 子=0..亥=11, 卯=3
3. 命宮干 by 五虎遁 from 年干: 甲己→丙寅, 乙庚→戊寅, 丙辛→庚寅, 丁壬→壬寅, 戊癸→甲寅
"""
from lunar_python import Solar

BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
B_IDX = {b: i for i, b in enumerate(BRANCHES)}

# 中氣 → 月將 mapping (lunar-python uses simplified names: 谷雨/小满/处暑)
ZHONGQI_TO_YUEJIANG = [
    ("雨水",   "亥"),  # 雨水 → 春分
    ("春分",   "戌"),  # 春分 → 谷雨
    ("谷雨",   "酉"),  # 谷雨 → 小满
    ("小满",   "申"),  # 小满 → 夏至
    ("夏至",   "未"),  # 夏至 → 大暑
    ("大暑",   "午"),  # 大暑 → 处暑
    ("处暑",   "巳"),  # 处暑 → 秋分
    ("秋分",   "辰"),  # 秋分 → 霜降
    ("霜降",   "卯"),  # 霜降 → 小雪
    ("小雪",   "寅"),  # 小雪 → 冬至
    ("冬至",   "丑"),  # 冬至 → 大寒
    ("大寒",   "子"),  # 大寒 → 雨水
]

# 五虎遁 lookup: year-stem → 寅月 starting stem (= 命宮支 index 寅)
WUHU_DUN = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

def get_yue_jiang(solar):
    """Find 月將 by checking which 中氣 the birth date is past."""
    lunar = solar.getLunar()
    jq_table = lunar.getJieQiTable()  # dict: name -> Solar object
    # Find the most recent 中氣 that solar is past
    target_zq = None
    target_julian = -1
    for zq_name, yue_jiang in ZHONGQI_TO_YUEJIANG:
        if zq_name in jq_table:
            zq_solar = jq_table[zq_name]
            # check if birth solar >= zq_solar
            if (solar.getYear(), solar.getMonth(), solar.getDay(), solar.getHour(), solar.getMinute()) >= \
               (zq_solar.getYear(), zq_solar.getMonth(), zq_solar.getDay(), zq_solar.getHour(), zq_solar.getMinute()):
                jul = (zq_solar.getYear()*10000 + zq_solar.getMonth()*100 + zq_solar.getDay())
                if jul > target_julian:
                    target_julian = jul
                    target_zq = (zq_name, yue_jiang)
    if target_zq is None:
        # Birth before this year's 雨水 → use previous year's 大寒 (月將 子)
        return "子"
    return target_zq[1]

def compute_bazi_minggong(year, month, day, hour, minute):
    """Returns 命宮干支 (e.g. '丙子')."""
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    bazi = solar.getLunar().getEightChar()
    year_stem = bazi.getYear()[0]
    hour_branch = bazi.getTime()[1]

    yj = get_yue_jiang(solar)
    yj_idx = B_IDX[yj]
    hb_idx = B_IDX[hour_branch]
    mg_branch_idx = (yj_idx + B_IDX["卯"] - hb_idx) % 12
    mg_branch = BRANCHES[mg_branch_idx]

    # 五虎遁: 寅月 stem from year stem
    yin_stem = WUHU_DUN[year_stem]
    yin_idx = STEMS.index(yin_stem)
    # offset from 寅 to mg_branch (going forward through stems & branches)
    branch_offset = (mg_branch_idx - B_IDX["寅"]) % 12
    mg_stem = STEMS[(yin_idx + branch_offset) % 10]

    return mg_stem + mg_branch


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    # Test all 10 subjects
    SUBJECTS = [
        ("Michele",   1995,  7, 22, 14,  0, None),
        ("Tommy",     1960,  5,  8, 22, 15, None),
        ("HuLiLi",    1964,  5,  5,  0,  5, "丙子"),
        ("LinWenJin", 1998,  2, 27,  9, 43, "辛酉"),
        ("LinPinAi",  1989,  5, 13,  7, 45, "壬申"),
        ("Leana",     1958,  6, 13, 16,  0, "乙卯"),
        ("Mike",      2018,  9, 13, 12, 23, "甲寅"),
        ("Bryant",    1991,  9,  4, 12, 51, "庚寅"),
        ("LinXiuLing",1990,  6, 11, 23, 40, "丁亥"),
        ("LinRuYi",   1995,  5, 30, 10, 35, "壬午"),
    ]
    print("BaZi 命宮 verification (子平 月將 formula):")
    ok = 0; checked = 0
    for name, y, mo, d, h, mi, gt in SUBJECTS:
        mg = compute_bazi_minggong(y, mo, d, h, mi)
        if gt is None:
            print(f"  {name:<12}: {mg}  (no GT)")
        else:
            checked += 1
            match = mg == gt
            if match: ok += 1
            print(f"  {name:<12}: {mg}  GT={gt}  {'OK' if match else 'DIFF'}")
    print(f"\n命宮: {ok}/{checked} match")
