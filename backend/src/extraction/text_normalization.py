# ========================= #
#      TEXT CLEANUP
# ========================= #

import re

def normalize_ocr_text(text : str) -> str:

  # removing page artifacts
  text = re.sub(r'.*page\s*\d+.*',' ',text)

  # removing bullet points
  text = re.sub(r'^\s*(?:[•◦·→\-]|o)\s+', ' ', text)

  # CRLF -> LF and remove multiple newlines
  text = re.sub(r'\r','\n',text)
  text = re.sub(r'\n\s*\n\s*\n+','\n',text)

  # removing multiple whitespaces and stripping trailing spaces
  text = re.sub(r'\s+',' ',text)
  text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])

  return text