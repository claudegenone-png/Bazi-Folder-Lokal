"""V4.8 Canonical Data Model.

This is the FIXED schema produced by the extractor pipeline. Renderers consume
ONLY this model — they should never touch raw MD again. Missing fields = None.

Confidence tiers (based on 7-MD audit):
  ALWAYS  (7/7): Subject, Karakter, Karir, Keuangan, Kesehatan, Pernikahan,
                 Tahunan, ShenSha, Ringkasan
  USUALLY (6/7): BaZi, Hikmat Klasik, Da Yun, FengShui (5/7+)
  OFTEN   (5/7): Kecocokan Shio, Anak/Orangtua/Saudara/Bawahan/Perpindahan
  PARTIAL (3/7): ZiWei 12 Istana lengkap
  RARE    (1/7): Glosarium
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════════════════════════
# Atomic primitives
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class HzTerm:
    """A Hanzi term with Indo translation."""
    hz: str = ""
    indo: str = ""
    pinyin: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Bullet:
    """A single bullet line, optionally with a bold-label prefix."""
    label: Optional[str] = None     # e.g. "Tegas dan berprinsip"
    text: str = ""                   # e.g. "memiliki pendirian yang kuat..."


@dataclass
class KeyValue:
    key: str = ""
    value: str = ""
    hz: Optional[str] = None         # optional Hanzi for the value
    indo: Optional[str] = None       # optional decoded Indo


# ═══════════════════════════════════════════════════════════════════════════
# Section: Subject identitas
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Subject:
    nama: str = ""                          # required, fail if absent
    nama_hanzi: Optional[str] = None        # 林如意
    nama_pinyin: Optional[str] = None       # Lin Ruyi
    gender: Optional[str] = None            # "Pria" / "Perempuan"
    yin_yang: Optional[str] = None          # "陰女 (Wanita Yin)"
    shio: Optional[str] = None              # "Babi"
    shio_hz: Optional[str] = None           # "豬"
    lahir_tanggal: Optional[str] = None     # "30 Mei 1995"
    lahir_lunar: Optional[str] = None       # "農曆乙亥 84年 5月 2日"
    lahir_jam: Optional[str] = None         # "10時35分"
    hari_lahir: Optional[str] = None        # "Selasa"
    kalender_nasional: Optional[str] = None # "民國 84年 5月 30日"
    tahun_masehi: Optional[str] = None      # "1995"
    lima_unsur: Optional[str] = None        # "火六局"
    # ZiWei core (often in identitas, sometimes scattered)
    ming_zhu: Optional[HzTerm] = None       # 命主
    shen_zhu: Optional[HzTerm] = None       # 身主
    ming_gong: Optional[HzTerm] = None      # 命宮
    shen_gong: Optional[HzTerm] = None      # 身宮


# ═══════════════════════════════════════════════════════════════════════════
# Section: BaZi 4-Pilar
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Pilar:
    """One of 4 pillars (Tahun/Bulan/Hari/Jam)."""
    posisi: str = ""                  # "Tahun" / "Bulan" / "Hari" / "Jam"
    posisi_hz: str = ""               # "年" / "月" / "日" / "時"
    gan: Optional[HzTerm] = None      # 天干 — Heavenly Stem
    zhi: Optional[HzTerm] = None      # 地支 — Earthly Branch
    elem: Optional[str] = None        # "Air"
    ten_god: Optional[HzTerm] = None  # 十神 relation
    is_day_master: bool = False


@dataclass
class BaZi:
    pilar: List[Pilar] = field(default_factory=list)   # 4 pillars
    yong_shen: Optional[HzTerm] = None                  # 用神 favorable
    xi_shen: Optional[HzTerm] = None                    # 喜神
    ji_shen: Optional[HzTerm] = None                    # 忌神 unfavorable
    transformasi: List[HzTerm] = field(default_factory=list)   # 化星 4 transformations
    wuxing_count: Dict[str, int] = field(default_factory=dict) # {"Kayu": 2, ...}
    day_master_strength: Optional[str] = None
    skor: Optional[str] = None
    interpretasi: Optional[str] = None                  # Indonesian intro from MD


# ═══════════════════════════════════════════════════════════════════════════
# Section: ZiWei
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Palace:
    nama_id: str = ""             # "Istana Nasib"
    nama_hz: str = ""             # "命宮"
    bintang_utama: List[HzTerm] = field(default_factory=list)
    age_range: Optional[str] = None        # "26-35"
    ganzhi: Optional[str] = None
    interpretasi: Optional[str] = None     # narrative paragraph (Indo)
    saran: Optional[str] = None            # subject-specific advice (e.g. "💼 Saran: ...")
    saran_icon: Optional[str] = None       # emoji icon dari saran header
    saran_label: Optional[str] = None      # detected keyword: Saran/Catatan/Tips/Note


@dataclass
class Transformasi:
    """Empat 四化 transformations."""
    star_hz: str = ""               # 武曲
    star_indo: Optional[str] = None # Wuqu
    role_hz: str = ""               # 化祿
    role_indo: Optional[str] = None # Jadi Rezeki
    makna: Optional[str] = None     # Kekayaan lewat kerja keras


@dataclass
class ZiWei:
    palaces: List[Palace] = field(default_factory=list)   # up to 12, partial OK
    transformasi: List[Transformasi] = field(default_factory=list)
    data_inti: List[KeyValue] = field(default_factory=list)
    interpretasi: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# Sections: per-bidang life areas
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LifeArea:
    """Generic life-area container. Used for karakter/karir/keuangan/dst."""
    intro: Optional[str] = None              # opening paragraph
    fakta: List[KeyValue] = field(default_factory=list)
    rekomendasi: List[Bullet] = field(default_factory=list)
    kewaspadaan: List[Bullet] = field(default_factory=list)
    bintang_terkait: List[HzTerm] = field(default_factory=list)
    raw_paragraphs: List[str] = field(default_factory=list)
    raw_bullets: List[Bullet] = field(default_factory=list)
    raw_quotes: List[str] = field(default_factory=list)


@dataclass
class Karakter:
    intro: Optional[str] = None
    kekuatan: List[Bullet] = field(default_factory=list)
    kelemahan: List[Bullet] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# Section: Da Yun (Decade Cycles)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DaYunPeriode:
    usia_start: int = 0
    usia_end: int = 0
    ganzhi: Optional[str] = None        # "丁亥"
    ganzhi_indo: Optional[str] = None   # "Api Babi"
    ten_god: Optional[HzTerm] = None    # 劫財 + Indo
    tema: Optional[str] = None
    narasi: Optional[str] = None
    is_active: bool = False             # currently in this period?


# ═══════════════════════════════════════════════════════════════════════════
# Section: Tahunan (year-by-year forecast)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Tahun:
    year: int = 0
    age: Optional[int] = None
    ganzhi: Optional[str] = None
    ganzhi_indo: Optional[str] = None         # "Kuda Api"
    stars_rating: Optional[int] = None        # 1-5 stars (None = no rating)
    tema: Optional[str] = None                # "Tahun Stabilisasi"
    narasi: Optional[str] = None              # opening paragraph
    hal_positif: List[Bullet] = field(default_factory=list)
    hal_diwaspadai: List[Bullet] = field(default_factory=list)
    bintang_aktif: List[HzTerm] = field(default_factory=list)
    saran: Optional[str] = None
    mood: Optional[str] = None                # "good"/"warn"/"bad"


# ═══════════════════════════════════════════════════════════════════════════
# Section: Tabel Tahunan Detail (per-tahun pivot table)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TahunDetailRow:
    usia: int = 0
    tahun_masehi: Optional[int] = None
    ganzhi: Optional[str] = None
    relasi: Optional[str] = None              # ten god relation
    fase_hidup: Optional[HzTerm] = None
    bintang_khusus: List[HzTerm] = field(default_factory=list)
    mood: Optional[str] = None
    is_current: bool = False


@dataclass
class TabelTahunanPeriode:
    usia_start: int = 0
    usia_end: int = 0
    da_yun_ctx: Optional[str] = None
    rows: List[TahunDetailRow] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# Section: ShenSha & Hikmat Klasik
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ShenShaItem:
    nama: HzTerm = field(default_factory=HzTerm)
    deskripsi: Optional[str] = None


@dataclass
class FengShuiElement:
    """One Feng Shui element in the home (orientasi/pintu/dapur/etc)."""
    aspek: str = ""              # "Orientasi Rumah"
    aspek_hz: Optional[str] = None  # "坐向"
    arah: str = ""               # "Hadap Barat Daya → Timur Laut"
    icon: Optional[str] = None   # emoji per aspek (auto-mapped)


@dataclass
class FengShuiRumah:
    elements: List[FengShuiElement] = field(default_factory=list)
    trigram_hz: Optional[str] = None     # "坤卦"
    trigram_indo: Optional[str] = None   # "Kun/Tanah"
    trigram_meaning: Optional[str] = None  # description from MD
    interpretasi: Optional[str] = None   # subject-specific Saran
    catatan: Optional[str] = None         # additional Catatan blockquote


@dataclass
class ShioMatch:
    """One shio compatibility entry."""
    shio_id: str = ""           # "Kambing"
    shio_hz: str = ""            # "羊"
    rating: int = 3              # 1-5 (5 = sangat cocok)
    mood: str = "neutral"        # good | neutral | warn | bad
    note: Optional[str] = None   # explanation
    is_other: bool = False       # "Shio lainnya / lain" generic row


@dataclass
class KecocokanShio:
    matches: List[ShioMatch] = field(default_factory=list)
    interpretasi: Optional[str] = None  # subject-specific intro/Saran
    pantangan_summary: Optional[str] = None  # combined warning text


@dataclass
class HikmatVerse:
    sumber: Optional[str] = None             # "三命通會"
    sumber_indo: Optional[str] = None        # "San Ming Tong Hui"
    hanzi: str = ""
    terjemahan: Optional[str] = None         # Indo translation (from MD or lookup)
    makna: Optional[str] = None              # explanation


@dataclass
class HikmatBundle:
    """Hikmat Klasik (古書云) page data — verses + synthesis."""
    verses: List[HikmatVerse] = field(default_factory=list)
    synthesis_intro: Optional[str] = None    # "Puisi-puisi kuno ini menggambarkan..."
    synthesis_bullets: List[str] = field(default_factory=list)
    catatan: Optional[str] = None            # disclaimer/source note


# ═══════════════════════════════════════════════════════════════════════════
# Section: Ringkasan / Kesimpulan
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Ringkasan:
    profil: Optional[str] = None
    kekuatan: List[Bullet] = field(default_factory=list)
    kelemahan: List[Bullet] = field(default_factory=list)
    saran_per_bidang: List[KeyValue] = field(default_factory=list)
    kalender_waspada: Optional[str] = None
    mantra: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# Section: Unknown / Additional content
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UnknownSection:
    """Section yang tidak match topic taxonomy — render via generic template."""
    title: str = ""
    title_hanzi: Optional[str] = None
    raw_lines: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# ROOT canonical model
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Canonical:
    """Top-level canonical data model. All fields optional except subject.nama."""
    # Required
    subject: Subject = field(default_factory=Subject)

    # Always (7/7) — should populate for all subjects
    karakter: Optional[Karakter] = None
    karir: Optional[LifeArea] = None
    keuangan: Optional[LifeArea] = None
    kesehatan: Optional[LifeArea] = None
    pernikahan: Optional[LifeArea] = None
    tahunan: List[Tahun] = field(default_factory=list)
    shensha: List[ShenShaItem] = field(default_factory=list)
    ringkasan: Optional[Ringkasan] = None

    # Usually (6/7)
    bazi: Optional[BaZi] = None
    hikmat_klasik: List[HikmatVerse] = field(default_factory=list)
    hikmat_bundle: Optional["HikmatBundle"] = None
    da_yun: List[DaYunPeriode] = field(default_factory=list)
    feng_shui: Optional["FengShuiRumah"] = None

    # Often (5/7)
    kecocokan_shio: Optional["KecocokanShio"] = None  # Agent 2 territory
    anak: Optional[LifeArea] = None
    orangtua: Optional[LifeArea] = None
    saudara: Optional[LifeArea] = None
    bawahan: Optional[LifeArea] = None
    perpindahan: Optional[LifeArea] = None
    properti: Optional[LifeArea] = None
    peruntungan: Optional[LifeArea] = None

    # Partial / data-rich
    ziwei: Optional[ZiWei] = None
    tabel_tahunan: List[TabelTahunanPeriode] = field(default_factory=list)
    takdir: Optional[LifeArea] = None      # 宿命

    # Rare
    glosarium: List[KeyValue] = field(default_factory=list)

    # Unknown / additional
    unknown_sections: List[UnknownSection] = field(default_factory=list)

    # Metadata
    md_source: Optional[str] = None
    extraction_warnings: List[str] = field(default_factory=list)
    unknown_hanzi: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# Validation report (printed before render)
# ═══════════════════════════════════════════════════════════════════════════

def validate(canonical: Canonical) -> Dict[str, Any]:
    """Inspect canonical model, return report dict.
    Format: {recognized: [...], missing_critical: [...], missing_optional: [...],
             unknown_sections: [...], unknown_hanzi: [...], warnings: [...]}
    """
    report = {
        "recognized": [],
        "missing_critical": [],
        "missing_optional": [],
        "unknown_sections": [],
        "unknown_hanzi": [],
        "warnings": list(canonical.extraction_warnings),
    }

    # Subject required
    if not canonical.subject or not canonical.subject.nama:
        report["missing_critical"].append("Subject nama tidak ditemukan")
    else:
        report["recognized"].append(f"Subject identitas ({canonical.subject.nama})")

    # Always-tier
    always = [
        ("karakter", canonical.karakter),
        ("karir", canonical.karir),
        ("keuangan", canonical.keuangan),
        ("kesehatan", canonical.kesehatan),
        ("pernikahan", canonical.pernikahan),
        ("ringkasan", canonical.ringkasan),
    ]
    for name, val in always:
        if val:
            report["recognized"].append(name)
        else:
            report["missing_optional"].append(f"{name} (always-tier)")
    if canonical.tahunan:
        report["recognized"].append(f"Tahunan ({len(canonical.tahunan)} years)")
    else:
        report["missing_optional"].append("tahunan (always-tier)")
    if canonical.shensha:
        report["recognized"].append(f"ShenSha ({len(canonical.shensha)} stars)")
    else:
        report["missing_optional"].append("shensha (always-tier)")

    # Usually-tier
    if canonical.bazi and canonical.bazi.pilar:
        report["recognized"].append(f"BaZi ({len(canonical.bazi.pilar)} pilar)")
    else:
        report["missing_optional"].append("bazi (usually-tier)")
    if canonical.hikmat_klasik:
        report["recognized"].append(f"Hikmat Klasik ({len(canonical.hikmat_klasik)} verses)")
    else:
        report["missing_optional"].append("hikmat_klasik (usually-tier)")
    if canonical.da_yun:
        report["recognized"].append(f"Da Yun ({len(canonical.da_yun)} periode)")
    else:
        report["missing_optional"].append("da_yun (usually-tier)")

    # Often-tier
    if canonical.kecocokan_shio:
        report["recognized"].append(f"Kecocokan Shio ({len(canonical.kecocokan_shio)} entries)")
    if canonical.ziwei and canonical.ziwei.palaces:
        report["recognized"].append(f"ZiWei ({len(canonical.ziwei.palaces)}/12 palaces)")
    if canonical.tabel_tahunan:
        report["recognized"].append(f"Tabel Tahunan ({len(canonical.tabel_tahunan)} periode)")

    # Unknown
    for u in canonical.unknown_sections:
        report["unknown_sections"].append(u.title)
    report["unknown_hanzi"] = list(canonical.unknown_hanzi)

    return report
