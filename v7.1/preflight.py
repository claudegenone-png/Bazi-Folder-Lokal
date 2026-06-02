"""V7.1 Pre-build validator — runs BEFORE build_pdf.py main work to catch:
1. marriage_cocok / marriage_hindari shape errors (invalid shios, overlap, count mismatch)
2. 5-elemen BaZi sum != 8 (4-pillar count constraint)
3. shio_hz vs year_branch inconsistency
4. Missing critical fields (ming_gong palace insight)
5. ** literal leak in rendered HTML (post-render check, hook from build_pdf)

Exit code:
  0 = pass (build can proceed)
  1 = warnings only (printed, build proceeds)
  2 = hard fail (build aborts)

Usage:
  python preflight.py {subject_id}
  python preflight.py {subject_id} --post-render

Auto-invoked by build_pdf.py at Step 0.5 (after MD parse, before subject build).
"""
import sys, re, json
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "subjects"
BUILD_DIR = ROOT / "_build"

# Nama subjek SAMPEL yang pernah jadi hardcode di template. Kalau muncul di render
# subjek LAIN = bukti template hardcode bocor (bleed). Post-render guard.
# Catatan: (1) cek ini skip blok komentar/style/script, jadi "Michele" di komentar
# template tidak ke-flag; (2) nama subjek AKTIF di-exclude saat runtime (lihat
# post_render_check_html) supaya subjek yg memang bernama "Leonardo" tidak false-positive.
# HANYA nama-subjek unik (bukan nilai field generik spt "Tanah Gunung"/"戌 Anjing").
SAMPLE_NAMES = ["Leonardo", "莊小敏", "Zhuang Xiao Min", "Michele"]

VALID_BRANCHES = set("子丑寅卯辰巳午未申酉戌亥")
SHIO_HZ_TO_BRANCH = {
    "鼠": "子", "牛": "丑", "虎": "寅", "兔": "卯",
    "龍": "辰", "蛇": "巳", "馬": "午", "羊": "未",
    "猴": "申", "雞": "酉", "狗": "戌", "豬": "亥",
}
PALACE_KEYS = ["ming_gong","xiongdi","fuqi","zinu","caibo","jie_e",
               "qianyi","puyi","guanlu","tianzhai","fude","fumu"]


def parse_md_full(md_text: str) -> dict:
    """Parse MD with section awareness.

    Returns dict with:
    - flat top-level fields as `key: value`
    - palace insights as `palace_{name}_insight: value` + `palace_{name}_action: value`
    """
    out = {}
    current_section = None  # e.g. "ming_gong"
    for line in md_text.split("\n"):
        # Detect palace section header: "ming_gong:" (no value after colon, top-level)
        m_sect = re.match(r"^([a-z_]+):\s*$", line)
        if m_sect:
            sect = m_sect.group(1)
            if sect in PALACE_KEYS:
                current_section = sect
                continue
            else:
                current_section = None  # other section types reset

        # Match "- key: value" pairs
        m_kv = re.match(r"^\s*-\s*([a-z_0-9]+)\s*:\s*(.*)$", line)
        if m_kv:
            k, v = m_kv.group(1), m_kv.group(2).strip()
            if v.lower() in ("null", "none", ""):
                v = None
            # If we're inside a palace section, namespace the key
            if current_section and k in ("insight", "action", "star"):
                out[f"palace_{current_section}_{k}"] = v
            else:
                out[k] = v
                # Other top-level kv resets section scope (e.g. once we hit non-palace fields)
                if k not in ("insight", "action", "star"):
                    pass
        elif line.strip() and not line.startswith("#") and not line.startswith("-"):
            # Non-key prose line → section likely ended
            if current_section and "###" in line:
                current_section = None
    return out


