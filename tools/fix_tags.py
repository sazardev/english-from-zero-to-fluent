#!/usr/bin/env python3
"""Balance the custom block tags in a set of MDX files.

The renderer tolerates mismatched tags, but the audit does not, and a
mismatched tag is invisible when reading the source. A tag that opens
on one line must close with the same tag; anything else is a slip.

Walks each file in order, tracking depth per tag, and rewrites a closing
tag whose matching tag is different. It never adds or removes a block,
only fixes which name it closes with.

usage: fix_tags.py file.mdx [file.mdx ...]
"""
import re
import sys
from pathlib import Path

TAGS = ("Warning", "DeepDive", "Axiom", "Note")
LINE = re.compile(rf"\A\s*(?P<close></(?P<ctag>{'|'.join(TAGS)})>)\s*\Z")


def fix(path):
    p = Path(path)
    lines = p.read_text(encoding="utf-8").split("\n")
    out = []
    stack = []
    fixed = 0

    for l in lines:
        m = LINE.match(l)
        if m:
            if stack and stack[-1] != m.group("ctag"):
                out.append(l.replace(f"</{m.group('ctag')}>", f"</{stack[-1]}>"))
                stack.pop()
                fixed += 1
            else:
                if not stack:
                    print(f"  {p.name}: stray </{m.group('ctag')}>", file=sys.stderr)
                else:
                    stack.pop()
                out.append(l)
            continue
        for t in TAGS:
            if re.search(rf"<{t}>", l):
                stack.append(t)
                break
        out.append(l)

    if stack:
        # a tag left open at the end: close it after the last content line
        idx = max((i for i, l in enumerate(out) if l.strip()), default=len(out) - 1)
        for t in reversed(stack):
            out.insert(idx + 1, f"</{t}>")
            fixed += 1

    p.write_text("\n".join(out), encoding="utf-8")
    print(f"  {p.name}: {fixed} tag(s) rebalanced")
    return fixed


if __name__ == "__main__":
    total = sum(fix(f) for f in sys.argv[1:])
    sys.exit(0 if total >= 0 else 1)
