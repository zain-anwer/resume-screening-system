"""
Builds text documents used by BM25 and Semantic Retrieval.
"""

from __future__ import annotations

from models.candidate import Candidate
from models.job_description import JobDescription


class DocumentBuilder:

    @staticmethod
    def build_candidate(candidate: Candidate) -> str:
        lines: list[str] = []

        # Personal Information
        if candidate.personal_info.name:
            lines.append(candidate.personal_info.name)

        if candidate.personal_info.location:
            lines.append(candidate.personal_info.location)

        # Experience
        if candidate.experience:
            lines.append("Experience")

            for exp in candidate.experience:

                if exp.title:
                    lines.append(exp.title)

                if exp.organization:
                    lines.append(exp.organization)

        # Total Experience
        lines.append(
            f"Total Experience {candidate.total_experience_years} Years"
        )

        # Skills
        if candidate.skills:
            lines.append("Skills")
            lines.extend(candidate.skills)

        # Education
        if candidate.education:
            lines.append("Education")

            for edu in candidate.education:

                if edu.degree_raw:
                    lines.append(edu.degree_raw)

                if edu.institution:
                    lines.append(edu.institution)

        # Certifications
        if candidate.certifications:
            lines.append("Certifications")

            for cert in candidate.certifications:

                if cert.name:
                    lines.append(cert.name)

        # Resume Text
        if candidate.resume_text:
            lines.append("Resume")
            lines.append(candidate.resume_text)

        return "\n".join(
            str(item)
            for item in lines
            if item
        )

    @staticmethod
    def build_job(job: JobDescription) -> str:

        lines: list[str] = []

        if job.title:
            lines.append(job.title)

        if job.experience_required:
            lines.append("Experience Required")
            lines.append(job.experience_required)

        if job.required_skills:
            lines.append("Required Skills")
            lines.extend(job.required_skills)

        if job.preferred_skills:
            lines.append("Preferred Skills")
            lines.extend(job.preferred_skills)

        if job.qualifications:
            lines.append("Qualifications")
            lines.extend(job.qualifications)

        if job.responsibilities:
            lines.append("Responsibilities")
            lines.extend(job.responsibilities)

        return "\n".join(
            str(item)
            for item in lines
            if item
        )