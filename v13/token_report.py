"""Token usage report untuk V11 workflow.

Jalankan setelah Claude selesai generate MD:
    python token_report.py

Akan cari session Claude terbaru, hitung semua token (main + subagents),
dan print summary lengkap.
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
PROJECT_SLUG = "c--Users-sukam-OneDrive-Documents-Ramalan"

# Harga Sonnet (API pricing, untuk referensi estimasi)
PRICE_INPUT       = 3.00   # $ per 1M token
PRICE_OUTPUT      = 15.00  # $ per 1M token
PRICE_CACHE_WRITE = 3.75   # $ per 1M token
PRICE_CACHE_READ  = 0.30   # $ per 1M token


def parse_usage_from_jsonl(filepath: Path) -> dict:
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "calls": 0}
    try:
        for line in filepath.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                usage = (obj.get("message") or {}).get("usage")
                if not usage:
                    continue
                totals["input"]       += int(usage.get("input_tokens", 0) or 0)
                totals["output"]      += int(usage.get("output_tokens", 0) or 0)
                totals["cache_read"]  += int(usage.get("cache_read_input_tokens", 0) or 0)
                totals["cache_write"] += int(usage.get("cache_creation_input_tokens", 0) or 0)
                totals["calls"]       += 1
            except Exception:
                continue
    except Exception:
        pass
    return totals


def find_latest_session(project_dir: Path, n: int = 1) -> list[tuple[Path, list[Path], datetime]]:
    """Return n sesi terbaru: (main_jsonl, subagent_jsonls, mtime)."""
    sessions = []
    for f in project_dir.glob("*.jsonl"):
        sid = f.stem
        sub_dir = project_dir / sid / "subagents"
        subs = list(sub_dir.glob("*.jsonl")) if sub_dir.exists() else []
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        sessions.append((f, subs, mtime))
    sessions.sort(key=lambda x: x[2], reverse=True)
    return sessions[:n]


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def calc_cost(totals: dict) -> float:
    return (
        totals["input"]       * PRICE_INPUT       / 1_000_000 +
        totals["output"]      * PRICE_OUTPUT      / 1_000_000 +
        totals["cache_write"] * PRICE_CACHE_WRITE / 1_000_000 +
        totals["cache_read"]  * PRICE_CACHE_READ  / 1_000_000
    )


def merge(a: dict, b: dict) -> dict:
    return {k: a[k] + b[k] for k in a}


def main():
    project_dir = CLAUDE_PROJECTS / PROJECT_SLUG
    if not project_dir.exists():
        print(f"ERROR: Folder tidak ditemukan: {project_dir}")
        sys.exit(1)

    # Ambil N session — default 1 (terbaru), bisa override: python token_report.py 3
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    sessions = find_latest_session(project_dir, n)

    if not sessions:
        print("Tidak ada session ditemukan.")
        sys.exit(1)

    print()
    print("=" * 62)
    print(" TOKEN USAGE REPORT — V11 Workflow")
    print("=" * 62)

    grand = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "calls": 0}

    for main_file, sub_files, mtime in sessions:
        print(f"\n Session : {main_file.stem[:8]}...")
        print(f" Tanggal : {mtime.strftime('%d %b %Y %H:%M')}")
        print(f" Subagen : {len(sub_files)}")

        # Hitung per file
        totals = parse_usage_from_jsonl(main_file)
        for sf in sub_files:
            totals = merge(totals, parse_usage_from_jsonl(sf))

        cost = calc_cost(totals)

        print()
        print(f"  {'Input tokens':<22}: {fmt_tokens(totals['input'])}")
        print(f"  {'Output tokens':<22}: {fmt_tokens(totals['output'])}")
        print(f"  {'Cache read':<22}: {fmt_tokens(totals['cache_read'])}  (gratis di Pro)")
        print(f"  {'Cache write':<22}: {fmt_tokens(totals['cache_write'])}")
        print(f"  {'API calls':<22}: {totals['calls']}")
        print()
        print(f"  Estimasi biaya (jika pakai API):")
        print(f"    Input        : ${totals['input'] * PRICE_INPUT / 1_000_000:.4f}")
        print(f"    Output       : ${totals['output'] * PRICE_OUTPUT / 1_000_000:.4f}")
        print(f"    Cache write  : ${totals['cache_write'] * PRICE_CACHE_WRITE / 1_000_000:.4f}")
        print(f"    Cache read   : ${totals['cache_read'] * PRICE_CACHE_READ / 1_000_000:.4f}")
        print(f"    ---------------------------------")
        print(f"    TOTAL        : ${cost:.4f}")

        grand = merge(grand, totals)

    if n > 1:
        grand_cost = calc_cost(grand)
        print()
        print("=" * 62)
        print(f" TOTAL {n} SESSION")
        print(f"  Input    : {fmt_tokens(grand['input'])}")
        print(f"  Output   : {fmt_tokens(grand['output'])}")
        print(f"  Estimasi : ${grand_cost:.4f}  (~${grand_cost/n:.4f}/laporan)")
        print("=" * 62)

    print()


if __name__ == "__main__":
    main()
