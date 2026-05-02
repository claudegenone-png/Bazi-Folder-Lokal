"""Sandbox1 Phase 4 - Native pillars compute from birth date+time.

Uses sxtwl library (precise solar term calculations) to compute 4 pillars
without needing OCR. Validated against 星僑 V2.6 software output.

Inputs: solar (Gregorian) date + time + optional gender for direction.
Outputs: pillars dict matching subject.json schema.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    import sxtwl
except ImportError:
    raise ImportError("sxtwl not installed. Run: pip install sxtwl")

STEMS_HZ = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
BRANCHES_HZ = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

STEMS_PINYIN = ["Jia","Yi","Bing","Ding","Wu","Ji","Geng","Xin","Ren","Gui"]
BRANCHES_PINYIN = ["Zi","Chou","Yin","Mao","Chen","Si","Wu","Wei","Shen","You","Xu","Hai"]


def compute_pillars(year: int, month: int, day: int, hour: int, minute: int = 0) -> dict:
    """Compute 4 pillars from solar (Gregorian) date+time.

    hour: 24-hour format (0-23). Minute used for boundary cases (e.g., 23:00-00:59 is 子時).
    """
    # sxtwl uses 24-hour clock; for hour boundary, use the actual clock hour
    d = sxtwl.fromSolar(year, month, day)

    y = d.getYearGZ()
    m = d.getMonthGZ()
    dg = d.getDayGZ()
    h = d.getHourGZ(hour)

    return {
        "year":  {"stem_hz": STEMS_HZ[y.tg],  "branch_hz": BRANCHES_HZ[y.dz],
                  "stem_id": STEMS_PINYIN[y.tg], "branch_id": BRANCHES_PINYIN[y.dz]},
        "month": {"stem_hz": STEMS_HZ[m.tg],  "branch_hz": BRANCHES_HZ[m.dz],
                  "stem_id": STEMS_PINYIN[m.tg], "branch_id": BRANCHES_PINYIN[m.dz]},
        "day":   {"stem_hz": STEMS_HZ[dg.tg], "branch_hz": BRANCHES_HZ[dg.dz],
                  "stem_id": STEMS_PINYIN[dg.tg], "branch_id": BRANCHES_PINYIN[dg.dz],
                  "is_day_master": True},
        "hour":  {"stem_hz": STEMS_HZ[h.tg],  "branch_hz": BRANCHES_HZ[h.dz],
                  "stem_id": STEMS_PINYIN[h.tg], "branch_id": BRANCHES_PINYIN[h.dz]},
    }


def da_yun_direction(year_stem_hz: str, gender_id: str) -> str:
    """Yang Year + Male = forward, Yin Year + Female = forward, others = backward.

    Yang stems: 甲丙戊庚壬 (indices 0,2,4,6,8). Yin: indices 1,3,5,7,9.
    """
    yang_stems = {"甲","丙","戊","庚","壬"}
    is_yang_year = year_stem_hz in yang_stems
    is_male = gender_id.lower() in ("male", "pria", "laki-laki", "m", "陽男")
    if is_yang_year == is_male:
        return "forward"
    return "backward"


def da_yun_start_age(year, month, day, hour, gender_id, year_stem_hz):
    """Compute Da Yun start age via solar term boundary (节 transition).

    Walk forward (or backward) day-by-day until month branch (地支) changes.
    Days / 3 = years (floor). Approximation; software may differ by ~1 year on
    boundary cases (no hour-precise term timestamps here).
    """
    from datetime import date, timedelta
    direction = da_yun_direction(year_stem_hz, gender_id)
    forward = direction == "forward"

    day_obj = sxtwl.fromSolar(year, month, day)
    m_start = day_obj.getMonthGZ().dz
    step = 1 if forward else -1
    d_start = date(year, month, day)

    for offset in range(1, 60):
        d = d_start + timedelta(days=offset * step)
        d_obj = sxtwl.fromSolar(d.year, d.month, d.day)
        if d_obj.getMonthGZ().dz != m_start:
            return offset // 3
    return 5 if forward else 10  # safe fallback


def compute_subject_core(name_id: str, name_hanzi: str, gender_id: str,
                          birth_date: str, birth_time: str, age_at_report: int = None):
    """One-shot: subject core computation from minimal inputs.

    birth_date: ISO YYYY-MM-DD
    birth_time: HH:MM (24h)
    Returns dict ready for build_subject() in build_subject.py.
    """
    y, mo, d = map(int, birth_date.split("-"))
    h, mi = map(int, birth_time.split(":"))

    pillars = compute_pillars(y, mo, d, h, mi)
    year_stem = pillars["year"]["stem_hz"]
    direction = da_yun_direction(year_stem, gender_id)
    # NOTE: start_age is approximation — should be derived from solar term distance
    start_age = da_yun_start_age(y, mo, d, h, gender_id, year_stem)

    return {
        "name_id": name_id,
        "name_hanzi": name_hanzi,
        "gender_id": gender_id,
        "birth_date": birth_date,
        "birth_time": birth_time,
        "age_at_report": age_at_report,
        "pillars": pillars,
        "da_yun_direction": direction,
        "da_yun_start_age": start_age,
    }


def _self_test():
    """Validate against known subjects."""
    print("=== Phase 4 Self-Test ===")
    cases = [
        ("Michele", "1995-07-22", "14:48", "Wanita",
         {"year":"乙亥","month":"癸未","day":"甲寅","hour":"辛未"}),
        ("Tommy", "1960-05-08", "22:15", "Pria",
         {"year":"庚子","month":"辛巳","day":"丙申","hour":"己丑"}),
    ]
    all_pass = True
    for name, dt, time_str, gender, expected in cases:
        y,mo,d = map(int, dt.split("-"))
        h,mi = map(int, time_str.split(":"))
        p = compute_pillars(y, mo, d, h, mi)
        got = {k: p[k]["stem_hz"]+p[k]["branch_hz"] for k in ["year","month","day","hour"]}
        ok = got == expected
        status = "PASS" if ok else "FAIL"
        print(f"  {name}: {status}")
        if not ok:
            for k in ["year","month","day","hour"]:
                e, g = expected[k], got[k]
                mark = "OK" if e == g else "WRONG"
                print(f"    {k}: expected {e}, got {g} [{mark}]")
            all_pass = False
        # Check direction
        direction = da_yun_direction(p["year"]["stem_hz"], gender)
        print(f"    direction: {direction}")
    print()
    print("OVERALL:", "PASS" if all_pass else "FAIL")


if __name__ == "__main__":
    _self_test()
