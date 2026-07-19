import re
import json
from pathlib import Path
from rapidfuzz import fuzz, process


CURR_DIR = Path(__file__).resolve().parent

def normalize_heading(text):
    text = text.lower()

    # removing commonly found punctuation in headings
    text = re.sub(r'[:\-|•]', '', text)

    # collapsing multiple white spaces into a single one
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# parse the raw text and break into headers to ensure proper regex and NER application

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

    if len(line.split()) > 3:
      section_segregated_text[current_header.lower()].append(line)
      continue

    normalized_line = normalize_heading(line)

    match, score, _ = process.extractOne(normalized_line,SECTION_HEADINGS.keys(),scorer=fuzz.WRatio)

    if score > 82:
      current_header = SECTION_HEADINGS[match]
    else:
      section_segregated_text[current_header.lower()].append(line)

  return section_segregated_text
