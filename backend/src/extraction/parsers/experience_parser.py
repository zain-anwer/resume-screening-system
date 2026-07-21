# ============================================== #
#       PRELIMINARY EXPERIENCE PARSER            #
# ============================================== #

import re
import copy
from regex_patterns import *

def detect_job_title(line):
    line = line.strip()
    if len(line) > 25:
        return False
    if experience_date_pattern.search(line):
        return False
    if line.endswith('.'):
        return False
    words = line.split()
    for word in words:
        if word[0].islower():
            return False
    if not title_keywords.search(line):
        return False
    return True


def new_exp():
    return {'job_title': None, 'organization': None,
            'start_date': None, 'end_date': None, 'description': None}


def parse_experience_section(lines):
    """
    Parse a single candidate's experience section (a list of raw lines)
    into a list of experience dicts: job_title, organization,
    start_date, end_date, description.
    """
    section_experience = []
    exp_obj = new_exp()

    for line in lines:
        chunks = chunk_pattern.split(line)

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            if detect_job_title(chunk):
                # new title -> flush whatever entry we were building
                if exp_obj['job_title']:
                    section_experience.append(copy.deepcopy(exp_obj))
                    exp_obj = new_exp()
                exp_obj['job_title'] = chunk
                continue

            date_match = experience_date_pattern.search(chunk)
            if date_match:
                exp_obj['start_date'] = date_match.group('start').strip()
                exp_obj['end_date'] = date_match.group('end').strip()
                # org sometimes rides along on the same chunk as the date
                # e.g. "MCB Islamic Bank Limited - Feb, 2024 - Present"
                remainder = experience_date_pattern.sub('', chunk).strip(' ,-()')
                if remainder and exp_obj['job_title'] and not exp_obj['organization']:
                    exp_obj['organization'] = remainder
                continue

            # neither a title nor a date -> org slot first, then description overflow
            if exp_obj['job_title'] and not exp_obj['organization']:
                exp_obj['organization'] = chunk
            elif exp_obj['job_title']:
                exp_obj['description'] = (
                    f"{exp_obj['description']} {chunk}".strip()
                    if exp_obj['description'] else chunk
                )

    # flush the LAST entry for this candidate only — once, after all their lines
    if exp_obj['job_title']:
        section_experience.append(copy.deepcopy(exp_obj))

    return section_experience
