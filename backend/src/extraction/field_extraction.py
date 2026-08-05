# preprocessing imports
from src.extraction.utils.layout_reconstruction import reconstruct_resume_layout
from src.extraction.utils.section_segregation import segregate_text
from src.extraction.utils.text_normalization import normalize_ocr_text
from src.extraction.utils.personal_info_reconciliation import reconcile_personal_info

# parser imports
from src.extraction.parsers.certifications_parser import parse_certifications_section
from src.extraction.parsers.education_parser import parse_education_section
from src.extraction.parsers.experience_parser import parse_experience_section
from src.extraction.parsers.header_parser import parse_header_section
from src.extraction.parsers.projects_parser import parse_projects_section
from src.extraction.parsers.references_parser import parse_references
from src.extraction.parsers.skills_parser import parse_skills_section

# postprocessing imports
from src.extraction.utils.experience_years_computation import get_experience_summary
from src.extraction.utils.eligibility_features_computation import compute_eligibility_features

import json


def section_has_text(section_lines):
    """
    Checks whether a segregated OCR section contains meaningful text.

    Sections are stored as lists of lines.
    """
    if not section_lines:
        return False

    return any(
        isinstance(line, str) and line.strip()
        for line in section_lines
    )


def extraction_is_low_quality(extracted_data):
    """
    Detects cases where parser returned something,
    but the extracted structure is probably unusable.
    """
    if not extracted_data:
        return True

    if isinstance(extracted_data, list):
        meaningful_items = 0

        for item in extracted_data:
            if isinstance(item, dict):
                meaningful_fields = [
                    value
                    for value in item.values()
                    if value not in (None, "", [], {})
                ]
                # Require at least two useful extracted fields
                if len(meaningful_fields) >= 2:
                    meaningful_items += 1
            else:
                if item:
                    meaningful_items += 1

        return meaningful_items == 0

    return False


def add_review_flag(flags, section, reason):
    flags["needs_ner_review"] = True

    entry = {
        "field": section,
        "reason": reason
    }

    if entry not in flags["ner_review_reasons"]:
        flags["ner_review_reasons"].append(entry)


def add_missing_field(flags, section):
    if section not in flags["missing_fields"]:
        flags["missing_fields"].append(section)


def extract_fields(input_path: str, output_path: str):

    with open(input_path, "r", encoding="utf-8") as file:
        inputs = json.load(file)

    inputs = reconstruct_resume_layout(inputs)

    outputs = []

    for input in inputs:

        output = {}

        # ----------------------------
        # PREPROCESSING
        # ----------------------------

        input["resume_text"] = normalize_ocr_text(
            input["resume_text"]
        )

        segregated_text = segregate_text(
            input["resume_text"]
        )

        flags = {
            "needs_ner_review": False,
            "ner_review_reasons": [],
            "missing_fields": []
        }

        # ----------------------------
        # IMAGE QUALITY & CNIC CHECKS
        # ----------------------------

        # 1. Resume Blur Check
        if input.get("resume_blurred") or input.get("resume_manual_review"):
            add_review_flag(
                flags,
                "resume",
                f"Resume image flagged as blurred (blur score: {input.get('resume_blur_score', 0.0)})"
            )

        # 2. CNIC Availability Check
        cnic_name = input.get("cnic_name")
        cnic_number = input.get("cnic_number")
        
        if not cnic_name and not cnic_number:
            add_missing_field(flags, "cnic")
            add_review_flag(
                flags,
                "cnic",
                "CNIC details are missing or could not be extracted"
            )
        else:
            # 3. CNIC Blur Check (if CNIC is present)
            if input.get("cnic_blurred") or input.get("cnic_manual_review"):
                add_review_flag(
                    flags,
                    "cnic",
                    f"CNIC image flagged as blurred (blur score: {input.get('cnic_blur_score', 0.0)})"
                )

        # ----------------------------
        # HEADER
        # ----------------------------

        personal_info, urls = parse_header_section(
            segregated_text.get("header", [])
        )

        personal_info, reconciliation_flags = reconcile_personal_info(
            personal_info,
            input
        )

        flags.update(reconciliation_flags)

        # ----------------------------
        # SECTION EXTRACTION
        # ----------------------------

        education = parse_education_section(
            segregated_text.get("education", [])
        )

        experience = parse_experience_section(
            segregated_text.get("experience", [])
        )

        skills = parse_skills_section(
            segregated_text.get("skills", [])
        )

        projects = parse_projects_section(
            segregated_text.get("projects", []),
            skills
        )

        certifications = parse_certifications_section(
            segregated_text.get("certifications", [])
        )

        references = parse_references(
            segregated_text.get("references", [])
        )

        extracted_sections = {
            "education": education,
            "experience": experience,
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "references": references
        }

        # ----------------------------
        # EXTRACTION VALIDATION
        # ----------------------------

        for section, extracted_data in extracted_sections.items():

            section_exists = section_has_text(
                segregated_text.get(section, [])
            )

            # OCR text exists but parser failed
            if section_exists and extraction_is_low_quality(extracted_data):
                add_review_flag(
                    flags,
                    section,
                    (
                        f"{section} section contained OCR text "
                        "but extraction returned empty or low-quality data"
                    )
                )

            # No OCR text and nothing extracted
            elif not section_exists and not extracted_data:
                add_missing_field(
                    flags,
                    section
                )

        # ----------------------------
        # OUTPUT BUILD
        # ----------------------------

        output["id"] = input["hash_id"]

        output["personal_info"] = personal_info

        output["education"] = education
        output["experience"] = experience
        output["projects"] = projects
        output["skills"] = skills
        output["certifications"] = certifications

        output["achievements"] = []
        output["publications"] = []
        output["languages"] = []

        output["urls"] = urls
        output["summary"] = None

        output["experience_summary"] = (
            get_experience_summary(
                experience
            )
        )

        output["eligibility_features"] = (
            compute_eligibility_features(
                output
            )
        )

        output["additional_sections"] = {
            "references": references,
            "interests": []
        }

        output["flags"] = flags

        output["metadata"] = {
            "job_category": input["job_category"],
            "candidate_id": input["hash_id"]
        }

        outputs.append(output)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            outputs,
            file,
            indent=2
        )