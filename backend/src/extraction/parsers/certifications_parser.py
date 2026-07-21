# ============================================== #
#          PRELIMINARY CERTIFICATIONS PARSER
# ============================================== #

from regex_patterns import *


# =========================================================
# CERTIFICATION TEMPLATE
# =========================================================

def new_certification_stub():

    return {
        'name': None,
        'issuer': None,
        'issue_date': None,
        'expiry_date': None,
        'credential_id': None,
        'credential_url': None
    }


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_certification_line(line):

    line = line.strip()

    line = CERTIFICATION_LABEL_RE.sub(
        '',
        line
    )

    line = CERTIFICATE_LABEL_RE.sub(
        '',
        line
    )

    return line.strip(
        ' |'
    )


# =========================================================
# INVALID / EMPTY CHECK
# =========================================================

def is_empty_certification(line):

    normalized = (
        line
        .lower()
        .strip(
            ' .,:;|-'
        )
    )

    return (
        not normalized
        or normalized in {
            'n/a',
            'na',
            'none',
            'not applicable',
            'no certifications',
            'no certification'
        }
    )


# =========================================================
# GENERIC CONTAMINATION CHECK
# =========================================================

def is_probably_non_certification(line):

    """
    Generic guardrail for lines that are unlikely to represent
    a certification.

    This deliberately avoids hardcoded language names or issuer names.
    """

    words = line.split()

    if not words:
        return True

    # A short comma-separated list is more likely to be a list
    # of values than a certification title.
    if (
        ',' in line
        and len(words) <= 6
    ):
        return True

    return False


# =========================================================
# NER ORGANIZATION EXTRACTION
# =========================================================

def extract_organizations(
    text,
    ner_pipeline=None
):

    if ner_pipeline is None:

        return []

    entities = ner_pipeline(
        text
    )

    organizations = []

    for entity in entities:

        label = (
            entity.get(
                'entity_group'
            )
            or entity.get(
                'entity'
            )
        )

        if label not in {
            'ORG',
            'B-ORG',
            'I-ORG'
        }:

            continue

        value = (
            entity.get(
                'word'
            )
            or entity.get(
                'text'
            )
        )

        if value:

            organizations.append(
                value.strip()
            )

    return organizations


# =========================================================
# DELIMITED FIELD EXTRACTION
# =========================================================

def extract_pipe_fields(line):

    parts = [
        part.strip(
            ' |'
        )
        for part in line.split(
            '|'
        )
        if part.strip(
            ' |'
        )
    ]

    return parts


def extract_delimited_issuer(
    line,
    ner_pipeline=None
):

    parts = extract_pipe_fields(
        line
    )

    if len(parts) < 2:

        return None, None

    name = parts[0]

    # The remaining fields may include:
    #
    # issuer
    # location
    # date
    #
    # We use NER to identify the organization rather than
    # assuming a fixed position.

    remaining_parts = parts[1:]

    for part in remaining_parts:

        organizations = (
            extract_organizations(
                part,
                ner_pipeline
            )
        )

        if organizations:

            return (
                name,
                organizations[0]
            )

    # If no organization entity is detected,
    # preserve the first structural field as issuer.
    #
    # This maintains the original parser's behavior
    # without relying on issuer keywords.

    return (
        name,
        remaining_parts[0]
    )


# =========================================================
# GENERIC HYPHEN HANDLING
# =========================================================

def extract_hyphen_issuer(
    line,
    ner_pipeline=None
):

    """
    Do NOT blindly split:

        PMP - Project Management Professional

    because the right side may be the expanded certification name.

    Instead, split temporarily and only treat one side as an issuer
    if NER identifies an organization.
    """

    parts = [
        part.strip(
            ' |'
        )
        for part in re.split(
            r'\s+-\s+',
            line
        )
        if part.strip(
            ' |'
        )
    ]

    if len(parts) < 2:

        return None, None

    left = parts[0]

    right = parts[1]

    left_orgs = (
        extract_organizations(
            left,
            ner_pipeline
        )
    )

    right_orgs = (
        extract_organizations(
            right,
            ner_pipeline
        )
    )

    if right_orgs:

        return (
            left,
            right_orgs[0]
        )

    if left_orgs:

        return (
            right,
            left_orgs[0]
        )

    # No organization detected.
    #
    # Therefore, do not make an unsupported assumption.

    return None, None


