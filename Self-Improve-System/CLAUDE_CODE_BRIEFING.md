# 🧠 Claude Code Agent Briefing — Ramalan PDF Generator

> **Status Proyek:** Multi-workstream aktif | V3 = Production | V4 = Staged | Beberapa eksperimen berjalan paralel

---

## 📁 Struktur Branch yang Direkomendasikan

```
main (V3 — PRODUCTION, tidak boleh disentuh langsung)
│
├── hotfix/v3-patch              ← revisi kecil V3
├── feature/v4-testing           ← uji coba V4
├── experiment/photo-vs-data     ← eksperimen foto vs nama+tanggal lahir
└── feature/parallel-generate    ← generate harian paralel (bukan antre 1-1)
```

### Setup Git Worktree (jalankan sekali)

```bash
# Dari folder root project (main/V3)
git worktree add ../project-v3-patch    hotfix/v3-patch
git worktree add ../project-v4          feature/v4-testing
git worktree add ../project-experiment  experiment/photo-vs-data
git worktree add ../project-parallel    feature/parallel-generate
```

Hasil: 5 folder aktif, masing-masing independen, tidak saling mengganggu.

```
project/               ← V3 production — daily generate tetap jalan di sini
project-v3-patch/      ← revisi kecil
project-v4/            ← testing V4
project-experiment/    ← eksperimen foto vs data
project-parallel/      ← generate paralel
```

---

## 📋 Briefing Per Workstream

---

### 🟢 Workstream 1 — V3 Patch (Revisi Kecil)

**Branch:** `hotfix/v3-patch` | **Folder:** `project-v3-patch/`

```
CONTEXT:
- Ini adalah branch hotfix dari V3 production
- V3 adalah software generator ramalan PDF dari HTML menggunakan foto sebagai input
- V3 sedang aktif digunakan untuk daily generate — jangan ganggu

TASK:
[Isi revisi spesifik yang kamu inginkan di sini]

CONSTRAINT:
- Perubahan harus backward-compatible dengan V3
- Jangan ubah arsitektur atau refactor besar
- Jangan sentuh file core yang tidak berhubungan dengan revisi
- Setelah selesai, output ringkasan: file apa saja yang berubah dan kenapa

DONE CRITERIA:
- Generate 1 sample PDF dari foto berhasil tanpa error
- Output PDF secara visual tidak berbeda dari V3 production
- Ada summary diff yang bisa direview sebelum merge
```

---

### 🔵 Workstream 2 — V4 Testing

**Branch:** `feature/v4-testing` | **Folder:** `project-v4/`

```
CONTEXT:
- V4 sudah dibuat tapi belum pernah diuji
- V3 production ada di folder ../project (jangan disentuh)
- Tujuan utama: validasi apakah V4 siap menggantikan V3

TASK:
1. Audit V4 terlebih dahulu:
   - List semua perbedaan V4 vs V3 (file, fungsi, dependensi)
   - Identifikasi perubahan yang berisiko atau belum jelas tujuannya
2. Jalankan test generate untuk minimal 3 sample foto berbeda
3. Ukur dan catat waktu generate per step per orang vs V3
4. Catat semua error, warning, atau output yang tidak sesuai ekspektasi
5. Simpan semua hasil di /test-results/v4-report.md

CONSTRAINT:
- Jangan merge ke main tanpa approval eksplisit
- Kalau ada bug, fix di branch ini — jangan ambil shortcut
- Jangan modifikasi sample input yang sama yang dipakai V3

DONE CRITERIA:
- Generate berhasil tanpa error untuk semua sample
- Waktu generate lebih cepat atau minimal setara V3
- Kualitas PDF output tidak turun dari V3
- /test-results/v4-report.md sudah terisi lengkap
```

---

### 🟡 Workstream 3 — Eksperimen: Foto vs Nama + Tanggal Lahir

**Branch:** `experiment/photo-vs-data` | **Folder:** `project-experiment/`

