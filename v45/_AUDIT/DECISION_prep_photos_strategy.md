# DECISION LOG — `prep_photos.py` strategy

**Status**: ✅ EXECUTED 2026-05-08 (Opsi A only). Opsi B (light-prep refactor) masih PENDING.
**Recorded**: 2026-05-08
**Owner**: user (sukam)

## Execution Log — Opsi A (2026-05-08)

Files edited:
- `v45/AUTORUN.md`: Step 1.5 prep_photos.py → SKIPPED. Step 2a cache_check.py → folder original. Catatan rename Step 6 di-update.
- `v49/AUDIT_AGENT_PROMPT.md`: placeholder `{photos_dir_prepped}` → `{photos_dir_original}` + warning note.
- `Ramalan/PROMPT_AUDIT_FOTO_ONLY.md`: INPUT section path → folder `{NAMA_SUBJECT_FOLDER}/` original + warning eksplisit.

Effect:
- Render baru post-2026-05-08 baca foto original langsung (`.jpeg`)
- Step prep di-skip (hemat 30-60s wall-clock + 50% disk per render)
- `prep_photos.py` script tetap available untuk fallback manual (foto miring/gelap)

Rollback: undo edits di 3 file di atas, atau trigger manual `python v45\prep_photos.py "<photos_dir>"` per kasus.

---

## Problem

Folder `1_prepped/.jpg` (hasil `prep_photos.py` upscale) ternyata **lebih blur** untuk hanzi kecil rapat dibanding original `.jpeg`. Penyebab: upscale interpolation bikin edges soft. Hasilnya:

- Hanzi mirip salah baca (傷/偏, 紫/天府/天相, 武曲/武貪, 廟旺平陷, sihua markers)
- False confidence (auditor yakin baca, padahal salah)
- Systematic error: semua subject + run terdampak

Konfirmasi visual: user verifikasi sendiri prepped lebih burem daripada original.

## Risk-reward analysis (singkat)

| Approach | Akurasi | Effort | Risk | Reward |
|---|---|---|---|---|
| **A** — Switch audit ke original folder, abaikan prepped | Tinggi | 5 menit (config path) | Rendah | Akurasi naik segera |
| **B** — Rewrite `prep_photos.py` hapus upscale (light prep only: rotate/crop/contrast) | Tinggi (permanent) | 30-60 menit (test+rollout) | Sedang (prepped lama obsolete, butuh re-run subject yg butuh prepped) | Akurasi naik + manfaat rotate/crop/enhance tetap |
| **C** — Output 2 versi (original + light-prepped) | Tertinggi | 1-2 jam | Rendah | Best, tapi disk 3× |
| **D** — Status quo | Rendah (continue error) | 0 | Tinggi | None |

## Rekomendasi

- **Patch sekarang**: Opsi **A** — audit + render baca foto dari folder original (`{tanggal}/{Nama}/`), bukan `1_prepped/`.
- **Jangka panjang**: Opsi **B** — refactor `prep_photos.py` jadi "light prep no upscale" (auto-rotate, crop frame, contrast ringan, **HAPUS upscale + artificial sharpening**).

## Action items (jangan dieksekusi tanpa konfirmasi user)

### Opsi A (patch cepat)
- [ ] Update `v45/AUTORUN.md` Step 1.5 / 2 — point foto path ke folder original (`{date}/{Nama}/.jpeg`)
- [ ] Update `v49/AUDIT_AGENT_PROMPT.md` — same
- [ ] Update `PROMPT_AUDIT_FOTO_ONLY.md` — clarify pakai original folder default
- [ ] Test: 1 subject baru, compare akurasi vs run lama
- [ ] Rollout setelah verifikasi

### Opsi B (refactor)
- [ ] Audit `prep_photos.py` saat ini — list semua step (rotate, crop, contrast, upscale, sharpen, dll)
- [ ] Identify step yang lossy (upscale + sharpen) vs yang aman (rotate, crop, contrast)
- [ ] Rewrite ke "light prep" — keep rotate/crop/contrast, drop upscale/sharpen
- [ ] Test 2-3 subject historis: re-run prep, audit pakai prepped baru, compare akurasi vs original-only
- [ ] Kalau hasil prepped baru ≥ original-only akurasi (dengan benefit tambahan: rotate/crop) → adopt
- [ ] Kalau tidak ada benefit → abandon prep, pakai original directly (Opsi A permanent)

## Bukti yang relevan

- Audit lixiangfa 2026-05-08: 4 high-confidence error MD vs foto. 3 dari 4 ada di field hanzi kecil (gender, palace stars, hour pillar) — area yang paling terdampak prepped blur.
- User visual check: prepped folder lebih burem dari original.
- External auditor sebelumnya pakai prepped → keliru di beberapa MEDIUM finding (palace stars, hour pillar shi_shen) yang setelah dicek ulang pakai foto user-upload jelas malah berbeda hasilnya.

## Notes

- Foto original `.jpeg` sudah selalu di-keep di folder `{date}/{Nama}/` (tidak dihapus saat prep). Jadi switch ke original tidak butuh re-collect data.
- Wall-clock saving Opsi A: ~30-60 detik per render (skip prep step).
- Disk saving Opsi A: ~50% (no duplicate prepped folder).
