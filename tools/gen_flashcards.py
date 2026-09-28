#!/usr/bin/env python3
"""Turn the Anki deck into printable chapters.

The deck already holds 5,822 notes, each verified by the linter and each
a piece of content somebody needed. Dumping them as flashcards is not
padding: it is the same material in a form you can read on paper, which
is what the book needs for learners who do not want Anki open.

Three shapes, because three shapes train three different things:

  * gap       cue plus answer, the recognition direction
  * production  a frame to fill, the recall direction
  * reference   tables and lists, to consult not to memorise

usage: gen_flashcards.py <deck.apkg> <out-dir> [--part 9]
"""
import argparse
import html
import re
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path


def strip(s):
    # <code> inside a table cell can be split across a page, which the
    # renderer flags. Inline code in a table gains nothing, so drop the tag
    # and keep the text.
    s = re.sub(r"</?code[^>]*>", "", s or "")
    s = re.sub(r"<br\s*/?>", " ", s or "")
    s = re.sub(r"</(p|div|li|tr)>", " | ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s*\|\s*", " · ", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip(" ·|")


def md(s):
    """Re-introduce the little Markdown that survives stripping."""
    s = strip(s)
    s = s.replace("  ", " ")
    return s


def open_deck(path):
    """Open a collection. The .apkg uses the pre-2.1.50 schema with no decks
    table, so deck names live in a column on cards; the live collection has
    the current schema. Both are handled here."""
    if str(path).endswith(".anki2"):
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    else:
        z = zipfile.ZipFile(path)
        names = [n for n in z.namelist() if n.endswith(".anki2")]
        d = tempfile.mkdtemp()
        z.extract(names[0], d)
        con = sqlite3.connect(Path(d) / names[0])
    con.create_collation("unicase",
                         lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
    if not con.execute(
            "select count(*) from sqlite_master where type='table' and name='decks'"
    ).fetchone()[0]:
        sys.exit(
            f"  {path} uses the legacy schema with no decks table.\n"
            "  Pass the live collection instead:\n"
            r"    gen_flashcards.py ~/.local/share/Anki2/User 1/collection.anki2")
    return con


def decks(con):
    return [(i, n) for i, n in con.execute(
        "select id, name from decks order by name")]


def notes_for(con, did):
    rows = con.execute(
        "select n.flds from notes n join cards c on c.nid = n.id where c.did = ?",
        (did,)).fetchall()
    return [r[0].split("\x1f") for r in rows]


def render(fields, kind):
    """Return markdown for one note, or '' if it has no usable content."""
    f = [md(x) for x in fields]
    if not any(f):
        return ""
    # cloze: the marked span is the answer
    has_cloze = any(re.search(r"\{\{c\d+::", x or "") for x in fields)
    if has_cloze:
        text = f[0]
        # show each cloze as: sentence with ___ for the first, then an answer line
        out = re.sub(r"\{\{c\d+::(.+?)\}\}", r"___\1__", text)
        answers = re.findall(r"\{\{c\d+::(.+?)\}\}", text)
        if len(answers) == 1:
            out = re.sub(r"___(.+?)__", "___", text)
            return f"{out}\n\n**Answer:** {answers[0]}"
        lines = [re.sub(r"\{\{c\d+::(.+?)\}\}", "___", text)]
        for i, a in enumerate(answers, 1):
            lines.append(f"{i}. **{a}**")
        return "\n".join(lines)

    if len(f) >= 2 and f[0] and f[1]:
        extra = []
        for x in f[2:]:
            if x and len(x) > 2 and not x.startswith("<"):
                extra.append(x)
        body = f"| cue | answer |\n|---|---|\n| {f[0]} | {f[1]} |"
        if extra:
            body += "\n\n" + extra[0]
        return body
    # single-field: a reference table or a definition
    if f[0] and "<table" in (fields[0] or ""):
        return fields[0]
    return f[0] if f[0] else ""


def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("outdir")
    ap.add_argument("--part", default="9")
    ap.add_argument("--only", help="comma-separated deck prefixes to keep")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None

    con = open_deck(a.deck)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    # group by top-level chapter ("16 Irregular Verbs::Irregular Forms")
    groups = {}
    for did, name in decks(con):
        if not name:
            continue
        top = name.split("\x1f")[0]
        groups.setdefault(top, []).append((did, name))

    total_notes = 0
    total_words = 0
    seq = 0
    manifest = []
    # the live collection also holds other subjects: Physics, CS, QC, QM
    only_english = only or set()
    for top in sorted(groups, key=lambda s: (len(s), s)):
        if only_english and not any(top.startswith(x) for x in only_english):
            continue
        chunk = groups[top]
        n = sum(len(notes_for(con, did)) for did, _ in chunk)
        total_notes += n
        if n == 0:
            continue
        seq += 1
        # split very large chapters so no single document is unwieldy
        MAX = 220
        batches = []
        cur, cnt = [], 0
        for did, name in chunk:
            notes = notes_for(con, did)
            for flds in notes:
                body = render(flds, top)
                if not body:
                    continue
                cur.append((name.split("\x1f")[-1], body))
                cnt += 1
                if cnt >= MAX:
                    batches.append(cur)
                    cur, cnt = [], 0
        if cur:
            batches.append(cur)

        for bi, batch in enumerate(batches):
            # Every document is a slice of one deck, so the deck name
            # alone repeats across the slice and across the deck's own
            # sub-decks. The slice number makes each heading unique, which
            # the table of contents and every internal link need.
            part = f", part {bi+1} of {len(batches)}" if len(batches) > 1 else ""
            title = top + part
            nav = f"{top} ({bi+1}/{len(batches)})"
            docid = f"{a.part}.{seq}.{bi+1}"
            fname = f"{a.part}-{seq:02d}-{bi+1}-{slug(top)[:40]}.mdx"
            body = [f"# {title}", ""]
            if len(batches) > 1:
                body.append(f"*Page {bi+1} of {len(batches)} for {top}*")
                body.append("")
            # Navigation matters for EPUB and Kindle: one MDX file is one
            # nav entry, so a chapter with no h2 has no in-chapter
            # navigation. A heading every twenty cards gives the reader
            # somewhere to jump to. One heading per note would be useless
            # noise and would repeat the sub-deck name, which breaks the
            # table of contents, so the deck, the slice and the block
            # number all go into the heading to keep it unique.
            n = 0
            for deckname, card in batch:
                if n % 20 == 0:
                    body.append(f"## {deckname} {nav}, block {n // 20 + 1}")
                    body.append("")
                n += 1
                body.append(card)
                body.append("")
            text = (f'---\nid: "[{docid}]"\ntitle: {title}\n---\n\n'
                    + "\n".join(body).rstrip() + "\n")
            w = len(text.split())
            total_words += w
            (out / fname).write_text(text, encoding="utf-8")
            manifest.append((docid, title, w, fname))

    print(f"  {total_notes} notes -> {len(manifest)} documents, {total_words:,} words")
    for docid, title, w, f in manifest[:6]:
        print(f"    [{docid}] {w:5,}w  {title[:50]}")
    if len(manifest) > 6:
        print(f"    ... and {len(manifest)-6} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
