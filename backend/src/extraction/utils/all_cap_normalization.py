import re

def normalize_all_caps(text):
  all_caps_phrase = re.compile(r'\b[A-Z][A-Z&/.\-]*(?:[ \t]+[A-Z][A-Z&/.\-]*)+\b')
  def replace(match):
    return " ".join(word.capitalize() for word in match.group().split())

  return all_caps_phrase.sub(replace, text)