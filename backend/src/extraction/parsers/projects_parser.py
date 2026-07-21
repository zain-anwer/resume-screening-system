# ============================================== #
#             PRELIMINARY PROJECTS PARSER
# ============================================== #

import re
import spacy # type: ignore
from regex_patterns import *
from pathlib import Path
from spacy.matcher import PhraseMatcher # type: ignore

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
matcher.add("SKILL", [nlp.make_doc(term) for term in SKILLS_GAZETTEER])

KNOWN_SKILLS_LOWER = {s.lower() for s in SKILLS_GAZETTEER}


# =========================================================
# ENTITY EXTRACTION
# =========================================================

def gazetteer_extract(text):
    doc = nlp(text)
    hits = matcher(doc)
    hits = sorted(hits, key=lambda h: (h[1], -(h[2] - h[1])))

    used, spans = set(), []
    for _, start, end in hits:
        if any(i in used for i in range(start, end)):
            continue
        spans.append(doc[start:end].text)
        used.update(range(start, end))

    return spans


def hf_pipeline_extract(text, ner_pipeline):
    ents = ner_pipeline(text)
    return sorted({
        e["word"].strip()
        for e in ents
        if e.get("entity_group") == "SKILL"
    })


def extract_entities(text, ner_pipeline=None):
    if ner_pipeline is not None:
        return hf_pipeline_extract(text, ner_pipeline)
    return gazetteer_extract(text)


# No char cap on the label itself — the word-count check at the call
# site (<= 6 words) is what actually bounds it. An earlier {1,40}
# char limit silently failed to match perfectly good labels that
# happened to run past 40 characters (e.g. "Social Media Listening
# and Community Tools:"), leaving the colon+value stuck in the name.
COLON_HEADER_RE = re.compile(r"^(?P<label>[A-Za-z][^:]*?):\s*(?P<rest>\S.+)$")

SKIP_TOKENS = {'n/a', 'na', ''}

NARRATIVE_VERBS = {
    'led', 'developed', 'managed', 'worked', 'collaborated', 'created',
    'implemented', 'designed', 'built', 'conducted', 'provided', 'maintained',
    'performed', 'ensured', 'responsible', 'proficient', 'experienced',
    'skilled', 'supported', 'coordinated', 'administered', 'oversaw',
    'assisted', 'engaged', 'utilized', 'analyzed', 'delivered', 'trained',
}

NON_PROJECT_RE = re.compile(
    r'\b('
    r'universit(?:y|ies)|colleg(?:e|iate)|collage|academy|institute|'
    r'bachelor(?:s)?|master(?:s)?|degree|diploma|certificat(?:e|ion)|'
    r'secondary\s+school|matriculation|intermediate'
    r')\b',
    re.IGNORECASE
)


# =========================================================
# PROJECT VALIDATION HELPERS
# =========================================================

def normalize_for_skill_check(line):
    stripped = TRAILING_PAREN_RE.sub('', line).strip()
    return stripped.lower().strip(' .')


def is_known_skill(line, known_skills_lower):
    normalized = normalize_for_skill_check(line)
    return (
        normalized in known_skills_lower
        or line.lower().strip(' .') in known_skills_lower
    )


def is_title_line(line, known_skills_lower):
    if not line or line.lower().strip(' .') in SKIP_TOKENS:
        return False
    if URL_RE.search(line):
        return False
    if is_known_skill(line, known_skills_lower):
        return False

    words = line.split()
    if len(words) > 10 or line.rstrip().endswith('.'):
        return False

    first_word = words[0].lower().strip('.,')
    if first_word in NARRATIVE_VERBS:
        return False

    return True


# =========================================================
# PROJECT OBJECT INITIALIZATION
# =========================================================

def new_project_stub():
    return {
        'name': None,
        'role': None,
        'description_parts': [],
        'start_date': None,
        'end_date': None,
        'technologies': [],
        'github': None,
        'demo': None
    }


# =========================================================
# COMPLETE PROJECTS PARSER
# =========================================================

def parse_projects_section(
    project_lines,
    parsed_skills,
    ner_pipeline=None,
    non_project_pattern=NON_PROJECT_RE
):
    """
    Parse a single candidate's projects section (a list of raw lines)
    into a list of project dicts: name, role, start_date, end_date,
    technologies, github, demo, description.
    """
    known_skills_lower = {s.lower() for s in parsed_skills} | KNOWN_SKILLS_LOWER

    projects = []
    current = None

    def flush():
        nonlocal current
        if current and (current['name'] or current['description_parts']):
            description = ' '.join(current['description_parts']).strip()
            current['description'] = description if description else None
            del current['description_parts']

            seen, deduped = set(), []
            for tech in current['technologies']:
                key = tech.lower()
                if key not in seen:
                    seen.add(key)
                    deduped.append(tech)
            current['technologies'] = sorted(deduped)

            projects.append(current)
        current = None

    for raw_line in project_lines:
        line = raw_line.strip()

        if not line or line.lower().strip(' .') in SKIP_TOKENS:
            continue

        if non_project_pattern and non_project_pattern.search(line):
            continue

        url_match = URL_RE.search(line)
        if url_match and current is not None:
            url = url_match.group(0)
            if 'github.com' in url.lower():
                current['github'] = url
            else:
                current['demo'] = url
            continue

        if is_title_line(line, known_skills_lower):
            flush()

            name = line
            start_date, end_date = None, None

            date_match = DATE_RANGE_RE.search(name)
            if date_match:
                start_date, end_date = date_match.group(1), date_match.group(2)
                name = DATE_RANGE_RE.sub('', name).strip(' -\u2013\u2014,.')
            else:
                year_match = SINGLE_YEAR_RE.search(name)
                if year_match:
                    start_date = end_date = year_match.group(1)
                    name = SINGLE_YEAR_RE.sub('', name).strip(' -\u2013\u2014,.()')

            role = None
            seed_description = None

            colon_match = COLON_HEADER_RE.match(name)
            if colon_match and len(colon_match.group('label').split()) <= 6:
                name = colon_match.group('label').strip()
                seed_description = colon_match.group('rest').strip()
            elif not date_match and ' - ' in name:
                left, _, right = name.partition(' - ')
                right = right.strip()
                if right and len(right.split()) <= 6 and not right.endswith('.'):
                    name, role = left.strip(), right

            # A bare header line with nothing after the colon (e.g.
            # "WordPress Development:") won't match COLON_HEADER_RE at
            # all (there's no value to seed a description with), so the
            # trailing colon is otherwise left stuck on the name.
            name = name.strip(' :-\u2013\u2014,.')

            current = new_project_stub()
            current.update({
                'name': name,
                'role': role,
                'start_date': start_date,
                'end_date': end_date
            })

            if seed_description:
                current['description_parts'].append(seed_description)
                current['technologies'].extend(extract_entities(seed_description, ner_pipeline))

            continue

        if current is None:
            continue

        current['description_parts'].append(line)
        current['technologies'].extend(extract_entities(line, ner_pipeline))

    flush()
    return projects
