# ==================================== #
#      PRELIMINARY SKILLS PARSER       #
# ==================================== #

import re
from pathlib import Path
import spacy # type: ignore
from spacy.matcher import PhraseMatcher # type: ignore
from src.extraction.utils.regex_patterns import *

CURR_DIR = Path(__file__).resolve().parent

# =========================================================
# NER COMPONENT
# =========================================================

nlp = spacy.blank("en")

with open(CURR_DIR.parent / 'dictionaries/skills_gazetteer.txt', 'r', encoding='utf-8') as f:
    SKILLS_GAZETTEER = sorted(
        {line.strip() for line in f if line.strip() and not line.startswith('#')},
        key=len,
        reverse=True
    )

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add(
    "SKILL",
    [nlp.make_doc(term) for term in SKILLS_GAZETTEER]
)

KNOWN_SKILLS_LOWER = {
    s.lower()
    for s in SKILLS_GAZETTEER
}


# =========================================================
# ENTITY EXTRACTION
# =========================================================

def gazetteer_extract(text):
    """Default NER: phrase-match against the skills gazetteer."""

    doc = nlp(text)

    hits = matcher(doc)

    hits = sorted(
        hits,
        key=lambda h: (
            h[1],
            -(h[2] - h[1])
        )
    )

    used, spans = set(), []

    for _, start, end in hits:

        if any(
            i in used
            for i in range(start, end)
        ):
            continue

        spans.append(
            doc[start:end].text
        )

        used.update(
            range(start, end)
        )

    return spans


def hf_pipeline_extract(text, ner_pipeline):
    
    # will use a finetuned NER pipeline from hugging faces later

    ents = ner_pipeline(text)
    return sorted({
        e["word"].strip()
        for e in ents
        if e.get("entity_group") == "SKILL"
    })


def extract_entities(text, ner_pipeline=None):

    if ner_pipeline is not None:
        return hf_pipeline_extract(
            text,
            ner_pipeline
        )

    return gazetteer_extract(text)

# =========================================================
# SKILL PARSING HELPERS
# =========================================================

def insert_camel_spaces(text):

    for pattern in CAMEL_BOUNDARY_RE:
        text = pattern.sub(
            ' ',
            text
        )

    return text


def split_respecting_parens(line):

    parts, depth, buf = [], 0, ''

    for ch in line:

        if ch in '([':
            depth += 1

        elif ch in ')]':
            depth = max(
                0,
                depth - 1
            )

        if (
            ch in DELIM_CHARS
            and depth == 0
        ):

            parts.append(buf)
            buf = ''

        else:
            buf += ch

    parts.append(buf)

    return [
        p.strip(' .')
        for p in parts
        if p.strip(' .')
    ]


def split_skill_line(
    line,
    ner_pipeline=None
):

    line = CATEGORY_LABEL_RE.sub(
        '',
        line
    ).strip()

    if (
        not line
        or line.lower().strip(' .')
        in SKIP_TOKENS
    ):
        return []

    if DELIM_RE.search(line):

        return split_respecting_parens(
            line
        )

    spaced = insert_camel_spaces(
        line
    )

    if spaced != line:

        extracted = extract_entities(
            spaced,
            ner_pipeline
        )

        if extracted:
            return extracted

    return [
        line.strip(' .')
    ]

def parse_skills_section(skill_lines,ner_pipeline=None):

    skills, seen = [], set()

    for line in skill_lines:

        for skill in split_skill_line(
            line,
            ner_pipeline
        ):

            key = skill.lower().strip()

            if (
                key
                and key not in seen
                and key not in SKIP_TOKENS
            ):

                seen.add(key)

                skills.append(
                    skill.strip()
                )

    return skills