#!/usr/bin/env bash
# build.sh - regenerate everything and ship the book.
#
#   ./build.sh          check, generate, build PDF + EPUB
#   ./build.sh check    run the pre-build checks only
#   ./build.sh fast     skip the header, page numbers and outline
#
# The generators read from the sibling repository, because that is where
# the master dataset lives. Everything in the reference half of this book
# is derived from it, so the book, the website, the CLI and the Anki deck
# cannot disagree.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"
BOOK=book
UPSTREAM="${UPSTREAM:-$HOME/Work/omarchy-english-toolkit}"
VERBS="$UPSTREAM/docs/data/verbs.json"
DECK="${ANKI_COLLECTION:-$HOME/.local/share/Anki2/User 1/collection.anki2}"
FORMAT="${FORMAT:-pdf,epub}"
THEME="${THEME:-academic}"
OUT="${OUT:-out/english-from-zero-to-fluent}"

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
die() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

# only the English chapters of the deck; the live collection also holds
# Physics, CS, QC and QM, which are a different subject
ONLY="$(python3 -c "print(','.join([f'{i:02d}' for i in range(1,26)]+['Irregular','Regular','Reference']))")"

# ------------------------------------------------------------------- checks
say "Pre-build checks"
python3 tools/check.py "$BOOK" || die "source problems, not building"

if [[ ${1:-} == check ]]; then exit 0; fi

# ---------------------------------------------------------------- generation
if [[ -f $VERBS ]]; then
  say "Generating the reference chapters"
  python3 tools/gen_reference.py "$VERBS" "$BOOK"
else
  say "No verbs.json at $VERBS, keeping the existing reference"
fi

say "Generating the grammar tables"
python3 tools/gen_grammar.py "$BOOK" >/dev/null

if [[ -f $DECK ]]; then
  say "Generating the practice chapters from the Anki deck"
  rm -f "$BOOK"/9-*.mdx
  python3 tools/gen_flashcards.py "$DECK" "$BOOK" --only "$ONLY" | tail -2
else
  say "No collection at $DECK, keeping the existing practice chapters"
fi

say "Re-checking after generation"
python3 tools/check.py "$BOOK" || die "generation produced problems"

# --------------------------------------------------------------------- build
say "Analyse"
pretty-converter analyze --source "$BOOK" | tail -6

mkdir -p "$(dirname "$OUT")"
say "Building: $FORMAT, theme $THEME"
FAST=""
[[ ${1:-} == fast ]] && FAST="--fast"
# shellcheck disable=SC2086
pretty-converter build \
  --source "$BOOK" \
  --out "$OUT" \
  --theme "$THEME" \
  --format "$FORMAT" \
  --title "English: From Zero to Fluent" \
  --subtitle "A complete, planned course in one volume" \
  $FAST

say "Result"
python3 - "$OUT" <<'PY'
import re, sys
from pathlib import Path
base = sys.argv[1]
for ext in (".pdf", ".epub"):
    p = Path(base + ext)
    if not p.exists():
        continue
    size = f"{p.stat().st_size/1024/1024:.1f} MB"
    if ext == ".pdf":
        pages = [int(x) for x in re.findall(rb"/Count (\d+)", p.read_bytes())]
        print(f"  {p.name}  {max(pages) if pages else '?'} pages  {size}")
    else:
        print(f"  {p.name}  {size}")
PY

say "Done"
echo "  open:  $OUT.pdf"
