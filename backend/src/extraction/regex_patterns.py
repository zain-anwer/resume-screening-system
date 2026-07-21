import re


# pakistani phone numbers
phone_pattern = re.compile(
    r'(?:(?:\+92|0092)[\s-]?)?'
    r'(?:0?3\d{2})[\s-]?\d{7}'
)

# phone number permissive regex
general_phone_pattern = re.compile(
    r'\+?\d[\d\s().-]{7,}\d'
)

# pakistani CNIC
# extract if available then flag mismatch
cnic_pattern = re.compile(
    r'\b\d{5}[-\s]?\d{7}[-\s]?\d\b'
)

# email addresses
email_pattern = re.compile(
    r'\b[a-zA-Z0-9._%+-]+'
    r'@'
    r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
)

# URLs (does not match emails because @ is excluded)
url_pattern = re.compile(
    r'(?<!@)\b'
    r'(?:https?://|www\.)?'
    r'[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+'
    r'(?:/[^\s@]*)?'
    r'\b',
    re.I
)

# father's name appears in some so
father_pattern = re.compile(
    r'(?im)^\s*'
    r'(?:'
        r"Father(?:'s)?(?:\s+Name)?"
        r'|S\s*/\s*O'
        r'|Son\s+of'
    r')'
    r'\s*:?\s*'
    r'(?P<father>[^\n\r]+)'
)

# DOB appears in some as well so
dob_pattern = re.compile(
    r'(?im)^\s*'
    r'(?:'
        r'D\.?\s*O\.?\s*B\.?'          # DOB, D.O.B.
        r'|Date\s+of\s+Birth'
        r'|Birth\s+Date'
        r'|Born'
    r')'
    r'\s*:?\s*'
    r'(?P<dob>[^\n\r]+)'
)

gender_pattern = re.compile(
    r'(?im)^\s*'
    r'(?:'
        r'Gender'
        r'|Sex'
    r')'
    r'\s*:?\s*'
    r'(?P<gender>Male|Female|M|F|Man|Woman|Other|Non[- ]?Binary|Prefer\s+Not\s+To\s+Say)'
    r'\s*$'
)

nationality_pattern = re.compile(
    r'(?im)^\s*Nationality\s*:?\s*(?P<nationality>[^\n\r]+)'
)

marital_status_pattern = re.compile(
    r'(?im)^\s*Marital\s+Status\s*:?\s*(?P<marital>Single|Married|Divorced|Widowed)'
)

degree_pattern = re.compile(
    r'\b('
    r'ph\.?\s*d\b|'
    r'm\.?\s*phil\b|'
    r'm\.?\s*(?:sc|s)\b|'
    r'b\.?\s*(?:sc|s)\b|'
    r'm\.?\s*eng\b|'
    r'b\.?\s*eng\b|'
    r'master(?:s)?\b|'
    r'bachelor(?:s)?\b|'
    r'bba\b|'
    r'mba\b|'
    r'bcom\b|'
    r'mcom\b|'
    r'be\b|'
    r'me\b|'
    r'dae\b|'
    r'intermediate\b|'
    r'fsc\b|'
    r'ics\b|'
    r'matric(?:ulation)?\b|'
    r'diploma\b'
    r')',
    re.I
)


year_pattern = re.compile(
    r'\b(?P<start>(?:19|20)\d{2})'
    r'(?:\s*[-–—]\s*'
    r'(?P<end>'
        r'(?:19|20)?\d{2}'
        r'|present'
        r'|current'
        r'|continue(?:d)?'
        r'|ongoing'
        r'|till\s+date'
    r'))?\b',
    re.I
)


cgpa_pattern = re.compile(
    r'\b(?:cgpa|gpa)'
    r'\s*[:=-]?\s*'
    r'(\d(?:\.\d{1,2})?)',
    re.I
)


scale_pattern = re.compile(
    r'\b(?:out\s+of|/)\s*\d+(?:\.\d+)?\b',
    re.I
)

institute_keywords = re.compile(
    r'\b('
    r'university|'
    r'institute|'
    r'college|'
    r'school|'
    r'polytechnic|'
    r'campus|'
    r'board|'
    r'academy|'
    r'faculty|'
    r'centre|'
    r'center'
    r')\b',
    re.I
)

known_institutions = re.compile(
    r'\b(?:'
    r'IBA|'
    r'LUMS|'
    r'FAST|'
    r'NUST|'
    r'GIKI|'
    r'COMSATS|'
    r'AKU|'
    r'Bahria|'
    r'PIEAS'
    r')\b',
    re.IGNORECASE
)

title_keywords = re.compile(
    r'\b('
    r'manager|engineer|developer|consultant|analyst|officer|architect|'
    r'administrator|technician|specialist|lead|head|director|executive|'
    r'intern|assistant|operator|coordinator|associate|project|supervisor'
    r')\b',
    re.I
)


MONTH_NAME = (
    r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|'
    r'may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|'
    r'oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
)


DATE_VALUE = (
    rf'(?:'
        rf'{MONTH_NAME}\.?\s*,?\s*(?:19|20)\d{{2}}'
        rf'|'
        rf'\d{{1,2}}/\d{{4}}'
        rf'|'
        rf'(?:19|20)\d{{2}}'
    rf')'
)


experience_date_pattern = re.compile(
    rf'(?P<start>{DATE_VALUE})'
    r'\s*(?:[-–—]|to)\s*'
    rf'(?P<end>'
        rf'{DATE_VALUE}'
        r'|present|current|continue(?:d)?|date'
    rf')',
    re.I
)


chunk_pattern = re.compile(
    r'\s*(?:\||•|▪|(?<!\d)\s-\s(?!\d|present|current|continue))\s*',
    re.I
)

