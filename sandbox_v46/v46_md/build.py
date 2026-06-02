# -*- coding: utf-8 -*-
"""V4.6 MD-driven Ramalan PDF builder.

Usage: python build.py <path_to_md_file> [--out OUT_DIR]

Reads markdown report (from Xing Yi software OCR), renders to PDF
following V4.5 design system.
"""
import sys, os, re, time, shutil, subprocess, html
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
TODAY = time.strftime("%Y-%m-%d")

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# Pinyin & translation lookups
GAN_PY = {"甲":"Jiǎ","乙":"Yǐ","丙":"Bǐng","丁":"Dīng","戊":"Wù","己":"Jǐ","庚":"Gēng","辛":"Xīn","壬":"Rén","癸":"Guǐ"}
ZHI_PY = {"子":"Zǐ","丑":"Chǒu","寅":"Yín","卯":"Mǎo","辰":"Chén","巳":"Sì","午":"Wǔ","未":"Wèi","申":"Shēn","酉":"Yǒu","戌":"Xū","亥":"Hài"}
DM_INDO = {
    "甲": ("Pohon Besar", "甲木"), "乙": ("Rumput Bunga", "乙木"),
    "丙": ("Matahari", "丙火"),    "丁": ("Api Lentera", "丁火"),
    "戊": ("Tanah Gunung", "戊土"), "己": ("Tanah Subur", "己土"),
    "庚": ("Logam Pedang", "庚金"), "辛": ("Logam Halus", "辛金"),
    "壬": ("Air Sungai", "壬水"),  "癸": ("Air Embun", "癸水"),
}
SHICHEN = [  # (start_h, hz, py)
    (23, "子時", "Zǐ"), (1, "丑時", "Chǒu"), (3, "寅時", "Yín"),
    (5, "卯時", "Mǎo"), (7, "辰時", "Chén"), (9, "巳時", "Sì"),
    (11, "午時", "Wǔ"), (13, "未時", "Wèi"), (15, "申時", "Shēn"),
    (17, "酉時", "Yǒu"), (19, "戌時", "Xū"), (21, "亥時", "Hài"),
]
def hour_to_shichen(h):
    # 子 spans 23-00:59
    if h == 23 or h == 0: return ("子時", "Zǐ")
    for (sh, hz, py) in SHICHEN[1:]:
        if sh <= h < sh + 2:
            return (hz, py)
    return ("子時", "Zǐ")

def hour_to_tod(h):
    if 0 <= h < 5: return "dini hari"
    if 5 <= h < 11: return "pagi"
    if 11 <= h < 15: return "siang"
    if 15 <= h < 18: return "sore"
    return "malam"

DOW_INDO = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_INDO = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
def parse_indo_date(s):
    """Parse '29 Januari 1963' → (29, 1, 1963)."""
    m = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", s)
    if not m: return (0, 0, 0)
    bm = {b: i for i, b in enumerate(BULAN_INDO)}
    return (int(m.group(1)), bm.get(m.group(2), 0), int(m.group(3)))

ELEM_HZ = {"Api": "火", "Kayu": "木", "Air": "水", "Logam": "金", "Tanah": "土"}

# Definisi standar (universal, bukan interpretasi spesifik) — untuk Info Inti
INFO_INTI_GLOSS = {
    "五行局": "Pola 5 Unsur Dasar bagan — menentukan ritme &amp; timing kemakmuran sepanjang hidup.",
    "命主": "Bintang Penguasa Nasib — arketipe karakter inti, dihitung dari pilar tahun lahir.",
    "身主": "Bintang Penguasa Tubuh — energi fisik &amp; dorongan diri, dihitung dari pilar jam lahir.",
    "命宮": "Posisi Istana Nasib di 12 cabang bumi — fondasi pemikiran &amp; arah hidup.",
    "身宮": "Posisi Istana Tubuh di 12 cabang bumi — sisi eksekusi &amp; tindakan nyata.",
    "格局": "Pola Nasib — tipe formasi yang menentukan kelas keberuntungan keseluruhan.",
    "特殊格": "Formasi Khusus — pola ekstra dengan kekuatan/risiko unik di luar pola utama.",
    "子年斗君": "Bintang Pemimpin Tahun Tikus — titik referensi posisi bintang tahunan.",
    "斗君": "Bintang Pemimpin Tahunan — titik referensi posisi tahunan dari shio tahun.",
}

# Definisi standar 四化 (Si Hua) — universal
SIHUA_DEFS = {
    "化祿": "Transformasi Rezeki — bintang ini membawa kemakmuran &amp; sumber daya.",
    "化權": "Transformasi Kekuasaan — bintang ini membawa otoritas &amp; pengaruh.",
    "化科": "Transformasi Prestasi — bintang ini membawa nama baik &amp; pencapaian akademik.",
    "化忌": "Transformasi Hambatan — bintang ini membawa rintangan yang harus diolah.",
}

# Shio mapping
SHIO_MAP = {
    "Tikus": ("鼠", "🐭", "zǐ"),  "Kerbau": ("牛", "🐂", "chǒu"),
    "Harimau": ("虎", "🐯", "yín"), "Kelinci": ("兔", "🐰", "mǎo"),
    "Naga": ("龍", "🐉", "chén"),  "Ular": ("蛇", "🐍", "sì"),
    "Kuda": ("馬", "🐴", "wǔ"),   "Kambing": ("羊", "🐑", "wèi"),
    "Monyet": ("猴", "🐒", "shēn"), "Ayam": ("雞", "🐓", "yǒu"),
    "Anjing": ("狗", "🐕", "xū"), "Babi": ("豬", "🐷", "hài"),
}

# Glossary candidates - terms commonly in MD; we filter to those actually present
GLOSSARY = {
    "八字": ("Bā Zì", "Empat Pilar Kelahiran — sistem dasar yang menggunakan tahun, bulan, hari, dan jam lahir untuk membaca takdir."),
    "紫微斗數": ("Zǐ Wēi Dòu Shù", "Sistem astrologi Tiongkok yang memetakan 12 istana hidup berdasarkan posisi bintang Ziwei."),
    "天干": ("Tiān Gān", "Sepuluh Batang Langit — komponen aksara yang membentuk pilar atas dalam Ba Zi."),
    "地支": ("Dì Zhī", "Dua Belas Cabang Bumi — komponen aksara yang membentuk pilar bawah, dipasangkan dengan shio."),
    "命宮": ("Mìng Gōng", "Istana Nasib — istana utama yang menggambarkan karakter inti dan jalur hidup keseluruhan."),
    "身宮": ("Shēn Gōng", "Istana Tubuh — menggambarkan kondisi fisik dan kekuatan dorongan diri."),
    "命主": ("Mìng Zhǔ", "Bintang Penguasa Nasib — bintang yang menentukan tema utama hidup berdasarkan tahun lahir."),
    "身主": ("Shēn Zhǔ", "Bintang Penguasa Tubuh — bintang yang melengkapi 命主 menentukan kekuatan jasmani."),
    "格局": ("Gé Jú", "Pola Nasib — formasi struktural khusus pada bagan yang menentukan kelas/tipe takdir."),
    "用神": ("Yòng Shén", "Dewa Berguna — unsur paling membantu untuk menyeimbangkan bagan."),
    "喜神": ("Xǐ Shén", "Dewa Disukai — unsur yang menguntungkan dan disukai oleh diri."),
    "忌神": ("Jì Shén", "Dewa Penghambat — unsur yang harus dihindari karena merugikan."),
    "閒神": ("Xián Shén", "Dewa Netral — unsur tanpa pengaruh signifikan."),
    "仇神": ("Chóu Shén", "Dewa Musuh — unsur yang menentang diri."),
    "正財": ("Zhèng Cái", "Harta Tetap — pendapatan stabil seperti gaji, investasi properti."),
    "偏財": ("Piān Cái", "Harta Sampingan — pendapatan tidak terduga seperti komisi, bonus, spekulasi."),
    "正官": ("Zhèng Guān", "Pejabat Resmi — pola karir formal, kekuasaan terstruktur."),
    "化祿": ("Huà Lù", "Transformasi Rezeki — bintang yang berubah membawa kemakmuran."),
    "化權": ("Huà Quán", "Transformasi Kekuasaan — bintang yang berubah membawa otoritas."),
    "化科": ("Huà Kē", "Transformasi Akademik — bintang yang berubah membawa prestasi."),
    "化忌": ("Huà Jì", "Transformasi Hambatan — bintang yang berubah membawa rintangan."),
    "羊刃格": ("Yáng Rèn Gé", "Formasi Pisau Domba — pola berani, tegas, namun rawan kekerasan."),
    "天相": ("Tiān Xiàng", "Bintang Perdana Menteri — kepribadian halus, suka menengahi, suka damai."),
    "天府": ("Tiān Fǔ", "Bintang Kekayaan & Sandang Pangan — penjamin kebutuhan hidup."),
    "武曲": ("Wǔ Qū", "Bintang Logam Keras — keuangan dan kemiliteran."),
    "破軍": ("Pò Jūn", "Bintang Perubahan — pelopor, dinamis, penghancur."),
    "巨門": ("Jù Mén", "Bintang Mulut Besar — kuat dalam komunikasi, debat, hukum."),
    "貪狼": ("Tān Láng", "Bintang Keinginan — daya tarik, sosial, namun rawan godaan."),
    "太陰": ("Tài Yīn", "Bintang Bulan — feminin, sentimentil, kekayaan tersembunyi."),
    "太陽": ("Tài Yáng", "Bintang Matahari — terang, terbuka, otoritas yang jelas."),
    "天機": ("Tiān Jī", "Bintang Kecerdikan — analisis, perencanaan, fleksibilitas."),
    "天梁": ("Tiān Liáng", "Bintang Pohon Cemara — bijak, panjang umur, suka mengayomi."),
    "七殺": ("Qī Shā", "Bintang Tujuh Pembunuh — keberanian, tindakan tegas."),
    "紫微": ("Zǐ Wēi", "Bintang Kaisar — kepemimpinan, kehormatan, mulia."),
    "廉貞": ("Lián Zhēn", "Bintang Disiplin — moral, hukum, pengendalian diri."),
    "文昌": ("Wén Chāng", "Bintang Akademik — kecerdasan, prestasi pelajaran."),
    "文曲": ("Wén Qū", "Bintang Sastra — bakat seni, sastra, retorika."),
    "驛馬": ("Yì Mǎ", "Kuda Pos — bintang perjalanan dan perpindahan."),
    "喪宿": ("Sāng Sù", "Bintang Berkabung — terisolasi sosial, suka menyendiri."),
    "元辰大耗": ("Yuán Chén Dà Hào", "Bintang Kerugian Besar — tantangan hidup berat, banyak rintangan."),
    "古書云": ("Gǔ Shū Yún", "Sebagaimana Tertulis di Kitab Lama — referensi pesan klasik."),
    "三命通會": ("Sān Mìng Tōng Huì", "Kitab Klasik Ba Zi — referensi utama kelahiran Ren-Gui."),
    "滴天髓": ("Dī Tiān Suǐ", "Kitab Tetes Langit — referensi klasik 10 batang langit."),
    "陽宅": ("Yáng Zhái", "Feng Shui Rumah Tinggal — tata letak hunian agar membawa keberuntungan."),
    "流年": ("Liú Nián", "Tahun Berjalan — ramalan untuk satu tahun spesifik."),
    "婚配": ("Hūn Pèi", "Kecocokan Pernikahan — kesesuaian shio antar pasangan."),
}

# === MD PARSER ===

ROMAN_TO_INT = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
    "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
}


def detect_topic(title):
    """Map BAB title to canonical topic key for adaptive dispatch."""
    t = title.upper()
    # Order matters — most specific first
    if any(k in t for k in ["TABEL LIMPASAN", "SIKLUS BESAR", "大運"]): return "siklus"
    if any(k in t for k in ["RAMALAN TAHUNAN", "TAHUNAN", "流年"]) and "TABEL" not in t: return "tahunan"
    if any(k in t for k in ["BA ZI", "EMPAT PILAR", "四柱", "BAZI"]): return "bazi"
    if any(k in t for k in ["ZI WEI", "BINTANG UNGU", "紫微", "ASTROLOGI BINTANG", "PETA BINTANG"]): return "ziwei"
    if any(k in t for k in ["KECOCOKAN SHIO", "KOMPATIBILITAS SHIO"]): return "kecocokan_shio"
    if any(k in t for k in ["PERNIKAHAN", "PASANGAN", "夫妻", "婚配", "ASMARA"]): return "pernikahan"
    if any(k in t for k in ["KARAKTER", "KEPRIBADIAN", "性情", "SIFAT"]): return "karakter"
    if any(k in t for k in ["KARIR", "JABATAN", "事業", "官祿", "USAHA", "PROFESI"]): return "karir"
    if any(k in t for k in ["KEUANGAN", "KEKAYAAN", "財帛", "財富", "HARTA"]): return "keuangan"
    if any(k in t for k in ["ANAK", "KETURUNAN", "子女"]): return "anak"
    if any(k in t for k in ["KESEHATAN", "疾厄"]): return "kesehatan"
    if any(k in t for k in ["ORANG TUA", "父母"]): return "orangtua"
    if any(k in t for k in ["BAWAHAN", "REKAN", "僕役"]): return "bawahan"
    if any(k in t for k in ["FENG SHUI", "陽宅", "GEOMANTIK", "RUMAH YANG"]) or ("PROPERTI" in t and "FENG" in t): return "fengshui"
    if any(k in t for k in ["PROPERTI", "田宅"]): return "properti"
    if any(k in t for k in ["PERPINDAHAN", "MOBILITAS", "MIGRASI", "遷移"]): return "perpindahan"
    if any(k in t for k in ["KEBAJIKAN", "PERUNTUNGAN", "福德"]) and "TAHUNAN" not in t: return "peruntungan"
    if any(k in t for k in ["BINTANG KHUSUS", "神煞", "SHEN SHA"]): return "shensha"
    if any(k in t for k in ["NASIB KESELURUHAN", "TAKDIR", "宿命", "全局總論", "全局", "MAKNA HIDUP"]): return "takdir"
    if any(k in t for k in ["SARAN", "KESIMPULAN", "RINGKASAN"]): return "saran_kesimpulan"
    if any(k in t for k in ["CATATAN", "PERINGATAN"]): return "catatan"
    return "generic"


def is_subject_heading(title):
    return bool(re.search(r"DATA\s+(?:PEMILIK|KLIEN|SUBJEK)|IDENTITAS\s+(?:SUBJEK|PEMILIK|KLIEN)|PROFIL\s+(?:SUBJEK|KLIEN|PEMILIK)", title, re.IGNORECASE))


def is_epilogue_heading(title):
    return bool(re.search(r"CATATAN\s*(?:&|DAN)?\s*PERINGATAN|RINGKASAN\s*(?:&|DAN)?\s*SARAN|^FOOTER|REFERENSI|SUMBER", title, re.IGNORECASE))


def clean_section_title(title):
    """Strip emoji + numbering prefix to get pure topic title."""
    t = title
    # Strip leading emojis & symbols
    t = re.sub(r"^[^\w\s]+\s*", "", t)
    # Strip "BAGIAN/BAB N —" or "Chapter N —"
    t = re.sub(r"^(?:BAGIAN|BAB|CHAPTER)\s+([IVXLCDM]+|\d+)\s*[—–\-:]\s*", "", t, flags=re.IGNORECASE)
    # Strip "1.2 —" or "1.2" sub-numbering
    t = re.sub(r"^(\d+\.\d+)\s*[—–\-:]?\s*", "", t)
    # Strip trailing emojis
    t = re.sub(r"\s*[^\w\s\(\)一-鿿·\-]+\s*$", "", t)
    return t.strip()


def parse_md(text):
    """Parse adaptive MD report — topic-based segmentation across heading levels."""
    data = {"sections": [], "subject": {}, "toc": [], "title": "", "epilogue": ""}
    lines = text.split("\n")

    # Title (first H1)
    for line in lines:
        m = re.match(r"^#\s+(.+)", line)
        if m:
            data["title"] = re.sub(r"[✦🌟🔮📋📊💎🎯⚠️✅🔴🀄☯️🏡📅💼💍🏮🌸📌🌿]", "", m.group(1)).strip()
            break

    # Subject — try multiple heading patterns
    SUBJECT_HEAD_PATTERNS = [
        r"DATA\s+PEMILIK", r"IDENTITAS\s+SUBJEK", r"PROFIL\s+(?:SUBJEK|KLIEN)",
        r"DATA\s+SUBJEK", r"IDENTITAS", r"DATA\s+KLIEN",
    ]
    in_data = False
    for line in lines:
        if line.startswith("## ") and any(re.search(p, line, re.IGNORECASE) for p in SUBJECT_HEAD_PATTERNS):
            in_data = True; continue
        if in_data:
            if line.startswith("## ") or line.startswith("---") and data["subject"]:
                in_data = False; continue
            if "|" in line and "---" not in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 2:
                    k = re.sub(r"\*\*", "", cells[0]).strip()
                    v = re.sub(r"\*\*", "", cells[1]).strip()
                    # Skip header rows
                    if k.lower() in ("atribut", "keterangan", "data", "field"): continue
                    if k: data["subject"][k] = v

    # Normalize subject key aliases — bridge multiple naming conventions
    SUBJECT_ALIASES = {
        # Tahun Masehi
        "Tahun Masehi": "Tahun Lahir (Masehi)",
        "Tahun Lahir Masehi": "Tahun Lahir (Masehi)",
        # Kalender Nasional / Tanggal Indonesia (only full dates, NOT just year)
        "Kalender Nasional (ROC)": "Kalender Nasional",
        "Tanggal Lahir (Nasional)": "Kalender Nasional",
        "Tanggal Lahir (Indonesia)": "Kalender Nasional",
        "Tanggal Lahir": "Kalender Nasional",
        # Kalender Lunar / Tanggal Tionghoa
        "Kalender Lunar (農曆)": "Kalender Lunar",
        "Kalender Tionghoa": "Kalender Lunar",
        "Tanggal Lahir (Imlek)": "Kalender Lunar",
        "Tanggal Lahir (Tionghoa)": "Kalender Lunar",
        # Hari & Jam
        "Hari": "Hari Lahir",
        "Jam": "Jam Lahir",
    }
    for src, dst in SUBJECT_ALIASES.items():
        if src in data["subject"] and dst not in data["subject"]:
            data["subject"][dst] = data["subject"][src]

    # Adaptive section parsing: H2 = BAB. Epilogue (TABEL SIKLUS/RINGKASAN/CATATAN) → parsed["epilogue"]
    H_PAT = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
    cur = None
    epilogue_started = False

    for line in lines:
        hm = H_PAT.match(line)
        if hm:
            level = len(hm.group(1))
            raw_title = hm.group(2).strip()

            if level == 2 and is_subject_heading(raw_title):
                continue

            clean = clean_section_title(raw_title)
            topic = detect_topic(clean)

            if level == 2:
                if re.search(r"Software|Version", raw_title, re.IGNORECASE):
                    continue
                is_bab = bool(re.search(r"\b(BAB|BAGIAN|CHAPTER|PART)\b", raw_title, re.IGNORECASE))
                is_epi = bool(re.search(r"TABEL\s+SIKLUS|TABEL\s+LIMPASAN|RINGKASAN|CATATAN", raw_title, re.IGNORECASE))
                if not is_bab and not is_epi:
                    continue
                # Epilogue → close current section, redirect to data["epilogue"]
                if is_epi and not is_bab:
                    if cur:
                        data["sections"].append(cur); cur = None
                    epilogue_started = True
                    data["epilogue"] += line + "\n"
                    continue
                # New BAB section
                if epilogue_started:
                    # Edge case: BAB after epilogue marker → keep in epilogue
                    data["epilogue"] += line + "\n"
                    continue
                if cur:
                    data["sections"].append(cur)
                cur = {"num": len(data["sections"]) + 1, "title": clean, "topic": topic, "lines": []}
                continue

            # H3 — sub-content within current BAB (or epilogue)
            if epilogue_started:
                data["epilogue"] += line + "\n"
                continue
            if level == 3 and cur is not None:
                cur["lines"].append(line)
                continue

        if epilogue_started:
            data["epilogue"] += line + "\n"
        elif cur is not None:
            cur["lines"].append(line)

    if cur:
        data["sections"].append(cur)

    # Build TOC
    for sec in data["sections"]:
        data["toc"].append({"num": sec["num"], "title": sec["title"], "topic": sec["topic"]})

    return data


def extract_interpretasi(lines):
    """Extract first relevant '> **LABEL:**' blockquote. Priority labels first.

    Priority: Interpretasi > Penjelasan awam > Apa Artinya > Tip > Saran (general)
    Skips specific-context labels like 'Saran kesehatan', 'Saran karir', etc.
    """
    PRIORITY_LABELS = [
        "Interpretasi", "Penjelasan awam", "Apa Artinya",
        "Penjelasan", "Ringkasan", "Tip", "Pesan",
    ]
    blocks = []  # list of (priority_index, text)
    cur = []; cur_label = None; cur_priority = None

    def commit():
        nonlocal cur, cur_label, cur_priority
        if cur and cur_priority is not None:
            blocks.append((cur_priority, " ".join(cur).strip()))
        cur = []; cur_label = None; cur_priority = None

    for line in lines:
        s = line.strip()
        if s.startswith(">"):
            txt = s.lstrip(">").strip()
            # Detect label
            label_m = re.match(r"^\s*[^a-zA-Z0-9\s]*\s*\*\*([^:*]+):\*\*\s*(.*)", txt)
            if label_m:
                # New labeled block — commit previous
                commit()
                label = label_m.group(1).strip()
                content = label_m.group(2).strip()
                # Find priority — match by prefix
                priority = None
                for i, pl in enumerate(PRIORITY_LABELS):
                    if label.lower().startswith(pl.lower()):
                        priority = i; break
                # Skip context-specific saran like "Saran kesehatan", "Saran karir"
                if label.lower().startswith("saran"):
                    rest = label[5:].strip()
                    if rest and rest.lower() not in ("praktis", "umum", ""):
                        # Specific saran (saran kesehatan, dll) — skip
                        continue
                    priority = len(PRIORITY_LABELS)  # general saran = lowest priority
                # Catatan = warning, lowest priority
                if label.lower().startswith("catatan") or label.lower().startswith("peringatan"):
                    priority = len(PRIORITY_LABELS) + 1
                if priority is not None:
                    cur_label = label; cur_priority = priority
                    if content: cur.append(content)
            elif cur_label:
                cur.append(txt)
        else:
            commit()

    commit()

    # Sort by priority (low number = high priority)
    blocks.sort(key=lambda x: x[0])
    return [b[1] for b in blocks if b[1]]


def parse_md_table(lines, start_idx):
    """Parse a markdown table starting at start_idx. Returns (headers, rows, end_idx)."""
    if start_idx >= len(lines) or "|" not in lines[start_idx]:
        return None, None, start_idx
    header_line = lines[start_idx]
    if start_idx + 1 >= len(lines) or "---" not in lines[start_idx + 1]:
        return None, None, start_idx
    headers = [c.strip() for c in header_line.strip("|").split("|")]
    rows = []
    i = start_idx + 2
    while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip("|").split("|")]
        rows.append(cells)
        i += 1
    return headers, rows, i


# === MD INLINE → HTML ===

def md_inline(s):
    """Inline markdown: **bold**, *italic*, Hanzi auto-style."""
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    # Hanzi auto-class (single char or pair of CJK)
    s = re.sub(r"([一-鿿]+)", r'<span class="hz">\1</span>', s)
    return s


def percent_class(p):
    if p >= 70: return "high"
    if p >= 50: return "mid"
    return "low"


def percent_class_year(p):
    if p >= 70: return ""  # gold default
    if p >= 50: return "mid"
    return "bad"


# === PAGE WRAPPER ===

def page(num, id_title, hz_title, section_label, body_html, subject_name):
    """Wrap content in standard page shell."""
    return f"""<section class="page">
  <header class="page-header">
    <div class="h-num">{num:02d}</div>
    <div class="h-titles">
      <div class="h-id">{id_title}</div>
      <div class="h-cn">{hz_title}</div>
    </div>
    <div class="h-section">{section_label}</div>
  </header>
  <div class="content">{body_html}</div>
  <footer class="footer">
    <div class="footer-l">Laporan Ramalan Tionghoa Klasik</div>
    <div class="footer-pg">— {num} —</div>
  </footer>
</section>"""


# === PAGE BUILDERS ===

def extract_pillars(sections):
    """Pull 4 pillar Hanzi from BAZI section (BAB 1 in original MD)."""
    out = ["", "", "", ""]
    gans = ["", "", "", ""]
    zhis = ["", "", "", ""]
    # Try topic=bazi first, fallback to BAB 1
    target_secs = [s for s in sections if s.get("topic") == "bazi"]
    if not target_secs:
        target_secs = [s for s in sections if s.get("num") == 1]
    for sec in target_secs:
        for line in sec["lines"]:
            if "Batang Langit" in line and "|" in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                for i, c in enumerate(cells[1:5]):
                    m = re.match(r"^([一-鿿]+)", c)
                    if m and m.group(1)[0] in GAN_PY: gans[i] = m.group(1)[0]
            if "Cabang Bumi" in line and "|" in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                for i, c in enumerate(cells[1:5]):
                    m = re.match(r"^([一-鿿]+)", c)
                    if m and m.group(1)[0] in ZHI_PY: zhis[i] = m.group(1)[0]
        for i in range(4):
            out[i] = gans[i] + zhis[i]
        break
    return out, gans, zhis


def extract_yong_xi_elements(sections):
    """Extract Yong Shen + Xi Shen Indo element names from BAB 1 's 喜用神 table.

    Table format (new):
    | Kategori | Elemen | Makna Praktis |
    | **用神** (Dewa Utama) | 木 Kayu | ... |
    | **喜神** (Dewa Keberuntungan) | 火 Api | ... |
    """
    favs = []
    for sec in sections:
        if sec.get("topic") != "bazi": continue
        in_t = False
        for line in sec["lines"]:
            if "喜用神" in line or "Elemen Keberuntungan" in line:
                in_t = True; continue
            if in_t and "|" in line and "---" not in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 3 and cells[0] and "Kategori" not in cells[0]:
                    cat = cells[0]
                    elem_cell = cells[1]  # e.g. "木 Kayu"
                    if "用神" in cat or "喜神" in cat:
                        # Extract Indo name (after Hanzi)
                        m = re.search(r"([一-鿿])\s*(\w+)", elem_cell)
                        if m:
                            hz = m.group(1)
                            indo = m.group(2)
                            favs.append((indo, hz))
            if in_t and (line.startswith("###") or line.startswith(">")):
                in_t = False
        break
    return favs


