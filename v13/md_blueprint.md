# NAMA_SUBJEK
# ============================================================
# V11 MD BLUEPRINT — copy file ini, isi dari foto, tulis null kalau tidak terlihat
# JANGAN ubah key name. JANGAN hapus key. JANGAN guess nilai — null kalau tidak ada.
# xi_yong_shen = 喜神 (BUKAN xi_shen — xi_shen tidak diparse engine)
# dm_pos_score / dm_neg_score = INTEGER e.g. 4100 (bukan +4.100)
# liu_nian_YYYY = umur|ganzhi|prose (WAJIB dua pipe, e.g. 24|丙午|Tekanan tahun...)
# yang_zhai_gua WAJIB ada kalau ada foto 陽宅 (e.g. 艮/坤/震/巽/離/坎/兌/乾)
# jie_e_palace_id WAJIB di ## DATA flat key — TAFSIR jie_e.insight tidak cukup
# ============================================================

## DATA

# === Identity ===
- nama: FILL
- hanzi: FILL
- gender_hz: FILL              # 陽男/陰男/陽女/陰女
- gender: FILL                 # Pria/Wanita
- shio_hz: FILL                # e.g. 蛇
- lahir_tanggal_lunar: FILL    # RAW dari foto: e.g. 民國42年5月23日 (農曆, verbatim)
- lahir_tanggal: FILL          # YYYY-MM-DD — WAJIB hasil `python lunar_convert.py`, JANGAN tebak
- lahir_jam: FILL              # HH:MM (24h)
- pilar_tahun: FILL            # 干/支 e.g. 辛/巳
- pilar_bulan: FILL            # 干/支
- pilar_hari: FILL             # 干/支
- pilar_jam: FILL              # 干/支

# === 先天體檢 (organ scores, integer 0-3) ===
- xiantian_jia: FILL           # 甲膽
- xiantian_yi: FILL            # 乙肝
- xiantian_bing: FILL          # 丙小腸
- xiantian_ding: FILL          # 丁心
- xiantian_wu: FILL            # 戊胃
- xiantian_ji: FILL            # 己脾
- xiantian_geng: FILL          # 庚大腸
- xiantian_xin: FILL           # 辛肺
- xiantian_ren: FILL           # 壬膀胱
- xiantian_gui: FILL           # 癸腎

# === 喜用神 5-shen panel (dari foto — posisi atas ke bawah) ===
- yong_shen: FILL              # 用神 e.g. 水
- xi_yong_shen: FILL           # 喜神 e.g. 土  ← WAJIB xi_yong_shen bukan xi_shen
- xian_shen: FILL              # 閒神 e.g. 金
- chou_shen: FILL              # 仇神 e.g. 木
- ji_shen: FILL                # 忌神 e.g. 火

# === 格局 Format (dari foto BaZi — 食神用事 → 食神格) ===
- format: null                 # e.g. 食神格/正官格/七殺格 — null kalau tidak ada foto

# === DM Strength (dari foto 批命備註) ===
- dm_pos_score: null           # INTEGER e.g. 4100 — null kalau tidak ada foto
- dm_neg_score: null           # INTEGER e.g. 3800 — null kalau tidak ada foto

# === 大運 Da Yun ===
- da_yun_arah: FILL            # 順行/逆行
- da_yun_start_age: FILL       # integer e.g. 3
- da_yun: FILL                 # format: age:ganzhi:ten_god, ... e.g. 10:己亥:正印, 20:戊戌:偏印

# === 婚配 Marriage ===
- marriage_cocok_shio_hz: FILL         # e.g. 牛, 雞
- marriage_hindari_shio_hz: FILL       # e.g. 虎, 猴, 豬
- marriage_cocok_tafsir: FILL          # WAJIB BAHASA INDONESIA — terjemahan prose cocok dari foto 婚配 (BUKAN transkripsi Chinese)
- marriage_hindari_tafsir: FILL        # WAJIB BAHASA INDONESIA — terjemahan prose hindari dari foto 婚配 (BUKAN transkripsi Chinese)
- marriage_cocok_relationships: null   # FORMAT: 未:大吉, 卯:大吉, 寅:吉凶相半 — WAJIB isi kalau ada tier beda per shio
                                       # 大吉=SANGAT COCOK, 吉凶相半=CUKUP COCOK, null=semua tampil COCOK (default)
                                       # Branch (地支), bukan shio-hanzi. Lihat foto 婚配 bagian rating per shio.

