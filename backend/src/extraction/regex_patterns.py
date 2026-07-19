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

# ------------------------ UNUSUAL ENTRIES FOUND IN SOME RESUMES ---------------------------------- # 

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

# -------------------------------------------------------------------------------------------------- #

# CGPA / GPA

cgpa_pattern = re.compile(
    r'(?i)'
    r'(?:cgpa|gpa)'
    r'\s*[:=-]?\s*'
    r'(?:[0-4]\.\d{1,2})'
)