"""Ringkasan extractor — profil + kekuatan + kelemahan + saran per bidang.

Adaptive across MD formats:
  - Subject 1 (Lin Ruyi): H3 children "Ringkasan Karakter X" (paragraph profil),
    "Ringkasan Perkiraan Nasib Per Periode" (table → periode_summary as KV),
    "Saran Cepat" (table → saran KV).
  - Subject 2 (Li Yuanxiang): H3 "Ringkasan Karakter Utama Anda" (table aspek),
    "Saran Praktis Berdasarkan Ramalan" (bold-label sub-buckets like
    "💼 Karir & Bisnis:" → saran KV; "📅 Kalender Tahun Penting:" → kalender).
  - Subject 3 (Lin Wen Han): "RINGKASAN KESELURUHAN" L2 (table relasi+interpretasi),
    "KESIMPULAN & SARAN PRAKTIS" L2 (empty), nested H3 saran bidang (bullets).
"""
import re
from canonical_model import Ringkasan, Bullet, KeyValue
from extractors.md_utils import split_sections_deep, strip_md_bold


KESIMPULAN_KW = ["KESIMPULAN", "RINGKASAN UMUM", "RINGKASAN EKSEKUTIF",
                 "RINGKASAN KESELURUHAN", "SARAN PRAKTIS", "SARAN HOLISTIK",
                 "PENUTUP"]
PROFIL_LBL = re.compile(r"\b(profil\s+singkat|ringkasan\s+karakter)\b", re.IGNORECASE)
KEKUATAN_LBL = re.compile(r"\b(kekuatan|sifat\s+positif|kelebihan)\b", re.IGNORECASE)
KELEMAHAN_LBL = re.compile(r"\b(kelemahan|sifat\s+negatif|tantangan|area\s+(?:perlu\s+)?perhatian|kekurangan)\b", re.IGNORECASE)
SARAN_LBL = re.compile(r"\b(saran|rekomendasi|kunci\s+sukses|mantra)\b", re.IGNORECASE)
KALENDAR_LBL = re.compile(r"\bkalender(\s+(waspada|tahun))?\b", re.IGNORECASE)
PERIODE_LBL = re.compile(r"\b(periode|perkiraan\s+nasib|siklus)\b", re.IGNORECASE)
ASPEK_TBL_LBL = re.compile(r"\b(ringkasan\s+karakter|aspek)\b", re.IGNORECASE)

BIDANG_ICON = {
    "karir": "💼", "karier": "💼", "bisnis": "💼", "pekerjaan": "💼",
    "keuangan": "💰", "uang": "💰", "finansial": "💰",
    "hubungan": "💑", "asmara": "❤️", "pernikahan": "💑", "jodoh": "💑",
    "rumah": "🏠", "feng shui": "🏠", "rumah tangga": "🏠", "properti": "🏠",
    "kesehatan": "🏥", "fisik": "🏥",
    "kalender": "📅", "tahun": "📅", "waktu": "📅",
    "warna": "🌈", "angka": "🔢", "arah": "🧭",
    "umum": "✦", "spiritual": "✦", "mental": "✦",
}

META_PREFIX = re.compile(r"^\*\*(penulis|nomor\s+registrasi|tanggal\s+analisis|sumber)", re.IGNORECASE)


def _is_h_header(line):
    return line.strip().startswith("###") or line.strip().startswith("####")


def _is_bold_label(line):
    s = line.strip()
    # **Title:** or **Title:**\n
    return bool(re.match(r"^\*\*[^*]+\*\*\s*:?\s*$", s))


def _bold_label_text(line):
    s = line.strip()
    s = re.sub(r"^\*\*([^*]+)\*\*\s*:?\s*$", r"\1", s).strip()
    # Strip leading emoji
    s = re.sub(r"^[\W_]+\s*", "", s)
    return s


def _icon_for(bidang):
    if not bidang: return "✦"
    low = bidang.lower()
    for k, v in BIDANG_ICON.items():
        if k in low:
            return v
    return "✦"


