"""
candidate_adapter.py

Converts raw candidate JSON into the standardized Candidate model
used internally by Module 4.
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

    REQUIRED_FIELDS = [
        "id",
        "personal_info",
        "education",
        "experience",
        "skills",
    ]

    @classmethod
    def adapt(cls, raw_candidate: dict[str, Any]) -> Candidate:

        cls._validate(raw_candidate)

        candidate_id = raw_candidate["id"].strip()

        if not candidate_id:
            raise CandidateValidationError(
                "Candidate id cannot be empty."
            )

        return Candidate(
            id=candidate_id,

            personal_info=cls._build_personal_info(
                raw_candidate["personal_info"]
            ),

            education=[
                cls._build_education(item)
                for item in raw_candidate.get("education", [])
            ],

            experience=[
                cls._build_experience(item)
                for item in raw_candidate.get("experience", [])
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
                    []
                )
            ],

            urls=cls._build_urls(
                raw_candidate.get("urls")
            ),

            flags=cls._build_flags(
                raw_candidate.get("flags")
            ),

            resume_text=cls._build_resume_text(
                raw_candidate
            ),
        )

    @classmethod
    def _validate(cls, data: dict[str, Any]) -> None:

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
    def _build_personal_info(
        data: dict[str, Any],
    ) -> PersonalInfo:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "personal_info must be an object."
            )

        phones = data.get("phone") or []

        phone = (
            phones[0]
            if isinstance(phones, list) and phones
            else ""
        )

        return PersonalInfo(
            name=data.get("name") or "",
            email=data.get("email") or "",
            phone=phone,
            cnic=data.get("cnic") or "",
            location=data.get("location") or "",
        )

    @staticmethod
    def _build_education(
        data: dict[str, Any],
    ) -> Education:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Each education entry must be an object."
            )

        try:
            graduation_year = int(
                data.get("end_year") or 0
            )
        except (TypeError, ValueError):
            graduation_year = 0

        return Education(
            degree_raw=data.get("degree") or "",
            degree_level="",
            field="",
            institution=data.get("institute") or "",
            graduation_year=graduation_year,
            is_current=False,
            cgpa=data.get("cgpa"),
        )

    @staticmethod
    def _build_experience(
        data: dict[str, Any],
    ) -> Experience:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Each experience entry must be an object."
            )

        return Experience(
            title=data.get("job_title") or "",
            organization=data.get("organization") or "",
            start_date=data.get("start_date") or "",
            end_date=data.get("end_date"),
            is_current=(
                str(data.get("end_date", "")).lower()
                == "present"
            ),
            duration_months=0,
        )

    @staticmethod
    def _build_certification(
        data: dict[str, Any],
    ) -> Certification:

        if not isinstance(data, dict):
            raise CandidateValidationError(
                "Each certification entry must be an object."
            )

        return Certification(
            name=data.get("name") or "",
            year=0,
        )

    @staticmethod
    def _build_urls(
        data: dict[str, Any] | None,
    ) -> URLs:

        if not isinstance(data, dict):
            data = {}

        return URLs(
            github=data.get("github") or "",
            linkedin=data.get("linkedin") or "",
            portfolio=list(
                data.get("portfolio", [])
            ),
        )

    @staticmethod
    def _build_flags(
        data: dict[str, Any] | None,
    ) -> Flags:

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

    @staticmethod
    def _build_resume_text(
        data: dict[str, Any],
    ) -> str:

        parts: list[str] = []

        if data.get("summary"):
            parts.append(data["summary"])

        parts.extend(data.get("skills", []))

        for exp in data.get("experience", []):
            parts.append(exp.get("job_title", ""))
            parts.append(exp.get("organization", ""))
            parts.append(exp.get("description", ""))

        for edu in data.get("education", []):
            parts.append(edu.get("degree", ""))
            parts.append(edu.get("institute", ""))

        for cert in data.get("certifications", []):
            parts.append(cert.get("name", ""))

        for project in data.get("projects", []):
            parts.append(project.get("name", ""))
            parts.append(project.get("description", ""))

            technologies = project.get(
                "technologies",
                [],
            )

            if technologies:
                parts.extend(technologies)

        return " ".join(
            str(item).strip()
            for item in parts
            if item
        )