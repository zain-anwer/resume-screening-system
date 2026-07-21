# ==========================================================
#                 REFERENCES PARSER
# ==========================================================

import re
import copy
from regex_patterns import *

# ----------------------------------------------------------
# Output template
# ----------------------------------------------------------

REFERENCE_TEMPLATE = {
    "name": None,
    "designation": None,
    "organization": None,
    "phone": None,
    "email": None
}

# ----------------------------------------------------------
# Utility functions
# ----------------------------------------------------------

def clean_text(text):
    """
    Normalize whitespace without destroying useful punctuation.
    """
    if not isinstance(text, str):
        return ""

    return re.sub(r'\s+', ' ', text).strip()


def is_empty_reference_value(text):
    """
    Detect references that do not contain actual contact information.
    """

    normalized = clean_text(text).lower()

    return normalized in {
        "",
        "n/a",
        "na",
        "none",
        "not available",
        "will be provided on request",
        "available on request",
        "references available on request",
        "references will be provided on request"
    }


# ----------------------------------------------------------
# Main parser
# ----------------------------------------------------------

def parse_references(reference_data):

    if not reference_data:
        return []

    # ------------------------------------------------------
    # Flatten and clean input
    # ------------------------------------------------------

    if isinstance(reference_data, str):
        reference_data = [reference_data]

    lines = [
        clean_text(item)
        for item in reference_data
        if clean_text(item)
    ]

    if not lines:
        return []

    # ------------------------------------------------------
    # Handle generic non-reference statements
    # ------------------------------------------------------

    if len(lines) == 1 and is_empty_reference_value(lines[0]):
        return []

    references = []

    # ------------------------------------------------------
    # Parse the section
    # ------------------------------------------------------

    i = 0

    while i < len(lines):

        current_line = lines[i]

        # --------------------------------------------------
        # Ignore generic "available on request" entries
        # --------------------------------------------------

        if is_empty_reference_value(current_line):
            i += 1
            continue

        # --------------------------------------------------
        # Determine whether this is a standalone name
        # --------------------------------------------------

        name = current_line

        # Usually the next line contains:
        #
        # Designation, Organization | Phone
        #
        # Example:
        # Director IT, Al-Noor Textiles Ltd | 0300-1112223
        #
        detail_line = ""

        if i + 1 < len(lines):
            next_line = lines[i + 1]

            # If the next line contains contact/detail information,
            # treat it as part of the current reference.
            if (
                "|" in next_line
                or PHONE_PATTERN.search(next_line)
                or EMAIL_PATTERN.search(next_line)
                or "," in next_line
            ):
                detail_line = next_line
                i += 1

        # --------------------------------------------------
        # Create a fresh reference object
        # --------------------------------------------------

        reference = copy.deepcopy(REFERENCE_TEMPLATE)

        reference["name"] = name

        # --------------------------------------------------
        # Extract email
        # --------------------------------------------------

        email_match = EMAIL_PATTERN.search(detail_line)

        if email_match:
            reference["email"] = email_match.group(0)

            detail_line = (
                detail_line[:email_match.start()]
                + detail_line[email_match.end():]
            ).strip()

        # --------------------------------------------------
        # Extract phone
        # --------------------------------------------------

        phone_match = PHONE_PATTERN.search(detail_line)

        if phone_match:
            reference["phone"] = phone_match.group(0)

            detail_line = (
                detail_line[:phone_match.start()]
                + detail_line[phone_match.end():]
            ).strip()

        # --------------------------------------------------
        # Remove separators
        # --------------------------------------------------

        detail_line = detail_line.strip(" |,-")

        # --------------------------------------------------
        # Parse designation and organization
        # --------------------------------------------------

        if detail_line:

            parts = [
                part.strip()
                for part in detail_line.split(",")
                if part.strip()
            ]

            if len(parts) >= 2:

                # First component is usually the designation
                reference["designation"] = parts[0]

                # Remaining components form the organization
                reference["organization"] = ", ".join(parts[1:])

            elif len(parts) == 1:

                # If there is only one detail value,
                # preserve it as designation.
                reference["designation"] = parts[0]

        # --------------------------------------------------
        # Keep only meaningful references
        # --------------------------------------------------

        if (
            reference["name"]
            or reference["designation"]
            or reference["organization"]
            or reference["phone"]
            or reference["email"]
        ):
            references.append(reference)

        i += 1

    return references