```
CONTEXT:
- Ini eksperimen mandiri, tidak ada tekanan production
- Goal: validasi apakah ramalan dari (nama + tanggal lahir saja) 
  bisa menghasilkan output yang "cukup mirip" dengan ramalan dari foto
- Kalau hasilnya cukup mirip → foto tidak wajib diminta ke user
  (cukup minta nama dan tanggal lahir saja)

TASK:
1. Buat dua pipeline terpisah:
   - Pipeline A: input foto → generate ramalan (reuse flow V3)
   - Pipeline B: input nama + tanggal lahir → generate ramalan (buat baru)
2. Buat mekanisme perbandingan output:
   - Bandingkan tema/topik ramalan (bukan kata per kata)
   - Bisa pakai similarity sederhana atau rubrik manual (misal: 
     "tema keberuntungan sama?", "tema hubungan sama?", dll)
3. Test dengan minimal 5 sample orang yang sudah tersedia fotonya
4. Simpan hasil di /test-results/experiment-report.md

CONSTRAINT:
- Ini pure eksperimen — jangan ada perubahan di codebase V3
- Fokus ke: apakah TEMA ramalan konsisten, bukan identik kata per kata
- Kalau Pipeline B butuh prompt baru ke Claude API, tulis prompt-nya 
  secara eksplisit agar bisa direview

DONE CRITERIA:
- Ada laporan: dari X sample, Y% hasilnya "cukup mirip" secara tema
- Ada rekomendasi konkret: apakah foto bisa dihilangkan dari flow atau tidak
- Ada threshold yang diusulkan (misal: "kalau similarity > 70%, foto opsional")
```

---

### ⚡ Workstream 4 — Performance: Profiling & Fix Generate yang Lambat

**Branch:** `hotfix/v3-patch` (bisa digabung) atau branch terpisah | **Folder:** sesuaikan

```
CONTEXT:
- V3 saat ini lambat saat generate untuk banyak orang
- Belum diketahui pasti di step mana bottleneck-nya

TASK:
1. PROFILING DULU sebelum apapun:
   Tambahkan timer di setiap step utama:
   - Baca & proses input foto
   - API call ke Claude (vision/analysis)
   - Render/generate HTML dari hasil analisis
   - Convert HTML ke PDF
2. Jalankan minimal 3 sample, catat waktu per step per run
3. Identifikasi step mana yang paling lama
4. Baru propose solusi konkret berdasarkan data — contoh:
   - Parallelisasi API call
   - Cache hasil analisis foto
   - Lazy load asset HTML
   - Optimize PDF rendering
5. Simpan hasil di /test-results/perf-report.md

CONSTRAINT:
- DILARANG optimize atau refactor sebelum profiling selesai
- Solusi yang dipropose harus disertai estimasi gain waktu
- Kalau fix masuk ke V3 langsung, pastikan tidak break flow existing

DONE CRITERIA:
- Diketahui dengan pasti step mana yang bottleneck (dengan data waktu)
- Ada proposal konkret + estimasi gain
- Kalau sudah diimplementasi: ada before/after benchmark
```

---

### 🚀 Workstream 5 — Parallel Daily Generate (Tidak Perlu Antre 1 per 1)

**Branch:** `feature/parallel-generate` | **Folder:** `project-parallel/`

