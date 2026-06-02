# PROMPT TAMBAHAN — Kesimpulan personalisasi (5 stat desc + life map)

> Paste ke Web Claude (chat existing yang sudah punya foto + MD subjek), satu kali per subjek.

---

Saya butuh tambahan field untuk halaman Kesimpulan di PDF subjek ini. Semua data DATA + TAFSIR sudah Anda generate sebelumnya — TAMBAHKAN field-field di bawah ini sebagai blok terpisah, **JANGAN regenerate seluruh MD**.

Konteks: 6 stat cards di halaman Kesimpulan saat ini menampilkan deskripsi generic. Saya butuh deskripsi PERSONAL per subjek + narasi peta hidup 3-fase (lalu / sekarang / berikutnya).

## ATURAN KETAT

- Output HANYA blok markdown di bawah ini (tidak ada teks pengantar).
- Patuhi budget kata SETIAP field.
- Pakai konvensi `[[Hanzi]]` untuk istilah teknis.
- Sebut nama subjek di sekitar 30% kalimat (bukan "Anda" terus).
- Kalau Anda ragu untuk satu field, tulis `null` (engine akan fallback ke deskripsi generic).

## FORMAT OUTPUT (paste ke chat lalu copy hasilnya)

```markdown
### Kesimpulan — Tambahan

stats:
- format_desc: {MAX 18 kata. Bagaimana format BaZi (mis. [[偏印格]]) memengaruhi karakter & jalur hidup subjek secara konkret.}
- yong_desc: {MAX 18 kata. Bagaimana yong shen (unsur pendukung) sebaiknya diaktifkan subjek dalam hidup sehari-hari.}
- dayun_desc: {MAX 18 kata. Tema inti fase Da Yun yang sedang dijalani — apa yang harus difokuskan/dihindari di rentang umur ini.}
- umur_desc: {MAX 18 kata. Karakter dekade umur subjek saat ini — peluang & tantangan utama.}
- kompat_desc: {MAX 18 kata. Pola relasi (cocok + hindari) yang paling perlu diingat subjek dalam memilih pasangan/mitra.}

life_map:
- lalu: {MAX 30 kata. Ringkasan fase-fase yang sudah dilewati subjek — elemen dominan, tema utama, hasil tempaan.}
- sekarang: {MAX 30 kata. Fase saat ini + tema pemurnian/pertumbuhan/transformasi yang sedang dijalani subjek.}
- berikutnya: {MAX 30 kata. Preview fase mendatang — apa yang dipanen, ke mana arah, transisi seperti apa.}
```

Mulai output sekarang.