def build_cover_NEW(subject, sections=None):
    """Adaptive cover with verbatim Kalender Nasional + structured Lunar."""
    nama = subject.get("Nama", "")
    shio_raw = subject.get("Shio", "")

    # Detect shio_id
    shio_id = ""; shio_hz = ""; shio_emoji = "·"
    for k, (hz, emoji, _) in SHIO_MAP.items():
        if k in shio_raw or hz in shio_raw:
            shio_id = k; shio_hz = hz; shio_emoji = emoji; break
    if not shio_id:
        # Fallback: extract first Hanzi if any
        hzm = re.search(r"([一-鿿])", shio_raw)
        if hzm:
            shio_hz = hzm.group(1)
            for k, (hz, emoji, _) in SHIO_MAP.items():
                if hz == shio_hz:
                    shio_id = k; shio_emoji = emoji; break

    # SVG shio asset
    SVG_DIRS = [
        Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\v45\assets"),
        Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\assets"),
        Path(__file__).parent / "assets",
        Path(__file__).parent.parent / "assets",
    ]
    svg_url = ""
    for asset_dir in SVG_DIRS:
        if shio_id:
            svg_path = asset_dir / f"{shio_id}-Merah.svg"
            if svg_path.exists():
                svg_url = "file:///" + str(svg_path).replace("\\", "/")
                break
    shio_inner = f'<img src="{svg_url}" alt="{shio_id}" style="width: 100%; height: 100%; object-fit: contain;">' if svg_url else f'<span style="font-size: 50pt;">{shio_emoji}</span>'

    # Tanggal Lahir (Indonesia) — VERBATIM from Kalender Nasional + (Hari) suffix
    nasional_raw = subject.get("Kalender Nasional", "") or subject.get("Tanggal Lahir", "")
    nasional_clean = re.sub(r"\s*\([^)]*Kalender[^)]*\)", "", nasional_raw).strip()

    # Hari Lahir — extract Indonesian day name
    hari_raw = subject.get("Hari Lahir", "")
    dow_str = ""
    hm = re.search(r"\b(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)\b", hari_raw)
    if hm: dow_str = hm.group(1)
    # If "Hari" already in nasional (e.g. "30 Mei 1995 (Minggu)"), don't duplicate
    if dow_str and f"({dow_str})" in nasional_clean:
        nasional_display = nasional_clean
    elif dow_str:
        nasional_display = f"{nasional_clean} ({dow_str})"
    else:
        nasional_display = nasional_clean

    # Tanggal Lahir (Tionghoa) — parse Lunar to "Tahun [Pinyin] ([HZ]), Bulan X, Tanggal Y, Jam Z"
    lunar_raw = subject.get("Kalender Lunar", "")
    lunar_pillar = ""; lunar_pillar_py = ""; lunar_month = ""; lunar_day = ""
    # Match 2-char pillar where first is gan & second is zhi
    for m in re.finditer(r"([一-鿿])([一-鿿])", lunar_raw):
        g, z = m.group(1), m.group(2)
        if g in GAN_PY and z in ZHI_PY:
            lunar_pillar = g + z
            lunar_pillar_py = f"{GAN_PY[g]} {ZHI_PY[z]}".strip()
            break
    # Parse month/day — patterns: "5月 2日", "Bulan 5 Tanggal 2", "1 月 5 日"
    md_m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", lunar_raw)
    if md_m:
        lunar_month = md_m.group(1); lunar_day = md_m.group(2)
    else:
        md_m2 = re.search(r"[Bb]ulan\s+(\d{1,2})[,\s]+[Tt]anggal\s+(\d{1,2})", lunar_raw)
        if md_m2:
            lunar_month = md_m2.group(1); lunar_day = md_m2.group(2)

    # Jam Lahir — parse hour
    jam_raw = subject.get("Jam Lahir", "")
    jam_hour = ""; jam_min = ""
    jh_m = re.match(r"(\d{1,2})\s*[時:]\s*(\d{1,2})?", jam_raw)
    if jh_m:
        jam_hour = jh_m.group(1)
        jam_min = jh_m.group(2) or "00"
    jam_full = f"{jam_hour}:{jam_min.zfill(2)}" if jam_hour else jam_raw

    # Tionghoa display
    if lunar_pillar and lunar_month and lunar_day:
        tionghoa_display = f'Tahun <em>{lunar_pillar_py}</em> (<span class="hz">{lunar_pillar}</span>), Bulan {lunar_month}, Tanggal {lunar_day}{f", Jam {jam_hour}" if jam_hour else ""}'
    elif lunar_raw:
        tionghoa_display = re.sub(r"^農曆\s*", "", lunar_raw)
    else:
        tionghoa_display = "—"

    # Jam display: "pukul HH:MM (siang · 未時)"
    jam_formatted = jam_full
    if jam_hour:
        try:
            h = int(jam_hour)
            sh_hz, sh_py = hour_to_shichen(h)
            tod = hour_to_tod(h)
            jam_formatted = f'pukul {jam_full} <em>({tod} · <span class="hz">{sh_hz}</span>)</em>'
        except Exception:
            pass

    # Pillars (for Day Master + 4 pillar mini badge)
    pillars_full, gans, zhis = extract_pillars(sections or [])
    dm_gan = gans[2] if gans and len(gans) > 2 and gans[2] else ""
    dm_indo, dm_hz = DM_INDO.get(dm_gan, ("", ""))
    dm_line = f'{dm_indo} <span class="hz">{dm_hz}</span>' if dm_gan else ""

    # Elemen Utama (Yong + Xi shen)
    favs = extract_yong_xi_elements(sections or [])
    elem_line = ""
    if favs:
        indo_names = " &amp; ".join(f[0] for f in favs)
        hz_chars = " ".join(f[1] for f in favs if f[1])
        elem_line = f'{indo_names} <span class="hz">{hz_chars}</span>'

    # Bagua decorative ring
    bagua = [("☰","乾","Qián","Langit"),("☱","兌","Duì","Danau"),("☲","離","Lí","Api"),("☳","震","Zhèn","Petir"),
             ("☷","坤","Kūn","Bumi"),("☶","艮","Gèn","Gunung"),("☵","坎","Kǎn","Air"),("☴","巽","Xùn","Angin")]
    bagua_svg_items = ""
    import math
    R = 56; cx = 60; cy = 60
    for i, (sym, hz, py, mean) in enumerate(bagua):
        ang = math.radians(-90 + i * 45)
        x = cx + R * math.cos(ang); y = cy + R * math.sin(ang)
        bagua_svg_items += f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" dominant-baseline="middle" fill="#C9A961" font-size="11" font-family="Noto Serif TC, serif" opacity="0.85">{sym}</text>'
    bagua_svg = f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="position:absolute; inset:0; width:100%; height:100%; pointer-events:none;">
  <circle cx="60" cy="60" r="58" fill="none" stroke="#C9A961" stroke-width="0.5" stroke-dasharray="2 1.5" opacity="0.6"/>
  <circle cx="60" cy="60" r="51" fill="none" stroke="#E5D3A1" stroke-width="0.3" opacity="0.4"/>
  {bagua_svg_items}
</svg>"""

    dragon_band = """<svg viewBox="0 0 200 14" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:8mm; opacity:0.55;" preserveAspectRatio="none">
  <defs><linearGradient id="goldFade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#C9A961" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#C9A961" stop-opacity="1"/>
    <stop offset="1" stop-color="#C9A961" stop-opacity="0"/>
  </linearGradient></defs>
  <line x1="0" y1="7" x2="200" y2="7" stroke="url(#goldFade)" stroke-width="0.4"/>
  <circle cx="100" cy="7" r="2.5" fill="#8B1A1A"/>
  <circle cx="100" cy="7" r="1.2" fill="#C9A961"/>
  <path d="M 75 7 Q 87 3 100 7 Q 113 11 125 7" fill="none" stroke="#C9A961" stroke-width="0.4"/>
  <path d="M 75 7 Q 87 11 100 7 Q 113 3 125 7" fill="none" stroke="#C9A961" stroke-width="0.4"/>
</svg>"""

    plr = pillars_full if pillars_full else ["", "", "", ""]
    pillars_mini = f"""<div class="cv-pillars-mini">
  <div class="pm-item"><div class="pm-lbl">TAHUN · 年</div><div class="pm-hz">{plr[0] or '—'}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item"><div class="pm-lbl">BULAN · 月</div><div class="pm-hz">{plr[1] or '—'}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item active"><div class="pm-lbl">HARI · 日</div><div class="pm-hz">{plr[2] or '—'}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item"><div class="pm-lbl">JAM · 時</div><div class="pm-hz">{plr[3] or '—'}</div></div>
</div>"""

    seal_svg = """<svg class="cv-seal" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="36" height="36" fill="#8B1A1A" rx="1"/>
  <rect x="3" y="3" width="34" height="34" fill="none" stroke="#F5EBD0" stroke-width="0.4"/>
  <text x="11" y="17" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">命</text>
  <text x="22" y="17" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">理</text>
  <text x="11" y="33" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">真</text>
  <text x="22" y="33" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">解</text>
</svg>"""

    return f"""<section class="page cover">
  <div class="cv-frame">
    <span class="cv-watermark tl">福</span>
    <span class="cv-watermark br">壽</span>
    <span class="cv-watermark cnr-tr" style="top:50%; right:6mm; font-size:140pt; transform:rotate(90deg) translateY(50%); transform-origin: right center;">命</span>

    <div class="cv-top-band">{dragon_band}</div>
    <div class="cv-eyebrow">命 · Laporan Ramalan Tionghoa Klasik · 命</div>

    <div class="cv-title-block">
      <div class="cv-title-cn">命</div>
      <div class="cv-title-id">Mìng — Takdir &amp; Bagan Hidup</div>
      <div class="cv-title-sub">四柱論命 · 紫微斗數 · 風水陽宅</div>
    </div>

    <div class="cv-mid">
      <div class="cv-shio-wrap">
        {bagua_svg}
        <div class="cv-shio-frame" data-shio="{shio_hz} · {shio_id.upper() if shio_id else ''}">{shio_inner}</div>
      </div>
      <div class="cv-name-row">
        <div class="cv-name">{html.escape(nama)}</div>
      </div>

      {pillars_mini}

      <div class="cv-info-panel">
        <div class="row"><span class="lbl">Tanggal Lahir (Indonesia)</span><span class="colon">:</span><span class="val">{nasional_display}</span></div>
        <div class="row"><span class="lbl">Tanggal Lahir (Tionghoa)</span><span class="colon">:</span><span class="val">{tionghoa_display}</span></div>
        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">{jam_formatted}</span></div>
        <div class="row"><span class="lbl">Shio</span><span class="colon">:</span><span class="val"><span class="hz">{shio_hz}</span> {shio_id}</span></div>
        {f'<div class="row"><span class="lbl">Penguasa Hari</span><span class="colon">:</span><span class="val">{dm_line}</span></div>' if dm_line else ''}
        {f'<div class="row"><span class="lbl">Elemen Utama</span><span class="colon">:</span><span class="val">{elem_line}</span></div>' if elem_line else ''}
      </div>
    </div>

    <div class="cv-bottom">
      <div class="cv-footer-l">
        <div class="cv-footer-line">八字 · 紫微斗數 · 風水陽宅</div>
        <div class="cv-footer-date">Disusun · {TODAY}</div>
      </div>
      {seal_svg}
    </div>
  </div>
</section>"""


def build_cover(subject, sections=None):
    """Original V4.6 cover format (pre v1/v2 testing)."""
    nama = subject.get("Nama", "")
    shio = subject.get("Shio", "Kelinci")
    # Bridge new MD subject keys → old expected keys
    if "Kalender Nasional" in subject and "Lahir" not in subject:
        # Build "Lahir" string from new keys
        nas = subject.get("Kalender Nasional", "")
        lun = subject.get("Kalender Lunar", "")
        tahun_m = subject.get("Tahun Lahir (Masehi)", "")
        # Extract DD Bulan from Kalender Nasional — search for digit + Indonesian month name
        bulan_pat = "|".join(BULAN_INDO[1:])
        nas_m = re.search(r"(\d{1,2})\s+(" + bulan_pat + r")", nas)
        nas_str = f"{nas_m.group(1)} {nas_m.group(2)} {tahun_m}" if (nas_m and tahun_m) else nas
        # Extract DD bulan from Kalender Lunar (e.g. "癸卯 52 年, 1 月 5 日")
        lun_m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", lun)
        if lun_m:
            lun_str = f"{lun_m.group(2)} {BULAN_INDO[int(lun_m.group(1))] if int(lun_m.group(1)) <= 12 else lun_m.group(1)} {tahun_m}"
        else:
            lun_str = lun
        subject = dict(subject)
        subject["Lahir"] = f"{nas_str} (Kalender Nasional) / {lun_str} (Kalender Imlek)"
    if "Jam Lahir" in subject and "Jam" not in subject:
        # "13 時 30 分" → "13:30"
        jm = re.match(r"(\d{1,2})\s*時\s*(\d{1,2})\s*分", subject.get("Jam Lahir", ""))
        if jm:
            subject = dict(subject)
            subject["Jam"] = f"{jm.group(1)}:{jm.group(2).zfill(2)}"
        else:
            subject["Jam"] = subject.get("Jam Lahir", "")
    shio_id = re.sub(r"[\(\)（）]", "", shio).split()[0].strip() if shio else "Kelinci"
    # Pick the Indonesian shio name (e.g. "Kelinci")
    for k in SHIO_MAP:
        if k in shio:
            shio_id = k
            break
    shio_hz, shio_emoji, shio_py = SHIO_MAP.get(shio_id, ("兔", "🐰", "mǎo"))
    gender = subject.get("Jenis Kelamin", "")
    lahir = subject.get("Lahir", "")
    jam = subject.get("Jam", "")
    soft = subject.get("Software", "")

    # Parse dates: "29 Januari 1963 (Kalender Nasional) / 5 Januari 1963 (Kalender Imlek)"
    dates = lahir.split("/")
    nasional_raw = dates[0].strip() if dates else ""
    imlek_raw = dates[1].strip() if len(dates) > 1 else ""
    # Strip "(Kalender X)" annotations
    nasional_clean = re.sub(r"\s*\([^)]*Kalender[^)]*\)", "", nasional_raw).strip()
    imlek_clean = re.sub(r"\s*\([^)]*Kalender[^)]*\)", "", imlek_raw).strip()

    # Day of week — prefer MD-provided value, else compute
    dow_str = ""
    raw_hari = subject.get("Hari Lahir", "")
    if raw_hari:
        # Format: "星期二 — Selasa" → extract last word
        hm = re.search(r"\b(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)\b", raw_hari)
        if hm: dow_str = hm.group(1)
    dd, mm, yy = parse_indo_date(nasional_clean)
    if not dow_str and dd and mm and yy:
        try:
            import datetime as _dt
            wk = _dt.date(yy, mm, dd).weekday()
            dow_str = DOW_INDO[wk]
        except Exception:
            pass

    # Imlek format
    imlek_formatted = imlek_clean
    idd, imm, iyy = parse_indo_date(imlek_clean)

    # Pillars from sections (BA ZI year pillar — used for 4-pilar mini badge)
    pillars_full, gans, zhis = extract_pillars(sections or [])

    # Lunar year pillar — different from BA ZI year (use for "Tanggal Tionghoa" display)
    # Source: subject["Kalender Lunar"] starts with [Hanzi pilar] (e.g. "癸卯 52 年...")
    lunar_pillar = ""
    lunar_pillar_py = ""
    raw_lunar = subject.get("Kalender Lunar", "")
    lp_m = re.match(r"^([一-鿿]{2})", raw_lunar)
    if lp_m:
        lunar_pillar = lp_m.group(1)
        lunar_pillar_py = f"{GAN_PY.get(lunar_pillar[0], '')} {ZHI_PY.get(lunar_pillar[1], '')}".strip()

    # Fallback to BA ZI year pillar if no lunar
    if not lunar_pillar and pillars_full:
        lunar_pillar = pillars_full[0]
        if len(lunar_pillar) >= 2:
            lunar_pillar_py = f"{GAN_PY.get(lunar_pillar[0], '')} {ZHI_PY.get(lunar_pillar[1], '')}".strip()

    if idd and imm and lunar_pillar:
        imlek_formatted = f'tanggal {idd} bulan {imm} tahun <span class="hz">{lunar_pillar}</span> <em>({lunar_pillar_py} · {iyy or yy})</em>'
    elif imlek_clean:
        imlek_formatted = imlek_clean

    # Time → shichen + tod
    jam_formatted = jam
    jh_m = re.match(r"(\d{1,2}):", jam)
    if jh_m:
        h = int(jh_m.group(1))
        sh_hz, sh_py = hour_to_shichen(h)
        tod = hour_to_tod(h)
        jam_formatted = f'pukul {jam} <em>({tod} · <span class="hz">{sh_hz}</span>)</em>'

    # Day Master
    dm_gan = gans[2] if gans and gans[2] else ""
    dm_indo, dm_hz = DM_INDO.get(dm_gan, ("", ""))
    dm_line = f'{dm_indo} <span class="hz">{dm_hz}</span>' if dm_gan else ""

    # Elemen Utama (Xi + Yong shen)
    favs = extract_yong_xi_elements(sections or [])
    elem_line = ""
    if favs:
        indo_names = " &amp; ".join(f[0] for f in favs)
        hz_chars = " ".join(f[1] for f in favs if f[1])
        elem_line = f'{indo_names} <span class="hz">{hz_chars}</span>'

    # SVG shio asset — try multiple known locations
    SVG_DIRS = [
        Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\v45\assets"),
        Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\assets"),
        Path(__file__).parent / "assets",
        Path(__file__).parent.parent / "assets",
    ]
    svg_url = ""
    for asset_dir in SVG_DIRS:
        svg_path = asset_dir / f"{shio_id}-Merah.svg"
        if svg_path.exists():
            svg_url = "file:///" + str(svg_path).replace("\\", "/")
            break
    shio_inner = f'<img src="{svg_url}" alt="{shio_id}" style="width: 100%; height: 100%; object-fit: contain;">' if svg_url else f'<span style="font-size: 50pt;">{shio_emoji}</span>'

    # 8 Bagua trigrams (Pre-Heaven order, clockwise from top)
    bagua = [
        ("☰", "乾", "Qián", "Langit"),     # N (top)
        ("☱", "兌", "Duì", "Danau"),       # NE
        ("☲", "離", "Lí", "Api"),          # E
        ("☳", "震", "Zhèn", "Petir"),      # SE
        ("☷", "坤", "Kūn", "Bumi"),        # S (bottom)
        ("☶", "艮", "Gèn", "Gunung"),      # SW
        ("☵", "坎", "Kǎn", "Air"),         # W
        ("☴", "巽", "Xùn", "Angin"),       # NW
    ]
    bagua_svg_items = ""
    import math
    R = 56  # radius
    cx, cy = 60, 60
    for i, (sym, hz, py, mean) in enumerate(bagua):
        ang = math.radians(-90 + i * 45)  # start top
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        bagua_svg_items += f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" dominant-baseline="middle" fill="#C9A961" font-size="11" font-family="Noto Serif TC, serif" opacity="0.85">{sym}</text>'

    # Outer ring + inner circle decorative
    bagua_svg = f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="position:absolute; inset:0; width:100%; height:100%; pointer-events:none;">
  <circle cx="60" cy="60" r="58" fill="none" stroke="#C9A961" stroke-width="0.5" stroke-dasharray="2 1.5" opacity="0.6"/>
  <circle cx="60" cy="60" r="51" fill="none" stroke="#E5D3A1" stroke-width="0.3" opacity="0.4"/>
  {bagua_svg_items}
</svg>"""

    # Decorative double-dragon scroll SVG band (top of cover)
    dragon_band = """<svg viewBox="0 0 200 14" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:8mm; opacity:0.55;" preserveAspectRatio="none">
  <defs>
    <linearGradient id="goldFade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#C9A961" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#C9A961" stop-opacity="1"/>
      <stop offset="1" stop-color="#C9A961" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <line x1="0" y1="7" x2="200" y2="7" stroke="url(#goldFade)" stroke-width="0.4"/>
  <circle cx="100" cy="7" r="2.5" fill="#8B1A1A"/>
  <circle cx="100" cy="7" r="1.2" fill="#C9A961"/>
  <path d="M 75 7 Q 87 3 100 7 Q 113 11 125 7" fill="none" stroke="#C9A961" stroke-width="0.4"/>
  <path d="M 75 7 Q 87 11 100 7 Q 113 3 125 7" fill="none" stroke="#C9A961" stroke-width="0.4"/>
</svg>"""

    # 4-Pillars mini badge band — dynamic from MD
    plr = pillars_full if pillars_full else ["", "", "", ""]
    pillars_mini = f"""<div class="cv-pillars-mini">
  <div class="pm-item"><div class="pm-lbl">TAHUN · 年</div><div class="pm-hz">{plr[0] or '—'}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item"><div class="pm-lbl">BULAN · 月</div><div class="pm-hz">{plr[1] or '—'}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item active"><div class="pm-lbl">HARI · 日</div><div class="pm-hz">{plr[2] or '—'}</div></div>
  <div class="pm-sep">·</div>
  <div class="pm-item"><div class="pm-lbl">JAM · 時</div><div class="pm-hz">{plr[3] or '—'}</div></div>
</div>"""

    # Seal stamp (red square chop)
    seal_svg = """<svg class="cv-seal" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="36" height="36" fill="#8B1A1A" rx="1"/>
  <rect x="3" y="3" width="34" height="34" fill="none" stroke="#F5EBD0" stroke-width="0.4"/>
  <text x="11" y="17" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">命</text>
  <text x="22" y="17" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">理</text>
  <text x="11" y="33" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">真</text>
  <text x="22" y="33" fill="#F5EBD0" font-family="Noto Serif TC, serif" font-size="13" font-weight="700">解</text>
</svg>"""

    return f"""<section class="page cover">
  <div class="cv-frame">
    <span class="cv-watermark tl">福</span>
    <span class="cv-watermark br">壽</span>
    <span class="cv-watermark cnr-tr" style="top:50%; right:6mm; font-size:140pt; transform:rotate(90deg) translateY(50%); transform-origin: right center;">命</span>

    <div class="cv-top-band">{dragon_band}</div>

    <div class="cv-eyebrow">命 · Laporan Ramalan Tionghoa Klasik · 命</div>

    <div class="cv-title-block">
      <div class="cv-title-cn">命</div>
      <div class="cv-title-id">Mìng — Takdir &amp; Bagan Hidup</div>
      <div class="cv-title-sub">四柱論命 · 紫微斗數 · 風水陽宅</div>
    </div>

    <div class="cv-mid">
      <div class="cv-shio-wrap">
        {bagua_svg}
        <div class="cv-shio-frame" data-shio="{shio_hz} · {shio_id.upper()}">{shio_inner}</div>
      </div>
      <div class="cv-name-row">
        <div class="cv-name">{html.escape(nama)}</div>
      </div>

      {pillars_mini}

      <div class="cv-info-panel">
        <div class="row"><span class="lbl">Tanggal Lahir (Indonesia)</span><span class="colon">:</span><span class="val">{html.escape(nasional_clean)}{f' <em>({dow_str})</em>' if dow_str else ''}</span></div>
        <div class="row"><span class="lbl">Tanggal Lahir (Tionghoa)</span><span class="colon">:</span><span class="val">{imlek_formatted}</span></div>
        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">{jam_formatted}</span></div>
        <div class="row"><span class="lbl">Shio</span><span class="colon">:</span><span class="val"><span class="hz">{shio_hz}</span> {shio_id}</span></div>
        {f'<div class="row"><span class="lbl">Penguasa Hari</span><span class="colon">:</span><span class="val">{dm_line}</span></div>' if dm_line else ''}
        {f'<div class="row"><span class="lbl">Elemen Utama</span><span class="colon">:</span><span class="val">{elem_line}</span></div>' if elem_line else ''}
      </div>
    </div>

    <div class="cv-bottom">
      <div class="cv-footer-l">
        <div class="cv-footer-line">八字 · 紫微斗數 · 風水陽宅</div>
        <div class="cv-footer-date">Disusun · {TODAY}</div>
      </div>
      {seal_svg}
    </div>
  </div>
</section>"""


def md_inline_simple(s):
    """Inline render WITHOUT escape (for strings already plain)."""
    s = re.sub(r"\(([^)]*)\)", r"<em>(\1)</em>", s)
    s = re.sub(r"([一-鿿]+)", r'<span class="hz">\1</span>', s)
    return s


# Section icon (single Hanzi) per BAB — new MD 16 BABs
SECTION_ICONS = {
    1: "命",   # Empat Pilar
    2: "宮",   # 12 Istana
    3: "性",   # Karakter
    4: "官",   # Karir
    5: "財",   # Keuangan
    6: "夫",   # Pernikahan
    7: "子",   # Anak
    8: "疾",   # Kesehatan
    9: "父",   # Orang Tua
    10: "僕",  # Bawahan
    11: "宅",  # Properti + Feng Shui
    12: "遷",  # Perpindahan
    13: "福",  # Peruntungan
    14: "煞",  # Bintang Khusus
    15: "宿",  # Takdir
    16: "流",  # Ramalan Tahunan
}

# Chapter groupings — 5 chapters in BAB sequence order (no page gaps)
CHAPTERS = [
    {"roman": "I",   "hz": "本命", "id": "Fondasi Diri",                  "py": "Běn Mìng",  "secs": [1, 2, 3]},
    {"roman": "II",  "hz": "生活", "id": "Karir, Keuangan, Hubungan",      "py": "Shēng Huó", "secs": [4, 5, 6, 7]},
    {"roman": "III", "hz": "身親", "id": "Kesehatan &amp; Keluarga",       "py": "Shēn Qīn",  "secs": [8, 9, 10]},
    {"roman": "IV",  "hz": "居所", "id": "Tempat &amp; Pergerakan",        "py": "Jū Suǒ",    "secs": [11, 12]},
    {"roman": "V",   "hz": "氣運", "id": "Nasib &amp; Masa Depan",         "py": "Qì Yùn",    "secs": [13, 14, 15, 16]},
]


def build_toc(toc_items, subject_name, page_starts, extras=None):
    """Visual TOC with 5 chapter blocks + extras section.

    extras: list of dicts {label, hz, page} for non-BAB pages (pengantar/siklus/kesimpulan/etc).
    """
    # Index toc by section number
    toc_by_num = {it["num"]: it for it in toc_items}

    chapter_blocks = ""
    for i, ch in enumerate(CHAPTERS):
        secs_html = ""
        for snum in ch["secs"]:
            it = toc_by_num.get(snum)
            if not it: continue
            ttl = it["title"]
            # Strip "(Hanzi)" from title
            hz_m = re.search(r"\(([一-鿿·\s]+)\)", ttl)
            hz_part = hz_m.group(1).strip() if hz_m else ""
            id_part = re.sub(r"\s*\([一-鿿·\s]+\)", "", ttl).strip()
            pg = page_starts.get(snum, "—")
            icon = SECTION_ICONS.get(snum, "·")
            secs_html += f"""<div class="ch-row">
  <div class="ch-icon">{icon}</div>
  <div class="ch-num">{snum:02d}</div>
  <div class="ch-ttl">
    <div class="id">{html.escape(id_part)}</div>
    <div class="hz">{hz_part}</div>
  </div>
  <div class="ch-dots"></div>
  <div class="ch-pg">{pg}</div>
</div>"""
        # Chapter range
        sec_pages = [page_starts.get(s, 0) for s in ch["secs"] if s in page_starts]
        pg_range = f"{min(sec_pages)}–{max(sec_pages)}" if sec_pages else "—"
        chapter_blocks += f"""<div class="ch-block">
  <div class="ch-head">
    <div class="ch-roman">{ch['roman']}</div>
    <div class="ch-titles">
      <div class="ch-hz">{ch['hz']} <span class="py">{ch['py']}</span></div>
      <div class="ch-id">{ch['id']}</div>
    </div>
    <div class="ch-range">hal. {pg_range}</div>
  </div>
  <div class="ch-rows">{secs_html}</div>
</div>"""

    # Top overview band
    overview_html = ""
    for ch in CHAPTERS:
        sec_pages = [page_starts.get(s, 0) for s in ch["secs"] if s in page_starts]
        pg_range = f"{min(sec_pages)}–{max(sec_pages)}" if sec_pages else "—"
        overview_html += f"""<div class="ov-card">
  <div class="ov-roman">{ch['roman']}</div>
  <div class="ov-hz">{ch['hz']}</div>
  <div class="ov-pg">hal. {pg_range}</div>
</div>"""

    body = f"""<div class="toc-lead">
  <div class="toc-lead-hz">目 錄</div>
  <div class="toc-lead-text">Laporan ini terdiri dari <strong>{len(toc_items)} bab</strong> yang dikelompokkan menjadi <strong>5 bagian besar</strong>, ditambah pengantar, kesimpulan, glosarium, dan disclaimer. Setiap bab fokus pada satu dimensi hidup dan dapat dibaca berdiri sendiri.</div>
</div>

<div class="toc-overview">{overview_html}</div>

<div class="toc-chapters">{chapter_blocks}</div>"""

    # Extras as Section VI (same red style as chapters)
    if extras:
        # Sort by page
        sorted_extras = sorted(extras, key=lambda x: x.get("page", 9999))
        extras_rows = ""
        for x in sorted_extras:
            extras_rows += f"""<div class="ch-row">
  <div class="ch-icon">{x.get('icon', '·')}</div>
  <div class="ch-num">·</div>
  <div class="ch-ttl">
    <div class="id">{x.get('label', '')}</div>
    <div class="hz">{x.get('hz', '')}</div>
  </div>
  <div class="ch-dots"></div>
  <div class="ch-pg">{x.get('page', '—')}</div>
</div>"""

        pgs = [x.get("page", 0) for x in sorted_extras if x.get("page")]
        pg_range = f"{min(pgs)}–{max(pgs)}" if pgs else "—"
        extras_block = f"""<div class="ch-block">
  <div class="ch-head">
    <div class="ch-roman">VI</div>
    <div class="ch-titles">
      <div class="ch-hz">附錄 <span class="py">Fù Lù</span></div>
      <div class="ch-id">Lampiran &amp; Penutup</div>
    </div>
    <div class="ch-range">hal. {pg_range}</div>
  </div>
  <div class="ch-rows">{extras_rows}</div>
</div>"""

        # Insert into chapters grid (so it shares 2-col layout with I-V)
        body = body.replace(
            f'<div class="toc-chapters">{chapter_blocks}</div>',
            f'<div class="toc-chapters">{chapter_blocks}{extras_block}</div>'
        )

    return page(2, "Daftar Isi", "目 錄", "DAFTAR ISI", body, subject_name)


