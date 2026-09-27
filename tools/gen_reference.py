#!/usr/bin/env python3
"""Generate the reference chapters of the book from the master dataset.

The verb table, the rule cards, the decision table, the situation index
and the glossary are all derived from docs/data/verbs.json in the
sibling omarchy-english-toolkit repo. Generating them means the book
cannot disagree with the website, the CLI and the Anki deck, and it means
a 415-row table cannot contain a typo.

usage: gen_reference.py <verbs.json> <out-dir> [--front 3.0.0]
"""
import argparse
import json
import sys
from pathlib import Path


def doc(fid, title, body):
    return f"---\nid: \"[{fid}]\"\ntitle: {title}\n---\n\n{body.rstrip()}\n"


def w(path, text):
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- front matter
def gen_verb_table(d, out):
    rows = []
    for v in d["verbs"]:
        rows.append(f"| **{v['base']}** | {v['third']} | {v['past']} | "
                    f"{v['participle']} | {v['ing']} | {v.get('meaning', '')} |")
    body = f"""# The complete irregular verb table

These are the only verbs in English that cannot be worked out from a
pattern. There are about a hundred and thirty of them. Everything else,
some fourteen thousand verbs, is produced by the six rules in the next
chapter.

Four forms are given for each verb, and the distinction between the last
two of them is where most irregular mistakes happen.

| verb | 3rd person | past simple | past participle | -ing | meaning |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## Reading the last two columns

The **past simple** is used for a finished action at a stated time.

> I *wrote* the letter yesterday.

The **past participle** is used after *have*, *has* and *had*, and after
*be* in the passive.

> I have *written* the letter.
> The letter was *written* yesterday.

When the two are different, as in *write* and *written*, using the past
simple where the participle belongs is the most common single error in
written English. There is no way to work it out; it has to be learned.

## The verbs that are not in this table

**Modals** — *can, could, may, might, must, shall, should, will, would*
— are not irregular verbs. They are a closed class with their own
patterns, and they are covered in their own chapter.

**Modals plus main verbs** behave as two verbs in one phrase, and the
modal does not conjugate:

> He *can swim*. / She *can swim*. / They *can swim*.
> He *can**s** swim*.

**Regular verbs** follow the six rules. You do not need to memorise
fourteen thousand tables; you need six rules.
"""
    w(out / "10-01-verb-table.mdx",
      doc("10.1.0", "The Complete Irregular Verb Table", body))


def gen_rules(d, out):
    parts = ["""# The six rules of regular verbs

A regular verb is not memorised. It is produced by one of six rules of
spelling, and knowing the six is worth more than knowing any number of
individual verbs, because together they cover roughly fourteen thousand.

## The order matters

The rules must be tested in a fixed order, and the order is not
arbitrary. The earlier rules are the **exceptions** to the later ones.
Test the sixth rule first, because if a verb ends in *-e* it can never
double, and that settles the whole case. Test the third rule second,
because a verb ending in *consonant + y* takes *-ied* and never doubles.

<Warning>
Testing the rules in the wrong order produces <i>liking</i> instead of
<i>liked</i>, and <i>comming</i> instead of <i>coming</i>. Always start
at R6.
</Warning>
"""]
    for r in d["rules"]:
        ex = "\n".join(
            f"| {e['base']} | {e['third']} | {e['past']} | {e['participle']} | {e['ing']} |"
            for e in r["examples"])
        parts.append(f"""## {r['id']}. {r['name']}

**When:** {r['test']}

**Pattern:** {r['how']}

{r['note']}

| base | 3rd person | past | past participle | -ing |
|---|---|---|---|---|
{ex}
""")
    w(out / "10-02-six-rules.mdx",
      doc("10.2.0", "The Six Rules of Regular Verbs", "\n".join(parts)))