SKIP_SUB_LBL = re.compile(r"\b(transkripsi|verbatim|software|raw)\b", re.IGNORECASE)


def _classify_subsection(title):
    if not title: return None
    if SKIP_SUB_LBL.search(title):
        return "skip"
    t = title.lower()
    if PROFIL_LBL.search(t):
        # "Ringkasan Karakter Utama Anda" — could be paragraph (profil) or table (aspek)
        return "profil_or_aspek"
    if PERIODE_LBL.search(t):
        return "periode"
    if KALENDAR_LBL.search(t):
        return "kalender"
    if KEKUATAN_LBL.search(t):
        return "kekuatan"
    if KELEMAHAN_LBL.search(t):
        return "kelemahan"
    if SARAN_LBL.search(t):
        return "saran"
    return None


def _parse_table(lines):
    """Parse markdown pipe table → list of [cells]. Returns rows after header."""
    rows = []
    in_table = False
    header = None
    for line in lines:
        if "|" not in line:
            if in_table: break
            continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line):
            in_table = True
            continue
        cells = [strip_md_bold(c.strip()) for c in line.strip().strip("|").split("|")]
        if not in_table:
            header = cells
            continue
        rows.append(cells)
    return header, rows


DISCLAIMER_RE = re.compile(r"\b(laporan\s+ini\s+disusun|disclaimer|astrologi\s+tionghoa\s+adalah)\b", re.IGNORECASE)


def _filter_meta(lines):
    """Drop disclaimer / Penulis Sistem trailing block + horizontal rules.
    Keep blockquote (`>`) content lines unless they look like the boilerplate disclaimer.
    """
    out = []
    skip_after = False
    for ln in lines:
        s = ln.strip()
        if META_PREFIX.match(s):
            skip_after = True
            continue
        if skip_after:
            continue
        if s == "---":
            continue
        if s.startswith(">"):
            inner = re.sub(r"^>\s?", "", s).strip()
            if not inner: continue
            if DISCLAIMER_RE.search(inner): continue
            out.append(inner)
            continue
        out.append(ln)
    return out


def _process_h2_lines(lines, out):
    """Walk the H2 body before any H3 — extract any inline tables / paragraphs.
    Treats first paragraph as profil, any 'aspek' table as kekuatan/kelemahan items."""
    lines = _filter_meta(lines)
    if not any(l.strip() for l in lines):
        return
    # Try table first (subject 3 RINGKASAN KESELURUHAN)
    header, rows = _parse_table(lines)
    if rows:
        for r in rows:
            if len(r) >= 2:
                label = r[0]
                text = " — ".join(r[1:])
                out.kekuatan.append(Bullet(label=label, text=text))
        # Continue: extract any non-table paragraph (e.g. Interpretasi blockquote after table)
        non_table = [l for l in lines if "|" not in l]
        text = " ".join(strip_md_bold(l.strip()) for l in non_table if l.strip())
        # Strip leading "💡 Interpretasi:" emoji label
        text = re.sub(r"^[\W_]*Interpretasi[\W_]*\s*:?\s*", "", text, flags=re.IGNORECASE)
        if text and not _is_predominantly_hanzi(text):
            out.profil = (out.profil + "\n\n" + text) if out.profil else text
        return
    # Plain paragraph → profil
    paras = []
    cur = []
    for ln in lines:
        s = ln.strip()
        if not s:
            if cur:
                paras.append(" ".join(cur)); cur = []
        else:
            cur.append(strip_md_bold(s))
    if cur:
        paras.append(" ".join(cur))
    if paras:
        joined = "\n\n".join(paras)
        if not _is_predominantly_hanzi(joined):
            out.profil = (out.profil + "\n\n" + joined) if out.profil else joined


