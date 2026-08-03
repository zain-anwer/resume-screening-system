from datetime import datetime
import yaml

from src.policy_engine.rules_adapter import normalize_rules
from src.policy_engine.policy_registry import evaluate_other_policies


# ---------------------------------------------------------
# Load YAML
# ---------------------------------------------------------

def load_rules(yaml_path):
    """Load a policy YAML file and normalize it into the internal shape.
    Tolerates both hand-authored configs and anything produced by the
    frontend PolicyBuilder (including partially-filled ones, since the
    frontend drops empty fields before saving)."""

    with open(yaml_path, "r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    return normalize_rules(raw)


# ---------------------------------------------------------
# Age Calculation
# ---------------------------------------------------------

def calculate_age(date_of_birth, reference_date):

    dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
    ref = datetime.strptime(reference_date, "%Y-%m-%d")

    age = ref.year - dob.year

    if (ref.month, ref.day) < (dob.month, dob.day):
        age -= 1

    return age


# ---------------------------------------------------------
# Education Level Ranking
# ---------------------------------------------------------

LEVELS = {
    "matric": 1,
    "intermediate": 2,
    "diploma": 3,
    "bachelors": 4,
    "masters": 5,
    "mphil": 6,
    "phd": 7
}


def get_candidate_level(candidate):

    level = (
        candidate.get("eligibility_features", {})
        .get("highest_degree_level", "")
        .lower()
    )

    mapping = {
        "diploma": "diploma",
        "associate": "diploma",
        "bachelors": "bachelors",
        "masters": "masters",
        "m.phil": "mphil",
        "mphil": "mphil",
        "phd": "phd"
    }

    return mapping.get(level, "")


def get_education_degree_name(education_record):

    if not isinstance(education_record, dict):
        return ""

    for key in ["degree_name", "degree", "qualification", "title"]:

        value = education_record.get(key)

        if value:
            return str(value)

    return ""


def get_candidate_education_years(candidate):
    """Best-effort lookup of a candidate's total years of education.
    The extraction pipeline's exact field name for this isn't confirmed
    yet, so this tries a few plausible spots and returns None (meaning
    "skip this check") if none are populated, rather than guessing
    wrong. Adjust the key list once the real candidate schema is
    confirmed."""

    features = candidate.get("eligibility_features", {})

    for key in ["total_education_years", "education_years"]:
        value = features.get(key)
        if value not in (None, ""):
            return value

    return None


# ---------------------------------------------------------
# Education Check
# ---------------------------------------------------------

def check_education(candidate, rules):

    result = {"status": False, "reason": ""}

    education_rules = rules["education"]
    minimum = education_rules["minimum_level"]

    if not minimum:
        raw_text = education_rules.get("raw_level_text") or "(not set)"
        result["reason"] = (
            f"Education requirement not configured or unrecognized: "
            f"'{raw_text}'"
        )
        return result

    if minimum not in LEVELS:
        result["reason"] = f"Unrecognized minimum education level: '{minimum}'"
        return result

    candidate_level = get_candidate_level(candidate)

    if candidate_level == "":
        result["reason"] = "Education not found"
        return result

    if LEVELS[candidate_level] < LEVELS[minimum]:
        result["reason"] = f"Minimum education required is {minimum}"
        return result

    # Optional: minimum years of education, if the policy configured it
    # and the candidate record has a matching field.
    required_years = education_rules.get("minimum_years")
    if required_years not in (None, ""):
        candidate_years = get_candidate_education_years(candidate)
        if candidate_years is not None and candidate_years < required_years:
            result["reason"] = (
                f"Minimum {required_years} years of education required, "
                f"candidate has {candidate_years}"
            )
            return result

    # Degree name check — skipped entirely if the policy left the
    # accepted-degrees list empty (HR opted to only require the level).
    if education_rules["any_degree_accepted"]:
        result["status"] = True
        result["reason"] = "Education requirement satisfied"
        return result

    accepted = [x.lower() for x in education_rules["accepted_degrees"]]

    found = False

    for edu in candidate.get("education", []):

        degree = get_education_degree_name(edu).lower()

        if not degree:
            continue

        for req in accepted:
            if req in degree or degree in req:
                found = True
                break

    if not found:

        if education_rules.get("equivalent_or_higher_allowed", False):
            result["status"] = True
            result["reason"] = "Higher qualification accepted"
            return result

        result["reason"] = "Required degree not found"
        return result

    result["status"] = True
    result["reason"] = "Education requirement satisfied"

    return result


# ---------------------------------------------------------
# Experience Check
# ---------------------------------------------------------

def check_experience(candidate, rules):

    required = rules["experience"]["minimum_years"]

    if required in (None, ""):
        return {"status": False, "reason": "Minimum experience not configured"}

    candidate_exp = (
        candidate.get("experience_summary", {})
        .get("total_experience_years", 0)
    )

    if candidate_exp >= required:
        return {
            "status": True,
            "reason": f"{candidate_exp} years experience"
        }

    return {
        "status": False,
        "reason": f"Only {candidate_exp} years experience"
    }


# ---------------------------------------------------------
# Supervisory Experience
# ---------------------------------------------------------

def check_supervisory(candidate, rules):

    required = rules["experience"].get("supervisory_years")

    if required in (None, ""):
        return {"status": True, "reason": "Not required"}

    candidate_years = (
        candidate.get("experience_summary", {})
        .get("management_experience_years", 0)
    )

    if candidate_years >= required:
        return {
            "status": True,
            "reason": f"{candidate_years} supervisory years"
        }

    return {
        "status": False,
        "reason": "Supervisory experience insufficient"
    }


# ---------------------------------------------------------
# Preferred Skills (legacy top-level `preferred` list)
# ---------------------------------------------------------
# Newer policies express this via an "Additional Policy" literally named
# "Preferred Skills" instead — see policy_registry.py. Both are honored;
# results from the two are reported separately (this one on the main
# result dict, the other inside other_policies).

def check_preferred(candidate, rules):

    preferred = rules.get("preferred", [])

    if not preferred:
        return {"status": True, "matched": []}

    skills = candidate.get("skills", [])
    skills = [str(x).lower() for x in skills]

    matched = []

    for item in preferred:
        if item.lower() in " ".join(skills):
            matched.append(item)

    return {"status": True, "matched": matched}


# ---------------------------------------------------------
# Age Check
# ---------------------------------------------------------

def check_age(candidate, rules):

    personal_info = candidate.get("personal_info", {})
    dob = personal_info.get("date_of_birth")

    max_age = rules["age"]["maximum"]

    if max_age in (None, ""):
        return {
            "status": False,
            "candidate_age": None,
            "allowed_age": None,
            "reason": "Maximum age not configured for this policy"
        }

    if not dob:
        return {
            "status": False,
            "candidate_age": None,
            "allowed_age": max_age,
            "reason": "Date of birth not found"
        }

    reference = rules["application"]["reference_date"]
    age = calculate_age(dob, reference)

    address = personal_info.get("address", {})
    province = address.get("province", "")

    relaxation = rules["relaxation"]
    base_max_age = max_age

    # -------------------------------
    # Regional Relaxation (per-region years; take the best match)
    # -------------------------------
    for entry in relaxation["regional"]:
        if province in entry.get("regions", []):
            max_age = max(max_age, base_max_age + entry.get("years", 0))

    # -------------------------------
    # Internal / employee relaxation
    # -------------------------------
    eligibility = candidate.get("eligibility_features", {})

    if eligibility.get("is_pspc_employee", False) and relaxation["employees_years"]:
        max_age = max(max_age, base_max_age + relaxation["employees_years"])

    # -------------------------------
    # Security Printing Relaxation (legacy config only — not yet
    # exposed on the frontend builder)
    # -------------------------------
    security_relax = relaxation["security_printing_experience"]
    if security_relax and eligibility.get("has_security_printing_experience", False):
        max_age = max(max_age, security_relax.get("maximum_age", max_age))

    if age <= max_age:
        return {
            "status": True,
            "candidate_age": age,
            "allowed_age": max_age,
            "reason": "Age within limit"
        }

    return {
        "status": False,
        "candidate_age": age,
        "allowed_age": max_age,
        "reason": "Age exceeds limit"
    }


# ---------------------------------------------------------
# Overall Eligibility
# ---------------------------------------------------------

def evaluate_candidate(candidate, rules):
    """rules must already be normalized (i.e. the return value of
    load_rules() / normalize_rules()) — evaluate_candidate does not
    normalize on its own, so callers that build a rules dict by hand
    should run it through normalize_rules() first."""

    education = check_education(candidate, rules)
    experience = check_experience(candidate, rules)
    supervisory = check_supervisory(candidate, rules)
    age = check_age(candidate, rules)
    preferred = check_preferred(candidate, rules)

    other_policy_results = evaluate_other_policies(
        candidate, rules.get("other_policies", [])
    )

    # Only policies with a registered, automated handler that reports
    # status False can block eligibility. Unregistered / informational
    # entries never affect overall_status.
    other_policies_blocking = any(
        (not p.get("status", True)) and p.get("automated", False)
        for p in other_policy_results
    )

    overall = (
        education["status"]
        and experience["status"]
        and supervisory["status"]
        and age["status"]
        and not other_policies_blocking
    )

    metadata = candidate.get("metadata", {})

    return {

        "candidate_id":
            metadata.get("candidate_id", "Unknown"),

        "job":
            metadata.get("job_category", "Unknown"),

        "overall_status":
            "Eligible"
            if overall
            else
            "Not Eligible",

        "education": education,

        "experience": experience,

        "supervisory": supervisory,

        "age": age,

        "preferred_skills": preferred,

        "other_policies": other_policy_results,
    }