def gen_decisions(d, out):
    rows = "\n".join(
        f"| {x['base']} | **{x['rule']}** | {x['why']} |" for x in d["decisions"])
    body = f"""# Which rule applies

The skill is not knowing the six rules. It is deciding, in one second,
which one fires on a verb you have never seen before.

## The decision table

| verb | rule | why |
|---|---|---|
{rows}

## The procedure, in order

<DeepDive>
1. **Does it end in -e?** Then no doubling at all. Use R2. This settles
   *like*, *change*, *use*, *dive*, *come*, *dive*, *sense*.
2. **Does it end in consonant + y?** Then *y* becomes *ied*. R3, and R5
   never applies. This settles *study*, *cry*, *apply*, *hurry*.
3. **Is it a stressed consonant-vowel-consonant?** Then double. R5. This
   settles *stop*, *plan*, *admit*, *prefer*, *travel*.
4. **Does it end in -e?** (it does not, or you would have stopped at 1)
   Drop the *e*. R2.
5. **Anything else.** Just add *-ed*. R1. This settles *work*, *want*,
   *open*, *watch*, *ask*.
</DeepDive>

## Why the order is not optional

*Travel* looks exactly like *stop*: consonant, vowel, consonant. It is
R5, so *travelled*. But it does not end in *-e*, so step 1 does not fire.

*Study* also looks like *stop*. But it ends in *-y* after a consonant, so
step 2 fires and R5 never gets a chance. The result is *studied*, not
*studyed*.

*Like* also looks like *stop*, but it ends in *-e*, so step 1 fires and
R5 is excluded. The result is *liked*, not *likked*.

Three verbs, one shape, three different rules. The shape does not
determine the rule; the ending does, and the order is what resolves it.

## British and American

Some verbs double in British English and not in American English. Both
are correct.

| British | American |
|---|---|
| travelled | traveled |
| cancelling | canceling |
| labelled | labeled |
| jewellery | jewelry |
| colour | color |

Pick one and stay consistent. Mixing them within one document is the
only real mistake.
"""
    w(out / "10-03-which-rule.mdx",
      doc("10.3.0", "Which Rule Applies", body))


def gen_situation_index(d, out):
    parts = ["""# Index of situations

Which verb fits which situation is a judgement about meaning, not a fact
anybody has tabulated, which is why no dictionary can give it to you.
These are the situations that speakers confuse with each other, and the
tense and pattern each one uses.
"""]
    for s in d["scenarios"]:
        vs = ", ".join(f"`{v}`" for v in s["verbs"])
        ex = "\n".join(f"> {e}" for e in s["examples"])
        parts.append(f"""## {s['title']}

{s['why']}

**Form:** {s['form']}
**Frame:** `{s['frame']}`

**Verbs that fit:** {vs}

{ex}
""")
    w(out / "10-04-situation-index.mdx",
      doc("10.4.0", "Index of Situations", "\n".join(parts)))


def gen_traps(d, out):
    rows = "\n".join(
        f"| {t['wrong']} | {t['right']} | {t['rule']} |" for t in d["traps"])
    body = f"""# The mistakes that cost the marks

These are the errors that appear again and again in written English and
in examinations. Each one is a rule being broken, not carelessness, and
the rule is given so you can check yourself.

<Warning>
Look at the left column and say out loud why it is wrong. A mistake you
can explain is a mistake you stop making.
</Warning>

| wrong | right | rule |
|---|---|---|
{rows}

## Why these particular ones

Three patterns account for most of the list.

**Spanish interference.** *I have been lived here* is a passive of a verb
that cannot be passive. *I look forward to see you* puts an infinitive
after a preposition, which English never does; Spanish does.

**Past simple where the perfect belongs.** *I have seen him yesterday*
cannot be right, because *yesterday* is a finished time. Spanish uses the
same tense for both, so this is invisible until you know to look for it.

**Stative verbs with a continuous form.** *He is knowing the answer* is
not English. *Know*, *like*, *love*, *hate*, *belong*, *own*, *need*,
*want*, *seem* and *contain* describe states, and states do not progress.
"""
    w(out / "10-05-traps.mdx",
      doc("10.5.0", "The Mistakes That Cost the Marks", body))


def gen_glossary(d, out):
    rows = "\n".join(
        f"| {v['base']} | {v.get('meaning', '—')} | {v['third']} | {v['past']} | "
        f"{v['participle']} | {v['ing']} |" for v in d["verbs"])
    body = f"""# Glossary of irregular verbs

Every irregular verb, alphabetically, with its meaning and all four forms.
Use this as a lookup, not as something to read straight through.

| verb | meaning | 3rd person | past | past participle | -ing |
|---|---|---|---|---|---|
{rows}

## Verbs whose meaning is not listed

Eighty-one of the entries carry no meaning, and that is deliberate. They
are all prefixed forms or archaic verbs that no longer appear in ordinary
English: *miswrite*, *underbuy*, *forelay*, *clepe*, *swelt*, *hight*.

You will meet some of them in nineteenth-century literature. You will not
need them to speak.
"""
    w(out / "10-06-glossary.mdx",
      doc("10.6.0", "Glossary of Irregular Verbs", body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("outdir")
    a = ap.parse_args()
    d = json.loads(Path(a.data).read_text(encoding="utf-8"))
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    gen_verb_table(d, out)
    gen_rules(d, out)
    gen_decisions(d, out)
    gen_situation_index(d, out)
    gen_traps(d, out)
    gen_glossary(d, out)
    for f in sorted(out.glob("*.mdx")):
        n = len(f.read_text(encoding="utf-8").split())
        print(f"  {n:6,} words  {f.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
