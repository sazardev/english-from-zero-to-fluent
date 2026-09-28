# English: From Zero to Fluent

A complete English course in one volume. **841 pages**, English only, built
from material that has already been tested.

Built with
[go-pretty-converter](https://github.com/sazardev/go-pretty-converter),
which renders Markdown to an audited PDF and an EPUB 3 through headless
Chrome.

```bash
./build.sh            # check, generate, build PDF + EPUB
open out/english-from-zero-to-fluent.pdf
```

## What is in it

| part | what | pages |
|---|---|---|
| 0 Front matter | how to use the book, the method | ~15 |
| 1 Foundations | what English is, the sentence, word classes, articles, pronouns, prepositions | ~40 |
| 2 The verb system | the twelve tenses, modals, conditionals, clauses | ~30 |
| 3 Verbs in full | the 415 irregular, the six rules, participles, phrasal verbs | ~25 |
| 4 Nouns and modifiers | countability, determiners, word formation | ~20 |
| 5 The sentence | clauses, connectors, inversion, ellipsis | ~25 |
| 6 Vocabulary and register | collocations, word families, formality | ~20 |
| 7 Reading and listening | how to read, how to listen, the science texts | ~25 |
| 8 Writing and speaking | how to write, paragraphs, cohesion, registers | ~25 |
| 9 Practice | 5,471 cards from the Anki deck, in printable form | ~400 |
| 10 Reference | full verb table, glossary, situation index, traps | ~60 |

Roughly 175,000 words across 60 documents.

## Where the material comes from

Nothing in the reference half was typed from memory, because memory fails
exactly when you need a reference: when you are tired.

| content | source | how it is verified |
|---|---|---|
| 415 irregular verbs, four forms each | Wiktionary's *Appendix: English irregular verbs* | the title header of every downloaded file is checked against the requested title |
| meanings | Princeton WordNet | offline corpus, 334 of 415 verbs |
| 5,471 flashcards | the Anki deck | a linter over the whole deck, 0 warnings |
| 6 rules, 34 situations, 14 traps | hand-written, checked against the grammar chapters | `tools/check.py` |

The same master dataset backs
[the website](https://sazardev.github.io/omarchy-english-toolkit), the
`verbdef` terminal tool and the Anki deck, so the four versions cannot
disagree.

## Three decisions that shape the book

<Warning>

### No translations, not once

Every page is in English. If each page were translated you would read
Spanish all day and acquire Spanish. Hard words are defined in English
using simpler words, which is a technique rather than a compromise.

### The reference half is generated

The verb table, the glossary, the situation index and the six rules come
out of scripts. A 415-row table typed by hand contains errors; a 415-row
table generated from a verified source cannot.

### Reading and writing come before grammar

Grammar explanation is the smallest part of the job and it is the part
everyone spends their time on. It is worth about fifteen per cent, because
grammar knowledge does not turn into ability on its own. Part 7 is about
input and part 8 is about output, and they are longer than the grammar
reference.

</Warning>

## Layout

```
book/            the source, ordered by [X.Y.Z] frontmatter id
  00-*.mdx       front matter, written by hand
  01-*.mdx       foundations, written by hand
  02-*.mdx       the verb system, some generated
  04-*.mdx       nouns and modifiers
  07-*.mdx       reading and listening
  08-*.mdx       writing and speaking
  09-*.mdx       practice, generated from the Anki deck
  10-*.mdx       reference, generated from the dataset
tools/
  check.py       pre-build checks: duplicate ids, unbalanced tags
  gen_grammar.py the twelve tenses, modals, conditionals, clauses, determiners
  gen_reference.py  the verb table, six rules, decisions, situations, traps, glossary
  gen_flashcards.py the Anki deck as printable chapters
  verify.py      build and report pages, words and warnings
build.sh         regenerate everything and ship
out/             the built PDF and EPUB, not committed
```

## Building

`build.sh` regenerates every generated chapter from the upstream
repository and then builds. It is idempotent.

```bash
UPSTREAM=../omarchy-english-toolkit ./build.sh    # point at the dataset
FORMAT=pdf ./build.sh                             # PDF only, skips EPUB
./build.sh fast                                   # no header, page numbers or outline
./build.sh check                                  # checks only, no render
```

The EPUB is 222 kB and needs neither Chrome nor Calibre. The PDF uses
headless Chrome, which `pretty-converter` downloads on first render.

## Quality

`pretty-converter` audits every render for overflow, low-contrast text,
broken anchors and unloaded fonts. Two warnings appear in the current
build and both are the theme's CSS rather than the content: the
`academic` theme does not set `page-break-inside: avoid` on `<code>`, and
a fenced code block in the method diagram can therefore be split across a
page. `tools/check.py` reports 0 problems on 60 documents.

## Licence

MIT. See [LICENSE](LICENSE).

The verbs come from Wiktionary (CC BY-SA) and the meanings from Princeton
WordNet (WordNet License). Both are attributed in
`tools/gen_reference.py` and in the book itself.
