"""V4.5 build+render orchestrator. Auto-detect MD vs ocr.json mode.

Daily flow (NEW MD-driven mode):
  1. User upload foto ke Web Claude, paste prompt → output {id}.md
  2. Save MD ke `data/subjects/{id}.md`
  3. Run: `python build_pdf.py {id}`, auto-detect MD, parse, build, render
  4. Output PDF ke `#result/{date}/{Name}-{Hanzi}-{Birth}.pdf`

Legacy mode (ocr.json only, no MD):
  - Same command works. Falls back to {id}.ocr.json + LinRuYi default prose.
"""
import sys, time, json, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engines"))

from build_from_ocr import build_subject_from_ocr
from render import render_subject, _normalize_subject_for_render
from parse_md import parse_md, hanzi_to_span, md_inline, parse_kepribadian_struct


DATA_DIR = ROOT / "data" / "subjects"


def notify_done(title: str, message: str):
    """Windows notification: play sound + show toast balloon. Best-effort, never block."""
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass
    try:
        import subprocess
        t = title.replace('"', "'")
        m = message.replace('"', "'").replace("\n", " ")
        ps = (
            'Add-Type -AssemblyName System.Windows.Forms; '
            'Add-Type -AssemblyName System.Drawing; '
            '$n = New-Object System.Windows.Forms.NotifyIcon; '
            '$n.Icon = [System.Drawing.SystemIcons]::Information; '
            '$n.Visible = $true; '
            f'$n.ShowBalloonTip(8000, "{t}", "{m}", '
            '[System.Windows.Forms.ToolTipIcon]::Info); '
            'Start-Sleep -Seconds 9; '
            '$n.Dispose()'
        )
        subprocess.Popen(
            ['powershell.exe', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', ps],
            creationflags=0x08000000
        )
    except Exception:
        pass


def find_md_for_subject(subject_id: str) -> Path | None:
    """Find MD file for subject_id. Tries multiple patterns."""
    candidates = [
        DATA_DIR / f"{subject_id}.md",
        DATA_DIR / f"{subject_id.lower()}.md",
    ]
    # Also scan for files starting with subject_id (case-insensitive)
    for f in DATA_DIR.glob("*.md"):
        if f.stem.lower().startswith(subject_id.lower()):
            candidates.append(f)
    # And subdirectories like "test 1/"
    for sub in DATA_DIR.iterdir():
        if sub.is_dir():
            for f in sub.glob("*.md"):
                if f.stem.lower().startswith(subject_id.lower()):
                    candidates.append(f)
    for c in candidates:
        if c.exists():
            return c
    return None


# Per-stem archetype profile for the dm-card on page 6.
# Keys = 10 天干 stems. Each entry: archetype name + 3 Indonesian trait bullets +
# 2 favorable elements (yong shen pair, used in the 3rd trait line).
DM_PROFILES = {
    "甲": {"label": "Pohon Besar",  "traits": ["<strong>Pendiri</strong>, kreatif, idealis",
                                                "Pohon kuat, butuh <strong>dipangkas</strong> agar berbuah",
                                                "Mekar dengan ekspresi + disiplin"], "fav": ["火","金"]},
    "乙": {"label": "Tanaman Lentur","traits": ["<strong>Adaptif</strong>, fleksibel, ulet",
                                                  "Tumbuh di celah, kuat secara halus",
                                                  "Mekar dengan ekspresi + akar tanah"], "fav": ["火","土"]},
    "丙": {"label": "Matahari",      "traits": ["<strong>Bersinar</strong>, ekspansif, hangat",
                                                  "Energi tinggi, perlu disalurkan ke karya nyata",
                                                  "Mekar dengan kayu (umpan) + air (penyeimbang)"], "fav": ["木","水"]},
    "丁": {"label": "Api Lilin",     "traits": ["<strong>Halus</strong>, intens, terkonsentrasi",
                                                  "Pemurnian, memberi terang yang spesifik",
                                                  "Mekar dengan kayu (umpan) + logam (cetakan)"], "fav": ["木","金"]},
    "戊": {"label": "Gunung",        "traits": ["<strong>Stabil</strong>, dapat diandalkan, tegas",
                                                  "Pondasi, orang lain bersandar pada Anda",
                                                  "Mekar dengan api (kehangatan) + logam (kanal)"], "fav": ["火","金"]},
    "己": {"label": "Tanah Subur",   "traits": ["<strong>Pengasuh</strong>, sabar, menyerap",
                                                  "Pelan tapi pasti, kekayaan terbangun bertahap",
                                                  "Mekar dengan api (matahari) + logam (alat)"], "fav": ["火","金"]},
    "庚": {"label": "Pedang",        "traits": ["<strong>Tegas</strong>, otoritatif, eksekutor",
                                                  "Logam keras, perlu dipakai, tidak disimpan",
                                                  "Mekar dengan api (penempa) + air (poles)"], "fav": ["火","水"]},
    "辛": {"label": "Logam Halus",   "traits": ["<strong>Pengrajin</strong>, presisi, perfeksionis",
                                                  "Detail tajam, keindahan dari ketelitian",
                                                  "Mekar dengan air (poles) + kayu (struktur)"], "fav": ["水","木"]},
    "壬": {"label": "Sungai Besar",  "traits": ["<strong>Pelopor</strong>, dinamis, ekspansif",
                                                  "Air mengalir, kekuatan dari pergerakan",
                                                  "Mekar dengan kayu (saluran) + api (tujuan)"], "fav": ["木","火"]},
    "癸": {"label": "Embun",         "traits": ["<strong>Pemikir</strong>, intuitif, mendalam",
                                                  "Halus tapi merembes, perubahan dari dalam",
                                                  "Mekar dengan kayu (penopang) + api (visi)"], "fav": ["木","火"]},
}

# Per-stem personality 6-axis radar + 3 cards + motto + archetype.
# Used for page_08_xingqing.html.
# axes order: top, top-right, bottom-right, bottom, bottom-left, top-left
# Each entry: (hz, pinyin, label_id, score 0-10)
# Cards: power (4 bullets), shadow (4 bullets), optimum (4 bullets)
# Motto: hz (1 char), id (Indo label), archetype (Mandarin), tag (4-char Hanzi)
XQ_PROFILES = {
    "甲": {
        "axes": [("進取","Jìnqǔ","Pelopor",9),("創新","Chuàngxīn","Inovatif",8),
                 ("領導","Lǐngdǎo","Memimpin",8),("急性","Jíxìng","Cepat panas",7),
                 ("直率","Zhíshuài","Terus-terang",7),("包容","Bāoróng","Toleran",5)],
        "motto": ("樹","Pohon Besar","本性 浩然","君子之風"),
        "power":   ["<strong>Pemimpin alami</strong>, visi jauh ke depan, berani memulai",
                    "<span class='hz'>創新精神</span> energi pelopor (Chuàng Xīn Jīng Shén)",
                    "<strong>Idealis</strong>, pegang prinsip, sulit dibengkokkan",
                    "Tegar berdiri sendiri, kekuatan internal kokoh"],
        "shadow":  ["<span class='hz'>頑固</span> keras kepala (Wán Gù), sulit kompromi",
                    "<strong>Egosentris</strong>, pandangan sendiri sering dianggap mutlak",
                    "Cepat mulai, lama menyelesaikan, perlu disiplin tahap eksekusi",
                    "<span class='hz'>急躁</span> sering tergesa, abai detail kecil"],
        "optimum": ["Peran <strong>founder / visioner</strong>, bukan eksekutor harian",
                    "Cari partner ber-<span class='hz'>金</span> (disiplin) sebagai pemangkas",
                    "Pakai <span class='hz'>火</span> (ekspresi) untuk menyalurkan energi",
                    "Tunda keputusan besar 24 jam, hindari impulsif"],
    },
    "乙": {
        "axes": [("韌性","Rènxìng","Ulet",9),("適應","Shìyìng","Adaptif",9),
                 ("同理","Tónglǐ","Empati",8),("細膩","Xìnì","Halus",7),
                 ("含蓄","Hánxù","Reserved",7),("表現","Biǎoxiàn","Ekspresi",6)],
        "motto": ("草","Tanaman Lentur","本性 柔韌","柔中帶剛"),
        "power":   ["<strong>Adaptif luar biasa</strong>, tumbuh di kondisi paling sulit",
                    "<span class='hz'>柔韌</span> kuat secara halus (Róu Rèn)",
                    "<strong>Empati tinggi</strong>, bisa baca emosi orang lain",
                    "Stamina panjang, daya tahan lebih dari kelihatannya"],
        "shadow":  ["<strong>Indecisive</strong>, terlalu banyak pertimbangan",
                    "<span class='hz'>依賴</span> mudah bergantung (Yī Lài)",
                    "Suara sendiri sering tertelan, kurang asertif",
                    "Mengakumulasi stress diam-diam, risiko burnout halus"],
        "optimum": ["Peran <strong>mediator / koordinator</strong>, penghubung tim",
                    "Bangun lingkungan stabil, Anda mekar di tanah yang aman",
                    "Latih asertivitas, suara Anda berharga, jangan dipendam",
                    "Pasangan ber-<span class='hz'>火</span>/<span class='hz'>土</span> melengkapi"],
    },
    "丙": {
        "axes": [("表現","Biǎoxiàn","Bersinar",9),("領導","Lǐngdǎo","Memimpin",8),
                 ("創新","Chuàngxīn","Inovatif",8),("急性","Jíxìng","Cepat panas",8),
                 ("直率","Zhíshuài","Terus-terang",7),("包容","Bāoróng","Toleran",7)],
        "motto": ("日","Matahari","本性 光明","光明磊落"),
        "power":   ["<strong>Karisma alami</strong>, orang tertarik mendekat",
                    "<span class='hz'>光明磊落</span> jujur terbuka (Guāng Míng Lěi Luò)",
                    "<strong>Generous</strong>, memberi tanpa pamrih",
                    "Optimis, meningkatkan mood orang sekitar"],
        "shadow":  ["<span class='hz'>急躁</span> mudah meledak (Jí Zào)",
                    "<strong>Boros</strong>, energi keluar terlalu cepat",
                    "Sulit menyembunyikan emosi, wajah jadi data publik",
                    "Bosan dengan rutinitas, perlu novelty terus"],
        "optimum": ["Peran <strong>frontman / performer</strong>, di panggung",
                    "Cari rutinitas yang punya <em>variasi terstruktur</em>",
                    "Pakai <span class='hz'>水</span> (Air) sebagai pendingin",
                    "Salurkan energi ke karya nyata, jangan idle"],
    },
    "丁": {
        "axes": [("細膩","Xìnì","Halus",9),("創新","Chuàngxīn","Inovatif",8),
                 ("表現","Biǎoxiàn","Ekspresi",8),("內斂","Nèiliǎn","Mendalam",7),
                 ("沉穩","Chénwěn","Tenang",6),("同理","Tónglǐ","Empati",7)],
        "motto": ("燭","Api Lilin","本性 溫煦","溫故知新"),
        "power":   ["<strong>Ketelitian tinggi</strong>, detail tidak luput",
                    "<span class='hz'>溫故知新</span> reflektif & memperbarui (Wēn Gù Zhī Xīn)",
                    "<strong>Kreatif halus</strong>, ide-ide dengan kedalaman",
                    "Loyal, sekali menyala, tahan lama"],
        "shadow":  ["<span class='hz'>多慮</span> banyak khawatir (Duō Lǜ)",
                    "<strong>Sensitif berlebih</strong>, terganggu oleh hal kecil",
                    "Energi terbatas, mudah lelah jika eksternal terlalu kuat",
                    "Sulit melepaskan masa lalu"],
        "optimum": ["Peran <strong>spesialis / kurator</strong>, kerja mendalam",
                    "Bangun lingkungan tenang & terjaga",
                    "Pakai <span class='hz'>木</span> (Kayu) sebagai umpan kreativitas",
                    "Latih meditasi, pikiran perlu jeda terstruktur"],
    },
    "戊": {
        "axes": [("穩重","Wěnzhòng","Stabil",9),("包容","Bāoróng","Toleran",8),
                 ("守信","Shǒuxìn","Dapat dipercaya",8),("務實","Wùshí","Praktis",8),
                 ("沉穩","Chénwěn","Tenang",7),("創新","Chuàngxīn","Inovatif",4)],
        "motto": ("山","Gunung","本性 厚重","厚德載物"),
        "power":   ["<strong>Pondasi yang kokoh</strong>, orang lain bersandar pada Anda",
                    "<span class='hz'>守信用</span> dapat dipercaya (Shǒu Xìn Yòng)",
                    "<strong>Sabar</strong>, bisa menunggu hasil bertahun-tahun",
                    "Pragmatis, solusi nyata, bukan teori"],
        "shadow":  ["<span class='hz'>固執</span> kepala batu (Gù Zhí), sulit berubah",
                    "<strong>Lambat beradaptasi</strong> dengan ide baru",
                    "Konservatif, peluang inovatif kerap dilewatkan",
                    "Akumulasi (uang, barang, beban) cenderung berlebih"],
        "optimum": ["Peran <strong>arsitek / pembangun jangka panjang</strong>",
                    "Buka diri ke <span class='hz'>火</span> (kehangatan) dan <span class='hz'>金</span> (kanal)",
                    "Latih perubahan kecil rutin, anti-stagnasi",
                    "Investasi properti & aset nyata, sesuai natur Anda"],
    },
    "己": {
        "axes": [("包容","Bāoróng","Toleran",9),("同理","Tónglǐ","Empati",8),
                 ("韌性","Rènxìng","Ulet",8),("守信","Shǒuxìn","Dapat dipercaya",7),
                 ("沉穩","Chénwěn","Tenang",7),("變通","Biàntōng","Fleksibel",6)],
        "motto": ("田","Tanah Subur","本性 慈悲","厚德育物"),
        "power":   ["<strong>Pengasuh alami</strong>, menyuburkan orang sekitar",
                    "<span class='hz'>慈悲心</span> welas asih tinggi (Cí Bēi Xīn)",
                    "<strong>Sabar luar biasa</strong>, proses pelan tapi pasti",
                    "Loyal & dapat dipercaya, andalan jangka panjang"],
        "shadow":  ["<strong>Mudah mengalah</strong>, kepentingan diri terabaikan",
                    "<span class='hz'>多愁善感</span> mudah tersentuh negatif",
                    "Lambat eksekusi keputusan besar",
                    "Mengakumulasi beban orang lain, risiko burnout"],
        "optimum": ["Peran <strong>pelatih / mentor / pengasuh</strong>",
                    "Latih <em>katakan tidak</em> tanpa rasa bersalah",
                    "Pakai <span class='hz'>火</span> (matahari) + <span class='hz'>金</span> (alat)",
                    "Buat batas waktu untuk diri sendiri"],
    },
    "庚": {
        "axes": [("剛硬","Gāngyìng","Tegas",9),("領導","Lǐngdǎo","Memimpin",8),
                 ("直率","Zhíshuài","Terus-terang",8),("進取","Jìnqǔ","Pelopor",8),
                 ("急性","Jíxìng","Cepat panas",7),("細膩","Xìnì","Halus",4)],
        "motto": ("劍","Pedang","本性 剛健","剛健中正"),
        "power":   ["<strong>Eksekutor tegas</strong>, keputusan cepat & jelas",
                    "<span class='hz'>剛正不阿</span> tidak bisa ditekuk (Gāng Zhèng Bù ē)",
                    "<strong>Berani</strong>, menghadapi konflik tanpa gentar",
                    "Loyal pada janji & sahabat sejati"],
        "shadow":  ["<span class='hz'>過剛易折</span> terlalu kaku mudah patah",
                    "<strong>Kurang sabar</strong> dengan proses lambat",
                    "Bicara tajam, sering melukai tanpa sadar",
                    "Sulit menerima kritik dari posisi lebih rendah"],
        "optimum": ["Peran <strong>komandan / eksekutor / hakim</strong>",
                    "Pakai <span class='hz'>火</span> (api penempa) + <span class='hz'>水</span> (poles)",
                    "Latih empati, dengarkan sebelum memvonis",
                    "Tantangan keras = nutrisi Anda; hindari medan datar"],
    },
    "辛": {
        "axes": [("細膩","Xìnì","Halus",9),("剛硬","Gāngyìng","Tegas",8),
                 ("表現","Biǎoxiàn","Ekspresi",7),("急性","Jíxìng","Cepat panas",7),
                 ("創新","Chuàngxīn","Inovatif",7),("包容","Bāoróng","Toleran",5)],
        "motto": ("玉","Logam Halus","本性 精緻","精益求精"),
        "power":   ["<strong>Pengrajin presisi</strong>, detail tajam terkurasi",
                    "<span class='hz'>精益求精</span> selalu berusaha lebih baik",
                    "<strong>Eksklusif</strong>, kualitas di atas kuantitas",
                    "Estetika tinggi, selera halus & elegan"],
        "shadow":  ["<span class='hz'>主觀</span> subjektif, sudut pandang sempit",
                    "<strong>Perfeksionis</strong>, sulit selesai/lepas",
                    "Sensitif terhadap kritik personal",
                    "<span class='hz'>缺緩衝</span> bicara terlalu tajam"],
        "optimum": ["Peran <strong>kurator / spesialis / advisor</strong>",
                    "Pakai <span class='hz'>水</span> (Air) sebagai pendingin sebelum bicara",
                    "Bangun standar realistis, selesai > sempurna",
                    "Anggap kritik = data, bukan serangan"],
    },
    "壬": {
        "axes": [("創新","Chuàngxīn","Inovatif",9),("變通","Biàntōng","Fleksibel",9),
                 ("表現","Biǎoxiàn","Ekspresi",8),("領導","Lǐngdǎo","Memimpin",7),
                 ("急性","Jíxìng","Cepat panas",7),("包容","Bāoróng","Toleran",6)],
        "motto": ("江","Sungai Besar","本性 浩瀚","海納百川"),
        "power":   ["<strong>Pelopor dinamis</strong>, selalu mencari arus baru",
                    "<span class='hz'>海納百川</span> menampung perspektif beragam",
                    "<strong>Networker</strong>, mudah bergerak antar lingkaran",
                    "Adaptif & cepat baca peluang"],
        "shadow":  ["<span class='hz'>多變</span> mudah berubah (Duō Biàn)",
                    "<strong>Sulit fokus</strong>, terlalu banyak pintu terbuka",
                    "Komitmen jangka panjang sering kompromi",
                    "Energi keluar tanpa wadah → boros"],
        "optimum": ["Peran <strong>strategist / penghubung lintas-domain</strong>",
                    "Bangun <em>satu</em> wadah jangka panjang sebagai jangkar",
                    "Pakai <span class='hz'>木</span> (saluran) + <span class='hz'>火</span> (tujuan)",
                    "Komitmen kontrak tertulis, anti-drift halus"],
    },
    "癸": {
        "axes": [("細膩","Xìnì","Halus",9),("變通","Biàntōng","Fleksibel",8),
                 ("同理","Tónglǐ","Empati",8),("內斂","Nèiliǎn","Mendalam",7),
                 ("創新","Chuàngxīn","Inovatif",7),("韌性","Rènxìng","Ulet",7)],
        "motto": ("露","Embun","本性 柔慧","水滴石穿"),
        "power":   ["<strong>Pemikir mendalam</strong>, wawasan halus",
                    "<span class='hz'>水滴石穿</span> halus tapi merembes (Shuǐ Dī Shí Chuān)",
                    "<strong>Empati intuitif</strong>, paham tanpa kata",
                    "Bertahan diam-diam, daya tahan psikis tinggi"],
        "shadow":  ["<span class='hz'>過慮</span> overthinking",
                    "<strong>Tertutup</strong>, menyimpan terlalu banyak sendiri",
                    "Mudah cemas akan masa depan",
                    "Energi terbatas, terkuras oleh lingkungan riuh"],
        "optimum": ["Peran <strong>penasihat / peneliti / penulis</strong>",
                    "Bangun ritme tenang, pagi & malam reflektif",
                    "Pakai <span class='hz'>木</span> (penopang) + <span class='hz'>火</span> (visi)",
                    "Salurkan kontemplasi ke output (tulisan, seni)"],
    },
}


# 6-axis radar geometry: center (200,200), 6 axes at 60° spacing
# Original LinRuYi axis endpoints (for reference): top 200,40 / TR 339,120 / BR 339,280
#  / bot 200,360 / BL 61,280 / TL 61,120
XQ_AXES_ENDPOINTS = [
    (200, 40),   # top
    (339, 120),  # top-right
    (339, 280),  # bottom-right
    (200, 360),  # bottom
    (61, 280),   # bottom-left
    (61, 120),   # top-left
]
XQ_LABEL_POSITIONS = [
    (200, 22),  (358, 113), (358, 290), (200, 382), (42, 290), (42, 113)
]
XQ_MAX = 10.0


def _build_xqcards_from_profile(p: dict) -> str:
    """Generate the inner HTML for the 3 personality cards from a profile dict."""
    if not p or not p.get("power"):
        return ""
    def card(klass, eb_hz, eb_id, title_hz, title_id, items):
        items_html = "\n".join(
            f'          <div class="xqc-item"><span class="ico">◆</span><span>{x}</span></div>'
            for x in items
        )
        return (
            f'      <div class="xq-card {klass}">\n'
            f'        <div class="xqc-eb">{eb_hz} · {eb_id}</div>\n'
            f'        <div class="xqc-title"><span class="xqc-hz">{title_hz}</span><span class="xqc-name">{title_id}</span></div>\n'
            f'        <div class="xqc-list">\n{items_html}\n        </div>\n'
            f'      </div>'
        )
    return (
        '\n' + card("power",   "魄 力", "Kekuatan", "優勢",   "Yōu Shì<br>Keunggulan", p["power"]) + '\n'
        + card("shadow",  "陰 影", "Shadow",   "隱 患",  "Yǐn Huàn<br>Sisi Gelap", p["shadow"]) + '\n'
        + card("optimum", "最 佳", "Optimum",  "應 用",   "Yīng Yòng<br>Cara Optimal", p["optimum"]) + '\n    '
    )


def _regen_xq_radar_from_profile(p: dict) -> tuple[str, str, tuple]:
    """Return (polygon+dots_html, labels_html, motto_4tuple) for personality radar."""
    if not p or not p.get("axes") or not p.get("motto"):
        return "", "", ("", "", "", "")
    cx, cy = 200, 200
    pts = []
    for (ex, ey), (hz, py, lid, score) in zip(XQ_AXES_ENDPOINTS, p["axes"]):
        t = score / XQ_MAX
        x = cx + (ex - cx) * t
        y = cy + (ey - cy) * t
        pts.append((x, y))
    pts_str = " ".join(f"{x:g},{y:g}" for x, y in pts)
    poly = (
        f'          <polygon points="{pts_str}"\n'
        f'            fill="rgba(139,26,26,0.18)" stroke="#8B1A1A" stroke-width="1.5"/>'
    )
    dots = "\n".join(
        f'          <circle cx="{x:g}" cy="{y:g}" r="3" fill="#8B1A1A"/>'
        for x, y in pts
    )
    poly_html = poly + "\n" + dots

    # Labels
    label_parts = []
    for (lx, ly), (hz, py, lid, score) in zip(XQ_LABEL_POSITIONS, p["axes"]):
        label_parts.append(
            f'            <text x="{lx}" y="{ly}" text-anchor="middle" font-size="14" fill="#8B1A1A" font-weight="700">{hz}</text>\n'
            f'            <text x="{lx}" y="{ly+11}" text-anchor="middle" font-size="6" fill="#6B5B3F" font-style="italic">{py} · {lid} · {score}</text>'
        )
    labels_html = '          <g font-family="Noto Serif TC,serif">\n' + "\n\n".join(label_parts) + "\n          </g>"

    return poly_html, labels_html, p["motto"]


EL_HZ = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
EL_ID = {"木":"Kayu","火":"Api","土":"Tanah","金":"Logam","水":"Air"}
PINYIN = {"甲":"Jiǎ","乙":"Yǐ","丙":"Bǐng","丁":"Dīng","戊":"Wù","己":"Jǐ","庚":"Gēng","辛":"Xīn","壬":"Rén","癸":"Guǐ"}


# Element descriptors for ji_shen / yong_shen body auto-generate
ELEMENT_PROFILE = {
    "金": {"id": "Logam", "pinyin": "Jīn",
           "fav_text": "kanal yang menyalurkan energi berlebih jadi karya, sumber disiplin & struktur",
           "ji_text": "Logam tajam yang dapat melukai bila terlalu dominan; hindari lingkungan terlalu kaku, hierarkis, dan kompetitif berlebih"},
    "水": {"id": "Air", "pinyin": "Shuǐ",
           "fav_text": "pendingin & adaptasi; mengalirkan kekuatan jadi pergerakan",
           "ji_text": "Air berlebih dapat menggerus pondasi; hindari emosi mendung berkepanjangan, basah/lembap, dan keputusan impulsif"},
    "木": {"id": "Kayu", "pinyin": "Mù",
           "fav_text": "pertumbuhan, idealisme, dan kreativitas yang menumbuhkan",
           "ji_text": "Kayu berlebih menyedot energi inti; hindari hijau dominan, terlalu banyak proyek baru, dan kepalanya keras"},
    "火": {"id": "Api", "pinyin": "Huǒ",
           "fav_text": "kehangatan, ekspresi, dan visibilitas; menyalurkan energi ke karya nyata",
           "ji_text": "Api berlebih membakar habis sumber daya; hindari merah-jingga dominan, panas/kering, dan reaksi cepat tanpa pendinginan"},
    "土": {"id": "Tanah", "pinyin": "Tǔ",
           "fav_text": "pondasi, ketenangan, dan akumulasi yang stabil",
           "ji_text": "Tanah berlebih membuat stagnasi; hindari berat/lembam, kebiasaan menumpuk, dan resisten terhadap perubahan"},
}


def build_yong_shen_body(subject: dict) -> str:
    """Generate yong_shen body HTML from yong_shen.elements_hz (rumus auto)."""
    ys = subject.get("yong_shen") or {}
    el_hz = ys.get("elements_hz", "")
    elements = [e for e in el_hz.split() if e in ELEMENT_PROFILE]
    if not elements:
        return ""
    parts = []
    for el in elements:
        p = ELEMENT_PROFILE[el]
        parts.append(f'<strong>{el}</strong> ({p["pinyin"]} · {p["id"]}), {p["fav_text"]}.')
    return " ".join(parts)


def build_ji_shen_body(subject: dict) -> str:
    """Generate ji_shen body HTML from ji_shen.elements_hz (rumus auto)."""
    js = subject.get("ji_shen") or {}
    el_hz = js.get("elements_hz", "")
    elements = [e for e in el_hz.split() if e in ELEMENT_PROFILE]
    if not elements:
        return ""
    parts = []
    for el in elements:
        p = ELEMENT_PROFILE[el]
        parts.append(f'<strong>{el}</strong> ({p["pinyin"]} · {p["id"]}), {p["ji_text"]}.')
    return " ".join(parts)


def build_dmcard_html(subject: dict) -> str:
    """Generate the inner HTML of the dm-card on page 6 from day master."""
    dm = subject.get("day_master") or {}
    stem = dm.get("stem_hz", "")
    profile = DM_PROFILES.get(stem)
    if not profile:
        return ""  # unknown stem, keep template default
    el_hz = EL_HZ[stem]
    el_id = EL_ID[el_hz]
    polarity = "Yang" if stem in "甲丙戊庚壬" else "Yin"
    pinyin = PINYIN[stem]
    strength = dm.get("strength_hz", "旺")
    strength_id = "KUAT" if strength == "旺" else "LEMAH"
    traits_html = "\n".join(
        f'          <div class="dmc-trait"><span class="ico">◆</span><span>{t}</span></div>'
        for t in profile["traits"]
    )
    return (
        f'\n        <div class="dmc-eyebrow">本 命 · Penguasa Hari</div>\n'
        f'        <div class="dmc-stem">{stem}</div>\n'
        f'        <div class="dmc-element">{el_hz} · {el_id} {polarity}</div>\n'
        f'        <div class="dmc-pinyin">{pinyin} {el_hz}, "{profile["label"]}"</div>\n'
        f'        <div class="dmc-traits">\n{traits_html}\n        </div>\n'
        f'        <div class="dmc-strength">Status: <span class="val">{strength_id}</span> · {strength}</div>\n      '
    )


def inject_dayun_overrides(subject: dict, tafsir_blocks: dict):
    """Override subject.da_yun.* with MD-derived narrative."""
    da_yun = subject.get("da_yun") or {}

    # Footer caption (used in all 14 page footers via render.py substitution)
    footer = tafsir_blocks.get("dayun_footer")
    if footer:
        da_yun["footer_caption_html"] = footer

    # Spotlight: extract headline + bullets from tafsir HTML
    spot = tafsir_blocks.get("dayun_spotlight", "")
    if spot:
        m_head = re.search(r'<div class="sp-headline">(.+?)</div>', spot, re.DOTALL)
        if m_head:
            da_yun["spotlight_headline_html"] = m_head.group(1).strip()
        m_bul = re.findall(r"<li>(.+?)</li>", spot, re.DOTALL)
        if m_bul:
            da_yun["spotlight_bullets_html"] = [b.strip() for b in m_bul]

    # 5 Seasons: parse "umur X-Y: Nama, kalimat" and override seasons[i].name_id
    seasons_html = tafsir_blocks.get("dayun_seasons", "")
    if seasons_html and da_yun.get("seasons"):
        # Extract <li>...</li>
        items = re.findall(r"<li>(.+?)</li>", seasons_html, re.DOTALL)
        for i, item in enumerate(items):
            if i >= len(da_yun["seasons"]):
                break
            # Strip HTML tags, parse "umur a-b: Name, sentence"
            plain = re.sub(r"<[^>]+>", "", item)
            # Extract season name (between "umur X-Y:" and "—")
            m = re.search(r"umur\s+\d+\s*-\s*\d+\s*:\s*(.+?)\s*[—\-]\s*(.+)", plain)
            if m:
                da_yun["seasons"][i]["name_id"] = m.group(1).strip()
                # Optional: store sentence too if we want to use it elsewhere
                da_yun["seasons"][i]["caption_id"] = m.group(2).strip()

    subject["da_yun"] = da_yun


def generate_quality_report(ocr: dict, subject: dict) -> str:
    """Generate user-friendly Indonesian quality report after PDF build.
    Output: tabel halaman bermasalah saja (skip halaman OK).
    Bahasa simpel, no jargon — untuk user awam non-teknis.
    Mapping: foto layar critical (Hanzi + Indo translation) → halaman PDF impact.
    """
    issues = []  # list of (page, status, reason)

    # ─── PAGE 1 (Cover) ───
    page1_problems = []
    # gender_hz check from ocr (foto-source). Valid: 陽男/陰男/陽女/陰女.
    gender_hz = ocr.get("gender_hz")
    if gender_hz not in ("陽男", "陰男", "陽女", "陰女"):
        page1_problems.append(
            "Foto info polaritas gender (陽男 / 陰男 / 陽女 / 陰女 = "
            "Pria Yang / Pria Yin / Wanita Yang / Wanita Yin) tidak terbaca jelas"
        )
    if page1_problems:
        issues.append(("1 (Cover)", "🟡 Perlu Cek", "; ".join(page1_problems)))

    # ─── PAGE 4 (Profil) ───
    if not ocr.get("dm_pos_score") or not ocr.get("dm_neg_score"):
        issues.append((
            "4 (Profil)", "🔴 Kosong",
            "Foto Catatan Skor Kekuatan (批命備註) belum ada / tidak terbaca jelas. "
            "Bagian Skor Kekuatan DM (angka pendukung & penekan) kosong"
        ))

    # ─── PAGE 6 (Day Master) ───
    page6_problems = []
    if not ocr.get("ti_xiang"):
        page6_problems.append(
            "Foto kolom Status Musim 5 Elemen (體相) tidak terbaca jelas → "
            "lingkaran kecil di sudut 5 kartu elemen tidak muncul"
        )
    if not ocr.get("dm_strength_hz") and not ocr.get("dm_strength_label_id"):
        page6_problems.append(
            "Status DM (Lemah / Kuat / Seimbang) kosong dari foto Catatan Skor"
        )
    # 5-Shen extended (xi_yong/xian/chou) — kalau 2+ missing, flag
    missing_5shen = sum(1 for k in ("xi_yong_shen_hz", "xian_shen_hz", "chou_shen_hz") if not ocr.get(k))
    if missing_5shen >= 2:
        page6_problems.append(
            "Foto 5-Shen lengkap (喜用神 / 閒神 / 仇神 = Pendukung Utama / Netral / Pengganggu) "
            "tidak terbaca jelas"
        )
    if page6_problems:
        issues.append(("6 (Day Master)", "🔴 Kosong", "; ".join(page6_problems)))

    # ─── PAGE 10 (Bintang Pelengkap) ───
    ssl = ocr.get("shen_sha_list")
    if not ssl or (isinstance(ssl, list) and len(ssl) == 0):
        issues.append((
            "10 (Bintang Pelengkap)", "🔴 Kosong",
            "Foto Bintang Pelengkap (神煞) belum ada / tidak terbaca jelas. "
            "Grid 8 kartu bintang kosong semua"
        ))

    # ─── Output ───
    if not issues:
        return (
            "\n" +
            "=" * 67 + "\n"
            " ✅ Semua bagian PDF terisi penuh — kualitas foto sumber bagus.\n"
            + "=" * 67
        )

    # Build markdown table
    lines = []
    lines.append("")
    lines.append("=" * 67)
    lines.append(" 📋 LAPORAN KUALITAS EKSTRAKSI")
    lines.append("=" * 67)
    lines.append("")
    lines.append(" Halaman Yang Punya Potensi Salah Karena Kualitas Foto Kurang Baik:")
    lines.append("")
    lines.append(" | Halaman | Status | Kenapa Bermasalah |")
    lines.append(" |---------|--------|-------------------|")
    for page, status, reason in issues:
        lines.append(f" | {page} | {status} | {reason} |")
    lines.append("")
    lines.append(" 💡 Saran: screenshot ulang dari software BaZi untuk layar yang")
    lines.append("    disebut di atas, lalu kirim ke window baru untuk render ulang.")
    lines.append("")
    lines.append(" (Halaman lain tampil normal sesuai data yang tersedia.)")
    lines.append("=" * 67)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_pdf.py <subject_id> "
              "[--name X --hanzi 漢字 --gender Pria --date YYYY-MM-DD --time HH:MM] "
              "[--md path/to/file.md]")
        sys.exit(1)

    subject_id = sys.argv[1]
    args = sys.argv[2:]
    kw = {}
    md_override = None
    no_pdf = False
    for i, a in enumerate(args):
        if a == "--name" and i+1 < len(args): kw["name_id"] = args[i+1]
        elif a == "--hanzi" and i+1 < len(args): kw["name_hanzi"] = args[i+1]
        elif a == "--gender" and i+1 < len(args): kw["gender_id"] = args[i+1]
        elif a == "--date" and i+1 < len(args): kw["birth_date"] = args[i+1]
        elif a == "--time" and i+1 < len(args): kw["birth_time"] = args[i+1]
        elif a == "--md" and i+1 < len(args): md_override = Path(args[i+1])
        elif a == "--no-pdf": no_pdf = True

    t0 = time.time()

    # ---------- Step 0: Detect MD mode ----------
    md_path = md_override or find_md_for_subject(subject_id)
    tafsir_blocks: dict = {}
    if md_path and md_path.exists():
        print(f"=== Step 0: MD mode, parsing {md_path.name} ===")
        ocr_data, tafsir_blocks, warns = parse_md(md_path)
        print(f"   Tafsir blocks: {len(tafsir_blocks)}")
        if warns:
            print("   Warnings:")
            for w in warns:
                print(f"     ⚠ {w}")
        # Write ocr.json from parsed MD (overwrites any existing)
        ocr_path = DATA_DIR / f"{subject_id}.ocr.json"
        ocr_path.write_text(json.dumps(ocr_data, ensure_ascii=False, indent=2),
                            encoding="utf-8")
        print(f"   Wrote {ocr_path.name}")
    else:
        print(f"=== Step 0: Legacy mode, using {subject_id}.ocr.json ===")

    # ---------- Step 1: Build subject.json ----------
    print(f"\n=== Step 1: Build {subject_id}.json from {subject_id}.ocr.json ===")
    subject = build_subject_from_ocr(subject_id, **kw)
    t1 = time.time()
    print(f"   Build: {t1-t0:.1f}s")

    # ---------- Step 1.5: DM cross-check + inject MD overrides ----------
    # Always rebuild dm-card from native day master (template hardcode is broken)
    dmcard = build_dmcard_html(subject)
    if dmcard:
        tafsir_blocks["_dmcard"] = dmcard
    # FULL-MD MODE: prefer MD `_jishen_body` (from TAFSIR daymaster ji_shen_body sub-field).
    # Fallback ke engine auto-generate kalau MD tidak provide.
    if not tafsir_blocks.get("_jishen_body"):
        jisbody = build_ji_shen_body(subject)
        if jisbody:
            tafsir_blocks["_jishen_body"] = jisbody

    # Family 4 cards (page 9): inject vibe/headline/body per sub-card
    fam = tafsir_blocks.get("_family_struct") or {}
    from parse_md import md_inline as _md_inline
    # Backward compat: accept "saudari" as alias for "saudara"
    if "saudari" in fam and "saudara" not in fam:
        fam["saudara"] = fam["saudari"]
    for key in ("pasangan", "anak", "saudara", "kepemimpinan"):
        card = fam.get(key) or {}
        for field in ("vibe", "headline", "body"):
            v = card.get(field)
            if v:
                tafsir_blocks[f"fam_{key}_{field}"] = _md_inline(v)

    # Caifu (page 11): 2 cards percent+body, 4 rules
    cf = tafsir_blocks.get("_caifu_struct") or {}
    for key, slug_prefix in [("zheng_cai", "caifu_zheng"), ("pian_cai", "caifu_pian")]:
        card = cf.get(key) or {}
        if card.get("percent"):
            pct = card["percent"].strip()
            # extract digits for width
            import re as _re
            m_pct = _re.search(r"(\d+(?:\.\d+)?)", pct)
            width = m_pct.group(1) if m_pct else "0"
            tafsir_blocks[f"{slug_prefix}_gauge"] = (
                f'<div class="cfm-gauge-fill" style="width:{width}%">{pct}</div>'
            )
        if card.get("body"):
            tafsir_blocks[f"{slug_prefix}_body"] = _md_inline(card["body"])
    rules = cf.get("rules") or []
    if rules:
        items = []
        for i, r in enumerate(rules[:4], 1):
            tone = r.get("tone", "").lower()
            klass = "tip" if tone == "tip" else ("warn" if tone == "warn" else "")
            klass_attr = f" {klass}" if klass else ""
            items.append(
                f'        <div class="cf-rule{klass_attr}">\n'
                f'          <div class="cfr-num">{i}</div>\n'
                f'          <div class="cfr-content">\n'
                f'            <div class="cfr-title">{_md_inline(r.get("title",""))}</div>\n'
                f'            <div class="cfr-context">{_md_inline(r.get("context",""))}</div>\n'
                f'          </div>\n'
                f'        </div>'
            )
        tafsir_blocks["_caifu_rules"] = "\n" + "\n".join(items) + "\n"

    # Zi Wei star Indonesian lookup (14 main + common support stars)
    ZW_STAR_ID = {
        "紫微":"Pemimpin Agung","天機":"Strategi","太陽":"Matahari","武曲":"Disiplin Material",
        "天同":"Harmoni","廉貞":"Integritas","天府":"Lumbung","太陰":"Bulan/Intuisi",
        "貪狼":"Hasrat","巨門":"Pintu Besar","天相":"Penolong","天梁":"Pelindung",
        "七殺":"Pemurnian","破軍":"Pembongkar",
        "文昌":"Akademik","文曲":"Komunikasi","左輔":"Mentor Kiri","右弼":"Mentor Kanan",
        "天魁":"Penolong Pria","天鉞":"Penolong Wanita","祿存":"Penjaga Rezeki",
        "火星":"Gerak Cepat","鈴星":"Tekanan","擎羊":"Pisau","陀羅":"Beban",
        "化祿":"Berkah","化權":"Otoritas","化科":"Reputasi","化忌":"Halangan",
        "天馬":"Mobilitas","紅鸞":"Asmara","天喜":"Sukacita","華蓋":"Naungan",
    }

    # Palace pages (17/18/19): generate full palace card content from MD struct
    # Each tuple: (slug, hanzi, pinyin, indonesian)
    PALACE_PAGES = [
        ("p1", "_palace1_struct", [
            ("ming_gong", "命宮", "Mìng Gōng", "Diri"),
            ("xiongdi", "兄弟", "Xiōng Dì", "Saudara"),
            ("fuqi", "夫妻", "Fū Qī", "Pasangan"),
            ("zinu", "子女", "Zǐ Nǚ", "Anak"),
        ]),
        ("p2", "_palace2_struct", [
            ("caibo", "財帛", "Cái Bó", "Rezeki"),
            ("jie_e", "疾厄", "Jí È", "Kesehatan"),
            ("qianyi", "遷移", "Qiān Yí", "Perpindahan"),
            ("puyi", "僕役", "Pú Yì", "Pertemanan"),
        ]),
        ("p3", "_palace3_struct", [
            ("guanlu", "官祿", "Guān Lù", "Karir"),
            ("tianzhai", "田宅", "Tián Zhái", "Properti"),
            ("fude", "福德", "Fú Dé", "Berkah"),
            ("fumu", "父母", "Fù Mǔ", "Orang Tua"),
        ]),
    ]
    for page_key, struct_key, palaces in PALACE_PAGES:
        struct = tafsir_blocks.get(struct_key) or {}
        for slug, hz, pinyin, id_label in palaces:
            data = struct.get(slug) or {}
            insight = data.get("insight", "")
            action = data.get("action", "")
            insight_html = f'<div class="pal-body">{_md_inline(insight)}</div>' if insight else ""
            action_html = ""
            if action:
                action_html = (
                    f'<div class="pal-actions">'
                    f'<div class="pal-actions-header">Saran Tindakan</div>'
                    f'<div class="pal-action"><span class="ico">▸</span><span>{_md_inline(action)}</span></div>'
                    f'</div>'
                )
            # Header: Indonesian (big red) on top, pinyin · hanzi (small) below
            head = (
                f'<div class="pal-head"><div class="pal-name">'
                f'<span class="pn-id">{id_label}</span>'
                f'<span class="pn-meta">{pinyin}<span class="hz">{hz}</span></span>'
                f'</div></div>'
            )
            tafsir_blocks[f"_{page_key}_{slug}"] = head + insight_html + action_html

    def _html_amp(s: str) -> str:
        return (s or "").replace("&", "&amp;")

    # Kesimpulan struct from MD (overrides default desc + life_map)
    kes_md = tafsir_blocks.get("_kesimpulan_struct") or {}
    kes_stats_md = kes_md.get("stats") or {}
    kes_lifemap_md = kes_md.get("life_map") or {}

    def _desc_or_default(key: str, default: str) -> str:
        v = kes_stats_md.get(key)
        return _md_inline(v) if v else default

    # Kesimpulan (page 20): 6 stat cards rebuild from rumus
    # FULL-MD MODE: normalize subject so None → "—" before card builders that
    # call .upper(), f-string format, etc. (otherwise crash on None DM strength,
    # null format, null marriage, etc. from MD-only mode).
    subject = _normalize_subject_for_render(subject)
    iden = subject.get("identity") or {}
    dm = subject.get("day_master") or {}
    fmt = subject.get("format") or {}
    ys_data = subject.get("yong_shen") or {}
    js_data = subject.get("ji_shen") or {}
    da_yun = subject.get("da_yun") or {}
    cycles = da_yun.get("cycles") or []
    cur_idx = da_yun.get("current_index", 0)
    cur_cycle = cycles[cur_idx] if cycles and cur_idx < len(cycles) else {}
    yz = subject.get("yang_zhai") or {}
    marriage = subject.get("marriage") or {}

    # Card 1: Penguasa Hari
    dm_hz = f'{dm.get("stem_hz","")}{dm.get("stem_element_hz","")}'
    dm_strength = dm.get("strength_id", "")
    dm_strength_hz = dm.get("strength_hz", "")
    wuxing = subject.get("wuxing") or {}
    wx_total = wuxing.get("total", 0)
    dm_pct = 0
    if dm.get("stem_element_hz"):
        EL_KEY = {"金":"jin","水":"shui","木":"mu","火":"huo","土":"tu"}
        k = EL_KEY.get(dm.get("stem_element_hz",""), "")
        dm_pct = (wuxing.get(k) or {}).get("percent", 0)
    card1_default_desc = f'Total Wu Xing {wx_total:g}, {dm.get("stem_element_hz","")} <strong>{dm_pct:.1f}%</strong> dari distribusi total'
    card1 = (
        f'<div class="kes-stat s1">'
        f'<div class="ks-eb">Penguasa Hari · 日主</div>'
        f'<div class="ks-num"><span class="hz">{dm_hz}</span><span class="unit">{dm_strength.upper()} · {dm_strength_hz}</span></div>'
        f'<div class="ks-title">{_html_amp(dm.get("label_id",""))} {dm_strength}</div>'
        f'<div class="ks-desc">{card1_default_desc}</div>'
        f'</div>'
    )

    # Card 2: Format
    card2 = (
        f'<div class="kes-stat s2">'
        f'<div class="ks-eb">Format · 格局</div>'
        f'<div class="ks-num"><span class="hz">{fmt.get("hz","")}</span><span class="unit">FORMAT</span></div>'
        f'<div class="ks-title">{fmt.get("pinyin","")}, {_html_amp(fmt.get("label_id",""))}</div>'
        f'<div class="ks-desc">{_desc_or_default("format_desc", "Konfigurasi BaZi yang membentuk pola karakter dan jalur takdir utama subjek.")}</div>'
        f'</div>'
    )

    # Card 3: Yong Shen
    card3 = (
        f'<div class="kes-stat s3">'
        f'<div class="ks-eb">Yong Shen · 喜用神</div>'
        f'<div class="ks-num"><span class="hz">{ys_data.get("elements_hz","")}</span><span class="unit">MENDUKUNG</span></div>'
        f'<div class="ks-title">{_html_amp(ys_data.get("elements_id",""))}, {_html_amp(ys_data.get("label_id",""))}</div>'
        f'<div class="ks-desc">{_desc_or_default("yong_desc", "Unsur penopang yang sebaiknya diaktifkan lewat lingkungan, profesi, warna, dan keputusan hidup.")}</div>'
        f'</div>'
    )

    # Card 4: Da Yun
    cur_age = f'{cur_cycle.get("age_start","")}-{cur_cycle.get("age_end","")}' if cur_cycle else ""
    cur_gz = f'{cur_cycle.get("stem_hz","")}{cur_cycle.get("branch_hz","")}' if cur_cycle else ""
    cur_tg = cur_cycle.get("ten_god_id","") if cur_cycle else ""
    cur_tg_hz = cur_cycle.get("ten_god_hz","") if cur_cycle else ""
    # Indonesian translation for stem-branch + ten god
    STEM_ID = {"甲":"Kayu Yang","乙":"Kayu Yin","丙":"Api Yang","丁":"Api Yin","戊":"Tanah Yang","己":"Tanah Yin","庚":"Logam Yang","辛":"Logam Yin","壬":"Air Yang","癸":"Air Yin"}
    BRANCH_ID = {"子":"Tikus","丑":"Kerbau","寅":"Macan","卯":"Kelinci","辰":"Naga","巳":"Ular","午":"Kuda","未":"Kambing","申":"Monyet","酉":"Ayam","戌":"Anjing","亥":"Babi"}
    cur_stem_hz = cur_cycle.get("stem_hz","") if cur_cycle else ""
    cur_br_hz = cur_cycle.get("branch_hz","") if cur_cycle else ""
    cur_gz_id = f'{STEM_ID.get(cur_stem_hz,"")} {BRANCH_ID.get(cur_br_hz,"")}'.strip()
    card4 = (
        f'<div class="kes-stat s4">'
        f'<div class="ks-eb">Da Yun · 大運</div>'
        f'<div class="ks-num">Fase {cur_idx+1}<span class="unit">dari 10</span></div>'
        f'<div class="ks-title">Fase {cur_tg} ({cur_age})</div>'
        f'<div class="ks-desc">{_desc_or_default("dayun_desc", "Cycle 10 tahun yang sedang dijalani, periode pembentukan tema utama dekade ini.")}</div>'
        f'</div>'
    )

    # Card 5: Da Xian (Zi Wei), fallback ke umur saat ini palace dengan range
    age = iden.get("age_at_report", 0)
    # Approximate da xian based on age, we don't have full Zi Wei compute, use age range
    age_decade_start = (age // 10) * 10
    if age_decade_start < 10:
        age_decade_start = 6
    age_decade_end = age_decade_start + 9
    card5 = (
        f'<div class="kes-stat s5">'
        f'<div class="ks-eb">Umur Subjek</div>'
        f'<div class="ks-num">{age}<span class="unit">tahun</span></div>'
        f'<div class="ks-title">Era {age_decade_start}–{age_decade_end}</div>'
        f'<div class="ks-desc">{_desc_or_default("umur_desc", "Tahap kehidupan saat laporan ini dibuat, rentang dekade aktif subjek.")}</div>'
        f'</div>'
    )

    # Card 6: Kompatibilitas + Yang Zhai
    def _branch_with_id(items):
        return " · ".join(
            f'{BRANCH_ID.get(item.get("branch_hz",""), "")} ({item.get("branch_hz","")})'
            for item in items
        )
    cocok_str = _branch_with_id(marriage.get("cocok",[]))
    hindari_str = _branch_with_id(marriage.get("hindari",[]))
    gua_hz = yz.get("gua_hz", "?")
    gua_label = yz.get("gua_label_id", "")
    group = yz.get("group_id", "")
    card6_default_desc = (
        f'Hindari: {hindari_str} · '
        f'Trigram <strong>{gua_label}</strong> ({gua_hz}) · Kelompok {group}'
    )
    card6 = (
        f'<div class="kes-stat s6">'
        f'<div class="ks-eb">Jodoh · 婚配 / 陽宅</div>'
        f'<div class="ks-num">{len(marriage.get("cocok",[]))} <span class="unit">cocok · {len(marriage.get("hindari",[]))} hindari</span></div>'
        f'<div class="ks-desc">{_desc_or_default("kompat_desc", card6_default_desc)}</div>'
        f'</div>'
    )

    tafsir_blocks["_kes_stats"] = "\n      " + "\n      ".join([card1, card2, card3, card4, card5, card6]) + "\n    "

    if age:
        tafsir_blocks["_kes_age"] = str(age)

    # HIDUP MAP narrative, from MD life_map (or fallback engine derive)
    lalu = kes_lifemap_md.get("lalu", "")
    sekarang = kes_lifemap_md.get("sekarang", "")
    berikutnya = kes_lifemap_md.get("berikutnya", "")
    if not lalu and cur_idx > 0:
        past_cycles = cycles[:cur_idx]
        elements = [c.get("element_class","").replace("el-","") for c in past_cycles]
        lalu = f"{cur_idx} fase telah dilalui, fondasi terbentuk lewat tempaan zaman muda hingga awal dewasa."
    if not sekarang and cur_cycle:
        sekarang = f"Fase {cur_tg} {cur_gz} ({cur_age}), tema utama {cur_tg.lower()} membentuk dekade ini."
    if not berikutnya and cur_idx + 1 < len(cycles):
        nxt = cycles[cur_idx + 1]
        nxt_gz = f"{nxt.get('stem_hz','')}{nxt.get('branch_hz','')}"
        nxt_tg = nxt.get("ten_god_id","")
        nxt_age = f"{nxt.get('age_start','')}-{nxt.get('age_end','')}"
        berikutnya = f"Fase {nxt_gz} {nxt_tg} ({nxt_age}), transisi menuju tema baru."

    rows_html = []
    if lalu:
        rows_html.append(
            f'          <div class="klm-row">'
            f'<div class="klm-row-icon">過<span class="id-label">Lalu</span></div>'
            f'<div class="klm-row-text"><span class="lbl">MASA LALU</span>{_md_inline(lalu)}</div>'
            f'</div>'
        )
    if sekarang:
        rows_html.append(
            f'          <div class="klm-row now">'
            f'<div class="klm-row-icon">今<span class="id-label">Kini</span></div>'
            f'<div class="klm-row-text"><span class="lbl">SEKARANG</span>{_md_inline(sekarang)}</div>'
            f'</div>'
        )
    if berikutnya:
        rows_html.append(
            f'          <div class="klm-row">'
            f'<div class="klm-row-icon">未<span class="id-label">Nanti</span></div>'
            f'<div class="klm-row-text"><span class="lbl">BERIKUTNYA</span>{_md_inline(berikutnya)}</div>'
            f'</div>'
        )
    if rows_html:
        tafsir_blocks["_kes_lifemap"] = "\n" + "\n".join(rows_html) + "\n        "

    # Position block (right side): season + 10-cell bar + meta
    SEASON_MAP = [
        (0, 1, "春", "Chūn", "Musim Semi Hidup"),
        (2, 4, "夏", "Xià", "Musim Panas Hidup"),
        (5, 7, "秋", "Qiū", "Musim Gugur Hidup"),
        (8, 9, "冬", "Dōng", "Musim Dingin Hidup"),
    ]
    season_hz, season_pinyin, season_label = "夏", "Xià", "Musim Panas Hidup"
    for s, e, hz_, py_, lbl_ in SEASON_MAP:
        if s <= cur_idx <= e:
            season_hz, season_pinyin, season_label = hz_, py_, lbl_
            break
    # 10-cell bar
    cells = []
    for i in range(10):
        if i < cur_idx:
            cells.append('<div class="klp-bar-cell past"></div>')
        elif i == cur_idx:
            cells.append('<div class="klp-bar-cell now"></div>')
        else:
            cells.append('<div class="klp-bar-cell future"></div>')
    bar_html = "\n            ".join(cells)
    dm_el_hz = dm.get("stem_element_hz", "")
    dm_el_id = {"金":"Logam","水":"Air","木":"Kayu","火":"Api","土":"Tanah"}.get(dm_el_hz, "")
    meta = (
        f'Fase <strong>{cur_idx+1} dari 10</strong> · Umur <strong>{cur_age}</strong> · '
        f'<strong>{dm_el_hz} {dm_el_id}</strong> dominan · {season_label}'
    )
    tafsir_blocks["_kes_position"] = (
        '\n          <div class="klp-eb">Posisi Sekarang</div>\n'
        f'          <div class="klp-hz">{season_hz}</div>\n'
        f'          <div class="klp-id">{season_pinyin}, "{season_label}"</div>\n'
        f'          <div class="klp-bar">\n            {bar_html}\n          </div>\n'
        f'          <div class="klp-meta">{meta}</div>\n        '
    )

    # ─── Sintesis (page 22): trio cards + 5 actions + attrib + timeline ───
    syn_md = tafsir_blocks.get("_sintesis_struct") or {}
    syn_trio = syn_md.get("trio") or {}
    syn_actions = syn_md.get("actions") or []

    # Attrib subline: "{strength_id} · {format_hz} · {format_pinyin}"
    attrib_parts = []
    if dm.get("label_id"):
        attrib_parts.append(_html_amp(dm.get("label_id","")))
    if fmt.get("hz"):
        attrib_parts.append(fmt.get("hz",""))
    if fmt.get("pinyin"):
        attrib_parts.append(fmt.get("pinyin",""))
    if attrib_parts:
        tafsir_blocks["_syn_attrib"] = " · ".join(attrib_parts)

    # Trio cards (3): kekuatan / tantangan / tindakan
    TRIO_META = [
        ("kekuatan",  "strength",  "力", "Kekuatan"),
        ("tantangan", "challenge", "驗", "Tantangan"),
        ("tindakan",  "action",    "為", "Tindakan"),
    ]
    if syn_trio:
        cards = []
        for key, css_class, num_hz, eb in TRIO_META:
            d = syn_trio.get(key) or {}
            hanzi = d.get("hanzi", "")
            pinyin = d.get("pinyin", "")
            arti = d.get("arti", "")
            body_md = d.get("body", "")
            body_html = _md_inline(body_md) if body_md else ""
            arti_html = (
                f'          <span class="syn-card-arti">{_md_inline(arti)}</span>\n'
                if arti else ""
            )
            card = (
                f'      <div class="syn-card {css_class}">\n'
                f'        <div class="syn-card-num">{num_hz}</div>\n'
                f'        <div class="syn-card-eyebrow">{eb}</div>\n'
                f'        <div class="syn-card-title">\n'
                f'          <span class="syn-card-hz">{hanzi}</span>\n'
                f'          <span class="syn-card-id">{pinyin}</span>\n'
                f'{arti_html}'
                f'        </div>\n'
                f'        <div class="syn-card-body">{body_html}</div>\n'
                f'      </div>'
            )
            cards.append(card)
        tafsir_blocks["_syn_trio"] = "\n" + "\n".join(cards) + "\n    "

    # 5 actions
    if syn_actions:
        items = []
        for i, a in enumerate(syn_actions[:5], start=1):
            title = _md_inline(a.get("title", ""))
            context = _md_inline(a.get("context", ""))
            item = (
                f'        <div class="syn-action">\n'
                f'          <div class="syn-action-num">{i}</div>\n'
                f'          <div class="syn-action-content">\n'
                f'            <div class="syn-action-title">{title}</div>\n'
                f'            <div class="syn-action-context">{context}</div>\n'
                f'          </div>\n'
                f'        </div>'
            )
            items.append(item)
        tafsir_blocks["_syn_actions"] = "\n" + "\n".join(items) + "\n      "


    # Yang Zhai (page 13): 6 zones from MD
    yz = tafsir_blocks.get("_yangzhai_struct") or {}
    zones = yz.get("zones") or []
    if zones:
        # Map label_id (or partial match) → (hz, pinyin)
        ZONE_HZ = {
            "pintu": ("門", "Mén · Pintu"),
            "kamar tidur": ("房", "Fáng · Kamar"),
            "ranjang": ("床", "Chuáng · Tempat Tidur"),
            "dapur": ("灶", "Zào · Tungku"),
            "kompor": ("灶", "Zào · Tungku"),
            "kamar mandi": ("廁", "Cè · Kamar Mandi"),
            "altar": ("神", "Shén · Sembahyang"),
            "sembah": ("神", "Shén · Sembahyang"),
            "ruang kerja": ("書", "Shū · Ruang Kerja"),
            "kerja": ("書", "Shū · Ruang Kerja"),
        }
        # Direction Hanzi → Indo abbrev
        DIR_ABBR = {
            "東":"T","南":"S","西":"B","北":"U",
            "東南":"TG","西南":"BD","東北":"TL","西北":"BL",
        }
        cells = []
        for z in zones[:6]:
            label = z.get("label", "").lower()
            hz, pinyin = "?", "?"
            for k, v in ZONE_HZ.items():
                if k in label:
                    hz, pinyin = v
                    break
            headline_raw = z.get("headline", "✓ Arah Optimal")
            is_warn = "⚠" in headline_raw or any(w in headline_raw.lower() for w in ["warn","perhati","penekan","hindari"])
            zone_class = " warn" if is_warn else ""
            pills_raw = z.get("pills", "").strip()
            pill_html_parts = []
            for p in pills_raw.split():
                p = p.strip().strip(",").strip("·").strip("/")
                # Skip Latin tokens (legacy MD format "南 S" — keep only hanzi).
                # Also skip arrow tokens ("→東" inside compound directions).
                if not p or p.startswith("{"):
                    continue
                if all(ord(c) < 0x4E00 for c in p):  # all chars below CJK range
                    continue
                if p and not p.startswith("{"):
                    abbr = DIR_ABBR.get(p, p[:2])
                    pill_class = "yz-pill bad" if is_warn else "yz-pill"
                    pill_html_parts.append(f'<span class="{pill_class}"><span class="hz">{p}</span>{abbr}</span>')
            pills_html = "\n              ".join(pill_html_parts)
            note = z.get("note", "")
            note_html = f'<div class="yz-zone-note">{_md_inline(note)}</div>' if note else ""
            id_label = z.get("label", "")
            cells.append(
                f'        <div class="yz-zone{zone_class}">\n'
                f'          <div class="yz-zone-label">\n'
                f'            <div class="yz-zone-hz">{hz}</div>\n'
                f'            <div class="yz-zone-id">{id_label}</div>\n'
                f'            <div class="yz-zone-pinyin">{pinyin}</div>\n'
                f'          </div>\n'
                f'          <div class="yz-zone-dirs">\n'
                f'            <div class="yz-zone-headline">{headline_raw}</div>\n'
                f'            <div class="yz-dir-pills">\n              {pills_html}\n            </div>\n'
                f'            {note_html}\n'
                f'          </div>\n'
                f'        </div>'
            )
        tafsir_blocks["_yangzhai_zones"] = "\n" + "\n".join(cells) + "\n"

    # Career (page 12): wuxing strip, 5 cells sorted by value DESC, with self/fav/unfav class
    wx = subject.get("wuxing") or {}
    ys_data = subject.get("yong_shen") or {}
    if wx and "jin" in wx:
        EL_HZ_MAP = {"jin":("金","Logam"),"shui":("水","Air"),"mu":("木","Kayu"),"huo":("火","Api"),"tu":("土","Tanah")}
        # Determine roles
        dm = subject.get("day_master") or {}
        dm_el = dm.get("stem_element_hz", "")
        ys_set = set(ys_data.get("elements_hz", "").split())
        js_set = set((subject.get("ji_shen") or {}).get("elements_hz", "").split())
        # Build sorted items
        items = [(k, wx[k]["value"]) for k in ["jin","shui","mu","huo","tu"]]
        items.sort(key=lambda x: x[1], reverse=True)
        max_val = items[0][1] if items[0][1] > 0 else 1
        cells = []
        for key, val in items:
            hz, name = EL_HZ_MAP[key]
            if hz == dm_el:
                klass = "self"
            elif hz in ys_set:
                klass = "fav"
            elif hz in js_set:
                klass = "unfav"
            else:
                klass = ""
            klass_attr = f" {klass}" if klass else ""
            height = round(val / max_val * 100)
            cells.append(
                f'        <div class="wux-cell{klass_attr}">\n'
                f'          <div class="wux-bar-track"><div class="wux-bar-fill" style="height:{height}%"></div></div>\n'
                f'          <div class="wux-label">{hz} {name}<span class="v">{val:g}</span></div>\n'
                f'        </div>'
            )
        tafsir_blocks["_career_wuxing"] = "\n" + "\n".join(cells) + "\n"

    # Career (page 12): title from yong_shen, avoid from ji_shen
    ys = subject.get("yong_shen") or {}
    ys_id = (ys.get("elements_id", "")).replace("&", "&amp;")
    if ys_id:
        tafsir_blocks["_career_title"] = (
            f'{ys_id} adalah aliran utama, '
            f'energi terbaik mengalir lewat industri ber-unsur ini'
        )
    js = subject.get("ji_shen") or {}
    js_hz = js.get("elements_hz", "")
    js_elements = [e for e in js_hz.split() if e in ELEMENT_PROFILE]
    if js_elements:
        names = " &amp; ".join(
            f'<strong>{el} ({ELEMENT_PROFILE[el]["id"]})</strong>'
            for el in js_elements
        )
        tafsir_blocks["_career_avoid"] = (
            f'Industri ber-unsur {names} sebaiknya dihindari, '
            f'menambah dominasi yang sudah kuat, menyebabkan energi macet & pertumbuhan terhambat.'
        )

    # Career (page 12): tags + 5 industri
    cr = tafsir_blocks.get("_career_struct") or {}
    tags = cr.get("tags") or {}
    if tags:
        parts = []
        for k, klass in [("fav_1",""),("fav_2",""),("unfav_1","bad"),("unfav_2","bad")]:
            if k in tags:
                hz, label = tags[k]
                cls = f"insight-tag {klass}".strip()
                parts.append(f'<span class="{cls}">{hz} {label}</span>')
        if parts:
            tafsir_blocks["_career_tags"] = "\n          " + "\n          ".join(parts) + "\n        "
    industri = cr.get("industri") or []
    if industri:
        # Element emoji per unsur
        EL_EMOJI = {"金":"⚙️","水":"💧","木":"🌳","火":"🔥","土":"🏛️"}
        # FIT scores descending
        FIT_SCORES = [95, 88, 82, 76, 70]
        items = []
        for i, ind in enumerate(industri[:5]):
            nama = ind.get("nama", "")
            unsur = ind.get("unsur", "").strip().strip("[]")
            alasan = ind.get("alasan", "")
            emoji = EL_EMOJI.get(unsur, "◆")
            score = FIT_SCORES[i] if i < len(FIT_SCORES) else 70
            top_class = " top" if i < 2 else ""
            items.append(
                f'        <div class="ind-row{top_class}">\n'
                f'          <div class="ind-icon">{emoji}</div>\n'
                f'          <div class="ind-info">\n'
                f'            <div class="ind-name">{_md_inline(nama)}</div>\n'
                f'            <div class="ind-reason">Unsur {unsur}, {_md_inline(alasan)}</div>\n'
                f'          </div>\n'
                f'          <div class="fit-col">\n'
                f'            <div class="fit-bar-track"><div class="fit-bar-fill" style="width:{score}%"></div></div>\n'
                f'          </div>\n'
                f'        </div>'
            )
        tafsir_blocks["_career_industri"] = "\n" + "\n".join(items) + "\n"

    # Shen Sha (page 10): hero star + strip
    sh = tafsir_blocks.get("_shensha_struct") or {}
    ds = sh.get("dominant_star") or {}
    if ds.get("hanzi"):
        tafsir_blocks["shensha_star_hz"] = ds["hanzi"]
    if ds.get("pinyin"):
        tafsir_blocks["shensha_star_pinyin"] = ds["pinyin"]
    if ds.get("label_id"):
        tafsir_blocks["shensha_star_label"] = f'"{ds["label_id"]}"'
    if ds.get("active_label"):
        tafsir_blocks["shensha_star_active"] = f'★ {ds["active_label"]} ★'
    if sh.get("strip"):
        tafsir_blocks["shensha_strip"] = _md_inline(sh["strip"])

    # Personality (page_08): MD struct overrides per-stem default if provided.
    dm_stem = (subject.get("day_master") or {}).get("stem_hz", "")
    md_struct = tafsir_blocks.get("_kepribadian_struct") or {}
    # Effective profile: deep-merge stem default with MD struct.
    base = dict(XQ_PROFILES.get(dm_stem, {}))
    if md_struct.get("radar_traits"):
        base["axes"] = md_struct["radar_traits"]
    if md_struct.get("motto"):
        base["motto"] = md_struct["motto"]
    if md_struct.get("power"):
        base["power"] = md_struct["power"]
    if md_struct.get("shadow"):
        base["shadow"] = md_struct["shadow"]
    if md_struct.get("optimum"):
        base["optimum"] = md_struct["optimum"]

    if base:
        # Build cards using effective profile.
        xqcards = _build_xqcards_from_profile(base)
        if xqcards:
            tafsir_blocks["_xqcards"] = xqcards
        # Build radar geometry + labels + motto from effective profile.
        poly_html, labels_html, motto = _regen_xq_radar_from_profile(base)
        if poly_html:
            subject["_xq_radar_poly"] = poly_html
            subject["_xq_radar_labels"] = labels_html
            subject["_xq_motto"] = list(motto)

    if tafsir_blocks:
        # Inject dayun overrides (data-path), use existing render machinery
        inject_dayun_overrides(subject, tafsir_blocks)
        # Store remaining tafsir blocks for anchor-based injection in render.py
        subject["_tafsir"] = tafsir_blocks
        # Save back
        json_path = DATA_DIR / f"{subject_id}.json"
        json_path.write_text(json.dumps(subject, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        print(f"   Injected MD overrides → updated {json_path.name}")

    # ---------- Step 2: Render ----------
    if no_pdf:
        print(f"\n=== Step 2: Render 23 pages (HTML only, --no-pdf) ===")
        from render import render_pages as _rp, build_master as _bm, BUILD_DIR as _BD
        import shutil as _sh
        subj = json.loads((DATA_DIR/f'{subject_id}.json').read_text(encoding='utf-8'))
        out = _BD/subject_id
        if out.exists(): _sh.rmtree(out)
        _rp(subj, out)
        master = _bm(out, subj)
        print(f"   HTML master: {master}")
        print(f"   Refresh URL: file:///{str(master).replace(chr(92), '/')}")
        print(f"DONE in {time.time()-t0:.1f}s")
        notify_done(
            f"V4.5 HTML render OK · {subject_id}",
            f"{time.time()-t0:.1f}s · refresh _master.html"
        )
    else:
        print(f"\n=== Step 2: Render 23 pages → PDF ===")
        pdf = render_subject(subject_id)
        print(f"   Render+PDF: {time.time()-t1:.1f}s\n")
        print(f"DONE in {time.time()-t0:.1f}s: {pdf}")
        notify_done(
            f"V4.5/V4.9 PDF render OK · {subject_id}",
            f"{(time.time()-t0):.0f}s · {Path(pdf).name}"
        )

        # Quality report — user-friendly Indonesian table
        try:
            ocr_path = DATA_DIR / f"{subject_id}.ocr.json"
            subj_path = DATA_DIR / f"{subject_id}.json"
            if ocr_path.exists() and subj_path.exists():
                ocr_data = json.loads(ocr_path.read_text(encoding='utf-8'))
                subj_data = json.loads(subj_path.read_text(encoding='utf-8'))
                print(generate_quality_report(ocr_data, subj_data))
        except Exception as e:
            print(f"[QUALITY-REPORT] Failed to generate: {e}")


if __name__ == "__main__":
    main()
