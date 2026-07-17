#used for bm25, sentence transfoemers and semantic ranking
from __future__ import annotations
from backend.models.candidate import Candidate
from backend.models.job_description import JobDescription
class DocumentBuilder:
    @staticmethod
    def build_candidate(candidate: Candidate)->str:
        lines:list[str]=[]
        if candidate.experience:
            lines.append("Experience")

            for exp in candidate.experience:
                lines.append(exp.title)
                lines.append(exp.organization)

        lines.append(
            f"Total Experience {candidate.total_experience_years} Years"
        )
        if candidate.skills:
            lines.append("Skills")
            lines.extend(candidate.skills)
        if candidate.education:
            lines.append("Education")

            for edu in candidate.education:
                lines.append(edu.degree_raw)
                lines.append(edu.field)
                lines.append(edu.institution)
        if candidate.certifications:
            lines.append("Certifications")

            for cert in candidate.certifications:
                lines.append(cert.name)
        if candidate.resume_text:
            lines.append("Resume")
            lines.append(candidate.resume_text)

        return "\n".join(lines)
    
    @staticmethod
    def build_job(job:JobDescription)->str:
        lines: list[str] = []
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

        return "\n".join(lines)