#!/usr/bin/env python3
"""Write and verify the PDF document metadata.

The renderer does not set the PDF's author, subject or keywords. It builds
an HTML page with <title> and <meta name="author"> and lets Chrome derive
the document info dictionary from that, which works for the body pages
and fails for this book in two ways:

1. The cover is rendered from its own minimal HTML, built in
   render/cover.go, which has a <meta charset> and no <title> at all. That
   page is merged in first, so the merged document inherits the temporary
   filename Chrome was given as its title: "go-pretty-converter-12345.html".

2. Chrome stamps itself as the creator, so the metadata names a headless
   browser rather than the tool or the author.

Neither is fixable from the command line, because neither --title nor
--author is routed into the cover's HTML. So the info dictionary is
written here instead, with qpdf, after the render.

qpdf's --update-from-json replaces the whole object, so this reads the
existing dictionary first and merges into it. That preserves /Title when
it is right and keeps the object's other keys, and it means the tool is
idempotent: running it twice produces the same file.

usage: metadata.py <pdf> [--verify]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TITLE = "The Complete English Course"
SUBTITLE = ("From Zero to Fluent — Grammar, Reading, Writing and "
            "5,471 Flashcards in One Volume")
AUTHOR = "Omar Flores"
SUBJECT = ("A complete self-study English course from A2 to C1: grammar, "
           "verb forms, the sentence, vocabulary and register, reading, "
           "writing, 415 irregular verbs, 5,471 flashcards, exercises and "
           "answer keys.")
KEYWORDS = [
    "english", "english course", "learn english", "english grammar",
    "english for beginners", "self-study", "cefr", "a2", "b1", "b2", "c1",
    "irregular verbs", "english vocabulary", "english writing",
    "english reading", "english exercises", "flashcards", "spaced repetition",
    "open textbook", "free ebook", "mit licence",
]
CREATOR = "The Complete English Course — built with go-pretty-converter"
PRODUCER = "go-pretty-converter (skia/pdf) · qpdf metadata pass"

FIELDS = {
    "/Title": TITLE,
    "/Subject": SUBJECT,
    "/Keywords": ", ".join(KEYWORDS),
    "/Author": AUTHOR,
    "/Creator": CREATOR,
    "/Producer": PRODUCER,
}


def find_info_object(doc):
    """The document info dictionary is the object holding /CreationDate.

    Its object number is not guaranteed, so it is found by content rather
    than assumed to be 1 0 R. Assuming is what produced a PDF whose title
    was a temporary filename.
    """
    for obj in doc.get("qpdf", [])[1:]:
        for key, val in obj.items():
            if not key.startswith("obj:"):
                continue
            inner = val.get("value") if isinstance(val, dict) else None
            if isinstance(inner, dict) and ("/CreationDate" in inner
                                            or "/Producer" in inner):
                return key, inner
    return None, None


def load(pdf):
    r = subprocess.run(["qpdf", "--json", str(pdf)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"qpdf could not read {pdf}: {r.stderr.strip()}")
    return json.loads(r.stdout)


def write(pdf, key, existing):
    merged = dict(existing)
    for k, v in FIELDS.items():
        merged[k] = "u:" + v
    payload = {"qpdf": [{"jsonversion": 2}, {key: {"value": merged}}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp = Path(f.name)
    out = pdf.with_suffix(".pdf.tmp")
    # qpdf 12 wants --opt=value for the file-taking options; the split
    # form was removed and it is not a deprecation warning, it is an error.
    r = subprocess.run(["qpdf", f"--update-from-json={tmp}",
                        "--deterministic-id", str(pdf), str(out)],
                       capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        out.unlink(missing_ok=True)
        sys.exit(f"qpdf could not write {pdf}: {r.stderr.strip()}")
    out.replace(pdf)


def read_fields(pdf):
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    got = {}
    for line in r.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            got[k.strip()] = v.strip()
    return got


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: metadata.py <pdf> [--verify]")
    pdf = Path(sys.argv[1])

    if "--verify" not in sys.argv:
        doc = load(pdf)
        key, existing = find_info_object(doc)
        if key is None:
            sys.exit(f"no document info dictionary found in {pdf}")
        write(pdf, key, existing)

    got = read_fields(pdf)
    want = {"Title": TITLE, "Author": AUTHOR, "Subject": SUBJECT,
            "Keywords": ", ".join(KEYWORDS)}
    bad = []
    for k, v in want.items():
        ok = got.get(k) == v
        print(f"  {'ok ' if ok else 'BAD'}  {k}: {got.get(k, '(missing)')[:70]}")
        if not ok:
            bad.append(k)
    pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    for line in pages.stdout.splitlines():
        if line.startswith(("Pages:", "Page size:")):
            print(f"  {line}")
    if bad:
        sys.exit(f"metadata wrong or missing: {', '.join(bad)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
