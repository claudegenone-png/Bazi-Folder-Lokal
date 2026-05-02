from pypdf import PdfReader, PdfWriter
import os, shutil, time

base = r"C:\Users\sukam\OneDrive\Documents\Ramalan"
src_main = os.path.join(base, "Henry_Ramalan_Lengkap.pdf")
src_new  = os.path.join(base, "Henry_Ramalan_Lengkap_012802.pdf")
tmp      = os.path.join(os.environ["TEMP"], "henry_spliced.pdf")

a = PdfReader(src_main)
b = PdfReader(src_new)

w = PdfWriter()
for i in range(len(a.pages)):
    if i == 21:  # Page 22 (0-indexed = 21) -> replace from new PDF
        w.add_page(b.pages[i])
    else:
        w.add_page(a.pages[i])

with open(tmp, "wb") as f:
    w.write(f)

# Try overwrite; if locked, save as _final
try:
    shutil.move(tmp, src_main)
    print(f"OK: {src_main}")
except PermissionError:
    alt = src_main.replace(".pdf", f"_final{time.strftime('%H%M%S')}.pdf")
    shutil.move(tmp, alt)
    print(f"LOCKED. Saved as: {alt}")

print(f"Pages: {len(a.pages)}")
