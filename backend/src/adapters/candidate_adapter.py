"""
candidate_adapter.py

Converts raw candidate JSON into the standardized Candidate model
used internally by Module 4.

Responsibilities
----------------
- Validate incoming JSON
- Normalize optional fields
- Convert dictionaries into domain models
- Raise meaningful validation exceptions
"""

from __future__ import annotations

import logging
from typing import Any

from backend.models.candidate import (
    Candidate,
    Certification,
    Education,
    Experience,
    Flags,
    PersonalInfo,
    URLs,
)
from backend.src.exceptions.validation import CandidateValidationError

logger = logging.getLogger(__name__)


class CandidateAdapter:
    """
    Converts raw candidate JSON into the internal Candidate model.
    """

    REQUIRED_FIELDS = [
        "id",
        "personal_info",
        "education",
        "experience",
        "skills",
        "resume_text",
    ]

    @classmethod
    def adapt(cls, raw_candidate: dict[str, Any]) -> Candidate:
        """
        Convert raw candidate JSON into a Candidate object.
        """

        cls._validate(raw_candidate)

        candidate_id = raw_candidate["id"].strip()

        if not candidate_id:
            raise CandidateValidationError(
                "Candidate id cannot be empty."
            )

        logger.debug(
            "Adapting candidate '%s'",
            candidate_id,
        )

        candidate = Candidate(
            id=candidate_id,

            personal_info=cls._build_personal_info(
                raw_candidate["personal_info"]
            ),

            education=[
                cls._build_education(item)
                for item in raw_candidate["education"]
            ],

            experience=[
                cls._build_experience(item)
                for item in raw_candidate["experience"]
            ],

            total_experience_years=float(
                raw_candidate.get(
                    "total_experience_years",
                    0,
                )
            ),

            skills=sorted(
                {
                    skill.strip().lower()
                    for skill in raw_candidate.get("skills", [])
                    if isinstance(skill, str)
                    and skill.strip()
                }
            ),

            certifications=[
                cls._build_certification(item)
                for item in raw_candidate.get(
                    "certifications",
                    [],
                )
            ],

            urls=cls._build_urls(
                raw_candidate.get("urls", {})
            ),

            flags=cls._build_flags(
                raw_candidate.get("flags", {})
            ),

            resume_text=" ".join(
                raw_candidate.get(
                    "resume_text",
                    "",
                ).split()
            ),
        )

        logger.debug(
            "Successfully adapted candidate '%s'",
            candidate.id,
        )

        return candidate

    @classmethod
    def _validate(cls, data: dict[str, Any]) -> None:
        """
        Validate the incoming candidate JSON.
        """

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Candidate must be a JSON object."
            )

        missing = [
            field
            for field in cls.REQUIRED_FIELDS
            if field not in data
        ]

        if missing:
            raise CandidateValidationError(
                f"Missing required fields: {missing}"
            )

        if not isinstance(data["education"], list):
            raise CandidateValidationError(
                "education must be a list."
            )

        if not isinstance(data["experience"], list):
            raise CandidateValidationError(
                "experience must be a list."
            )

        if not isinstance(data["skills"], list):
            raise CandidateValidationError(
                "skills must be a list."
            )

    @staticmethod
    def _build_personal_info(data: dict[str, Any]) -> PersonalInfo:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "personal_info must be an object."
            )

        return PersonalInfo(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            cnic=data.get("cnic", ""),
            location=data.get("location", ""),
        )

    @staticmethod
    def _build_education(data: dict[str, Any]) -> Education:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Each education entry must be an object."
            )

        try:
            graduation_year = int(
                data.get("graduation_year", 0)
            )
        except (TypeError, ValueError):
            raise CandidateValidationError(
                "graduation_year must be an integer."
            )

        return Education(
            degree_raw=data.get("degree_raw", ""),
            degree_level=data.get("degree_level", ""),
            field=data.get("field", ""),
            institution=data.get("institution", ""),
            graduation_year=graduation_year,
            is_current=bool(
                data.get("is_current", False)
            ),
            cgpa=data.get("cgpa"),
        )

    @staticmethod
    def _build_experience(data: dict[str, Any]) -> Experience:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Each experience entry must be an object."
            )

        try:
            duration = int(
                data.get("duration_months", 0)
            )
        except (TypeError, ValueError):
            raise CandidateValidationError(
                "duration_months must be an integer."
            )

        return Experience(
            title=data.get("title", ""),
            organization=data.get("organization", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date"),
            is_current=bool(
                data.get("is_current", False)
            ),
            duration_months=duration,
        )

    @staticmethod
    def _build_certification(data: dict[str, Any]) -> Certification:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Each certification entry must be an object."
            )

        try:
            year = int(
                data.get("year", 0)
            )
        except (TypeError, ValueError):
            raise CandidateValidationError(
                "Certification year must be an integer."
            )

        return Certification(
            name=data.get("name", ""),
            year=year,
        )

    @staticmethod
    def _build_urls(data: dict[str, Any]) -> URLs:

        if not isinstance(data, dict):
            data = {}

        return URLs(
            github=data.get("github", ""),
            linkedin=data.get("linkedin", ""),
            portfolio=list(
                data.get("portfolio", [])
            ),
        )

    @staticmethod
    def _build_flags(data: dict[str, Any]) -> Flags:

        if not isinstance(data, dict):
            data = {}

        return Flags(
            missing_fields=list(
                data.get("missing_fields", [])
            ),
            low_confidence_fields=list(
                data.get(
                    "low_confidence_fields",
                    [],
                )
            ),
            ner_review_needed=bool(
                data.get(
                    "ner_review_needed",
                    False,
                )
            ),
        )