# === 陽宅 Yang Zhai (dari foto — gua WAJIB diisi) ===
- yang_zhai_gua: null                  # WAJIB kalau ada foto: 艮/坤/震/巽/離/坎/兌/乾
- yang_zhai_zone_rumah_hz: null        # e.g. 東北, 西南
- yang_zhai_zone_rumah_note: null
- yang_zhai_zone_pintu_hz: null
- yang_zhai_zone_pintu_note: null
- yang_zhai_zone_dapur_hz: null
- yang_zhai_zone_dapur_note: null
- yang_zhai_zone_kamar_hz: null
- yang_zhai_zone_kamar_note: null
- yang_zhai_zone_ranjang_hz: null
- yang_zhai_zone_ranjang_note: null
- yang_zhai_zone_altar_hz: null          # 神位 — WAJIB kalau ada di foto
- yang_zhai_zone_altar_note: null
- yang_zhai_zone_kamar_mandi_hz: null
- yang_zhai_zone_kamar_mandi_note: null

# === 紫微 Zi Wei ===
- ziwei_ming_zhu: FILL         # e.g. 祿存
- ziwei_shen_zhu: FILL         # e.g. 天機
- ziwei_ming_gong: FILL        # branch e.g. 寅
- ziwei_shen_gong: FILL        # branch e.g. 戌
- ziwei_wu_xing_ju: FILL       # e.g. 木三局
- ziwei_shi_jun: FILL          # e.g. 子
- ziwei_su_ming: FILL          # prose dari foto 宿命

# === 適業 Career (ZiWei) ===
- ziwei_career_recommended_hz: FILL    # dari foto
- ziwei_career_recommended_id: FILL    # terjemahan Indonesia
- ziwei_career_alternate_hz: null      # opsional
- ziwei_career_alternate_id: null      # opsional
# WAJIB: shiye_favorable_full dan shiye_supportive_full pakai format: 漢字|Indonesia, 漢字|Indonesia
# Jangan pakai 、(Chinese comma) — harus koma biasa dan pipe per item
- shiye_favorable_full: null           # format: 鋼鐵工廠|Pabrik baja, 五金行|Toko besi, ...
- shiye_supportive_full: null          # format: 醫師|Dokter, 記者|Jurnalis, ...

# === 命宮 Ming Gong (WAJIB di sini DAN di TAFSIR) ===
- palace_ming_gong_insight: FILL  # terjemah penuh dari foto 命宮 (dari prompt), no ringkas, ≥95% klausa

# === 疾厄 Jie E (WAJIB di sini — bukan hanya TAFSIR) ===
- jie_e_palace_id: FILL        # terjemahan penuh dari foto palace 疾厄
- jie_e_organ_focus_id: null   # organ utama — opsional

# === 神煞 Shen Sha (format: hz|pinyin|label_id|tafsir_hz|tafsir_id) ===
- shen_sha_detail_1: null      # e.g. 華蓋|Hua Gai|Mahkota Pelangi|求學能自動...|Kemampuan...
- shen_sha_detail_2: null
- shen_sha_detail_3: null
- shen_sha_detail_4: null
# tambah shen_sha_detail_5 dst kalau ada lebih dari 4

# === 流年 Liu Nian (format WAJIB: umur|ganzhi|prose) ===
# Kalimat pertama WAJIB diawali "Tahun YYYY..." dan pembuka antar-tahun harus diparafrasekan secara bervariasi.
# Jika foto memakai struktur berulang, pertahankan seluruh makna tetapi hindari pola kalimat Indonesia yang identik.
- liu_nian_2026: null          # e.g. 24|丙午|Tekanan tahun ini...
- liu_nian_2027: null
- liu_nian_2028: null
- liu_nian_2029: null
- liu_nian_2030: null
- liu_nian_2031: null
# sesuaikan tahun dengan tahun prediksi di foto

# === 八字秤骨 Bone Weight (dari foto 先天論命 秤骨 — null kalau tidak ada foto) ===
- bone_weight_year: null       # e.g. 五錢  (dari baris 年)
- bone_weight_month: null      # e.g. 一兩八錢 (dari baris 月)
- bone_weight_day: null        # e.g. 一兩七錢 (dari baris 日)
- bone_weight_hour: null       # e.g. 七錢  (dari baris 時)
- bone_weight_total: null      # e.g. 四兩七錢 (秤骨輕重 total)
- bone_weight_poem_hz: null    # 詩曰 verbatim dari foto (pisah dengan ；)
- bone_weight_poem_id: null    # terjemahan Indonesia poem — WAJIB kalau poem_hz diisi

