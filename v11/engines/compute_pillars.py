"""FULL-MD MODE: compute disabled. Functions retained as no-op for API compatibility.
All values come from MD via parse_md.py.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8')

# FULL-MD MODE: sxtwl import removed (no compute performed).

STEMS_HZ = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
BRANCHES_HZ = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

STEMS_PINYIN = ["Jia","Yi","Bing","Ding","Wu","Ji","Geng","Xin","Ren","Gui"]
BRANCHES_PINYIN = ["Zi","Chou","Yin","Mao","Chen","Si","Wu","Wei","Shen","You","Xu","Hai"]


def compute_pillars(year: int, month: int, day: int, hour: int, minute: int = 0) -> dict:
    """No-op. Pillars now sourced from MD via parse_md.py."""
    # FULL-MD MODE: disabled
    return {"year": None, "month": None, "day": None, "hour": None}


def da_yun_direction(year_stem_hz: str, gender_id: str) -> str | None:
    """No-op. Da Yun direction now sourced from MD field da_yun_arah_id."""
    # FULL-MD MODE: disabled
    return None


def da_yun_start_age(year, month, day, hour, gender_id, year_stem_hz):
    """No-op. Da Yun start age now sourced from MD field da_yun_start_age."""
    # FULL-MD MODE: disabled
    return None


def compute_subject_core(name_id: str, name_hanzi: str, gender_id: str,
                          birth_date: str, birth_time: str, age_at_report: int = None):
    """No-op. Subject core now built from MD via build_from_ocr.py."""
    # FULL-MD MODE: disabled
    return {
        "name_id": name_id,
        "name_hanzi": name_hanzi,
        "gender_id": gender_id,
        "birth_date": birth_date,
        "birth_time": birth_time,
        "age_at_report": age_at_report,
        "pillars": {"year": None, "month": None, "day": None, "hour": None},
        "da_yun_direction": None,
        "da_yun_start_age": None,
    }


if __name__ == "__main__":
    print("FULL-MD MODE: compute disabled. This module is now a no-op shim.")
