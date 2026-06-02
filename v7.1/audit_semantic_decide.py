"""V7.1 — Semantic check decider.

Consumes verifier subagent JSON output and decides whether to STOP build.

Usage:
  python audit_semantic_decide.py <subject_id>
  # Reads _AUDIT_LOGS/semantic_{subject_id}.json
  # Exit 0=PROCEED, 1=warn, 2=FIX_BEFORE_BUILD (block), 3=MANUAL_REVIEW
"""
import sys, json
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "_AUDIT_LOGS"


def main(subject_id: str) -> int:
    inp = AUDIT_DIR / f"semantic_{subject_id}.json"
    if not inp.exists():
        print(f"[semantic-decide] No verifier output at {inp}")
        print(f"  Either skip semantic check or spawn verifier first (AUDIT_SEMANTIC_PROMPT.md).")
        return 0  # graceful: missing verifier = not run, not failure

    data = json.loads(inp.read_text(encoding='utf-8'))
    verdicts = data.get("verdicts", []) or []
    summary = data.get("summary", {}) or {}
    rec = data.get("recommendation", "PROCEED")
    high_sev = data.get("high_severity_count", 0)

    print(f"\n=== Semantic Check Decision (subject={subject_id}) ===")
    print(f"Total checks: {data.get('n_checks', len(verdicts))}")
    print(f"Summary: {summary}")
    print(f"High-severity mismatches: {high_sev}")
    print(f"Recommendation: {rec}")

    # List mismatches
    mismatches = [v for v in verdicts if v.get("verdict") == "MISMATCH"]
    conflicts = [v for v in verdicts if v.get("verdict") == "INTERNAL_CONFLICT"]
    if mismatches:
        print(f"\n  ✘ MISMATCH ({len(mismatches)}):")
        for v in mismatches:
            sev = v.get("severity","")
            print(f"    [{sev}] {v.get('field')} — {v.get('evidence','')[:150]}")
    if conflicts:
        print(f"\n  ⚠ INTERNAL_CONFLICT ({len(conflicts)}):")
        for v in conflicts:
            print(f"    {v.get('field')} — {v.get('evidence','')[:150]}")

    if rec == "FIX_BEFORE_BUILD" or high_sev >= 1:
        print(f"\n[semantic-decide] BLOCK — fix high-severity issues before build.")
        return 2
    if rec == "MANUAL_REVIEW":
        print(f"\n[semantic-decide] MANUAL REVIEW recommended.")
        return 3
    print(f"\n[semantic-decide] PROCEED.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: audit_semantic_decide.py <subject_id>")
        sys.exit(99)
    sys.exit(main(sys.argv[1]))
