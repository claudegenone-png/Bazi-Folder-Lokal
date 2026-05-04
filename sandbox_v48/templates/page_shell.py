"""Page shell — consistent header + footer wrapper for all non-cover pages."""
import html as _html


def _esc(s):
    return _html.escape(s or "", quote=False)


def page_shell(num: int, title_id: str, title_hz: str, section_label: str,
               body_html: str, subject_name: str = "", footer_l: str = None) -> str:
    """Standard page shell.

    Args:
        num: page number (rendered in header + footer)
        title_id: Indonesian page title (left-aligned in header)
        title_hz: Hanzi page title (red, large, right of Indo)
        section_label: small uppercase label top-right (e.g. "BA ZI · 八字")
        body_html: page content
        subject_name: subject name for footer right-tag
        footer_l: optional override for footer left text
    """
    fl = footer_l or "Laporan Ramalan Tionghoa Klasik"
    return f"""<section class="page">
  <header class="ps-header">
    <div class="ps-num">{num:02d}</div>
    <div class="ps-titles">
      <div class="ps-id">{_esc(title_id)}</div>
      <div class="ps-hz">{_esc(title_hz)}</div>
    </div>
    <div class="ps-section">{_esc(section_label)}</div>
  </header>
  <div class="ps-content">{body_html}</div>
  <footer class="ps-footer">
    <div class="ps-footer-l">{_esc(fl)}</div>
    <div class="ps-footer-c">{_esc(subject_name)}</div>
    <div class="ps-footer-pg">— {num} —</div>
  </footer>
</section>"""


PAGE_SHELL_CSS = """
/* === PAGE SHELL (V4.8 standard non-cover page) === */
.page:not(.cover) {
  padding: 12mm 14mm 10mm 14mm;
  display: grid; grid-template-rows: auto 1fr auto; gap: 4mm;
  background: var(--color-paper);
}
.ps-header {
  display: grid; grid-template-columns: auto 1fr auto; gap: var(--sp-3);
  align-items: baseline; padding-bottom: 2.5mm;
  border-bottom: 0.4mm double var(--color-gold);
}
.ps-num {
  font-family: var(--font-display); font-size: 22pt;
  color: var(--color-gold-deep); font-weight: 700; line-height: 1;
  letter-spacing: 1px;
}
.ps-titles {
  display: flex; flex-direction: column-reverse; gap: 0.5mm;
  white-space: nowrap;
}
.ps-id {
  font-family: var(--font-display); font-size: 14pt;
  color: var(--color-red); font-weight: 600;
  letter-spacing: 0.5px;
}
.ps-hz {
  font-family: var(--font-serif-tc); font-size: 9.5pt;
  color: var(--color-muted); letter-spacing: 4px;
}
.ps-section {
  font-family: var(--font-body); font-size: 7.5pt;
  letter-spacing: 3px; color: var(--color-gold-deep);
  text-transform: uppercase; font-weight: 700;
  align-self: end;
  padding: 1mm 3mm; border: 0.2mm solid var(--color-gold-soft);
  border-radius: var(--r-sm); background: var(--color-gold-tint);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.ps-content {
  overflow: hidden; min-height: 0;
}
.ps-footer {
  display: grid; grid-template-columns: 1fr auto 1fr; gap: var(--sp-3);
  align-items: center; padding-top: 2.5mm;
  border-top: 0.2mm solid var(--color-gold-soft);
  font-size: 7.5pt; color: var(--color-muted); letter-spacing: 1px;
}
.ps-footer-l { text-align: left; }
.ps-footer-c { text-align: center; font-family: var(--font-display); font-style: italic; color: var(--color-red); font-size: 8pt; }
.ps-footer-pg { text-align: right; font-family: var(--font-display); font-size: 9pt; color: var(--color-gold-deep); font-weight: 600; }
"""
