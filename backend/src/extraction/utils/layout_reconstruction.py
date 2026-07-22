# ================================================= #
#     PRELIMINARY LAYOUT RECONSTRUCTION LAYER
# ================================================= #

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

# current dir for path formulation
CURR_DIR = Path(__file__).resolve().parent

with open(CURR_DIR.parent / 'schemas/section_mapping.json', 'r',encoding = 'utf-8') as file:
    section_mapping_dict = json.load(file)

DEFAULT_HEADING_VOCAB = set(section_mapping_dict.keys())

 

BULLET_CHARS = {'•', '◦', '·', '‣', '▪', '○', '●', '■', '*'}
CONTINUATION_SUFFIXES = (',', ';', '&', 'and', 'or', 'with', 'for', 'of', 'to', 'in', 'the')
TERMINAL_PUNCT = ('.', '!', '?')


def _is_bullet_marker_only(line: str) -> bool:
    return line in BULLET_CHARS

def _starts_with_bullet(line: str) -> bool:
    return bool(line) and line[0] in BULLET_CHARS

def _is_plain_title_case(line: str) -> bool:
    words = line.split()
    if not words:
        return False
    return all(re.fullmatch(r"[A-Z][a-z]+", w) for w in words)


def _is_allcaps_fragment(line: str, max_words: int = 3, max_len: int = 25) -> bool:
    letters = [ch for ch in line if ch.isalpha()]
    return (
        bool(letters)
        and all(ch.isupper() for ch in letters)
        and len(line) <= max_len
        and len(line.split()) <= max_words
    )


def _should_merge(current: str, nxt: str, at_doc_start: bool, heading_vocab: Set[str]) -> bool:
    if not current or not nxt:
        return False

    # 1. Word broken across the margin, e.g. "imple-" / "mentation"
    if current.endswith('-') and current[-2:-1].isalpha():
        return True

    # 2. A bullet glyph sitting alone on its own line -> glue to its text
    if _is_bullet_marker_only(current):
        return True

    # 3. The next line starts a *new* bullet item -> never absorb it
    if _starts_with_bullet(nxt):
        return False

    # 4. Name reconstruction: only while still building the very first
    #    logical line of the document (the candidate's name).
    if at_doc_start and _is_plain_title_case(current) and _is_plain_title_case(nxt):
        return True

    # 5. Section headings split across two lines, e.g. "PROFESSIONAL"/"SUMMARY"
    combined = f"{current} {nxt}".upper()
    if combined in heading_vocab and current.upper() not in heading_vocab:
        return True
    if not heading_vocab and _is_allcaps_fragment(current) and _is_allcaps_fragment(nxt):
        return True  # generic fallback when no heading vocabulary supplied

    # A finished, standalone heading is a hard stop: nothing merges past it
    # except the split-heading case just handled above.
    if current.upper() in heading_vocab or (not heading_vocab and _is_allcaps_fragment(current)):
        return False

    # 6. Field label immediately followed by its value, e.g. "Father Name:"
    if current.endswith(':') and len(current.split()) <= 4:
        return True

    # 7. Line ends on a soft/continuation cue -> more of the same clause follows
    lower_current = current.lower()
    if current.endswith(CONTINUATION_SUFFIXES) or any(
        lower_current.endswith(' ' + w) for w in CONTINUATION_SUFFIXES if w.isalpha()
    ):
        return True

    # 8. A finished sentence -> keep the line break
    if current.endswith(TERMINAL_PUNCT):
        return False

    # 9. Wrapped mid-sentence: next line resumes in lowercase
    if nxt[0].islower():
        return True

    # 10. URLs split across multiple lines
    url_like_current = bool(re.search(
        r'(?i)(?:https?://|www\.|'
        r'(?:linkedin|github|gitlab|facebook|twitter|x|'
        r'stackoverflow|bitbucket|medium|behance|dribbble)\.'
        r'|[A-Za-z0-9-]+\.(?:com|org|net|io|co|pk|me|dev)'
        r'(?:[/:]|$))',
        current
    ))

    url_like_next = bool(re.search(
    r'(?i)^(?:'
    r'https?://|'
    r'www\.|'
    r'[/#?&=]'
    r')',
    nxt
    )) or (
        current.endswith('/')
        and bool(re.fullmatch(
            r'[A-Za-z0-9._~!$&\'()*+,;=%-]+',
            nxt
        ))
    )

    if url_like_current and url_like_next:
        return True

    # 11. Default: genuinely a new line (new job title, new date range, etc.)
    return False


def _join(current: str, nxt: str) -> str:
    if current.endswith('-') and current[-2:-1].isalpha():
        return current + nxt  # true word-break hyphen, no extra space
    
    # URL fragments must be joined without a space
    if re.search(
        r'(?i)(?:https?://|www\.|'
        r'(?:linkedin|github|gitlab|facebook|twitter|x|'
        r'stackoverflow|bitbucket|medium|behance|dribbble)\.)',
        current
    ):
        return current + nxt.lstrip()
    
    return f"{current} {nxt}"


def _clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def reconstruct_text_layout(text: str, heading_vocab: Optional[Set[str]] = None) -> str:
   
    if not text or not text.strip():
        return text

    vocab = heading_vocab if heading_vocab is not None else DEFAULT_HEADING_VOCAB
    raw_lines = [ln.strip() for ln in text.split("\n")]
    raw_lines = [ln for ln in raw_lines if ln]  # blank lines carry no info; drop them
    if not raw_lines:
        return ""

    merged: List[str] = []
    buffer = raw_lines[0]
    for nxt in raw_lines[1:]:
        at_doc_start = len(merged) == 0  # still assembling the first output line (the name)
        if _should_merge(buffer, nxt, at_doc_start, vocab):
            buffer = _join(buffer, nxt)
        else:
            merged.append(buffer)
            buffer = nxt
    merged.append(buffer)

    return "\n".join(_clean_line(ln) for ln in merged)


def reconstruct_resume_layout(candidates,heading_vocab = None):
   
    for c in candidates:
        text = c.get("resume_text", "")
        if text:
            c["resume_text"] = reconstruct_text_layout(text, heading_vocab)
    return candidates