def _process_subsection(sub, out):
    title = sub["title"]
    lines = _filter_meta(sub["lines"])
    bucket = _classify_subsection(title)
    if bucket == "skip":
        return

    # Try table parse
    header, rows = _parse_table(lines)

    if bucket == "profil_or_aspek":
        if rows:
            # Aspek table → kekuatan/kelemahan inferred by penilaian column
            # Header e.g. ['Aspek','Penilaian','Catatan'] — treat each row as kekuatan Bullet
            for r in rows:
                if len(r) >= 2:
                    label = r[0]
                    rest = " — ".join(c for c in r[1:] if c)
                    out.kekuatan.append(Bullet(label=label, text=rest))
            return
        # Paragraph profil
        text = " ".join(strip_md_bold(l.strip()) for l in lines if l.strip())
        if text:
            out.profil = (out.profil + "\n\n" + text) if out.profil else text
        return

    if bucket == "periode":
        # Table → store as saran KV with key="Periode {ganzhi/usia}"
        if rows:
            for r in rows:
                if len(r) >= 2:
                    key = r[0]
                    val = " — ".join(c for c in r[1:] if c)
                    out.saran_per_bidang.append(KeyValue(key=key, value=val))
        return

    if bucket == "kalender":
        # Bullets like **2026:** ... or just paragraph
        items = _extract_bullets_with_label(lines)
        if items:
            text = "\n".join(f"{b.label}: {b.text}" if b.label else b.text for b in items)
            out.kalender_waspada = text
        else:
            text = " ".join(strip_md_bold(l.strip()) for l in lines if l.strip())
            if text:
                out.kalender_waspada = text
        return

    if bucket == "kekuatan":
        for b in _extract_bullets_with_label(lines):
            out.kekuatan.append(b)
        return

    if bucket == "kelemahan":
        for b in _extract_bullets_with_label(lines):
            out.kelemahan.append(b)
        return

    if bucket == "saran":
        # Mode A: table with Area|Saran header (subject 1)
        if rows:
            for r in rows:
                if len(r) >= 2:
                    key = strip_md_bold(r[0])
                    val = " — ".join(c for c in r[1:] if c)
                    out.saran_per_bidang.append(KeyValue(key=key, value=val))
            return
        # Mode B: bold-label sub-buckets (subject 2) — each "**Bidang:**" + bullets
        cur_bidang = None
        cur_bullets = []
        def flush():
            nonlocal cur_bidang, cur_bullets
            if cur_bidang and cur_bullets:
                low = cur_bidang.lower()
                if "kalender" in low:
                    out.kalender_waspada = "\n".join(
                        (f"{b.label}: {b.text}" if b.label else b.text) for b in cur_bullets
                    )
                else:
                    val = "\n".join(
                        (f"{b.label} — {b.text}" if b.label else f"• {b.text}") for b in cur_bullets
                    )
                    out.saran_per_bidang.append(KeyValue(key=cur_bidang, value=val))
            cur_bidang = None
            cur_bullets = []

        for raw in lines:
            s = raw.strip()
            if not s: continue
            if _is_bold_label(raw):
                flush()
                cur_bidang = _bold_label_text(raw)
                continue
            mb = re.match(r"^\s*[-*]\s+(.+)$", raw)
            if not mb:
                mb = re.match(r"^\s*\d+\.\s+(.+)$", raw)
            if mb:
                content = mb.group(1).strip()
                m_lbl = re.match(r"^\*\*([^*]+)\*\*\s*[—–\-:]\s*(.+)$", content)
                if m_lbl:
                    cur_bullets.append(Bullet(label=m_lbl.group(1).strip(), text=m_lbl.group(2).strip()))
                else:
                    cur_bullets.append(Bullet(text=strip_md_bold(content)))
        flush()
        # If still nothing, fall back to plain bullets as a single saran entry
        if not out.saran_per_bidang:
            for b in _extract_bullets_with_label(lines):
                out.saran_per_bidang.append(KeyValue(
                    key=b.label or title, value=b.text
                ))
        return

    # Unclassified subsection — treat as profil paragraph if no profil yet
    # AND content is not predominantly Hanzi-only (those are raw verses).
    if not out.profil:
        text = " ".join(strip_md_bold(l.strip()) for l in lines if l.strip())
        if text and not _is_predominantly_hanzi(text):
            out.profil = text


