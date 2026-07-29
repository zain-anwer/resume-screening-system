import re

# ---------------------------------------------------------
# Degree level detection
# ---------------------------------------------------------

# Ordered highest -> lowest so the first match wins when a degree
# string is ambiguous or ranked incorrectly by naive substring checks.
DEGREE_KEYWORDS = [
    ("phd",       ["phd", "ph.d", "ph d", "doctor of philosophy", "doctorate"]),
    ("mphil",     ["m.phil", "mphil", "m phil"]),
    ("masters",   ["ms ", "m.s.", "msc", "m.sc", "master", "mba", "me ", "m.e.", "meng"]),
    ("bachelors", ["bs ", "b.s.", "bsc", "b.sc", "bachelor", "be ", "b.e.", "beng", "bba"]),
    ("diploma",   ["diploma", "associate","dae"]),
    ("intermediate", ["intermediate","hssc","higher secondary school certificate","higher secondary","fsc","f.sc","fa","f.a","ics","i.com","icom"]),
    ("matriculation", ["matric","matriculation","ssc","secondary school certificate","secondary education","o level","o-level",
    ]),
]


def _normalize(text):
    return (text or "").strip().lower()


def determine_highest_degree(education):

    found_levels = set()

    for record in education or []:

        if not isinstance(record, dict):
            continue

        degree_text = _normalize(record.get("degree") or record.get("degree_name")
                                  or record.get("qualification") or record.get("title"))

        if not degree_text:
            continue

        # pad so short keywords like "ms " / "be " don't false-match mid-word
        padded = f" {degree_text} "

        for level, keywords in DEGREE_KEYWORDS:
            if any(kw in padded for kw in keywords):
                found_levels.add(level)
                break  # this record matched; move to next education entry

    if not found_levels:
        return ""

    # DEGREE_KEYWORDS is already ordered highest -> lowest
    for level, _ in DEGREE_KEYWORDS:
        if level in found_levels:
            return level

    return ""


# ---------------------------------------------------------
# PSPC employment detection
# ---------------------------------------------------------

PSPC_PATTERNS = [
    r"\bpspc\b",
    r"public services and procurement canada",
    r"public works and government services canada",  # PSPC's former name
    r"\bpwgsc\b",
]


def check_pspc_employment(experience):

    for job in experience or []:

        if not isinstance(job, dict):
            continue

        haystack = _normalize(job.get("organization")) + " " + _normalize(job.get("description"))

        for pattern in PSPC_PATTERNS:
            if re.search(pattern, haystack):
                return True

    return False


# ---------------------------------------------------------
# Security printing experience detection
# ---------------------------------------------------------

SECURITY_PRINTING_KEYWORDS = [
    "security printing",
    "secure printing",
    "banknote",
    "bank note",
    "currency printing",
    "passport printing",
    "stamp printing",
    "excise stamp",
    "anti-counterfeiting",
    "counterfeit-resistant printing",
]


def check_security_printing_experience(experience):

    for job in experience or []:

        if not isinstance(job, dict):
            continue

        haystack = " ".join([
            _normalize(job.get("job_title")),
            _normalize(job.get("organization")),
            _normalize(job.get("description")),
        ])

        if any(kw in haystack for kw in SECURITY_PRINTING_KEYWORDS):
            return True

    return False


# ---------------------------------------------------------
# Main entry point
# ---------------------------------------------------------

def compute_eligibility_features(candidate):
    education = candidate.get("education", [])
    experience = candidate.get("experience", [])

    return {
        "highest_degree_level": determine_highest_degree(education),
        "is_pspc_employee": check_pspc_employment(experience),
        "has_security_printing_experience": check_security_printing_experience(experience),
    }

"""

MAIN TESTING FUNCTION

if __name__ == "__main__":
    # Quick manual sanity check using the Ahmed Siddiqui sample record
    sample_candidate = {
        "education": [
            {"degree": "MS Computer Science", "institute": "NED University", "end_year": "2016"},
            {"degree": "BS Computer Science", "institute": "NED University", "end_year": "2014"},
        ],
        "experience": [
            {
                "job_title": "IT Manager",
                "organization": "Al-Noor Textiles Ltd, Karachi",
                "description": "Led Oracle ERP implementation across 6 plants...",
            },
        ],
    }

    print(compute_eligibility_features(sample_candidate))
    # Expected: {'highest_degree_level': 'masters', 'is_pspc_employee': False,
    #            'has_security_printing_experience': False}

"""