#!/usr/bin/env python3
"""Build the book and report pages, words and warnings.

One command, so the page count in the README is never a guess.
"""
import re
import subprocess
import sys
from pathlib import Path

def pages(pdf):
    raw = Path(pdf).read_bytes()
    c = [int(x) for x in re.findall(rb"/Count (\d+)", raw)]
    return max(c) if c else 0

def main():
    src, out, theme = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "academic")
    r = subprocess.run(
        ["pretty-converter", "build", "--source", src, "--out", out, "--theme", theme],
        capture_output=True, text=True)
    warn = [l.strip() for l in r.stdout.splitlines() if "⚠" in l]
    m = re.search(r"Documents:\s*(\d+)", r.stdout)
    print(f"  documents: {m.group(1) if m else '?'}")
    print(f"  pages:     {pages(out + '.pdf')}")
    print(f"  warnings:  {len(warn)}")
    for w in warn[:5]:
        print(f"    {w}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
