#!/usr/bin/env python3
"""Generate the dense grammar tables: the whole tense system, the modal
table, the conditional table, the clause table and the determiner table.

These are the pages a learner opens when they are stuck, so they are
written as tables rather than prose: a table is scanned, prose is read.

Every table is complete rather than representative. A grammar reference
that shows three examples teaches three examples, not a system.

usage: gen_grammar.py <out-dir>
"""
import sys
from pathlib import Path


def doc(fid, title, body, tags=()):
    """Frontmatter in the tool's own format. Tags are what analyze asks for.

    tags is a flat sequence of strings: ("grammar", "tenses")."""
    flat = []
    for t in tags:
        if isinstance(t, str):
            flat.append(t)
        else:
            flat.extend(t)
    t = "tags: [" + ", ".join(flat) + "]" if flat else ""
    head = f'---\nid: "[{fid}]"\ntitle: {title}'
    if t:
        head += f"\n{t}"
    return f"{head}\n---\n\n{body.rstrip()}\n"


# The twelve tenses, built from four components.
# aspect x time: simple / continuous x present / past / future, plus
# perfect and perfect continuous. The naming is a trap for learners, so
# every table gives the formula as well as the name.
TENSES = [
    # (name, formula, use, example, negative, question)
    ("Present simple",
     "base / 3rd -s",
     "habits, routines, permanent facts, timetables",
     "She works in Madrid.",
     "She doesn't work here.",
     "Does she work here?"),
    ("Present continuous",
     "am/is/are + -ing",
     "happening now, temporary, definite future arrangements",
     "She is working from home this week.",
     "She isn't working today.",
     "Is she working today?"),
    ("Past simple",
     "past form",
     "a finished action at a stated time",
     "She worked here for three years.",
     "She didn't work last year.",
     "Did she work here?"),
    ("Past continuous",
     "was/were + -ing",
     "an action in progress when something else happened",
     "She was working when the phone rang.",
     "She wasn't working at ten.",
     "Was she working when you called?"),
    ("Present perfect",
     "have/has + participle",
     "a finished action with present relevance, or a situation from the past that still holds",
     "She has worked here since 2019.",
     "She hasn't worked here.",
     "Has she worked here long?"),
    ("Present perfect continuous",
     "have/has been + -ing",
     "an action that started in the past and is still running",
     "She has been working here for an hour.",
     "She hasn't been working all day.",
     "How long has she been working?"),
    ("Past perfect",
     "had + participle",
     "the earlier of two past actions",
     "She had left before I arrived.",
     "She hadn't left yet.",
     "Had she left before you arrived?"),
    ("Past perfect continuous",
     "had been + -ing",
     "how long something had been happening before another past point",
     "She had been working for two hours when it ended.",
     "She hadn't been working long.",
     "How long had she been working?"),
    ("Future simple",
     "will + base",
     "a decision now, a prediction, a promise, an offer",
     "I'll call you tomorrow.",
     "I won't call.",
     "Will you call?"),
    ("Future continuous",
     "will be + -ing",
     "an action in progress at a future moment",
     "I'll be working at six.",
     "I won't be working then.",
     "Will you be working at six?"),
    ("Future perfect",
     "will have + participle",
     "finished before another future point",
     "I'll have finished by June.",
     "I won't have finished by then.",
     "Will you have finished by June?"),
    ("Future perfect continuous",
     "will have been + -ing",
     "ongoing up to a future point",
     "I'll have been working here for ten years by 2030.",
     "I won't have been working that long.",
     "How long will you have been working?"),
]

MODALS = [
    # modal, meaning, form, example, note
    ("can", "ability, permission", "can + base",
     "I can swim. / Can I sit here?", "no *can* to after can"),
    ("could", "past ability, polite request, possibility",
     "could + base",
     "I could read at six. / Could you help?", "same form for all persons"),
    ("may", "formal permission, possibility", "may + base",
     "May I leave? / It may rain.", "more formal than can"),
    ("might", "less certain possibility", "might + base",
     "He might come later.", "weaker than may"),
    ("must", "strong obligation, deduction", "must + base",
     "You must wear a helmet. / He must be late.", "deduction: 90% certain"),
    ("have to", "obligation from outside", "have to + base",
     "I have to file by Friday.", "obligation, not ability"),
    ("should", "advice, expectation", "should + base",
     "You should see a doctor.", "advice, not command"),
    ("ought to", "advice, formal", "ought to + base",
     "You ought to leave earlier.", "same meaning as should"),
    ("will", "spontaneous decision, promise, prediction", "will + base",
     "I'll have the soup.", "decided at the moment of speaking"),
    ("would", "polite request, habit, conditional", "would + base",
     "Would you mind waiting?", "polite past of will"),
    ("shall", "formal suggestion or offer", "shall + base",
     "Shall I close the window?", "rare outside legal English"),
    ("shouldn't", "advice against", "shouldn't + base",
     "You shouldn't worry.", ""),
]

