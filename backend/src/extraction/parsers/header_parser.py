# ======================================== #
#      PRELIMINARY HEADER PARSER           #
# ======================================== #

# FLOW: extract structured data -> mask regex extracted data -> apply NER -> extract remaining fields
# salient design principle:
# masking fields after extraction

import spacy # type: ignore
from urllib.parse import urlparse
import re

from src.extraction.utils.regex_patterns import *

# the smallest model available for english NLP
nlp = spacy.load('en_core_web_sm')

# ======================================= #
#           HELPER FUNCTIONS              #
# ======================================= #

LABEL_PATTERNS = {
    "date_of_birth": re.compile(r'Date\s+of\s+Birth\s*:', re.I),
    "father_name":   re.compile(r"Father(?:'s)?\s*Name\s*:", re.I),
    "gender":        re.compile(r'Gender\s*:', re.I),
    "cnic":          re.compile(r'CNIC\s*(?:No\.?|Number)?\s*:', re.I),
    "address":       re.compile(r'Address\s*:', re.I),
    "nationality":   re.compile(r'Nationality\s*:', re.I),
    "marital_status":re.compile(r'Marital\s*Status\s*:', re.I),
}

VALUE_PATTERNS = {
    "cnic":          re.compile(r'\d{5}-\d{7}-\d'),
    "date_of_birth": re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}'),
    "gender":        re.compile(r'\b(?:Male|Female|M|F)\b'),
    "marital_status":re.compile(r'\b(?:Single|Married|Divorced|Widowed)\b', re.I),
    "nationality":   re.compile(r'\b(?:Pakistani|Indian|Bangladeshi|Afghan|Chinese|British|American|Canadian|Saudi|Emirati)\b', re.I),
    "father_name":   re.compile(r'(?:[A-Z][a-z]+\s+){1,3}[A-Z][a-z]+'),
}
FREEFORM_FIELDS = {"address"}  # no fixed shape - absorbs whatever's left


def descramble_header_labels(header_text: str) -> str:
    matches = []
    for field, pat in LABEL_PATTERNS.items():
        for m in pat.finditer(header_text):
            matches.append((m.start(), m.end(), field, m.group()))
    matches.sort(key=lambda t: t[0])
    if not matches:
        return header_text

    # group labels that have nothing but whitespace between them
    clusters, current = [], [matches[0]]
    for prev, cur in zip(matches, matches[1:]):
        if header_text[prev[1]:cur[0]].strip() == "":
            current.append(cur)
        else:
            clusters.append(current)
            current = [cur]
    clusters.append(current)

    scrambled = [c for c in clusters if len(c) > 1]
    if not scrambled:
        return header_text

    rebuilt, offset = header_text, 0
    priority = ["cnic", "date_of_birth", "gender", "marital_status",
                "nationality", "father_name"]

    for cluster in scrambled:
        cluster_fields = [c[2] for c in cluster]
        cluster_end = cluster[-1][1]
        next_starts = [m[0] for m in matches if m[0] >= cluster_end and m not in cluster]
        span_end = next_starts[0] if next_starts else len(header_text)
        nl = header_text.find('\n', cluster_end, span_end)
        if nl != -1:
            span_end = nl

        remaining = header_text[cluster_end:span_end]
        assigned = {}
        for field in priority:
            if field not in cluster_fields or field in assigned:
                continue
            m = VALUE_PATTERNS[field].search(remaining)
            if m:
                assigned[field] = m.group().strip()
                remaining = remaining[:m.start()] + remaining[m.end():]

        leftover_fields = [f for f in cluster_fields if f in FREEFORM_FIELDS and f not in assigned]
        leftover_text = remaining.strip(" ,")
        if leftover_fields:
            assigned[leftover_fields[0]] = leftover_text
        elif leftover_text:
            unassigned = [f for f in cluster_fields if f not in assigned]
            if unassigned:
                assigned[unassigned[-1]] = leftover_text

        pieces = [f"{label_text} {assigned.get(field, '')}".strip()
                  for _, _, field, label_text in cluster]
        replacement = " ".join(pieces)

        start, end = cluster[0][0] + offset, span_end + offset
        tail = rebuilt[end:]
        sep = "" if tail[:1] in ("", "\n", " ", "\t") else " "
        rebuilt = rebuilt[:start] + replacement + sep + tail
        offset += len(replacement) + len(sep) - (end - start)

    return rebuilt


