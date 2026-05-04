"""Universal Hanzi → Indo lookup. Combined dictionary for gloss inline."""

# Heavenly Stems (天干)
GAN_PY = {"甲":"Jiǎ","乙":"Yǐ","丙":"Bǐng","丁":"Dīng","戊":"Wù","己":"Jǐ","庚":"Gēng","辛":"Xīn","壬":"Rén","癸":"Guǐ"}
GAN_INDO = {
    "甲": "Pohon Besar",  "乙": "Rumput Bunga",
    "丙": "Matahari",     "丁": "Api Lentera",
    "戊": "Tanah Gunung", "己": "Tanah Subur",
    "庚": "Logam Pedang", "辛": "Logam Halus",
    "壬": "Air Sungai",   "癸": "Air Embun",
}
GAN_ELEMEN = {"甲":"Kayu","乙":"Kayu","丙":"Api","丁":"Api","戊":"Tanah","己":"Tanah","庚":"Logam","辛":"Logam","壬":"Air","癸":"Air"}

# Earthly Branches (地支) — Shio
ZHI_PY = {"子":"Zǐ","丑":"Chǒu","寅":"Yín","卯":"Mǎo","辰":"Chén","巳":"Sì","午":"Wǔ","未":"Wèi","申":"Shēn","酉":"Yǒu","戌":"Xū","亥":"Hài"}
ZHI_INDO = {
    "子":"Tikus","丑":"Kerbau","寅":"Macan","卯":"Kelinci",
    "辰":"Naga","巳":"Ular","午":"Kuda","未":"Kambing",
    "申":"Monyet","酉":"Ayam","戌":"Anjing","亥":"Babi",
}
ZHI_ELEMEN = {"子":"Air","丑":"Tanah","寅":"Kayu","卯":"Kayu","辰":"Tanah","巳":"Api","午":"Api","未":"Tanah","申":"Logam","酉":"Logam","戌":"Tanah","亥":"Air"}

# Ten Gods (十神)
TENGOD_INDO = {
    "比肩": "Rekan Setara",
    "劫財": "Perampas Rezeki",
    "食神": "Dewa Makanan",
    "傷官": "Pejabat Terluka",
    "偏財": "Harta Sampingan",
    "正財": "Harta Tetap",
    "七殺": "Tujuh Pembunuh",
    "正官": "Pejabat Resmi",
    "偏印": "Cetakan Tidak Langsung",
    "正印": "Cetakan Resmi",
    "命主": "Hari Utama",
}

# 12-fase lifecycle
LIFEFASE_INDO = {
    "長生":"Kelahiran Panjang", "沐浴":"Pemandian", "冠帶":"Pemahkotaan",
    "臨官":"Mendekati Jabatan", "帝旺":"Puncak Kaisar", "衰":"Pelemahan",
    "病":"Sakit", "死":"Kematian", "墓":"Pemakaman",
    "絕":"Pemutusan", "胎":"Pembuahan", "養":"Pemeliharaan",
}
LIFEFASE_MOOD = {
    "長生":"good","沐浴":"neutral","冠帶":"good",
    "臨官":"good","帝旺":"good","衰":"warn",
    "病":"warn","死":"bad","墓":"neutral",
    "絕":"bad","胎":"neutral","養":"good",
}