def check_marriage_shape(data: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    cocok = data.get("marriage_cocok")
    hindari = data.get("marriage_hindari")

    def parse_list(v):
        if not v: return []
        return [s.strip() for s in re.split(r"[,\s/]+", str(v)) if s.strip()]

    cocok_l = parse_list(cocok)
    hindari_l = parse_list(hindari)

    if not cocok_l and not hindari_l:
        return errors, warnings

    for b in cocok_l:
        if b in SHIO_HZ_TO_BRANCH:
            errors.append(f"marriage_cocok contains shio-hanzi '{b}' — should be branch '{SHIO_HZ_TO_BRANCH[b]}'")
        elif b not in VALID_BRANCHES:
            errors.append(f"marriage_cocok invalid entry '{b}' — must be one of 12 branches")
    for b in hindari_l:
        if b in SHIO_HZ_TO_BRANCH:
            errors.append(f"marriage_hindari contains shio-hanzi '{b}' — should be branch '{SHIO_HZ_TO_BRANCH[b]}'")
        elif b not in VALID_BRANCHES:
            errors.append(f"marriage_hindari invalid entry '{b}' — must be one of 12 branches")

    overlap = set(cocok_l) & set(hindari_l)
    if overlap:
        errors.append(f"marriage_cocok ∩ marriage_hindari overlap: {overlap}")

    # Tafsir prose existence (field name is `marriage_cocok_tafsir` without _id suffix)
    cocok_tafsir = data.get("marriage_cocok_tafsir") or data.get("marriage_cocok_tafsir_id")
    hindari_tafsir = data.get("marriage_hindari_tafsir") or data.get("marriage_hindari_tafsir_id")
    if cocok_l and not cocok_tafsir:
        warnings.append(f"marriage_cocok has {len(cocok_l)} shios but no tafsir prose")
    if hindari_l and not hindari_tafsir:
        warnings.append(f"marriage_hindari has {len(hindari_l)} shios but no tafsir prose")

    # Tier label consistency: marriage_cocok_relationships should have one tier label per cocok shio
    rels = data.get("marriage_cocok_relationships") or ""
    if cocok_l and rels:
        # Format: "子:大吉, 巳:大吉, 酉:大吉"
        tier_entries = [e.strip() for e in rels.split(",") if ":" in e]
        rel_branches = {e.split(":")[0].strip() for e in tier_entries}
        cocok_set = set(cocok_l)
        missing = cocok_set - rel_branches
        extra = rel_branches - cocok_set
        if missing:
            warnings.append(f"marriage_cocok_relationships missing tier label for: {missing}")
        if extra:
            warnings.append(f"marriage_cocok_relationships has extra entries not in cocok list: {extra}")

    return errors, warnings


def check_wuxing_sum(data: dict) -> list[str]:
    keys = ["wuxing_jin","wuxing_shui","wuxing_mu","wuxing_huo","wuxing_tu"]
    vals = []
    for k in keys:
        v = data.get(k)
        if v is None:
            return []
        try:
            vals.append(int(re.sub(r"\D","",str(v)) or "0"))
        except Exception:
            return []
    total = sum(vals)
    if total < 6 or total > 12:
        return [f"5-elemen sum = {total} (expected 7-9 for BaZi 4-pillar) — {dict(zip(keys, vals))}"]
    return []


def check_shio_year_branch(data: dict) -> list[str]:
    shio = (data.get("shio_hz") or "").strip()
    yr = (data.get("pilar_tahun") or "").strip()
    if not shio or not yr:
        return []
    yr_clean = re.sub(r"[^一-鿿]", "", yr)
    if len(yr_clean) < 2:
        return []
    yr_branch = yr_clean[-1]
    if shio not in SHIO_HZ_TO_BRANCH:
        return []
    expected = SHIO_HZ_TO_BRANCH[shio]
    if expected != yr_branch:
        return [f"shio_hz '{shio}' implies year branch '{expected}', but pilar_tahun is '{yr}' (branch={yr_branch})"]
    return []


def check_critical_fields(data: dict) -> list[str]:
    errors = []
    if not data.get("palace_ming_gong_insight"):
        errors.append("CRITICAL: ming_gong palace insight missing — V7.1 page 16 (Diri) requires this prose. STOP build.")
    return errors


# Pattern set: (regex, category, description)
LEAK_PATTERNS = [
    (r'\*\*[^*]+\*\*',          "markdown",     "raw ** bold literal (md_inline lupa)"),
    (r'\[\[[^\]]+\]\]',        "markdown",     "raw [[hanzi]] literal (hanzi_to_span lupa)"),
    (r'(?<![=&!])\|\|(?![=&!])',  "separator",    "raw || paragraph separator (split lupa)"),
    (r'\(verbatim[^)]*\)',        "source-attr",  "(verbatim ...) attribution leak"),
    (r'\(V\d+\.\d+\)',         "source-attr",  "(V2.5)/(Vn.n) attribution leak"),
    (r'\bFoto V\d',               "source-attr",  "Foto V<digit> attribution leak"),
    (r'dari foto terlihat',         "source-attr",  "'dari foto terlihat' phrase leak"),
    (r'\(tulis di sini\)',        "placeholder",  "template placeholder leak"),
    # v7.4: MICHELE/LinRuYi sample-data leak (field missing -> no substitution)
    (r'Lin Ru Yi',                "sample-leak",  "MICHELE/LinRuYi sample identity leak"),
    (r'Yi Hai . 1995',            "sample-leak",  "sample lunar date (1995) leak"),
    (r'28\.6%',                   "sample-leak",  "hardcoded sample wuxing percent leak"),
    (r'辛金 cenderung lemah',      "sample-leak",  "hardcoded sample DM insight leak"),
]

def post_render_check_html(subject_id: str) -> list[tuple]:
    """After render, scan _build/{id}/*.html for multiple leak patterns.
    Returns list of (file, line, category, description, excerpt)."""
    import re as _re
    issues = []
    build_dir = BUILD_DIR / subject_id
    if not build_dir.exists():
        return issues
    compiled = [(_re.compile(p), cat, desc) for p, cat, desc in LEAK_PATTERNS]
    # Exclude nama subjek aktif dari daftar sample (subjek yg memang bernama "Leonardo" dll
    # tidak boleh ke-flag sebagai bleed). Ambil nama dari MD.
    _cur_name = ""
    try:
        _mdp = DATA_DIR / f"{subject_id}.md"
        if _mdp.exists():
            _m = _re.search(r"^- *nama *: *(.+)$", _mdp.read_text(encoding="utf-8"), _re.M)
            if _m:
                _cur_name = _m.group(1).strip().lower()
    except Exception:
        pass
    sample_names = [n for n in SAMPLE_NAMES
                    if n.lower() not in _cur_name and (_cur_name == "" or _cur_name not in n.lower())]
    for html in build_dir.glob("page_*.html"):
        try:
            text = html.read_text(encoding="utf-8")
        except Exception:
            continue
        in_style = False
        in_script = False
        for ln, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            # Skip CSS + JS blocks (false positives)
            if "<style" in line.lower(): in_style = True
            if "</style" in line.lower(): in_style = False; continue
            if "<script" in line.lower(): in_script = True
            if "</script" in line.lower(): in_script = False; continue
            if in_style or in_script: continue
            # Skip HTML comments
            if stripped.startswith("<!--") and stripped.endswith("-->"): continue
            for regex, cat, desc in compiled:
                if regex.search(line):
                    excerpt = stripped[:140]
                    issues.append((html.name, ln, cat, desc, excerpt))
                    break  # 1 issue per line max
            # Anti-bleed: nama subjek sampel (dari template hardcode) bocor ke subjek lain
            for _nm in sample_names:
                if _nm in line:
                    issues.append((html.name, ln, "BLEED",
                                   f"nama/data sampel '{_nm}' muncul (template hardcode bocor?)",
                                   stripped[:140]))
                    break
            # Kartu zona Yang Zhai dgn hanzi '?' (label tak ter-map ke 6 zona standar)
            if 'yz-zone-hz">?' in line.replace(" ", ""):
                issues.append((html.name, ln, "ZONE?",
                               "kartu zona hanzi '?' (label tak ke-map zona standar)",
                               stripped[:140]))
    return issues


def check_palace_completeness(data: dict) -> list[str]:
    """Warn kalau insight 12 istana kelihatan diringkas/stub (terlalu pendek).
    Narasi 詳細解說 ZiWei biasanya panjang (300-700 char Indo); insight pendek
    biasanya tanda diringkas, BUKAN diterjemah penuh dari foto. Mencegah
    ketidaklengkapan lolos ke PDF tanpa ketahuan (kasus subjek CS 2026-05-21)."""
    warnings = []
    SHORT = 220  # char; di bawah ini insight dicurigai diringkas
    present = 0
    for pal in PALACE_KEYS:
        ins = (data.get(f"palace_{pal}_insight") or "").strip()
        if not ins or ins in ("—", "-", "—"):
            continue
        present += 1
        if len(ins) < SHORT:
            warnings.append(
                f"istana '{pal}' insight cuma {len(ins)} char (dicurigai DIRINGKAS) "
                f"-> WAJIB terjemah PENUH & faithful dari layar 詳細解說 foto, jangan ringkas")
    if 0 < present < 12:
        warnings.append(
            f"cuma {present}/12 istana punya insight -> pastikan semua 12 layar "
            f"詳細解說 terbaca (enhance kalau buram) & diterjemahkan")
    return warnings


def check_liunian_completeness(md_text: str) -> list:
    """Warn kalau prosa liu_nian (umur|ganzhi|prosa) terlalu pendek (dicurigai
    diringkas). Layar liu_nian panjang (puisi shensha + peringatan + watak);
    prosa pendek biasanya tanda diringkas. Cegah ketidaklengkapan ke PDF."""
    warnings = []
    SHORT = 400
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("- liu_nian_") and ":" in line:
            key, _, val = line[2:].partition(":")
            parts = val.split("|")
            if len(parts) >= 3:
                prosa = "|".join(parts[2:]).strip()
                if prosa and prosa not in ("—", "-") and len(prosa) < SHORT:
                    warnings.append(key.strip() + " prosa cuma " + str(len(prosa)) + " char (dicurigai DIRINGKAS) -> terjemah PENUH layar 流年 (puisi 神煞 + peringatan + watak), jangan ringkas")
    return warnings


def run(subject_id: str, post_render: bool = False) -> int:
    if post_render:
        issues = post_render_check_html(subject_id)
        print(f"\n[preflight V7.1 — post-render] subject_id={subject_id}")
        if issues:
            # Group by category
            by_cat = {}
            for f, ln, cat, desc, ex in issues:
                by_cat.setdefault(cat, []).append((f, ln, desc, ex))
            print(f"   ⚠ Found {len(issues)} leak(s) across {len(by_cat)} categories:")
            for cat, items in by_cat.items():
                print(f"\n   [{cat}] ({len(items)} hits)")
                for f, ln, desc, ex in items[:5]:  # show max 5 per cat
                    print(f"     - {f}:{ln} ({desc})")
                    print(f"       {ex}")
                if len(items) > 5:
                    print(f"     ... and {len(items)-5} more")
            print(f"\n   Action:")
            print(f"   - markdown leak → wrap tafsir field injection with _md_inline() in engines/render.py")
            print(f"   - separator leak → split prose on || before injection")
            print(f"   - source-attr leak → strip prefix from MD before write OR clean in render injection")
            print(f"   - placeholder leak → field missing in MD, fill or set null\n")
            return 1
        print(f"   OK — no markdown/separator/source-attr leak in rendered HTML.\n")
        return 0

    md_path = DATA_DIR / f"{subject_id}.md"
    if not md_path.exists():
        print(f"[preflight] MD file not found: {md_path}")
        return 2

    md_text = md_path.read_text(encoding="utf-8")
    data = parse_md_full(md_text)

    errors, warnings = [], []
    e, w = check_marriage_shape(data); errors += e; warnings += w
    errors += check_critical_fields(data)
    warnings += check_wuxing_sum(data)
    warnings += check_shio_year_branch(data)
    warnings += check_palace_completeness(data)
    warnings += check_liunian_completeness(md_text)

    print(f"\n[preflight V7.1] subject_id={subject_id}")
    print(f"   MD: {md_path.name} ({len(md_text):,} chars, {len(data)} fields)")

    if warnings:
        print(f"\n   ⚠ Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"     - {w}")

    if errors:
        print(f"\n   ✘ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"     - {e}")
        print(f"\n[preflight] FAIL — fix MD errors above before building.\n")
        return 2

    print(f"\n[preflight] PASS (warnings={len(warnings)}, errors=0)\n")
    return 1 if warnings else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: preflight.py <subject_id> [--post-render]")
        sys.exit(2)
    post = "--post-render" in sys.argv
    sys.exit(run(sys.argv[1], post_render=post))
