"""
lunar_convert.py — Konversi tanggal 農曆 (Lunar Chinese) ke Masehi (Solar)
Digunakan di Step 1 V13 sebelum tulis lahir_tanggal ke MD.

Usage:
    python lunar_convert.py 1953 5 23
    python lunar_convert.py 1982 -4 15   # bulan kabisat (leap month): negatif

Output (stdout):
    1953-07-03

Exit code:
    0 = sukses
    1 = input salah / error

Catatan:
    - Tahun input = tahun lunar (bukan 民國). Konversi 民國: tahun_masehi = minkuo + 1911
    - Bulan kabisat (閏月): pakai negatif, contoh bulan kabisat 4 → -4
    - Library: lunar-python 1.4.8 (sudah installed)
"""

import sys
from lunar_python import Lunar


def lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int) -> str:
    """
    Convert Chinese lunar date to solar (Gregorian) date string YYYY-MM-DD.
    lunar_month negative = leap month (閏月), e.g. -4 = leap 4th month.
    Raises ValueError with descriptive message on invalid input.
    """
    try:
        l = Lunar.fromYmd(lunar_year, lunar_month, lunar_day)
        s = l.getSolar()
        return f"{s.getYear()}-{s.getMonth():02d}-{s.getDay():02d}"
    except Exception as e:
        raise ValueError(
            f"Gagal konversi 農曆 {lunar_year}/{lunar_month}/{lunar_day}: {e}"
        )


def minkuo_to_western(minkuo_year: int) -> int:
    """民國 year → Western year. e.g. 民國42 → 1953"""
    return minkuo_year + 1911


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python lunar_convert.py <lunar_year> <lunar_month> <lunar_day>")
        print("       Leap month: pakai negatif, e.g. -4 untuk bulan kabisat 4")
        print("       Minkuo conversion: tahun_minkuo + 1911 = tahun Masehi")
        sys.exit(1)

    try:
        ly = int(sys.argv[1])
        lm = int(sys.argv[2])
        ld = int(sys.argv[3])
    except ValueError:
        print(f"ERROR: input harus integer, dapat: {sys.argv[1:]}", file=sys.stderr)
        sys.exit(1)

    try:
        result = lunar_to_solar(ly, lm, ld)
        print(result)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