# 14 Main ZiWei Stars (主星)
STAR_DEFS = {
    "紫微": ("Bintang Kaisar",         "Zǐwēi",   "Kepemimpinan natural, kehormatan, mulia."),
    "天機": ("Bintang Kecerdikan",     "Tiānjī",  "Analitis, fleksibel, cepat berpindah pikiran."),
    "太陽": ("Bintang Matahari",        "Tàiyáng", "Terang, terbuka, otoritas yang jelas."),
    "武曲": ("Bintang Logam Keras",    "Wǔqū",    "Tegas, disiplin, pekerja keras."),
    "天同": ("Bintang Kebahagiaan",    "Tiāntóng","Lembut, suka damai, harmonis."),
    "廉貞": ("Bintang Disiplin Moral", "Liánzhēn","Penegak hukum dan moral, pengendalian diri."),
    "天府": ("Bintang Sandang Pangan", "Tiānfǔ",  "Penjamin kebutuhan, stabilitas, akumulasi."),
    "太陰": ("Bintang Bulan",           "Tàiyīn",  "Feminin, sentimental, intuitif."),
    "貪狼": ("Bintang Keinginan",      "Tānláng", "Daya tarik tinggi, sosial, suka pengalaman baru."),
    "巨門": ("Bintang Mulut Besar",    "Jùmén",   "Komunikasi kuat, debat, hukum."),
    "天相": ("Bintang Perdana Menteri","Tiānxiàng","Diplomatis, menengahi konflik, halus."),
    "天梁": ("Bintang Pohon Cemara",   "Tiānliáng","Bijak, panjang umur, suka mengayomi."),
    "七殺": ("Bintang Tujuh Pembunuh", "Qīshā",   "Berani, tegas, suka tindakan langsung."),
    "破軍": ("Bintang Pelopor Perubahan","Pòjūn", "Dinamis, suka tantangan, pemberontak konstruktif."),
    # Extended (auxiliaries):
    "祿存": ("Bintang Kemakmuran",     "Lùcún",   "Kekayaan dan stabilitas finansial."),
    "文昌": ("Bintang Cendekia",        "Wénchāng","Studi, tulisan, dan ujian membawa hasil."),
    "文曲": ("Bintang Seni",            "Wénqū",  "Bakat seni, sastra, dan kecantikan."),
    "左輔": ("Pendamping Kiri",         "Zuǒfǔ",  "Bantuan rekan terpercaya."),
    "右弼": ("Pendamping Kanan",        "Yòubì",  "Bantuan rekan loyal."),
    "天魁": ("Bantuan Surga Yang",      "Tiānkuí","Mentor laki-laki yang membimbing."),
    "天鉞": ("Bantuan Surga Yin",       "Tiānyuè","Mentor perempuan yang membimbing."),
    "火星": ("Bintang Api",             "Huǒxīng","Energi cepat, eksekusi tegas."),
    "鈴星": ("Bintang Lonceng",         "Língxīng","Tekanan halus, refleksi mendalam."),
    "擎羊": ("Pisau Domba",             "Qíngyáng","Ketajaman yang berisiko konflik."),
    "陀羅": ("Bintang Putar",           "Tuóluó", "Rintangan berulang, perlu kesabaran."),
}

# 12 Palaces (十二宮)
PALACE_INDO = {
    "命宮":   "Istana Nasib",
    "兄弟宮": "Istana Saudara",
    "夫妻宮": "Istana Pasangan",
    "子女宮": "Istana Anak",
    "財帛宮": "Istana Keuangan",
    "疾厄宮": "Istana Kesehatan",
    "遷移宮": "Istana Perpindahan",
    "僕役宮": "Istana Bawahan",
    "官祿宮": "Istana Karier",
    "田宅宮": "Istana Properti",
    "福德宮": "Istana Kebahagiaan",
    "父母宮": "Istana Orang Tua",
    "身宮":   "Istana Tubuh",
}