CONDITIONALS = [
    ("Zero", "general truth", "If + present, present",
     "If you heat water, it boils.",
     "If I see her, I tell her. / If I see her, do I tell her?"),
    ("First", "real and likely", "If + present, will + base",
     "If I finish early, I'll call you.",
     "If it rains, will you stay? / What will you do if it rains?"),
    ("Second", "unreal now or imagined", "If + past, would + base",
     "If I had more time, I would learn it.",
     "If you were me, what would you do?  <- were, never *was*"),
    ("Third", "unreal past", "If + had + participle, would have + participle",
     "If I had studied, I would have passed.",
     "If she had asked, would you have helped?"),
    ("Mixed", "unreal past, real present", "If + had + participle, will + base",
     "If you had slept, you won't be tired now.",
     ""),
]

DETERMINERS = [
    ("Articles", "a, an, the, zero",
     "a book, an hour, the book, books", "the first mention uses *a*/*an*, later uses *the*"),
    ("Possessives", "my, your, his, her, its, our, their",
     "my book, her book, its cover", "its is the possessive; it is is the contraction"),
    ("Demonstratives", "this, that, these, those",
     "this book, those books", ""),
    ("Quantifiers", "some, any, no, each, every, all, both, few, little, many, much",
     "some water, no water, much water", "some and any swap in negatives and questions"),
    ("Cardinal numbers", "one to a billion", "three books", "one book is *a*, not *one*"),
    ("Ordinal numbers", "first to billionth", "the third book", "always with *the* or a possessive"),
    ("Countable with a", "a, one, two...", "a book, two books", "not with uncountable nouns"),
    ("Uncountable with much/some", "much, little, some, plenty of",
     "much water, little water", "not with countable nouns: *much books* is wrong"),
]

