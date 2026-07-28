import re
from datetime import date
from calendar import monthrange

_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

_OPEN_ENDED = {"present", "current", "currently", "continue", "continuing",
               "till date", "to date", "now", "ongoing", "date"}

_YEAR_RE = re.compile(r"(19|20)\d{2}")
_MONTH_RE = re.compile(
    r"\b(" + "|".join(sorted(_MONTHS.keys(), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

# Management role keywords — matched as whole words against job_title.
# Order doesn't matter here since it's just membership testing.
_MANAGEMENT_KEYWORDS = {
    "manager", "management", "managing",
    "director", "head", "chief",
    "lead", "leader", "leading",
    "supervisor", "supervising",
    "vp", "vice president",
    "president", "ceo", "cto", "cfo", "coo",
    "principal", "president",
    "executive",
    "team lead", "tech lead",
}

_MANAGEMENT_KEYWORD_RE = re.compile(
    r"\b(" + "|".join(sorted((re.escape(k) for k in _MANAGEMENT_KEYWORDS), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def _parse_date(raw, *, is_end=False, today=None):

    if today is None:
        today = date.today()

    if raw is None:
        return None

    text = str(raw).strip()
    if not text:
        return None

    low = text.lower().strip(" .")
    if low in _OPEN_ENDED:
        return today if is_end else None

    year_match = _YEAR_RE.search(text)
    if not year_match:
        return None
    year = int(year_match.group(0))

    month_match = _MONTH_RE.search(text)
    month = _MONTHS[month_match.group(1).lower()] if month_match else None

    if month is None:
        # Year-only entry
        return date(year, 12, 31) if is_end else date(year, 1, 1)

    if is_end:
        last_day = monthrange(year, month)[1]
        return date(year, month, last_day)
    return date(year, month, 1)


def _merge_intervals(intervals):
    """Merge overlapping/adjacent (start, end) date intervals."""
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda iv: iv[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:  # overlap or touching -> merge
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def _is_management_title(job_title):
    """Return True if job_title contains a management-role keyword."""
    if not job_title:
        return False
    return bool(_MANAGEMENT_KEYWORD_RE.search(str(job_title)))


def _build_intervals(experience, *, today, management_only=False):
    intervals = []
    for entry in experience:
        if not isinstance(entry, dict):
            continue
        if management_only and not _is_management_title(entry.get("job_title")):
            continue
        start = _parse_date(entry.get("start_date"), is_end=False, today=today)
        if start is None:
            continue
        end = _parse_date(entry.get("end_date"), is_end=True, today=today)
        if end is None:
            end = today
        if end < start:
            start, end = end, start
        intervals.append((start, end))
    return intervals


def _years_from_intervals(intervals, round_to):
    merged = _merge_intervals(intervals)
    total_days = sum((end - start).days for start, end in merged)
    years = total_days / 365.25
    return round(years, round_to) if round_to is not None else years


def get_total_experience_years(experience, *, today=None, round_to=2):
    if not experience:
        return 0.0
    if today is None:
        today = date.today()

    intervals = _build_intervals(experience, today=today, management_only=False)
    return _years_from_intervals(intervals, round_to)


def get_management_experience_years(experience, *, today=None, round_to=2):
  
    if not experience:
        return 0.0
    if today is None:
        today = date.today()

    intervals = _build_intervals(experience, today=today, management_only=True)
    return _years_from_intervals(intervals, round_to)


def get_experience_summary(experience, *, today=None, round_to=2):
    
    if today is None:
        today = date.today()

    flagged = [
        entry.get("job_title")
        for entry in (experience or [])
        if isinstance(entry, dict) and _is_management_title(entry.get("job_title"))
    ]

    return {
        "total_experience_years": get_total_experience_years(experience, today=today, round_to=round_to),
        "management_experience_years": get_management_experience_years(experience, today=today, round_to=round_to),
        "management_titles_flagged": flagged,
    }