def build_pengantar(subject_name):
    body = """<div class="pg-hero">
  <div class="pg-hero-mark">前</div>
  <div class="pg-hero-text">
    <div class="pg-hero-title">Selamat Datang</div>
    <div class="pg-hero-sub">Laporan ini adalah <strong>peta</strong> bawaan kelahiran Anda — bukan vonis takdir. 16 bab membahas karakter, karir, keuangan, hubungan, kesehatan, dan masa depan, plus rangkuman saran praktis.</div>
  </div>
</div>

<div class="pg-method-grid">
  <div class="pg-method-card">
    <div class="pg-method-hz">八字</div>
    <div class="pg-method-py">Bā Zì</div>
    <div class="pg-method-id">Empat Pilar Kelahiran</div>
    <div class="pg-method-desc">Sistem berdasarkan <strong>Tahun · Bulan · Hari · Jam</strong> lahir — fondasi karakter, keuangan, kesehatan, &amp; relasi.</div>
  </div>
  <div class="pg-method-card highlight">
    <div class="pg-method-hz">紫微</div>
    <div class="pg-method-py">Zǐ Wēi Dǒu Shù</div>
    <div class="pg-method-id">12 Istana Hidup</div>
    <div class="pg-method-desc">Memetakan <strong>12 istana</strong> — pasangan, anak, properti, karir — masing-masing dihuni bintang arketipe.</div>
  </div>
  <div class="pg-method-card">
    <div class="pg-method-hz">陽宅</div>
    <div class="pg-method-py">Yáng Zhái</div>
    <div class="pg-method-id">Feng Shui Rumah</div>
    <div class="pg-method-desc">Tata letak hunian: arah hadap, posisi pintu, kompor, kamar — diselaraskan dengan elemen bawaan Anda.</div>
  </div>
</div>

<div class="pg-section-title">
  <span class="num">1</span><span class="ttl">Cara Membaca Laporan</span><span class="hz">如何閱讀</span>
</div>

<div class="pg-step-grid">
  <div class="pg-step">
    <div class="pg-step-num">01</div>
    <div class="pg-step-ttl">Tidak Perlu Berurutan</div>
    <div class="pg-step-txt">Langsung ke bab yang paling relevan dengan situasi Anda saat ini. Tiap bab dapat berdiri sendiri.</div>
  </div>
  <div class="pg-step">
    <div class="pg-step-num">02</div>
    <div class="pg-step-ttl">Cek Skor Persentase</div>
    <div class="pg-step-txt">Persentase = <strong>kecenderungan bawaan</strong>. Tinggi = kekuatan alami. Rendah = area untuk dilatih.</div>
  </div>
  <div class="pg-step">
    <div class="pg-step-num">03</div>
    <div class="pg-step-ttl">Catat &amp; Refleksi</div>
    <div class="pg-step-txt">Tandai bagian yang resonan dan yang terasa janggal. Bagan adalah titik awal, bukan titik akhir.</div>
  </div>
  <div class="pg-step">
    <div class="pg-step-num">04</div>
    <div class="pg-step-ttl">Terapkan Bertahap</div>
    <div class="pg-step-txt">Pilih 1-2 rekomendasi paling konkret dulu — feng shui, profesi, jadwal — coba 30 hari, evaluasi.</div>
  </div>
</div>

<div class="pg-section-title">
  <span class="num">2</span><span class="ttl">Skala Persentase Bawaan</span><span class="hz">百分尺度</span>
</div>

<div class="pg-scale-demo">
  <div class="pg-scale-row">
    <div class="pg-scale-lbl"><strong>Kuat</strong> · 70% &amp; ke atas</div>
    <div class="bar-track"><div class="bar-fill high" style="width: 78%"></div></div>
    <div class="pg-scale-pct">78%</div>
    <div class="pg-scale-note">Kekuatan alami — maksimalkan tanpa banyak usaha tambahan.</div>
  </div>
  <div class="pg-scale-row">
    <div class="pg-scale-lbl"><strong>Seimbang</strong> · 50–69%</div>
    <div class="bar-track"><div class="bar-fill mid" style="width: 60%"></div></div>
    <div class="pg-scale-pct">60%</div>
    <div class="pg-scale-note">Cukup — bisa lebih baik dengan latihan dan lingkungan tepat.</div>
  </div>
  <div class="pg-scale-row">
    <div class="pg-scale-lbl"><strong>Perlu Dilatih</strong> · &lt; 50%</div>
    <div class="bar-track"><div class="bar-fill low" style="width: 35%"></div></div>
    <div class="pg-scale-pct">35%</div>
    <div class="pg-scale-note">Bukan kelemahan permanen — area untuk disiplin atau kompensasi.</div>
  </div>
</div>

<div class="pg-closing">
  <div class="pg-closing-seal">命</div>
  <div class="pg-closing-text">
    <strong>Selamat membaca.</strong> Bagan adalah <em>kompas</em>, bukan jadwal. Anda tetap pelaku utama dalam hidup Anda — kebijaksanaan, kebebasan, dan tindakan Anda yang membentuk hasil akhir.
  </div>
</div>"""
    return page(3, "Pengantar &amp; Cara Membaca", "前 言", "PENGANTAR", body, subject_name)


# === SECTION 1 - EMPAT PILAR ===

def pot_block_pair(pos_list, warn_list, fav_head="Faktor Pendukung", warn_head="Yang Diwaspadai"):
    """Render Pendukung / Diwaspadai as side-by-side blocks. Hide warn block if empty."""
    pos_html = "".join(f'<div class="pot-item fav">{md_inline(b)}</div>' for b in pos_list)
    warn_html = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in warn_list)
    if pos_list and warn_list:
        return f"""<div class="potensi-grid">
  <div class="potensi-block fav">
    <div class="potensi-head"><span class="ico">✦</span> {fav_head}</div>
    <div class="pot-stack">{pos_html}</div>
  </div>
  <div class="potensi-block unfav">
    <div class="potensi-head"><span class="ico">⚠</span> {warn_head}</div>
    <div class="pot-stack">{warn_html}</div>
  </div>
</div>"""
    elif pos_list:
        return f"""<div class="potensi-block fav full-w">
  <div class="potensi-head"><span class="ico">✦</span> {fav_head}</div>
  <div class="pot-stack">{pos_html}</div>
</div>"""
    elif warn_list:
        return f"""<div class="potensi-block unfav full-w">
  <div class="potensi-head"><span class="ico">⚠</span> {warn_head}</div>
  <div class="pot-stack">{warn_html}</div>
</div>"""
    return ""


def render_interpretasi(text):
    """Visual interpretasi callout (no title) — placed at TOP of page for quick understanding."""
    if not text:
        return ""
    return f"""<div class="interp-block">
  <div class="interp-icon">💡</div>
  <div class="interp-text">{md_inline(text)}</div>
</div>"""


def build_section_1(sec, subject_name, page_num):
    """BAB 1: BA ZI Empat Pilar — new MD format."""
    lines = sec["lines"]
    text = "\n".join(lines)

    # Parse 4 Pillars table (rows: Ten God, Tian Gan, Di Zhi, Akar, Ten God Berlapis)
    pilar_data = {}
    cols = ["Tahun", "Bulan", "Hari", "Jam"]
    GAN_ELEM = {"甲":"Kayu","乙":"Kayu","丙":"Api","丁":"Api","戊":"Tanah","己":"Tanah","庚":"Logam","辛":"Logam","壬":"Air","癸":"Air"}
    ZHI_ELEM = {"子":"Air","丑":"Tanah","寅":"Kayu","卯":"Kayu","辰":"Tanah","巳":"Api","午":"Api","未":"Tanah","申":"Logam","酉":"Logam","戌":"Tanah","亥":"Air"}
    for line in lines:
        if "Ten God" in line and "十神" in line and "Berlapis" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            for i, c in enumerate(cells[1:5]):
                pilar_data.setdefault(i, {})["ten_god"] = re.sub(r"\([^)]*\)", "", c).strip()
        if "Batang Langit" in line and "天干" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            for i, c in enumerate(cells[1:5]):
                m = re.match(r"^([一-鿿]+)\s*(.+)", c)
                if m:
                    pilar_data.setdefault(i, {})["gan"] = m.group(1)
                    pilar_data[i]["gan_id"] = m.group(2).strip()
        if "Cabang Bumi" in line and "地支" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            for i, c in enumerate(cells[1:5]):
                m = re.match(r"^([一-鿿]+)\s*(.+)", c)
                if m:
                    pilar_data.setdefault(i, {})["zhi"] = m.group(1)
                    pilar_data[i]["zhi_id"] = m.group(2).strip()

    # Derive element from gan
    for i, d in pilar_data.items():
        if "gan" in d:
            d["elem"] = GAN_ELEM.get(d["gan"], "")

    pilar_html = ""
    for i, col in enumerate(cols):
        d = pilar_data.get(i, {})
        gan = d.get("gan", "")
        zhi = d.get("zhi", "")
        gan_id = d.get("gan_id", "")
        zhi_id = d.get("zhi_id", "")
        elem = d.get("elem", "")
        ten_god = d.get("ten_god", "")
        is_dm = (col == "Hari")
        cls = "pilar-card dm" if is_dm else "pilar-card"
        dm_tag = '<div class="pilar-dm-tag">DAY MASTER</div>' if is_dm else ""
        pilar_html += f"""<div class="{cls}">
  <div class="pilar-label">{col} <span class="hz">{['年','月','日','時'][i]}</span></div>
  <div class="pilar-tag">{gan}{zhi}</div>
  <div class="pilar-tag-id">{gan_id} · {zhi_id}</div>
  <div class="pilar-element">{elem}</div>
  {dm_tag}
</div>"""

    # Parse Transformasi (huaxing) table — new format: | Bintang | Transformasi | Makna |
    huaxing = []
    in_hx = False
    for line in lines:
        if "Transformasi Bintang" in line:
            in_hx = True; continue
        if in_hx and "|" in line and "---" not in line and "Bintang" not in line.split("|")[1] if line.count("|") > 1 else False:
            parts = [c.strip() for c in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0]:
                huaxing.append({"star": parts[0], "trans": parts[1], "meaning": parts[2]})
        if in_hx and line.startswith("###"):
            in_hx = False
    # Re-parse fallback (logic above has truthiness issue)
    if not huaxing:
        in_hx = False
        for line in lines:
            if "Transformasi Bintang" in line:
                in_hx = True; continue
            if in_hx and line.startswith("###"):
                in_hx = False; continue
            if in_hx and "|" in line and "---" not in line:
                parts = [c.strip() for c in line.strip("|").split("|")]
                if len(parts) >= 3 and parts[0] and "Bintang" not in parts[0]:
                    huaxing.append({"star": parts[0], "trans": parts[1], "meaning": parts[2]})

    hx_html = ""
    for h in huaxing:
        m = re.match(r"^([一-鿿]+)\s*(.+)", h["star"])
        star = m.group(1) if m else h["star"]
        py = m.group(2).strip() if m else ""
        hx_html += f"""<div class="huaxing-card">
  <div class="star">{star}</div>
  <div class="pinyin">{py}</div>
  <div class="trans">{md_inline(h['trans'])}</div>
  <div class="meaning">{md_inline(h['meaning'])}</div>
</div>"""

    # Parse 喜用神 table (new format: | Kategori | Elemen | Makna Praktis |)
    shen = []
    in_shen = False
    for line in lines:
        if "喜用神" in line or "Elemen Keberuntungan" in line:
            in_shen = True; continue
        if in_shen and line.startswith("###"):
            in_shen = False; continue
        if in_shen and line.strip().startswith(">"):
            in_shen = False; continue
        if in_shen and "|" in line and "---" not in line:
            parts = [c.strip() for c in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0] and "Kategori" not in parts[0]:
                shen.append({"cat": parts[0], "elem": parts[1], "desc": parts[2]})

    shen_html = ""
    cat_map = {"用": "use", "喜": "fav", "閒": "neutral", "仇": "unfav", "忌": "unfav"}
    for s in shen:
        cat_hz = re.search(r"([一-鿿])", s["cat"])
        css_cls = cat_map.get(cat_hz.group(1) if cat_hz else "", "neutral")
        cat_clean = re.sub(r"\*\*", "", s["cat"])
        # Elem: "木 Kayu" → split
        elem_cell = s["elem"]
        em_m = re.match(r"^([一-鿿]+)\s*(.*)", elem_cell)
        elem_hz = em_m.group(1) if em_m else elem_cell
        elem_id = em_m.group(2).strip() if em_m else ""
        shen_html += f"""<div class="shen-card {css_cls}">
  <div class="lbl">{md_inline(cat_clean)}</div>
  <div class="elem"><span class="hz">{elem_hz}</span> {elem_id}</div>
  <div class="desc">{md_inline(s['desc'])}</div>
</div>"""

    # Strength meter — new MD format: "**+4.986 / −3.654** → ..."
    pos_val = neg_val = ""
    strength_note = ""
    for line in lines:
        m = re.search(r"\*\*\s*\+?([\d.]+)\s*/\s*[−\-]([\d.]+)\s*\*\*\s*→\s*(.+)", line)
        if m:
            pos_val = m.group(1); neg_val = m.group(2); strength_note = m.group(3).strip()
            break

    strength_html = ""
    if pos_val:
        try:
            pv = float(pos_val); nv = float(neg_val)
            if pv > nv * 1.2:
                bal_label = "Kuat"; bal_cls = "fav"; bal_desc = "Diri <strong>dominan</strong> — butuh elemen menyalurkan."
            elif nv > pv * 1.2:
                bal_label = "Lemah"; bal_cls = "unfav"; bal_desc = "Diri <strong>kurang dukungan</strong> — butuh elemen memperkuat."
            else:
                bal_label = "Seimbang"; bal_cls = "neutral"; bal_desc = "Dukungan dan tantangan <strong>setara</strong>."
        except Exception:
            bal_label = ""; bal_cls = ""; bal_desc = ""
        strength_html = f"""<div class="strength-explain">Bobot total <strong>8 elemen</strong> di bagan: <strong>+</strong> mendukung Pilar Hari, <strong>−</strong> melawan. Selisih = kuat/lemahnya diri.</div>
<div class="strength-meter">
  <div class="strength-side pos">
    <div class="lbl">Mendukung <span class="hz">日主旺</span></div>
    <div class="val">+{pos_val}</div>
  </div>
  <div class="strength-side neg">
    <div class="lbl">Melawan <span class="hz">日主弱</span></div>
    <div class="val">−{neg_val}</div>
  </div>
</div>
<div class="strength-balance {bal_cls}"><span class="bal-tag">{bal_label}</span><span class="bal-desc">{bal_desc}</span></div>"""

    # Wu Xing 5-element distribution
    elem_count = {"Kayu":0, "Api":0, "Tanah":0, "Logam":0, "Air":0}
    gans_zhis = []
    for line in lines:
        if "Batang Langit" in line and "天干" in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            for c in cs[1:5]:
                m = re.match(r"^([一-鿿]+)", c)
                if m: gans_zhis.append(("gan", m.group(1)))
        if "Cabang Bumi" in line and "地支" in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            for c in cs[1:5]:
                m = re.match(r"^([一-鿿]+)", c)
                if m: gans_zhis.append(("zhi", m.group(1)))
    for kind, ch in gans_zhis:
        e = GAN_ELEM.get(ch) if kind == "gan" else ZHI_ELEM.get(ch)
        if e: elem_count[e] += 1

    favs_indo = []; unfavs_indo = []
    for s in shen:
        cat = s["cat"]
        em = re.match(r"^[一-鿿]+\s*(\w+)", s["elem"])
        if not em: continue
        ename = em.group(1)
        if "用" in cat or "喜" in cat: favs_indo.append(ename)
        elif "忌" in cat or "仇" in cat: unfavs_indo.append(ename)

    elem_max = max(elem_count.values()) if any(elem_count.values()) else 1
    elem_hz_map = {"Kayu":"木","Api":"火","Tanah":"土","Logam":"金","Air":"水"}
    elem_order = ["Kayu","Api","Tanah","Logam","Air"]
    wuxing_html = ""
    for e in elem_order:
        cnt = elem_count[e]
        pct = int(round(cnt / elem_max * 100)) if elem_max else 0
        cls = "self"
        if e in favs_indo: cls = "fav"
        elif e in unfavs_indo: cls = "unfav"
        else: cls = ""
        wuxing_html += f"""<div class="wux-cell {cls}">
  <div class="wux-bar-track"><div class="wux-bar-fill" style="height: {pct}%;"></div></div>
  <div class="wux-label"><span class="hz">{elem_hz_map[e]}</span> {e} <span class="v">×{cnt}</span></div>
</div>"""

    # Siklus Besar (大運) — 10 dekade table
    siklus = []
    in_sb = False
    for line in lines:
        if "Siklus Besar" in line and "大運" in line and not in_sb:
            in_sb = True; continue
        if in_sb and line.startswith("###"):
            in_sb = False; continue
        if in_sb and line.strip().startswith(">"):
            in_sb = False
        if in_sb and "|" in line and "---" not in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            if len(cs) >= 2 and cs[0]:
                siklus.append(cs)

    # siklus[0] = header (Usia 3, 13, 23, ...), siklus[1] = pillars (甲寅, 乙卯, ...)
    siklus_html = ""
    if len(siklus) >= 2:
        usias = [c for c in siklus[0][1:] if c.isdigit()]
        pillars = [c for c in siklus[1][1:] if c]
        # Determine current dekade based on subject age
        # We don't have age dynamically; use 63 as placeholder (YUDY age 2026)
        # Better: parse from MD interpretasi mentioning "usia 63"
        cur_age_m = re.search(r"usia\s+(\d+)", text, re.IGNORECASE)
        cur_age = int(cur_age_m.group(1)) if cur_age_m else 0
        items = []
        for i, (u, p) in enumerate(zip(usias, pillars)):
            try: u_int = int(u)
            except: u_int = 0
            is_active = cur_age and u_int <= cur_age < u_int + 10
            cls = "active" if is_active else ""
            items.append(f"""<div class="sb-item {cls}">
  <div class="sb-age">{u}</div>
  <div class="sb-pillar">{p}</div>
</div>""")
        siklus_html = f"""<div class="siklus-besar">{''.join(items)}</div>"""

    # Extract two interpretasi blockquotes
    interps = extract_interpretasi(lines)
    interp1 = interps[0] if len(interps) > 0 else ""
    interp2 = interps[1] if len(interps) > 1 else ""

    # Intro paragraph (first paragraph of section)
    intro = ""
    for line in lines:
        if line.strip() and not line.startswith("#") and not line.startswith(">") and not line.startswith("|") and not line.startswith("-"):
            intro = line.strip()
            break

    # Page 1: Interpretasi (TOP) + 4 pilar + WuXing + Strength + Shen (intros lengkap, font kecil)
    body1 = f"""{render_interpretasi(interp1)}

<div class="card-title compact">Empat Pilar Kelahiran <span class="hz">四柱</span></div>
<div class="zw-section-intro tight"><strong>Empat Pilar (四柱)</strong> = momen kelahiran Anda dipotong jadi 4 pilar — Tahun, Bulan, Hari, Jam. Setiap pilar punya satu Batang Langit (天干) di atas dan satu Cabang Bumi (地支) di bawah. <strong>Pilar Hari = diri Anda sendiri</strong>; tiga pilar lain adalah lingkungan, keluarga, dan perjalanan hidup yang membentuk Anda.</div>
<div class="pilar-grid">{pilar_html}</div>

<div class="card-title compact">Distribusi 5 Unsur &amp; Kekuatan Hari <span class="hz">五行 · 日主</span></div>
<div class="zw-section-intro tight"><strong>5 Unsur (五行)</strong>: Kayu, Api, Tanah, Logam, Air. Tiap pilar membawa unsur tertentu — distribusi ini menunjukkan unsur mana yang <strong>terlalu banyak</strong> atau <strong>kurang</strong> di bagan Anda. Hijau = unsur yang membantu, merah = yang harus diwaspadai. <strong>Kekuatan Hari</strong> mengukur seberapa kuat Pilar Hari Anda dibandingkan elemen lain di bagan.</div>
<div class="grid-2-3" style="display:grid; grid-template-columns: 1.4fr 1fr; gap: 4mm; align-items: stretch;">
  <div class="wux-col">
    <div class="wuxing-strip wuxing-tall">
      <div class="wuxing-bar wuxing-bar-tall">{wuxing_html}</div>
      <div class="wuxing-legend">
        <span class="lg-item"><span class="dot fav"></span> Disukai (喜/用)</span>
        <span class="lg-item"><span class="dot self"></span> Netral (閒)</span>
        <span class="lg-item"><span class="dot unfav"></span> Dihindari (忌/仇)</span>
      </div>
    </div>
  </div>
  <div class="str-col">{strength_html}</div>
</div>

<div class="card-title compact">5 Dewa Elemen <span class="hz">喜用神</span></div>
<div class="zw-section-intro tight"><strong>5 Dewa Elemen</strong> mengkategorikan 5 unsur menjadi: <strong>用神</strong> paling dibutuhkan (kekurangan jadi tantangan), <strong>喜神</strong> pendukung yang menyenangkan, <strong>閒神</strong> netral tanpa pengaruh, <strong>仇神</strong> yang melawan diri, <strong>忌神</strong> yang harus dihindari. Pakai warna, arah, dan profesi yang sesuai dewa <strong>用</strong> &amp; <strong>喜</strong> untuk hidup lebih lancar.</div>
<div class="shen-row">{shen_html}</div>"""

    # Page 2: Interpretasi (TOP) + Huaxing + Siklus Besar
    body2 = f"""{render_interpretasi(interp2)}

<div class="char-block">
  <div class="char-block-head neutral">
    <div class="bd-ico">◆</div>
    <div class="bd-titles"><div class="bd-id">Transformasi Bintang Utama</div><div class="bd-hz">化星 · 四化</div></div>
    <div class="bd-cnt">{len(huaxing)} Bintang</div>
  </div>
  <div class="zw-section-intro"><strong>四化 (Si Hua)</strong> = empat transformasi bintang yang membentuk dinamika hidup Anda. Setiap orang punya 4 bintang ter-transformasi: satu membawa <strong>rezeki (祿)</strong>, satu <strong>kekuasaan (權)</strong>, satu <strong>prestasi (科)</strong>, dan satu <strong>hambatan (忌)</strong>. Tahu bintang mana yang ter-transformasi = tahu di area mana hidup Anda paling dinamis.</div>
  <div class="huaxing-grid">{hx_html}</div>
</div>

<div class="char-block">
  <div class="char-block-head neutral">
    <div class="bd-ico">◆</div>
    <div class="bd-titles"><div class="bd-id">Siklus Besar 10 Tahun</div><div class="bd-hz">大運 Dà Yùn</div></div>
    <div class="bd-cnt">{len(siklus[0]) - 1 if siklus else 0} Dekade</div>
  </div>
  <div class="zw-section-intro"><strong>大運 (Da Yun)</strong> = setiap 10 tahun Anda memasuki "iklim energi" baru dengan pilar penguasa berbeda. Pilar yang sedang aktif menentukan corak peruntungan dekade ini — bisa lebih beruntung di satu dekade dan lebih menantang di dekade lain. Dekade aktif saat ini ditandai <strong>khusus</strong>.</div>
  {siklus_html}
</div>"""

    pages = []
    pages.append(page(page_num, "Empat Pilar Kelahiran", "八字四柱", "BA ZI · 八字", body1, subject_name))
    pages.append(page(page_num + 1, "Transformasi &amp; Siklus Besar", "化星與大運", "BA ZI · 大運", body2, subject_name))
    return pages, page_num + 2


# === GENERIC SECTION ===

def parse_bullets(lines, start_marker_re=None):
    """Parse bullet points from `- ` lines."""
    bullets = []
    for line in lines:
        m = re.match(r"^-\s+(.+)", line)
        if m:
            bullets.append(m.group(1).strip())
    return bullets


def build_callouts_from_quotes(lines):
    """Convert > 💡 / > ⚠️ blockquotes into callout HTML."""
    out = []
    cur = []
    for line in lines:
        if line.startswith(">"):
            cur.append(line.lstrip("> ").strip())
        else:
            if cur:
                txt = " ".join(cur)
                cls = "info"; ico = "💡"
                if "⚠" in txt[:5]: cls = "warn"; ico = "⚠️"
                elif "💡" in txt[:5]: cls = "tip"; ico = "💡"
                elif "🎯" in txt[:5]: cls = "info"; ico = "🎯"
                elif "📌" in txt[:5]: cls = "info"; ico = "📌"
                elif "📝" in txt[:5]: cls = "info"; ico = "📝"
                elif "📊" in txt[:5]: cls = "info"; ico = "📊"
                elif "💊" in txt[:5]: cls = "tip"; ico = "💊"
                elif "✅" in txt[:5]: cls = "tip"; ico = "✅"
                txt = re.sub(r"^[💡⚠️🎯📌📝📊💊✅\s]+", "", txt)
                out.append(f'<div class="callout {cls}"><div class="ico">{ico}</div><div>{md_inline(txt)}</div></div>')
                cur = []
    if cur:
        txt = " ".join(cur)
        cls = "info"; ico = "💡"
        if "⚠" in txt[:5]: cls = "warn"; ico = "⚠️"
        elif "💡" in txt[:5]: cls = "tip"; ico = "💡"
        txt = re.sub(r"^[💡⚠️🎯📌📝📊💊✅\s]+", "", txt)
        out.append(f'<div class="callout {cls}"><div class="ico">{ico}</div><div>{md_inline(txt)}</div></div>')
    return out


def render_bullet_list(bullets, css_cls=""):
    if not bullets: return ""
    items = "".join(f'<div class="li">{md_inline(b)}</div>' for b in bullets)
    return f'<div class="list-bul {css_cls}">{items}</div>'


def render_rating_bars(rows):
    """rows = list of (id_label, hz_label, percent)"""
    out = []
    for id_lab, hz_lab, pct in rows:
        cls = percent_class(pct)
        out.append(f"""<div class="bar-row">
  <div class="bar-label"><div class="id">{id_lab}</div><div class="hz">{hz_lab}</div></div>
  <div class="bar-track"><div class="bar-fill {cls}" style="width: {pct}%"></div></div>
  <div class="bar-pct">{pct}%</div>
</div>""")
    return "".join(out)


