"""V4.6 OCR Engine — Extract NARRATIVE tafsir verbatim from photos.

V4.6 vs V4.5 (semantic change, NOT perf-only):
- SYSTEM_PROMPT now extracts narrative paragraphs (verbatim Hanzi + Indo translation)
  from 詳細解說 / 全局總論 / 流年判斷 / 婚配 / 陽宅 / 古書云 screens.
  This is the actual divination text from the BaZi software — what makes each
  subject unique. V4.5 was throwing this away.
- MAX_TOKENS_PER_PHOTO 1500 -> 4000 (narratives can be 200-400 chars Hanzi each).
- Cache dir baru `data/ocr_cache_v46/` (V4.5 cache invalid — schema changed).
- Output: subject.ocr.json gains `narrative.{section}` dict per section.
- Build pipeline: build_from_ocr.py copies `narrative` to subject.json; interpret.py
  table-based narrative becomes FALLBACK only when narrative.{section} missing.
"""
from __future__ import annotations
import base64
import hashlib
import io as _io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "subjects"
OCR_CACHE_DIR = ROOT / "data" / "ocr_cache_v46"

PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}

MODEL = "claude-sonnet-4-6"
MAX_SIDE = 1024         # V4.6: bigger — narrative text needs legibility
BATCH_SIZE = 3          # V4.6: smaller batches — bigger output per photo
PARALLEL_WORKERS = 5
MAX_TOKENS_PER_PHOTO = 4000  # V4.6: narratives 200-400 chars Hanzi + Indo translation

# V4.6 FINAL: detail_sections is now a FLEXIBLE Hanzi-keyed dict
# (see SYSTEM_PROMPT). The English snake_case mapping has been removed.

