"""
jd_adapter.py

Reads a job description text file and converts it into the
standardized JobDescription model.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from models.job_description import JobDescription
from src.exceptions.validation import JobDescriptionValidationError

logger = logging.getLogger(__name__)


class JobDescriptionAdapter:
    """
    Converts raw job description text into a standardized
    JobDescription model.
    """

    SECTION_HEADERS = {
        "company": None,
        "department": "department",
        "location": "location",
        "employment type": "employment_type",
        "experience required": "experience_required",
        "education required": "education_required",
        "required skills": "required_skills",
        "preferred": "preferred_skills",
        "preferred skills": "preferred_skills",
        "responsibilities": "responsibilities",
        "qualifications": "qualifications",
    }

    @classmethod
    def adapt(
        cls,
        job_id: str,
        file_path: str | Path,
    ) -> JobDescription:
        """
        Read and parse a job description text file.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise JobDescriptionValidationError(
                f"Job description not found: {file_path}"
            )

        raw_text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not raw_text:
            raise JobDescriptionValidationError(
                "Job description is empty."
            )

        logger.info(
            "Parsing job description '%s'",
            job_id,
        )

        return cls._parse(
            job_id,
            raw_text,
        )

    @classmethod
    def _parse(
        cls,
        job_id: str,
        raw_text: str,
    ) -> JobDescription:
        """
        Convert raw text into a JobDescription object.
        """

        lines = [
            line.strip()
            for line in raw_text.splitlines()
            if line.strip()
        ]

        if not lines:
            raise JobDescriptionValidationError(
                "Invalid job description."
            )

        # -----------------------
        # Parse title
        # -----------------------

        title = lines[0]

        if ":" in title:
            key, value = title.split(":", 1)

            if key.strip().lower() == "job title":
                title = value.strip()

        # -----------------------
        # Initialize storage
        # -----------------------

        data = {
            "department": "",
            "location": "",
            "employment_type": "",
            "experience_required": "",
            "education_required": "",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
        }

        current_section = None

        # -----------------------
        # Parse remaining lines
        # -----------------------

        for line in lines[1:]:

            # Handle inline fields like:
            # Experience Required: 5 Years

            if ":" in line:

                key, value = line.split(":", 1)

                normalized = key.strip().lower()

                if normalized in cls.SECTION_HEADERS:

                    current_section = cls.SECTION_HEADERS[
                        normalized
                    ]

                    if current_section is None:
                        continue

                    if isinstance(
                        data[current_section],
                        list,
                    ):
                        if value.strip():
                            data[current_section].append(
                                value.strip()
                            )
                    else:
                        data[current_section] = (
                            value.strip()
                        )

                    continue

            normalized = re.sub(r"^#+\s*", "", line.lower())
            normalized = normalized.rstrip(":").strip()

            if normalized in cls.SECTION_HEADERS:

                current_section = cls.SECTION_HEADERS[
                    normalized
                ]

                continue

            if current_section is None:
                continue

            if current_section in {
                "required_skills",
                "preferred_skills",
                "responsibilities",
                "qualifications",
            }:

                item = re.sub(
                    r"^[•*\-]\s*",
                    "",
                    line,
                ).strip()

                if item:
                    data[current_section].append(item)

            else:
                data[current_section] = line.strip()
        print(data)
        job = JobDescription(
            job_id=job_id,
            title=title,
            department=data["department"],
            location=data["location"],
            employment_type=data["employment_type"],
            experience_required=data[
                "experience_required"
            ],
            education_required=data[
                "education_required"
            ],
            required_skills=sorted(
                set(data["required_skills"])
            ),
            preferred_skills=sorted(
                set(data["preferred_skills"])
            ),
            responsibilities=data[
                "responsibilities"
            ],
            qualifications=data[
                "qualifications"
            ],
            raw_text=" ".join(raw_text.split()),
        )

        logger.info(
            "Successfully parsed '%s'",
            job.job_id,
        )

        return job