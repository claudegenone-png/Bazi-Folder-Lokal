# QA Report — V4.5 Full-MD Mode

**Date:** 2026-05-07
**Auditor:** Agent E
**Scope:** Cross-agent integration audit + smoke test post Agents A/B/C/D

---

## 1. Schema Consistency (Agent A → Agent B)

Agent A `engines/parse_md.py` writes the following keys to `ocr_data` (FULL-MD MODE block, lines ~259-380):

| ocr_data key | Type | Set by parse_md.py | Read by build_from_ocr.py |
|---|---|---|---|
| `dm_strength_hz` | str/None | line 263/265 | line 285 ✅ |
| `dm_strength_label_id` | str/None | line 267/269 | line 284 ✅ |
| `dm_pos_score` | float/None | line 277 | line 463 ✅ |
| `dm_neg_score` | float/None | line 277 | line 463 ✅ |
| `xiantian_per_stem` | dict/None | line 291 | line 465 ✅ |
| `wangdu_per_stem` | dict/None | line 304 | line 466 ✅ |
| `wangdu_total` | dict/None | line 316 | line 467 ✅ |
| `da_yun_arah_id` | "forward"/"backward"/None | line 322-327 | line 236 ✅ |
| `da_yun_start_age` | int/None | line 335 | line 237 ✅ |
| `shen_sha_list` | list[{hanzi,pillar}]/None | line 354/356 | line 390 ✅ |
| `nayin_per_pillar` | dict{year,month,day,hour}/None | line 367 | line 468 ✅ |
| `canggan_per_pillar` | dict{year,month,day,hour}/None | line 377 | line 469 ✅ |

**[PASS]** — All 12 new field keys + types match between Agent A output and Agent B input.

### Agent B → Agent D (subject.json → render.py)

| subject.json field | Agent B writes | render.py null-safety |
|---|---|---|
| `day_master.strength_id/strength_hz` | line 292 | line 184 ✅ |
| `format.hz/pinyin/label_id` | line 317 | line 226-238 ✅ |
| `yong_shen.elements_hz/elements_id/label_id` | line 297 | line 228 ✅ |
| `ji_shen.elements_hz/elements_id/label_id` | line 298 | line 230 ✅ |
| `marriage.cocok/hindari` | line 338-342 | line 250-257 ✅ |
| `yang_zhai.gua_hz/...` | line 351 | line 264-271 ✅ |
| `zi_wei.{12 fields}` | line 371-388 | line 241-247 ✅ |
| `shen_sha_list` | line 461 (passthrough) | line 260-261 ✅ |
| `da_yun.cycles/seasons` | line 261 | line 273-303 ✅ |
| `pillars.{slot}.{stem_hz,branch_hz}` | line 222-226 | line 188-196 ✅ |

**[PASS]** — render.py `_normalize_subject_for_render()` (line 149-305) covers every nullable field that Agent B emits.

---

## 2. No-Compute Audit (forbidden patterns)

| Pattern | Status | Location |
|---|---|---|
| `sxtwl.fromSolar` for pillar derivation | **REMOVED** in compute_pillars.py | Only remaining call: build_from_ocr.py:406 — used for **lunar display only** (allowed per plan) |
| `sxtwl.getYearGZ` etc. | None active | — |
| `py_iztro` / `iztro` | **REMOVED** | grep returns 0 hits |
| `infer_relationship` | **REMOVED** | grep returns 0 hits |
| `_compute_shensha` | **REMOVED** | grep returns 0 hits |
| `_compute_ziwei_engine` | **REMOVED** | grep returns 0 hits |
| Hardcoded `"正官格"` default | **REMOVED** as default. The literal at build_from_ocr.py:305 is a **pinyin lookup table key** (legitimate). render.py:88 is **Michele reference** (legitimate baseline for substitution) | OK |
| `pct >= 25` DM strength threshold | **REMOVED** | grep returns 0 hits |
| Stem-counting wuxing fallback | **REMOVED** | grep returns 0 hits |
| Ba Zhai sexagenary digit-sum | **REMOVED** | grep returns 0 hits |
| `compute_pillars()` body | No-op (returns None dict) | compute_pillars.py:17-20 ✅ |
| `da_yun_direction()` body | Returns None | compute_pillars.py:23-26 ✅ |
| `da_yun_start_age()` body | Returns None | compute_pillars.py:29-32 ✅ |

**[PASS]** — All 11 compute zones successfully eliminated.

---

## 3. Null-Handling Audit

