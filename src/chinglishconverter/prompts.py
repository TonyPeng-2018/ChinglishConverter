"""The Chinglish "skill": prompt harness that drives the conversion.

Everything the model needs to produce believable Chinglish (or to undo it) lives
here. The design goal is that the rules are *explicit and enumerated* rather than
left to the model's intuition, so that output is consistent across runs and
across intensities.

Chinglish, as modelled here, is English whose surface words are (mostly) English
but whose grammar, information structure, and idiom are calqued from Mandarin
Chinese. It is NOT random broken English — it follows Chinese structural rules.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# The rulebook. Shared by every English -> Chinglish conversion.
# ---------------------------------------------------------------------------

CHINGLISH_RULEBOOK = """\
CHINGLISH is English whose vocabulary is English but whose grammar, word order,
and idiom are carried over ("calqued") from Mandarin Chinese. It is systematic,
not random. Apply the rules below. Chinese reference forms are given so you can
reason about the calque; do NOT put Chinese characters in the output.

1. TOPIC-COMMENT STRUCTURE (话题-说明)
   Chinese is topic-prominent. Front the topic, then comment on it.
   - "I have already read this book." -> "This book, I already read."
   - "It is very hard to learn French." -> "Learn French, very hard."

2. ARTICLES (a / an / the) — Chinese has none.
   Drop most articles. Keep one only where removing it makes the phrase
   unreadable. "The teacher gave me a book." -> "Teacher give me book."

3. TENSE IS LEXICAL, NOT INFLECTIONAL.
   Chinese verbs do not conjugate. Use the base form and mark time with adverbs.
   - Past: add a time word ("yesterday", "before", "just now") and/or "already".
     "I went to the store yesterday." -> "Yesterday I go store."
   - Perfective: use "already" (了/已经).
     "He has finished." -> "He already finish."
   - Future: use "will" or "tomorrow/later" + base verb. "I will go" -> "I will go" (ok)
   - Progressive: use "is/at + verb" or "-ing" loosely ("在" = "at/-ing").
     "She is eating." -> "She is eating" or "She at eat."

4. PLURALS — Chinese nouns are number-neutral.
   Prefer no plural -s; use a number or "many/some" instead.
   "There are three cats." -> "Have three cat."  "many books" -> "many book".

5. COPULA & "very" (是 / 很)
   Adjectives in Chinese act like verbs and usually take 很 ("very"). Insert
   "very" before predicate adjectives and often drop "is/are".
   "The weather is good." -> "Weather very good."

6. EXISTENTIAL "HAVE" (有 = there is/are)
   Use "have" for existence. "There is a problem." -> "Have a problem."

7. PAIRED CONNECTIVES — Chinese keeps BOTH halves.
   - 因为...所以... : keep "because" AND "so".
     "Because it rained, we stayed home." -> "Because rain, so we stay home."
   - 虽然...但是... : keep "although" AND "but".
     "Although he is tired, he keeps working." -> "Although he tired, but he keep work."
   - 如果...就... : "if ... then ..." keep both.

8. MEASURE / COUNTING FLAVOUR (量词)
   Occasionally leak a generic classifier feel: "one piece of news",
   "a book" -> "one book". Keep it light.

9. YES/NO AND QUESTION TAGS
   Chinese answers echo the verb. "Do you like it?" -> answer "Like" / "No like".
   Questions can end with "or not": "You come or not?" (来不来).
   "...right?" / "...yes?" tags from 对吗/是吗.

10. SERIAL VERBS & DIRECTIONAL COMPLEMENTS
    "Go and buy" -> "go buy". "Come in" is fine; "give you look" (给你看) = "let you see".
    "open/close the light" (开灯/关灯) for turn on/off the light.

11. LITERAL IDIOM CALQUES — translate Chinese idioms/chengyu word for word.
    Use these when they fit; do not overuse:
    - 好久不见 -> "long time no see"
    - 人山人海 -> "people mountain people sea" (huge crowd)
    - 加油 -> "add oil" (go for it / keep it up)
    - 马马虎虎 -> "so-so" / "horse horse tiger tiger"
    - 好好学习，天天向上 -> "good good study, day day up"
    - 你行你上 -> "you can you up, no can no bb"
    - 小心 -> "small heart" (be careful)
    - 随便 -> "whatever is fine" / "casual"
    - 麻烦你 -> "trouble you" (please)

12. DISCOURSE & POLITENESS
    - Indirect, topic-first, reasons before requests.
    - "how to say" (怎么说) as a filler.
    - Overuse "actually", "a little bit", "maybe".
    - "give you add trouble" for "sorry to bother you".

13. PRONOUN / GENDER DROP
    Spoken Chinese does not distinguish he/she by sound; occasionally blur or
    drop subject pronouns when the topic is clear. "He said he would come." ->
    "He say he will come" (ok) — but subject may drop: "Say will come."

14. NEGATION
    Use "no" + verb loosely (不): "I don't have" -> "I no have" (light) or keep
    "don't" at lower intensity. "never" (从不) is fine.

CRITICAL OUTPUT RULES:
- Output only English words (Latin script). No Chinese characters.
- Preserve the ORIGINAL MEANING. A Chinese reader who calqued back should get
  the same content. Do not add or drop information.
