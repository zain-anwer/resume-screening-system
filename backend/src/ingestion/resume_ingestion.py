import hashlib
import json
from pathlib import Path

from src.ingestion.utils.parser import (
    get_all_candidates,
    extract_text,
    extract_cnic_details,
)
from src.ingestion.utils.cleaner import clean_text


def ingest_resumes(input_path: str, output_path: str):

    output_file_path = Path(output_path)

    # Create parent directories if they don't exist
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    candidates = get_all_candidates(input_path)

    all_candidates = []

    print("=" * 60)
    print(f"Found {len(candidates)} candidates")
    print("=" * 60)

    for candidate in candidates:

        job_category = clean_text(candidate["job_category"])
        candidate_id = clean_text(candidate["candidate_id"])

        # -------------------------------------------------
        # Resume
        # -------------------------------------------------

        resume_text = ""
        resume_manual_review = False
        resume_blurred = False
        resume_blur_score = 0.0

        if candidate["resume"] is not None:

            resume_result = extract_text(candidate["resume"])

            if isinstance(resume_result, dict):

                resume_text = clean_text(
                    resume_result.get("text", "")
                )

                resume_manual_review = bool(
                    resume_result.get("manual_review", False)
                )

                resume_blurred = bool(
                    resume_result.get("blurred", False)
                )

                resume_blur_score = float(
                    resume_result.get("blur_score", 0.0)
                )

            else:

                resume_text = clean_text(resume_result)

        # -------------------------------------------------
        # CNIC
        # -------------------------------------------------

        cnic_data = extract_cnic_details(candidate["cnic"])

        cnic_manual_review = False
        cnic_blurred = False
        cnic_blur_score = 0.0

        if candidate["cnic"] is not None:

            cnic_result = extract_text(candidate["cnic"])

            if isinstance(cnic_result, dict):

                # Fixed bug: manual_review instead of blurred
                cnic_manual_review = bool(
                    cnic_result.get("manual_review", False)
                )

                cnic_blurred = bool(
                    cnic_result.get("blurred", False)
                )

                cnic_blur_score = float(
                    cnic_result.get("blur_score", 0.0)
                )

        # -------------------------------------------------
        # Cleaning
        # -------------------------------------------------

        cleaned_resume_text = clean_text(resume_text)
        cleaned_cnic_name = clean_text(
            cnic_data.get("name", "")
        )
        cleaned_cnic_dob = clean_text(
            cnic_data.get("dob", "")
        )
        cleaned_cnic_number = clean_text(
            cnic_data.get("cnic", "")
        )

        # -------------------------------------------------
        # Candidate Record
        # -------------------------------------------------

        record = {
            "hash_id": hashlib.sha256(
                (
                    f"{job_category}|"
                    f"{candidate_id}|"
                    f"{cleaned_resume_text}"
                ).encode("utf-8")
            ).hexdigest(),

            "job_category": job_category,

            "candidate_id": candidate_id,

            "resume_text": cleaned_resume_text,

            "cnic_name": cleaned_cnic_name,

            "cnic_dob": cleaned_cnic_dob,

            "cnic_number": cleaned_cnic_number,

            "resume_manual_review": resume_manual_review,

            "cnic_manual_review": cnic_manual_review,

            "resume_blurred": resume_blurred,

            "cnic_blurred": cnic_blurred,

            "resume_blur_score": resume_blur_score,

            "cnic_blur_score": cnic_blur_score,
        }

        all_candidates.append(record)

    # -------------------------------------------------
    # Save Output
    # -------------------------------------------------

    with open(output_file_path, "w", encoding="utf-8") as output_file:

        json.dump(
            all_candidates,
            output_file,
            ensure_ascii=False,
            indent=2,
        )

    print("=" * 60)
    print(f"Processed {len(all_candidates)} candidates successfully.")
    print(f"Wrote {output_file_path}")
    print("=" * 60)

    return all_candidates


if __name__ == "__main__":

    ingest_resumes(
        input_path="jobs",
        output_path="output/all_candidates.json",
    )