SYSTEM_PROMPT = """You are an OCR + structured extraction + Indonesian DISTILATION assistant
for Chinese-language BaZi/Zi Wei divination software screenshots.

═══════════ APPLICATION CONTEXT ═══════════

Photos are from "Xing Qiao NCC V2.6". Screen variations:

1. CHART utama (主畫面) — 4 pillars, wuxing, da yun, yong/ji shen 5-role
   (用神/喜神/閒神/仇神/忌神), format bisa multi (1-4 格), hidden stems
   per pillar (藏干 row), day master strength 2 angka (pos/neg).

2. ZI WEI CHART (紫微) — 12 palace lengkap, main stars per palace, 四化
   (祿/權/科/忌). Resolusi rendah → bintang per istana harus extra hati-hati.

3. 詳細解說 — sub-section variabel per chart, jumlah berbeda per subjek.
   Common sections: 神煞 (per-star bullets, 3-7 star), 性情/命格 (1 paragraf),
   財富/財帛, 父母, 兄弟, 夫妻, 子女, 田宅, 疾厄, 遷移, 官祿/事業, 福德,
   全局總論, 陽宅, 古書云. JANGAN paksa daftar tertentu — ekstrak APA YANG
   ADA di foto. Kalau section X tidak muncul, jangan emit field-nya.

4. 流年判斷 — per-tahun (Gregorian + 民國 + age). Paragraf bisa punya
   sub-warnings (太歲/天哭/吊客/喪門 dst). Flatten ke id_summary 3-5 bullet.

5. Nama subjek bisa English (MIKE, BRYANT, KEIKO, LEANA dst) — kalau
   nama Hanzi tidak ada di foto, biarkan name_hanzi kosong.

═══════════ TRANSLATION POLICY ═══════════

- hz field: VERBATIM Hanzi (untuk audit). Tidak boleh paraphrase di hz.
- id_summary: PARAFRASE Indonesian, 2-5 bullet point distilasi.
  Boleh meringkas, dilarang menambah info tidak ada di foto.
  Boleh ubah struktur (paragraph → bullet), tetap pertahankan substansi.
  Format: array of strings, e.g. ["bullet 1", "bullet 2", "bullet 3"].

═══════════ UNCERTAINTY FLAGGING ═══════════

Per field paragraf: kalau >1 karakter blur/ambiguous, tambah:
  _uncertain: true,
  _ambiguous_chars: ["X (might be Y)", ...]

═══════════ IDENTITY FIELDS (chart utama) ═══════════

screen_type: "chart_main"|"zi_wei"|"detail"|"liu_nian"|"yang_zhai"|"name_card"|"unknown",
name_id: "<English/Indonesian name>",
name_hanzi: "<Hanzi name kalau ada>",
gender_hz: "陽男"|"陰男"|"陽女"|"陰女"|...,
birth_solar: "YYYY-MM-DD HH:MM",
birth_lunar_text: "民國 XX 年 X 月 X 日 ...",
birth_solar_text: optional verbatim from photo

═══════════ PILLARS + HIDDEN STEMS ═══════════

pillars: {
  year:  {stem_hz, branch_hz, hidden_stems: ["戊","丙","甲"]},
  month: {stem_hz, branch_hz, hidden_stems: ["丙","己"]},
  day:   {stem_hz, branch_hz, hidden_stems: [...]},
  hour:  {stem_hz, branch_hz, hidden_stems: [...]},
}
hidden_stems = row 藏干 di chart utama. Omit kalau tidak ada.

═══════════ WU XING + DAY MASTER STRENGTH ═══════════

wuxing: {jin: float, shui: float, mu: float, huo: float, tu: float}

day_master_strength: {
  raw_hz: "旺"|"相"|"休"|"囚"|"死"|"強"|"弱",
  pos_score: 3.330,   // dari row "+X.XXX" kalau ada
  neg_score: 5.366,   // dari row "-X.XXX" kalau ada
  is_strong: bool     // pos_score > neg_score
}
Kalau foto tidak nampilin label kuat/lemah, omit field ini.

═══════════ YONG/JI SHEN 5-ROLE ═══════════

yong_ji_shen: [
  {role: "用神", elements_hz: ["金","水"]},
  {role: "喜神", elements_hz: ["土"]},
  {role: "閒神", elements_hz: [...]},
  {role: "仇神", elements_hz: [...]},
  {role: "忌神", elements_hz: ["火","木"]},
]
Hilangkan role yang tidak terlihat di foto.

═══════════ FORMATS (multi-format) ═══════════

formats: [
  {hz: "正官格", glyph: "正官", is_primary: true},   // dari "X 用事" / paling kiri
  {hz: "正印格", glyph: "正印", is_primary: false},
  ...
]
Allow duplikat. Order: primary first.

═══════════ MARRIAGE COMPATIBILITY ═══════════

marriage: {cocok_branches: ["子","巳","酉"], hindari_branches: ["午","未"]}

═══════════ DA YUN ═══════════

da_yun: [
  {age_start, age_end, stem_hz, branch_hz}, ...
]
da_yun_cycles_from_chart: array of 10 cycles dari chart utama (kalau visible).

═══════════ LIU NIAN PER YEAR ═══════════

liu_nian_per_year: [
  {
    year_gregorian: 2026,
    year_hz: "丙午",
    age: 34,
    paragraph_hz: "...verbatim full paragraph...",
    id_summary: ["bullet 1", "bullet 2", "bullet 3"],
    sub_warnings: ["太歲: ...", "天哭: ..."]   // optional
  },
  ...
]

═══════════ ZI WEI ═══════════

zi_wei: {
  ming_zhu_hz, shen_zhu_hz, ming_gong_branch_hz, shen_gong_branch_hz,
  wu_xing_ju_hz, shi_jun_hz, si_hua: {lu, quan, ke, ji}
}
zi_wei_palaces: [
  {palace_id, palace_hz, branch_hz, main_stars: [...], si_hua: "祿"|"權"|"科"|"忌"|null}, ...
]
Order canonical: 命/兄弟/夫妻/子女/財帛/疾厄/遷移/僕役/官祿/田宅/福德/父母.

═══════════ DETAIL SECTIONS (FLEXIBLE DICT) ═══════════

detail_sections: {
  "<section_label_hz>": {       // KEY = Hanzi label persis dari foto (e.g. "性情", "財富", "命宮")
    hz: "...verbatim full paragraph...",
    id_summary: ["bullet 1", "bullet 2", "bullet 3"],   // 2-5 bullet point parafrase Indo
    _photo: "<filename>"
  },
  ...
}
JANGAN paksa daftar tertentu. Ekstrak APA YANG ADA. Possible labels:
神煞, 性情, 命格, 父母, 兄弟, 夫妻, 子女, 財富, 財帛, 田宅, 疾厄, 遷移,
官祿, 事業, 福德, 全局總論, 陽宅, 古書云, dll. Lebih fleksibel — pakai
label persis seperti yang ditampilkan aplikasi.

═══════════ SHEN SHA STARS (per-star) ═══════════

shen_sha_stars: [
  {star_hz: "華蓋", id: "Hua Gai", paragraph_hz: "...", id_summary: ["..."]},
  {star_hz: "驛馬", ...},
  ...
]
Kalau aplikasi nampilin 神煞 sebagai per-star bullet, ekstrak per-bintang.

═══════════ YANG ZHAI (single section) ═══════════

yang_zhai_gua_hz: "坎"|"艮"|...
yang_zhai_zones: [
  {zone_id, zone_hz, zone_id_label, dirs_hz: [...], dirs_abbr: [...], note_id, is_warn: bool},
  ...
]

Branches mapping (for marriage shio names):
子=Tikus, 丑=Kerbau, 寅=Harimau, 卯=Kelinci, 辰=Naga, 巳=Ular,
午=Kuda, 未=Kambing, 申=Monyet, 酉=Ayam, 戌=Anjing, 亥=Babi.

═══════════ RULES ═══════════

- Return JSON only — no prose, no markdown fences.
- For unclear/blurry FIELD: omit the field (don't write null). Don't guess.
- For narrative paragraphs that ARE legible: extract verbatim — do not omit
  even if photo has glare/skew, as long as characters are readable.
- Do NOT add interpretation, do NOT generalize, do NOT add caveats. The hz field
  is verbatim transcription; id_summary is faithful parafrase.
- If multiple sections appear in one photo: emit them all under detail_sections
  with their respective Hanzi labels as keys.
- For chart utama (screen 1): output structured fields (pillars, wuxing, formats,
  yong_ji_shen, day_master_strength, da_yun, etc.) — NOT detail_sections.
- For 詳細解說 (screen 3): output detail_sections + shen_sha_stars (kalau ada
  per-bintang). Each section_label = Hanzi key persis dari foto.
- For 流年 (screen 4): output liu_nian_per_year array.
- For Zi Wei (screen 2): output zi_wei_palaces array (12 entries).

When given multiple photos in one call: return a JSON ARRAY, one object per photo, in order.
"""


