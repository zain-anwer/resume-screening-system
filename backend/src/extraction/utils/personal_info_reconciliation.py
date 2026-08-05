from rapidfuzz import fuzz
from dateutil import parser


def dates_are_equal(date_1, date_2):
    try:
        return parser.parse(date_1, fuzzy=True).date() == parser.parse(date_2, fuzzy=True).date()

    except (ValueError, TypeError, OverflowError):
        return False


def reconcile_personal_info(personal_info, input_dict):

    flags = {
        "needs_ner_review": False,
        "ner_review_reasons": [],
        "missing_fields": []
    }

    def add_ner_review(field, reason):
        flags["needs_ner_review"] = True
        flags["ner_review_reasons"].append({
            "field": field,
            "reason": reason
        })

    # If CNIC verification data is unavailable, skip reconciliation
    if (
        not input_dict.get("cnic_number") or
        not input_dict.get("cnic_name") or
        not input_dict.get("cnic_dob")
    ):
        return personal_info, flags


    # Name reconciliation
    if personal_info.get("name"):
        if fuzz.ratio(
            personal_info["name"].lower(),
            input_dict["cnic_name"].lower()
        ) < 80:

            add_ner_review(
                "name",
                "Extracted name does not match CNIC name"
            )

        personal_info["name"] = input_dict["cnic_name"]

    else:
        personal_info["name"] = input_dict["cnic_name"]


    # CNIC reconciliation
    if personal_info.get("cnic"):
        if personal_info["cnic"] != input_dict["cnic_number"]:

            add_ner_review(
                "cnic",
                "Extracted CNIC number does not match CNIC document"
            )

    else:
        personal_info["cnic"] = input_dict["cnic_number"]


    # DOB reconciliation
    if personal_info.get("date_of_birth"):
        if not dates_are_equal(
            personal_info["date_of_birth"],
            input_dict["cnic_dob"]
        ):

            add_ner_review(
                "date_of_birth",
                "Extracted date of birth does not match CNIC date of birth"
            )

    else:
        personal_info["date_of_birth"] = input_dict["cnic_dob"]


    # Infer gender from CNIC
    if not personal_info.get("gender") and personal_info.get("cnic"):

        last_digit = int(personal_info["cnic"][-1])
        personal_info["gender"] = "Male" if last_digit % 2 else "Female"


    # Missing fields check
    for key, value in personal_info.items():
        if value is None or value == "" or value == []:
            flags["missing_fields"].append(key)


    return personal_info, flags