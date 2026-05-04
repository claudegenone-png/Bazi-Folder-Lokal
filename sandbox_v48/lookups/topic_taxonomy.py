"""Topic taxonomy — map section title keywords to canonical topic.

Used by extractor pipeline to dispatch sections to the right field in canonical model.
"""
import re


# Each topic = list of keyword patterns (case-insensitive substring match in title)
TOPIC_KEYWORDS = {
    "bazi": [
        r"\bba\s*zi\b", r"\bbazi\b", r"empat pilar", r"四柱", r"八字",
        r"si\s*zhu", r"\bsi zhu\b",
    ],
    "ziwei": [
        r"zi\s*wei", r"ziwei", r"紫微", r"peta bintang", r"peta nasib",
        r"papan ziwei", r"命盤", r"ming pan", r"peta langit",
    ],
    "ziwei_palace_collection": [
        r"interpretasi.*istana", r"detail.*istana", r"setiap istana",
        r"ringkasan.*istana", r"interpretasi.*setiap",
    ],
    "karakter": [
        r"karakter", r"kepribadian", r"watak", r"sifat", r"性情",
        r"xing\s*qing", r"profil singkat",
    ],
    "karir": [
        r"karir", r"karier", r"jabatan", r"profesi", r"事業",
        r"官祿", r"shi\s*ye", r"guan\s*lu", r"pekerjaan", r"usaha",
    ],
    "keuangan": [
        r"keuangan", r"kekayaan", r"財帛", r"財富", r"財宮",
        r"cai\s*bo", r"cai\s*fu", r"harta", r"rezeki",
    ],
    "properti": [
        r"properti", r"田宅", r"tian\s*zhai", r"tanah", r"rumah\b",
    ],
    "fengshui": [
        r"feng\s*shui", r"陽宅", r"yang\s*zhai", r"geomantik",
        r"arah rumah",
    ],
    "pernikahan": [
        r"pernikahan", r"pasangan", r"asmara", r"夫妻", r"婚配",
        r"fu\s*qi", r"hun\s*pei", r"cinta",
    ],
    "kecocokan_shio": [
        r"kecocokan shio", r"kecocokan jodoh", r"婚配", r"hun\s*pei",
        r"jodoh",
    ],
    "anak": [
        r"anak[-\s]?anak", r"keturunan", r"子女", r"zi\s*nu", r"\banak\b",
    ],
    "kesehatan": [
        r"kesehatan", r"疾厄", r"ji\s*e", r"penyakit", r"tubuh",
    ],
    "orangtua": [
        r"orang\s*tua", r"父母", r"fu\s*mu",
    ],
    "saudara": [
        r"saudara", r"persahabatan", r"兄弟", r"xiong\s*di",
    ],
    "bawahan": [
        r"bawahan", r"rekan kerja", r"僕役", r"pu\s*yi", r"pegawai",
    ],
    "perpindahan": [
        r"perpindahan", r"mobilitas", r"perjalanan", r"遷移",
        r"qian\s*yi", r"migrasi",
    ],
    "peruntungan": [
        r"peruntungan", r"keberuntungan", r"福德", r"fu\s*de",
        r"kebajikan", r"kebahagiaan", r"reputasi", r"spiritual",
    ],
    "shensha": [
        r"神煞", r"shen\s*sha", r"bintang spiritual", r"bintang khusus",
        r"bintang dewata", r"faktor nasib",
    ],
    "takdir": [
        r"宿命", r"su\s*ming", r"takdir", r"nasib akhir", r"nasib bawaan",
        r"全局", r"全局總論", r"makna hidup", r"misi hidup",
    ],
    "hikmat_klasik": [
        r"古書", r"gu\s*shu", r"hikmat klasik", r"kitab kuno",
        r"syair klasik", r"puisi ramalan", r"kutipan klasik",
        r"kata.*klasik", r"catatan buku",
    ],
    "tahunan": [
        r"流年判斷", r"liu\s*nian", r"ramalan tahunan", r"tahun.*ke depan",
        r"besar nasib.*tahunan", r"\btahunan\b",
    ],
    "tabel_tahunan": [
        r"tabel.*tahunan", r"tabel.*aliran", r"tabel.*perjalanan",
        r"流年.*易鑒", r"流年鑑易", r"tabel.*nasib.*tahunan",
        r"tabel.*besar", r"perjalanan besar", r"perjalanan nasib",
    ],
    "da_yun": [
        r"\bda\s*yun\b", r"大運", r"siklus.*besar.*10", r"siklus.*nasib.*besar",
        r"tabel besar.*10", r"siklus.*10\s*tahun",
    ],
    "ringkasan": [
        r"ringkasan", r"kesimpulan", r"saran praktis", r"saran holistik",
        r"全局總論", r"refleksi", r"penutup", r"saran.*kesimpulan",
    ],
    "glosarium": [
        r"glosarium", r"glossary", r"daftar istilah", r"lampiran.*istilah",
    ],
    "subject": [
        r"identitas", r"data pemilik", r"data subjek", r"data klien",
        r"data identitas", r"profil subjek", r"profil klien",
        r"informasi dasar",
    ],
    "header_meta": [
        r"^software", r"sistem.*software", r"^analisis lengkap",
        r"profil shio", r"sistem.*ziwei",
    ],
    "epilogue_meta": [
        r"^penutup$",
    ],
}


def detect_topic(title: str) -> str:
    """Return canonical topic key for given section title. Returns 'UNKNOWN' if no match."""
    if not title:
        return "UNKNOWN"
    t = title.upper()
    # Order matters: more specific topics first (kecocokan before pernikahan, etc.)
    priority = [
        "subject", "header_meta", "epilogue_meta",
        "tabel_tahunan", "tahunan", "da_yun",  # tabel must come before tahunan
        "ziwei_palace_collection",  # before generic ziwei
        "kecocokan_shio",  # before pernikahan
        "fengshui",  # before properti
        "hikmat_klasik",
        "ringkasan", "glosarium", "shensha", "takdir",
        "bazi", "ziwei",
        "karakter", "karir", "keuangan", "properti",
        "pernikahan", "anak", "kesehatan", "orangtua",
        "saudara", "bawahan", "perpindahan", "peruntungan",
    ]
    for topic in priority:
        for pat in TOPIC_KEYWORDS.get(topic, []):
            if re.search(pat, t, re.IGNORECASE):
                return topic
    return "UNKNOWN"
