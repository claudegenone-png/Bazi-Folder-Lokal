"""
validate_bazi.py — Cross-check BaZi MD fields secara matematis (tanpa foto).

5 checks:
1. shio_hz vs pilar_tahun branch (lookup deterministik 12 shio)
2. Semua 4 pilar stem = valid 天干
3. Semua 4 pilar branch = valid 地支
4. da_yun intervals konsisten (+10 tahun per cycle)
5. pilar_bulan vs da_yun[0] konsisten (1 langkah di 60-jiazi)

Usage:
    python validate_bazi.py <subject_id>

Exit code:
    0 = semua pass
    2 = ada error — fix MD sebelum build

Dipanggil otomatis oleh build_pdf.py setelah preflight.
"""

import sys, re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "subjects"

VALID_STEMS    = set("甲乙丙丁戊己庚辛壬癸")
VALID_BRANCHES = set("子丑寅卯辰巳午未申酉戌亥")

SHIO_TO_BRANCH = {
    "鼠": "子", "牛": "丑", "虎": "寅", "兔": "卯",
    "龍": "辰", "蛇": "巳", "馬": "午", "羊": "未",
    "猴": "申", "雞": "酉", "狗": "戌", "豬": "亥",
}

# 60-jiazi cycle: (stem, branch) index 0-59
_STEMS_L    = list("甲乙丙丁戊己庚辛壬癸")
_BRANCHES_L = list("子丑寅卯辰巳午未申酉戌亥")
JIAZI_60    = [(_STEMS_L[i % 10], _BRANCHES_L[i % 12]) for i in range(60)]
JIAZI_INDEX = {(s, b): i for i, (s, b) in enumerate(JIAZI_60)}


def _parse_md_data(md_path: Path) -> dict:
    data = {}
    in_data = False
    for line in md_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## DATA":
            in_data = True; continue
        if stripped.startswith("## ") and stripped != "## DATA":
            in_data = False
        if in_data and stripped.startswith("- ") and ":" in stripped:
            key, _, val = stripped[2:].partition(":")
            val = val.strip()
            if val.lower() not in ("null", "none", ""):
                data[key.strip()] = val
    return data


def _parse_pillar(s: str):
    """'干/支' -> (stem, branch). Return (None, None) kalau format salah."""
    parts = re.split(r"[/／]", s.strip())
    if len(parts) != 2:
        return None, None
    return parts[0].strip(), parts[1].strip()


def _parse_dayun(dayun_str: str) -> list:
    """'age:gz:tengod, ...' -> [(age, stem, branch), ...]"""
    result = []
    for entry in dayun_str.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) < 2:
            continue
        try:
            age = int(parts[0].strip())
        except ValueError:
            continue
        gz = parts[1].strip()
        if len(gz) >= 2 and gz[0] in VALID_STEMS and gz[1] in VALID_BRANCHES:
            result.append((age, gz[0], gz[1]))
    return result


# ── Check 1: shio_hz vs pilar_tahun branch ──────────────────────────────────

def check_shio_branch(data: dict) -> list[str]:
    shio = data.get("shio_hz", "").strip()
    pil  = data.get("pilar_tahun", "").strip()
    if not shio or not pil:
        return []
    expected = SHIO_TO_BRANCH.get(shio)
    if not expected:
        return [f"shio_hz '{shio}' tidak dikenal — bukan salah satu dari 12 shio"]
    _, branch = _parse_pillar(pil)
    if branch and branch != expected:
        return [
            f"SHIO MISMATCH: shio_hz '{shio}' → branch wajib '{expected}', "
            f"tapi pilar_tahun='{pil}' branch='{branch}'. "
            f"Kolom TAHUN di BaZi grid adalah kolom PALING KANAN — cek ulang."
        ]
    return []


# ── Check 2+3: valid 天干 / 地支 ─────────────────────────────────────────────