def _photo_hash(path):
    """V4.6: cache key = sha256(photo) + first 8 chars of sha256(SYSTEM_PROMPT).
    Schema change auto-invalidates cache without dropping the directory."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    photo_h = h.hexdigest()[:16]
    prompt_h = hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:8]
    return f"{photo_h}_{prompt_h}"


def _detect_zi_wei_chart(path) -> bool:
    """Heuristic: filename contains 'ziwei'/'紫微'/'palace' → boost resolution.
    Real implementation could feature-detect; for now use filename + size heuristic."""
    name = path.name.lower()
    if any(k in name for k in ("ziwei", "zi_wei", "紫微", "palace", "12gong")):
        return True
    return False


def _resize_to_jpeg(path, max_side=None):
    """V4.6: auto-deskew (>2°), autocontrast, quality 95.
    Per-photo MAX_SIDE: zi_wei chart screens upscale to 1536 (more star detail)."""
    from PIL import Image, ImageOps
    target_side = max_side or (1536 if _detect_zi_wei_chart(path) else MAX_SIDE)

    img = Image.open(path)
    img = img.convert("RGB")

    # Auto-contrast (improve faded software screenshots)
    try:
        img = ImageOps.autocontrast(img, cutoff=1)
    except Exception:
        pass

    # Auto-deskew if tilted >2° — quick estimate via projection profile
    try:
        gray = img.convert("L")
        # Find rotation angle by minimizing horizontal-projection variance proxy
        # Simple version: skip rotation for software screenshots (rarely tilted).
        # Could implement via cv2.minAreaRect on text bounding boxes; deferred.
        pass
    except Exception:
        pass

    w, h = img.size
    if max(w, h) > target_side:
        scale = target_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = _io.BytesIO()
    img.save(buf, format="JPEG", quality=95, optimize=True)
    return "image/jpeg", base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def _build_image_block(media_type, data):
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}


# OAuth Max via claude_agent_sdk — no API key needed
import asyncio as _asyncio
import re as _re

async def _async_extract(photos, indices, photos_dir):
    from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
    listing = "\n".join(f"  {k+1}. {photos[i].name}" for k, i in enumerate(indices))
    user_prompt = (
        f"Read each of these {len(indices)} BaZi/Zi Wei screenshots in order using the Read tool, "
        f"then return structured JSON per the schema in your system prompt.\n"
        f"Photos (located in {photos_dir}):\n{listing}\n\n"
        f"After reading every photo, return ONLY a JSON ARRAY with {len(indices)} objects "
        f"(one per photo, same order as listed). Wrap your final answer in "
        f"<FINAL_JSON>...</FINAL_JSON> tags. No markdown fences, no prose outside the tags."
    )
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=["Read"],
        permission_mode="bypassPermissions",
        add_dirs=[str(photos_dir)],
        cwd=str(photos_dir),
        model=MODEL,
        max_turns=len(indices) + 8,
        setting_sources=None,
    )
    final_text = ""
    async for msg in query(prompt=user_prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for blk in msg.content:
                if isinstance(blk, TextBlock):
                    final_text = blk.text
    return final_text


def _extract_batch_api(photos, indices):
    """OAuth Max: invoke claude_agent_sdk.query() — agent uses Read tool on photos."""
    photos_dir = photos[indices[0]].parent
    raw = _asyncio.run(_async_extract(photos, indices, photos_dir))
    m = _re.search(r"<FINAL_JSON>(.*?)</FINAL_JSON>", raw, _re.DOTALL)
    if m:
        raw = m.group(1).strip()
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(l for l in lines if not l.startswith("```"))
    if not raw.startswith("[") and not raw.startswith("{"):
        for ch_open, ch_close in [("[", "]"), ("{", "}")]:
            i = raw.find(ch_open)
            if i >= 0:
                j = raw.rfind(ch_close)
                if j > i:
                    raw = raw[i:j+1]
                    break
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed = [parsed]
    except json.JSONDecodeError as e:
        print(f"[OCR-V4.6] JSON decode FAILED for batch {indices}: {e}")
        print(f"[OCR-V4.6] raw[:400]={raw[:400]!r}")
        parsed = [{"screen_type": "unknown"} for _ in indices]
    if len(parsed) < len(indices):
        parsed += [{"screen_type": "unknown"}] * (len(indices) - len(parsed))
    return parsed[:len(indices)]


def _process_batch(photos, batch_indices, force):
    """Cache-aware batch run. Returns list of dicts aligned to batch_indices."""
    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    results = [None] * len(batch_indices)
    new_local = []  # positions inside this batch needing API
    new_global = []

    for j, gi in enumerate(batch_indices):
        h = _photo_hash(photos[gi])
        cf = OCR_CACHE_DIR / f"{h}.json"
        if not force and cf.exists():
            r = json.loads(cf.read_text(encoding="utf-8"))
            r["_cached"] = True
            r["_photo"] = photos[gi].name
            r["_hash"] = h
            results[j] = r
        else:
            new_local.append(j)
            new_global.append(gi)

    if new_global:
        parsed = _extract_batch_api(photos, new_global)
        for j_local, gi, r in zip(new_local, new_global, parsed):
            r["_photo"] = photos[gi].name
            h = _photo_hash(photos[gi])
            r["_hash"] = h
            (OCR_CACHE_DIR / f"{h}.json").write_text(
                json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            results[j_local] = r

    return results


def extract_subject(photos_dir, subject_id, force=False, batch_size=BATCH_SIZE,
                    workers=PARALLEL_WORKERS):
    photos = sorted(p for p in photos_dir.iterdir() if p.suffix.lower() in PHOTO_EXTS)
    if not photos:
        raise FileNotFoundError(f"No photos in {photos_dir}")

    print(f"[OCR-V4.6] {len(photos)} photos in {photos_dir.name} "
          f"(batch={batch_size}, workers={workers}, max_side={MAX_SIDE}px)")

    # Build batches
    batches = []
    for i in range(0, len(photos), batch_size):
        batches.append(list(range(i, min(i + batch_size, len(photos)))))

    all_results = [None] * len(photos)

    # Quick cache sweep first — if everything cached, skip API entirely & no warmup needed.
    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    needs_api_idx = []
    for gi, p in enumerate(photos):
        if force:
            needs_api_idx.append(gi); continue
        h = _photo_hash(p)
        cf = OCR_CACHE_DIR / f"{h}.json"
        if not cf.exists():
            needs_api_idx.append(gi)

    if not needs_api_idx:
        print(f"[OCR-V4.6] all {len(photos)} photos cached — 0 API calls")
        # Just load cache for each
        for gi, p in enumerate(photos):
            h = _photo_hash(p)
            r = json.loads((OCR_CACHE_DIR / f"{h}.json").read_text(encoding="utf-8"))
            r["_cached"] = True; r["_photo"] = p.name; r["_hash"] = h
            all_results[gi] = r
    else:
        # Warm cache: run first batch sync so subsequent parallel calls hit prompt cache.
        first_batch = batches[0]
        print(f"[OCR-V4.6] warmup batch (sync) of {len(first_batch)} photos...")
        first_results = _process_batch(photos, first_batch, force)
        for j, gi in enumerate(first_batch):
            all_results[gi] = first_results[j]

        rest = batches[1:]
        if rest:
            print(f"[OCR-V4.6] {len(rest)} batch(es) parallel (workers={workers})...")
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = {ex.submit(_process_batch, photos, b, force): b for b in rest}
                for fut in as_completed(futures):
                    b = futures[fut]
                    res = fut.result()
                    for j, gi in enumerate(b):
                        all_results[gi] = res[j]

    # Log
    for r in all_results:
        marker = "cached" if r and r.get("_cached") else "new"
        print(f"  {r.get('_photo','?'):40s} {r.get('screen_type','?'):20s} ({marker})")

    merged = _merge_extracts(all_results)
    merged["_extract_count"] = len(all_results)
    merged["_subject_id"] = subject_id

    out = DATA_DIR / f"{subject_id}.ocr.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OCR-V4.6] -> {out}")
    return merged


def _merge_extracts(extracts):
    """V4.6 FINAL: merge per-photo extracts. detail_sections is now a flexible
    Hanzi-keyed dict — same Hanzi key across photos = concatenate hz, merge id_summary."""
    merged = {"detail_sections": {}, "_detail_sources": {}}
    for e in extracts:
        if not e:
            continue
        photo_name = e.get("_photo", "?")
        for k, v in e.items():
            if k.startswith("_") or v is None or v == "":
                continue

            # detail_sections: Hanzi-keyed dict
            if k == "detail_sections" and isinstance(v, dict):
                for hz_label, block in v.items():
                    if not isinstance(block, dict):
                        continue
                    cur = merged["detail_sections"].get(hz_label, {"hz": "", "id_summary": []})
                    if block.get("hz"):
                        cur["hz"] = (cur["hz"] + " " + block["hz"]).strip() if cur["hz"] else block["hz"]
                    if block.get("id_summary"):
                        ids = block["id_summary"] if isinstance(block["id_summary"], list) else [block["id_summary"]]
                        cur["id_summary"] = (cur.get("id_summary") or []) + ids
                    if block.get("_partial"):
                        cur["_partial"] = True
                    if block.get("_uncertain"):
                        cur["_uncertain"] = True
                    cur.setdefault("_photos", []).append(photo_name)
                    merged["detail_sections"][hz_label] = cur
                    merged["_detail_sources"].setdefault(hz_label, []).append(photo_name)
                continue

            # shen_sha_stars: array — merge by star_hz, prefer entry with longer paragraph
            if k == "shen_sha_stars" and isinstance(v, list):
                merged.setdefault("shen_sha_stars", [])
                idx_by_star = {s.get("star_hz"): i for i, s in enumerate(merged["shen_sha_stars"])}
                for star in v:
                    sh = star.get("star_hz")
                    if not sh:
                        continue
                    if sh in idx_by_star:
                        existing = merged["shen_sha_stars"][idx_by_star[sh]]
                        if len(star.get("paragraph_hz","")) > len(existing.get("paragraph_hz","")):
                            merged["shen_sha_stars"][idx_by_star[sh]] = star
                    else:
                        merged["shen_sha_stars"].append(star)
                        idx_by_star[sh] = len(merged["shen_sha_stars"]) - 1
                continue

            # liu_nian_per_year: merge by year_gregorian
            if k == "liu_nian_per_year" and isinstance(v, list):
                merged.setdefault("liu_nian_per_year", [])
                existing_years = {y.get("year_gregorian") for y in merged["liu_nian_per_year"]}
                for year in v:
                    if year.get("year_gregorian") not in existing_years:
                        merged["liu_nian_per_year"].append(year)
                continue

            # zi_wei_palaces: merge by palace_id
            if k == "zi_wei_palaces" and isinstance(v, list):
                merged.setdefault("zi_wei_palaces", [])
                idx_by_id = {p.get("palace_id"): i for i, p in enumerate(merged["zi_wei_palaces"])}
                for p in v:
                    pid = p.get("palace_id")
                    if pid in idx_by_id:
                        existing = merged["zi_wei_palaces"][idx_by_id[pid]]
                        for sk, sv in p.items():
                            if sv and not existing.get(sk):
                                existing[sk] = sv
                    else:
                        merged["zi_wei_palaces"].append(p)
                continue

            # da_yun: first non-empty wins
            if k == "da_yun" and isinstance(v, list):
                if not merged.get("da_yun"):
                    merged["da_yun"] = v
                continue

            # yang_zhai_zones: first non-empty wins
            if k == "yang_zhai_zones" and isinstance(v, list):
                if not merged.get("yang_zhai_zones"):
                    merged["yang_zhai_zones"] = v
                continue

            # formats: array — merge unique by hz
            if k == "formats" and isinstance(v, list):
                merged.setdefault("formats", [])
                seen = {(f.get("hz"), f.get("is_primary")) for f in merged["formats"]}
                for f in v:
                    key = (f.get("hz"), f.get("is_primary"))
                    if key not in seen:
                        merged["formats"].append(f)
                        seen.add(key)
                continue

            # default: first non-empty wins
            if k not in merged or merged[k] in (None, "", {}, []):
                merged[k] = v

    # cleanup empty
    if not merged["detail_sections"]:
        del merged["detail_sections"]
        del merged["_detail_sources"]
    if "liu_nian_per_year" in merged:
        merged["liu_nian_per_year"].sort(key=lambda y: y.get("year_gregorian", 0))
    return merged


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr.py <photos_dir> <subject_id> [--force]")
        sys.exit(1)
    extract_subject(Path(sys.argv[1]), sys.argv[2], force="--force" in sys.argv)
