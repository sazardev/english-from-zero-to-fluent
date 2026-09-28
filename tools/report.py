#!/usr/bin/env python3
"""Report the figures for a built book: documents, pages, words, sizes.

Shared by build.sh and verify.py so the numbers in the README, in the
commit messages and in the release notes all come from one place and
cannot drift.

usage: report.py <out-base>
"""
import re
import subprocess
import sys
from pathlib import Path


def pages(pdf):
    """Largest /Count in the file, which is the page tree root."""
    raw = Path(pdf).read_bytes()
    c = [int(x) for x in re.findall(rb"/Count (\d+)", raw)]
    return max(c) if c else 0


def words(pdf):
    """Word count from the rendered text, which is what a reader sees."""
    if not shutil_which("pdftotext"):
        return 0
    r = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True)
    return len(re.findall(r"\S+", r.stdout)) if r.returncode == 0 else 0


def shutil_which(name):
    from shutil import which
    return which(name)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "out/english-from-zero-to-fluent"
    pdf, ep = Path(base + ".pdf"), Path(base + ".epub")
    if not pdf.exists():
        print(f"  no pdf at {pdf}")
        return 1
    print(f"  {pdf.name}  {pages(pdf)} pages  {pdf.stat().st_size/1e6:.1f} MB"
          f"  {words(pdf):,} words")
    if ep.exists():
        print(f"  {ep.name}  {ep.stat().st_size/1e3:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