def parse_rating_table(lines, header_marker):
    """Look for a markdown table with rating-like format. Returns list of (id, hz, pct)."""
    rows = []
    in_tbl = False
    for line in lines:
        if header_marker in line:
            in_tbl = True; continue
        if in_tbl:
            if "|" in line and "---" not in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 3:
                    if "Aspek" in cells[0] or "Hanzi" in cells[1]:
                        continue
                    pct_m = re.search(r"(\d+)%", line)
                    if pct_m:
                        rows.append((cells[0], cells[1], int(pct_m.group(1))))
            elif line.strip() == "" and rows:
                continue
            elif line.startswith("##") or line.startswith("---"):
                in_tbl = False
    return rows


def find_main_star(lines):
    """Look for **Bintang Utama:** ... line."""
    for line in lines:
        m = re.search(r"\*\*Bintang(?:\s+Utama)?(?:[^*]*)?:\*\*\s*(.+)", line)
        if m:
            return m.group(1).strip()
    return ""


def build_generic_section(sec, subject_name, page_num):
    """Generic single-page renderer for sections 3,6,7,9,11,12,13,14."""
    lines = sec["lines"]
    title = sec["title"]
    # Split title to ID + HZ
    m = re.match(r"^(.+?)\s*\(([一-鿿·\s]+)\)\s*$", title)
    id_t = m.group(1).strip() if m else title
    hz_t = m.group(2).strip() if m else ""
    label = "ZI WEI · 紫微"

    main_star = find_main_star(lines)
    star_tag = ""
    if main_star:
        m = re.match(r"^([一-鿿]+(?:\s*[一-鿿]+)?)\s*\(?(.*?)\)?\s*$", main_star)
        if m:
            star_tag = f'<div><span class="bintang-tag"><span class="lbl">Bintang Utama</span> {m.group(1)} {m.group(2)}</span></div>'
        else:
            star_tag = f'<div><span class="bintang-tag"><span class="lbl">Bintang Utama</span> {main_star}</span></div>'

    bullets = parse_bullets(lines)
    callouts = build_callouts_from_quotes(lines)

    # Render text-only bullets that include heading-prefixed paragraphs
    body_blocks = []

    # If section has subheading like "### Gambaran" treat as cards
    cur_section = None
    cur_bullets = []
    for line in lines:
        if line.startswith("### "):
            if cur_bullets:
                body_blocks.append({"kind": "card", "title": cur_section, "bullets": cur_bullets})
                cur_bullets = []
            cur_section = re.sub(r"^###\s+", "", line).strip()
        elif re.match(r"^-\s+", line):
            cur_bullets.append(re.sub(r"^-\s+", "", line).strip())
    if cur_bullets:
        body_blocks.append({"kind": "card", "title": cur_section, "bullets": cur_bullets})

    blocks_html = ""
    for blk in body_blocks:
        if blk["bullets"]:
            t = blk.get("title") or "Gambaran"
            blocks_html += f"""<div class="card">
  <div class="card-title">{md_inline(t)}</div>
  <div class="card-body">{render_bullet_list(blk['bullets'])}</div>
</div>"""

    callout_html = "".join(callouts)

    body = f"""{star_tag}
{blocks_html}
{callout_html}"""

    p = page(page_num, id_t, hz_t, label, body, subject_name)
    return [p], page_num + 1


# === SECTION 2 - KARAKTER ===

def build_section_2(sec, subject_name, page_num):
    """BAB 2: Zi Wei Dou Shu — 12 Istana grid."""
    lines = sec["lines"]

    # Parse 12 istana table — adaptive: 3-col or 4-col format
    palaces = []
    in_t = False
    header_cells = []
    for line in lines:
        # Detect start of palace table — header has "Istana"
        if not in_t and "|" in line and "Istana" in line and "---" not in line:
            in_t = True
            header_cells = [c.strip().lower() for c in line.strip("|").split("|")]
            continue
        if in_t and line.startswith("###"):
            in_t = False; continue
        if in_t and line.strip().startswith(">"):
            in_t = False
            continue
        if in_t and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0] and "Istana" not in cells[0]:
                # 3-col: Istana | Posisi | Bintang
                # 4-col: Istana | Posisi | Bintang | Catatan
                pal = {"name": cells[0], "posisi": cells[1] if len(cells) > 1 else "",
                       "bintang": cells[2] if len(cells) > 2 else "",
                       "catatan": cells[3] if len(cells) > 3 else ""}
                palaces.append(pal)

    # Indo translation map for palace names
    PALACE_INDO = {
        "命宮": "Kehidupan", "父母": "Orang Tua", "福德": "Kebajikan",
        "田宅": "Properti", "官祿": "Karir", "僕役": "Bawahan",
        "遷移": "Perpindahan", "疾厄": "Kesehatan", "財帛": "Kekayaan",
        "子女": "Anak", "夫妻": "Pasangan", "兄弟": "Saudara",
    }

    pal_html = ""
    for p in palaces[:12]:
        nm_m = re.match(r"^([一-鿿]+)\s*(.*)", p["name"])
        nm_hz = nm_m.group(1) if nm_m else p["name"]
        nm_indo = PALACE_INDO.get(nm_hz, nm_m.group(2).strip() if nm_m else "")
        is_self = nm_hz == "命宮"
        cls = "pal-card self" if is_self else "pal-card"

        pal_html += f"""<div class="{cls}">
  <div class="pal-pos">{md_inline(p['posisi'])}</div>
  <div class="pal-hz">{nm_hz}</div>
  <div class="pal-indo">{nm_indo}</div>
  <div class="pal-stars">{md_inline(p['bintang'])}</div>
  <div class="pal-note">{md_inline(p['catatan'])}</div>
</div>"""

    # Intro paragraph from MD
    intro = ""
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">") and not s.startswith("|") and not s.startswith("-"):
            intro = s; break

    # Try interpretasi (BAB 2 may not have one)
    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">12 Istana Kehidupan <span class="hz">十二宮</span></div>
<div class="zw-section-intro tight"><strong>Zi Wei Dou Shu</strong> memetakan hidup Anda ke <strong>12 istana</strong> — masing-masing mewakili satu aspek (diri, pasangan, anak, karir, dsb). Setiap istana dihuni bintang-bintang yang membentuk arketipe aspek tersebut. Istana <strong>命宮 (Kehidupan)</strong> adalah pusat — dari sini semua aspek lain bekerja.</div>

<div class="palace-grid">{pal_html}</div>"""

    return [page(page_num, "Peta 12 Istana Hidup", "紫微十二宮", "ZI WEI · 紫微", body, subject_name)], page_num + 1


def build_section_3(sec, subject_name, page_num):
    """BAB 3: Karakter & Kepribadian — new MD format with Indo labels."""
    lines = sec["lines"]

    # Parse Kekuatan + Kelemahan bullets
    kek = []; kel = []
    cur = None
    for line in lines:
        if "Kekuatan" in line and line.startswith("###"):
            cur = "kek"; continue
        if "Kelemahan" in line and line.startswith("###"):
            cur = "kel"; continue
        if line.startswith("###"):
            cur = None; continue
        if cur and re.match(r"^-\s+", line):
            (kek if cur == "kek" else kel).append(re.sub(r"^-\s+", "", line).strip())

    # Parse "**LABEL** — description" pattern
    def parse_t(b):
        m = re.match(r"^\*\*([^*]+)\*\*\s*[—–-]\s*(.+)$", b)
        if m: return (m.group(1).strip(), m.group(2).strip())
        return ("", b)

    kek_traits = [parse_t(b) for b in kek[:6]]
    kel_traits = [parse_t(b) for b in kel[:6]]

    def render_traits(traits, kind):
        out = ""
        for label, desc in traits:
            if label:
                out += f"""<div class="trait-card {kind}">
  <div class="trait-label">{md_inline(label)}</div>
  <div class="trait-text">{md_inline(desc)}</div>
</div>"""
            else:
                out += f"""<div class="trait-card {kind} no-hz">
  <div class="trait-text">{md_inline(desc)}</div>
</div>"""
        return out

    kek_html = render_traits(kek_traits, "kekuatan")
    kel_html = render_traits(kel_traits, "kelemahan")

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Kekuatan Utama <span class="hz">優勢</span></div>
<div class="zw-section-intro tight"><strong>Sifat-sifat positif</strong> yang menjadi modal utama Anda — dimaksimalkan dalam karir, hubungan, dan keputusan sehari-hari.</div>
<div class="trait-grid kek-grid grid-2">{kek_html}</div>

<div class="card-title compact">Kelemahan yang Perlu Diperhatikan <span class="hz">需注意</span></div>
<div class="zw-section-intro tight"><strong>Pola yang berisiko</strong> — bukan vonis permanen, melainkan kecenderungan untuk dikenali dan dikelola dengan kesadaran.</div>
<div class="trait-grid kel-grid grid-2">{kel_html}</div>"""

    return [page(page_num, "Karakter &amp; Kepribadian", "性 情", "KARAKTER · 性情", body, subject_name)], page_num + 1


def build_section_2_OLD(sec, subject_name, page_num):
    """OLD section 2 (Karakter) — preserved for reference, not used."""
    lines = sec["lines"]
    title = "Karakter &amp; Kepribadian"
    hz = "性 情"

    # Split into Kekuatan vs Kelemahan vs Rating
    blocks = {"kekuatan": [], "kelemahan": []}
    cur = None
    for line in lines:
        if "Kekuatan Karakter" in line:
            cur = "kekuatan"; continue
        if "Kelemahan" in line and "**" in line:
            cur = "kelemahan"; continue
        if line.startswith("###"):
            cur = None; continue
        if cur and re.match(r"^-\s+", line):
            blocks[cur].append(re.sub(r"^-\s+", "", line).strip())

    rating_rows = parse_rating_table(lines, "Rating Kepribadian")

    # Parse each bullet into (hanzi_label, indo_text)
    def parse_trait(bullet):
        # Pattern: **Hanzi** — text  OR  **Hanzi 拼音** — text
        m = re.match(r"^\*\*([一-鿿\s]+)\*\*\s*[—–-]\s*(.+)$", bullet)
        if m:
            return (m.group(1).strip(), m.group(2).strip())
        # Sometimes Hanzi appears mid-bullet: extract first Hanzi cluster as label, rest as text
        m2 = re.match(r"^([一-鿿]{2,})\s*[—–-]\s*(.+)$", bullet)
        if m2:
            return (m2.group(1).strip(), m2.group(2).strip())
        return ("", bullet)

    kek_traits = [parse_trait(b) for b in blocks['kekuatan'][:6]]
    kel_traits = [parse_trait(b) for b in blocks['kelemahan'][:4]]

    # Top 3 ratings highlight
    top3 = sorted(rating_rows, key=lambda r: -r[2])[:3] if rating_rows else []
    top_html = ""
    for id_lab, hz_lab, pct in top3:
        cls = "high" if pct >= 70 else ("mid" if pct >= 50 else "low")
        top_html += f"""<div class="char-top {cls}">
  <div class="char-top-pct">{pct}%</div>
  <div class="char-top-name"><div class="id">{id_lab}</div><div class="hz">{hz_lab}</div></div>
</div>"""

    # Kekuatan cards
    kek_html = ""
    for hzlab, indo in kek_traits:
        if hzlab:
            kek_html += f"""<div class="trait-card kekuatan">
  <div class="trait-hz">{hzlab}</div>
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""
        else:
            kek_html += f"""<div class="trait-card kekuatan no-hz">
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""

    # Kelemahan cards
    kel_html = ""
    for hzlab, indo in kel_traits:
        if hzlab:
            kel_html += f"""<div class="trait-card kelemahan">
  <div class="trait-hz">{hzlab}</div>
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""
        else:
            kel_html += f"""<div class="trait-card kelemahan no-hz">
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""

    body = f"""<div class="lead">Karakter Anda adalah lapisan utama yang membentuk semua keputusan hidup. Bagian ini meringkas <strong>kekuatan inti</strong> untuk dimaksimalkan dan <strong>kelemahan</strong> yang perlu dikenali.</div>

<div class="char-top-row">{top_html}</div>

<div class="char-block">
  <div class="char-block-head fav">
    <div class="bd-ico">✦</div>
    <div class="bd-titles">
      <div class="bd-id">Kekuatan Karakter</div>
      <div class="bd-hz">性格優勢</div>
    </div>
    <div class="bd-cnt">{len(kek_traits)} Sifat</div>
  </div>
  <div class="trait-grid kek-grid">{kek_html}</div>
</div>

<div class="char-block">
  <div class="char-block-head unfav">
    <div class="bd-ico">⚠</div>
    <div class="bd-titles">
      <div class="bd-id">Sisi yang Perlu Diwaspadai</div>
      <div class="bd-hz">需注意之處</div>
    </div>
    <div class="bd-cnt">{len(kel_traits)} Catatan</div>
  </div>
  <div class="trait-grid kel-grid">{kel_html}</div>
</div>

<div class="char-block">
  <div class="char-block-head neutral">
    <div class="bd-ico">◆</div>
    <div class="bd-titles">
      <div class="bd-id">Rating Kepribadian</div>
      <div class="bd-hz">人格評分</div>
    </div>
    <div class="bd-cnt">{len(rating_rows)} Aspek</div>
  </div>
  <div class="char-rating">{render_rating_bars(rating_rows)}</div>
</div>"""
    return [page(page_num, title, hz, "KARAKTER · 性情", body, subject_name)], page_num + 1


# === SHARED PALACE BUILDER (sec 3, 6, 7, 9, 11, 12, 13, 14, 14) ===

# Star arketipe definitions (universal — sama untuk siapapun)
STAR_DEFS = {
    "天相": ("Bintang Perdana Menteri", "Tiānxiàng", "Diplomatis, suka menengahi konflik, halus, suka damai. Pemerataan, keadilan, dan harmoni adalah temanya."),
    "天府": ("Bintang Sandang Pangan", "Tiānfǔ", "Penjamin kebutuhan hidup, stabilitas, akumulasi. Konservatif dalam keuangan, suka rumah yang teratur."),
    "武曲": ("Bintang Logam Keras", "Wǔqū", "Tegas, disiplin, pekerja keras. Cocok di bidang keuangan, militer, atau profesi yang butuh ketegasan."),
    "破軍": ("Bintang Pelopor Perubahan", "Pòjūn", "Dinamis, suka tantangan, suka menghancurkan untuk membangun ulang. Pemberontak yang konstruktif."),
    "巨門": ("Bintang Mulut Besar", "Jùmén", "Komunikasi kuat, debat, hukum. Bisa karismatik atau tukang kritik tergantung dukungan bintang lain."),
    "貪狼": ("Bintang Keinginan", "Tānláng", "Daya tarik tinggi, sosial, suka pengalaman baru. Rawan godaan dan kelebihan keinginan."),
    "太陰": ("Bintang Bulan", "Tàiyīn", "Feminin, sentimentil, intuitif. Kekayaan tersembunyi, suka rumah dan keluarga."),
    "太陽": ("Bintang Matahari", "Tàiyáng", "Terang, terbuka, otoritas yang jelas. Suka memimpin dan menjadi pusat perhatian."),
    "天機": ("Bintang Kecerdikan", "Tiānjī", "Analitis, fleksibel, cepat berpindah pikiran. Cocok di bidang yang butuh strategi."),
    "天梁": ("Bintang Pohon Cemara", "Tiānliáng", "Bijak, panjang umur, suka mengayomi. Cocok di bidang konsultasi, pendidikan, atau spiritual."),
    "七殺": ("Bintang Tujuh Pembunuh", "Qīshā", "Berani, tegas, suka tindakan langsung. Pejuang dan eksekutor yang efektif."),
    "紫微": ("Bintang Kaisar", "Zǐwēi", "Kepemimpinan natural, kehormatan, mulia. Membawa otoritas dan rasa tanggung jawab."),
    "廉貞": ("Bintang Disiplin Moral", "Liánzhēn", "Penegak hukum dan moral, pengendalian diri. Bisa kaku atau adil tergantung dukungan."),
}


def build_palace_section(sec, subject_name, page_num):
    """Visual palace page: hero star + grouped trait cards."""
    lines = sec["lines"]
    title = sec["title"]
    m = re.match(r"^(.+?)\s*\(([一-鿿·\s]+)\)\s*$", title)
    id_t = m.group(1).strip() if m else title
    hz_t = m.group(2).strip() if m else ""

    # Map section title to header label
    SECTION_LABELS = {
        3: "ISTANA NASIB · 命宮",
        6: "ASMARA · 夫妻宮",
        7: "ANAK-ANAK · 子女宮",
        9: "MIGRASI · 遷移宮",
        11: "ORANG TUA · 父母宮",
        12: "BAWAHAN · 僕役宮",
        13: "KEBERUNTUNGAN · 福德宮",
        14: "NASIB AKHIR · 宿命",
    }
    label = SECTION_LABELS.get(sec["num"], "ZI WEI · 紫微")

    # Find main star
    main_star = find_main_star(lines)
    star_hz = ""; star_py = ""; star_arketipe = ""; star_def = ""
    if main_star:
        m2 = re.match(r"^([一-鿿]+)星?\s*\(?([A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+)?\)?\s*[—–-]?\s*(.*)", main_star)
        if m2:
            star_hz = m2.group(1)
            star_py = m2.group(2) or ""
            star_arketipe = m2.group(3).strip()
        # Lookup universal def
        if star_hz in STAR_DEFS:
            d = STAR_DEFS[star_hz]
            if not star_arketipe:
                star_arketipe = d[0]
            if not star_py:
                star_py = d[1]
            star_def = d[2]

    # Compact star strip
    hero_html = _palace_hero_html(star_hz, star_py, star_arketipe, star_def)

    # Group bullets: positive (no ⚠), category-prefix (**X:**), warnings (⚠)
    positives = []
    categories = []
    warnings = []
    for line in lines:
        m_b = re.match(r"^-\s+(.+)", line)
        if not m_b: continue
        b = m_b.group(1).strip()
        if "⚠" in b:
            warnings.append(re.sub(r"⚠️?\s*", "", b))
        elif re.match(r"^\*\*[^*]+:\*\*", b):
            categories.append(b)
        else:
            positives.append(b)

    # Parse trait cards (Hanzi + indo) for positives and warnings
    def parse_t(b):
        m = re.match(r"^\*\*([一-鿿\s]+)\*\*\s*[—–-]\s*(.+)$", b)
        if m: return (m.group(1).strip(), m.group(2).strip())
        m2 = re.match(r"^([一-鿿]{3,})\s*[—–-]\s*(.+)$", b)
        if m2: return (m2.group(1).strip(), m2.group(2).strip())
        return ("", b)

    def render_traits(traits, kind):
        out = ""
        for hzlab, indo in traits:
            if hzlab:
                out += f"""<div class="trait-card {kind}">
  <div class="trait-hz">{hzlab}</div>
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""
            else:
                out += f"""<div class="trait-card {kind} no-hz">
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""
        return out

    pos_traits = [parse_t(b) for b in positives[:8]]
    warn_traits = [parse_t(b) for b in warnings[:5]]

    pos_html = render_traits(pos_traits, "kekuatan") if pos_traits else ""
    warn_html = render_traits(warn_traits, "kelemahan") if warn_traits else ""

    # Categories rendered as compact callouts
    cat_html = ""
    for c in categories[:4]:
        cm = re.match(r"^\*\*([^*]+):\*\*\s*(.+)$", c)
        if cm:
            cat_html += f"""<div class="palace-cat">
  <div class="pc-tag">{cm.group(1).strip()}</div>
  <div class="pc-text">{md_inline(cm.group(2).strip())}</div>
</div>"""

    callouts = build_callouts_from_quotes(lines)

    pos_block = ""
    if pos_html:
        pos_block = f"""<div class="char-block">
  <div class="char-block-head fav">
    <div class="bd-ico">✦</div>
    <div class="bd-titles"><div class="bd-id">Gambaran Inti</div><div class="bd-hz">主要特徵</div></div>
    <div class="bd-cnt">{len(pos_traits)} Sifat</div>
  </div>
  <div class="trait-grid kek-grid">{pos_html}</div>
</div>"""

    warn_block = ""
    if warn_html:
        warn_block = f"""<div class="char-block">
  <div class="char-block-head unfav">
    <div class="bd-ico">⚠</div>
    <div class="bd-titles"><div class="bd-id">Yang Harus Diwaspadai</div><div class="bd-hz">需注意</div></div>
    <div class="bd-cnt">{len(warn_traits)} Catatan</div>
  </div>
  <div class="trait-grid kel-grid">{warn_html}</div>
</div>"""

    cat_block = ""
    if cat_html:
        cat_block = f"""<div class="char-block">
  <div class="char-block-head neutral">
    <div class="bd-ico">◆</div>
    <div class="bd-titles"><div class="bd-id">Variasi Khusus</div><div class="bd-hz">特殊情況</div></div>
    <div class="bd-cnt">{len(categories[:4])} Catatan</div>
  </div>
  <div class="palace-cat-grid">{cat_html}</div>
</div>"""

    body = f"""{hero_html}
{pos_block}
{warn_block}
{cat_block}
{''.join(callouts[:2])}"""

    return [page(page_num, id_t, hz_t, label, body, subject_name)], page_num + 1


# === SECTION 4 - KEKAYAAN ===

def _palace_hero_html(star_hz, star_py, star_arketipe, star_def):
    """Removed — no hero block at top. Star info still shown in trait blocks below."""
    return ""


def _star_lookup(main_star_str):
    """Parse main star string + lookup universal definition."""
    if not main_star_str:
        return ("", "", "", "")
    m = re.match(r"^([一-鿿]+)星?\s*\(?([A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+)?\)?\s*[—–-]?\s*(.*)", main_star_str)
    star_hz = m.group(1) if m else ""
    star_py = (m.group(2) or "") if m else ""
    star_arketipe = m.group(3).strip() if m else ""
    star_def = ""
    if star_hz in STAR_DEFS:
        d = STAR_DEFS[star_hz]
        if not star_arketipe: star_arketipe = d[0]
        if not star_py: star_py = d[1]
        star_def = d[2]
    return (star_hz, star_py, star_arketipe, star_def)


def build_section_4(sec, subject_name, page_num):
    """BAB 4: Karir & Jabatan — new MD format."""
    lines = sec["lines"]

    # Parse blocks: **Kelompok N — Title:** or **Jabatan Spesifik...:** followed by paragraph
    groups = []
    cur_title = None; cur_text = []
    for line in lines:
        m = re.match(r"^\*\*([^*]+):\*\*\s*$", line.strip())
        if m:
            if cur_title:
                groups.append({"title": cur_title, "text": " ".join(cur_text).strip()})
            cur_title = m.group(1).strip(); cur_text = []
        elif cur_title is not None:
            s = line.strip()
            if s and not s.startswith("#") and not s.startswith(">"):
                cur_text.append(s)
            elif s.startswith(">") or s.startswith("#"):
                if cur_title:
                    groups.append({"title": cur_title, "text": " ".join(cur_text).strip()})
                    cur_title = None; cur_text = []
    if cur_title:
        groups.append({"title": cur_title, "text": " ".join(cur_text).strip()})

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    # Render group cards with profession chips
    GROUP_COLORS = ["green", "gold", "red"]  # cycle through accent colors
    group_html = ""
    for i, g in enumerate(groups):
        color = GROUP_COLORS[i % len(GROUP_COLORS)]
        # Split title to main + subtitle
        title = g["title"]
        # Format examples: "Kelompok 1 — Seni, Pendidikan & Budaya" or "Jabatan Spesifik (dari analisis 官祿)"
        tm = re.match(r"^(Kelompok\s+\d+|Jabatan\s+\w+|.+?)\s*[—–]?\s*(.*)$", title)
        title_main = tm.group(1).strip() if tm else title
        title_sub = tm.group(2).strip() if tm else ""

        # Chips from comma-separated professions
        items = [p.strip().rstrip(".") for p in re.split(r"[,，;]", g["text"]) if p.strip()]
        chips_html = "".join(f'<span class="prof-chip">{md_inline(it)}</span>' for it in items)

        group_html += f"""<div class="prof-card prof-{color}">
  <div class="prof-head">
    <div class="prof-num">{i + 1:02d}</div>
    <div class="prof-titles">
      <div class="prof-main">{md_inline(title_main)}</div>
      <div class="prof-sub">{md_inline(title_sub) if title_sub else ''}</div>
    </div>
    <div class="prof-cnt">{len(items)} bidang</div>
  </div>
  <div class="prof-chips">{chips_html}</div>
</div>"""

    body = f"""{interp_html}

<div class="card-title compact">Bidang Karir yang Cocok <span class="hz">事業適合</span></div>
<div class="zw-section-intro tight">Berdasarkan analisis bagan, berikut <strong>kelompok bidang &amp; jabatan</strong> yang paling selaras dengan elemen bawaan dan bintang penguasa Anda. Lebih cocok dipilih sebagai <strong>karir utama</strong> atau pivot karir.</div>

<div class="prof-stack">{group_html}</div>"""

    return [page(page_num, "Karir &amp; Jabatan", "事 業 · 官 祿", "KARIR · 事業", body, subject_name)], page_num + 1


def build_section_5(sec, subject_name, page_num):
    """BAB 5: Keuangan & Kekayaan — new MD format."""
    lines = sec["lines"]

    # Parse Sumber Harta table (3 cols: Jenis, Kondisi, Saran)
    wealth = []
    in_t = False
    for line in lines:
        if "Sumber Harta" in line:
            in_t = True; continue
        if in_t and line.startswith("###"):
            in_t = False; continue
        if in_t and line.strip().startswith(">"):
            in_t = False
        if in_t and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0] and "Jenis" not in cells[0]:
                wealth.append({"jenis": cells[0], "kondisi": cells[1], "saran": cells[2]})

    # Parse Potensi bullets
    pot_bullets = []
    in_p = False
    for line in lines:
        if "Potensi Besar" in line and line.startswith("###"):
            in_p = True; continue
        if in_p and line.startswith("###"):
            in_p = False; continue
        if in_p and line.strip().startswith(">"):
            in_p = False
        if in_p and re.match(r"^-\s+", line):
            pot_bullets.append(re.sub(r"^-\s+", "", line).strip())

    # Render wealth cards
    WEALTH_ICONS = {"正財": "🏛", "偏財": "💰"}
    wealth_html = ""
    for w in wealth[:2]:
        # jenis: "**正財 Harta Tetap** (gaji, investasi)"
        jenis_clean = re.sub(r"\*\*", "", w["jenis"])
        hz_m = re.search(r"([一-鿿]+)", jenis_clean)
        hz = hz_m.group(1) if hz_m else ""
        # Indo name after Hanzi
        rest = re.sub(r"^[一-鿿]+\s*", "", jenis_clean).strip()
        # Split parenthetical
        paren_m = re.match(r"^([^(]+?)\s*\(([^)]+)\)\s*$", rest)
        indo_name = paren_m.group(1).strip() if paren_m else rest
        sumber = paren_m.group(2).strip() if paren_m else ""
        icon = WEALTH_ICONS.get(hz, "💼")
        is_zheng = "正" in hz
        sumber_inline = f' <span class="wc-sumber">({md_inline(sumber)})</span>' if sumber else ''
        wealth_html += f"""<div class="wealth-card {'zheng' if is_zheng else 'pian'}">
  <div class="wc-top"><span class="wc-icon">{icon}</span> <span class="wc-hz">{hz}</span></div>
  <div class="wc-indo">{md_inline(indo_name)}{sumber_inline}</div>
  <div class="wc-divider"></div>
  <div class="wc-row"><span class="wc-k">Kondisi</span><span class="wc-v">{md_inline(w['kondisi'])}</span></div>
  <div class="wc-row hl"><span class="wc-k">Saran</span><span class="wc-v">{md_inline(w['saran'])}</span></div>
</div>"""

    # Split potensi into positive (good) and warning (⚠)
    pot_pos = []; pot_warn = []
    for b in pot_bullets:
        if "⚠" in b:
            pot_warn.append(re.sub(r"⚠️?\s*", "", b))
        else:
            pot_pos.append(b)

    # Render each potensi item as separate box (1-bar card)
    pot_pos_html = "".join(f'<div class="pot-item fav">{md_inline(b)}</div>' for b in pot_pos)
    pot_warn_html = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in pot_warn) or '<div class="pot-item neutral">Tidak ada peringatan khusus.</div>'

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Sumber Kekayaan <span class="hz">財源分析</span></div>
<div class="zw-section-intro tight">Dalam Ba Zi, kekayaan dibagi 2 jenis: <strong>正財</strong> (Harta Tetap — gaji, investasi reguler) dan <strong>偏財</strong> (Harta Sampingan — komisi, spekulasi, peluang dadakan). Bagan Anda menunjukkan kondisi masing-masing &amp; saran pengelolaannya.</div>
<div class="wealth-grid">{wealth_html}</div>

