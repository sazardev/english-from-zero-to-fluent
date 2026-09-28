# Book plan

Target: 1,000+ pages at 6x9in, English only, built with
`pretty-converter`. Every document is `[X.Y.Z]` frontmatter so the tool
orders it, and every page must be worth reading.

**Status: met.** 1,126 pages, 113 documents, 0 build errors, 0 build
warnings from the source. The one remaining audit warning is documented in
`go-pretty-converter.yml`.

## Why this shape

The material already collected decides the structure. There is no point
inventing an order that ignores what exists:

- 415 irregular verbs, generated, with meanings
- 6 regular rules and a decision table
- 34 situations, each with tense, frame, verbs and examples
- 14 recurring errors
- 25 Anki chapters covering B1 to C2
- 109 public-domain works: novels, stories, poetry, essays, epics,
  science, biographies
- 15 arXiv computer science papers
- 5,822 flashcards

A grammar book is a reference. A course is a path. This is both, and the
reference half is generated so it cannot contain errors, while the path
half is written so it can teach.

## Parts

| Part | Title | Ch | Status |
|---|---|---|---|
| 0 | Front matter | 4 | done: how to use this book, the method, your tools, the levels |
| 1 | Foundations | 8 | done: what English is, the sentence, articles, pronouns, prepositions of place and time, plurals and countability, there/it and possessives |
| 2 | The verb system | 10 | done: present, past, future, perfect, passive, the twelve tenses, modals, conditionals, clauses |
| 3 | Verbs in full | 8 | done: -ing against to, participles, phrasal verbs, verbs with a preposition, the -ed ending, auxiliaries, the 415 |
| 4 | Nouns and modifiers | 7 | partly: determiners, adjective order, adverbs, word formation. Still missing: comparison in depth, and the countability chapter sits in part 1 where it is needed |
| 5 | The sentence | 8 | done: connectors, relative clauses, cleft and ellipsis, inversion and negation, questions |
| 6 | Vocabulary and register | 6 | done: collocations, verb patterns, word families, formality and register, false friends, prepositions at scale |
| 7 | Reading and listening | 6 | done: how to read, how to listen, science prose, reading a paper, poetry, reading speed |
| 8 | Writing and speaking | 6 | done: how to write, paragraphs, cohesion, hedging, registers in practice, the fourteen errors |
| 9 | Practice | 10 | 5,471 flashcards, generated, in printable chapters |
| 11 | Exercises | 13 | done: exercises for parts 1 to 8, complete answer keys, four self-tests with mark scales |
| 10 | Reference | 8 | done: verb table, grammar tables, glossary, situation index, answer key |

## Page budget, as built

| | planned | actual |
|---|---|---|
| prose | ~400 pages | ~560 pages, 205,108 words |
| generated tables | ~80 pages | ~90 pages |
| flashcards | ~190 pages | ~400 pages, 5,471 cards |
| exercises and keys | 150 pages | ~60 pages, 4 exercise sets and 5 answer keys |
| reading extracts | 200 pages | 0 |

The flashcards came in at twice the plan, which is correct: part 0 says
they are the highest-value part for retention, and the plan already said
they were not to be trimmed.

**The reading extracts were not written.** The plan budgeted 200 pages
from the 109 public-domain works and the 15 arXiv papers, and both are
collected and available. What is in part 7 instead is the *method* for
reading them: how science is written, how to take a paper apart in fifteen
minutes, how poetry works, how to read faster. The extracts themselves are
the outstanding item on this plan.

## Rules for every document

1. **English only.** No native-language scaffolding, not even a word.
   Enforced by `tools/check_english.py`, which fails the build.
2. **Every explanation gives an example.** A rule with no example is not
   an explanation.
3. **The wrong version is shown too.** Learners need to see the mistake
   to recognise it, and the mistake is shown **in English**, which is what
   makes it recognisable.
4. **Generated content is generated.** The verb table, the glossary and
   the indexes come from scripts, so they cannot drift.
5. **No filler.** If a section cannot say something the learner did not
   already know, it is cut.

## What the checks are for

Each exists because a real mistake got past the earlier ones, and each one
was written after measuring rather than after assuming.

`tools/check.py` — duplicate ids, unbalanced custom tags, duplicate heading
anchors. The anchor check is **global**, because the renderer uses one id
space for the whole book. That was confirmed the hard way: it was relaxed
to per-file on a reasonable assumption and the build audit reported the
same heading in two different files within a minute.

`tools/check_english.py` — non-English content. It caught a corrupted line
in the poetry chapter that I introduced myself.

`tools/fix_tags.py` — rebalances a mismatched tag by rewriting the closing
name rather than adding or removing a block, and drops a closing tag with
no opening one.

`tools/report.py` — the figures, shared by `build.sh` and the README, so
the page count quoted in either cannot drift from the build.

## The one standing warning

`page-break-inside-risk` on `<table>`. The audit wants
`page-break-inside: avoid` on the table element. The irregular verb table
is 415 rows and runs for many pages, so a table has to be allowed to
break; the theme sets `avoid` on the row instead, which is the part that
matters, because a row split across a page boundary puts the verb at the
bottom of one page and its past form at the top of the next.

The audit does not read the theme's CSS, so it cannot see the row rule
that already prevents the problem it describes, and all seventeen built-in
themes raise the same warning for the same reason. Reasoned out in
`go-pretty-converter.yml`.
</content>
