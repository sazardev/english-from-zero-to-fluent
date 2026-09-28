#!/usr/bin/env python3
"""Pre-build checks that catch the failures that cost a build.

pretty-converter catches duplicate ids itself, but only at build time and
only the first one. These checks run in a second and list every problem,
so a structural mistake is found before a two-minute render.
"""
import collections
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "book")
problems = []

files = sorted(list(SRC.glob("*.md")) + list(SRC.glob("*.mdx")) + list(SRC.glob("*.txt")))
if not files:
    problems.append("no source documents found")

ids = collections.defaultdict(list)
for f in files:
    t = f.read_text(encoding="utf-8")
    m = re.search(r'id:\s*"\[([\d.]+)\]"', t[:300])
    if m:
        ids[m.group(1)].append(f.name)

for k, v in sorted(ids.items()):
    if len(v) > 1:
        problems.append(f"duplicate id [{k}]: {', '.join(v)}")

for f in files:
    t = f.read_text(encoding="utf-8")
    # ignore the frontmatter block, and match the tags as whole words so
    # <Warning> is not counted inside a longer tag name
    # a tag shown as documentation, as in a table cell writing `<DeepDive>`,
    # is not a real tag. Strip inline code before counting.
    tc = re.sub(r"`[^`]*`", "", t)
    for tag in ("Warning", "DeepDive", "Axiom", "Note"):
        o = len(re.findall(rf"<{tag}>", tc))
        c = len(re.findall(rf"</{tag}>", tc))
        if o != c:
            problems.append(f"{f.name}: unbalanced <{tag}> ({o} open, {c} close)")
    if "\t" in t:
        problems.append(f"{f.name}: contains a literal tab")
    if re.search(r"[ \t]+$", t, re.M):
        problems.append(f"{f.name}: trailing whitespace")

# duplicate heading slugs break the table of contents and every internal
# link that points at them, and the renderer only reports the first
def slug(h):
    s = re.sub(r"<[^>]+>", "", h.lower())
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())

slugs = collections.defaultdict(list)
for f in files:
    for i, l in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m:
            slugs[slug(m.group(2))].append(f"{f.name}:{i}")
for k, v in sorted(slugs.items()):
    if len(v) > 1:
        problems.append(f"duplicate heading slug '{k}': {', '.join(v)}")

if problems:
    print(f"  {len(problems)} problem(s):")
    for p in problems[:25]:
        print(f"    {p}")
    sys.exit(1)
print(f"  {len(files)} documents, {len(ids)} unique ids, no problems")
sys.exit(0)
