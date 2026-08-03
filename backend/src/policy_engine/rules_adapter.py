"""
Normalizes policy rule dicts (loaded from YAML) into one internal shape
that the rest of policy_engine can rely on.

Why this exists
----------------
Policy YAML now comes from two places that don't agree on field names:

  * hand-authored config files (older shape) — e.g.
        relaxation:
          regional: {regions: [...], years: 3}
          pspc_employee: {years: 2}
        education:
          minimum_level: bachelors
          accepted_degrees: [...]
        application:
          reference_date: "2026-01-01"

  * the PolicyBuilder frontend (new shape) — e.g.
        age_relaxation:
          regional: [{region: ..., relaxation_years: ...}, ...]
          employees: {applicable: true, relaxation_years: 2}
        education:
          level: "BS"
          degrees: [...]

The frontend also runs every saved policy through a `deepClean()` step,
so any section can be a partial object or missing entirely rather than
present-with-empty-values. Nothing downstream should assume a key exists.

normalize_rules() is the single place that absorbs all of that variance.
Every check_* function in eligibility.py should read from its output,
never from the raw YAML dict.
"""

import re
from datetime import date


# ---------------------------------------------------------
# Education level aliases
# ---------------------------------------------------------
# The frontend collects education level as free text (e.g. "BS", "MS",
# "PhD"). This maps common variants onto the internal LEVELS keys used
# by eligibility.py. Extend this as new phrasing shows up in real data.

_LEVEL_ALIASES = {
    "matric": "matric", "ssc": "matric", "matriculation": "matric",
    "intermediate": "intermediate", "fsc": "intermediate", "f.sc": "intermediate",
    "hssc": "intermediate", "a level": "intermediate", "a-level": "intermediate",
    "diploma": "diploma", "associate": "diploma", "associates": "diploma",
    "bachelors": "bachelors", "bachelor": "bachelors", "bachelor's": "bachelors",
    "bs": "bachelors", "b.s": "bachelors", "bsc": "bachelors", "b.sc": "bachelors",
    "ba": "bachelors", "b.a": "bachelors", "beng": "bachelors", "b.eng": "bachelors",
    "masters": "masters", "master": "masters", "master's": "masters",
    "ms": "masters", "m.s": "masters", "msc": "masters", "m.sc": "masters",
    "ma": "masters", "m.a": "masters", "mba": "masters",
    "mphil": "mphil", "m.phil": "mphil", "m phil": "mphil",
    "phd": "phd", "ph.d": "phd", "ph.d.": "phd", "doctorate": "phd",
}


def _slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text or "").strip().lower()).strip("_")


def normalize_education_level(raw_text):
    """Map free-text education level onto an internal LEVELS key, or
    return None if it can't be recognized."""
    if not raw_text:
        return None
    key = str(raw_text).strip().lower().replace("’", "'")
    return _LEVEL_ALIASES.get(key)


# ---------------------------------------------------------
# Section normalizers
# ---------------------------------------------------------

def _normalize_relaxation(raw):
    """Combine legacy `relaxation.*` and new `age_relaxation.*` into one
    shape:

        {
            "regional": [{"regions": [...], "years": N}, ...],
            "employees_years": N or None,
            "security_printing_experience": {"maximum_age": N} or None,
        }

    `regional` is a list (not a single dict) because the new builder
    lets HR set a different relaxation for each region.
    """
    legacy = raw.get("relaxation") or {}
    new = raw.get("age_relaxation") or {}

    regional_entries = []

    legacy_regional = legacy.get("regional")
    if isinstance(legacy_regional, dict) and legacy_regional.get("regions"):
        regional_entries.append({
            "regions": legacy_regional.get("regions", []),
            "years": legacy_regional.get("years", 0) or 0,
        })

    new_regional = new.get("regional")
    if isinstance(new_regional, list):
        for entry in new_regional:
            if not isinstance(entry, dict):
                continue
            region = entry.get("region")
            years = entry.get("relaxation_years")
            if region and years not in (None, ""):
                regional_entries.append({"regions": [region], "years": years})

    employees_years = None
    legacy_employee = legacy.get("pspc_employee")
    if isinstance(legacy_employee, dict) and legacy_employee.get("years") not in (None, ""):
        employees_years = legacy_employee["years"]

    new_employee = new.get("employees")
    if isinstance(new_employee, dict) and new_employee.get("applicable"):
        candidate_years = new_employee.get("relaxation_years")
        if candidate_years not in (None, ""):
            employees_years = max(employees_years or 0, candidate_years)

    security_printing = None
    legacy_security = legacy.get("security_printing_experience")
    if isinstance(legacy_security, dict) and legacy_security.get("maximum_age") not in (None, ""):
        # Not currently exposed in the frontend builder — only reachable
        # via a hand-edited or legacy config file.
        security_printing = {"maximum_age": legacy_security["maximum_age"]}

    return {
        "regional": regional_entries,
        "employees_years": employees_years,
        "security_printing_experience": security_printing,
    }


def _normalize_education(raw):
    section = raw.get("education") or {}

    minimum_level = section.get("minimum_level")
    raw_level_text = section.get("level")
    if not minimum_level and raw_level_text:
        minimum_level = normalize_education_level(raw_level_text)

    accepted_degrees = section.get("accepted_degrees")
    if accepted_degrees is None:
        accepted_degrees = section.get("degrees") or []

    return {
        "minimum_level": minimum_level,
        # kept only for error messages when minimum_level can't be resolved
        "raw_level_text": raw_level_text or section.get("minimum_level") or "",
        "accepted_degrees": accepted_degrees,
        # if HR left the degree list empty, any degree at the required
        # level is accepted (this matches the frontend's own hint text)
        "any_degree_accepted": len(accepted_degrees) == 0,
        "equivalent_or_higher_allowed": section.get("equivalent_or_higher_allowed", False),
        "minimum_years": section.get("minimum_years"),
    }


def _normalize_experience(raw):
    section = raw.get("experience") or {}
    return {
        "minimum_years": section.get("minimum_years"),
        "supervisory_years": section.get("supervisory_years"),
    }


def _normalize_application(raw):
    section = raw.get("application") or {}
    reference_date = section.get("reference_date")
    defaulted = False
    if not reference_date:
        # The frontend has no field for this today, so fall back to
        # "evaluate as of today" rather than failing every candidate.
        reference_date = date.today().strftime("%Y-%m-%d")
        defaulted = True
    return {"reference_date": reference_date, "reference_date_defaulted": defaulted}


def normalize_rules(raw):
    """Turn a raw policy dict (loaded straight from YAML) into the
    internal shape used throughout policy_engine. Safe to call on
    partial/incomplete dicts — every section defaults to something
    inert rather than raising.
    """
    raw = raw or {}

    return {
        "job_name": raw.get("job_name") or raw.get("job") or "Unknown",
        "age": {"maximum": (raw.get("age") or {}).get("maximum")},
        "relaxation": _normalize_relaxation(raw),
        "education": _normalize_education(raw),
        "experience": _normalize_experience(raw),
        "application": _normalize_application(raw),
        "preferred": list(raw.get("preferred") or []),
        "other_policies": raw.get("other_policies") or [],
    }
