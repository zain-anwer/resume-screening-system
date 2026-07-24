from datetime import datetime
import yaml


# ---------------------------------------------------------
# Load YAML
# ---------------------------------------------------------

def load_rules(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


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


# ---------------------------------------------------------
# Education Check
# ---------------------------------------------------------

def check_education(candidate, rules):

    result = {
        "status": False,
        "reason": ""
    }

    minimum = rules["education"]["minimum_level"]

    candidate_level = get_candidate_level(candidate)

    if candidate_level == "":

        result["reason"] = "Education not found"
        return result

    if LEVELS[candidate_level] < LEVELS[minimum]:

        result["reason"] = (
            f"Minimum education required is {minimum}"
        )

        return result

    accepted = [
        x.lower()
        for x in rules["education"]["accepted_degrees"]
    ]

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

        if rules["education"].get(
                "equivalent_or_higher_allowed",
                False):

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

    if "supervisory_years" not in rules["experience"]:

        return {
            "status": True,
            "reason": "Not required"
        }

    required = rules["experience"]["supervisory_years"]

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
# Preferred Skills
# ---------------------------------------------------------

def check_preferred(candidate, rules):

    if "preferred" not in rules:

        return {
            "status": True,
            "matched": []
        }

    skills = candidate.get("skills", [])

    skills = [str(x).lower() for x in skills]

    matched = []

    for item in rules["preferred"]:

        if item.lower() in " ".join(skills):
            matched.append(item)

    return {
        "status": True,
        "matched": matched
    }
# ---------------------------------------------------------
# Age Check
# ---------------------------------------------------------

def check_age(candidate, rules):

    personal_info = candidate.get("personal_info", {})

    dob = personal_info.get("date_of_birth")

    if not dob:
        return {
            "status": False,
            "candidate_age": None,
            "allowed_age": rules["age"]["maximum"],
            "reason": "Date of birth not found"
        }

    reference = rules["application"]["reference_date"]

    age = calculate_age(
        dob,
        reference
    )

    max_age = rules["age"]["maximum"]

    # -------------------------------
    # Address may not exist
    # -------------------------------
    address = personal_info.get("address", {})

    province = address.get("province", "")

    # -------------------------------
    # Regional Relaxation
    # -------------------------------
    if "regional" in rules.get("relaxation", {}):

        region_rules = rules["relaxation"]["regional"]

        if province in region_rules.get("regions", []):

            max_age += region_rules.get("years", 0)

    eligibility = candidate.get("eligibility_features", {})

    # -------------------------------
    # PSPC Employee Relaxation
    # -------------------------------
    if eligibility.get("is_pspc_employee", False):

        if "pspc_employee" in rules.get("relaxation", {}):

            max_age += (
                rules["relaxation"]["pspc_employee"]
                .get("years", 0)
            )

    # -------------------------------
    # Security Printing Relaxation
    # -------------------------------
    if eligibility.get("has_security_printing_experience", False):

        if "security_printing_experience" in rules.get("relaxation", {}):

            max_age = max(
                max_age,
                rules["relaxation"]["security_printing_experience"]
                .get("maximum_age", max_age)
            )

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

    education = check_education(candidate, rules)

    experience = check_experience(candidate, rules)

    supervisory = check_supervisory(candidate, rules)

    age = check_age(candidate, rules)

    preferred = check_preferred(candidate, rules)

    overall = (
        education["status"]
        and experience["status"]
        and supervisory["status"]
        and age["status"]
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

        "preferred_skills": preferred
    }