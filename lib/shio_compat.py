"""
Shio Compatibility — static 12x12 lookup table.
Based on tradisi 三合 / 六合 / 六沖 / 六害 / 三刑.
"""

# 12 branches with Indonesian names and SVG file basenames
SHIO_INFO = {
    "子": {"id": "Tikus", "svg": "Tikus", "order": 0},
    "丑": {"id": "Kerbau", "svg": "Kerbau", "order": 1},
    "寅": {"id": "Macan", "svg": "Harimau", "order": 2},
    "卯": {"id": "Kelinci", "svg": "Kelinci", "order": 3},
    "辰": {"id": "Naga", "svg": "Naga", "order": 4},
    "巳": {"id": "Ular", "svg": "Ular", "order": 5},
    "午": {"id": "Kuda", "svg": "Kuda", "order": 6},
    "未": {"id": "Kambing", "svg": "Kambing", "order": 7},
    "申": {"id": "Monyet", "svg": "Monyet", "order": 8},
    "酉": {"id": "Ayam", "svg": "Ayam", "order": 9},
    "戌": {"id": "Anjing", "svg": "Anjing", "order": 10},
    "亥": {"id": "Babi", "svg": "Babi", "order": 11},
}

# 三合 (San He / Triple Harmony) — 4 groups of 3 branches each
SAN_HE = [
    ("申", "子", "辰"),  # Logam-Air group
    ("亥", "卯", "未"),  # Kayu group
    ("寅", "午", "戌"),  # Api group
    ("巳", "酉", "丑"),  # Logam group
]

# 六合 (Liu He / Sextile Harmony) — 6 pairs
LIU_HE = [
    ("子", "丑"), ("寅", "亥"), ("卯", "戌"),
    ("辰", "酉"), ("巳", "申"), ("午", "未"),
]

# 六沖 (Liu Chong / Direct Conflict) — 6 opposing pairs
LIU_CHONG = [
    ("子", "午"), ("丑", "未"), ("寅", "申"),
    ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
]

# 六害 (Liu Hai / Harm) — 6 pairs
LIU_HAI = [
    ("子", "未"), ("丑", "午"), ("寅", "巳"),
    ("卯", "辰"), ("申", "亥"), ("酉", "戌"),
]

# 三刑 (San Xing / Triple Punishment)
SAN_XING = [
    ("寅", "巳"), ("巳", "申"), ("申", "寅"),  # Triangle 1
    ("丑", "戌"), ("戌", "未"), ("未", "丑"),  # Triangle 2
    ("子", "卯"),  # Mutual punishment
    ("辰", "辰"), ("午", "午"), ("酉", "酉"), ("亥", "亥"),  # Self-punishment
]


def _pair_in(pairs, a, b):
    """Check if (a,b) or (b,a) is in the list of pairs/triples."""
    for grp in pairs:
        if a in grp and b in grp and a != b:
            return True
    return False


def relation(self_branch: str, other_branch: str) -> dict:
    """Return relationship between two shio (one-way: self → other).
    Priority: san_he > liu_he > liu_chong > san_xing > liu_hai > netral.
    """
    if self_branch == other_branch:
        return {"code": "self", "label_id": "Diri Sendiri", "label_cn": "本命",
                "tier": "self", "score": 0}

    # San He (triple harmony) — strongest positive
    for grp in SAN_HE:
        if self_branch in grp and other_branch in grp:
            return {"code": "san_he", "label_id": "Sangat Cocok", "label_cn": "三合",
                    "tier": "very_good", "score": 3}

    # Liu He (sextile harmony) — positive
    for a, b in LIU_HE:
        if (self_branch == a and other_branch == b) or \
           (self_branch == b and other_branch == a):
            return {"code": "liu_he", "label_id": "Harmonis", "label_cn": "六合",
                    "tier": "good", "score": 2}

    # Liu Chong (direct conflict) — strong negative
    for a, b in LIU_CHONG:
        if (self_branch == a and other_branch == b) or \
           (self_branch == b and other_branch == a):
            return {"code": "liu_chong", "label_id": "Bertentangan", "label_cn": "六沖",
                    "tier": "avoid", "score": -3}

    # San Xing (triple punishment)
    if _pair_in(SAN_XING, self_branch, other_branch):
        return {"code": "san_xing", "label_id": "Konflik Tiga", "label_cn": "三刑",
                "tier": "avoid", "score": -2}

    # Liu Hai (harm)
    if _pair_in(LIU_HAI, self_branch, other_branch):
        return {"code": "liu_hai", "label_id": "Saling Melukai", "label_cn": "六害",
                "tier": "warning", "score": -1}

    return {"code": "neutral", "label_id": "Netral", "label_cn": "平",
            "tier": "neutral", "score": 0}


def full_compatibility(self_branch: str) -> dict:
    """Return compatibility map of self_branch with all 12 branches."""
    result = []
    branches = ["子", "丑", "寅", "卯", "辰", "巳",
                "午", "未", "申", "酉", "戌", "亥"]
    for b in branches:
        info = SHIO_INFO[b]
        rel = relation(self_branch, b)
        result.append({
            "branch": b,
            "id": info["id"],
            "svg": info["svg"],
            **rel,
        })

    # Group by tier
    grouped = {
        "very_good": [r for r in result if r["tier"] == "very_good"],
        "good": [r for r in result if r["tier"] == "good"],
        "avoid": [r for r in result if r["tier"] == "avoid"],
        "warning": [r for r in result if r["tier"] == "warning"],
        "neutral": [r for r in result if r["tier"] == "neutral"],
    }
    return {"all": result, "grouped": grouped}


if __name__ == "__main__":
    import json, sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    macan_compat = full_compatibility("寅")
    print("Macan compatibility:")
    for r in macan_compat["all"]:
        print(f"  {r['branch']} {r['id']}: {r['label_id']} ({r['label_cn']})")