### render.py
- **[PASS]** `_normalize_subject_for_render()` walks subject dict, converts None → `EM_DASH "—"` for all string fields, 0 for numeric SVG fields, sets `_empty: True` flag on dicts where every numeric was None.
- **[PASS]** Da Yun: 10 placeholder cycles synthesized when MD had no da_yun (line 289-298), preserving lifeline grid shape.
- **[PASS]** Wuxing: percent/value default to 0 for SVG geometry; `_empty` flag drives subdued styling.
- **[PASS]** Marriage: cocok/hindari default to `[]`, `_empty` flag set.
- **[PASS]** TAFSIR null slug → italic em-dash placeholder (line 2078-2079).

### Templates
- **[PASS]** page_dayun.html line 83: explicit V4.5 null-safety comment + dim "—" placeholders.
- **[NOTE]** page_06_daymaster.html line 202 + page_yangzhai.html line 230, 271: comments still reference "Michele's polygon / N-S axis" — these are template authoring notes, NOT runtime placeholders. Harmless.

**[PASS]** — Null handling is comprehensive in render.py. Templates rely on substitution + `_normalize_subject_for_render`.

---

## 4. Smoke Test

```powershell
python build_pdf.py wuhuanyang
python build_pdf.py chelsey
```

| Subject | Step 0 (parse_md) | Step 1 (build_from_ocr) | Step 2 (render+PDF) | Verdict |
|---|---|---|---|---|
| `wuhuanyang` | OK (23 tafsir blocks) | OK (subject.json written) | **CRASH** at build_pdf.py:675 | **FAIL** |
| `chelsey` | OK (26 tafsir blocks) | OK (subject.json written) | **CRASH** at build_pdf.py:675 | **FAIL** |

Both crash with the same exception:
```
AttributeError: 'NoneType' object has no attribute 'upper'
  File "build_pdf.py", line 675
    f'<div class="ks-num"><span class="hz">{dm_hz}</span><span class="unit">{dm_strength.upper()} · {dm_strength_hz}</span></div>'
```

Root cause: `build_pdf.py:662` does `dm.get("strength_id", "")` — but Agent B writes the key `strength_id` with value `None`. `dict.get(k, default)` returns the **stored None**, not the default. Same pattern at line 663 (`strength_hz`).

This bug is in **build_pdf.py main() Card 1 builder**, which builds the kesimpulan stat-card HTML BEFORE handing the subject to render.py — so render.py's `_normalize_subject_for_render` null-safety never gets applied here.

