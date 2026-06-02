# V7.1 Triple-Vote Test Mode (per-foto)

Test mode untuk validasi triple-vote workflow tanpa full PDF render. User kasih 1-N foto BaZi grid, agent jalankan 3 reader paralel + decision script per foto.

## Use case

User mau test akurasi triple-vote pada foto BaZi grid yang sudah ada (tidak butuh full subject MD/PDF). Hasil per foto = tabel 19 field × 3 reading + decision.

## Trigger prompt (paste di window baru)

```
TEST V7.1 triple-vote — baca foto BaZi grid, lapor hasil per foto.

Foto yang mau di-test:
1. {path/foto1.jpeg}
2. {path/foto2.jpeg}
3. {path/foto3.jpeg}
4. {path/foto4.jpeg}
5. {path/foto5.jpeg}

Untuk SETIAP foto, jalankan workflow ini:

1. Spawn 3 BaZi-specialist subagent paralel (slot A, B, C):
   - subagent_type: general-purpose
   - run_in_background: true
   - prompt: pakai template `v7.1/AUDIT_BAZI_PROMPT.md` dengan ganti placeholder:
     - {subject_id} → "test_foto{N}"  (mis. test_foto1, test_foto2, ...)
     - {photos_dir} → folder parent dari foto itu
     - {audit_logs_dir} → "v7.1/_AUDIT_LOGS"
     - PLUS modifikasi: subagent baca CUMA 1 foto spesifik (foto path tertentu), bukan scan folder
     - Output JSON: "test_foto{N}_agent_{slot}.json" (slot=A/B/C)

2. Tunggu 3 subagent selesai.

3. Run audit_decide.py dalam test mode:

   cd c:\Users\sukam\OneDrive\Documents\Ramalan\v7.1
   python audit_decide.py --test foto{N} _AUDIT_LOGS/test_foto{N}_agent_A.json _AUDIT_LOGS/test_foto{N}_agent_B.json _AUDIT_LOGS/test_foto{N}_agent_C.json

4. Print tabel hasil ke user.

Setelah 5 foto selesai, kasih ringkasan total:
- Berapa field PASS / STOP per foto
- Field mana yang paling sering STOP
- Confidence rata-rata
```

## Format output expected per foto

```
=== TEST foto1 ===
Sources: agent-A, agent-B, agent-C

Field                Agent A      Agent B      Agent C      Decision Value
------------------------------------------------------------------------------------
yong_shen            金(H)        金(H)        金(H)        ✅       '金'
xi_shen              土(H)        土(H)        土(M)        ✅       '土'
xian_shen            木(L)        水(L)        火(L)        🛑       None
chou_shen            水(H)        水(H)        水(H)        ✅       '水'
ji_shen              火(H)        火(H)        火(H)        ✅       '火'
xiantian_jia         0(H)         0(H)         0(H)         ✅       0
xiantian_yi          4(H)         4(H)         4(H)         ✅       4
...
canggan_tahun        辛癸己(H)   辛癸己(H)   辛癸己(H)   ✅       '辛癸己'
...

Summary: 17/19 PASS, 2 STOP
STOP fields: xian_shen, xiantian_wu
  • xian_shen: no_agreement (each reading different across 3 sources)
  • xiantian_wu: minority_more_confident (majority max=1, minority max=3)
```

## Modifikasi prompt subagent (untuk test mode 1 foto)

Karena `AUDIT_BAZI_PROMPT.md` template scan folder cari foto BaZi grid, untuk test mode kita kasih single-foto override. Tambahkan paragraf di atas isi prompt:

```
**TEST MODE OVERRIDE**: Baca CUMA foto ini (skip folder scan):
{specific_foto_path}

Output JSON ke {audit_logs_dir}/test_foto{N}_agent_{slot}.json (single file, single foto reading).
Schema sama dengan AUDIT_BAZI_PROMPT.md.
```

## Catatan

- 3 agent baca foto yang SAMA = test repeatability/consistency (bukan diversity).
- Kalau 3 agent baca beda untuk field tertentu = signal kuat foto itu memang ambigu di field itu.
- 5 foto × 3 agent = 15 spawn paralel. Token budget: ~40-60k total, wall-clock ~3-5 menit.
- Tidak ada PDF generation, tidak ada MD subjek baru ditulis. Cuma audit log JSON + result table di stdout.

## Path agar mudah dipaste

User di window baru tinggal copy-paste:

```
TEST V7.1 triple-vote 5 foto BaZi:

1. C:\Users\sukam\OneDrive\Documents\Ramalan\foto\09-05-2026\Zhuang Xiao Min\WhatsApp Image 2026-05-09 at 14.01.35.jpeg
2. C:\...\foto\foto2.jpeg
3. ...
4. ...
5. ...

Baca v7.1/TEST_TRIPLE_VOTE.md untuk workflow.
```

Window baru akan jalan otomatis pakai instruksi ini.
