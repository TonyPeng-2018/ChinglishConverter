# A Short Tutorial on Chinglish

**Chinglish** is English whose *words* are English but whose *grammar, word order,
and idiom* are carried over from Mandarin Chinese. It is not random broken
English — it is systematic. If you know the Chinese rule behind each pattern, the
output is predictable. This tutorial explains the main structural differences so
you can read (and write) Chinglish on purpose.

Throughout, `EN` is standard English and `CH` is Chinglish.

---

## 1. Sentence structure: topic-comment vs. subject-verb-object

English is **subject-prominent**: every sentence is built around *subject → verb
→ object*. Chinese is **topic-prominent**: it names a topic first, then comments
on it. Chinglish fronts the topic.

- EN: *I have already read this book.*
- CH: *This book, I already read.*

- EN: *It is very difficult to learn French.*
- CH: *Learn French, very difficult.*

- EN: *As for the money, don't worry about it.*
- CH: *This money, no need worry.*

The "extra" subject *it* that English inserts (*it is difficult…*, *there is…*)
usually disappears, because Chinese does not need a dummy subject.

---

## 2. Articles (a / an / the)

Chinese has **no articles**. Chinglish drops most of them.

- EN: *The teacher gave me a book.*
- CH: *Teacher give me book.*

---

## 3. Tense: lexical, not inflectional

Chinese verbs **do not conjugate**. Time is shown with adverbs (*yesterday*,
*already*, *before*), not with verb endings. Chinglish uses the base verb.

| Meaning | English | Chinglish |
|---|---|---|
| Past | *I went yesterday.* | *Yesterday I go.* |
| Perfect | *He has finished.* | *He already finish.* (了) |
| Progressive | *She is eating.* | *She is eating* / *She at eat.* (在) |
| Future | *I will go tomorrow.* | *Tomorrow I go.* |

The particle **了 (le)** — completion — becomes the word **"already"**.

---

## 4. Plurals and counting

Chinese nouns are **number-neutral**; number is shown by a numeral or a word
like *many*, not by adding *-s*.

- EN: *There are three cats.* → CH: *Have three cat.*
- EN: *many books* → CH: *many book*

Note *have* for existence (see §6).

---

## 5. Adjectives are verbs, and love "very"

A Chinese adjective behaves like a verb and usually carries **很 (hěn, "very")**.
So Chinglish drops the copula *is/are* and inserts *very*.

- EN: *The weather is good.* → CH: *Weather very good.*
- EN: *She is tall.* → CH: *She very tall.*

---

## 6. "Have" = there is / there are

The verb **有 (yǒu)** means both *to have* and *there is/are*. Chinglish uses
*have* for existence.

- EN: *There is a problem.* → CH: *Have a problem.*

---

## 7. Doubled connectives

Chinese keeps **both halves** of a correlative pair; English keeps only one.
Chinglish keeps both.

| Chinese pair | English keeps | Chinglish keeps both |
|---|---|---|
| 因为…所以… | *Because …* | *Because rain, so we stay home.* |
| 虽然…但是… | *Although …* | *Although he tired, but he keep work.* |
| 如果…就… | *If …* | *If you go, then I go too.* |

---

## 8. Literal idiom calques

Chinese idioms (成语 chéngyǔ) translated word-for-word are the most famous part
of Chinglish. A few have even entered real English.

| Chinese | Literal Chinglish | Meaning |
|---|---|---|
| 好久不见 | *long time no see* | it's been a while (now standard English!) |
| 加油 | *add oil* | keep it up / go for it |
| 人山人海 | *people mountain people sea* | a huge crowd |
| 马马虎虎 | *horse horse tiger tiger* | so-so, mediocre |
| 好好学习，天天向上 | *good good study, day day up* | study hard and improve daily |
| 小心 | *small heart* | be careful |
| 你行你上 | *you can you up* | if you're so good, do it yourself |

---

## 9. Verbs of "turning on/off" and giving

- 开灯 / 关灯 → *open the light* / *close the light* (turn on/off).
- 给你看 → *give you look* (let you see / show you).
- Serial verbs stack: *go buy*, *come see*, *sit down eat*.

---

## 10. Questions and answers

- **"…or not?"** questions (from 来不来, "come-not-come"): *You come or not?*
- **Echo answers**: Chinese answers a yes/no question by repeating the verb.
  *Do you like it?* → *Like.* / *No like.*
- **Tags**: 对吗 / 是吗 → *…, right?* / *…, yes?*

---

## 11. Politeness and discourse

- Reasons come **before** the request; requests are indirect.
- Filler *"how to say…"* (怎么说).
- *"trouble you"* (麻烦你) for *"could you please…"*.
- Frequent *actually*, *a little bit*, *maybe*.

---

## Putting it together

> **EN:** Although it was raining yesterday, I still went to the library, because
> there were three books I had to return.

> **CH (medium):** Yesterday although rain, but I still go library, because have
> three book I must return.

Same meaning, Chinese scaffolding. That is Chinglish.

---

### How this tool uses these rules

`chinglish convert` feeds an explicit version of the rules above to the Claude
API and asks it to apply them at a chosen intensity (`light`, `medium`,
`heavy`). Converting **back** (`--to english`) reverses each rule to recover
standard English. The tool preserves LaTeX markup, math, code, numbers, and
citations unchanged — only prose is restyled.

_No accuracy, quality, or safety guarantee is made. See DISCLAIMER.md._