def check_valid_chars(data: dict) -> list[str]:
    errors = []
    for field in ("pilar_tahun", "pilar_bulan", "pilar_hari", "pilar_jam"):
        val = data.get(field, "")
        if not val:
            continue
        stem, branch = _parse_pillar(val)
        if stem is None:
            errors.append(f"{field}='{val}' format salah — wajib '干/支' (e.g. 甲/子)")
            continue
        if stem not in VALID_STEMS:
            errors.append(f"{field} stem '{stem}' bukan 天干 valid [甲乙丙丁戊己庚辛壬癸]")
        if branch not in VALID_BRANCHES:
            errors.append(f"{field} branch '{branch}' bukan 地支 valid [子丑寅卯辰巳午未申酉戌亥]")
    return errors


# ── Check 4: da_yun intervals +10 tahun ─────────────────────────────────────

def check_dayun_intervals(data: dict) -> list[str]:
    dayun_str = data.get("da_yun", "")
    if not dayun_str:
        return []
    cycles = _parse_dayun(dayun_str)
    if len(cycles) < 2:
        return []
    errors = []
    for i in range(1, len(cycles)):
        gap = cycles[i][0] - cycles[i-1][0]
        if gap != 10:
            errors.append(
                f"da_yun interval bukan 10 tahun: cycle {i} age={cycles[i][0]} "
                f"vs cycle {i-1} age={cycles[i-1][0]} (gap={gap}). "
                f"Da Yun selalu 10 tahun per cycle — cek foto Da Yun table."
            )
    return errors


# ── Check 5: pilar_bulan vs da_yun[0] dalam 60-jiazi ────────────────────────

def check_bulan_dayun(data: dict) -> list[str]:
    pil_bulan = data.get("pilar_bulan", "").strip()
    dayun_str = data.get("da_yun", "").strip()
    arah      = (data.get("da_yun_arah") or "").strip()
    if not pil_bulan or not dayun_str or not arah:
        return []

    stem_b, branch_b = _parse_pillar(pil_bulan)
    if not stem_b or stem_b not in VALID_STEMS or branch_b not in VALID_BRANCHES:
        return []

    bulan_idx = JIAZI_INDEX.get((stem_b, branch_b))
    if bulan_idx is None:
        return []

    cycles = _parse_dayun(dayun_str)
    if not cycles:
        return []

    dy0_stem, dy0_branch = cycles[0][1], cycles[0][2]
    dy0_idx = JIAZI_INDEX.get((dy0_stem, dy0_branch))
    if dy0_idx is None:
        return []

    expected_idx = (bulan_idx + 1) % 60 if "順" in arah else (bulan_idx - 1) % 60
    exp_s, exp_b = JIAZI_60[expected_idx]

    if dy0_idx != expected_idx:
        return [
            f"PILAR MISMATCH: pilar_bulan='{pil_bulan}' + {arah} → da_yun pertama "
            f"seharusnya '{exp_s}/{exp_b}' (1 langkah di 60-jiazi), "
            f"tapi da_yun[0]='{dy0_stem}/{dy0_branch}'. "
            f"Kemungkinan pilar_bulan atau Da Yun terbaca salah — cek foto BaZi grid "
            f"(kolom BULAN = kolom ke-2 dari kanan)."
        ]
    return []


# ── Main ──────────────────────────────────────────────────────────────────────

def run(subject_id: str) -> int:
    md_path = DATA_DIR / f"{subject_id}.md"
    if not md_path.exists():
        print(f"[validate_bazi] MD tidak ditemukan: {md_path}")
        return 2

    data   = _parse_md_data(md_path)
    errors = []
    errors += check_valid_chars(data)
    errors += check_shio_branch(data)
    errors += check_dayun_intervals(data)
    errors += check_bulan_dayun(data)

    print(f"\n[validate_bazi] subject_id={subject_id}")
    if errors:
        print(f"   FAIL — {len(errors)} error:")
        for e in errors:
            print(f"   x {e}")
        print(
            f"\n   Hint: BaZi grid dibaca KANAN ke KIRI = 年/月/日/時\n"
            f"   Label Ten God di baris atas tiap kolom = konfirmasi posisi.\n"
        )
        return 2

    print(f"   PASS — shio/branch, 天干地支, Da Yun intervals, bulan<->da_yun[0] semua konsisten.\n")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_bazi.py <subject_id>")
        sys.exit(2)
    sys.exit(run(sys.argv[1]))
