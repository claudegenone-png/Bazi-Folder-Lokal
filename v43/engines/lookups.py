"""Deterministic lookup tables for BaZi rendering.

These don't change per subject — they're traditional Chinese metaphysics constants.
"""

# 10 Heavenly Stems (天干) → element + polarity
STEMS = {
    "甲": {"el_hz": "木", "el_id": "Kayu",  "polarity_id": "Yang", "pinyin": "Jiǎ"},
    "乙": {"el_hz": "木", "el_id": "Kayu",  "polarity_id": "Yin",  "pinyin": "Yǐ"},
    "丙": {"el_hz": "火", "el_id": "Api",   "polarity_id": "Yang", "pinyin": "Bǐng"},
    "丁": {"el_hz": "火", "el_id": "Api",   "polarity_id": "Yin",  "pinyin": "Dīng"},
    "戊": {"el_hz": "土", "el_id": "Tanah", "polarity_id": "Yang", "pinyin": "Wù"},
    "己": {"el_hz": "土", "el_id": "Tanah", "polarity_id": "Yin",  "pinyin": "Jǐ"},
    "庚": {"el_hz": "金", "el_id": "Logam", "polarity_id": "Yang", "pinyin": "Gēng"},
    "辛": {"el_hz": "金", "el_id": "Logam", "polarity_id": "Yin",  "pinyin": "Xīn"},
    "壬": {"el_hz": "水", "el_id": "Air",   "polarity_id": "Yang", "pinyin": "Rén"},
    "癸": {"el_hz": "水", "el_id": "Air",   "polarity_id": "Yin",  "pinyin": "Guǐ"},
}

# 12 Earthly Branches (地支) → shio + radical hz
BRANCHES = {
    "子": {"shio_id": "Tikus",   "shio_radical_hz": "鼠", "pinyin": "Zǐ"},
    "丑": {"shio_id": "Kerbau",  "shio_radical_hz": "牛", "pinyin": "Chǒu"},
    "寅": {"shio_id": "Harimau", "shio_radical_hz": "虎", "pinyin": "Yín"},
    "卯": {"shio_id": "Kelinci", "shio_radical_hz": "兔", "pinyin": "Mǎo"},
    "辰": {"shio_id": "Naga",    "shio_radical_hz": "龍", "pinyin": "Chén"},
    "巳": {"shio_id": "Ular",    "shio_radical_hz": "蛇", "pinyin": "Sì"},
    "午": {"shio_id": "Kuda",    "shio_radical_hz": "馬", "pinyin": "Wǔ"},
    "未": {"shio_id": "Kambing", "shio_radical_hz": "羊", "pinyin": "Wèi"},
    "申": {"shio_id": "Monyet",  "shio_radical_hz": "猴", "pinyin": "Shēn"},
    "酉": {"shio_id": "Ayam",    "shio_radical_hz": "雞", "pinyin": "Yǒu"},
    "戌": {"shio_id": "Anjing",  "shio_radical_hz": "狗", "pinyin": "Xū"},
    "亥": {"shio_id": "Babi",    "shio_radical_hz": "豬", "pinyin": "Hài"},
}


def stem_pillar_text(stem_hz: str) -> str:
    """e.g., '辛' → '金 Logam Yin' formatted for the t-pill body."""
    s = STEMS[stem_hz]
    return f"{s['el_hz']}{s['el_id']} {s['polarity_id']}"


def branch_pillar_text(branch_hz: str) -> str:
    """e.g., '未' → '羊 Kambing' formatted for the t-pill body."""
    b = BRANCHES[branch_hz]
    return f"{b['shio_radical_hz']}{b['shio_id']}"


# Earthly branches in clock-wise order (i=0 子 top)
BRANCH_ORDER = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]


# 8 Trigrams (八卦) for Yang Zhai compass
TRIGRAMS = {
    "坎": {"symbol": "☵", "pinyin": "Kǎn", "label_id": "Air",    "dir_id": "Utara",     "dir_abbr": "U",  "dir_cn": "北",    "group": "Timur", "pos": "N"},
    "艮": {"symbol": "☶", "pinyin": "Gèn", "label_id": "Gunung", "dir_id": "Timur Laut","dir_abbr": "TL", "dir_cn": "東北", "group": "Barat", "pos": "NE"},
    "震": {"symbol": "☳", "pinyin": "Zhèn","label_id": "Petir",  "dir_id": "Timur",     "dir_abbr": "T",  "dir_cn": "東",    "group": "Timur", "pos": "E"},
    "巽": {"symbol": "☴", "pinyin": "Xùn", "label_id": "Angin",  "dir_id": "Tenggara",  "dir_abbr": "TG", "dir_cn": "東南", "group": "Timur", "pos": "SE"},
    "離": {"symbol": "☲", "pinyin": "Lí",  "label_id": "Api",    "dir_id": "Selatan",   "dir_abbr": "S",  "dir_cn": "南",    "group": "Timur", "pos": "S"},
    "坤": {"symbol": "☷", "pinyin": "Kūn", "label_id": "Bumi",   "dir_id": "Barat Daya","dir_abbr": "BD", "dir_cn": "西南", "group": "Barat", "pos": "SW"},
    "兌": {"symbol": "☱", "pinyin": "Duì", "label_id": "Danau",  "dir_id": "Barat",     "dir_abbr": "B",  "dir_cn": "西",    "group": "Barat", "pos": "W"},
    "乾": {"symbol": "☰", "pinyin": "Qián","label_id": "Langit", "dir_id": "Barat Laut","dir_abbr": "BL", "dir_cn": "西北", "group": "Barat", "pos": "NW"},
}

# Compass badge positions (cx, cy)
COMPASS_POSITIONS = {
    "N":  (200, 55),
    "NE": (302.5, 97.5),
    "E":  (345, 200),
    "SE": (302.5, 302.5),
    "S":  (200, 345),
    "SW": (97.5, 302.5),
    "W":  (55, 200),
    "NW": (97.5, 97.5),
}


# Wheel cell positions (cx, cy, label_x, label_y) — matches Michele's exact coordinates
WHEEL_POSITIONS = [
    (200,   55,    200, 22),   # 0 子 top
    (272.5, 74.4,  295, 46),   # 1 丑
    (325.6, 127.5, 368, 100),  # 2 寅
    (345,   200,   382, 204),  # 3 卯 right
    (325.6, 272.5, 368, 306),  # 4 辰
    (272.5, 325.6, 295, 358),  # 5 巳
    (200,   345,   200, 382),  # 6 午 bottom
    (127.5, 325.6, 105, 362),  # 7 未
    (74.4,  272.5, 32,  306),  # 8 申
    (55,    200,   22,  204),  # 9 酉 left
    (74.4,  127.5, 32,  100),  # 10 戌
    (127.5, 74.4,  85,  42),   # 11 亥
]