CLAUSES = [
    ("Adverbial of time", "when, before, after, while, as soon as, until",
     "When I arrived, she had left."),
    ("Adverbial of condition", "if, unless, as long as, provided that",
     "Unless you hurry, you will be late."),
    ("Adverbial of reason", "because, since, as, now that, given that",
     "I stayed home because it rained."),
    ("Adverbial of purpose", "so that, in order that, lest",
     "He spoke slowly so that I could understand."),
    ("Adverbial of result", "so, such that, enough to",
     "It was so cold that the pipes froze."),
    ("Adverbial of contrast", "although, though, even though, whereas, while",
     "Although it rained, we went out."),
    ("Adverbial of concession", "despite, in spite of, however",
     "Despite the rain, we went out."),
    ("Relative clause", "who, whom, whose, which, that, where, when, why",
     "The book that I borrowed was good."),
    ("Defining relative", "who, which, that", "the man who called"),
    ("Non-defining relative", "who, which", "my brother, who lives in Lima,"),
    ("Nominal relative", "the one that, the person who, whatever, whoever",
     "She is the one who designed it."),
    ("Cleft sentence", "It is X that Y", "It was Anna who called."),
    ("Pseudo-cleft", "What X did was Y", "What I did was leave early."),
    ("Inversion after a negative", "never, rarely, seldom, hardly, not only",
     "Never have I seen such a thing."),
    ("Inversion in a conditional", "were, had, should",
     "Were I you, I would refuse. / Had I known, I would have called."),
    ("Ellipsis", "omit what is understood",
     "She will do it, and so will I."),
]


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "book")
    out.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------- the twelve tenses
    rows = "\n".join(
        f"| **{n}** | {f} | {u} | {e} | {ng} | {qq} |"
        for n, f, u, e, ng, qq in TENSES)
    body = f"""# The twelve tenses, complete

English has twelve tenses. Most languages have fewer, and most English
learners use four of them well and the other eight badly. This table is
the whole system, and it is the single most useful page in the book.

<Warning>
The names are misleading. <i>Present perfect</i> is not the present. It
is the past with a present result. Learn the <b>formula</b> in the second
column, not the name in the first.
</Warning>

| tense | formula | use | example | negative | question |
|---|---|---|---|---|---|
{rows}

## How the twelve are built

The system is not a list of twelve, it is a grid. Pick a **time** and an
**aspect**.

| | present | past | future |
|---|---|---|---|
| simple | eat | ate | will eat |
| continuous | am eating | was eating | will be eating |
| perfect | have eaten | had eaten | will have eaten |
| perfect continuous | have been eating | had been eating | will have been eating |

Twelve cells, twelve tenses. Once you see the grid, the names stop
mattering.

## Choosing between the two past tenses

> I **wrote** the letter.   *(finished, time implied or stated)*
> I **was writing** the letter when you arrived. *(in progress, interrupted)*

> I **have written** the letter. *(finished, present relevance)*
> I **had written** the letter before you arrived. *(finished, earlier past)*

## The three past tenses compared

| tense | when | finished? | example |
|---|---|---|---|
| past simple | at a stated time | yes | I left at nine. |
| present perfect | time not stated | yes | I have left. |
| past perfect | before another past time | yes | I had left by nine. |

<DeepDive>
If a finished time expression appears, you cannot use the present
perfect. *Yesterday*, *in 2010*, *last week*, *when I was a child* and
*ago* are all finished times, and they force the past simple.

This is the most common error for a Spanish speaker, because Spanish
does not make this distinction.
</DeepDive>
"""
    (out / "02-06-twelve-tenses.mdx").write_text(
        doc("2.6.0", "The Twelve Tenses, Complete", body, tags=["grammar", "tenses"]), encoding="utf-8")

    # ------------------------------------------------------------- modals
    rows = "\n".join(f"| **{m}** | {meaning} | {f} | {ex} | {nt} |"
                     for m, meaning, f, ex, nt in MODALS)
    body = f"""# Modals, complete

Modals are a closed class. There are thirteen of them, you either know
them or you do not, and no new ones are being coined. That makes them
easier than the verbs.

## What they all have in common

- **No *to***: *can swim*, never *can to swim*
- **No *-s***: *she can*, not *she cans*
- **No *do* in negatives or questions**: *she can't*, *Can she?* — not
  *doesn't can*, *Does she can?*
- **Same form for every person**: *I can*, *you can*, *she can*

<Warning>
<i>Mustn't</i> means <b>prohibition</b>. <i>Don't have to</i> means
<b>no obligation</b>. They are opposites, not synonyms.
</Warning>

| modal | meaning | form | example | note |
|---|---|---|---|---|
{rows}

## Obligation, four ways

| strength | phrase | example |
|---|---|---|
| strongest | must | You must wear a helmet. |
| | have to | I have to file by Friday. |
| | should | You should see a doctor. |
| weakest | don't have to | You don't have to come. |

<DeepDive>
<i>Must</i> comes from the speaker. <i>Have to</i> comes from the world.

*You must be tired* — I say so, from noticing your face.
*You have to work on Sunday* — the world says so, the company does.

And <i>mustn't</i> forbids: <i>You mustn't smoke here</i>. While
<i>don't have to</i> merely removes the requirement:
<i>You don't have to smoke</i> means it is your choice.
</DeepDive>

## Deduction with must and might

| you are | 90% sure | 50% sure | 100% sure not |
|---|---|---|---|
| say | must be | might be | can't be |
| past | must have been | might have been | can't have been |

> He must be tired.  *(he is, almost certainly)*
> He must have forgotten.  *(he did, and we only know now)*
> He can't have left.  *(he did not, definitely)*
"""
    (out / "02-07-modals.mdx").write_text(
        doc("2.7.0", "Modals, Complete", body, tags=["grammar", "modals"]), encoding="utf-8")

    # ------------------------------------------------------- conditionals
    rows = "\n".join(f"| **{n}** | {u} | {f} | {e} | {qq} |"
                     for n, u, f, e, qq in CONDITIONALS)
    body = f"""# Conditionals, complete

The four conditionals plus the mixed one, and the question form of each,
which is where most learners lose the thread.

| type | situation | form | example | question |
|---|---|---|---|---|
{rows}

## The backshift rule

<Warning>
In the second and third conditionals, the <i>if</i> clause takes
<b>were</b> for every person, never <i>was</i>. This is not optional in
formal English and it is how you sound educated.
</Warning>

| ✗ wrong | ✓ right |
|---|---|
| If I **was** you, I would go. | If I **were** you, I would go. |
| If she **was** rich, she would travel. | If she **were** rich, she would travel. |
| If he **was** here, he would know. | If he **were** here, he would know. |

## Choosing the right one

Ask two questions.

1. **Is the condition real?** If yes, use zero or first. If it is
   imagined, unreal or politely untrue, use second or third.
2. **Is the situation past or present?** Present: second. Past: third.

| you mean | use |
|---|---|
| a general truth | zero |
| a real, likely future | first |
| an imagined present | second |
| an imagined, regretted past | third |

## The three time clauses learners mix up

| clause | if | when | while |
|---|---|---|---|
| future, real | If it rains, I'll stay. | When it rains, I'll stay. | While it rains, I'll stay. |
| past | — | When it rained, I stayed. | While it rained, I stayed. |
| meaning | condition | time | duration, and *and* |

<DeepDive>
*While* can introduce a condition too: *While you're here, tell me about
it.* And *when* cannot introduce a duration the way *while* does.
</DeepDive>
"""
    (out / "02-08-conditionals.mdx").write_text(
        doc("2.8.0", "Conditionals, Complete", body, tags=["grammar", "conditionals"]), encoding="utf-8")

    # ----------------------------------------------------- clause types
    rows = "\n".join(f"| {n} | {w} | {e} |" for n, w, e in CLAUSES)
    body = f"""# Clause types, complete

One clause can do more than one job, and telling the jobs apart is how you
build sentences that hold together. Every subordinate clause in English
falls into one of these.

| clause type | words | example |
|---|---|---|
{rows}

## Because and although

This is the classic Spanish interference pair, and the order reverses.

| | position | English | Spanish |
|---|---|---|---|
| because | after | Although it rained, we went out. | Because it rained, we went out. |
| but | after | It rained, but we went out. | — |

<Warning>
English puts the *subordinate* clause first and the *main* clause last,
with a comma between. Spanish does the opposite. Putting *because* at
the end of an English sentence is correct only for emphasis, and to a
Spanish ear it sounds wrong even when it is right.
</Warning>

## Connecting ideas instead of repeating

| function | options | example |
|---|---|---|
| add | and, also, moreover, furthermore, in addition | Moreover, the cost rose. |
| contrast | but, however, nevertheless, on the other hand, yet | However, sales held. |
| cause | because, since, as, due to, owing to | Sales held, since costs rose. |
| result | so, therefore, thus, consequently, as a result | Costs rose; therefore sales held. |
| example | for example, for instance, such as, namely | Animals, such as dogs, need space. |
| sequence | first, then, next, finally, meanwhile | First we tested; then we shipped. |
| emphasis | indeed, in fact, actually, certainly | It was, indeed, a hard year. |

## Avoiding a comma splice

Two complete sentences cannot be joined with only a comma.

| ✗ wrong | ✓ right |
|---|---|
| I was late, so I missed the meeting. | I was late, **so** I missed the meeting. *(so is fine)* |
| The test was hard, I passed it. | The test was hard. I passed it. |
| The test was hard, but I passed it. | The test was hard, **but** I passed it. |
| The test was hard, **which** surprised me. | The test was hard, **which** surprised me. |

A comma splice is only acceptable before *which*, *and that*, or when the
second half is a participle phrase: *The test was hard, **passing** easily.*
"""
    (out / "02-09-clauses.mdx").write_text(
        doc("2.9.0", "Clause Types, Complete", body, tags=["grammar", "clauses"]), encoding="utf-8")

    # ------------------------------------------------------- determiners
    rows = "\n".join(f"| {n} | {w} | {e} | {nt} |" for n, w, e, nt in DETERMINERS)
    body = f"""# Determiners and quantifiers, complete

The determiner is the word that comes before a noun and tells you what
kind of noun you are looking at. It is the first place where a Spanish
speaker has to unlearn something: Spanish often has no determiner at all.

| type | words | example | note |
|---|---|---|---|
{rows}

## Countable and uncountable

This is the distinction English insists on and Spanish does not.

| | countable | uncountable |
|---|---|---|
| singular | one book, a book | ✗ one water |
| plural | two books | two waters *(a kind, a glass)* |
| *many* | many books | ✓ much water |
| *much* | ✗ much books | much water |
| *a few* / *a little* | a few books | a little water |
| *few* / *little* | not many | not much |
| *few* / *little* + plural | — | **not** a little *waters* |

<Warning>
*Water, information, advice, furniture, luggage, research, news, evidence*
are uncountable in English. *A water* is a glass of water, not the
liquid. *Advices* and *informations* do not exist.
</Warning>

## Zero article

English drops the article in cases where Spanish keeps one.

- plurals and uncountables in general: *Dogs are loyal. Water is wet.*
- meals: *have breakfast, have dinner*
- most place names: *go to Madrid, live in Spain*
- languages and subjects: *speak English, study history*
- institutions: *go to university, be at school*
- diseases: *have flu, have cancer*

## The article, in full

| use | example |
|---|---|
| first mention | I bought **a** book. |
| second mention | **The** book was expensive. |
| unique thing | **The** sun, *the* internet, *the* government |
| specific known thing | Close **the** door. *(the one you mean)* |
| superlative | **the** best, *the* only |
| after a generalisation | *Music is* **the** *art of...* |
| whole thing | **The** USA, *the* Netherlands, *the* Alps |

*Spain, France* and *Britain* take no article. *the USA* and *the Alps* do.
"""
    (out / "04-01-determiners.mdx").write_text(
        doc("4.1.0", "Determiners and Quantifiers, Complete", body, tags=["grammar", "determiners"]),
        encoding="utf-8")

    for f in ("02-06-twelve-tenses", "02-07-modals", "02-08-conditionals",
              "02-09-clauses", "04-01-determiners"):
        p = out / f"{f}.mdx"
        if p.exists():
            print(f"  {len(p.read_text().split()):6,} words  {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
