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