# Shen Sha (神煞 — Special Stars)
SHENSHA_INDO = {
    "太歲":   ("Penguasa Tahun",       "Tài Suì",     "Bintang utama tahun, perlu hormat."),
    "元辰":   ("Dewa Asal",            "Yuán Chén",   "Tahun penuh kekacauan kecil & rasa tidak puas."),
    "大耗":   ("Penguras Besar",        "Dà Hào",      "Pengeluaran besar, hilangnya harta."),
    "病符":   ("Tanda Penyakit",        "Bìng Fú",     "Waspadai kesehatan tahun ini."),
    "天狗":   ("Anjing Surga",         "Tiān Gǒu",    "Risiko luka kecil."),
    "福德":   ("Berkah Kebajikan",     "Fú Dé",       "Tahun yang membawa rezeki batin & ketenangan."),
    "白虎":   ("Macan Putih",          "Bái Hǔ",      "Konflik, perdebatan, atau cedera ringan."),
    "紅鸞":   ("Burung Mistik Merah",  "Hóng Luán",   "Pertanda asmara / pernikahan / kabar gembira."),
    "寡宿":   ("Bintang Janda",        "Guǎ Sù",      "Rasa kesepian atau jarak dengan pasangan."),
    "孤辰":   ("Bintang Tunggal",      "Gū Chén",     "Sendirian, perlu fokus pada diri sendiri."),
    "羊刃":   ("Pisau Domba",          "Yáng Rèn",    "Kekuatan tajam, rawan konflik fisik."),
    "將星":   ("Bintang Jenderal",     "Jiāng Xīng",  "Kepemimpinan & komando — tahun menonjol."),
    "驛馬":   ("Kuda Pengembara",      "Yì Mǎ",       "Tahun perjalanan, perpindahan, atau ekspansi."),
    "天乙":   ("Bantuan Surga",        "Tiān Yǐ",     "Bantuan tak terduga dari orang berpengaruh."),
    "華蓋":   ("Penaung Cemerlang",    "Huá Gài",     "Selera seni & spiritualitas tinggi."),
    "桃花":   ("Bunga Persik",         "Táo Huā",     "Daya tarik & peluang asmara meningkat."),
    "天喜":   ("Bintang Sukacita",     "Tiān Xǐ",     "Kabar gembira keluarga, kelahiran, kesuksesan."),
    "龍德":   ("Kebajikan Naga",       "Lóng Dé",     "Perlindungan ilahi & kebaikan datang."),
    "天掃":   ("Penyapu Surga",        "Tiān Sào",    "Pembersihan / kehilangan."),
    "死符":   ("Tanda Maut",           "Sǐ Fú",       "Pertanda berkabung."),
    "暗耀":   ("Gemerlap Gelap",       "Àn Yào",      "Bahaya tersembunyi, jaga rahasia & lisan."),
    "官符":   ("Tanda Pejabat",        "Guān Fú",     "Risiko urusan hukum atau birokrasi."),
    "火煞":   ("Pembunuh Api",         "Huǒ Shà",     "Hindari amarah, api, kecelakaan tajam."),
    "喪宿":   ("Tanda Berkabung",      "Sàng Sù",     "Hari/tahun mendung."),
    "金奧":   ("Misteri Logam",        "Jīn Ào",      "Daya analitik & strategi tajam."),
    "文昌":   ("Bintang Cendekia",     "Wénchāng",    "Studi & ujian."),
    "天魁":   ("Bantuan Surga Yang",   "Tiānkuí",     "Mentor laki-laki."),
    "天鉞":   ("Bantuan Surga Yin",    "Tiānyuè",     "Mentor perempuan."),
}


def gloss(hz: str):
    """Look up Hanzi term across all dictionaries. Returns Indo or empty string."""
    if not hz: return ""
    # Try multi-char compounds first (longer)
    for src in (TENGOD_INDO, LIFEFASE_INDO, PALACE_INDO):
        if hz in src: return src[hz]
    if hz in STAR_DEFS: return STAR_DEFS[hz][0]
    if hz in SHENSHA_INDO: return SHENSHA_INDO[hz][0]
    # Single char
    if hz in GAN_INDO: return GAN_INDO[hz]
    if hz in ZHI_INDO: return ZHI_INDO[hz]
    return ""


def gloss_pinyin(hz: str):
    """Look up pinyin for Hanzi term."""
    if not hz: return ""
    if hz in STAR_DEFS: return STAR_DEFS[hz][1]
    if hz in SHENSHA_INDO: return SHENSHA_INDO[hz][1]
    if hz in GAN_PY: return GAN_PY[hz]
    if hz in ZHI_PY: return ZHI_PY[hz]
    return ""


def shio_indo(zhi_hz: str):
    return ZHI_INDO.get(zhi_hz, "")
