"""
classify_and_split.py - Prepare and apply photo classification into data/ and transelate/ subfolders.

Usage:
  python classify_and_split.py <photos_dir>           # prepare if not done, then apply if result exists
  python classify_and_split.py <photos_dir> --prepare # only write pending_classify.json
  python classify_and_split.py <photos_dir> --apply   # only apply classify_result.json (move files)
"""

import sys
import os
import json
import shutil
from pathlib import Path

SUPPORTED_EXTS = {".jpeg", ".jpg", ".png", ".webp"}
AUDIT_DIR = "_AUDIT_LOGS"
PENDING_FILE = "pending_classify.json"
RESULT_FILE = "classify_result.json"
DATA_SUBDIR = "data"
TRANSLATE_SUBDIR = "transelate"


def err(msg: str) -> None:
    print(f"[ERR] {msg}", file=sys.stderr)


def scan_photos(photos_dir: Path) -> list[str]:
    """Return sorted list of photo filenames (top-level only, supported extensions)."""
    files = []
    try:
        for entry in photos_dir.iterdir():
            if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTS:
                files.append(entry.name)
    except PermissionError as e:
        err(f"Cannot read directory {photos_dir}: {e}")
        sys.exit(1)
    return sorted(files)


def is_already_classified(photos_dir: Path) -> bool:
    """
    Return True if data/ and transelate/ both exist AND at least one of them
    contains at least one photo file.
    """
    data_dir = photos_dir / DATA_SUBDIR
    translate_dir = photos_dir / TRANSLATE_SUBDIR

    if not data_dir.is_dir() or not translate_dir.is_dir():
        return False

    def has_photos(d: Path) -> bool:
        return any(
            f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
            for f in d.iterdir()
        )

    try:
        return has_photos(data_dir) or has_photos(translate_dir)
    except PermissionError:
        return False


def ensure_dirs(photos_dir: Path) -> tuple[Path, Path, Path]:
    """Create data/, transelate/, _AUDIT_LOGS/ if not present. Return (data, translate, audit) paths."""
    data_dir = photos_dir / DATA_SUBDIR
    translate_dir = photos_dir / TRANSLATE_SUBDIR
    audit_dir = photos_dir / AUDIT_DIR

    for d in (data_dir, translate_dir, audit_dir):
        d.mkdir(exist_ok=True)

    return data_dir, translate_dir, audit_dir


def write_pending(photos_dir: Path, photo_names: list[str]) -> Path:
    """Write pending_classify.json. Returns path to the file."""
    _, _, audit_dir = ensure_dirs(photos_dir)
    pending_path = audit_dir / PENDING_FILE

    payload = {
        "photos_dir": str(photos_dir),
        "photos": photo_names,
        "instruction": (
            "For each photo, classify as 'data' (grid/table/list) or 'transelate' "
            "(paragraph narrative text). Write classify_result.json in the same "
            "_AUDIT_LOGS/ folder with schema: "
            "{\"results\": [{\"filename\": \"...\", \"class\": \"data\"|\"transelate\"}]}"
        ),
    }

    with open(pending_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return pending_path


def load_result(photos_dir: Path) -> dict | None:
    """Load classify_result.json. Returns None if not found."""
    result_path = photos_dir / AUDIT_DIR / RESULT_FILE
    if not result_path.exists():
        return None
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        err(f"Cannot read {result_path}: {e}")
        sys.exit(1)


def apply_classification(photos_dir: Path, result: dict) -> None:
    """Move files according to classify_result.json."""
    entries = result.get("results")
    if not isinstance(entries, list):
        err("classify_result.json must have a 'results' list")
        sys.exit(1)

    data_dir = photos_dir / DATA_SUBDIR
    translate_dir = photos_dir / TRANSLATE_SUBDIR

    # ensure target dirs exist
    data_dir.mkdir(exist_ok=True)
    translate_dir.mkdir(exist_ok=True)

    moved_data = 0
    moved_translate = 0
    skipped = 0
    errors = 0

    for entry in entries:
        if not isinstance(entry, dict):
            err(f"Invalid entry in results: {entry!r}")
            errors += 1
            continue

        filename = entry.get("filename")
        cls = entry.get("class")

        if not filename or cls not in ("data", "transelate"):
            err(f"Skipping invalid entry: {entry!r}")
            errors += 1
            continue

        src = photos_dir / filename
        if not src.exists():
            err(f"Source file not found, skipping: {src}")
            errors += 1
            continue

        if cls == "data":
            dest = data_dir / filename
            moved_data += 1
        else:
            dest = translate_dir / filename
            moved_translate += 1

        if dest.exists():
            # file already in target — skip move
            skipped += 1
            if cls == "data":
                moved_data -= 1
            else:
                moved_translate -= 1
            continue

        try:
            shutil.move(str(src), str(dest))
        except (OSError, shutil.Error) as e:
            err(f"Failed to move {filename}: {e}")
            errors += 1
            if cls == "data":
                moved_data -= 1
            else:
                moved_translate -= 1

    summary_parts = [f"[APPLY] Moved {moved_data} to data/, {moved_translate} to transelate/"]
    if skipped:
        summary_parts.append(f"{skipped} already in target (skipped)")
    if errors:
        summary_parts.append(f"{errors} error(s) — check stderr")
    print(". ".join(summary_parts) + ".")


def cmd_prepare(photos_dir: Path) -> None:
    photos = scan_photos(photos_dir)
    if not photos:
        print(f"[ERR] No supported photos found in {photos_dir}")
        sys.exit(1)

    pending_path = write_pending(photos_dir, photos)
    print(
        f"[CLASSIFY] {len(photos)} photos need classification "
        f"-> {pending_path}"
    )


def cmd_apply(photos_dir: Path) -> None:
    result = load_result(photos_dir)
    if result is None:
        err(
            f"classify_result.json not found in {photos_dir / AUDIT_DIR}. "
            "Run --prepare first and let the AI agent write the result."
        )
        sys.exit(1)
    apply_classification(photos_dir, result)


def cmd_auto(photos_dir: Path) -> None:
    """Default: prepare if needed, apply if result exists."""
    if is_already_classified(photos_dir):
        print("[SKIP] Already classified (idempotent).")
        return

    result = load_result(photos_dir)

    if result is None:
        # No result yet — just prepare
        cmd_prepare(photos_dir)
    else:
        # Result available — apply
        cmd_apply(photos_dir)


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    mode = None
    photos_dir_str = None

    for arg in args:
        if arg in ("--prepare", "--apply"):
            mode = arg
        elif not arg.startswith("--"):
            photos_dir_str = arg
        else:
            err(f"Unknown flag: {arg}")
            sys.exit(1)

    if photos_dir_str is None:
        err("photos_dir argument is required")
        sys.exit(1)

    photos_dir = Path(photos_dir_str).resolve()

    if not photos_dir.exists():
        err(f"Directory does not exist: {photos_dir}")
        sys.exit(1)

    if not photos_dir.is_dir():
        err(f"Not a directory: {photos_dir}")
        sys.exit(1)

    if mode == "--prepare":
        cmd_prepare(photos_dir)
    elif mode == "--apply":
        cmd_apply(photos_dir)
    else:
        cmd_auto(photos_dir)


if __name__ == "__main__":
    main()