<div class="card-title compact">Potensi Istana Kekayaan <span class="hz">財帛宮潛能</span></div>
<div class="zw-section-intro tight"><strong>Istana Kekayaan (財帛宮)</strong> di Zi Wei menentukan potensi maksimum kekayaan. Bintang utama yang menghuni istana ini menentukan apakah Anda bisa kaya raya, stabil, atau perlu hati-hati.</div>

<div class="potensi-grid">
  <div class="potensi-block fav">
    <div class="potensi-head"><span class="ico">✦</span> Faktor Pendukung</div>
    <div class="pot-stack">{pot_pos_html}</div>
  </div>
  <div class="potensi-block unfav">
    <div class="potensi-head"><span class="ico">⚠</span> Yang Diwaspadai</div>
    <div class="pot-stack">{pot_warn_html}</div>
  </div>
</div>"""

    return [page(page_num, "Keuangan &amp; Kekayaan", "財 富 · 財 帛", "KEKAYAAN · 財帛", body, subject_name)], page_num + 1


def build_section_6(sec, subject_name, page_num):
    """BAB 6: Pernikahan & Pasangan."""
    lines = sec["lines"]

    # Intro paragraph (Dinamika Hubungan)
    dinamika = []
    in_d = False
    for line in lines:
        if "Dinamika Hubungan" in line and line.startswith("###"):
            in_d = True; continue
        if in_d and line.startswith("###"):
            in_d = False; continue
        if in_d and line.strip().startswith(">"):
            in_d = False
        if in_d:
            s = line.strip()
            if s and not s.startswith("|") and not s.startswith("-"):
                dinamika.append(s)
    dinamika_html = " ".join(dinamika)

    # Kecocokan Shio table
    shios = []
    in_t = False
    for line in lines:
        if "Kecocokan Shio" in line and line.startswith("###"):
            in_t = True; continue
        if in_t and line.startswith("###"):
            in_t = False; continue
        if in_t and line.strip().startswith(">"):
            in_t = False
        if in_t and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0] and "Shio" not in cells[0]:
                shios.append({"name": cells[0], "level": cells[1], "ket": cells[2]})

    # Render shio compatibility cards
    SHIO_EMOJI = {"鼠":"🐭","牛":"🐂","虎":"🐯","兔":"🐰","龍":"🐉","蛇":"🐍","馬":"🐴","羊":"🐑","猴":"🐒","雞":"🐓","狗":"🐕","豬":"🐷"}
    SHIO_INDO = {"鼠":"Tikus","牛":"Kerbau","虎":"Harimau","兔":"Kelinci","龍":"Naga","蛇":"Ular","馬":"Kuda","羊":"Kambing","猴":"Monyet","雞":"Ayam","狗":"Anjing","豬":"Babi"}
    shio_html = ""
    for s in shios:
        # Parse star count from level e.g. "★★★★★ Sangat Baik"
        stars_count = s["level"].count("★")
        # Extract Hanzi from name e.g. "馬 Kuda"
        hz_m = re.search(r"([一-鿿])", s["name"])
        hz = hz_m.group(1) if hz_m else ""
        emoji = SHIO_EMOJI.get(hz, "·")
        indo = SHIO_INDO.get(hz, re.sub(r"^[一-鿿]+\s*", "", s["name"]))
        # Skip "Shio lain" rows
        if "Shio lain" in s["name"]:
            indo = "Shio Lain"
            emoji = "•"
        # Determine class
        if stars_count >= 5: cls = "best"
        elif stars_count >= 4: cls = "good"
        elif stars_count >= 3: cls = "ok"
        else: cls = "weak"
        # Level label cleaned
        level_clean = re.sub(r"[★☆]+\s*", "", s["level"]).strip()
        shio_html += f"""<div class="shio-row {cls}">
  <div class="shio-emoji">{emoji}</div>
  <div class="shio-name"><span class="hz">{hz}</span> <span class="id">{indo}</span></div>
  <div class="shio-stars">{'★' * stars_count}{'☆' * (5 - stars_count)}</div>
  <div class="shio-level">{level_clean}</div>
  <div class="shio-ket">{md_inline(s['ket'])}</div>
</div>"""

    # Peringatan bullets
    perings = []
    in_p = False
    for line in lines:
        if "Peringatan" in line and line.startswith("###"):
            in_p = True; continue
        if in_p and line.startswith("###"):
            in_p = False; continue
        if in_p and line.strip().startswith(">"):
            in_p = False
        if in_p and re.match(r"^-\s+", line):
            perings.append(re.sub(r"^-\s+", "", line).strip())

    pering_html = "".join(f'<div class="pot-item unfav">{md_inline(p)}</div>' for p in perings)

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Dinamika Hubungan <span class="hz">夫妻動態</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(dinamika_html)}</p></div></div>

<div class="card-title compact">Kecocokan Shio Pasangan <span class="hz">婚配</span></div>
<div class="zw-section-intro tight">Tabel ini menunjukkan tingkat <strong>kecocokan shio Anda dengan calon/pasangan</strong>. Bintang lebih banyak = energi lebih harmonis. <strong>Hindari</strong> pasangan dengan rating rendah karena rawan konflik berkelanjutan.</div>
<div class="shio-compat-stack">{shio_html}</div>

<div class="card-title compact">Peringatan Penting <span class="hz">注意</span></div>
<div class="pot-stack">{pering_html}</div>"""

    return [page(page_num, "Pernikahan &amp; Pasangan", "夫 妻 · 婚 配", "PERNIKAHAN · 夫妻", body, subject_name)], page_num + 1


def build_section_7(sec, subject_name, page_num):
    """BAB 7: Anak & Keturunan."""
    lines = sec["lines"]

    # Intro paragraph + bullets
    intro = ""
    bullets = []
    saran = ""
    in_q = False; cur_q = []
    for line in lines:
        s = line.strip()
        if s.startswith(">"):
            cur_q.append(re.sub(r"^>\s*\*\*[^*]+:\*\*\s*", "", s.lstrip(">").strip()))
            in_q = True
        elif in_q and not s.startswith(">"):
            saran = " ".join(cur_q).strip()
            in_q = False; cur_q = []
        if re.match(r"^-\s+", line):
            bullets.append(re.sub(r"^-\s+", "", line).strip())
        elif s and not s.startswith("#") and not s.startswith(">") and not s.startswith("-") and not intro:
            intro = s

    if cur_q and not saran:
        saran = " ".join(cur_q).strip()

    bul_html = "".join(f'<div class="li">{md_inline(b)}</div>' for b in bullets)

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    # Saran callout (from > **Saran:** ...)
    saran_html = ""
    if saran:
        saran_html = f'<div class="callout tip"><div class="ico">💡</div><div><strong>Saran:</strong> {md_inline(saran)}</div></div>'

    body = f"""{interp_html}

<div class="card-title compact">Gambaran Anak-Anak Anda <span class="hz">子女</span></div>
<div class="zw-section-intro tight">{md_inline(intro)}</div>

<div class="card thin">
  <div class="card-title">Karakter &amp; Bakat Anak</div>
  <div class="card-body"><div class="list-bul green">{bul_html}</div></div>
</div>

{saran_html}"""

    return [page(page_num, "Anak &amp; Keturunan", "子 女", "ANAK · 子女", body, subject_name)], page_num + 1


def build_section_8(sec, subject_name, page_num):
    """BAB 8: Kesehatan — area perlu diperhatikan."""
    lines = sec["lines"]

    # Intro paragraph
    intro = ""
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">") and not s.startswith("|") and not s.startswith("-"):
            intro = s; break

    # Parse "Area yang Perlu Diperhatikan" table (3 cols: Area, Risiko, Tingkat Perhatian)
    areas = []
    in_t = False
    for line in lines:
        if "Area yang Perlu Diperhatikan" in line:
            in_t = True; continue
        if in_t and line.startswith("###"):
            in_t = False; continue
        if in_t and line.strip().startswith(">"):
            in_t = False
        if in_t and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0] and "Area" not in cells[0]:
                areas.append({"area": cells[0], "risiko": cells[1], "tingkat": cells[2]})

    # Render area cards (1 column with bar accent)
    AREA_ICONS = {
        "Mata": "👁", "Sendi": "🦴", "Saraf": "⚡", "Jantung": "❤", "Perut": "🍽",
    }
    area_html = ""
    for a in areas:
        # Determine severity from "Tingkat Perhatian" → cls
        tingkat = a["tingkat"].lower()
        if "perlu cek" in tingkat or "tinggi" in tingkat:
            cls = "unfav"; tag = "Perlu Cek"
        elif "sedang" in tingkat:
            cls = "neutral"; tag = "Sedang"
        else:
            cls = "fav"; tag = re.sub(r"⚠️?\s*", "", a["tingkat"]).strip()
        # Pick icon
        icon = "·"
        for k, v in AREA_ICONS.items():
            if k in a["area"]:
                icon = v; break
        area_html += f"""<div class="health-card {cls}">
  <div class="hc-icon">{icon}</div>
  <div class="hc-body">
    <div class="hc-area">{md_inline(a['area'])}</div>
    <div class="hc-risiko">{md_inline(a['risiko'])}</div>
  </div>
  <div class="hc-tag">{tag}</div>
</div>"""

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Gambaran Umum Kesehatan <span class="hz">健康概況</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(intro)}</p></div></div>

<div class="card-title compact">Area yang Perlu Diperhatikan <span class="hz">注意之處</span></div>
<div class="zw-section-tight tight"></div>
<div class="health-stack">{area_html}</div>"""

    return [page(page_num, "Kesehatan", "疾 厄", "KESEHATAN · 疾厄", body, subject_name)], page_num + 1


def build_section_9(sec, subject_name, page_num):
    """BAB 9: Orang Tua."""
    lines = sec["lines"]

    intro = ""
    bullets = []
    for line in lines:
        s = line.strip()
        if re.match(r"^-\s+", line):
            bullets.append(re.sub(r"^-\s+", "", line).strip())
        elif s and not s.startswith("#") and not s.startswith(">") and not s.startswith("-") and not intro:
            intro = s

    # Split bullets: warning (with ⚠) vs general
    pos = []; warn = []
    for b in bullets:
        if "⚠" in b:
            warn.append(re.sub(r"⚠️?\s*", "", b))
        else:
            pos.append(b)

    pos_html = "".join(f'<div class="pot-item fav">{md_inline(b)}</div>' for b in pos)
    warn_html = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in warn)

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Gambaran Orang Tua <span class="hz">父母</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(intro)}</p></div></div>

{pot_block_pair(pos, warn, "Karakteristik Hubungan", "Yang Diwaspadai")}"""

    return [page(page_num, "Orang Tua", "父 母", "ORANG TUA · 父母", body, subject_name)], page_num + 1


def build_section_10(sec, subject_name, page_num):
    """BAB 10: Bawahan & Rekan."""
    lines = sec["lines"]

    intro = ""
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">") and not s.startswith("|") and not s.startswith("-"):
            intro = s; break

    # Parse table (Kondisi | Hasil)
    rows = []
    in_t = False
    for line in lines:
        if line.startswith("|") and "Kondisi" in line and "Hasil" in line:
            in_t = True; continue
        if in_t and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0]:
                rows.append({"kondisi": cells[0], "hasil": cells[1]})

    rows_html = ""
    for r in rows:
        # Tag positive/negative based on hasil text
        h = r["hasil"].lower()
        if "musuh" in h or "sulit" in h or "tidak" in h:
            cls = "unfav"
        else:
            cls = "fav"
        rows_html += f"""<div class="bawahan-card {cls}">
  <div class="bw-kondisi">{md_inline(r['kondisi'])}</div>
  <div class="bw-arrow">→</div>
  <div class="bw-hasil">{md_inline(r['hasil'])}</div>
</div>"""

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Gambaran Bawahan &amp; Rekan <span class="hz">僕役</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(intro)}</p></div></div>

<div class="card-title compact">Variasi Kondisi <span class="hz">情況變化</span></div>
<div class="zw-section-intro tight">Tergantung pada <strong>posisi istana</strong> dan <strong>bintang seistana</strong>, kualitas hubungan dengan bawahan/rekan bisa berbeda-beda. Berikut variasinya.</div>
<div class="bawahan-stack">{rows_html}</div>"""

    return [page(page_num, "Bawahan &amp; Rekan", "僕 役", "BAWAHAN · 僕役", body, subject_name)], page_num + 1


# Direction abbreviations (Indo) → (Hanzi, Indo-short)
DIR_MAP = {
    "Utara": ("北", "U", "n"),     "Selatan": ("南", "S", "s"),
    "Timur": ("東", "T", "e"),     "Barat": ("西", "B", "w"),
    "Timur Laut": ("東北", "TL", "ne"), "Tenggara": ("東南", "TG", "se"),
    "Barat Laut": ("西北", "BL", "nw"), "Barat Daya": ("西南", "BD", "sw"),
}

# Bagua trigrams per direction (Pre-Heaven order)
DIR_GUA = {
    "Utara":     ("☵", "坎", "Kǎn", "Air"),
    "Timur Laut":("☶", "艮", "Gèn", "Gunung"),
    "Timur":     ("☳", "震", "Zhèn", "Petir"),
    "Tenggara":  ("☴", "巽", "Xùn", "Angin"),
    "Selatan":   ("☲", "離", "Lí", "Api"),
    "Barat Daya":("☷", "坤", "Kūn", "Bumi"),
    "Barat":     ("☱", "兌", "Duì", "Danau"),
    "Barat Laut":("☰", "乾", "Qián", "Langit"),
}

# Eight Mansions: East Group (East 4) vs West Group (West 4)
EAST_GROUP_TRIGRAMS = {"坎", "離", "震", "巽"}  # N, S, E, SE — favored axes
WEST_GROUP_TRIGRAMS = {"乾", "坤", "艮", "兌"}  # NW, SW, NE, W

EAST_GROUP_DIRS = ["Utara", "Selatan", "Timur", "Tenggara"]
WEST_GROUP_DIRS = ["Barat Laut", "Barat Daya", "Timur Laut", "Barat"]


def extract_dirs_from_text(text):
    """Extract direction names from a text. Returns list of (Indo_full, hz, abbr)."""
    found = []
    for indo in sorted(DIR_MAP.keys(), key=lambda x: -len(x)):  # longer first
        if indo in text:
            hz, ab, _ = DIR_MAP[indo]
            found.append((indo, hz, ab))
            text = text.replace(indo, "")  # avoid duplicate match
    return found


def build_fengshui_block(lines, intro_text=""):
    """Build adaptive Feng Shui compass + zones block (V4.5 style)."""
    # 1. Detect user's trigram from intro_text or section text
    full_text = intro_text + "\n" + "\n".join(lines)
    user_gua_hz = ""; user_gua_indo = ""; user_gua_py = ""; user_gua_glyph = ""; user_gua_dir = ""
    # Try patterns: "Trigram 坎卦", "坎卦 (Air/Utara)"
    gua_m = re.search(r"Trigram\s+([一-鿿])卦", full_text) or re.search(r"([坎艮震巽離坤兌乾])卦", full_text)
    if gua_m:
        user_gua_hz = gua_m.group(1)
        for d, info in DIR_GUA.items():
            if info[1] == user_gua_hz:
                user_gua_glyph = info[0]; user_gua_indo = info[3]; user_gua_py = info[2]; user_gua_dir = d
                break
    # Default fallback to 坎 (water)
    if not user_gua_hz:
        user_gua_hz = "坎"; user_gua_glyph = "☵"; user_gua_indo = "Air"; user_gua_py = "Kǎn"; user_gua_dir = "Utara"

    is_east_group = user_gua_hz in EAST_GROUP_TRIGRAMS
    favored_dirs = EAST_GROUP_DIRS if is_east_group else WEST_GROUP_DIRS
    avoided_dirs = WEST_GROUP_DIRS if is_east_group else EAST_GROUP_DIRS
    group_label = "Kelompok Timur" if is_east_group else "Kelompok Barat"

    # 2. Parse Feng Shui table from MD: aspek → directions
    fs_rows = []
    in_fs = False
    for line in lines:
        if "Feng Shui" in line and line.startswith("###"):
            in_fs = True; continue
        if in_fs and line.startswith("###"):
            in_fs = False; continue
        if in_fs and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and "Aspek" not in cells[0]:
                fs_rows.append({"aspek": cells[0], "rec": cells[1]})

    # 3. Map aspek to zone (Hanzi + key)
    ZONE_MAP = [
        ("Arah Rumah", "宅", "Arah Rumah", "Zhái", False),
        ("Pintu", "門", "Pintu Utama", "Mén", False),
        ("Kompor", "灶", "Dapur/Kompor", "Zào", False),
        ("Dapur", "灶", "Dapur/Kompor", "Zào", False),
        ("Kamar Tidur", "房", "Kamar Tidur", "Fáng", False),
        ("Tempat Tidur", "床", "Ranjang", "Chuáng", False),
        ("Altar", "神", "Altar", "Shén", False),
        ("Kamar Mandi", "廁", "Kamar Mandi", "Cè", True),  # warn
        ("WC", "廁", "Kamar Mandi", "Cè", True),
    ]

    seen_zones = set()
    zones_html = ""
    for f in fs_rows:
        # Match aspek to zone
        zone_hz = ""; zone_id = ""; zone_py = ""; is_warn = False
        for needle, hz, label, py, warn in ZONE_MAP:
            if needle in f["aspek"]:
                zone_hz, zone_id, zone_py, is_warn = hz, label, py, warn
                break
        if not zone_hz: continue
        if zone_hz in seen_zones: continue
        seen_zones.add(zone_hz)
        # Extract directions from rec
        dirs = extract_dirs_from_text(f["rec"])
        if not dirs: continue
        pills_html = "".join(
            f'<span class="yz-pill {"bad" if is_warn else ""}"><span class="hz">{hz}</span>{ab}</span>'
            for indo, hz, ab in dirs
        )
        head_label = "⚠ Arah Penekan" if is_warn else "✓ Arah Optimal"
        zones_html += f"""<div class="yz-zone {'warn' if is_warn else ''}">
  <div class="yz-zone-label">
    <div class="yz-zone-hz">{zone_hz}</div>
    <div class="yz-zone-id">{zone_id}</div>
    <div class="yz-zone-pinyin">{zone_py}</div>
  </div>
  <div class="yz-zone-dirs">
    <div class="yz-zone-headline">{head_label}</div>
    <div class="yz-dir-pills">{pills_html}</div>
  </div>
</div>"""

    # 4. Build compass SVG with user's gua highlighted
    DIR_COORDS = {
        "Utara":     (200, 55,  "n"),  "Timur Laut":(302.5, 97.5, "ne"),
        "Timur":     (345, 200, "e"),  "Tenggara":  (302.5, 302.5, "se"),
        "Selatan":   (200, 345, "s"),  "Barat Daya":(97.5, 302.5, "sw"),
        "Barat":     (55, 200,  "w"),  "Barat Laut":(97.5, 97.5,  "nw"),
    }
    DIR_SHORT_INDO = {
        "Utara":"U", "Timur Laut":"TL", "Timur":"T", "Tenggara":"TG",
        "Selatan":"S", "Barat Daya":"BD", "Barat":"B", "Barat Laut":"BL",
    }
    badges_svg = ""
    for d, (cx, cy, code) in DIR_COORDS.items():
        glyph, hz, py, indo = DIR_GUA[d]
        is_user = (d == user_gua_dir)
        is_fav = d in favored_dirs and not is_user
        if is_user:
            fill = "#FFF8E1"; stroke = "#8B1A1A"; sw = "2"; tx_fill = "#8B1A1A"
            extra = f'<text x="{cx}" y="{cy + 45}" text-anchor="middle" font-size="6" fill="#8B1A1A" font-weight="700" letter-spacing="1">★ TRIGRAM ANDA ★</text>'
        elif is_fav:
            fill = "#E8F0EA"; stroke = "#2D6A4F"; sw = "1.2"; tx_fill = "#2D6A4F"
            extra = ""
        else:
            fill = "#FFFEF8"; stroke = "#D8C896"; sw = "0.6"; tx_fill = "#2C2416"
            extra = ""
        sub_indo = DIR_SHORT_INDO[d]
        badges_svg += f"""
  <g>
    <circle cx="{cx}" cy="{cy}" r="{36 if is_user else 30}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>
    <text x="{cx}" y="{cy - (10 if is_user else 7)}" text-anchor="middle" font-size="{15 if is_user else 13}" fill="{tx_fill}">{glyph}</text>
    <text x="{cx}" y="{cy + (6 if is_user else 7)}" text-anchor="middle" font-size="{14 if is_user else 13}" fill="{tx_fill}" font-weight="700" font-family="Noto Serif TC, serif">{hz}</text>
    <text x="{cx}" y="{cy + (19 if is_user else 19)}" text-anchor="middle" font-size="6" fill="{tx_fill}" font-style="italic">{sub_indo} · {py} · {indo}</text>
    {extra}
  </g>"""

    compass_svg = f"""<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <circle cx="200" cy="200" r="186" fill="none" stroke="#E5D3A1" stroke-width="0.6"/>
  <circle cx="200" cy="200" r="178" fill="#FFFEF8" stroke="#C9A961" stroke-width="0.4"/>
  <circle cx="200" cy="200" r="118" fill="none" stroke="#E5D3A1" stroke-width="0.4" stroke-dasharray="2,3"/>
  <line x1="200" y1="22" x2="200" y2="378" stroke="#E5D3A1" stroke-width="0.3" stroke-dasharray="2,3"/>
  <line x1="22" y1="200" x2="378" y2="200" stroke="#E5D3A1" stroke-width="0.3" stroke-dasharray="2,3"/>
  {badges_svg}
  <g>
    <circle cx="200" cy="200" r="32" fill="#FFFEF8" stroke="#C9A961" stroke-width="1.2"/>
    <path d="M 184 208 L 200 192 L 216 208 L 216 218 L 184 218 Z" fill="none" stroke="#8B1A1A" stroke-width="1.2" stroke-linejoin="round"/>
    <rect x="195" y="211" width="6" height="7" fill="#8B1A1A"/>
    <text x="200" y="232" text-anchor="middle" font-size="7" fill="#6B5B3F" font-style="italic" letter-spacing="1">RUMAH</text>
  </g>
  <text x="376" y="32" text-anchor="end" font-size="6" fill="#C9A961" font-weight="600" letter-spacing="1.5">UTARA · U</text>
</svg>"""

    return f"""<div class="yz-hero">
  <div class="yz-compass-frame">{compass_svg}</div>
  <div class="yz-gua-panel">
    <div class="yz-gua-eyebrow">本 命 卦 · Trigram Pribadi</div>
    <div class="yz-trigram">{user_gua_glyph}</div>
    <div class="yz-gua-name">{user_gua_hz}</div>
    <div class="yz-gua-pinyin">{user_gua_py} — "{user_gua_indo}"</div>
    <div class="yz-gua-meaning">
      Anda termasuk <strong>{group_label}</strong>. Arah favorit: {', '.join(favored_dirs)}.
    </div>
    <div class="yz-gua-axis">
      <span>Sumbu hoki:</span> arah utama selaras dengan trigram <span class="hz">{user_gua_hz}</span>.
    </div>
  </div>
</div>

<div class="yz-zones-frame">
  <div class="yz-zones-eyebrow">
    <div>
      <span class="label">六 大 方 位</span>
      <span class="id">Penempatan Optimal Hunian</span>
    </div>
    <div class="meta">{user_gua_hz}卦 · {group_label.upper()}</div>
  </div>
  <div class="yz-zones-grid">{zones_html}</div>
  <div class="yz-legend">
    <span><strong>U</strong>=Utara</span>
    <span><strong>TL</strong>=Timur Laut</span>
    <span><strong>T</strong>=Timur</span>
    <span><strong>TG</strong>=Tenggara</span>
    <span><strong>S</strong>=Selatan</span>
    <span><strong>BD</strong>=Barat Daya</span>
    <span><strong>B</strong>=Barat</span>
    <span><strong>BL</strong>=Barat Laut</span>
  </div>
</div>"""


def build_section_11(sec, subject_name, page_num):
    """BAB 11: Properti & Rumah + Feng Shui."""
    lines = sec["lines"]

    intro = ""
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">") and not s.startswith("|") and not s.startswith("-"):
            intro = s; break

    # Parse properti bullets
    pro_bullets = []
    in_b = False
    for line in lines:
        s = line.strip()
        if line.startswith("###") and "Feng Shui" not in line:
            in_b = False
        if line.startswith("###") and "Feng Shui" in line:
            in_b = False
        if re.match(r"^-\s+", line):
            pro_bullets.append(re.sub(r"^-\s+", "", line).strip())

    # Split positive vs warning (broader keyword detection)
    WARN_KEYS = ["⚠", "sulit", "tidak bisa", "habis", "rawan", "kerugian", "hati-hati"]
    pos = []; warn = []
    for b in pro_bullets:
        bl = b.lower()
        if any(k in bl for k in WARN_KEYS):
            warn.append(re.sub(r"⚠️?\s*", "", b))
        else:
            pos.append(b)

    pos_html = "".join(f'<div class="pot-item fav">{md_inline(b)}</div>' for b in pos)
    warn_html = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in warn)

    # Feng Shui table (Aspek | Rekomendasi)
    fs_rows = []
    in_fs = False
    for line in lines:
        if "Feng Shui" in line and line.startswith("###"):
            in_fs = True; continue
        if in_fs and line.startswith("###"):
            in_fs = False; continue
        if in_fs and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and "Aspek" not in cells[0]:
                fs_rows.append({"aspek": cells[0], "rec": cells[1]})

    FS_ICONS = {"Arah Rumah":"🏠","Altar":"🕯","Pintu":"🚪","Kompor":"🔥","Kamar Tidur":"🛏","Tempat Tidur":"🛌","Kamar Mandi":"🚽"}
    fs_html = ""
    for f in fs_rows:
        icon = "·"
        for k, v in FS_ICONS.items():
            if k in f["aspek"]:
                icon = v; break
        fs_html += f"""<div class="fs-card">
  <div class="fs-icon">{icon}</div>
  <div class="fs-body">
    <div class="fs-aspek">{md_inline(f['aspek'])}</div>
    <div class="fs-rec">{md_inline(f['rec'])}</div>
  </div>
</div>"""

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Potensi Istana Properti <span class="hz">田宅宮</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(intro)}</p></div></div>

{pot_block_pair(pos, warn)}

<div class="card-title compact">Feng Shui Rumah <span class="hz">陽宅</span></div>
<div class="zw-section-intro tight"><strong>Trigram 坎卦 (Air/Utara)</strong> — tata letak yang selaras dengan elemen bawaan Anda untuk membawa keberuntungan.</div>
<div class="fs-grid">{fs_html}</div>"""

    return [page(page_num, "Properti &amp; Feng Shui", "田 宅 · 陽 宅", "PROPERTI · 田宅", body, subject_name)], page_num + 1


