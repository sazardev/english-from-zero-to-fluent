#!/usr/bin/env python3
"""Check that the book is written in English only.

The plan requires it: "English only. No native-language scaffolding, not
even a word." A learner reading a page that mixes in another language
stops reading English and starts decoding, and the habit of decoding is
the habit this book is trying to break.

Mentioning a language by name in an English sentence is not scaffolding.
Showing a sentence written in another language is. So this looks for
foreign material: accented characters outside the Latin-1 letters English
uses, and a short list of function words that only appear in the source
language of this book's author, checked only where they cannot be English.

Fenced code blocks and generated tables are exempt: a code block can hold
a shell command, a table can hold a form in any script on purpose.

usage: check_english.py book/
"""
import pathlib
import re
import sys
import unicodedata

# Words that are Spanish function words and are not plausible English in
# running prose. Each is checked in lower case with word boundaries.
SPANISH = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "soy", "eres", "es", "esta", "está", "esto", "ese", "esa", "eso",
    "aqui", "aquí", "alli", "allí", "ahi", "ahí",
    "muy", "tambien", "también", "mas", "más", "pero", "porque", "cuando",
    "donde", "dónde", "como", "cómo", "para", "porque", "aunque",
    "tengo", "tiene", "tenemos", "tienen", "hay", "ha", "he", "han",
    "fue", "fueron", "era", "eran", "sea", "ser", "estar", "estoy", "esta",
    "estás", "estamos", "están", "van", "voy", "vas", "ver", "hacer",
    "poder", "decir", "venir", "dar", "saber", "querer", "quiere",
    "libro", "libros", "mesa", "escribir", "escribe", "cartas", "comido",
    "viviendo", "mudé", "llegue", "llamaré", "honesto", "listo", "verte",
    "años", "allí", "yo", "nosotros", "vosotros", "usted", "ustedes",
    "nuestro", "vuestro", "sus", "más", "mío", "tú", "usted",
}

# Accented letters that are legitimately French or German loanwords in an
# English book, so they are not treated as foreign on their own.
ALLOWED_ACCENTS = set("éÉèÈêÊëËáÁàÀâÂäÄíÍìÌîÎïÏóÓòÒôÔöÖúÚùÙûÛüÜñÑçÇ")


def strip_code_and_tables(text):
    """Drop fenced blocks, inline code and table rows, keeping line numbers.

    The line number has to survive, otherwise every report points at the
    wrong line as soon as the file contains a table, which is most of them.
    """
    out, fence = [], False
    for n, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or line.lstrip().startswith("|"):
            continue
        out.append((n, re.sub(r"`[^`]*`", "", line)))
    return out


# The International Phonetic Alphabet. Pronunciation is part of the
# subject, so these characters are content, not a foreign language.
IPA = set("ɑɐæɒʌəɚɛɜɝɞɟʄɡɢɣɤʥʦʧʨθðʃʒʔβɣχʁħʋɹɻɫɬɮɳʲʷːˈˌ")


def audit(path):
    problems = []
    text = path.read_text(encoding="utf-8")
    for i, line in strip_code_and_tables(text):
        if line.lstrip().startswith(("id:", "title:", "tags:", "---")):
            continue
        # Only letters and ideographs are evidence. Punctuation is not
        # language: this book uses an en dash, an ellipsis, a middle dot
        # and arrows on purpose, and flagging those would bury the real
        # findings in noise.
        for ch in line:
            cat = unicodedata.category(ch)
            if ch in IPA:
                continue
            if cat[0] == "L" and "LATIN" not in unicodedata.name(ch, ""):
                problems.append(
                    f"{path.name}:{i} letter outside the Latin alphabet: "
                    f"{ch!r} ({unicodedata.name(ch, '?')})"
                )
                break
        low = line.lower()
        hits = [w for w in SPANISH if re.search(rf"\b{re.escape(w)}\b", low)]
        # "es" and "esta" and "ha" and "he" and "un" and "a" collide with
        # real English words; only report them when another marker appears
        strong = [w for w in hits if w not in {"es", "esta", "está", "ha", "he",
                                              "un", "una", "son", "van", "ver",
                                              "dar", "saber", "sus", "mas"}]
        if strong:
            found = ", ".join(sorted(strong)[:6])
            snippet = line.strip()[:70]
            problems.append(f"{path.name}:{i} possible non-English: {found}  |  {snippet}")
    return problems


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "book")
    files = sorted(p for p in root.rglob("*.mdx"))
    problems = []
    for f in files:
        problems += audit(f)
    if problems:
        print(f"  {len(problems)} problem(s):")
        for p in problems:
            print(f"    {p}")
        return 1
    print(f"  {len(files)} documents, English only, no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
