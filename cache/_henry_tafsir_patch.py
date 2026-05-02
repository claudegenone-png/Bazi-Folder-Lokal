"""
Tafsir patch — generate 3-5 bullet tafsir per category for Henry,
linking transcript content to:
  - Day Master 庚金 (Logam Yang Kuat) — Format 偏印格
  - Shio 寅 Macan, year pillar 壬寅
  - 喜用神 水, 木  ·  忌神 金, 土
  - Current 大運 丙辰 (七殺, age 55-64) — fase tantangan + transformasi
  - Zi Wei: 命主 廉貞, 身主 天梁, 命宮 申, 身宮 寅, 五行局 土五局
  - Gender M, age 64

Bullets singkat, padat, pemberdayaan, etika reframing.
"""
import json
from pathlib import Path

INPUT = Path(__file__).parent / "_input_henry.json"

TAFSIR = {
    "性情": [
        "Kombinasi 庚金 + 偏印格 yang Anda bawa membuat tegar dan cepat eksekusi adalah kekuatan inti — dipakai dengan tepat, ini menjadi modal kepemimpinan teknis yang langka.",
        "Sifat “suka jadi sorotan” di umur 60-an cocok dialihkan ke peran mentor / penasihat — energi pejuang Anda lebih bernilai saat membentuk orang lain daripada ikut bersaing langsung.",
        "Karena Anda “memberi sambil berharap dihargai”, latih ekspektasi: niatkan memberi sebagai investasi karakter, bukan transaksi. Kepuasan jadi lebih konsisten.",
        "Di fase 大運 丙辰 (七殺, 55-64) sekarang, sisi keras Anda sedang diuji. Pakai elemen 水 (Air) — diam-tenang-mengamati — untuk mendinginkan keputusan sebelum eksekusi.",
        "Saudari kandung dan pasangan adalah “sensor” karakter Anda. Saat mereka sebut Anda terlalu keras, anggap itu data, bukan serangan.",
    ],
    "全局總論": [
        "Pola “bukan pemegang kekuasaan besar tapi eksekutor handal” adalah keunggulan, bukan kekurangan — banyak organisasi mati karena pemimpin tidak punya orang seperti Anda.",
        "Pasangan yang cerdas + ekstrover adalah pasangan komplementer untuk 庚金 yang condong introspektif; biarkan dia jadi “suara keluar”, Anda jadi “otak proses”.",
        "Anak laki-laki yang lembut hati di palace 子女 dengan 天府 mengindikasikan stabilitas keluarga — peran Anda di umur ini adalah memberi mereka panggung, bukan menutupi mereka.",
        "Resistensi pada saudari & atasan = tanda Anda butuh otonomi tinggi. Negosiasikan ruang gerak di awal kerjasama, jangan tunggu konflik.",
    ],
    "神煞": [
        "Bintang 驛馬 di bagan Anda + Day Master 庚金 + 大運 丙辰 yang dinamis = pola hidup “gerak” adalah natural state, bukan kebetulan. Memaksa diam justru bikin macet.",
        "Manfaatkan 驛馬 di umur 60-an untuk perjalanan yang punya makna: ziarah, edukasi, kunjungan keluarga jauh — bukan sekadar plesir.",
        "Bila ada gejolak di hunian / pekerjaan, baca itu sebagai sinyal 驛馬 minta disalurkan. Pindah ruangan, redekorasi, atau perjalanan 1-2 minggu sering kali cukup.",
        "Karena 驛馬 mendorong banyak perubahan, jaga dokumen & administrasi tetap rapi — itu modal bergerak yang sering diabaikan.",
    ],
    "財富": [
        "Kombinasi 正財 + 偏財 yang sama-sama berlimpah jarang. Aturan emas: 正財 (gaji/hasil tetap) untuk pondasi & jangka panjang, 偏財 (komisi/spekulasi) untuk eksperimen — jangan dibalik.",
        "庚金 strong + 喜用神 水木: rezeki Anda lebih lancar di sektor yang berkaitan dengan aliran (logistik, perdagangan, distribusi) daripada akumulasi statis.",
        "Di 大運 丙辰 sekarang, hindari over-leveraging. 七殺 cenderung memunculkan peluang besar yang juga berisiko besar; pakai aturan max 20% modal untuk peluang spekulatif.",
        "Latih disiplin: setiap rezeki tak terduga (偏財) langsung sisihkan ≥30% ke tabungan / investasi defensif sebelum digunakan.",
    ],
    "婚配": [
        "Hindari shio Ular & Monyet bukan vonis — itu sinyal pola karakter yang berisiko bentrok dengan 庚金 Anda. Kalau pasangan dekat ber-shio itu, kompensasi lewat komunikasi & batas waktu istirahat.",
        "Shio Kuda + Anjing (三合 dengan Macan) adalah dukungan natural — di lingkungan kerja, prioritaskan kerja sama dengan mereka untuk proyek penting.",
        "Saran “lebih baik telat menikah” sudah lewat di kasus Anda; tafsir ulang: jaga pernikahan dengan ritme “api yang stabil” — fokus pada konsistensi harian, bukan ledakan emosi.",
        "Pasangan cerdas + ekstrover adalah pelengkap, bukan saingan. Beri panggung, beri otonomi keuangan rumah tangga — itu cara 庚金 menampung 太陰 di palace 夫妻.",
    ],
    "事業": [
        "Daftar industri klasik panjang, tapi yang paling sesuai dengan 喜用神 水木 Anda: penerbitan, pendidikan, perdagangan, logistik, kerajinan kayu/seni — semua mengalir & menumbuhkan.",
        "Industri yang berunsur 金 dan 土 (logam berat, mining, properti tanah-kering) disebut software, tapi waspada: itu menambah dominasi 庚金 yang sudah kuat — energi macet, profit lambat.",
        "Di umur 60-an + 大運 丙辰, peran terbaik adalah “arsitek senior / penasihat” — bisnis yang mengandalkan reputasi & jaringan, bukan operasional harian melelahkan.",
        "Bila membuka usaha baru, partner 喜用神 水/木 (orang air/kayu — biasanya tipe komunikatif/edukatif) lebih cocok daripada partner sesama 庚金.",
    ],
    "陽宅": [
        "Hexagram 坤 di bagan rumah Anda menggarisbawahi tema “stabilitas + penerima” — rumah Anda berperan sebagai pondasi, bukan panggung.",
        "Arah hadap Timur Laut ↔ Barat Daya selaras dengan format 偏印格 Anda; manfaatkan untuk meja kerja & ruang baca — fokus mental Anda paling tajam di sumbu ini.",
        "Pintu utama di Barat / Barat Laut OK secara teori, tapi tambahkan elemen 水 (akuarium kecil, fountain mini, atau sekadar warna biru gelap) di area tersebut untuk menghidupkan 喜用神 Anda.",
        "Kompor di Timur / Barat aman; hindari menambah unsur Tanah berat (batu besar, gerabah jumbo) di area dapur — itu memperberat 忌神 土 Anda.",
        "Toilet di Utara / Timur / Tenggara / Selatan aman; periksa instalasi air rutin — 水 yang bocor di area “netral” bisa jadi penanda gangguan rezeki kecil.",
    ],
    "古書云": [
        "Garis besar kitab klasik konsisten: 庚金 Anda butuh ditempa Api & dibersihkan Air — bukan dilindungi terus-menerus. Tantangan yang datang adalah “tempaan”, bukan hukuman.",
        "Kalimat “kalah dari adik 乙 (Kayu Yin)” menjelaskan pola Anda: lawan paling sulit ditangani adalah orang lemah-lembut yang sabar — mereka tidak bisa Anda tebas dengan ketegasan.",
        "Pesan praktis: jangan cari medan datar. Kelas Anda baru muncul saat menghadapi masalah berat — atur hidup supaya selalu ada satu “tantangan layak” di depan.",
        "Hindari lingkungan terlalu kering (忌 土 berlebih) maupun air terlalu dalam (terlalu banyak distraksi/spekulasi). Cari ekuilibrium — ini juga sesuai dengan 偏印格 yang butuh keseimbangan input.",
    ],
    "命宮": [
        "巨門 + resonansi 廉貞 di 命宮 申 Anda = tipe komunikator-pejuang. Kekuatan utama: artikulasi tajam dan eksekusi cepat — keduanya langka dimiliki bersamaan.",
        "Sisi “seperti api” mudah membakar. Aturan praktis untuk umur 60-an: tunda respon 24 jam sebelum mengirim pesan/email yang emosional.",
        "Ingatan emosional yang dalam adalah modal sebagai mentor / cerita-pemberi-makna — namun jangan dipakai sebagai amunisi konflik lama.",
        "Day Master 庚金 + 命宮 申 (rumah Logam) = lapisan ganda Logam. Itu sebab Anda kokoh, tapi juga sebab Anda butuh ekstra Air (relaksasi, refleksi) supaya tidak getas.",
        "Peran ideal di 大運 丙辰 sekarang: bukan front-line, tapi “suara keras yang dipakai sengaja” — pengarah, juri, kritikus konstruktif.",
    ],
    "夫妻": [
        "Pola “api cepat menyala lalu cepat padam” adalah ciri 庚金 + palace 夫妻 yang dinamis. Solusi: bangun ritual harian (sarapan/teh sore bersama) — itu yang menjaga bara.",
        "Kelebihan Anda dalam berpisah dengan tegas (tidak menggantung) sebenarnya berkah — di umur sekarang, terapkan ini untuk konflik kecil: selesaikan hari ini, jangan dipendam.",
        "Saran “晚婚” sudah tidak relevan secara harfiah, tapi prinsipnya hidup: matangkan setiap fase pernikahan baru (anak menikah, pensiun, pindah rumah) sebagai 'pernikahan ulang'.",
        "Pasangan + Wen Chang/Wen Qu yang disebut transkrip = kalau pasangan Anda artistik/edukatif, dukung secara finansial; itu langsung memperkuat 喜用神 Anda.",
        "Hindari menjadi “api yang membakar” saat lelah; pakai sinyal pribadi (mis. minum air) sebelum percakapan berat dengan pasangan.",
    ],
    "子女": [
        "天府 di palace 子女 = anak Anda sebenarnya “lumbung” — mereka tipe yang menjaga & menampung. Peran Anda bukan lagi menyetir, tapi memberi ruang & restu.",
        "Anak laki-laki yang berbakti perlu didorong mengambil tanggung jawab sendiri, jangan dilindungi terus — kalau tidak, kebaikan mereka akan mandeg.",
        "Di umur 60-an, transfer pengetahuan adalah hadiah terbesar untuk anak — terstruktur (catat dalam tulisan), bukan hanya verbal.",
        "Kalau Anda merasa anak “tidak memberi cukup”, baca ulang tafsir asli: peringatannya tentang “apabila ada bintang jahat”. Tanpa itu, dukungan mereka adalah natural — biarkan datang dengan ritme mereka.",
    ],
    "疾厄": [
        "庚金 dengan unsur 金 dominan + transkrip menyebut liver, mata, kaki-pinggang: pola Logam-keras yang minim relaksasi. 喜用神 水 Anda secara fisik = hidrasi cukup + tidur teratur.",
        "Untuk masa kecil yang sering bengkak/cedera + 大運 丙辰 (七殺, fase tegang): periksa stress level, bukan hanya gula/tensi — 七殺 sering bermanifestasi di sistem saraf.",
        "Latihan postur (pinggang) dan check-up liver tahunan adalah dua investasi kesehatan dengan ROI tertinggi untuk pola Anda.",
        "Mata mudah lelah: kurangi screen-time setelah jam 9 malam — Logam butuh “gelap” untuk reset.",
        "Sumber stres terbesar untuk 庚金 sering bukan beban kerja, tapi konflik nilai. Jaga diri dari relasi yang membuat Anda merasa “diperlakukan tidak fair” berkepanjangan.",
    ],
    "遷移": [
        "Pola “gerakan lancar tapi hidup tidak pernah tenang” adalah karakter 寅 + 驛馬 + 庚金 — bukan kutukan, itu energi natural. Resep: bukan menghindari gerakan, tapi memilih ritme yang Anda mampu.",
        "Saat Anda merasa stuck, satu intervensi paling murah: 1-2 minggu pindah lingkungan (rumah saudara, cottage, hotel kerja) — sering itu cukup mereset 大運 丙辰.",
        "Saran klasik “tahan emosi di dalam” perlu di-update: tahan reaksi cepat, tapi tetap proses emosi (jurnal, bicara dengan teman) — kalau dipendam total, Logam jadi karat.",
        "Pindah profesi di umur 60-an = mungkin, tapi sebaiknya dalam bentuk shift peran (dari operasional ke advisory) bukan ganti industri total.",
    ],
    "財帛": [
        "Disiplin menabung Anda + lihai mengelola tabungan = pasangan yang langka. Skala-up: gunakan struktur formal (rekening tujuan terpisah) — supaya disiplin tidak bergantung mood.",
        "Di 大運 七殺 sekarang, tantangan: peluang besar berisiko besar muncul lebih sering. Komitmen aturan dulu (max % portofolio) sebelum peluang datang.",
        "庚金 + 喜用神 水: pertimbangkan kelas aset yang “mengalir” — bonds, dividen, saham consumer staples — bukan emas/properti yang mengeras.",
        "Beri 5-10% rezeki ke filantropi/keluarga besar setiap bulan: itu “air mengalir keluar” yang justru menjaga aliran masuk tetap lancar — sesuai prinsip 喜用神 Anda.",
    ],
    "官祿": [
        "Catatan klasik menyebut beberapa industri (termasuk hiburan dewasa) — saring sesuai etika & nilai pribadi Anda. Tafsir pakai prinsip elemen 水 + 木: pilih yang berdaya alir & berbudi pendidik.",
        "Politik / pengusaha / seniman cocok karena format 偏印格 Anda butuh “panggung tidak konvensional”. Hindari peran murni administratif — itu memboroskan modal karakter Anda.",
        "Di 七殺 大運, Anda pas berperan sebagai “tokoh yang berani bicara” — komentator, advisor industri, board member. Bukan eksekutif lapangan.",
        "Reputasi adalah aset utama umur 60-an — jaga dengan menjawab “tidak” lebih sering daripada “ya”. Setiap proyek yang ditolak dengan elegan justru meningkatkan nilai Anda.",
    ],
    "田宅": [
        "Sinyal “sibuk dengan properti” sangat khas 庚金 + 紫微-bumi. Selama Anda mengerti aturan main, properti memang “lapangan permainan” natural Anda — dengan disiplin.",
        "Mulai dari mengelola apartemen (kos / sewa) lebih sesuai 喜用神 水 (aliran cashflow) daripada investasi tanah kosong (土 statis).",
        "Arah keberuntungan Barat — pertimbangkan ini untuk fokus akuisisi properti, atau orientasi ruang kerja di rumah utama.",
        "Hindari spekulasi properti di 大運 七殺 ini; ini bukan fase “gas full akuisisi”. Konsolidasi & lepas properti yang menguras energi (sengketa, sewa macet) lebih bernilai.",
        "Bila ada properti dari “sumber tidak jelas” muncul (warisan rebutan, pembagian rumit) — selesaikan secara legal & transparan, jangan diam-diam. Itu salah satu trigger 七殺 yang bisa berlarut.",
    ],
    "僕役": [
        "Bawahan “lambat seperti sapi” = sebenarnya tipe loyal-konsisten. 庚金 yang serba cepat sering frustasi; reframing: mereka adalah pondasi, bukan akselerator.",
        "Beri instruksi tertulis + deadline yang lebih longgar 30% dari ekspektasi awal — output naik signifikan, konflik turun.",
        "Cocok untuk peran berulang & detail-oriented (pembukuan, maintenance, customer service rutin). Jangan paksa mereka di peran inovatif.",
        "Di 大運 七殺, godaan untuk “ganti tim” akan besar. Tahan sebentar — sering kali tim lama yang dilatih ulang lebih untung daripada cari baru.",
    ],
    "父母": [
        "Konfigurasi palace 父母 yang “mudah berubah” + orangtua optimis = relasi Anda dengan beliau adalah tarik-ulur antara stabilitas mereka & kebutuhan otonomi Anda.",
        "Tipe orangtua optimis-cerdas adalah guru hidup Anda yang sebenarnya — banyak pola eksekusi Anda diwarisi dari mereka, sadari & syukuri.",
        "Bila ada gesekan (terutama bila pola 武曲/廉貞 muncul): biasanya bukan soal isu, tapi soal cara penyampaian. Pakai bahasa apresiasi sebelum kritik.",
        "Di umur 60-an dengan orangtua mungkin sudah lansia atau sudah tiada: pakai dialog batin / ritual ziarah sebagai cara meneruskan transmisi nilai. Itu juga memperkuat palace 父母 Anda untuk diteruskan ke anak.",
    ],
    "福德": [
        "Pola “lambat di awal, makin tua makin berkah” cocok dengan 偏印格 — energi Anda dirancang untuk maraton, bukan sprint. Umur 60-an adalah mulai panen.",
        "Sisi “kurang proaktif” yang disebut transkrip bukan kelemahan — itu kompensasi untuk eksekusi cepat di sisi lain. Anda butuh rest mode untuk reload.",
        "Saran “jadi pendamping/wakil” sangat sesuai untuk 大運 丙辰 sekarang: peran #2 yang strategis (CEO bayangan / board member) sering lebih berdampak daripada #1 di panggung.",
        "Jaga kesehatan = kunci utama membuka rezeki di umur ini. 福德 dan 疾厄 saling menopang — investasi kesehatan = investasi rezeki secara langsung.",
        "Hangatkan relasi dengan orang-orang yang sudah lama mengenal Anda. Kebajikan yang sudah ditanam (transkrip menyebut 'kemanusiaan yang hangat') sudah bertumbuh — saatnya panen, bukan menanam baru.",
    ],
}


def patch():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    n = 0
    for cat, bullets in TAFSIR.items():
        if cat in data["transcripts"]:
            data["transcripts"][cat]["tafsir"] = bullets
            n += 1
    INPUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return n


if __name__ == "__main__":
    n = patch()
    print(f"Tafsir applied to {n} categories.")