def build_section_12(sec, subject_name, page_num):
    """BAB 12: Perpindahan & Mobilitas."""
    lines = sec["lines"]

    intro = ""
    bullets = []
    for line in lines:
        s = line.strip()
        if re.match(r"^-\s+", line):
            bullets.append(re.sub(r"^-\s+", "", line).strip())
        elif s and not s.startswith("#") and not s.startswith(">") and not s.startswith("-") and not intro:
            intro = s

    # Detect warning sentences in intro (split on "namun", "ironisnya", "tapi")
    intro_warn = ""
    intro_pos = intro
    split_m = re.search(r"(.+?)(?:\s*[—,—]\s*|\s+)(namun|ironisnya|tapi)\s+(.+)", intro, re.IGNORECASE)
    if split_m:
        intro_pos = split_m.group(1).strip().rstrip(",").rstrip("—").strip()
        intro_warn = split_m.group(3).strip()

    WARN_KEYS = ["⚠", "sulit", "tidak bisa", "habis", "rawan", "kerugian", "hati-hati", "terhambat", "berhenti"]
    pos = []; warn = []
    for b in bullets:
        bl = b.lower()
        if any(k in bl for k in WARN_KEYS):
            warn.append(re.sub(r"⚠️?\s*", "", b))
        else:
            pos.append(b)
    if intro_warn:
        warn.insert(0, intro_warn)
        intro = intro_pos

    pos_html = "".join(f'<div class="pot-item fav">{md_inline(b)}</div>' for b in pos)
    warn_html = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in warn)

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Gambaran Mobilitas Hidup <span class="hz">遷移宮</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(intro)}</p></div></div>

{pot_block_pair(pos, warn)}"""

    return [page(page_num, "Perpindahan &amp; Mobilitas", "遷 移", "PERPINDAHAN · 遷移", body, subject_name)], page_num + 1


def build_section_13(sec, subject_name, page_num):
    """BAB 13: Peruntungan & Kebajikan."""
    lines = sec["lines"]

    intro = ""
    bullets = []
    for line in lines:
        s = line.strip()
        if re.match(r"^-\s+", line):
            bullets.append(re.sub(r"^-\s+", "", line).strip())
        elif s and not s.startswith("#") and not s.startswith(">") and not s.startswith("-") and not intro:
            intro = s

    pos = []; warn = []
    for b in bullets:
        if "⚠" in b or "sulit" in b.lower() or "破軍" in b:
            warn.append(re.sub(r"⚠️?\s*", "", b))
        else:
            pos.append(b)

    pos_html = "".join(f'<div class="pot-item fav">{md_inline(b)}</div>' for b in pos)
    warn_html = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in warn)

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Gambaran Kebajikan &amp; Keberuntungan Batin <span class="hz">福德宮</span></div>
<div class="card thin"><div class="card-body"><p>{md_inline(intro)}</p></div></div>

{pot_block_pair(pos, warn, "Yang Membawa Keberuntungan", "Yang Mengganggu")}"""

    return [page(page_num, "Peruntungan &amp; Kebajikan", "福 德", "KEBERUNTUNGAN · 福德", body, subject_name)], page_num + 1


def build_section_14(sec, subject_name, page_num):
    """BAB 14: Bintang Khusus."""
    lines = sec["lines"]

    # Parse table (Bintang | Nama | Pengaruh)
    rows = []
    in_t = False
    for line in lines:
        if "|" in line and "Bintang" in line and "Pengaruh" in line:
            in_t = True; continue
        if in_t and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0]:
                rows.append({"bintang": cells[0], "nama": cells[1], "pengaruh": cells[2]})

    star_html = ""
    for r in rows:
        # Extract Hanzi from bintang field e.g. "**驛馬 Yi Ma**"
        bintang_clean = re.sub(r"\*\*", "", r["bintang"])
        hz_m = re.search(r"([一-鿿]+)", bintang_clean)
        hz = hz_m.group(1) if hz_m else ""
        py = re.sub(r"^[一-鿿]+\s*", "", bintang_clean).strip()
        # Determine warning
        is_warn = "⚠" in r["nama"] or "⚠" in r["pengaruh"] or "ujian" in r["pengaruh"].lower() or "boros" in r["pengaruh"].lower()
        cls = "unfav" if is_warn else "neutral"
        star_html += f"""<div class="star-card {cls}">
  <div class="star-hz">{hz}</div>
  <div class="star-info">
    <div class="star-py">{py}</div>
    <div class="star-nama">{md_inline(r['nama'])}</div>
    <div class="star-pengaruh">{md_inline(r['pengaruh'])}</div>
  </div>
</div>"""

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}

<div class="card-title compact">Tanda Bintang Khusus <span class="hz">神煞</span></div>
<div class="zw-section-intro tight"><strong>神煞 (Shen Sha)</strong> adalah bintang khusus yang memberi <strong>warna unik</strong> pada bagan. Beberapa membantu, beberapa harus diwaspadai. Mereka tidak menentukan nasib, tapi memberi <strong>aksen</strong> pada perjalanan hidup.</div>
<div class="star-stack">{star_html}</div>"""

    return [page(page_num, "Bintang Khusus", "神 煞", "BINTANG KHUSUS · 神煞", body, subject_name)], page_num + 1


def build_section_15(sec, subject_name, page_num):
    """BAB 15: Takdir & Nasib Dasar — Ringkasan Karakter + Kutipan Kitab Kuno."""
    lines = sec["lines"]

    # Parse 6 bullet points: "- HZ → **Indo translation**"
    bullets = []
    in_b = False
    for line in lines:
        if "Ringkasan Karakter" in line and line.startswith("###"):
            in_b = True; continue
        if in_b and line.startswith("###"):
            in_b = False; continue
        if in_b and re.match(r"^-\s+", line):
            bullets.append(re.sub(r"^-\s+", "", line).strip())

    # Each bullet has format "Hanzi text → **Indo translation**"
    def parse_bullet(b):
        m = re.match(r"^(.+?)\s*→\s*\*\*(.+?)\*\*\s*$", b)
        if m:
            return (m.group(1).strip(), m.group(2).strip())
        return ("", b)

    items = [parse_bullet(b) for b in bullets]
    items_html = ""
    for i, (hz, indo) in enumerate(items, 1):
        # Determine if positive or negative based on Indo text
        indo_lower = indo.lower()
        is_neg = any(k in indo_lower for k in ["kurang", "sulit", "tidak", "terbatas", "cerewet", "tidak menyelesaikan"])
        cls = "unfav" if is_neg else "fav"
        items_html += f"""<div class="takdir-card {cls}">
  <div class="td-num">{i:02d}</div>
  <div class="td-body">
    <div class="td-hz">{hz}</div>
    <div class="td-indo">{md_inline(indo)}</div>
  </div>
</div>"""

    # Parse Kutipan Kitab Kuno
    kutipan_hz = ""; kutipan_indo = ""
    in_k = False
    for line in lines:
        if "Kutipan" in line or "古書云" in line:
            in_k = True; continue
        if in_k:
            s = line.strip()
            # Italic quote
            if s.startswith("*\"") or s.startswith('*"'):
                kutipan_hz = re.sub(r"^\*[\"']|[\"']\*$", "", s).strip()
            elif s.startswith(">"):
                kutipan_indo = s.lstrip(">").strip()
                in_k = False

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    kutipan_html = ""
    if kutipan_hz or kutipan_indo:
        kutipan_html = f"""<div class="card-title compact">Kutipan Kitab Kuno <span class="hz">古書云</span></div>
<div class="syair-card">
  <div class="src"><span class="hz">三命通會</span> San Ming Tong Hui</div>
  <div class="verse">{kutipan_hz}</div>
  <div class="trans">"{md_inline(kutipan_indo)}"</div>
</div>"""

    body = f"""{interp_html}

<div class="card-title compact">Ringkasan Karakter dari Software <span class="hz">宿命總論</span></div>
<div class="zw-section-intro tight">Software Xing Yi memberikan <strong>{len(items)} poin distilasi</strong> dari seluruh bagan — pernyataan langsung yang merangkum karakter inti. Beberapa positif, beberapa harus disadari.</div>
<div class="takdir-stack">{items_html}</div>

{kutipan_html}"""

    return [page(page_num, "Takdir &amp; Nasib Dasar", "宿 命 · 總 論", "TAKDIR · 宿命", body, subject_name)], page_num + 1


def build_section_16(sec, subject_name, page_num):
    """BAB 16: Ramalan Tahunan 2026-2031."""
    lines = sec["lines"]
    text = "\n".join(lines)

    # Split per year. Pattern: ### ★★★★☆ 2026 — Usia 64 Tahun | 歲次丙午
    year_blocks = []
    cur = None
    for line in lines:
        m = re.match(r"^###\s+(★+☆*)\s+(\d{4})\s+—\s+(.+)", line)
        if m:
            if cur:
                year_blocks.append(cur)
            stars = m.group(1).count("★")
            cur = {"year": int(m.group(2)), "stars": stars, "header": m.group(3).strip(), "lines": []}
        elif cur is not None:
            if line.startswith("##"):
                year_blocks.append(cur); cur = None
            else:
                cur["lines"].append(line)
    if cur:
        year_blocks.append(cur)

    def render_year_card(yb):
        # Extract age + 歲次 from header
        age_m = re.search(r"Usia\s+(\d+)", yb["header"])
        age = age_m.group(1) if age_m else ""
        gan_m = re.search(r"歲次\s*([一-鿿]+)", yb["header"])
        gan = gan_m.group(1) if gan_m else ""

        # Bintang aktif
        bintang_m = re.search(r"\*\*Bintang Aktif:\*\*\s*(.+)", "\n".join(yb["lines"]))
        bintang = bintang_m.group(1).strip() if bintang_m else ""

        # Karakter tahun
        karakter_m = re.search(r"\*\*Karakter Tahun Ini:\*\*\s*(.+?)(?=\n>|\n\n|$)", "\n".join(yb["lines"]), re.DOTALL)
        karakter = karakter_m.group(1).strip() if karakter_m else ""

        # Ringkasan blockquote
        ringkasan = ""
        for line in yb["lines"]:
            s = line.strip()
            if s.startswith(">") and "Ringkasan" in s:
                ringkasan = re.sub(r"^>\s*\*\*Ringkasan:\*\*\s*", "", s.lstrip(">").strip())
                break

        # Kondisi Umum bullets (for compact display)
        kondisi = []
        in_k = False
        for line in yb["lines"]:
            if "Kondisi Umum:" in line: in_k = True; continue
            if "Detail Bintang:" in line or "Karakter Tahun" in line: in_k = False
            if in_k and re.match(r"^-\s+", line):
                kondisi.append(re.sub(r"^-\s+", "", line).strip())

        stars = yb["stars"]
        if stars >= 4: cls = "good"
        elif stars >= 3: cls = "ok"
        else: cls = "weak"
        star_html = "★" * stars + "☆" * (5 - stars)

        kondisi_html = "".join(f'<div class="li">{md_inline(b)}</div>' for b in kondisi[:3])

        return f"""<div class="year-card {cls}">
  <div class="yc-head">
    <div class="yc-year">{yb['year']}</div>
    <div class="yc-meta">
      <div class="yc-stars">{star_html}</div>
      <div class="yc-age">Usia {age} · <span class="hz">歲次 {gan}</span></div>
    </div>
  </div>
  <div class="yc-body">
    <div class="yc-bintang"><span class="lbl">Bintang Aktif</span> {md_inline(bintang)}</div>
    <div class="list-bul">{kondisi_html}</div>
    {f'<div class="yc-karakter"><strong>Karakter:</strong> {md_inline(karakter)}</div>' if karakter else ''}
    {f'<div class="yc-ringkasan">💡 <strong>Ringkasan:</strong> {md_inline(ringkasan)}</div>' if ringkasan else ''}
  </div>
</div>"""

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    # Page 1: 2026-2028 (first 3 years)
    cards1 = "".join(render_year_card(yb) for yb in year_blocks[:3])
    body1 = f"""{interp_html}

<div class="card-title compact">Ramalan Tahunan 2026 – 2028 <span class="hz">流年判斷</span></div>
<div class="zw-section-intro tight"><strong>流年 (Liu Nian)</strong> = ramalan per tahun. Setiap tahun bagan Anda berinteraksi dengan energi tahun tersebut (歲次), menghasilkan corak peruntungan unik. <strong>Bintang Aktif</strong> memberi tema tahunnya.</div>
<div class="year-stack">{cards1}</div>"""

    # Page 2: 2029-2031 + summary bar chart
    cards2 = "".join(render_year_card(yb) for yb in year_blocks[3:6])
    summary_rows = ""
    for yb in year_blocks:
        stars = yb["stars"]
        pct = stars * 20  # 5★ = 100%
        if stars >= 4: cls = "high"
        elif stars >= 3: cls = "mid"
        else: cls = "low"
        summary_rows += f"""<div class="bar-row">
  <div class="bar-label"><div class="id">Tahun {yb['year']}</div><div class="hz">{stars}★ Rating</div></div>
  <div class="bar-track"><div class="bar-fill {cls}" style="width: {pct}%"></div></div>
  <div class="bar-pct">{pct}%</div>
</div>"""

    body2 = f"""<div class="card-title compact">Ramalan Tahunan 2029 – 2031 <span class="hz">流年判斷</span></div>
<div class="year-stack">{cards2}</div>"""

    body3 = f"""<div class="card-title compact">Ringkasan 6 Tahun ke Depan <span class="hz">總覽</span></div>
<div class="zw-section-intro tight"><strong>Visual ringkasan</strong> rating peruntungan 6 tahun ke depan. Tahun dengan bar lebih panjang = peruntungan lebih baik. Pakai untuk merencanakan keputusan besar (pindah, ekspansi, investasi) di tahun-tahun favorable.</div>
<div class="card thin"><div class="card-body">{summary_rows}</div></div>"""

    return [
        page(page_num, "Ramalan Tahunan 2026 – 2028", "流 年 判 斷", "RAMALAN TAHUNAN · 流年", body1, subject_name),
        page(page_num + 1, "Ramalan Tahunan 2029 – 2031", "流 年 判 斷", "RAMALAN TAHUNAN · 流年", body2, subject_name),
        page(page_num + 2, "Ringkasan 6 Tahun ke Depan", "流 年 總 覽", "RAMALAN TAHUNAN · 流年", body3, subject_name),
    ], page_num + 3


# Indonesian translations for Ten God terms (universal lookup)
TENGOD_INDO = {
    "比肩": "Rekan Setara", "劫財": "Perampas Rezeki",
    "食神": "Dewa Makanan", "傷官": "Pejabat Terluka",
    "偏財": "Harta Sampingan", "正財": "Harta Tetap",
    "七殺": "Tujuh Pembunuh", "正官": "Pejabat Resmi",
    "偏印": "Cetakan Tidak Langsung", "正印": "Cetakan Resmi",
    "貪神": "Dewa Keinginan",
}
# 12-fase lifecycle translations
LIFEFASE_INDO = {
    "長生": "Kelahiran Panjang", "沐浴": "Pemandian", "冠帶": "Pemahkotaan",
    "臨官": "Mendekati Jabatan", "帝旺": "Puncak Kaisar", "衰": "Pelemahan",
    "病": "Sakit", "死": "Kematian", "墓": "Pemakaman",
    "絕": "Pemutusan", "胎": "Pembuahan", "養": "Pemeliharaan",
}


def translate_hanzi_cell(text, lookup):
    """Translate Hanzi terms in cell using lookup. Returns formatted Hanzi + Indo."""
    if not text or text == "—":
        return "—"
    # Try exact match first
    for hz in sorted(lookup.keys(), key=lambda x: -len(x)):
        if hz in text:
            indo = lookup[hz]
            # Render: <span class="hz">HZ</span> Indo
            text = text.replace(hz, f'<span class="hz">{hz}</span><br><span class="indo-sub">{indo}</span>', 1)
            return text
    return f'<span class="hz">{text}</span>'


# Year highlights derived from Lifecycle phase + Ten God combo (universal mapping)
LIFEFASE_MOOD = {
    "長生": ("growth", "Fase Tumbuh — energi baru bermunculan, awal yang segar."),
    "沐浴": ("flux", "Fase Pembersihan — emosi naik-turun, periode adaptasi."),
    "冠帶": ("rise", "Fase Persiapan — bersiap mengambil tanggung jawab besar."),
    "臨官": ("rise", "Fase Mendekati Puncak — promosi, otoritas bertambah."),
    "帝旺": ("peak", "Fase Puncak — energi maksimum, hasilkan sebanyak mungkin."),
    "衰": ("decline", "Fase Pelemahan — mulai kurangi beban, jaga energi."),
    "病": ("decline", "Fase Sakit — rentan, perhatikan kesehatan & emosi."),
    "死": ("decline", "Fase Akhir — tutup bab lama, refleksi mendalam."),
    "墓": ("rest", "Fase Pemakaman — istirahat, akumulasi diam-diam."),
    "絕": ("rest", "Fase Pemutusan — transisi, lepas yang tidak perlu."),
    "胎": ("seed", "Fase Pembuahan — gagasan baru mulai tumbuh diam-diam."),
    "養": ("seed", "Fase Pemeliharaan — rawat yang sudah dibangun."),
}


def build_tabel_siklus_besar(parsed, subject_name, page_num):
    """Tabel Siklus Besar — beginner-friendly, focus dekade aktif + simple year cards."""
    epi = parsed.get("epilogue", "")
    lines = epi.split("\n")

    # Auto-compute current age from subject birth year + today
    subject = parsed.get("subject", {})
    tahun_lahir = subject.get("Tahun Lahir (Masehi)", "")
    today_year = int(time.strftime("%Y")) if "time" in dir() else 2026
    try:
        import datetime as _dt
        today_year = _dt.date.today().year
    except Exception:
        pass
    try:
        birth_year = int(tahun_lahir)
        cur_age = today_year - birth_year
    except Exception:
        cur_age = 0

    # Parse dekades — adaptive to multiple heading patterns
    dekades = []
    cur = None
    DEKADE_PAT = re.compile(r"^(?:###|####)\s+(?:Siklus|Periode|Dekade|Cycle)\s*(\d+)\s*[–\-]\s*(\d+)\s*[:\(]?\s*(.+?)?\s*\)?\s*$", re.IGNORECASE)
    for line in lines:
        m = DEKADE_PAT.match(line)
        if m:
            if cur: dekades.append(cur)
            cur = {"start": int(m.group(1)), "title": (m.group(3) or "").strip().rstrip(")").strip(), "rows": []}
        elif cur is not None:
            if line.startswith("##") or (re.match(r"^###?\s+", line) and not DEKADE_PAT.match(line) and ("Periode" not in line and "Siklus" not in line)):
                dekades.append(cur); cur = None
            elif "|" in line and "---" not in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 5 and cells[0] and "Usia" not in cells[0] and not re.match(r"^[\-\=]+$", cells[0]):
                    # Pad to 6 cells if needed
                    while len(cells) < 6: cells.append("—")
                    cur["rows"].append(cells)
    if cur: dekades.append(cur)

    # Graceful fallback when no dekades found
    if not dekades:
        body = """<div class="card-title compact">Siklus Besar Hidup Anda <span class="hz">大運</span></div>
<div class="zw-section-intro tight">Data siklus besar tidak tersedia di sumber MD. Halaman ini akan terisi otomatis bila MD memiliki section berisi tabel periode 10-tahunan.</div>"""
        return page(page_num, "Siklus Besar Hidup Anda", "大 運", "SIKLUS BESAR · 大運", body, subject_name)

    # Find active dekade
    active_dk = None
    other_dks = []
    for d in dekades:
        if d["start"] <= cur_age < d["start"] + 10:
            active_dk = d
        else:
            other_dks.append(d)

    if not active_dk and dekades:
        active_dk = dekades[-1]
        other_dks = dekades[:-1]

    # Parse dekade title for theme
    # Format: "偏印 庚申 (Cetakan Tidak Langsung)" → main_hz=偏印, indo=Cetakan Tidak Langsung
    dk_theme_hz = ""; dk_theme_indo = ""; dk_pilar = ""
    if active_dk:
        tm = re.match(r"^([一-鿿]+)\s+([一-鿿]+)\s*\(([^)]+)\)", active_dk["title"])
        if tm:
            dk_theme_hz = tm.group(1)
            dk_pilar = tm.group(2)
            dk_theme_indo = tm.group(3)

    # Render active dekade as year cards
    year_cards_html = ""
    if active_dk:
        for r in active_dk["rows"]:
            usia = int(r[0]) if r[0].isdigit() else 0
            is_now = (usia == cur_age)
            # Translate Ten God
            tg_hz = re.sub(r"<[^>]+>", "", r[2]).strip()  # strip any html
            tg_first = re.match(r"^([一-鿿]+)", tg_hz)
            tg_indo = TENGOD_INDO.get(tg_first.group(1) if tg_first else tg_hz, tg_hz)
            # Translate Lifecycle
            ph_first = re.match(r"^([一-鿿]+)", r[3].strip())
            ph_hz = ph_first.group(1) if ph_first else r[3]
            ph_mood, ph_desc = LIFEFASE_MOOD.get(ph_hz, ("", LIFEFASE_INDO.get(ph_hz, ph_hz)))
            ph_indo = LIFEFASE_INDO.get(ph_hz, ph_hz)
            # Bintang tahunan (just hanzi, no translation needed for now)
            cls = "now" if is_now else ph_mood
            now_tag = '<div class="yr-now-tag">TAHUN INI</div>' if is_now else ""
            year_cards_html += f"""<div class="yr-card {cls}">
  {now_tag}
  <div class="yr-age">{usia}<span class="yr-th">th</span></div>
  <div class="yr-pilar"><span class="hz">{r[1]}</span></div>
  <div class="yr-tg">{tg_indo}</div>
  <div class="yr-phase"><span class="phase-hz">{ph_hz}</span> {ph_indo}</div>
  <div class="yr-desc">{ph_desc}</div>
</div>"""

    # Other dekades — labeled per relative position (sebelumnya / berikutnya)
    other_html = ""
    sebelum_dks = [d for d in other_dks if d["start"] + 9 < cur_age]
    sesudah_dks = [d for d in other_dks if d["start"] > cur_age + 9]
    for d in sorted(sebelum_dks, key=lambda x: -x["start"])[:1]:  # latest sebelumnya
        tm = re.match(r"^([一-鿿]+)\s+([一-鿿]+)\s*\(([^)]+)\)", d["title"])
        theme = tm.group(3) if tm else d["title"]
        other_html += f"""<div class="other-dk past">
  <div class="od-tag">⟵ Sebelumnya</div>
  <div class="od-range">Usia {d['start']}–{d['start']+9}</div>
  <div class="od-theme">{theme}</div>
</div>"""
    for d in sorted(sesudah_dks, key=lambda x: x["start"])[:1]:  # nearest sesudah
        tm = re.match(r"^([一-鿿]+)\s+([一-鿿]+)\s*\(([^)]+)\)", d["title"])
        theme = tm.group(3) if tm else d["title"]
        other_html += f"""<div class="other-dk future">
  <div class="od-tag">Berikutnya ⟶</div>
  <div class="od-range">Usia {d['start']}–{d['start']+9}</div>
  <div class="od-theme">{theme}</div>
</div>"""

    body = f"""<div class="card-title compact">Siklus Besar Hidup Anda <span class="hz">大運</span></div>
<div class="zw-section-intro tight">Hidup Anda terbagi menjadi <strong>periode 10-tahunan</strong> bernama <strong>大運 (Da Yun)</strong>. Setiap dekade punya "iklim energi" sendiri — beberapa periode lebih beruntung, beberapa lebih menantang. Halaman ini fokus ke <strong>dekade aktif Anda saat ini</strong>.</div>

<div class="dk-active-hero">
  <div class="dah-tag">DEKADE AKTIF SAAT INI</div>
  <div class="dah-range">Usia {active_dk['start']}–{active_dk['start']+9}</div>
  <div class="dah-theme">
    <span class="dah-hz">{dk_theme_hz}</span>
    <span class="dah-indo">{dk_theme_indo}</span>
  </div>
  <div class="dah-pilar">Pilar Penguasa: <span class="hz">{dk_pilar}</span></div>
</div>

<div class="card-title compact">Detail per Tahun (Dekade Aktif)</div>
<div class="zw-section-intro tight">Setiap tahun dalam dekade aktif punya <strong>fase hidup berbeda</strong> (12 fase siklus). Tahun dengan fase "Puncak" = energi maksimum, "Sakit/Akhir" = waktu istirahat, "Pembuahan/Tumbuh" = saatnya mulai hal baru. <strong>Tahun ini Anda</strong> ditandai khusus.</div>
<div class="yr-grid">{year_cards_html}</div>

{f'''<div class="card-title compact">Konteks Dekade Lain <span class="hz">前後大運</span></div>
<div class="zw-section-intro tight">Sebagai konteks — dekade <strong>sebelumnya</strong> (yang baru selesai Anda lewati) dan <strong>berikutnya</strong> (yang akan datang). Tema setiap dekade memengaruhi peruntungan keseluruhan periode itu.</div>
<div class="other-dk-stack">{other_html}</div>''' if other_html else ''}"""

    return page(page_num, "Siklus Besar Hidup Anda", "大 運", "SIKLUS BESAR · 大運", body, subject_name)


def build_kesimpulan(parsed, subject_name, page_num):
    """Kesimpulan Keseluruhan — Profil Singkat sebagai standalone visual page."""
    epi = parsed.get("epilogue", "")
    lines = epi.split("\n")

    # Profil paragraph
    profil = ""
    in_p = False
    for line in lines:
        if "Profil Singkat" in line:
            in_p = True; continue
        if in_p and line.startswith("###"):
            in_p = False; continue
        if in_p:
            s = line.strip()
            if s and not s.startswith("|"):
                profil += " " + s

    # Subject identity
    subject = parsed.get("subject", {})
    shio = subject.get("Shio", "")
    shio_id = ""
    for k in SHIO_MAP:
        if k in shio:
            shio_id = k; break

    hari_lahir_raw = subject.get("Hari Lahir", "")
    hari_lahir_clean = re.sub(r"^[一-鿿\s—–-]+", "", hari_lahir_raw)
    nama_safe = html.escape(subject.get("Nama", ""))
    body = f"""<div class="kes-hero">
  <div class="kes-eyebrow">Kesimpulan Keseluruhan</div>
  <div class="kes-title">命 · Inti Bagan Anda</div>
  <div class="kes-subtitle">Distilasi seluruh laporan dalam satu pernyataan</div>
</div>

<div class="kes-card">
  <div class="kes-seal">命</div>
  <div class="kes-text">{md_inline(profil.strip())}</div>
</div>

<div class="kes-tag-row">
  <div class="kes-tag-item"><span class="kt-lbl">Nama</span><span class="kt-val">{nama_safe}</span></div>
  <div class="kes-tag-item"><span class="kt-lbl">Shio</span><span class="kt-val">{shio_id or shio}</span></div>
  <div class="kes-tag-item"><span class="kt-lbl">Hari Lahir</span><span class="kt-val">{hari_lahir_clean}</span></div>
</div>

<div class="kes-cta">
  <div class="kes-cta-text">
    <strong>Halaman berikutnya</strong> berisi saran praktis konkret untuk Anda terapkan — di bidang karir, keuangan, kesehatan, hubungan, rumah, dan timing 6 tahun ke depan.
  </div>
  <div class="kes-cta-arrow">→</div>
