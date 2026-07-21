# ========================= #
#      TEXT CLEANUP
# ========================= #

import re

def normalize_ocr_text(text: str) -> str:
    # CRLF -> LF first
    text = re.sub(r'\r\n?', '\n', text)

    # remove page-artifact lines (case-insensitive)
    text = re.sub(r'.*page\s*\d+.*', ' ', text, flags=re.IGNORECASE)

    # removing bullet points
    text = re.sub(r'^\s*(?:[•◦·→\-]|o)\s+', ' ', text,flags=re.MULTILINE)

    # collapse runs of 3+ blank lines down to one
    text = re.sub(r'\n\s*\n\s*\n+', '\n', text)

    # collapse repeated spaces/tabs WITHOUT eating newlines
    text = re.sub(r'[ \t]+', ' ', text)

    # strip each line, drop empties
    text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())

    return text