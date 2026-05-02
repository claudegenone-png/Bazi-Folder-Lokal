"""Sandbox1 OCR Engine V4.3 - Resize + Batch + per-photo cache.

V4.3 improvements over V4.1:
- Resize photos to MAX_SIDE px before vision (cuts vision tokens 2-4x).
- Batch BATCH_SIZE photos per API call (saves system prompt overhead).
- Per-photo SHA256 cache still applies (re-render = 0 tokens).
- Skip OCR for pillars (use Phase 4 native compute via build_subject).
"""
from __future__ import annotations
import base64
import hashlib
import io as _io
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "subjects"
OCR_CACHE_DIR = ROOT / "data" / "ocr_cache"

PHOTO_EXTS = {".jpeg", ".jpg", ".png", ".webp"}

MODEL = "claude-sonnet-4-6"
MAX_SIDE = 1024     # resize photos so longest side <= this (vision token saver)
BATCH_SIZE = 5      # photos per API call (overhead saver)

SYSTEM_PROMPT = """You are a precise OCR + data extraction assistant for Chinese metaphysics software screenshots.

Photos are screenshots from "Xing Qiao NCC V2.6" software. Screen types:
1. BaZi Chart (主畫面) - 4 pillars, Wu Xing distribution, Da Yun, Yong Shen.
2. Zi Wei Chart (紫微斗數) - 12 palaces, 大限, 小限.
3. 詳細解說 - 神煞 / 性情 / 父母 / 兄弟 / 夫妻 / 子女 / 財帛 / 田宅 / 疾厄 / 遷移 / 官祿 / 福德 / 古書云 / 全局總論 / 婚配 / 陽宅 / 事業.
4. 流年判斷.
5. Photo of person/handwritten name.

Identify screen type and extract ALL structured data visible. Return JSON only (no prose).
For unclear/blurry, use null. Do not guess.

Branches mapping:
子=Tikus, 丑=Kerbau, 寅=Harimau, 卯=Kelinci, 辰=Naga, 巳=Ular,
午=Kuda, 未=Kambing, 申=Monyet, 酉=Ayam, 戌=Anjing, 亥=Babi.

Output JSON object per photo with relevant subset of:
screen_type, tafsir_section, name_id, gender_hz, birth_solar, birth_lunar_text,
pillars{year,month,day,hour}, wuxing{jin,shui,mu,huo,tu}, yong_shen_hz, ji_shen_hz,
format_hz, da_yun[], marriage{cocok_branches,hindari_branches}, yang_zhai_gua_hz,
zi_wei{ming_zhu_hz,shen_zhu_hz,ming_gong_branch_hz,shen_gong_branch_hz,wu_xing_ju_hz,shi_jun_hz},
raw_text.

When given multiple photos in one call: return a JSON array, one object per photo, in order.
"""


def _photo_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _resize_to_jpeg(path, max_side=MAX_SIDE):
    """Resize photo so longest side <= max_side. Return (media_type, base64_str)."""
    from PIL import Image
    img = Image.open(path)
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
    buf = _io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    data = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    return "image/jpeg", data


def _build_image_block(media_type, data):
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}


def extract_batch(photos, force=False):
    """Extract a batch of photos in one API call. Returns list of result dicts (same order)."""
    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Resolve cache hits first
    results = [None] * len(photos)
    new_indices = []
    for i, p in enumerate(photos):
        h = _photo_hash(p)
        cf = OCR_CACHE_DIR / f"{h}.json"
        if not force and cf.exists():
            r = json.loads(cf.read_text(encoding="utf-8"))
            r["_cached"] = True
            r["_photo"] = p.name
            r["_hash"] = h
            results[i] = r
        else:
            new_indices.append(i)

    if not new_indices:
        return results

    from anthropic import Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY env var not set")
    client = Anthropic(api_key=api_key)

    # Build content with all new photos + extraction prompt
    content = []
    for i in new_indices:
        media, data = _resize_to_jpeg(photos[i])
        content.append(_build_image_block(media, data))
        content.append({"type": "text", "text": f"[Photo {i + 1}]"})
    content.append({
        "type": "text",
        "text": (
            f"Return a JSON ARRAY with {len(new_indices)} objects, "
            "one per photo IN ORDER. Each object follows the schema. JSON only."
        ),
    })

    print(f"[OCR] batch of {len(new_indices)} photos -> Claude vision...")
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000 * len(new_indices),
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
            parsed = [parsed]  # single-photo fallback
    except json.JSONDecodeError:
        # Fallback: dump raw, treat each as unknown
        for i in new_indices:
            results[i] = {"screen_type": "unknown", "raw_text": "JSON parse failed",
                          "_photo": photos[i].name}
        return results

    # Save each parsed result to cache + assign to results
    for j, idx in enumerate(new_indices):
        if j >= len(parsed):
            r = {"screen_type": "unknown"}
        else:
            r = parsed[j]
        r["_photo"] = photos[idx].name
        h = _photo_hash(photos[idx])
        r["_hash"] = h
        cf = OCR_CACHE_DIR / f"{h}.json"
        cf.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        results[idx] = r

    return results


def extract_subject(photos_dir, subject_id, force=False, batch_size=BATCH_SIZE):
    photos = sorted(p for p in photos_dir.iterdir() if p.suffix.lower() in PHOTO_EXTS)
    if not photos:
        raise FileNotFoundError(f"No photos in {photos_dir}")

    print(f"[OCR] {len(photos)} photos in {photos_dir.name} (batch={batch_size}, max_side={MAX_SIDE}px)")

    all_results = []
    for i in range(0, len(photos), batch_size):
        batch = photos[i:i + batch_size]
        all_results.extend(extract_batch(batch, force=force))

    # Log
    for r in all_results:
        marker = "cached" if r.get("_cached") else "new"
        print(f"  {r.get('_photo','?')}: {r.get('screen_type','?')} ({marker})")

    merged = _merge_extracts(all_results)
    merged["_extract_count"] = len(all_results)
    merged["_subject_id"] = subject_id

    out = DATA_DIR / f"{subject_id}.ocr.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OCR] -> {out}")
    return merged


def _merge_extracts(extracts):
    merged = {"raw_texts": []}
    for e in extracts:
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
