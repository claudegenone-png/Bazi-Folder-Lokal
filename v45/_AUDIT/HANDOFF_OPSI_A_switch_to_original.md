# HANDOFF — Opsi A: Switch audit/render ke folder foto ORIGINAL

> Untuk main window agent. Patch cepat: bypass folder `1_prepped/` (yang upscale-nya bikin hanzi blur), pakai folder original `{date}/{Nama}/` directly.

## CONTEXT

External auditor + user visual confirm: `1_prepped/.jpg` lebih blur dari `{Nama}/.jpeg` original karena upscale interpolation merusak hanzi kecil rapat (傷/偏, palace stars, sihua markers).

Decision log: `Ramalan/v45/_AUDIT/DECISION_prep_photos_strategy.md`

User pilih **Opsi A**: switch path foto, tidak refactor `prep_photos.py` (Opsi B di-skip untuk sekarang).

## SCOPE

Hanya ubah **path foto** di 3 dokumen workflow. **Tidak** mengubah:
- `prep_photos.py` script (biarkan, bisa dimatikan dari workflow saja)
- `engines/render.py` atau code engine
- MD subject yang sudah ada

## FILE YANG DI-EDIT

### 1. `v45/AUTORUN.md` — V4.5 daily render workflow

Cari step yang refer ke folder `1_prepped/`. Ubah path foto target dari:
```
{photos_dir}_prepped/
```
menjadi:
```
{photos_dir}/{Nama}/   (folder original)
```

**Catatan**: kalau Step prep masih dipanggil (`python prep_photos.py ...`) tapi outputnya tidak dipakai, **skip step itu** untuk hemat waktu. Edit AUTORUN.md jelaskan: "Step prep_photos.py di-skip mulai 2026-05-08 (Opsi A) — pakai folder original."

### 2. `v49/AUDIT_AGENT_PROMPT.md` — V4.9 audit subagent prompt

Cari `{photos_dir_prepped}` di template prompt. Ganti placeholder name + path-nya ke `{photos_dir_original}` yang point ke folder `{Nama}/`, bukan `1_prepped/`.

Baris terdampak (cari pattern):
```
- Foto folder: {photos_dir_prepped}
```
→
```
- Foto folder: {photos_dir_original}  (folder original .jpeg, BUKAN 1_prepped/)
```

### 3. `Ramalan/PROMPT_AUDIT_FOTO_ONLY.md` — External auditor prompt

Cari section "INPUT" yang refer ke `1_prepped/`. Ganti default ke folder original. Tambah catatan eksplisit:
```
Folder foto: C:\Users\sukam\OneDrive\Documents\Ramalan\foto\{TANGGAL_FOLDER}\{NAMA_SUBJECT_FOLDER}\
(ORIGINAL .jpeg, JANGAN pakai 1_prepped/.jpg karena upscale bikin hanzi blur — lihat DECISION_prep_photos_strategy.md)
```

## CHECKLIST EKSEKUSI

- [ ] Edit `v45/AUTORUN.md` — path foto switch ke original
- [ ] Edit `v49/AUDIT_AGENT_PROMPT.md` — path foto switch ke original
- [ ] Edit `Ramalan/PROMPT_AUDIT_FOTO_ONLY.md` — path foto switch ke original
- [ ] Edit `v45/AUTORUN.md` — note step prep_photos.py di-skip
- [ ] Update `Ramalan/v45/_AUDIT/DECISION_prep_photos_strategy.md` — mark Opsi A status `EXECUTED 2026-05-08`
- [ ] Test smoke: render 1 subject baru pakai original folder, cek tidak ada error path
- [ ] Lapor user: list file yang di-edit + summary diff per file

## VERIFIKASI POST-CHANGE

Saat render berikutnya:
1. Foto yang dibaca = `.jpeg` di folder `{Nama}/` (bukan `1_prepped/.jpg`)
2. Wall-clock turun ~30-60 detik (skip prep step)
3. Disk hemat ~50% (no duplicate prepped folder per render)

## ROLLBACK PLAN (kalau ada masalah)

Kalau original folder ternyata bermasalah untuk subject tertentu (foto miring/gelap):
- Manual fallback: render itu spesifik trigger pakai `1_prepped/` (override path)
- Atau roll forward ke Opsi B (refactor prep_photos.py jadi light-prep)

Tidak hapus `prep_photos.py` — tetap available kalau butuh.

## DEPENDENCY

Independent dari `HANDOFF_lixiangfa_MASTER.md`. **Tidak overlap.** Bisa dikerjakan paralel atau berurutan.

**Saran ordering** (paling smooth):
1. **Opsi A dulu** (5-10 menit) — patch config selesai
2. **MASTER lixiangfa** setelahnya — main agent baca foto pakai config baru (sudah point ke original)

Begitu Opsi A done, MASTER otomatis baca foto original tanpa perlu special-case path.