</div>"""

    return page(page_num, "Kesimpulan Keseluruhan", "綜 合 結 論", "KESIMPULAN · 結論", body, subject_name)


def build_profil_saran(parsed, subject_name, page_num):
    """Profil Singkat + Saran Praktis dari epilogue."""
    epi = parsed.get("epilogue", "")
    lines = epi.split("\n")

    profil = ""
    in_p = False
    for line in lines:
        if "Profil Singkat" in line:
            in_p = True; continue
        if in_p and line.startswith("###"):
            in_p = False; continue
        if in_p:
            s = line.strip()
            if s and not s.startswith("|"):
                profil += " " + s

    saran_rows = []
    in_s = False
    for line in lines:
        if "Saran Berdasarkan Analisis" in line:
            in_s = True; continue
        if in_s and line.startswith("###"):
            in_s = False; continue
        if in_s and line.startswith("---"):
            in_s = False
        if in_s and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and "Bidang" not in cells[0]:
                bidang = re.sub(r"\*\*", "", cells[0])
                saran_rows.append({"bidang": bidang, "saran": cells[1]})

    SARAN_ICONS = {"Karir":"💼","Keuangan":"💰","Kesehatan":"🏥","Hubungan":"❤","Rumah":"🏠","2026":"📅","2028":"⚠","2030":"🌱"}

    ambig = []
    in_a = False
    for line in lines:
        if "Catatan Karakter Ambigu" in line:
            in_a = True; continue
        if in_a and line.startswith("---"):
            in_a = False; continue
        if in_a and re.match(r"^\d+\.\s+", line):
            ambig.append(re.sub(r"^\d+\.\s+", "", line).strip())

    ambig_html = ""
    if ambig:
        items = "".join(f'<div class="pot-item unfav">{md_inline(a)}</div>' for a in ambig)
        ambig_html = f"""<div class="card-title compact">Catatan Akurasi <span class="hz">注意</span></div>
<div class="potensi-block unfav full-w">
  <div class="potensi-head"><span class="ico">⚠</span> Karakter Ambigu di Foto Sumber</div>
  <div class="pot-stack">{items}</div>
</div>"""

    # Split saran into bidang (life areas) vs time (year periods)
    bidang_cards = []; time_cards = []
    for s in saran_rows:
        icon = "·"
        for k, v in SARAN_ICONS.items():
            if k in s["bidang"]: icon = v; break
        is_time = bool(re.match(r"^\d{4}", s["bidang"]))
        card = f"""<div class="saran-card {'time' if is_time else 'bidang'}">
  <div class="sr-icon">{icon}</div>
  <div class="sr-body">
    <div class="sr-bidang">{md_inline(s['bidang'])}</div>
    <div class="sr-saran">{md_inline(s['saran'])}</div>
  </div>
</div>"""
        (time_cards if is_time else bidang_cards).append(card)

    bidang_html = "".join(bidang_cards)
    time_html = "".join(time_cards)

    # Adaptive split: if too many saran items, split to 2 pages
    SPLIT_THRESHOLD = 6  # if total saran > 6, split
    pages_out = []

    if len(saran_rows) > SPLIT_THRESHOLD:
        # Page A: Profil + Saran Bidang Utama
        body_a = f"""<div class="card-title compact">Profil Singkat <span class="hz">綜合人格</span></div>
<div class="profil-card">
  <div class="profil-seal">{html.escape(subject_name[0]) if subject_name else '命'}</div>
  <div class="profil-text">{md_inline(profil.strip())}</div>
</div>

<div class="card-title compact">Saran Praktis — Bidang Hidup Utama <span class="hz">人生建議</span></div>
<div class="zw-section-intro tight">Distilasi <strong>seluruh laporan</strong> menjadi saran praktis untuk <strong>{len(bidang_cards)} bidang hidup utama</strong> — siap diterapkan sehari-hari.</div>
<div class="saran-grid">{bidang_html}</div>"""
        pages_out.append(page(page_num, "Profil &amp; Saran Bidang Hidup", "綜 合 人 格", "PROFIL · 人格", body_a, subject_name))

        # Page B: Saran Timing + Catatan
        body_b = f"""<div class="card-title compact">Saran Praktis — Timing 6 Tahun ke Depan <span class="hz">時運建議</span></div>
<div class="zw-section-intro tight"><strong>Timing matters</strong> — saran berdasarkan periode 2 tahunan untuk 6 tahun ke depan. Manfaatkan tahun yang baik, hati-hati di tahun sulit, ekspansi di tahun pemulihan.</div>
<div class="saran-grid">{time_html}</div>

{ambig_html}"""
        pages_out.append(page(page_num + 1, "Saran Timing &amp; Catatan Akurasi", "時 運 · 註 解", "RINGKASAN · 總評", body_b, subject_name))
    else:
        body = f"""<div class="card-title compact">Profil Singkat <span class="hz">綜合人格</span></div>
<div class="profil-card">
  <div class="profil-seal">{html.escape(subject_name[0]) if subject_name else '命'}</div>
  <div class="profil-text">{md_inline(profil.strip())}</div>
</div>

<div class="card-title compact">Saran Praktis Berdasarkan Analisis <span class="hz">建議</span></div>
<div class="zw-section-intro tight">Distilasi <strong>seluruh laporan</strong> menjadi {len(saran_rows)} saran praktis — siap diterapkan di kehidupan sehari-hari.</div>
<div class="saran-grid">{bidang_html}{time_html}</div>

{ambig_html}"""
        pages_out.append(page(page_num, "Ringkasan &amp; Saran Praktis", "綜 合 總 評", "RINGKASAN · 總評", body, subject_name))

    return pages_out


TOPIC_BUILDERS = {
    "bazi":             "build_section_1",
    "ziwei":            "build_section_2",
    "karakter":         "build_section_3",
    "karir":            "build_section_4",
    "keuangan":         "build_section_5",
    "pernikahan":       "build_section_6",
    "anak":             "build_section_7",
    "kesehatan":        "build_section_8",
    "orangtua":         "build_section_9",
    "bawahan":          "build_section_10",
    "properti":         "build_section_11",
    "fengshui":         "build_section_11",  # combined
    "perpindahan":      "build_section_12",
    "peruntungan":      "build_section_13",
    "shensha":          "build_section_14",
    "takdir":           "build_section_15",
    "tahunan":          "build_section_16",
    "siklus":           "build_section_siklus_inline",  # render inline as section
    "kecocokan_shio":   "build_kecocokan_shio_section",
    "saran_kesimpulan": "build_saran_inline",
    "catatan":          "build_catatan_inline",
}


def get_builder_for_topic(topic):
    """Return builder function from topic key. Falls back to generic."""
    name = TOPIC_BUILDERS.get(topic, None)
    if name and name in globals():
        return globals()[name]
    return build_generic_section


def build_section_siklus_inline(sec, subject_name, page_num):
    """Render BAB 'Tabel Limpasan' / 'Siklus Besar' as inline section."""
    # Wrap section data into mock "epilogue" format then call build_tabel_siklus_besar
    epi_text = "## TABEL SIKLUS BESAR DETAIL\n" + "\n".join(sec["lines"])
    fake_parsed = {"epilogue": epi_text, "subject": {}}
    p = build_tabel_siklus_besar(fake_parsed, subject_name, page_num)
    return [p], page_num + 1


def build_kecocokan_shio_section(sec, subject_name, page_num):
    """Standalone Kecocokan Shio page (when MD has it as own BAB)."""
    # Reuse logic from build_section_6 but only the shio compat table portion
    lines = sec["lines"]
    shios = []
    for line in lines:
        if "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0] and "Shio" not in cells[0] and not re.match(r"^[\-\=]+$", cells[0]):
                shios.append({"name": cells[0], "level": cells[1] if len(cells) > 1 else "", "ket": cells[2] if len(cells) > 2 else ""})

    SHIO_EMOJI = {"鼠":"🐭","牛":"🐂","虎":"🐯","兔":"🐰","龍":"🐉","蛇":"🐍","馬":"🐴","羊":"🐑","猴":"🐒","雞":"🐓","狗":"🐕","豬":"🐷"}
    SHIO_INDO = {"鼠":"Tikus","牛":"Kerbau","虎":"Harimau","兔":"Kelinci","龍":"Naga","蛇":"Ular","馬":"Kuda","羊":"Kambing","猴":"Monyet","雞":"Ayam","狗":"Anjing","豬":"Babi"}
    rows_html = ""
    for s in shios[:14]:
        stars_count = s["level"].count("★") if "★" in s["level"] else 0
        hz_m = re.search(r"([一-鿿])", s["name"])
        hz = hz_m.group(1) if hz_m else ""
        emoji = SHIO_EMOJI.get(hz, "·")
        indo = SHIO_INDO.get(hz, re.sub(r"^[一-鿿]+\s*", "", s["name"]))
        if stars_count >= 5: cls = "best"
        elif stars_count >= 4: cls = "good"
        elif stars_count >= 3: cls = "ok"
        else: cls = "weak"
        level_clean = re.sub(r"[★☆]+\s*", "", s["level"]).strip()
        rows_html += f"""<div class="shio-row {cls}">
  <div class="shio-emoji">{emoji}</div>
  <div class="shio-name"><span class="hz">{hz}</span> <span class="id">{indo}</span></div>
  <div class="shio-stars">{'★' * stars_count}{'☆' * max(0, 5 - stars_count)}</div>
  <div class="shio-level">{level_clean}</div>
  <div class="shio-ket">{md_inline(s['ket'])}</div>
</div>"""

    interps = extract_interpretasi(lines)
    interp_html = render_interpretasi(interps[0]) if interps else ""

    body = f"""{interp_html}
<div class="card-title compact">Kecocokan Shio Pasangan <span class="hz">婚配</span></div>
<div class="zw-section-intro tight">Tabel kecocokan shio Anda. Bintang lebih banyak = energi lebih harmonis.</div>
<div class="shio-compat-stack">{rows_html}</div>"""

    return [page(page_num, "Kecocokan Shio", "婚 配", "KECOCOKAN SHIO · 婚配", body, subject_name)], page_num + 1


def build_saran_inline(sec, subject_name, page_num):
    """Render BAB 'Saran & Kesimpulan' as standard ringkasan page."""
    epi_text = "## RINGKASAN & SARAN PRAKTIS\n\n### Profil Singkat\n" + "\n".join(sec["lines"])
    fake_parsed = {"epilogue": epi_text, "subject": {"Nama": subject_name}}
    pages_out = build_profil_saran(fake_parsed, subject_name, page_num)
    if isinstance(pages_out, list):
        return pages_out, page_num + len(pages_out)
    return [pages_out], page_num + 1


def build_catatan_inline(sec, subject_name, page_num):
    """Render Catatan/Peringatan as info page."""
    bullets = []
    for line in sec["lines"]:
        s = line.strip()
        if re.match(r"^-\s+", line):
            bullets.append(re.sub(r"^-\s+", "", line).strip())
        elif re.match(r"^\d+\.\s+", line):
            bullets.append(re.sub(r"^\d+\.\s+", "", line).strip())
    items = "".join(f'<div class="pot-item unfav">{md_inline(b)}</div>' for b in bullets)
    body = f"""<div class="card-title compact">{md_inline(sec['title'])}</div>
<div class="potensi-block unfav full-w">
  <div class="potensi-head"><span class="ico">⚠</span> Catatan Penting</div>
  <div class="pot-stack">{items}</div>
</div>"""
    return [page(page_num, sec["title"], "注 意", "CATATAN · 注意", body, subject_name)], page_num + 1


def build_section_4_OLD(sec, subject_name, page_num):
    """OLD section 4 — preserved for reference."""
    lines = sec["lines"]
    main_star = find_main_star(lines)
    star_hz, star_py, star_arketipe, star_def = _star_lookup(main_star)
    hero_html = _palace_hero_html(star_hz, star_py, star_arketipe, star_def)

    # ZWDS bullets
    zwds_bullets = []
    cur = None
    for line in lines:
        if "Zi Wei Dou Shu" in line and line.startswith("###"):
            cur = "zwds"; continue
        if "Sumber Kekayaan" in line and line.startswith("###"):
            cur = "bazi"; continue
        if line.startswith("###"):
            cur = None; continue
        if cur == "zwds" and re.match(r"^-\s+", line):
            zwds_bullets.append(re.sub(r"^-\s+", "", line).strip())

    # Parse traits from ZWDS bullets
    def parse_t(b):
        m = re.match(r"^\*\*([一-鿿\s]+)\*\*\s*[—–-]\s*(.+)$", b)
        if m: return (m.group(1).strip(), m.group(2).strip())
        m2 = re.match(r"^([一-鿿]{3,})\s*[—–-]\s*(.+)$", b)
        if m2: return (m2.group(1).strip(), m2.group(2).strip())
        return ("", b)

    zwds_traits = [parse_t(b) for b in zwds_bullets[:6]]
    zwds_html = ""
    for hzlab, indo in zwds_traits:
        if hzlab:
            zwds_html += f"""<div class="trait-card kekuatan">
  <div class="trait-hz">{hzlab}</div>
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""
        else:
            zwds_html += f"""<div class="trait-card kekuatan no-hz">
  <div class="trait-text">{md_inline(indo)}</div>
</div>"""

    # Pian/Zheng cards
    pian_cards = []
    in_pian = False
    for line in lines:
        if "Sumber Kekayaan" in line:
            in_pian = True; continue
        if in_pian and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4 and "Jenis" not in cells[0]:
                pian_cards.append({"name": cells[0], "hz": cells[1], "status": cells[2], "rec": cells[3]})
        if in_pian and line.startswith(">"):
            in_pian = False

    # Wealth icons mapping
    WEALTH_ICONS = {"偏財": "💰", "正財": "🏛", "正财": "🏛", "偏财": "💰"}
    wealth_html = ""
    for p in pian_cards[:2]:
        # extract Hanzi + Indo name
        nm = p["name"]
        nm_clean = re.sub(r"\*\*", "", nm)
        nm_hz_m = re.search(r"([一-鿿]+)", nm_clean)
        nm_hz = nm_hz_m.group(1) if nm_hz_m else ""
        nm_indo = re.sub(r"[一-鿿]+\s*", "", nm_clean).strip()
        icon = WEALTH_ICONS.get(nm_hz, "💼")
        is_zheng = "正" in nm_hz
        wealth_html += f"""<div class="wealth-card {'zheng' if is_zheng else 'pian'}">
  <div class="wc-icon">{icon}</div>
  <div class="wc-hz">{nm_hz}</div>
  <div class="wc-indo">{md_inline(nm_indo)}</div>
  <div class="wc-divider"></div>
  <div class="wc-row"><span class="wc-k">Status</span><span class="wc-v">{md_inline(p['status'])}</span></div>
  <div class="wc-row"><span class="wc-k">Rekomendasi</span><span class="wc-v">{md_inline(p['rec'])}</span></div>
</div>"""

    callouts = build_callouts_from_quotes(lines)
    rating_rows = parse_rating_table(lines, "Rating Keuangan")
    top3 = sorted(rating_rows, key=lambda r: -r[2])[:3] if rating_rows else []
    top_html = ""
    for id_lab, hz_lab, pct in top3:
        cls = "high" if pct >= 70 else ("mid" if pct >= 50 else "low")
        top_html += f"""<div class="char-top {cls}">
  <div class="char-top-pct">{pct}%</div>
  <div class="char-top-name"><div class="id">{id_lab}</div><div class="hz">{hz_lab}</div></div>
</div>"""

    body = f"""{hero_html}

<div class="char-block">
  <div class="char-block-head fav">
    <div class="bd-ico">✦</div>
    <div class="bd-titles"><div class="bd-id">Analisis Zi Wei Dou Shu</div><div class="bd-hz">紫微財運</div></div>
    <div class="bd-cnt">{len(zwds_traits)} Insight</div>
  </div>
  <div class="trait-grid kek-grid">{zwds_html}</div>
</div>

<div class="char-block">
  <div class="char-block-head neutral">
    <div class="bd-ico">◆</div>
    <div class="bd-titles"><div class="bd-id">Sumber Kekayaan — Analisis Ba Zi</div><div class="bd-hz">正財 · 偏財</div></div>
    <div class="bd-cnt">2 Sumber</div>
  </div>
  <div class="wealth-grid">{wealth_html}</div>
</div>

<div class="char-block">
  <div class="char-block-head neutral">
    <div class="bd-ico">◆</div>
    <div class="bd-titles"><div class="bd-id">Rating Keuangan</div><div class="bd-hz">財運評分</div></div>
    <div class="bd-cnt">{len(rating_rows)} Aspek</div>
  </div>
  <div class="char-top-row">{top_html}</div>
  <div class="char-rating">{render_rating_bars(rating_rows)}</div>
</div>

{''.join(callouts[:1])}"""
    return [page(page_num, "Kekayaan &amp; Keuangan", "財 帛 宮", "KEKAYAAN · 財帛", body, subject_name)], page_num + 1


# === SECTION 5 - KARIR (OLD - preserved) ===

def build_section_5_OLD(sec, subject_name, page_num):
    lines = sec["lines"]
    main_star = find_main_star(lines)
    star_tag = f'<div><span class="bintang-tag"><span class="lbl">Bintang Utama</span> {main_star}</span></div>' if main_star else ""

    # Profession ZWDS table
    prof_zwds = []
    in_pz = False
    for line in lines:
        if "Cocok — Zi Wei Dou Shu" in line:
            in_pz = True; continue
        if in_pz and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and "Kategori" not in cells[0]:
                prof_zwds.append((cells[0], cells[1]))
        if in_pz and line.startswith("###"):
            in_pz = False

    pz_html = "".join(f"<tr><td><strong>{c[0]}</strong></td><td>{md_inline(c[1])}</td></tr>" for c in prof_zwds)

    # BaZi profession bullets (Kayu/Api)
    kayu = []; api = []
    cur = None
    for line in lines:
        if "Kayu (木)" in line and "**" in line:
            cur = "kayu"; continue
        if "Api (火)" in line and "**" in line:
            cur = "api"; continue
        if line.startswith("###"):
            cur = None; continue
        if cur and re.match(r"^-\s+", line):
            (kayu if cur == "kayu" else api).append(re.sub(r"^-\s+", "", line).strip())

    # Kelebihan & Kelemahan
    kelebihan = []; kelemahan = []
    cur = None
    for line in lines:
        if "✅" in line and "Kelebihan" in line:
            cur = "p"; continue
        if "⚠️" in line and "Kelemahan" in line:
            cur = "n"; continue
        if line.startswith("###"):
            cur = None; continue
        if cur and re.match(r"^-\s+", line):
            (kelebihan if cur == "p" else kelemahan).append(re.sub(r"^-\s+", "", line).strip())

    rating_rows = parse_rating_table(lines, "Rating Karir")

    body1 = f"""{star_tag}
<div class="card">
  <div class="card-title">Profesi Cocok — Zi Wei Dou Shu</div>
  <div class="card-body"><table class="tbl"><thead><tr><th style="width: 40mm">Kategori</th><th>Profesi</th></tr></thead><tbody>{pz_html}</tbody></table></div>
</div>
<div class="card">
  <div class="card-title">Profesi Cocok — Ba Zi (Unsur Kayu &amp; Api)</div>
  <div class="card-body">
    <div class="grid-2">
      <div><div style="color:var(--green); font-weight:600; font-size:9pt; margin-bottom:1.5mm;">🌳 Kayu (木) — Sangat Cocok</div>{render_bullet_list(kayu[:6], 'green')}</div>
      <div><div style="color:var(--red); font-weight:600; font-size:9pt; margin-bottom:1.5mm;">🔥 Api (火) — Cocok</div>{render_bullet_list(api[:5], 'red')}</div>
    </div>
  </div>
</div>"""

    body2 = f"""<div class="grid-2">
  <div class="card">
    <div class="card-title">✦ Kelebihan Karir</div>
    <div class="card-body">{render_bullet_list(kelebihan, 'green')}</div>
  </div>
  <div class="card">
    <div class="card-title">⚠ Kelemahan Karir</div>
    <div class="card-body">{render_bullet_list(kelemahan, 'red')}</div>
  </div>
</div>
<div class="card">
  <div class="card-title">Rating Karir <span class="hz">事業評分</span></div>
  <div class="card-body">{render_rating_bars(rating_rows)}</div>
</div>"""
    return [
        page(page_num, "Karir &amp; Jabatan", "官 祿 宮", "KARIR · 官祿", body1, subject_name),
        page(page_num + 1, "Karir — Kelebihan &amp; Rating", "事業評分", "KARIR · 事業評分", body2, subject_name),
    ], page_num + 2


# === SECTION 8 - KESEHATAN (OLD) ===

def build_section_8_OLD(sec, subject_name, page_num):
    lines = sec["lines"]

    # ZWDS bullets
    zwds = []
    in_z = False
    for line in lines:
        if "Zi Wei Dou Shu" in line and "**" in line:
            in_z = True; continue
        if line.startswith("**Analisis Ba Zi"):
            in_z = False
        if line.startswith("###") or line.startswith("##"):
            in_z = False
        if in_z and re.match(r"^-\s+", line):
            zwds.append(re.sub(r"^-\s+", "", line).strip())

    # Organ table
    organs = []
    in_o = False
    for line in lines:
        if "Organ Tubuh" in line:
            in_o = True; continue
        if in_o and "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 5 and cells[0] and "Nomor" not in cells[0]:
                organs.append(cells)
        if in_o and line.startswith(">"):
            in_o = False

    organ_rows = ""
    for o in organs:
        risk_cls = ""
        if "Perhatian" in o[4] or "tinggi" in o[4].lower():
            risk_cls = "hl"
        organ_rows += f'<tr class="{risk_cls}"><td>{o[0]}</td><td><strong>{o[1]}</strong></td><td>{md_inline(o[2])}</td><td>{o[3]}</td><td>{md_inline(o[4])}</td></tr>'

    callouts = build_callouts_from_quotes(lines)
    rating_rows = parse_rating_table(lines, "Rating Kesehatan")

    body = f"""<div class="card">
  <div class="card-title">Analisis Zi Wei Dou Shu</div>
  <div class="card-body">{render_bullet_list(zwds[:5])}</div>
</div>
<div class="card-title">Analisis Ba Zi — Organ Tubuh <span class="hz">五行五臟</span></div>
<table class="tbl"><thead><tr><th>No</th><th>Organ</th><th>Hanzi</th><th>Elemen</th><th>Risiko</th></tr></thead><tbody>{organ_rows}</tbody></table>
{''.join(callouts[:1])}
<div class="card">
  <div class="card-title">Rating Kesehatan <span class="hz">健康評分</span></div>
  <div class="card-body">{render_rating_bars(rating_rows)}</div>
</div>"""
    return [page(page_num, "Kesehatan", "疾 厄 宮", "KESEHATAN · 疾厄", body, subject_name)], page_num + 1


# === SECTION 10 - PROPERTI (OLD) ===

def build_section_10_OLD(sec, subject_name, page_num):
    lines = sec["lines"]
    main_star = find_main_star(lines)
    star_tag = f'<div><span class="bintang-tag"><span class="lbl">Bintang Utama</span> {main_star}</span></div>' if main_star else ""
    bullets = parse_bullets(lines)
    rating_rows = parse_rating_table(lines, "Rating Properti")

    body = f"""{star_tag}
<div class="card"><div class="card-title">Gambaran Properti</div><div class="card-body">{render_bullet_list(bullets[:6])}</div></div>
<div class="card"><div class="card-title">Rating Properti <span class="hz">田宅評分</span></div><div class="card-body">{render_rating_bars(rating_rows)}</div></div>"""
    return [page(page_num, "Properti &amp; Rumah", "田 宅 宮", "PROPERTI · 田宅", body, subject_name)], page_num + 1


# === SECTION 15 - SHEN SHA ===

def build_section_15_OLD(sec, subject_name, page_num):
    lines = sec["lines"]
    stars = []
    in_s = False
    for line in lines:
        if "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and "Bintang" not in cells[0] and cells[0]:
                stars.append({"name": cells[0], "hz": cells[1], "meaning": cells[2]})

    cards = ""
    for s in stars:
        m = re.match(r"^\*\*([一-鿿]+)\s*([^*]+)\*\*", s["name"])
        nm_hz = m.group(1) if m else s["name"]
        nm_py = m.group(2).strip() if m else ""
        cards += f"""<div class="card">
  <div class="card-title"><span class="hz">{nm_hz}</span> {nm_py}</div>
  <div class="card-body"><p>{md_inline(s['meaning'])}</p></div>
</div>"""

    callouts = build_callouts_from_quotes(lines)

    body = f"""<div class="lead"><strong>Shen Sha</strong> adalah bintang-bintang nasib khusus yang memberi warna unik pada bagan. Beberapa bersifat membantu, beberapa harus diwaspadai.</div>
{cards}
{''.join(callouts)}"""
    return [page(page_num, "Tanda Bintang Khusus", "神 煞", "BINTANG KHUSUS · 神煞", body, subject_name)], page_num + 1


# === SECTION 16 - KESIMPULAN UMUM ===

def build_section_16_OLD(sec, subject_name, page_num):
    lines = sec["lines"]
    points = []
    in_t = False
    for line in lines:
        if "|" in line and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0].isdigit():
                points.append({"id": cells[1], "hz": cells[2]})

    items = ""
    for i, p in enumerate(points, 1):
        items += f"""<div class="li">
  <div class="num">{i}</div>
  <div><div style="color:var(--text); font-weight:500;">{md_inline(p['id'])}</div>
       <div style="font-family: 'Noto Serif TC', serif; color: var(--red); font-size:8.5pt; margin-top:0.5mm;">{p['hz']}</div></div>
</div>"""

    callouts = build_callouts_from_quotes(lines)

    body = f"""<div class="lead">Tujuh poin di bawah merupakan <strong>distilasi inti</strong> dari seluruh analisis bagan — lihat bagian ini sebagai checklist hidup.</div>
<div class="card">
  <div class="card-title">Tujuh Poin Inti <span class="hz">全局總論</span></div>
  <div class="card-body"><div class="list-num red">{items}</div></div>
</div>
{''.join(callouts)}"""
    return [page(page_num, "Kesimpulan Umum", "全 局 總 論", "KESIMPULAN · 全局", body, subject_name)], page_num + 1


# === SECTION 17 - FENG SHUI ===

def build_section_17(sec, subject_name, page_num):
    lines = sec["lines"]

    # Hardcode compass cells based on MD content (北/中/南 grid).
    # MD ascii compass: BL/U/TL on top row; B/Tengah/T on middle; BD/S/Tg on bottom.
    # Based on MD: Utara TERBAIK, Timur Laut bagus, Timur, Tenggara, Selatan bagus
    # Barat Laut, Barat, Barat Daya = bad
    cells = [
        ("Barat Laut", "戌乾", "bad", "凶"),
        ("Utara",      "壬子癸", "center", "✓ TERBAIK"),
        ("Timur Laut", "丑艮寅", "good", "✓"),
        ("Barat",      "庚酉辛", "bad", "凶"),
        ("Tengah",     "中宮",  "center", "RUMAH"),
        ("Timur",      "甲卯乙", "good", "✓"),
        ("Barat Daya", "未坤申", "bad", "凶"),
        ("Selatan",    "丙午丁", "good", "✓"),
        ("Tenggara",   "辰巽巳", "good", "✓"),
    ]
    compass_html = ""
    for c in cells:
        cls = c[2]
        compass_html += f"""<div class="compass-cell {cls}">
  <div class="dir">{c[0]}</div>
  <div class="hz">{c[1]}</div>
  <div class="mark">{c[3]}</div>
</div>"""

    # Recommendations table
    recs = []
    in_r = False
    for line in lines:
        if "Rekomendasi Feng Shui" in line:
            in_r = True; continue
        if in_r and "|" in line and "---" not in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            if len(cs) >= 4 and cs[0] and "Elemen" not in cs[0]:
                recs.append(cs)

    rec_rows = "".join(f"<tr><td><strong>{md_inline(r[0])}</strong></td><td><span class='hz'>{r[1]}</span></td><td>{md_inline(r[2])}</td></tr>" for r in recs)

    body = f"""<div class="lead">Tata letak rumah memengaruhi kualitas hidup penghuninya. Bagian ini memberi panduan arah hadap dan posisi elemen-elemen utama berdasarkan bagan Anda.</div>
<div class="grid-2">
  <div>
    <div class="card-title">Kompas Arah <span class="hz">方位</span></div>
    <div class="compass">{compass_html}</div>
  </div>
  <div>
    <div class="card-title">Rekomendasi Feng Shui Rumah</div>
    <table class="tbl"><thead><tr><th>Elemen</th><th>Hanzi</th><th>Rekomendasi</th></tr></thead><tbody>{rec_rows}</tbody></table>
  </div>
</div>"""
    return [page(page_num, "Feng Shui Rumah", "陽 宅", "FENG SHUI · 陽宅", body, subject_name)], page_num + 1


