"""Smoke test for audit_decide.vote() — covers 10 scenarios from rule spec.

Run: python test_audit_decide.py
Expects: all 10 cases match expected outcome. Exit 0 on full pass.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from audit_decide import vote, HIGH_RISK

cases = [
    # (label, field, readings, expected_decision, expected_value)
    ("3/3 same, all high",
     "yong_shen",
     [
         {"value": "金", "confidence": "high", "source": "main"},
         {"value": "金", "confidence": "high", "source": "blind"},
         {"value": "金", "confidence": "high", "source": "bazi"},
     ],
     "PASS", "金"),

    ("2/1 majority, high in maj",
     "yong_shen",
     [
         {"value": "金", "confidence": "high", "source": "main"},
         {"value": "金", "confidence": "high", "source": "blind"},
         {"value": "土", "confidence": "low", "source": "bazi"},
     ],
     "PASS", "金"),

    ("3/3 same but ALL LOW (Celah 1)",
     "yong_shen",
     [
         {"value": "金", "confidence": "low", "source": "main"},
         {"value": "金", "confidence": "low", "source": "blind"},
         {"value": "金", "confidence": "low", "source": "bazi"},
     ],
     "STOP", None),

    ("2/1 majority but minority more confident",
     "yong_shen",
     [
         {"value": "金", "confidence": "low", "source": "main"},
         {"value": "金", "confidence": "low", "source": "blind"},
         {"value": "土", "confidence": "high", "source": "bazi"},
     ],
     "STOP", None),

    ("2/1 mixed conf in majority but has high",
     "yong_shen",
     [
         {"value": "金", "confidence": "low", "source": "main"},
         {"value": "金", "confidence": "high", "source": "blind"},
         {"value": "土", "confidence": "low", "source": "bazi"},
     ],
     "PASS", "金"),

    ("0/3 different all high (Celah 2)",
     "yong_shen",
     [
         {"value": "金", "confidence": "high", "source": "main"},
         {"value": "土", "confidence": "high", "source": "blind"},
         {"value": "木", "confidence": "high", "source": "bazi"},
     ],
     "STOP", None),

    ("0/3 different, mixed conf",
     "yong_shen",
     [
         {"value": "金", "confidence": "high", "source": "main"},
         {"value": "土", "confidence": "low", "source": "blind"},
         {"value": "木", "confidence": "low", "source": "bazi"},
     ],
     "STOP", None),

    ("2/1 split with majority all high, minority high (count wins fairly)",
     "yong_shen",
     [
         {"value": "金", "confidence": "high", "source": "main"},
         {"value": "金", "confidence": "high", "source": "blind"},
         {"value": "土", "confidence": "high", "source": "bazi"},
     ],
     "PASS", "金"),

    ("Invalid value 丁 — falls to safety net via secondary fix",
     "yong_shen",
     [
         {"value": "丁", "confidence": "high", "source": "main"},
         {"value": "火", "confidence": "high", "source": "blind"},
         {"value": "火", "confidence": "high", "source": "bazi"},
     ],
     "PASS", "火"),

    ("All majority medium (no high) — STOP",
     "yong_shen",
     [
         {"value": "金", "confidence": "med", "source": "main"},
         {"value": "金", "confidence": "med", "source": "blind"},
         {"value": "土", "confidence": "low", "source": "bazi"},
     ],
     "STOP", None),

    ("xiantian int field — 2/1 majority high",
     "xiantian_yi",
     [
         {"value": 4, "confidence": "high", "source": "main"},
         {"value": 4, "confidence": "high", "source": "blind"},
         {"value": 3, "confidence": "low", "source": "bazi"},
     ],
     "PASS", 4),

    ("xiantian out-of-range fails safety",
     "xiantian_yi",
     [
         {"value": 99, "confidence": "high", "source": "main"},
         {"value": 99, "confidence": "high", "source": "blind"},
         {"value": 4, "confidence": "low", "source": "bazi"},
     ],
     "STOP", None),

    ("canggan stem_list — exact match approve",
     "canggan_tahun",
     [
         {"value": "辛癸己", "confidence": "high", "source": "main"},
         {"value": "辛癸己", "confidence": "high", "source": "blind"},
         {"value": "辛癸己", "confidence": "high", "source": "bazi"},
     ],
     "PASS", "辛癸己"),

    ("canggan order matters — different stems STOP",
     "canggan_tahun",
     [
         {"value": "辛癸己", "confidence": "high", "source": "main"},
         {"value": "癸辛己", "confidence": "high", "source": "blind"},
         {"value": "己辛癸", "confidence": "high", "source": "bazi"},
     ],
     "STOP", None),

    ("Tier 2 — 5 readings, 4/5 majority high",
     "yong_shen",
     [
         {"value": "金", "confidence": "high", "source": "main"},
         {"value": "金", "confidence": "high", "source": "blind"},
         {"value": "土", "confidence": "low", "source": "bazi"},
         {"value": "金", "confidence": "high", "source": "tier2-a"},
         {"value": "金", "confidence": "high", "source": "tier2-b"},
     ],
     "PASS", "金"),
]

# Run cases
fail = 0
for label, field, readings, exp_dec, exp_val in cases:
    result = vote(field, readings)
    ok = result["decision"] == exp_dec and result.get("value") == exp_val
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}")
    print(f"   field={field} → decision={result['decision']} value={result.get('value')!r}")
    print(f"   reason: {result.get('reason')}")
    if not ok:
        print(f"   ✗ expected: decision={exp_dec} value={exp_val!r}")
        fail += 1
    print()

if fail:
    print(f"\n❌ {fail}/{len(cases)} cases failed")
    sys.exit(1)
print(f"\n✅ all {len(cases)} cases passed")
sys.exit(0)