```
CONTEXT:
- Saat ini daily generate berjalan sequential: orang 1 selesai → baru orang 2
- Goal: bisa generate untuk beberapa orang secara bersamaan (concurrent)
- Ini workstream terpisah — jangan modifikasi V3 production langsung

TASK:
1. Analisis flow generate V3 yang ada:
   - Identifikasi bagian mana yang bisa diparalelkan
   - Identifikasi shared resource yang bisa jadi race condition 
     (file output, API rate limit, temp folder, dll)
2. Implementasi concurrent generate, pilih approach yang paling sesuai:
   - Opsi A: asyncio / ThreadPoolExecutor (kalau Python)
   - Opsi B: Promise.all / worker threads (kalau Node.js)
   - Opsi C: queue system sederhana (kalau butuh kontrol lebih)
3. Pastikan:
   - Output file per orang tidak saling overwrite
   - Error satu orang tidak crash orang lain
   - Ada logging yang jelas: siapa sedang diproses, siapa sudah selesai
4. Test dengan 3–5 orang sekaligus
5. Simpan hasil di /test-results/parallel-report.md

CONSTRAINT:
- Jangan merge ke main sebelum ditest dengan minimal 3 orang sekaligus
- Rate limit Claude API harus diperhatikan — jangan kirim semua sekaligus 
  tanpa throttle
- Kalau pakai queue, buat queue-nya simple dulu — jangan over-engineer

DONE CRITERIA:
- Bisa generate minimal 3 orang secara bersamaan tanpa error
- Output masing-masing orang benar (tidak tertukar)
- Waktu total lebih cepat dibanding sequential
- /test-results/parallel-report.md sudah terisi
```

---

## 🔄 Urutan Prioritas yang Disarankan

```
Segera (hari ini / besok):
  [1] Setup Git Worktree → isolasi semua workstream (10 menit)
  [2] Workstream 4 (Profiling) → tahu dulu lambatnya di mana

Paralel setelah setup:
  [3] Workstream 2 (V4 Testing) → jalan di terminal terpisah
  [4] Workstream 1 (V3 Patch)   → revisi kecil, merge cepat

Setelah profiling selesai:
  [5] Workstream 5 (Parallel Generate) → pakai data profiling sebagai baseline

Paling santai (tidak urgent):
  [6] Workstream 3 (Eksperimen foto vs data) → riset jangka panjang
```

---

## 🔀 Merge Protocol (Kapan Boleh Merge ke Main)

Setiap workstream hanya boleh merge ke `main` setelah memenuhi semua ini:

| Checklist | Keterangan |
|---|---|
| ✅ Test generate berhasil | Minimal 3 sample, tidak ada error |
| ✅ Output PDF tidak turun kualitas | Bandingkan visual dengan V3 |
| ✅ Ada test-results report | File .md di /test-results/ terisi |
| ✅ Ada approval eksplisit | Kamu (owner) sudah review dan setuju |
| ✅ Daily generate V3 tidak terganggu | Cek dulu sebelum merge |

```bash
# Setelah semua checklist terpenuhi:
cd project/         # masuk ke main
git merge hotfix/v3-patch   # atau branch yang relevan

# Cleanup setelah merge
git worktree remove ../project-v3-patch
git branch -d hotfix/v3-patch
```

---

> ## ⚠️ Disclaimer Penting untuk Claude Code
>
> **Briefing ini dibuat tanpa melihat struktur folder, codebase, dan sistem aktual yang sudah berjalan.**
>
> Artinya:
> - Nama file, fungsi, dependensi, dan flow yang disebutkan di sini **bisa tidak sesuai** dengan kondisi nyata proyekmu
> - Beberapa saran mungkin **tidak relevan** atau **sudah diterapkan** di V3/V4
> - Beberapa asumsi tentang stack teknologi (Python/Node.js, Puppeteer, dll) **belum diverifikasi**
>
> **Yang harus dilakukan Claude Code sebelum mengeksekusi apapun:**
> 1. Baca dan pahami struktur folder yang ada terlebih dahulu
> 2. Identifikasi mana dari briefing ini yang relevan dan mana yang tidak
> 3. Kalau ada bagian yang tidak cocok dengan kondisi aktual — **abaikan dan usulkan solusi yang lebih sesuai**
> 4. Jangan eksekusi perubahan besar tanpa konfirmasi ulang ke owner
>
> *Briefing ini adalah panduan arah, bukan instruksi yang harus diikuti kata per kata.*
