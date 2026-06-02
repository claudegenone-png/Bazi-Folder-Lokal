"""V7.1 audit decision-maker (triple-vote autonomous).

Reads 3-5 source JSON files (audit-blind, BaZi-specialist Tier 1, optional Tier 2 a+b),
plus main agent reading from MD, then applies voting logic to 19 high-risk fields.

Usage:
  python audit_decide.py {subject_id}            # Tier 1 (3 sources: main + blind + bazi)
  python audit_decide.py {subject_id} --tier2    # Tier 2 (5 sources: + bazi_tier2_a + bazi_tier2_b)

Exit codes:
  0 = all fields decided (PASS), prints JSON to stdout
  1 = STOP, some fields couldn't be decided. Detail di stderr + JSON di stdout.
  2 = error (missing input file, malformed JSON)

Input expected paths:
  data/subjects/{id}.md                                  (main agent reading)
  _AUDIT_LOGS/{id}_blind.json                            (audit-blind)
  _AUDIT_LOGS/{id}_bazi.json                             (BaZi-specialist Tier 1)
  _AUDIT_LOGS/{id}_bazi_tier2_a.json + _b.json           (Tier 2 only)

Output:
  _AUDIT_LOGS/{id}_decision.json                         (decisions + audit trail)
  stdout                                                  (PASS summary or STOP detail)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

# ============== CONFIG ==============

ROOT = Path(__file__).parent
SUBJECTS_DIR = ROOT / "data" / "subjects"
AUDIT_DIR = ROOT / "_AUDIT_LOGS"

ELEMENTS = list("金木水火土")
STEMS = list("甲乙丙丁戊己庚辛壬癸")
CONF_RANK = {"high": 3, "med": 2, "low": 1, "medium": 2, "h": 3, "m": 2, "l": 1}


def normalize_conf(c):
    """Normalize confidence value: numeric 0-1 → string label; else passthrough."""
    if isinstance(c, (int, float)):
        if c >= 0.85:
            return "high"
        elif c >= 0.6:
            return "med"
        else:
            return "low"
    if isinstance(c, str):
        return c.lower().strip()
    return "med"

# 19 high-risk fields
HIGH_RISK = {
    # 5 elements (single hanzi from 金木水火土)
    "yong_shen":  {"type": "element"},
    "xi_shen":    {"type": "element"},
    "xian_shen":  {"type": "element"},
    "chou_shen":  {"type": "element"},
    "ji_shen":    {"type": "element"},
    # 10 xiantian counts (integer 0-8)
    "xiantian_jia":  {"type": "int", "range": (0, 8)},
    "xiantian_yi":   {"type": "int", "range": (0, 8)},
    "xiantian_bing": {"type": "int", "range": (0, 8)},
    "xiantian_ding": {"type": "int", "range": (0, 8)},
    "xiantian_wu":   {"type": "int", "range": (0, 8)},
    "xiantian_ji":   {"type": "int", "range": (0, 8)},
    "xiantian_geng": {"type": "int", "range": (0, 8)},
    "xiantian_xin":  {"type": "int", "range": (0, 8)},
    "xiantian_ren":  {"type": "int", "range": (0, 8)},
    "xiantian_gui":  {"type": "int", "range": (0, 8)},
    # 4 canggan rows (1-3 hanzi from STEMS, comma or no-separator format)
    "canggan_tahun": {"type": "stem_list"},
    "canggan_bulan": {"type": "stem_list"},
    "canggan_hari":  {"type": "stem_list"},
    "canggan_jam":   {"type": "stem_list"},
}

# ============== INPUT LOADERS ==============

def load_main_md(md_path: Path) -> dict:
    """Parse main MD ## DATA section, extract high-risk fields with confidence='high' default.

    Main agent reading is treated as 1 source. Confidence defaults to 'med' since main
    didn't tag confidence in MD format. Optional `# conf: low` inline comment lowers it.
    """
    if not md_path.exists():
        raise FileNotFoundError(f"main MD not found: {md_path}")
    text = md_path.read_text(encoding="utf-8")
    # extract ## DATA section
    m = re.search(r"^##\s+DATA\s*\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S)
    if not m:
        raise ValueError(f"DATA section not found in {md_path}")
    data_text = m.group(1)

    fields = {}
    for line in data_text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        if key not in HIGH_RISK:
            continue
        # extract optional `# conf: X` inline tag
        conf = "med"  # default
        m_conf = re.search(r"#\s*conf:\s*(high|med|low)", val)
        if m_conf:
            conf = m_conf.group(1)
            val = re.sub(r"#\s*conf:.*$", "", val).strip()
        else:
            val = re.sub(r"\s+#.*$", "", val).strip()
        # strip [[..]] wrap
        val = re.sub(r"\[\[([^\]]+)\]\]", r"\1", val)
        if val.lower() in ("null", "", "none"):
            fields[key] = {"value": None, "confidence": conf}
            continue
        # type-aware parse
        spec = HIGH_RISK[key]
        if spec["type"] == "int":
            try:
                fields[key] = {"value": int(float(val)), "confidence": conf}
            except ValueError:
                fields[key] = {"value": None, "confidence": "low"}
        else:
            fields[key] = {"value": val, "confidence": conf}
    return fields


def load_audit_json(json_path: Path) -> dict:
    """Load audit JSON, normalize fields to standard schema.

    Audit-blind format has nested 'fields' with various structures:
      - simple {value, confidence, ...}
      - canggan as {value: {tahun: [...], bulan: [...], ...}, confidence}
      - xiantian_counts as {value: {甲膽: 0, ...}, confidence}
    Normalize all to flat fields[key] = {value, confidence}.
    """
    if not json_path.exists():
        return {}
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        sys.stderr.write(f"⚠ failed to parse {json_path}: {e}\n")
        return {}
    raw = data.get("fields", {})
    out = {}

    # 5-shen aliases — agen kadang pakai xiyong_*, wuxing_*, etc.
    # Mapping pinyin/english → hanzi
    PINYIN_TO_HANZI = {
        "mu": "木", "jin": "金", "shui": "水", "huo": "火", "tu": "土",
        "wood": "木", "metal": "金", "water": "水", "fire": "火", "earth": "土",
    }

    # Handle "xiyong_5elem" / "wuxing_5elem" / "5shen" packed string ("土火金水木")
    # Position 1=yong, 2=xi, 3=xian, 4=chou, 5=ji
    SHEN_ORDER = ["yong_shen", "xi_shen", "xian_shen", "chou_shen", "ji_shen"]
    for packed_key in ("xiyong_5elem", "wuxing_5elem", "5shen", "5elem", "shen_5"):
        if packed_key in raw:
            entry = raw[packed_key]
            packed_val = entry.get("value") if isinstance(entry, dict) else entry
            packed_conf = normalize_conf(entry.get("confidence", entry.get("conf", "med"))) if isinstance(entry, dict) else "med"
            if isinstance(packed_val, str):
                # extract 5-elemen hanzi in order
                hanzi_chars = [c for c in packed_val if c in ELEMENTS]
                if len(hanzi_chars) >= 5:
                    for i, target in enumerate(SHEN_ORDER):
                        if target not in out:
                            out[target] = {"value": hanzi_chars[i], "confidence": packed_conf}
            elif isinstance(packed_val, list):
                hanzi_chars = [c for c in packed_val if isinstance(c, str) and c in ELEMENTS]
                if len(hanzi_chars) >= 5:
                    for i, target in enumerate(SHEN_ORDER):
                        if target not in out:
                            out[target] = {"value": hanzi_chars[i], "confidence": packed_conf}
    shen_aliases = [
        ("yong_shen", ["yong_shen", "xiyong_yong", "wuxing_yong", "yong"]),
        ("xi_shen",   ["xi_shen", "xiyong_xi", "wuxing_xi", "xi"]),
        ("xian_shen", ["xian_shen", "xiyong_xian", "wuxing_xian", "xian"]),
        ("chou_shen", ["chou_shen", "xiyong_chou", "wuxing_chou", "chou"]),
        ("ji_shen",   ["ji_shen", "xiyong_ji", "wuxing_ji", "ji"]),
    ]
    for target, aliases in shen_aliases:
        if target in out:
            continue
        for alias in aliases:
            if alias in raw:
                entry = raw[alias]
                if isinstance(entry, dict):
                    val = entry.get("value")
                    conf = normalize_conf(entry.get("confidence", entry.get("conf", "med")))
                else:
                    val = entry
                    conf = "med"
                # pinyin → hanzi normalization
                if isinstance(val, str) and val.lower().strip() in PINYIN_TO_HANZI:
                    val = PINYIN_TO_HANZI[val.lower().strip()]
                out[target] = {"value": val, "confidence": conf}
                break

    # normalize xiantian — could be flat (xiantian_jia=0) or nested in xiantian_counts
    if "xiantian_counts" in raw:
        xt_entry = raw["xiantian_counts"]
        xt_value = xt_entry.get("value", {})
        xt_conf = xt_normalize_conf(entry.get("confidence", entry.get("conf", "med")))
        # map by stem name
        STEM_ORGAN = {
            "甲膽": "xiantian_jia", "乙肝": "xiantian_yi",
            "丙小腸": "xiantian_bing", "丁心": "xiantian_ding",
            "戊胃": "xiantian_wu", "己脾": "xiantian_ji",
            "庚大腸": "xiantian_geng", "辛肺": "xiantian_xin",
            "壬膀胱": "xiantian_ren", "癸腎": "xiantian_gui",
        }
        if isinstance(xt_value, dict):
            for organ_key, target_field in STEM_ORGAN.items():
                if organ_key in xt_value:
                    try:
                        out[target_field] = {
                            "value": int(xt_value[organ_key]),
                            "confidence": xt_conf,
                        }
                    except (ValueError, TypeError):
                        pass
    # also accept flat xiantian_jia etc (dict or scalar int)
    for stem in ("jia","yi","bing","ding","wu","ji","geng","xin","ren","gui"):
        key = f"xiantian_{stem}"
        if key in raw:
            entry = raw[key]
            try:
                if isinstance(entry, dict):
                    out[key] = {
                        "value": int(entry.get("value")),
                        "confidence": normalize_conf(entry.get("confidence", entry.get("conf", "med"))),
                    }
                else:
                    # scalar int
                    out[key] = {"value": int(entry), "confidence": "med"}
            except (ValueError, TypeError):
                pass

    # normalize canggan — could be canggan_tahun (flat string) or canggan (nested dict)
    if "canggan" in raw:
        cg_entry = raw["canggan"]
        cg_value = cg_entry.get("value", {})
        cg_conf = cg_normalize_conf(entry.get("confidence", entry.get("conf", "med")))
        if isinstance(cg_value, dict):
            for slot_audit, target_field in [
                ("tahun", "canggan_tahun"), ("bulan", "canggan_bulan"),
                ("hari", "canggan_hari"), ("jam", "canggan_jam"),
            ]:
                if slot_audit in cg_value:
                    v = cg_value[slot_audit]
                    if isinstance(v, list):
                        v = "".join(v)
                    out[target_field] = {"value": v, "confidence": cg_conf}
    # Pinyin polysyllable → hanzi tokenizer untuk canggan (e.g. "xinguiji" → "辛癸己")
    STEM_PINYIN = [
        ("jia", "甲"), ("yi", "乙"), ("bing", "丙"), ("ding", "丁"),
        ("wu", "戊"), ("ji", "己"), ("geng", "庚"), ("xin", "辛"),
        ("ren", "壬"), ("gui", "癸"),
    ]
    STEM_PINYIN.sort(key=lambda x: -len(x[0]))  # longest first for greedy match

    def pinyin_to_canggan_hanzi(s: str) -> str:
        """xinguiji → 辛癸己. Returns empty if no match."""
        s = s.lower().strip()
        result = []
        i = 0
        while i < len(s):
            matched = False
            for pinyin, hanzi in STEM_PINYIN:
                if s[i:i+len(pinyin)] == pinyin:
                    result.append(hanzi)
                    i += len(pinyin)
                    matched = True
                    break
            if not matched:
                return ""  # unparseable
        return "".join(result)

    # canggan aliases: canggan_*, renyuan_*, year_canggan suffix, with tahun/year, bulan/month
    canggan_aliases = []
    for prefix in ("canggan", "renyuan"):
        for slot, target_field in [
            ("tahun", "canggan_tahun"), ("bulan", "canggan_bulan"),
            ("hari", "canggan_hari"), ("jam", "canggan_jam"),
            ("year", "canggan_tahun"), ("month", "canggan_bulan"),
            ("day", "canggan_hari"), ("hour", "canggan_jam"),
        ]:
            canggan_aliases.append((f"{prefix}_{slot}", target_field))
    # Suffix order: year_canggan, month_canggan, etc.
    for suffix in ("canggan", "renyuan"):
        for slot, target_field in [
            ("year", "canggan_tahun"), ("month", "canggan_bulan"),
            ("day", "canggan_hari"), ("hour", "canggan_jam"),
            ("tahun", "canggan_tahun"), ("bulan", "canggan_bulan"),
            ("hari", "canggan_hari"), ("jam", "canggan_jam"),
        ]:
            canggan_aliases.append((f"{slot}_{suffix}", target_field))
    for key, target_field in canggan_aliases:
        if key in raw and target_field not in out:
            entry = raw[key]
            if not isinstance(entry, dict):
                v = entry
                conf = "high"  # scalar inputs assume agent confident (no conf field provided)
            else:
                v = entry.get("value")
                conf = normalize_conf(entry.get("confidence", entry.get("conf", "med")))
            if isinstance(v, list):
                v = "".join(v)
            # Convert pinyin polysyllable → hanzi if needed
            if isinstance(v, str) and v.strip():
                # Check if already has hanzi stems
                has_hanzi = any(c in STEMS for c in v)
                if not has_hanzi:
                    converted = pinyin_to_canggan_hanzi(v)
                    if converted:
                        v = converted
            out[target_field] = {"value": v, "confidence": conf}

    # graceful scalar handling: if any field is scalar (not dict), wrap with med conf
    for key in list(raw.keys()):
        if key in HIGH_RISK and key not in out and not isinstance(raw[key], dict):
            v = raw[key]
            if isinstance(v, list):
                v = v[0] if v else None
            out[key] = {"value": v, "confidence": "med"}

    return out


# ============== NORMALIZATION ==============

def normalize_value(value, field_spec):
    """Canonicalize value for comparison purposes.

    - element: keep as 1-char str (or None)
    - int: convert to int
    - stem_list: sort and join hanzi (canggan order can vary; we treat 辛癸己 same as 己癸辛 for comparison)
    """
    if value is None:
        return None
    t = field_spec["type"]
    if t == "element":
        # handle list input: ["金","土"] → "金"
        if isinstance(value, list):
            for v in value:
                if isinstance(v, str) and v.strip() and v.strip()[0] in ELEMENTS:
                    return v.strip()[0]
            return None
        s = str(value).strip()
        # extract first valid element hanzi (skip brackets/quotes/spaces)
        for c in s:
            if c in ELEMENTS:
                return c
        return None
    if t == "int":
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    if t == "stem_list":
        # remove punctuation/space, keep only stem hanzi
        s = re.sub(r"[^甲乙丙丁戊己庚辛壬癸]", "", str(value))
        # NOT sort — order matters for canggan (人元 main/middle/余 ordering)
        return s
    return value


def is_valid(value, field_spec):
    """Check if value passes Step 3 safety net."""
    if value is None:
        return False
    t = field_spec["type"]
    if t == "element":
        return value in ELEMENTS
    if t == "int":
        lo, hi = field_spec.get("range", (-9999, 9999))
        try:
            iv = int(value)
            return lo <= iv <= hi
        except (ValueError, TypeError):
            return False
    if t == "stem_list":
        return all(c in STEMS for c in value) and 1 <= len(value) <= 3
    return False


# ============== VOTE LOGIC ==============

def vote(field_name, readings):
    """Apply 3-step voting to readings list for a single field.

    readings: list of {value, confidence, source}
    Returns: {decision, value, reason, audit_trail}
    """
    spec = HIGH_RISK[field_name]
    audit_trail = [
        {"source": r.get("source"), "value": r.get("value"),
         "confidence": r.get("confidence")}
        for r in readings
    ]

    # Filter null reads (treat as no-vote, not as a value)
    valid = [r for r in readings if r.get("value") is not None]
    if len(valid) < 2:
        return {
            "decision": "STOP", "value": None,
            "reason": f"insufficient_readings ({len(valid)} non-null out of {len(readings)})",
            "audit_trail": audit_trail,
        }

    # Group by normalized value
    groups: dict[str, list[dict]] = {}
    for r in valid:
        norm = normalize_value(r["value"], spec)
        if norm is None:
            continue
        key = str(norm)
        groups.setdefault(key, []).append(r)

    if not groups:
        return {
            "decision": "STOP", "value": None,
            "reason": "all_readings_unparseable",
            "audit_trail": audit_trail,
        }

    # Find largest group
    sorted_groups = sorted(groups.items(), key=lambda x: -len(x[1]))
    top_key, top_readings = sorted_groups[0]

    # STEP 1: Agreement check
    if len(top_readings) < 2:
        return {
            "decision": "STOP", "value": None,
            "reason": f"no_agreement (each reading different across {len(valid)} sources)",
            "audit_trail": audit_trail,
        }

    # STEP 2: Confidence check
    maj_max = max((CONF_RANK.get(r.get("confidence"), 0) for r in top_readings), default=0)
    minority = [r for r in valid if r not in top_readings]
    min_max = max((CONF_RANK.get(r.get("confidence"), 0) for r in minority), default=0)

    if min_max > maj_max:
        return {
            "decision": "STOP", "value": None,
            "reason": f"minority_more_confident (majority max={maj_max}, minority max={min_max})",
            "audit_trail": audit_trail,
        }
    # UNANIMITY OVERRIDE: kalau semua agen yang non-null sepakat (no minority disagree)
    # dan min confidence >= MED, PASS — unanimity lebih kuat dari conf label per-cell.
    is_unanimous = (len(minority) == 0 and len(top_readings) >= 2)
    maj_min = min((CONF_RANK.get(r.get("confidence"), 0) for r in top_readings), default=0)
    if is_unanimous and maj_min >= CONF_RANK["med"]:
        decided_value = normalize_value(top_readings[0]["value"], spec)
        if is_valid(decided_value, spec):
            return {
                "decision": "PASS",
                "value": decided_value,
                "reason": f"unanimous {len(top_readings)}/{len(valid)} agree, min_conf={maj_min}",
                "audit_trail": audit_trail,
            }
    if maj_max < CONF_RANK["high"]:
        return {
            "decision": "STOP", "value": None,
            "reason": f"majority_too_uncertain (no high-confidence reading in majority; max={maj_max})",
            "audit_trail": audit_trail,
        }

    # STEP 3: Safety net
    decided_value = normalize_value(top_readings[0]["value"], spec)
    if not is_valid(decided_value, spec):
        return {
            "decision": "STOP", "value": None,
            "reason": f"invalid_value ({decided_value!r} fails {spec['type']} safety check)",
            "audit_trail": audit_trail,
        }

    return {
        "decision": "PASS",
        "value": decided_value,
        "reason": f"{len(top_readings)}/{len(valid)} majority, max_conf={maj_max}",
        "audit_trail": audit_trail,
    }


# ============== POST-PROCESS RULES ==============

SHEN_FIELDS = ["yong_shen", "xi_shen", "xian_shen", "chou_shen", "ji_shen"]


def enforce_5shen_unique(decisions: dict, stops: list) -> tuple[dict, list]:
    """5-shen wajib 5 elemen unik dari 金木水火土. Logika:

    - Kalau 4 PASS unik + 1 STOP → derive missing element ke field yang STOP.
    - Kalau ada duplicate (mis. yong=木, xi=木) → demote ke STOP, flag manual verify.
    """
    pass_vals = {f: decisions[f]["value"] for f in SHEN_FIELDS
                 if f in decisions and decisions[f]["decision"] == "PASS"
                 and decisions[f]["value"] in ELEMENTS}
    stop_fields = [f for f in SHEN_FIELDS
                   if f in decisions and decisions[f]["decision"] == "STOP"]

    # Detect duplicates among PASS (group fields by element value)
    by_value: dict[str, list[str]] = {}
    for f, v in pass_vals.items():
        by_value.setdefault(v, []).append(f)

    # For each duplicate group: keep field with highest max-confidence in audit_trail; demote others
    def max_conf(field):
        trail = decisions[field].get("audit_trail", [])
        return max((CONF_RANK.get(r.get("confidence"), 0) for r in trail), default=0)

    for v, fields_with_v in by_value.items():
        if len(fields_with_v) < 2:
            continue
        # Sort by max conf desc; keep first, demote rest
        ranked = sorted(fields_with_v, key=lambda f: -max_conf(f))
        keeper = ranked[0]
        losers = ranked[1:]
        for f in losers:
            decisions[f] = {
                "decision": "STOP", "value": None,
                "reason": f"5shen_duplicate_detected ({f} & {keeper} both = {v}; demoting lower-conf {f})",
                "audit_trail": decisions[f].get("audit_trail", []),
            }
            if f not in stops:
                stops.append(f)
            pass_vals.pop(f, None)
            if f not in stop_fields:
                stop_fields.append(f)

    # Auto-derive missing element if 4 PASS unique + exactly 1 STOP
    used = set(pass_vals.values())
    missing = [e for e in ELEMENTS if e not in used]
    if len(pass_vals) == 4 and len(stop_fields) == 1 and len(missing) == 1:
        target = stop_fields[0]
        derived = missing[0]
        decisions[target] = {
            "decision": "PASS",
            "value": derived,
            "reason": f"auto_derived (4 of 5 shen known, missing element from 五行 must be {derived})",
            "audit_trail": decisions[target].get("audit_trail", []),
        }
        if target in stops:
            stops.remove(target)

    return decisions, stops


# ============== MAIN ==============

def run_test_mode(test_id: str, json_paths: list[Path]):
    """Test mode: 3 JSON paths langsung, bypass MD/blind. Untuk testing per foto."""
    sources = []
    for i, p in enumerate(json_paths):
        f = load_audit_json(p)
        if f:
            sources.append((f"agent-{chr(65+i)}", f))  # agent-A, agent-B, agent-C
        else:
            sys.stderr.write(f"⚠ failed to load {p}\n")

    if len(sources) < 2:
        sys.stderr.write(f"⚠ only {len(sources)} sources loaded, need 2+\n")
        sys.exit(2)

    decisions = {}
    stops = []
    for field_name in HIGH_RISK:
        readings = []
        for src_name, src_fields in sources:
            if field_name in src_fields:
                r = src_fields[field_name].copy()
                r["source"] = src_name
                readings.append(r)
        if not readings:
            continue
        result = vote(field_name, readings)
        decisions[field_name] = result
        if result["decision"] == "STOP":
            stops.append(field_name)

    # POST-PROCESS: 5-shen unique constraint
    # Rule: yong/xi/xian/chou/ji_shen MUST be 5 different elements from 金木水火土.
    # - If 4 PASS (unique) + 1 STOP → auto-derive 5th as missing element
    # - If duplicate detected among PASS → flag as STOP (likely misread)
    decisions, stops = enforce_5shen_unique(decisions, stops)

    out_path = AUDIT_DIR / f"test_{test_id}_decision.json"
    AUDIT_DIR.mkdir(exist_ok=True)
    out_path.write_text(json.dumps({
        "test_id": test_id,
        "sources": [s[0] for s in sources],
        "decisions": decisions,
        "stops": stops,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print as compact table
    pass_count = sum(1 for d in decisions.values() if d["decision"] == "PASS")
    sys.stdout.write(f"\n=== TEST {test_id} ===\n")
    sys.stdout.write(f"Sources: {', '.join(s[0] for s in sources)}\n\n")
    sys.stdout.write(f"{'Field':<20} {'Agent A':<12} {'Agent B':<12} {'Agent C':<12} {'Decision':<8} {'Value':<10}\n")
    sys.stdout.write("-" * 84 + "\n")
    for field_name in HIGH_RISK:
        if field_name not in decisions:
            continue
        d = decisions[field_name]
        # pull readings per source
        readings_by_src = {r["source"]: r for r in d["audit_trail"]}
        a = readings_by_src.get("agent-A", {})
        b = readings_by_src.get("agent-B", {})
        c = readings_by_src.get("agent-C", {})
        def fmt(r):
            v = r.get("value", "—")
            cf_raw = r.get("confidence", "")
            cf = str(cf_raw)[:1].upper() if cf_raw else ""
            return f"{v}({cf})" if v not in (None, "—") else "—"
        decision_mark = "✅" if d["decision"] == "PASS" else "🛑"
        sys.stdout.write(f"{field_name:<20} {fmt(a):<12} {fmt(b):<12} {fmt(c):<12} {decision_mark:<8} {d.get('value', '—')!r}\n")

    sys.stdout.write(f"\nSummary: {pass_count}/{len(decisions)} PASS, {len(stops)} STOP\n")
    if stops:
        sys.stdout.write(f"STOP fields: {', '.join(stops)}\n")
        for fn in stops:
            sys.stdout.write(f"  • {fn}: {decisions[fn]['reason']}\n")

    sys.exit(0 if not stops else 1)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage:\n")
        sys.stderr.write("  audit_decide.py {subject_id} [--tier2]\n")
        sys.stderr.write("  audit_decide.py --test {test_id} {jsonA} {jsonB} {jsonC}\n")
        sys.exit(2)

    if sys.argv[1] == "--test":
        if len(sys.argv) < 6:
            sys.stderr.write("usage: audit_decide.py --test {test_id} {jsonA} {jsonB} {jsonC}\n")
            sys.exit(2)
        test_id = sys.argv[2]
        paths = [Path(p) for p in sys.argv[3:]]
        run_test_mode(test_id, paths)
        return

    subject_id = sys.argv[1]
    tier2 = "--tier2" in sys.argv[2:]

    md_path = SUBJECTS_DIR / f"{subject_id}.md"
    blind_path = AUDIT_DIR / f"{subject_id}_blind.json"
    bazi_path = AUDIT_DIR / f"{subject_id}_bazi.json"
    bazi_t2a = AUDIT_DIR / f"{subject_id}_bazi_tier2_a.json"
    bazi_t2b = AUDIT_DIR / f"{subject_id}_bazi_tier2_b.json"

    sources = []
    try:
        main_fields = load_main_md(md_path)
        sources.append(("main", main_fields))
    except Exception as e:
        sys.stderr.write(f"⚠ skip main: {e}\n")

    blind_fields = load_audit_json(blind_path)
    if blind_fields:
        sources.append(("audit-blind", blind_fields))
    bazi_fields = load_audit_json(bazi_path)
    if bazi_fields:
        sources.append(("bazi-specialist", bazi_fields))

    if tier2:
        for tag, p in [("tier2-a", bazi_t2a), ("tier2-b", bazi_t2b)]:
            f = load_audit_json(p)
            if f:
                sources.append((tag, f))

    if len(sources) < 3:
        sys.stderr.write(f"⚠ only {len(sources)} sources loaded, need 3+\n")
        sys.exit(2)

    # Vote per field
    decisions = {}
    stops = []
    for field_name in HIGH_RISK:
        readings = []
        for src_name, src_fields in sources:
            if field_name in src_fields:
                r = src_fields[field_name].copy()
                r["source"] = src_name
                readings.append(r)
        if not readings:
            decisions[field_name] = {
                "decision": "SKIP", "value": None,
                "reason": "no source has this field", "audit_trail": [],
            }
            continue
        result = vote(field_name, readings)
        decisions[field_name] = result
        if result["decision"] == "STOP":
            stops.append(field_name)

    # POST-PROCESS: 5-shen unique constraint (auto-derive missing + flag duplicate)
    decisions, stops = enforce_5shen_unique(decisions, stops)

    # Output
    out_path = AUDIT_DIR / f"{subject_id}_decision.json"
    AUDIT_DIR.mkdir(exist_ok=True)
    out = {
        "subject_id": subject_id,
        "tier": 2 if tier2 else 1,
        "sources": [s[0] for s in sources],
        "decisions": decisions,
        "stops": stops,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print summary
    pass_count = sum(1 for d in decisions.values() if d["decision"] == "PASS")
    stop_count = len(stops)
    skip_count = sum(1 for d in decisions.values() if d["decision"] == "SKIP")
    sys.stdout.write(f"=== Audit Decision (Tier {2 if tier2 else 1}) — {subject_id} ===\n")
    sys.stdout.write(f"  PASS: {pass_count} fields\n")
    sys.stdout.write(f"  STOP: {stop_count} fields\n")
    sys.stdout.write(f"  SKIP: {skip_count} fields (no source had data)\n")
    sys.stdout.write(f"  Sources: {', '.join(s[0] for s in sources)}\n")
    sys.stdout.write(f"  Output: {out_path}\n")

    if stops:
        sys.stdout.write("\n--- STOP fields detail ---\n")
        for fn in stops:
            d = decisions[fn]
            sys.stdout.write(f"\n[{fn}] reason: {d['reason']}\n")
            for r in d["audit_trail"]:
                sys.stdout.write(f"  • {r['source']:20s} value={r['value']!r:15} conf={r['confidence']}\n")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
