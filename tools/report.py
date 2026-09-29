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
    """Page count.

    The /Count in the page tree root used to be enough. It stopped being
    enough when a cover page was added, because the renderer merges two
    PDFs and the result has more than one /Count, none of which is the
    total. qpdf --show-npages walks the tree and is not fooled by that, so
    it is asked first and the regex is only a fallback for when qpdf is
    missing.
    """
    try:
        r = subprocess.run(["qpdf", "--show-npages", pdf],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return int(r.stdout.strip())
    except FileNotFoundError:
        pass
    raw = Path(pdf).read_bytes()
    c = [int(x) for x in re.findall(rb"/Count (\d+)", raw)]
    return max(c) if c else 0


def page_size(pdf):
    """First page size in points, from pdfinfo, which reads the first
    MediaBox rather than averaging."""
    r = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("Page size:"):
            pts = line.split(":", 1)[1].split("pts")[0].strip()
            try:
                w, h = (float(x) for x in pts.split("x"))
                return f"{w/72:.1f} x {h/72:.1f} in"
            except ValueError:
                return pts
    return "?"


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
    print(f"  {pdf.name}  {pages(pdf)} pages  {page_size(pdf)}  "
          f"{pdf.stat().st_size/1e6:.1f} MB  {words(pdf):,} words")
    if ep.exists():
        print(f"  {ep.name}  {ep.stat().st_size/1e3:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
