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

# Heading slugs become anchor ids, and the renderer uses one id space for
# the whole book, not one per file. The build audit reports a duplicate id
# across any two files, so a heading repeated in two chapters is a real
# fault and not a stylistic choice: it makes the book's contents offer two
# identical anchors and breaks every link to either.
#
# The recurring chapter-ending section is the usual offender, which is
# why the fix is to name it after the chapter's subject. Two chapters can
# each have a section about their own mistakes, but not with the same
# words.
slugs = collections.defaultdict(list)
for f in files:
    for i, l in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m:
            slugs[slug(m.group(2))].append(f"{f.name}:{i}")
for s, v in sorted(slugs.items()):
    if len(v) > 1:
        hint = " (rename it after this chapter's subject)" if s in (
            "four-things-learners-get-wrong", "common-mistakes",
            "when-problems-arise", "summary") else ""
        if re.fullmatch(r"\d+-.+", s) and "answered" not in s:
            # An answer key repeats the exercise headings on purpose, so
            # the fix is a marker on the answer side: "## 3. Articles —
            # answered".
            hint = " (this looks like an answer key echoing the exercises; add \"— answered\")"
        problems.append(
            f"duplicate heading {s!r}{hint}: {', '.join(v[:6])}"
        )

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
