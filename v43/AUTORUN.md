# AUTORUN — Sandbox1 V4.3 Pipeline

User akan kasih lokasi folder foto saja (contoh: `C:\Users\sukam\Downloads\banzi1`).
Kamu langsung jalankan pipeline tanpa nanya.

## 0. Baca dulu (sekali)
- `MEMORY.md` index
- `v3_freeze_policy.md` (V3 LOCKED)
- `v41_shared_templates.md` (6 shared templates)
- `sandbox1_milestone.md` (engine architecture)
- `lessons_tommy_iteration.md` (edge cases)

## 1. Aturan
- DILARANG sentuh `cache/michele`, `cache/linruyi`, `cache/_shared` (V3 LOCKED)
- DILARANG ubah design + konten
- Output ke `sandbox1/_pdf_out/{tanggal}/`, JANGAN `#result/`
- Konten harus sesuai foto, bukan tebakan
- Native compute (sxtwl) untuk pillars
- Auto-OCR + auto-build subject + auto-render, no questions

## 2. Subject ID
`subject_id` = nama folder lowercase. Contoh `banzi1` -> `banzi1`.

## 3. API key
Cek `$env:ANTHROPIC_API_KEY`. Kalau kosong, tanya user (satu-satunya boleh tanya).

## 4. Pipeline

### A. OCR
```
cd C:\Users\sukam\OneDrive\Documents\Ramalan\sandbox1
python engines/ocr.py "{photos_dir}" {subject_id}
```
Output: `data/subjects/{subject_id}.ocr.json`. Cached per-photo (re-run = 0 token).

### B. Build subject.json
Run `python engines/build_subject_from_ocr.py {subject_id}`.
Kalau script belum ada, buat pakai template di bawah file ini.
Output: `data/subjects/{subject_id}.json`.

### C. Render PDF
```
python engines/render.py {subject_id}
```
Output: `_pdf_out/{tanggal}/{Name}-{Hanzi}-{Birth}-V4.3.pdf`.

## 5. Report singkat
- Link PDF + size
- Token actual + waktu
- Field fallback (kalau ada)

## 6. Error handling
- OCR JSON parse fail: cek `data/ocr_cache/{hash}.raw.txt`
- Pillar diff OCR vs native: trust native
- Chrome lock: pastikan PDF lama tidak open di viewer

## 7. NEVER
- Tanya user soal routine
- OCR ulang foto sama (cache active)
- Modifikasi V3 folders
- Overwrite #result/ V3 PDFs
- Tebak data kalau OCR partial

---

## Template engines/build_subject_from_ocr.py

```python
import json, sys
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent))
from compute_pillars import compute_subject_core
from build_subject import build_subject

def build_from_ocr(subject_id):
    ROOT = Path(__file__).resolve().parent.parent
    ocr = json.loads((ROOT / "data" / "subjects" / f"{subject_id}.ocr.json").read_text(encoding="utf-8"))

    name_id = ocr.get("name_id") or subject_id.title()
    name_hanzi = ocr.get("name_hanzi") or ""
    gender_hz = ocr.get("gender_hz") or ""
    gender_id = "Pria" if "男" in gender_hz else "Wanita"

    birth_solar = ocr.get("birth_solar") or "1990-01-01 12:00"
    parts = birth_solar.split(" ")
    birth_date = parts[0]
    birth_time = parts[1] if len(parts) > 1 else "12:00"

    core = compute_subject_core(name_id, name_hanzi, gender_id,
                                 birth_date, birth_time, age_at_report=None)
    by, bm, bd = map(int, birth_date.split("-"))
    today = date.today()
    core["age_at_report"] = today.year - by - ((today.month, today.day) < (bm, bd))
    core["subject_id"] = subject_id

    core["wuxing"] = ocr.get("wuxing") or {"jin":0,"shui":0,"mu":0,"huo":0,"tu":0}
    core["yong_shen"] = {"elements_hz": ocr.get("yong_shen_hz") or ""}
    core["ji_shen"] = {"elements_hz": ocr.get("ji_shen_hz") or ""}
    core["format"] = {"hz": ocr.get("format_hz") or ""}
    core["yang_zhai"] = {"gua_hz": ocr.get("yang_zhai_gua_hz") or ""}
    core["zi_wei"] = ocr.get("zi_wei") or {}

    subject = build_subject(core)
    out = ROOT / "data" / "subjects" / f"{subject_id}.json"
    out.write_text(json.dumps(subject, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return out

if __name__ == "__main__":
    build_from_ocr(sys.argv[1])
```