def classify_urls(urls : list[str]) -> dict:

  result = {
      'github' : None,
      'linkedin': None,
      'portfolio': []
  }

  for url in urls:

    normalized_url = url if url.startswith('http') else f'https://{url}'
    domain = urlparse(normalized_url).netloc.lower().replace("www.","")

    if "github.com" in domain:
      result["github"] = normalized_url
    elif "linkedin.com" in domain:
      result["linkedin"] = normalized_url
    elif domain and '@' not in normalized_url:
      result["portfolio"].append(normalized_url)

  return result

def normalize_all_caps(text):
  all_caps_phrase = re.compile(r'\b[A-Z][A-Z&/.\-]*(?:[ \t]+[A-Z][A-Z&/.\-]*)+\b')
  def replace(match):
    return " ".join(word.capitalize() for word in match.group().split())

  return all_caps_phrase.sub(replace, text)


def parse_header_section(header_lines):

  urls = None
  personal_info = {
    "name": None,
    "gender": None,
    "marital_status": None,
    "father_name": None,
    "email": None,
    "phone": [],
    "landline": [],
    "cnic": None,
    "location": None,
    "date_of_birth": None,
    "nationality": None
  }

  header_text = '\n'.join(header_lines)
  print("BEFORE DESCRAMBLE:", repr(header_text))
  header_text = descramble_header_labels(header_text)
  print("AFTER DESCRAMBLE:", repr(header_text))

  # ------------------- REGEX LAYER ------------------------ #
  # father_name, phone, email, cnic, date_of_birth, etc.

  email_match  = email_pattern.search(header_text)
  if email_match:
    personal_info["email"] = email_match.group()
    header_text = header_text.replace(email_match.group(),'<EMAIL>')

  cnic_match   = cnic_pattern.search(header_text)
  if cnic_match:
    personal_info["cnic"] = cnic_match.group()
    header_text = header_text.replace(cnic_match.group(),'<CNIC>')

  father_match = father_pattern.search(header_text)
  if father_match:
    personal_info['father_name'] = father_match.group('father').strip()
    header_text = header_text.replace(father_match.group(),'<FATHER_NAME>')

  dob_match    = dob_pattern.search(header_text)
  if dob_match:
    personal_info['date_of_birth'] = dob_match.group('dob').strip()
    header_text = header_text.replace(dob_match.group(),'<DOB>')

  gender_match = gender_pattern.search(header_text)
  if gender_match:
    value = gender_match.group('gender').strip()
    if value.lower() in ['f','female']:
      value = 'Female'
    elif value.lower() in ['m','male']:
      value = 'Male'
    else:
      value = 'Other'
    personal_info['gender'] = value

  url_list     = url_pattern.findall(header_text)
  if url_list:
    for url in url_list:
      header_text = header_text.replace(url,'<URL>')
    urls = classify_urls(url_list)

  nat_match = nationality_pattern.search(header_text)
  if nat_match:
    value = nat_match.group('nationality').strip()
    personal_info['nationality'] = value
    header_text = header_text.replace(value,'<NATIONALITY>')

  marital_match = marital_status_pattern.search(header_text)
  if marital_match:
    value = marital_match.group('marital').strip()
    personal_info['marital_status'] = value
    header_text = header_text.replace(value,'<MARITAL_STATUS>')

  phone_matches = phone_pattern.findall(header_text)
  if phone_matches:
    personal_info["phone"] = phone_matches
    for phone_match in phone_matches:
      header_text = header_text.replace(phone_match,'<PHONE>')

  general_phone_matches = general_phone_pattern.findall(header_text)
  if general_phone_matches:
      personal_info["landline"] = general_phone_matches
      for general_phone_match in general_phone_matches:
        header_text = header_text.replace(general_phone_match,'<LANDLINE>')

  # since NER fails on all caps names we will find all caps convert and then check via NER
  normalized_copy = normalize_all_caps(header_text)

  for line in normalized_copy.splitlines():
    doc = nlp(line)
    for ent in doc.ents:

      # person name
      if ent.label_ == 'PERSON' and not personal_info['name']:
        name = ' '.join(re.split(r'\s',ent.text))
        if len(name.split()) <= 3:
          personal_info['name'] = name

      # father name (NER unreliable)
   #   if ent.label_ == 'PERSON' and personal_info['name']:
   #     if len(ent.text.split()) > 1 and ent.text != personal_info['name']:
   #       personal_info['father_name'] = ent.text

      # geopolitical entity
      if ent.label_ == 'GPE':
        personal_info["location"] = ent.text

  return personal_info, urls