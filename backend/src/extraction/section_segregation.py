# old heuristic: reject any lines with more than three words
# new heuristic: reject any lines with more than four words without upper casing or title casing

# ================================================= #
#        PRELIMINARY SECTION SEGREGATOR
# ================================================= #

import re
import json
from pathlib import Path
from rapidfuzz import fuzz, process

CURR_DIR = Path(__file__).resolve().parent

# additional heading normalization to help with dictionary matches
def normalize_heading(text):
    text = text.lower()

    # removing commonly found punctuation in headings
    text = re.sub(r'[:\-|•]', '', text)

    # collapsing multiple white spaces into a single one
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# dictionary mapping all possible synonyms to their formalized section headings
with open(CURR_DIR / 'schemas/section_mapping.json','r',encoding='utf-8') as file:
  SECTION_HEADINGS = json.load(file)

def segregate_text(raw_text : str):

  current_header = 'HEADER'
  raw_text = raw_text.splitlines()

  section_segregated_text = {
      'header': [],
      'education': [],
      'experience':[],
      'skills': [],
      'projects': [],
      'certifications': [],
      'achievements': [],
      'research':[],
      'leadership':[],
      'volunteering':[],
      'languages':[],
      'references':[],
      'interests':[]
  }

  for line in raw_text:

    if not line:
      continue

    """
    if len(line.split()) > 3:
      section_segregated_text[current_header.lower()].append(line)
      continue
    """

    stripped = line.strip(':-|• ')
    is_heading_shaped = len(line.split()) <= 4 and (stripped.isupper() or stripped.istitle())

    if not is_heading_shaped:
      section_segregated_text[current_header.lower()].append(line)
      continue


    normalized_line = normalize_heading(line)

    match, score, _ = process.extractOne(normalized_line,SECTION_HEADINGS.keys(),scorer=fuzz.WRatio)

    if score > 82:
      current_header = SECTION_HEADINGS[match]
    else:
      section_segregated_text[current_header.lower()].append(line)

  return section_segregated_text