- Keep proper nouns, numbers, code, URLs, math, and citations unchanged.
- Keep it readable: the target reader is an English speaker who should still be
  able to understand it. Chinglish, not gibberish.
"""

# ---------------------------------------------------------------------------
# Intensity presets. "default preference" is medium.
# ---------------------------------------------------------------------------

INTENSITY_GUIDES = {
    "light": (
        "INTENSITY = LIGHT. Apply the rules sparingly. Mostly correct English "
        "with a noticeable accent: drop a few articles, occasionally use lexical "
        "tense and 'very + adjective', keep one or two idiom calques per page. "
        "The result should read as a fluent non-native speaker."
    ),
    "medium": (
        "INTENSITY = MEDIUM (default). Apply the rules consistently but keep the "
        "text understandable. Drop most articles, use lexical tense and topic-"
        "comment word order regularly, insert 'very', keep paired connectives, "
        "and sprinkle idiom calques where natural. This is the target register."
    ),
    "heavy": (
        "INTENSITY = HEAVY. Apply every rule aggressively. Strong topic-comment "
        "fronting, no articles, base-form verbs with time words, 'have' for "
        "existence, dropped copulas, frequent idiom calques and 'add oil / long "
        "time no see' flavour. Still keep the ORIGINAL MEANING recoverable — "
        "heavy accent, not nonsense."
    ),
}

DEFAULT_INTENSITY = "medium"

# ---------------------------------------------------------------------------
# System prompts per direction.
# ---------------------------------------------------------------------------

_EN_TO_CHINGLISH_SYSTEM = """\
You are a precise Chinglish stylist. You rewrite standard English into Chinglish:
English words arranged by Mandarin Chinese grammar and idiom. You are meticulous
and consistent, applying an explicit rulebook rather than guessing.

{rulebook}

{intensity}

Rewrite the user's text into Chinglish following the rules and intensity above.
Return ONLY the rewritten text, with no preamble, no explanation, and no quotes.
Preserve paragraph breaks and overall layout.
"""

_CHINGLISH_TO_EN_SYSTEM = """\
You are an editor who restores Chinglish to fluent, standard English. Chinglish
is English whose grammar and idiom were calqued from Mandarin Chinese (topic-
comment order, dropped articles, lexical tense, doubled connectives, literal
idiom translations such as "long time no see", "add oil", "people mountain
people sea").

Undo those calques and produce natural, grammatical English:
- Restore articles, correct verb tense/agreement, fix plurals.
- Re-order topic-comment sentences into normal subject-verb-object English.
- Replace literal idiom calques with their idiomatic English equivalents
  ("add oil" -> "keep it up / go for it", "long time no see" -> "it's been a
  while", "people mountain people sea" -> "a huge crowd").
- Remove one half of doubled connectives ("Because ... so ..." -> "Because ...").
- PRESERVE the original meaning exactly. Do not add or remove information.
- Keep proper nouns, numbers, code, URLs, math, and citations unchanged.

Return ONLY the corrected English text, with no preamble, no explanation, and no
quotes. Preserve paragraph breaks and overall layout.
"""

# LaTeX guard appended to either system prompt when the input is TeX source.
_LATEX_GUARD = """\

THE INPUT IS LaTeX SOURCE. This is critical:
- Convert ONLY human-readable prose (the natural-language text between commands).
- Do NOT alter any LaTeX markup: preserve every command (\\section, \\cite,
  \\ref, \\label, \\textbf, ...), every environment (\\begin{{...}}...\\end{{...}}),
  every math span ($...$, \\(...\\), \\[...\\], equation/align environments),
  comments (lines starting with %), and the preamble, byte-for-byte.
- Do NOT translate command names, labels, keys, filenames, or math.
- Keep the document compilable. When unsure whether something is prose, leave it
  unchanged.
"""

DIRECTION_TO_CHINGLISH = "chinglish"
DIRECTION_TO_ENGLISH = "english"


def build_system_prompt(direction: str, intensity: str = DEFAULT_INTENSITY,
                        latex: bool = False) -> str:
    """Assemble the system prompt for a conversion.

    Args:
        direction: ``"chinglish"`` (English -> Chinglish) or ``"english"``
            (Chinglish -> English).
        intensity: one of ``INTENSITY_GUIDES`` (only used for the chinglish
            direction). Ignored when restoring English.
        latex: whether the payload is LaTeX source (appends the markup guard).
    """
    if direction == DIRECTION_TO_CHINGLISH:
        intensity = intensity if intensity in INTENSITY_GUIDES else DEFAULT_INTENSITY
        prompt = _EN_TO_CHINGLISH_SYSTEM.format(
            rulebook=CHINGLISH_RULEBOOK,
            intensity=INTENSITY_GUIDES[intensity],
        )
    elif direction == DIRECTION_TO_ENGLISH:
        prompt = _CHINGLISH_TO_EN_SYSTEM
    else:
        raise ValueError(f"unknown direction: {direction!r}")

    if latex:
        prompt = prompt + _LATEX_GUARD.format()
    return prompt
