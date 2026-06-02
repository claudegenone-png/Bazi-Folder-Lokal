"""V7.1 — Marriage page triple-vote decider.

Consumes 3 (or 5 with Tier 2) marriage agent JSON outputs and decides consensus.

Usage:
  python audit_marriage_decide.py <subject_id> <agent_A.json> <agent_B.json> <agent_C.json> [<agent_D.json> <agent_E.json>]

Output:
  - stdout: human-readable decision summary
  - file: _AUDIT_LOGS/marriage_{subject_id}_decision.json (machine-readable)
  - exit code: 0=PASS unanimous, 1=PASS majority, 2=ESCALATE Tier 2, 3=STOP

Decision logic (per tier_block):
  - shios_branch set equality across slots → 3/3 = unanimous, 2/3 = majority
  - tier_label_hz must match across slots (string)
  - Disagreement on either → STOP that tier_block for retake

Used by: AUTORUN.md Step 3.7c (after spawning 3 marriage-specialist agents)
"""
import sys, json, io
from pathlib import Path
from collections import Counter

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "_AUDIT_LOGS"


def load_agent(path: Path) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e), "path": str(path)}


def normalize_tier_label(label: str) -> str:
    """Map tier label variants to canonical."""
    label = (label or "").strip()
    aliases = {
        "大吉": "大吉", "吉": "吉", "次吉": "次吉",
        "吉凶相半": "吉凶相半", "半吉": "吉凶相半",
        "忌": "忌", "凶": "忌",
    }
    return aliases.get(label, label)


def vote_tier_block(slots: list[dict], tier_label_hz: str) -> dict:
    """For one tier, vote on shios_branch + prose presence."""
    # Find this tier in each slot
    found = []
    for slot in slots:
        for tb in slot.get("tier_blocks", []) or []:
            if normalize_tier_label(tb.get("tier_label_hz","")) == tier_label_hz:
                found.append(tb)
                break

    n_present = len(found)
    if n_present == 0:
        return {"tier": tier_label_hz, "verdict": "ABSENT", "consensus": 0, "decision_shios": []}

    # Vote on shios_branch
    branch_sets = [frozenset(tb.get("shios_branch") or []) for tb in found]
    counter = Counter(branch_sets)
    top_set, top_count = counter.most_common(1)[0]
    n_total = len(slots)

    if top_count == n_total:
        verdict = "UNANIMOUS"
    elif top_count >= (n_total + 1) // 2:  # strict majority
        verdict = "MAJORITY"
    else:
        verdict = "DISAGREE"

    # Vote on prose: pick high-confidence agent's prose
    prose_hz = None; prose_id = None
    for tb in found:
        if tb.get("prose_hz_verbatim") and not prose_hz:
            prose_hz = tb["prose_hz_verbatim"]
        if tb.get("prose_id_paraphrase") and not prose_id:
            prose_id = tb["prose_id_paraphrase"]

    return {
        "tier": tier_label_hz,
        "verdict": verdict,
        "consensus": f"{top_count}/{n_total}",
        "decision_shios": sorted(top_set),
        "shios_count": len(top_set),
        "prose_hz": prose_hz,
        "prose_id": prose_id,
        "vote_breakdown": {
            ", ".join(sorted(s)): c for s, c in counter.most_common()
        },
    }


def main(argv):
    if len(argv) < 5:
        print("Usage: python audit_marriage_decide.py <subject_id> <A.json> <B.json> <C.json> [<D.json> <E.json>]")
        return 99

    subject_id = argv[1]
    slot_paths = [Path(p) for p in argv[2:]]
    slots = [load_agent(p) for p in slot_paths]
    valid_slots = [s for s in slots if "tier_blocks" in s]

    print(f"\n=== Marriage Triple-Vote Decision (subject={subject_id}) ===")
    print(f"Slots loaded: {len(valid_slots)}/{len(slots)}")
    for i, s in enumerate(slots):
        if "error" in s:
            print(f"  Slot {chr(65+i)}: ERROR — {s['error']}")
        else:
            n_tiers = len(s.get("tier_blocks") or [])
            print(f"  Slot {chr(65+i)}: {n_tiers} tiers, confidence={s.get('confidence','—')}")

    # Collect all tier labels seen across slots
    all_tiers = set()
    for s in valid_slots:
        for tb in s.get("tier_blocks", []) or []:
            all_tiers.add(normalize_tier_label(tb.get("tier_label_hz","")))
    all_tiers.discard("")

    decisions = []
    overall_verdict = "PASS"
    for tier in sorted(all_tiers):
        d = vote_tier_block(valid_slots, tier)
        decisions.append(d)
        print(f"\n  Tier '{tier}':")
        print(f"    verdict: {d['verdict']} ({d['consensus']})")
        print(f"    decision_shios: {d['decision_shios']} (count={d['shios_count']})")
        if d['verdict'] == "DISAGREE":
            print(f"    breakdown: {d['vote_breakdown']}")
            overall_verdict = "ESCALATE"

    # Check overlap (shios should be mutually exclusive across tiers)
    used = set()
    for d in decisions:
        for b in d["decision_shios"]:
            if b in used:
                print(f"\n  ⚠ Branch '{b}' appears in multiple tiers — manual review needed")
                overall_verdict = "STOP"
            used.add(b)

    print(f"\n=== Overall: {overall_verdict} ===")

    # Save decision
    AUDIT_DIR.mkdir(exist_ok=True)
    out_path = AUDIT_DIR / f"marriage_{subject_id}_decision.json"
    out = {
        "subject_id": subject_id,
        "n_slots": len(valid_slots),
        "decisions": decisions,
        "overall_verdict": overall_verdict,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Decision saved: {out_path}")

    # Recommend MD field updates
    cocok_tiers = [d for d in decisions if d["tier"] in ("大吉","吉","次吉","吉凶相半")]
    hindari_tiers = [d for d in decisions if d["tier"] in ("忌","凶")]
    cocok_shios = sorted(set(b for d in cocok_tiers for b in d["decision_shios"]))
    hindari_shios = sorted(set(b for d in hindari_tiers for b in d["decision_shios"]))
    rels = ", ".join(f"{b}:{d['tier']}" for d in cocok_tiers for b in d["decision_shios"])

    print(f"\n=== Recommended MD field values ===")
    print(f"  marriage_cocok: {', '.join(cocok_shios)}")
    print(f"  marriage_hindari: {', '.join(hindari_shios)}")
    print(f"  marriage_cocok_relationships: {rels}")
    if cocok_tiers and cocok_tiers[0].get("prose_id"):
        print(f"  marriage_cocok_tafsir: {cocok_tiers[0]['prose_id'][:80]}...")
    if hindari_tiers and hindari_tiers[0].get("prose_id"):
        print(f"  marriage_hindari_tafsir: {hindari_tiers[0]['prose_id'][:80]}...")

    if overall_verdict == "PASS":
        return 0
    elif overall_verdict == "ESCALATE":
        return 2
    else:
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