# =========================================================
# CERTIFICATION PARSER
# =========================================================

def parse_certification_line(
    line,
    ner_pipeline=None
):

    line = normalize_certification_line(
        line
    )

    if is_empty_certification(
        line
    ):

        return None

    if is_probably_non_certification(
        line
    ):

        return None

    certification = (
        new_certification_stub()
    )

    # -----------------------------------------------------
    # Extract URL
    # -----------------------------------------------------

    url_match = URL_RE.search(
        line
    )

    if url_match:

        certification[
            'credential_url'
        ] = url_match.group(
            0
        )

        line = URL_RE.sub(
            '',
            line
        ).strip(
            ' ,;|-'
        )

    # -----------------------------------------------------
    # Extract credential ID
    # -----------------------------------------------------

    credential_id_match = (
        CREDENTIAL_ID_RE.search(
            line
        )
    )

    if credential_id_match:

        certification[
            'credential_id'
        ] = credential_id_match.group(
            1
        )

        line = CREDENTIAL_ID_RE.sub(
            '',
            line
        ).strip(
            ' ,;|-'
        )

    # -----------------------------------------------------
    # Extract dates
    # -----------------------------------------------------

    dates = DATE_RE.findall(
        line
    )

    if len(dates) >= 1:

        certification[
            'issue_date'
        ] = dates[0]

    if len(dates) >= 2:

        certification[
            'expiry_date'
        ] = dates[1]

    for date in dates:

        line = line.replace(
            date,
            ''
        )

    line = line.strip(
        ' ,;|-'
    )

    # -----------------------------------------------------
    # Pipe-delimited structure
    # -----------------------------------------------------

    name, issuer = (
        extract_delimited_issuer(
            line,
            ner_pipeline
        )
    )

    if name:

        certification[
            'name'
        ] = name

        certification[
            'issuer'
        ] = issuer

        return certification

    # -----------------------------------------------------
    # Hyphen-delimited structure
    # -----------------------------------------------------

    name, issuer = (
        extract_hyphen_issuer(
            line,
            ner_pipeline
        )
    )

    if name:

        certification[
            'name'
        ] = name

        certification[
            'issuer'
        ] = issuer

        return certification

    # -----------------------------------------------------
    # Plain certification text
    #
    # Example:
    #
    # AWS Certified Solutions Architect
    #
    # The NER model can identify AWS as ORG.
    # -----------------------------------------------------

    organizations = (
        extract_organizations(
            line,
            ner_pipeline
        )
    )

    if organizations:

        issuer = organizations[0]

        issuer_start = (
            line.lower().find(
                issuer.lower()
            )
        )

        issuer_end = (
            issuer_start
            + len(issuer)
        )

        # If the organization is at the beginning,
        # remove it from the certification name.
        #
        # Example:
        #
        # AWS Certified Solutions Architect
        #
        # becomes:
        #
        # issuer: AWS
        # name:   Certified Solutions Architect
        #

        if issuer_start == 0:

            name = (
                line[
                    issuer_end:
                ]
                .strip(
                    ' ,:-|'
                )
            )

            certification[
                'name'
            ] = (
                name
                if name
                else line
            )

            certification[
                'issuer'
            ] = issuer

            return certification

        # Otherwise preserve the full certification text.
        #
        # This is safer when the organization appears as part
        # of the certification title.

        certification[
            'name'
        ] = line

        certification[
            'issuer'
        ] = issuer

        return certification

    # -----------------------------------------------------
    # Final fallback
    # -----------------------------------------------------

    certification[
        'name'
    ] = line

    return certification


# =========================================================
# COMPLETE CERTIFICATIONS PARSER
# =========================================================

def parse_certifications_section(
    certification_lines,
    ner_pipeline=None
):

    certifications = []

    seen = set()

    for raw_line in certification_lines:

        if not isinstance(
            raw_line,
            str
        ):

            continue

        certification = (
            parse_certification_line(
                raw_line,
                ner_pipeline
            )
        )

        if certification is None:

            continue

        if not certification[
            'name'
        ]:

            continue

        key = (
            certification[
                'name'
            ]
            .lower()
            .strip()
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        certifications.append(
            certification
        )

    return certifications