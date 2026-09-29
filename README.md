# The Complete English Course

**From Zero to Fluent** — grammar, reading, writing and 5,471 flashcards
in one volume. **1,258 pages** at 6×9in, English only, MIT licensed.

**→ https://sazardev.github.io/english-from-zero-to-fluent/**

A complete English course in one volume, built from material that has
already been tested. A twelve-week guided track in part 12 gives you a
chapter, a writing task and an exercise for each of 84 days.

Built with
[go-pretty-converter](https://github.com/sazardev/go-pretty-converter),
which renders Markdown to an audited PDF and an EPUB 3 through headless
Chrome.

```bash
./build.sh            # check, generate, build PDF + EPUB
open out/english-from-zero-to-fluent.pdf
```

The built book is in the [releases](https://github.com/sazardev/english-from-zero-to-fluent/releases),
as PDF and EPUB, and there is a [landing page](https://sazardev.github.io/english-from-zero-to-fluent/)
built from `docs/`.

## What is in it

118 documents, 212,132 words in the rendered PDF, 6×9in on every page.

| part | documents | words | what |
|---|---|---|---|
| 0 Front matter | 4 | 4,362 | how to use the book, the method, your tools, the levels |
| 1 Foundations | 8 | 10,601 | what English is, the sentence, articles, pronouns, prepositions, plurals and countability, there/it and possessives |
| 2 The verb system | 9 | 10,838 | present, past, future, perfect, passive, the twelve tenses, modals, conditionals, clauses |
| 3 Verbs in full | 7 | 10,055 | -ing against to, participles, phrasal verbs, verbs with a preposition, the -ed ending, auxiliaries, the 415 |
| 4 Nouns and modifiers | 4 | 5,146 | determiners, adjective order, adverbs, word formation |
| 5 The sentence | 5 | 7,452 | connectors, relative clauses, cleft, ellipsis, inversion and negation, questions |
| 6 Vocabulary and register | 6 | 8,889 | collocations, verb patterns, word families, formality, false friends, prepositions at scale |
| 7 Reading and listening | 6 | 8,691 | how to read, how to listen, science prose, reading a paper, poetry, reading speed |
| 8 Writing and speaking | 6 | 8,388 | how to write, paragraphs, cohesion, hedging, registers, the fourteen errors |
| 9 Practice | 42 | 149,456 | 5,471 cards from the Anki deck, in printable form |
| 10 Reference | 6 | 18,217 | the 415-verb table, the six rules, the situation index, the traps, the glossary |
| 11 Exercises | 10 | 13,823 | exercises for parts 1 to 8, complete answer keys, four self-tests |
| 12 The guided track | 5 | 8,279 | the twelve-week programme, your first week hour by hour, worked examples, the diagnostic |

The reading extracts the plan budgeted for were not written. Part 7
teaches the method for reading them instead, which is what it is for; the
corpus of 109 public-domain works and 15 arXiv papers is collected and
unused. `PLAN.md` records that as the outstanding item.

Parts 6, and the reading extracts and exercises in 7 and 9, are the work
still to do. `PLAN.md` holds the budget.

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

### No translations, not once

Every page is in English. If each page were translated you would read your
own language all day and acquire it. Hard words are defined in English
using simpler words, which is a technique rather than a compromise.

Four chapters broke this while they were being written, each one showing a
foreign sentence to make a point about interference. Every one was replaced
with the wrong *English*, which is what the rule asks for anyway: show the
mistake so the learner recognises it. `tools/check_english.py` now fails the
build on it.

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

## Layout

```
book/            the source, ordered by [X.Y.Z] frontmatter id
  00-*.mdx       front matter, written by hand
  01-*.mdx       foundations
  02-*.mdx       the verb system
  03-*.mdx       verbs in full
  04-*.mdx       nouns and modifiers
  05-*.mdx       the sentence
  06-*.mdx       vocabulary and register
  07-*.mdx       reading and listening
  08-*.mdx       writing and speaking
  09-*.mdx       practice, generated from the Anki deck
  10-*.mdx       reference, generated from the dataset
  11-*.mdx       exercises, answer keys and self-tests
  12-*.mdx       the guided track: a day-by-day route through the book
docs/            the landing page, published on GitHub Pages
tools/
  check.py       pre-build checks: ids, tags, anchors, frontmatter
  check_english.py  fails the build on non-English content
  fix_tags.py    rebalances a mismatched custom block tag
  gen_grammar.py the twelve tenses, modals, conditionals, clauses, determiners
  gen_reference.py  the verb table, six rules, decisions, situations, traps, glossary
  gen_flashcards.py the Anki deck as printable chapters
  verify.py      build and report
  report.py      the figures, shared by the build and the README
  metadata.py    writes and verifies the PDF's document metadata
cover.svg        the cover, vector, sized to the paper
themes/
  academic-print.theme.yml   the academic theme plus the print rules
build.sh         regenerate everything and ship
out/             the built PDF and EPUB, not committed
```

## Building

`build.sh` regenerates every generated chapter from the upstream
repository and then builds. It is idempotent.

```bash
UPSTREAM=../omarchy-english-toolkit ./build.sh    # point at the dataset
FORMAT=pdf ./build.sh                             # PDF only, skips EPUB
THEME=latex ./build.sh                            # override the config theme
./build.sh fast                                   # no header, page numbers or outline
./build.sh check                                  # checks only, no render
```

The theme, the paper size and the cover come from
`go-pretty-converter.yml` unless overridden in the environment. The EPUB
needs neither Chrome nor Calibre; the PDF uses headless Chrome, which
`pretty-converter` downloads on first render.

Two things about the config are worth knowing if you edit it, because both
were wrong here for several builds and neither produced an error:

**`paper` lives under `render:`.** A top-level `paper:` key is parsed and
then ignored, and the book renders at the default A4. The same is true of
`cover_image` under `render:`, `density` under `theme_options:`, and the
output path, which is `output` and not `out`.

**The PDF's document metadata is written after the render.** The renderer
sets only the title, and the cover page it merges in is built from an HTML
fragment with no title element at all, so the merged document inherits the
temporary filename Chrome was given. `tools/metadata.py` writes the author,
subject and keywords with qpdf and then verifies them, which means a build
that lost its metadata fails instead of shipping.

The cover is `cover.svg`, sized in CSS pixels at 96 per inch, so 576×864 is
exactly 6×9in. Anything else produces a cover page of a different size and
the type comes out stretched.

## Quality

Three checks run before every build, and each one exists because a real
mistake got past the earlier ones.

`tools/check.py` finds duplicate ids, unbalanced `<Warning>` and
`<DeepDive>` tags, trailing whitespace, and heading anchors that collide.
The anchor check is global because the renderer uses one id space for the
whole book, which the build audit confirmed when it reported the same
heading in two different files.

`tools/check_english.py` fails the build on non-English content. It ignores
tables and fenced blocks, where a form in another script is deliberate, and
it allows IPA, which is pronunciation and therefore part of the subject.

`tools/fix_tags.py` rebalances a mismatched tag by rewriting the closing
name rather than adding or removing a block, and drops a closing tag that
has no opening one.

Both checkers report 0 problems on 118 documents.

`pretty-converter` audits every render for overflow, low-contrast text,
broken anchors and unloaded fonts. One warning remains, and it is expected:
`page-break-inside-risk` on `<table>`. The advice is wrong for this book.
The irregular verb table is 415 rows and runs across many pages, so a table
has to be allowed to break; the theme sets `avoid` on the row instead,
which is the part that matters, because a row split across a page boundary
is unreadable. The audit checks the table element, does not read the theme's
CSS, and raises the same warning for all seventeen built-in themes. The
reasoning is written out in `go-pretty-converter.yml`.

## Licence

MIT. See [LICENSE](LICENSE).

The verbs come from Wiktionary (CC BY-SA) and the meanings from Princeton
WordNet (WordNet License). Both are attributed in
`tools/gen_reference.py` and in the book itself.
</content>
</invoke>