Per plan, build_pdf.py is owned by main session (not in any agent's scope), so this needs a main-session fix.

---

## 5. DATA_EXTRA Isolation

**[PASS]** — parse_md.py:122-123 only reads `sections.get("DATA")` and `sections.get("TAFSIR")`. `## DATA_EXTRA` section is implicitly skipped (no parsing path for it). Confirmed: no `DATA_EXTRA` references in parse_md.py.

---

## 6. Field Name Consistency Spot-Checks

- `dm_strength_hz` parser sets (line 263) → builder reads (line 285): **MATCH** ✅
- `da_yun_arah_id` ("forward"/"backward") parser sets (line 322-327) → builder reads (line 236): **MATCH** ✅
- `shen_sha_list` parser emits `[{"hanzi":..., "pillar":...}]` (line 354) → builder passes through to subject (line 461): **MATCH** ✅, render.py treats as iterable list (line 260-261).
- `marriage.cocok_branches/hindari_branches` parser key names (line 227-228) → builder reads same names (line 321-322): **MATCH** ✅

---

## Bugs Found

### [CRITICAL] build_pdf.py:662-663 — `dict.get(k, "")` returns None when key holds None

**File:** `build_pdf.py:662-663`
**Symptom:** `AttributeError: 'NoneType' object has no attribute 'upper'` at line 675 for every subject whose MD lacks `dm_strength_label_id` (i.e. all existing subjects until re-extracted).
**Root cause:**
```python
dm_strength = dm.get("strength_id", "")        # returns None, not ""
dm_strength_hz = dm.get("strength_hz", "")     # returns None, not ""
...
f'... {dm_strength.upper()} · {dm_strength_hz} ...'  # crash here
```
Agent B explicitly writes `strength_id: None` (build_from_ocr.py:292 via `_stem_to_dm_block` line 55-56), so the key exists with None.
**Fix (main session):** replace with `dm.get("strength_id") or ""` (and `or ""` for `strength_hz`). Or normalize subject through `_normalize_subject_for_render` before build_pdf builds the kesimpulan cards.
**Blocking:** YES — blocks every smoke test PDF build.

### [CRITICAL] build_pdf.py main() builds HTML cards BEFORE render-layer null-safety

**File:** `build_pdf.py:660-735` (Card 1-6 stat cards)
**Symptom:** Card builders directly format `dm`, `fmt`, `ys_data`, `js_data`, `da_yun`, `cur_cycle`, `marriage` straight off `subject` dict — bypassing render.py's `_normalize_subject_for_render`. Any None field (label_id, elements_hz, elements_id, etc.) will format as the string `"None"` or crash.
**Audit-time check:** In addition to the line 662-663 crash, the same pattern at lines 685-687 (`fmt.get("hz","")` etc.), 695-697, 716-717 will silently emit "None" or empty into PDF if upstream is None. Need same `or ""` treatment OR call `_normalize_subject_for_render` first.
**Fix (main session):** Either (a) `from render import _normalize_subject_for_render` and apply to subject **before** Card 1-6 building, or (b) audit every `.get("…","")` in the kesimpulan/synthesis card builders and harden each.

### [MEDIUM] parse_md.py: TAFSIR section title "Da Yun — …" with em-dash not in SECTION_SLUGS

**File:** `engines/parse_md.py:30-33`
**Symptom:** wuhuanyang.md uses headings `### Da Yun — Spotlight (Fase Sekarang)` (em-dash `—`), but SECTION_SLUGS keys are `"da yun, spotlight (fase sekarang)"` (comma). Mismatch causes 3 sections to be silently skipped:
```
TAFSIR: unknown section 'Da Yun — Spotlight (Fase Sekarang)', skipped
TAFSIR: unknown section 'Da Yun — 5 Seasons', skipped
TAFSIR: unknown section 'Da Yun — Footer Caption', skipped
```
chelsey.md uses comma form so it works (26 blocks vs wuhuanyang 23).
**Fix:** Add em-dash variants to SECTION_SLUGS, OR normalize `—`/`–` to `,` before slug lookup.
**Severity:** MEDIUM — Da Yun spotlight tafsir not injected for wuhuanyang, but engine has fallback narrative at build_from_ocr.py:146-187.

### [MINOR] build_from_ocr.py:393 — dead code

**File:** `engines/build_from_ocr.py:393`
```python
weekday_id = _WEEKDAY_ID.get(bdt.weekday() if bdt.weekday() != 6 else 0) if False else None
```
`if False else None` always assigns None. Code below correctly recomputes via sxtwl or python fallback. Cosmetic only — remove the dead branch.

### [MINOR] parse_md.py:158 — operator precedence

**File:** `engines/parse_md.py:158`
```python
out["name_id"] = raw.get("nama") or h1.split()[0] if h1 else ""
```
Reads as `raw.get("nama") or (h1.split()[0] if h1 else "")` — works as intended, but parens recommended for clarity.

### [MINOR] build_from_ocr.py:284 has comment "removed REMOVED" — strength_id `.upper()` not applied

`strength_id` from MD is "Kuat"/"Lemah"/"Seimbang"; line 287 `wx["self_strength_id"] = strength_id.upper()` produces "KUAT" — make sure templates expect uppercase. (Not a bug, behavior note.)

---

## Verdict

**🟥 NEEDS FIX — NOT READY for production.**

Both smoke tests crash before producing a PDF. The blocker is a 2-line null-handling miss in `build_pdf.py` Card 1 builder (file owned by main session, not in any agent's scope). Once the `dm.get("strength_id") or ""` fix is applied AND the broader Card 1-6 null-safety is verified, build should succeed and the rest of the V4.5 FULL-MD pipeline (parse_md → build_from_ocr → render) is in good shape per the schema and no-compute audits.

### Recommended next steps (main session)

1. **Hotfix** `build_pdf.py:662-663` (and audit lines 660-735 for sibling patterns) — apply `or ""` defensive defaults OR call `render._normalize_subject_for_render(subject)` before kesimpulan card building.
2. **Re-run** `python build_pdf.py wuhuanyang` and `python build_pdf.py chelsey` — confirm PDF generated, fields are "—" where MD null, layout intact (radar polygon, wuxing bar, lifeline grid, marriage wheel).
3. **Optional polish:** patch SECTION_SLUGS em-dash variants (medium bug) so wuhuanyang's Da Yun tafsir injects properly.

Agents A, B, C, D all delivered to spec for their assigned scopes; the failure is at the integration boundary between Agent B output (subject.json with explicit `None`) and the build_pdf.py kesimpulan card builder (which used `.get(k, "")` defaults that don't trigger when the key holds None).
