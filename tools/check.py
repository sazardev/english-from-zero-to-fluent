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

def slug(h):
    s = re.sub(r"<[^>]+>", "", h.lower())
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())


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

# Heading slugs become anchor ids. Each MDX file is one document, so an
# anchor only has to be unique inside its own file, and a duplicate there
# breaks that file's table of contents and every link pointing at it. This
# is what the flashcard chapters were doing, with the same sub-deck name
# eleven times in one file.
#
# The h1 is different: it becomes the chapter title in the book's table of
# contents, so two h1s with the same words would give the contents two
# identical entries. That is checked across every file.
slugs = collections.defaultdict(list)
titles = collections.defaultdict(list)
for f in files:
    for i, l in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if not m:
            continue
        level, s = len(m.group(1)), slug(m.group(2))
        if level == 1:
            titles[s].append(f"{f.name}:{i}")
        else:
            slugs[(f.name, s)].append(i)
for (name, s), v in sorted(slugs.items()):
    if len(v) > 1:
        problems.append(
            f"{name}: heading {s!r} used {len(v)} times (lines "
            f"{', '.join(str(x) for x in v[:6])}); a repeated anchor id breaks "
            f"this chapter's own contents"
        )
for s, v in sorted(titles.items()):
    if len(v) > 1:
        problems.append(f"duplicate chapter title {s!r}: {', '.join(v)}")

# pretty-converter's page-break-inside-risk warning was originally blamed
# on fenced blocks of twelve lines or more, and a limit was written here to
# catch them. That limit was a coincidence: the same document with one
# fewer line of prose stopped warning, and a seven-line block warned once
# the text above it grew. The warning is a layout heuristic about where a
# block lands in the rendered page, it ignores the theme's CSS, and it
# fires differently for the same content on a different theme. There is
# no content rule that predicts it, so a content rule would be a guess.
# The build audit is advisory and the expectation is recorded in
# go-pretty-converter.yml instead.

if problems:
    print(f"  {len(problems)} problem(s):")
    for p in problems[:25]:
        print(f"    {p}")
    sys.exit(1)
print(f"  {len(files)} documents, {len(ids)} unique ids, no problems")
sys.exit(0)
