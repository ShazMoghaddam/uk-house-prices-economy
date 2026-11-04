"""Checks that keep the repo tidy. Run with: python3 .github/scripts/check_repo.py

1. Every link and image in the Markdown files points at a file that exists.
2. Every Python file is valid Python.
3. Submissions follow the rules in CONTRIBUTING.md: submissions/YYYY-MM/username/,
   a README.md in each folder, no raw data files and under 10MB.

Uses only the standard library, so it runs anywhere without installing anything.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]

# The template's image is a placeholder for people to replace, so it isn't a real link.
SKIP_LINKS_IN = {"SUBMISSION_TEMPLATE.md"}

RAW_DATA = {".csv", ".xlsx", ".xls", ".zip"}
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_FOLDER_BYTES = 10 * 1024 * 1024

MD_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_LINK = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""")
CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")

errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def tracked_files() -> list[Path]:
    skip = {".git", ".venv", "__pycache__", ".ipynb_checkpoints"}
    return [p for p in ROOT.rglob("*") if p.is_file() and not skip & set(p.relative_to(ROOT).parts)]


def check_links(files: list[Path]) -> None:
    for md in (p for p in files if p.suffix.lower() == ".md"):
        if md.name in SKIP_LINKS_IN:
            continue
        text = INLINE_CODE.sub("", CODE_BLOCK.sub("", md.read_text(encoding="utf-8")))
        for target in MD_LINK.findall(text) + HTML_LINK.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                continue  # web links, mailto: and links within the same page
            path = unquote(target.split("#")[0].split("?")[0])
            if not path:
                continue
            resolved = (ROOT / path.lstrip("/")) if path.startswith("/") else (md.parent / path)
            if not resolved.exists():
                errors.append(f"{rel(md)}: broken link to '{target}'")


def check_python(files: list[Path]) -> None:
    for py in (p for p in files if p.suffix == ".py"):
        try:
            compile(py.read_text(encoding="utf-8"), rel(py), "exec")
        except SyntaxError as e:
            errors.append(f"{rel(py)}: line {e.lineno}: {e.msg}")


def check_submissions() -> None:
    subs = ROOT / "submissions"
    if not subs.is_dir():
        return
    for month in sorted(subs.iterdir()):
        if month.name.startswith("."):
            continue
        if not (month.is_dir() and re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month.name)):
            errors.append(f"{rel(month)}: should be a month folder named like submissions/2026-11/")
            continue
        for entry in sorted(month.iterdir()):
            if entry.name.startswith("."):
                continue
            if not entry.is_dir():
                errors.append(f"{rel(entry)}: put your files in a folder named after your GitHub username")
                continue
            files = [p for p in entry.rglob("*") if p.is_file()]
            if not (entry / "README.md").is_file():
                errors.append(f"{rel(entry)}: add a README.md (copy SUBMISSION_TEMPLATE.md)")
            for f in files:
                if f.suffix.lower() in RAW_DATA:
                    errors.append(f"{rel(f)}: don't upload raw data, link to the source instead")
            size = sum(f.stat().st_size for f in files)
            if size > MAX_FOLDER_BYTES:
                errors.append(f"{rel(entry)}: folder is {size / 1024 / 1024:.1f}MB, keep it under 10MB")
            if not any(f.suffix.lower() in IMAGES for f in files):
                warnings.append(f"{rel(entry)}: no image yet, add one so your entry can go in the gallery")


def main() -> int:
    files = tracked_files()
    check_links(files)
    check_python(files)
    check_submissions()
    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")
    if errors:
        print(f"\n{len(errors)} problem(s) found.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
