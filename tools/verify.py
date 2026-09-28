#!/usr/bin/env python3
"""Build the book and report pages, words and warnings.

One command, so the figures in the README are never a guess. The output
path is the base name pretty-converter uses, without an extension, because
the tool writes <out>.pdf and <out>.epub and passing an extension makes it
write <out>.pdf.pdf.

usage: verify.py [source] [out-base] [theme]
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from report import pages, words  # noqa: E402


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "book"
    out = sys.argv[2] if len(sys.argv) > 2 else "out/english-from-zero-to-fluent"
    theme = sys.argv[3] if len(sys.argv) > 3 else "academic-print"

    r = subprocess.run(
        ["pretty-converter", "build", "--source", src, "--out", out, "--theme", theme],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
        return r.returncode

    warn = sorted({l.strip() for l in r.stdout.splitlines() if "⚠" in l})
    m = re.search(r"Documents:\s*(\d+)", r.stdout)
    pdf = out + ".pdf"
    ep = out + ".epub"

    print(f"  documents: {m.group(1) if m else '?'}")
    print(f"  pages:     {pages(pdf)}")
    print(f"  words:     {words(pdf):,}")
    print(f"  pdf:       {Path(pdf).stat().st_size / 1e6:.1f} MB")
    if Path(ep).exists():
        print(f"  epub:      {Path(ep).stat().st_size / 1e3:.0f} KB")
    print(f"  warnings:  {len(warn)}")
    for w in warn[:8]:
        print(f"    {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
