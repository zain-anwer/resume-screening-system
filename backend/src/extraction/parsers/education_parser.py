# =========================================== #
#       PRELIMINARY EDUCATION PARSER          #
# =========================================== #

import re
import copy
from src.extraction.utils.regex_patterns import *

# typical text cleaning
def clean_line(line):

    line = line.strip()
    line = re.sub(r'\s+',' ',line )
    return line


# field extraction functions

def extract_year(line):

    match = year_pattern.search(line)

    if not match:
        return None, None

    start = match.group("start")
    end = match.group("end")

    if end:
        # convert shortened years like 11 -> 2011
        if end.isdigit() and len(end) == 2:
            end = start[:2] + end

    return start, end

def extract_cgpa(line):

    match = cgpa_pattern.search(line)
    return match.group(1) if match else None

def is_institute_line(line):

    # scheme
    # institute keywords :- 3
    # known insitution acronyms :- 3
    # all caps :- 1
    # title case :- 1

    classification_score = 0
    if institute_keywords.search(line):
      classification_score += 3
    if known_institutions.search(line):
      classification_score += 3
    if line.isupper():
      classification_score += 1
    elif line.istitle():
      classification_score += 1
    
    if classification_score >= 3:
      return True
    return False

def extract_institute(line):

    institute = line
    # remove degree information
    # institute = degree_pattern.sub('',institute)

    # remove dates
    institute = year_pattern.sub('',institute)

    # remove CGPA
    institute = cgpa_pattern.sub('',institute)
    institute = scale_pattern.sub('',institute)
    institute = institute.strip(" |,-.")

    if institute and is_institute_line(institute):
      return institute
    return None
      
def extract_degree(line):

    # if line looks like an institute do not classify it as degree
    if is_institute_line(line):
        return None

    if not degree_pattern.search(line):
        return None

    degree = line

    # remove metadata
    degree = year_pattern.sub('',degree)
    degree = cgpa_pattern.sub('',degree)
    degree = scale_pattern.sub('',degree)
    degree = degree.strip(" |,-.")


    return degree if degree else None

# ==========================================================
#                      Parser                              #
# ==========================================================

def parse_education_section(education_lines):

    education_objects = []


    current = {
        "degree": None,
        "institute": None,
        "start_year": None,
        "end_year": None,
        "cgpa": None
    }


    for education_line in education_lines:


        # split only safe separators
        chunks = re.split(r'\|',education_line)


        for chunk in chunks:

            line = clean_line(chunk)
            if not line:
                continue

            institute = extract_institute(line)
            degree = extract_degree(line)
            start, end = extract_year(line)
            cgpa = extract_cgpa(line)

            # ---------------------------------
            # Degree starts a new education item
            # ---------------------------------

            if degree:

                if current["degree"]:
                    education_objects.append(
                        copy.deepcopy(current)
                    )
                    current = {
                        "degree": None,
                        "institute": None,
                        "start_year": None,
                        "end_year": None,
                        "cgpa": None
                    }
                current["degree"] = degree

            if institute:
                current["institute"] = institute

            if start and end:
              current['start_year'] = start
              current['end_year'] = end

            # only one year mentioned probably year of graduation
            if start and not end:
              current['end_year'] = start

            if cgpa:
                current["cgpa"] = cgpa

    # store final object

    if any(current.values()):

        education_objects.append(
            copy.deepcopy(current)
        )


    return education_objects