# === 古書云 Gushu Quote ===
- gushu_quote_1: null          # prose dari foto — null kalau tidak ada

# === Kesimpulan (sintesis akhir) ===
- kesimpulan_narrative: FILL   # prose panjang Indonesia — synthesis dari semua data

## TAFSIR

### Kepribadian

paragraf:
FILL — prose 2-3 kalimat: Day Master + format + unsur sahabat (yong/ji shen). Pakai nama subjek.

power:
- FILL — kelebihan utama dari foto (1 kalimat per bullet)
- FILL

shadow:
- FILL — kelemahan dari foto
- FILL

optimum:
- FILL — saran tindakan dari foto
- FILL

### Kepribadian Detail

# FORMAT WAJIB: poin: diikuti list "- kalimat" (1 baris per poin)
# JANGAN tulis poin: nilai_inline — wajib list terpisah
poin:
- FILL — poin 1 dari foto 性情 (verbatim, 1 kalimat per bullet)
- FILL — poin 2
- FILL — poin 3

### Sekilas Hidup

# FORMAT WAJIB: card: (baris kosong) lalu "- Label | teks" per baris
# JANGAN tulis "card: Label | teks" inline — parser TIDAK baca format itu → halaman KOSONG
card:
- FILL Label | FILL teks dari foto 全局總論
- FILL Label | FILL teks
- FILL Label | FILL teks

### Keluarga & Pasangan

pasangan:
- vibe: FILL — e.g. "Penuh Gairah · Butuh Keseimbangan"
- headline: FILL — e.g. "Pasangan ideal dari shio Kerbau atau Ayam"
- cocok_list:
  - shio: FILL — hanzi shio e.g. 牛 (Kerbau)
    label: 大吉
    teks: FILL — prose dari foto 婚配
- hindari_list:
  - shio: FILL — hanzi shio e.g. 虎 (Harimau)
    teks: FILL — prose dari foto 婚配

### Karir & Industri

# WAJIB diisi — tanpa ini kartu besar "Wawasan Utama" halaman Karir tampilkan teks orang lain (template default)
# intro: = 1-2 kalimat SATU BARIS. Section name WAJIB "### Karir & Industri" (bukan "### Career")
intro: FILL — prose 1-2 kalimat (SATU BARIS): Day Master + format + yong/xi shen → kecenderungan bidang karir. Pakai nama subjek. Sebutkan ji shen yg dihindari.

### Palace Detail 1

ming_gong:
- star: null                   # bintang utama e.g. 七殺
- insight: null                # terjemahan PENUH verbatim dari foto — DILARANG singkat
- action: null

xiongdi:
- star: null
- insight: null
- action: null

fuqi:
- star: null
- insight: null
- action: null

zinu:
- star: null
- insight: null
- action: null

### Palace Detail 2

caibo:
- star: null
- insight: null
- action: null

jie_e:
- star: null
- insight: null
- action: null

qianyi:
- star: null
- insight: null
- action: null

puyi:
- star: null
- insight: null
- action: null

### Palace Detail 3

guanlu:
- star: null
- insight: null
- action: null

tianzhai:
- star: null
- insight: null
- action: null

fude:
- star: null
- insight: null
- action: null

fumu:
- star: null
- insight: null
- action: null

### Sintesis & Saran Aksi

> Wajib diisi dari foto 命宮 / 全局總論. Kalau tidak ada foto tersebut, gunakan foto palace yang paling relevan.
> DILARANG: mengarang, paraphrase generik, canonical default. Harus spesifik per subjek.

opening: null
# Kalimat pembuka 1–2 kalimat — rangkuman karakter utama subjek dari 命宮 / 全局.
# Contoh: "JS adalah sosok yang tegas dan visioner, dengan daya tahan mental di atas rata-rata."

trio:
  kekuatan: null
  # Kekuatan utama subjek dalam 1 kalimat. Dari foto — BUKAN generik.
  tantangan: null
  # Tantangan atau hambatan utama. Dari foto.
  tindakan: null
  # Rekomendasi tindakan inti. Dari foto.

actions:
- title: null
  context: null
  tag: null
# Format 5 baris wajib. Setiap action: title (3–5 kata), context (1 kalimat), tag (1 kata kunci).
# Contoh:
# - title: Perkuat Fondasi Finansial
#   context: Periode ini membuka peluang akumulasi aset — prioritaskan investasi jangka panjang.
#   tag: Finansial
# - title: Kelola Emosi di Relasi
#   context: Tekanan di lingkungan kerja bisa terbawa ke hubungan — latih komunikasi terbuka.
#   tag: Relasi
