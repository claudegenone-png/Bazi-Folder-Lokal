"""Sandbox2 OCR Engine V4.5 — Parallel batches + tighter schema + smaller images.

V4.5 vs V4.3 changes (perf only — output schema IDENTIK dengan V4.3):
- Parallel batches via ThreadPoolExecutor (PARALLEL_WORKERS=5).
- MAX_SIDE 1024 -> 768 (Claude vision tile boundary; ~1 tile vs ~4 tile).
- max_tokens 4000*N -> 1500*N (output JSON aktual jauh lebih kecil).
- System prompt: OMIT raw_text (tidak dipakai build_from_ocr).
- Cache warm-up: kirim 1 batch dulu (sync) supaya prompt cache populate,
  sisanya fan-out parallel = semua hit cache.
- Cache dir terpisah `data/ocr_cache_v45/` supaya tidak bentrok V4.3.
- Output merged JSON byte-compatible dengan build_from_ocr.py (no schema change).
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
OCR_CACHE_DIR = ROOT / "data" / "ocr_cache_v45"

PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}

MODEL = "claude-sonnet-4-6"
MAX_SIDE = 768          # was 1024 in V4.3
BATCH_SIZE = 5          # photos per API call
PARALLEL_WORKERS = 5    # concurrent batches
MAX_TOKENS_PER_PHOTO = 1500  # was 4000 in V4.3

SYSTEM_PROMPT = """You are a precise OCR + data extraction assistant for Chinese metaphysics software screenshots.

Photos are screenshots from "Xing Qiao NCC V2.6". Screen types:
1. BaZi Chart (主畫面) — 4 pillars, Wu Xing distribution, Da Yun, Yong Shen.
2. Zi Wei Chart (紫微斗數) — 12 palaces, 大限, 小限.
3. 詳細解說 — 神煞 / 性情 / 父母 / 兄弟 / 夫妻 / 子女 / 財帛 / 田宅 / 疾厄 / 遷移 / 官祿 / 福德 / 古書云 / 全局總論 / 婚配 / 陽宅 / 事業.
4. 流年判斷.
5. Photo of person / handwritten name.

Identify screen type and extract structured data visible. Return JSON only (no prose, no markdown fences).
For unclear/blurry, OMIT the field entirely (do not write null). Do not guess.
DO NOT include raw_text — only structured fields.

Branches mapping:
子=Tikus, 丑=Kerbau, 寅=Harimau, 卯=Kelinci, 辰=Naga, 巳=Ular,
午=Kuda, 未=Kambing, 申=Monyet, 酉=Ayam, 戌=Anjing, 亥=Babi.

Output JSON object per photo with relevant subset of:
screen_type, tafsir_section, name_id, gender_hz, birth_solar, birth_lunar_text,
pillars{year,month,day,hour}, wuxing{jin,shui,mu,huo,tu}, yong_shen_hz, ji_shen_hz,
format_hz, da_yun[], marriage{cocok_branches,hindari_branches}, yang_zhai_gua_hz,
zi_wei{ming_zhu_hz,shen_zhu_hz,ming_gong_branch_hz,shen_gong_branch_hz,wu_xing_ju_hz,shi_jun_hz}.

When given multiple photos in one call: return a JSON array, one object per photo, in order.
"""


def _photo_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _resize_to_jpeg(path, max_side=MAX_SIDE):
    from PIL import Image
    img = Image.open(path)
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = _io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    return "image/jpeg", base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def _build_image_block(media_type, data):
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}


_client_singleton = None
def _client():
    global _client_singleton
    if _client_singleton is None:
        from anthropic import Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY env var not set")
        _client_singleton = Anthropic(api_key=api_key)
    return _client_singleton


def _extract_batch_api(photos, indices):
    """Send 1 API call for a list of photos. Returns parsed list aligned to `indices`."""
    content = []
    for i in indices:
        media, data = _resize_to_jpeg(photos[i])
        content.append(_build_image_block(media, data))
        content.append({"type": "text", "text": f"[Photo {i + 1}]"})
    content.append({
        "type": "text",
        "text": (
            f"Return a JSON ARRAY with {len(indices)} objects, "
            "one per photo IN ORDER. Each object follows the schema. JSON only."
        ),
    })

    msg = _client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_PER_PHOTO * len(indices),
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": content}],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(l for l in lines if not l.startswith("```"))

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed = [parsed]
    except json.JSONDecodeError:
        parsed = [{"screen_type": "unknown"} for _ in indices]

    # pad/truncate
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

    print(f"[OCR-V4.5] {len(photos)} photos in {photos_dir.name} "
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
        print(f"[OCR-V4.5] all {len(photos)} photos cached — 0 API calls")
        # Just load cache for each
        for gi, p in enumerate(photos):
            h = _photo_hash(p)
            r = json.loads((OCR_CACHE_DIR / f"{h}.json").read_text(encoding="utf-8"))
            r["_cached"] = True; r["_photo"] = p.name; r["_hash"] = h
            all_results[gi] = r
    else:
        # Warm cache: run first batch sync so subsequent parallel calls hit prompt cache.
        first_batch = batches[0]
        print(f"[OCR-V4.5] warmup batch (sync) of {len(first_batch)} photos...")
        first_results = _process_batch(photos, first_batch, force)
        for j, gi in enumerate(first_batch):
            all_results[gi] = first_results[j]

        rest = batches[1:]
        if rest:
            print(f"[OCR-V4.5] {len(rest)} batch(es) parallel (workers={workers})...")
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
    print(f"[OCR-V4.5] -> {out}")
    return merged


def _merge_extracts(extracts):
    merged = {"raw_texts": []}
    for e in extracts:
        if not e:
            continue
        for k, v in e.items():
            if k.startswith("_") or v is None or v == "":
                continue
            if k == "raw_text":
                merged["raw_texts"].append(v)
            elif k == "da_yun" and isinstance(v, list):
                if not merged.get("da_yun"):
                    merged["da_yun"] = v
            elif k not in merged or merged[k] in (None, "", {}, []):
                merged[k] = v
    return merged


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr.py <photos_dir> <subject_id> [--force]")
        sys.exit(1)
    extract_subject(Path(sys.argv[1]), sys.argv[2], force="--force" in sys.argv)