def _is_predominantly_hanzi(text):
    if not text: return False
    han = sum(1 for c in text if "一" <= c <= "鿿")
    latn = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return han > 0 and han > latn * 1.5


def _extract_bullets_with_label(lines):
    items = []
    for raw in lines:
        s = raw.strip()
        m = re.match(r"^\s*[-*]\s+(.+)$", s)
        if not m:
            m = re.match(r"^\s*\d+\.\s+(.+)$", s)
        if not m:
            continue
        content = m.group(1).strip()
        ml = re.match(r"^\*\*([^*]+)\*\*\s*[—–\-:]\s*(.+)$", content)
        if ml:
            items.append(Bullet(label=ml.group(1).strip(), text=ml.group(2).strip()))
        else:
            items.append(Bullet(text=strip_md_bold(content)))
    return items


def extract_ringkasan(sections):
    """Adaptive ringkasan extractor. Accepts both:
       - flat split_sections() output (mixed L2/L3 entries)
       - deep split_sections_deep() output (L2 with 'sub' arrays of L3 children)
    """
    # Detect format: deep has 'sub' key
    is_deep = any("sub" in s for s in sections)

    parents = []
    if is_deep:
        for s in sections:
            if s.get("level") == 2 and any(k in s["title"].upper() for k in KESIMPULAN_KW):
                # h2.lines in deep mode contains ALL lines (own + all H3 children mixed).
                # We only want the H2's own pre-H3 body. Reconstruct by stripping H3 sub lines.
                own_lines = list(s["lines"])
                for sub in s.get("sub", []):
                    sub_lines = sub.get("lines", [])
                    # Remove first occurrence of each sub-line to get the H2 own body
                    # (sub.lines mirror the trailing portion). Simpler: own = lines BEFORE
                    # first sub. But we don't have positions, so approximate by removing
                    # the contiguous trailing slice equal to combined sub lines.
                # Simpler approach: in deep mode, the H2 own-body = lines that DON'T appear
                # in any sub. But duplicates mean false positives. So just take the lines
                # BEFORE the first non-empty content matching first sub's first line.
                if s.get("sub"):
                    first_sub_first = next((l for l in s["sub"][0]["lines"] if l.strip()), None)
                    if first_sub_first is not None:
                        try:
                            cut = own_lines.index(first_sub_first)
                            own_lines = own_lines[:cut]
                        except ValueError:
                            pass
                h2_view = {"title": s["title"], "lines": own_lines, "level": 2}
                parents.append({"h2": h2_view, "subs": s.get("sub", [])})
        if not parents:
            # Fallback: scan H3 subs across all H2 sections
            for s in sections:
                for sub in s.get("sub", []) if "sub" in s else []:
                    if any(k in sub["title"].upper() for k in KESIMPULAN_KW):
                        parents.append({"h2": {"title": sub["title"], "lines": [], "level": 3}, "subs": [sub]})
    else:
        i = 0
        n = len(sections)
        while i < n:
            s = sections[i]
            if s["level"] == 2 and any(k in s["title"].upper() for k in KESIMPULAN_KW):
                children = []
                j = i + 1
                while j < n and sections[j]["level"] >= 3:
                    children.append(sections[j])
                    j += 1
                parents.append({"h2": s, "subs": children})
                i = j
                continue
            i += 1
        if not parents:
            for s in sections:
                if s["level"] >= 3 and any(k in s["title"].upper() for k in KESIMPULAN_KW):
                    parents.append({"h2": s, "subs": []})

    if not parents:
        return None

    out = Ringkasan()

    for p in parents:
        h2 = p["h2"]
        # Process h2's own body lines (often empty, sometimes a table or paragraph)
        _process_h2_lines(h2["lines"], out)
        for sub in p["subs"]:
            _process_subsection(sub, out)

    if not (out.profil or out.kekuatan or out.kelemahan or out.saran_per_bidang or out.kalender_waspada):
        return None
    return out