# === SECTION 18 - LIU NIAN ===

def build_section_18(sec, subject_name, page_num):
    """Yearly forecast 2026-2031 + summary chart."""
    lines = sec["lines"]
    # Split per year
    text = "\n".join(lines)
    year_blocks = re.split(r"###\s+Tahun\s+(\d+)\s+—\s+", text)
    years = []
    # year_blocks[0] = preamble; then alternating year, body, year, body...
    for i in range(1, len(year_blocks), 2):
        yr = year_blocks[i]
        body = year_blocks[i + 1] if i + 1 < len(year_blocks) else ""
        years.append({"year": int(yr), "raw": body})

    year_cards = []
    for y in years:
        body = y["raw"]
        # Header line: "西元2026年 · 丙午年 · Usia 64 Tahun" -> on first line
        head_m = re.match(r"^([^\n]+)", body)
        head = head_m.group(1).strip() if head_m else ""
        gan_m = re.search(r"·\s*([一-鿿]+年?)\s*·", head)
        gan = gan_m.group(1) if gan_m else ""
        age_m = re.search(r"Usia\s+(\d+)", head)
        age = age_m.group(1) if age_m else ""
        # Stars
        stars_m = re.search(r"\*\*Bintang Tahunan Aktif:\*\*\s*(.+)", body)
        stars_html = ""
        if stars_m:
            star_str = stars_m.group(1)
            for s in re.findall(r"([一-鿿]+)\s*\(([^)]+)\)", star_str):
                stars_html += f'<span class="star-tag">{s[0]} {s[1]}</span>'
        # Aspects table
        rows_html = ""
        in_t = False
        for line in body.split("\n"):
            if "|" in line and "---" not in line:
                cs = [c.strip() for c in line.strip("|").split("|")]
                if len(cs) >= 2 and cs[0] and "Aspek" not in cs[0]:
                    k = cs[0]; v = cs[1] if len(cs) > 1 else ""
                    rows_html += f'<div class="row"><div class="k">{md_inline(k)}</div><div>{md_inline(v)}</div></div>'
        # Prediksi pct
        pct_m = re.search(r"\*\*[^*]*Prediksi:?\s*[^*]*?(\d+)%\*\*", body)
        pct = int(pct_m.group(1)) if pct_m else 50
        pct_cls = ""
        if pct >= 70: pct_cls = ""
        elif pct >= 50: pct_cls = "mid"
        else: pct_cls = "bad"

        year_cards.append(f"""<div class="year-card">
  <div class="yhead">
    <div class="yr">{y['year']}</div>
    <div class="meta"><div class="gan">{gan}</div><div class="age">Usia {age} Tahun</div></div>
    <div class="pct {pct_cls}">{pct}%</div>
  </div>
  <div class="ybody">
    <div class="stars">{stars_html}</div>
    {rows_html}
  </div>
</div>""")

    # Summary bar chart from MD's "Ringkasan Ramalan Tahunan" table (last 6 rows)
    summary_rows = []
    for line in lines:
        if "|" in line and "---" not in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            if len(cs) >= 5 and re.match(r"^\*\*\d{4}\*\*", cs[0]):
                yr = re.search(r"\d{4}", cs[0]).group(0)
                age = cs[1]
                shio = cs[2]
                star = cs[3]
                pct_m = re.search(r"(\d+)%", cs[4])
                pct = int(pct_m.group(1)) if pct_m else 50
                summary_rows.append({"yr": yr, "age": age, "shio": shio, "star": star, "pct": pct})

    summary_html = ""
    for r in summary_rows:
        cls = percent_class(r["pct"])
        summary_html += f"""<div class="bar-row">
  <div class="bar-label">
    <div class="id">Tahun {r['yr']} · Usia {r['age']}</div>
    <div class="hz">{md_inline(r['shio'])} · {md_inline(r['star'])}</div>
  </div>
  <div class="bar-track"><div class="bar-fill {cls}" style="width: {r['pct']}%"></div></div>
  <div class="bar-pct">{r['pct']}%</div>
</div>"""

    callouts = build_callouts_from_quotes(lines)

    pages = []
    # Page 1: years 2026-2028
    body1 = f"""<div class="lead">Tiga tahun pertama dari periode ramalan. Setiap kartu menampilkan <strong>bintang aktif</strong>, aspek utama, dan persentase keberuntungan keseluruhan.</div>
<div style="display: flex; flex-direction: column; gap: 3mm;">{''.join(year_cards[:3])}</div>"""
    pages.append(page(page_num, "Ramalan Tahunan 2026-2028", "流 年 判 斷", "RAMALAN TAHUNAN · 流年", body1, subject_name))

    # Page 2: years 2029-2031
    body2 = f"""<div class="lead">Tiga tahun berikutnya — perhatikan transisi keberuntungan sebagai panduan kapan harus berani dan kapan harus berhati-hati.</div>
<div style="display: flex; flex-direction: column; gap: 3mm;">{''.join(year_cards[3:6])}</div>"""
    pages.append(page(page_num + 1, "Ramalan Tahunan 2029-2031", "流 年 判 斷", "RAMALAN TAHUNAN · 流年", body2, subject_name))

    # Page 3: summary chart
    body3 = f"""<div class="lead"><strong>Ringkasan visual</strong> 6 tahun ke depan. Tahun terbaik dan terburuk dari periode ini ditunjukkan oleh tinggi bar.</div>
<div class="card">
  <div class="card-title">Persentase Keberuntungan Tahunan</div>
  <div class="card-body">{summary_html}</div>
</div>
{''.join(callouts[-1:])}"""
    pages.append(page(page_num + 2, "Ringkasan Ramalan Tahunan", "流 年 總 覽", "RINGKASAN TAHUNAN · 流年", body3, subject_name))

    return pages, page_num + 3


# === SECTION 19 - KECOCOKAN SHIO ===

def build_section_19(sec, subject_name, page_num):
    lines = sec["lines"]
    rows = []
    for line in lines:
        if "|" in line and "---" not in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            if len(cs) >= 5 and "%" in line and "Shio" not in cs[0]:
                # cs[0] = "**Kuda 🐴**", cs[1] = "馬", cs[2] = "**95%**", cs[3] = "⭐⭐⭐⭐⭐ Terbaik", cs[4] = ket
                emoji_m = re.search(r"([\U0001F400-\U0001F4FF\U0001F300-\U0001F3FF\U0001F900-\U0001F9FF])", cs[0])
                emoji = emoji_m.group(1) if emoji_m else "·"
                name_m = re.search(r"\*\*([^*🐭🐂🐯🐰🐉🐍🐴🐑🐒🐓🐕🐷]+?)\s*[\U0001F400-\U0001F4FF]?\*\*", cs[0])
                name = name_m.group(1).strip() if name_m else cs[0].strip("*")
                hz = cs[1]
                pct_m = re.search(r"(\d+)%", cs[2])
                pct = int(pct_m.group(1)) if pct_m else 0
                level = re.sub(r"⭐+\s*", "", cs[3]).replace("✗", "").strip() or "—"
                desc = cs[4] if len(cs) > 4 else ""
                rows.append({"emoji": emoji, "name": name, "hz": hz, "pct": pct, "level": level, "desc": desc})

    rows_html = ""
    for r in rows:
        if r["pct"] >= 80: cls = "best"
        elif r["pct"] >= 65: cls = "good"
        elif r["pct"] >= 50: cls = "ok"
        else: cls = "weak"
        rows_html += f"""<div class="shio-compat-row">
  <div class="icon">{r['emoji']}</div>
  <div class="name"><div class="id">{html.escape(r['name'])}</div><div class="hz">{r['hz']}</div></div>
  <div class="bar"><div class="fill {cls}" style="width: {r['pct']}%"></div></div>
  <div class="pct">{r['pct']}%</div>
  <div class="level">{html.escape(r['level'])}</div>
</div>"""

    callouts = build_callouts_from_quotes(lines)

    body = f"""<div class="lead"><strong>Persentase kecocokan</strong> shio Anda dengan 12 shio lain. Pasangan ideal di atas 80%; sebaiknya hindari di bawah 40%.</div>
<div class="card">
  <div class="card-title">Tabel Kecocokan Shio Anda</div>
  <div class="card-body">{rows_html}</div>
</div>
{''.join(callouts[:2])}"""
    return [page(page_num, "Kecocokan Shio", "婚 配 對 照", "KECOCOKAN SHIO · 婚配", body, subject_name)], page_num + 1


# === SECTION 20 - PESAN KLASIK ===

def build_section_20(sec, subject_name, page_num):
    text = "\n".join(sec["lines"])
    # Each syair starts with **... :** then > line(s), then italic translation
    # Pattern: bold marker line, then '> verse', then '> *italic*'
    syairs = []
    blocks = re.split(r"\*\*([^*]+)\s*\(([^)]+)\):\*\*", text)
    # blocks: [pre, src1, label1, body1, src2, label2, body2, ...]
    for i in range(1, len(blocks), 3):
        src = blocks[i].strip()
        label = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
        body = blocks[i + 2] if i + 2 < len(blocks) else ""
        # Extract verse (lines starting with >, not italic) and trans (italic)
        verse_lines = []
        trans_lines = []
        for ln in body.split("\n"):
            if ln.strip().startswith(">"):
                content = ln.lstrip(">").strip()
                if content.startswith("*") and content.endswith("*"):
                    trans_lines.append(content.strip("*"))
                elif content:
                    verse_lines.append(content)
        if verse_lines or trans_lines:
            syairs.append({"src": src, "label": label, "verse": verse_lines, "trans": trans_lines})

    cards = ""
    for s in syairs[:3]:
        verse = "<br>".join(html.escape(v) for v in s["verse"])
        trans = " ".join(t for t in s["trans"])
        cards += f"""<div class="syair-card">
  <div class="src"><span class="hz">{s['src']}</span> {s['label']}</div>
  <div class="verse">{verse}</div>
  <div class="trans">{md_inline(trans)}</div>
</div>"""

    body = f"""<div class="lead">Tiga pesan dari <strong>kitab klasik Ba Zi</strong> yang relevan dengan pola kelahiran Anda. Bacalah sebagai bahan refleksi, bukan literal.</div>
<div style="display: flex; flex-direction: column; gap: 3.5mm;">{cards}</div>"""
    return [page(page_num, "Pesan Klasik Ba Zi", "古 書 云", "PESAN KLASIK · 古書", body, subject_name)], page_num + 1


# === EPILOGUE: SKOR + SARAN ===

def build_skor_akhir(parsed, subject_name, page_num):
    """Dashboard skor akhir from epilogue."""
    epi = parsed["epilogue"]
    rows = []
    overall = None
    in_t = False
    for line in epi.split("\n"):
        if "SKOR KESELURUHAN" in line:
            in_t = True; continue
        if in_t and "|" in line and "---" not in line:
            cs = [c.strip() for c in line.strip("|").split("|")]
            if len(cs) >= 4 and "Aspek Hidup" not in cs[0]:
                pct_m = re.search(r"(\d+)%", cs[3])
                if pct_m:
                    pct = int(pct_m.group(1))
                    name = re.sub(r"\*\*", "", cs[0])
                    hz = re.sub(r"\*\*", "", cs[1])
                    if "Rata-rata" in name or "綜合" in hz:
                        overall = (name, hz, pct)
                    else:
                        rows.append({"id": name, "hz": hz, "pct": pct})

    cards = ""
    for r in rows:
        cls = "high" if r["pct"] >= 70 else ("mid" if r["pct"] >= 50 else "low")
        cards += f"""<div class="dash-card {cls}">
  <div class="top">
    <div class="name"><div class="id">{md_inline(r['id'])}</div><div class="hz">{r['hz']}</div></div>
    <div class="pct">{r['pct']}%</div>
  </div>
  <div class="bar-track"><div class="bar-fill {cls}" style="width: {r['pct']}%"></div></div>
</div>"""

    overall_html = ""
    if overall:
        overall_html = f"""<div class="dash-overall">
  <div><div class="lbl">Rata-rata Keseluruhan</div><div style="font-family:'Noto Serif TC',serif; font-size:14pt; margin-top:1mm;">{overall[1]}</div></div>
  <div class="desc">Rata-rata dari seluruh aspek kehidupan. Skor di atas 65% menunjukkan profil hidup yang seimbang dan beruntung secara umum.</div>
  <div class="pct-big">{overall[2]}%</div>
</div>"""

    body = f"""<div class="lead">Distilasi <strong>seluruh laporan</strong> dalam satu dashboard skor. Lihat aspek mana yang paling kuat dan mana yang perlu perhatian khusus.</div>
<div class="dash-grid">{cards}</div>
{overall_html}"""
    return page(page_num, "Skor Akhir Bagan", "綜 合 總 評", "SKOR AKHIR · 總評", body, subject_name)


def build_saran(parsed, subject_name, page_num):
    epi = parsed["epilogue"]

    # Kekuatan Terbesar (numbered list)
    kek = []; tan = []; rec = []
    cur = None
    for line in epi.split("\n"):
        if "Kekuatan Terbesar" in line:
            cur = "k"; continue
        if "Tantangan Terbesar" in line:
            cur = "t"; continue
        if "Rekomendasi Praktis" in line:
            cur = "r"; continue
        if line.startswith("###") or line.startswith("---"):
            cur = None; continue
        m = re.match(r"^\d+\.\s+(.+)", line)
        if m and cur in ("k", "t"):
            (kek if cur == "k" else tan).append(m.group(1).strip())
        m2 = re.match(r"^-\s+(.+)", line)
        if m2 and cur == "r":
            rec.append(m2.group(1).strip())

    rec_cards = ""
    for r in rec[:6]:
        # Extract emoji at start
        em_m = re.match(r"^([\U0001F300-\U0001F9FF])\s*(?:\*\*(.+?)\*\*)?\s*[—–-]?\s*(.*)", r)
        if em_m:
            emoji = em_m.group(1)
            bold = em_m.group(2) or ""
            rest = em_m.group(3)
            content = (f"<strong>{bold}</strong> — " if bold else "") + rest
        else:
            emoji = "•"
            content = r
        rec_cards += f'<div class="saran-card green"><div class="ico">{emoji}</div><div>{md_inline(content)}</div></div>'

    kek_items = ""
    for i, k in enumerate(kek[:4], 1):
        kek_items += f'<div class="li"><div class="num">{i}</div><div>{md_inline(k)}</div></div>'

    tan_items = ""
    for i, t in enumerate(tan[:4], 1):
        tan_items += f'<div class="li"><div class="num">{i}</div><div>{md_inline(t)}</div></div>'

    body = f"""<div class="grid-2">
  <div class="card">
    <div class="card-title">✦ Kekuatan Terbesar</div>
    <div class="card-body"><div class="list-num green">{kek_items}</div></div>
  </div>
  <div class="card">
    <div class="card-title">⚠ Tantangan Terbesar</div>
    <div class="card-body"><div class="list-num red">{tan_items}</div></div>
  </div>
</div>
<div class="card-title">Rekomendasi Praktis Hidup</div>
<div class="saran-grid">{rec_cards}</div>"""
    return page(page_num, "Saran &amp; Kesimpulan Akhir", "建 議 與 總 結", "SARAN PRAKTIS · 建議", body, subject_name)


# === GLOSSARY (DYNAMIC) ===

def build_glossary(md_text, subject_name, page_num):
    """Extract Hanzi terms used in MD. Auto-split to multiple pages if too many."""
    used = []
    for term, (py, defn) in GLOSSARY.items():
        if term in md_text:
            used.append((term, py, defn))

    PER_PAGE = 22  # fits comfortably in 2-col grid
    pages_out = []
    chunks = [used[i:i + PER_PAGE] for i in range(0, len(used), PER_PAGE)] or [[]]
    total_pages = len(chunks)

    for idx, chunk in enumerate(chunks):
        items = ""
        for term, py, defn in chunk:
            items += f"""<div class="gloss-item">
  <div class="term">{term}<span class="py">{py}</span></div>
  <div class="def">{md_inline(defn)}</div>
</div>"""

        suffix = f" (Bagian {idx + 1}/{total_pages})" if total_pages > 1 else ""
        intro_text = "Glosarium istilah Hanzi yang muncul dalam laporan ini." if idx == 0 else "Lanjutan glosarium istilah."
        body = f"""<div class="zw-section-intro tight"><strong>{intro_text}</strong> Daftar dibuat otomatis dari kemunculan istilah di teks. {f'Total <strong>{len(used)} istilah</strong> dalam {total_pages} halaman.' if total_pages > 1 else f'Total <strong>{len(used)} istilah</strong>.'}</div>
<div class="card thin">
  <div class="gloss-grid">{items}</div>
</div>"""
        pages_out.append(page(page_num + idx, f"Glosarium Istilah{suffix}", "詞 彙 表", "GLOSARIUM · 詞彙", body, subject_name))

    return pages_out


def build_disclaimer(subject_name, page_num):
    """Disclaimer V4.5 hardcode — 4-card layout with hero + closing."""
    body = """<div class="dis-hero">
  <div class="dh-seal">告白</div>
  <div class="dh-text">
    <div class="dh-eb">Etika &amp; Batasan</div>
    <div class="dh-quote">
      Bagan ini adalah <span class="hz">peta pola</span>, bukan vonis. Pakai sebagai referensi tradisi &amp; <strong>eksplorasi diri</strong> — keputusan tetap di tangan Anda.
    </div>
  </div>
</div>

<div class="dis-cards">
  <div class="dc-card dont">
    <div class="dc-eb">不 用 · Yang Tidak Dilakukan</div>
    <div class="dc-title"><span class="dc-hz">禁忌</span><span class="dc-name">Jìn Jì · Larangan Etis</span></div>
    <div class="dc-list">
      <div class="dc-item"><span class="ico">✗</span><span>Tidak ada <strong>prediksi kematian</strong> dalam bentuk apapun</span></div>
      <div class="dc-item"><span class="ico">✗</span><span>Tidak ada kalimat absolut ("PASTI akan...", "TIDAK MUNGKIN...")</span></div>
      <div class="dc-item"><span class="ico">✗</span><span>Tidak ada <strong>diagnosa medis/hukum</strong> spesifik</span></div>
      <div class="dc-item"><span class="ico">✗</span><span>Tidak ada bahasa menakutkan atau intimidasi</span></div>
    </div>
  </div>

  <div class="dc-card do">
    <div class="dc-eb">必 行 · Yang Dijamin</div>
    <div class="dc-title"><span class="dc-hz">原則</span><span class="dc-name">Yuán Zé · Prinsip Etis</span></div>
    <div class="dc-list">
      <div class="dc-item"><span class="ico">✓</span><span>Bahasa <strong>pemberdayaan</strong>: "kecenderungan", "trend", "potensi"</span></div>
      <div class="dc-item"><span class="ico">✓</span><span>Bahasa negatif <strong>dibalik konstruktif</strong>: "tantangan ini bisa diatasi dengan ..."</span></div>
      <div class="dc-item"><span class="ico">✓</span><span>Saran berbasis <strong>data dari sumber</strong>, bukan opini bebas</span></div>
      <div class="dc-item"><span class="ico">✓</span><span>Pengakuan: <strong>budaya, bukan ilmu pasti</strong></span></div>
    </div>
  </div>

  <div class="dc-card scope">
    <div class="dc-eb">範 圍 · Cakupan</div>
    <div class="dc-title"><span class="dc-hz">範圍</span><span class="dc-name">Fàn Wéi · Scope</span></div>
    <div class="dc-list">
      <div class="dc-item"><span class="ico">◆</span><span>Sumber data: <strong>output software</strong> 星僑 四柱論命附加紫微斗數 V2.6</span></div>
      <div class="dc-item"><span class="ico">◆</span><span>Methodology multi-school: <span class="hz">三命通會</span>, <span class="hz">子平真詮</span>, <span class="hz">滴天髓</span></span></div>
      <div class="dc-item"><span class="ico">◆</span><span>Cakupan: 八字 (Ba Zi) + 紫微斗數 (Zi Wei) + 陽宅 (Feng Shui)</span></div>
      <div class="dc-item"><span class="ico">◆</span><span>Tidak menambah prediksi <strong>di luar data sumber</strong></span></div>
    </div>
  </div>

  <div class="dc-card legal">
    <div class="dc-eb">法 律 · Pernyataan Hukum</div>
    <div class="dc-title"><span class="dc-hz">聲明</span><span class="dc-name">Shēng Míng · Pernyataan</span></div>
    <div class="dc-list">
      <div class="dc-item"><span class="ico">◆</span><span>Bagan ini <strong>tidak menggantikan</strong> keputusan medis profesional</span></div>
      <div class="dc-item"><span class="ico">◆</span><span><strong>Tidak menggantikan</strong> nasihat hukum atau finansial</span></div>
      <div class="dc-item"><span class="ico">◆</span><span>Tidak menjamin akurasi terjemahan istilah klasik (lihat <span class="hz">辭典</span> halaman glosarium)</span></div>
      <div class="dc-item"><span class="ico">◆</span><span>Subjek &amp; pembuat tidak bertanggung jawab atas keputusan berdasarkan laporan ini</span></div>
    </div>
  </div>
</div>

<div class="dis-close">
  <div class="dc-close-text">
    <div class="dc-close-eb">Penutup</div>
    <div class="dc-close-quote">
      "<span class="hz">命由己造，相由心生</span>" — Takdir dibentuk oleh diri sendiri; wajah lahir dari hati. Bagan ini cermin pola; <strong>kunci tetap di tangan Anda</strong>.
    </div>
  </div>
  <div class="dc-close-mark">完</div>
</div>"""
    return page(page_num, "Disclaimer &amp; Etika", "告 白", "DISCLAIMER · 告白", body, subject_name)


# === MASTER ASSEMBLY ===

def assemble_master(pages, subject_name):
    css_path = (ROOT / "style.css").resolve()
    css_url = "file:///" + str(css_path).replace("\\", "/")
    pages_html = "\n".join(pages)
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>{html.escape(subject_name)} — Laporan Ramalan</title>
<link rel="stylesheet" href="{css_url}">
<style>
@page {{ size: A4 portrait; margin: 0; }}
html, body {{ background: white !important; margin: 0 !important; padding: 0 !important; }}
.page {{ page-break-after: always !important; page-break-inside: avoid !important; margin: 0 !important; box-shadow: none !important; }}
.page:last-child {{ page-break-after: auto !important; }}
</style>
</head>
<body>
{pages_html}
</body>
</html>"""


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Chrome / Edge not found")


def run_chrome(master_html: Path, out_pdf: Path) -> Path:
    chrome = find_chrome()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    tmp_pdf = Path(os.environ.get("TEMP", ".")) / f"_pdf_v46_{os.getpid()}.pdf"
    src_url = "file:///" + str(master_html).replace("\\", "/")
    args = [
        chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
        "--disable-extensions", "--disable-background-networking",
        "--allow-file-access-from-files",
        "--virtual-time-budget=2500",
        "--run-all-compositor-stages-before-draw",
        "--disable-features=PaintHolding",
        f"--print-to-pdf={tmp_pdf}",
        "--no-pdf-header-footer",
        src_url,
    ]
    subprocess.run(args, capture_output=True, timeout=90)
    if not tmp_pdf.exists():
        raise RuntimeError("Chrome did not produce PDF")
    try:
        shutil.move(str(tmp_pdf), str(out_pdf))
        return out_pdf
    except (PermissionError, OSError):
        alt = out_pdf.with_name(out_pdf.stem + f"_{time.strftime('%H%M%S')}.pdf")
        shutil.move(str(tmp_pdf), str(alt))
        return alt


# === MAIN ===

def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <md_file>")
        sys.exit(1)

    md_path = Path(sys.argv[1]).resolve()
    md_text = md_path.read_text(encoding="utf-8")
    parsed = parse_md(md_text)

    subject_name = parsed["subject"].get("Nama", "Subject")

    # Plan pages: cover(1), toc(2), pengantar(3), section1+1=2 pages(4-5), section 2..20 pages, epilog 2, glossary, disclaimer.
    # Build the pages first then later assemble TOC with real page numbers.

    pages = []
    page_starts = {}  # section_num → first page
    pn = 4  # cover=1, toc=2, pengantar=3 → sections start at 4

    # Build sections in order
    section_builders = {
        1: build_section_1,
        2: build_section_2,
        3: build_palace_section,
        4: build_section_4,
        5: build_section_5,
        6: build_palace_section,
        7: build_palace_section,
        8: build_section_8,
        9: build_palace_section,
        10: build_section_10,
        11: build_palace_section,
        12: build_palace_section,
        13: build_palace_section,
        14: build_palace_section,
        15: build_section_15,
        16: build_section_16,
        17: build_section_17,
        18: build_section_18,
        19: build_section_19,
        20: build_section_20,
    }

    section_pages = []
    for sec in parsed["sections"]:
        n = sec["num"]
        builder = section_builders.get(n, build_generic_section)
        page_starts[n] = pn
        try:
            sps, pn = builder(sec, subject_name, pn)
        except Exception as e:
            print(f"!! Error building section {n}: {e}")
            sps = [page(pn, sec["title"], "", "ERROR", f"<div class='lead'>Error: {html.escape(str(e))}</div>", subject_name)]
            pn += 1
        section_pages.extend(sps)

    # Epilogue
    skor_pn = pn
    skor_page = build_skor_akhir(parsed, subject_name, pn); pn += 1
    saran_page = build_saran(parsed, subject_name, pn); pn += 1
    glossary_page = build_glossary(md_text, subject_name, pn); pn += 1
    disclaimer_page = build_disclaimer(subject_name, pn); pn += 1

    # Build cover, toc, pengantar
    cover_html = build_cover(parsed["subject"], parsed["sections"])
    toc_html = build_toc(parsed["toc"], subject_name, page_starts)
    pengantar_html = build_pengantar(subject_name)

    all_pages = [cover_html, toc_html, pengantar_html] + section_pages + [skor_page, saran_page, glossary_page, disclaimer_page]

    master = assemble_master(all_pages, subject_name)
    out_html = ROOT / "_out" / "master.html"
    out_html.parent.mkdir(exist_ok=True)
    out_html.write_text(master, encoding="utf-8")
    print(f"[1/2] HTML written: {out_html}")

    # PDF naming: {NAME}-{DD-MM-YYYY}.pdf
    # Extract birth date
    lahir = parsed["subject"].get("Lahir", "")
    dm = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", lahir)
    bulan_map = {"Januari":"01","Februari":"02","Maret":"03","April":"04","Mei":"05","Juni":"06","Juli":"07","Agustus":"08","September":"09","Oktober":"10","November":"11","Desember":"12"}
    if dm:
        dd = dm.group(1).zfill(2); mm = bulan_map.get(dm.group(2), "01"); yyyy = dm.group(3)
        date_str = f"{dd}-{mm}-{yyyy}"
    else:
        date_str = "00-00-0000"
    name_clean = re.sub(r"\s+", "-", subject_name).upper()
    pdf_name = f"{name_clean}-{date_str}.pdf"

    # Write to OneDrive #result/{TODAY}/
    onedrive_out = Path(r"C:\Users\sukam\OneDrive\Documents\Ramalan\#result") / TODAY / pdf_name
    local_out = ROOT / "_out" / pdf_name

    print(f"[2/2] Chrome → PDF...")
    pdf_path = run_chrome(out_html, local_out)
    print(f"   Local: {pdf_path}")

    try:
        onedrive_out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(pdf_path), str(onedrive_out))
        print(f"   OneDrive: {onedrive_out}")
    except Exception as e:
        print(f"   OneDrive copy failed: {e}")

    print(f"DONE: {pdf_path}")


if __name__ == "__main__":
    main()

