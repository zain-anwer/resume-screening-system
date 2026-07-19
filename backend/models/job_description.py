from dataclasses import dataclass, field


@dataclass(slots=True)
class JobDescription:
    """
    Standardized representation of a job description.
    """

    job_id: str

    title: str

    department: str

    location: str

    employment_type: str

    experience_required: str

    education_required: str

    required_skills: list[str] = field(default_factory=list)

    preferred_skills: list[str] = field(default_factory=list)

    responsibilities: list[str] = field(default_factory=list)

    qualifications: list[str] = field(default_factory=list)

    raw_text: str = ""