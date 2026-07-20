import json
from pathlib import Path

from backend.src.adapters.jd_adapter import JobDescriptionAdapter
from backend.src.services.retrieval_service import RetrievalService

# -----------------------------
# Build Retrieval Index
# -----------------------------

service = RetrievalService()

service.build_index(
    "backend/data/candidates"
)

# -----------------------------
# Load Job Description
# -----------------------------

job = JobDescriptionAdapter.adapt(
    job_id="jd_001",
    file_path="backend/data/job_descriptions/ai_engineer.txt",
)

# -----------------------------
# Retrieve Ranked Candidates
# -----------------------------

results = service.retrieve(
    job,
    top_k=5,
)

# -----------------------------
# Print Results
# -----------------------------

print("=" * 70)
print("TOP RANKED CANDIDATES")
print("=" * 70)

for candidate in results:

    print(f"\nRank: {candidate.rank}")
    print(f"Candidate ID: {candidate.candidate.id}")
    print(f"Name: {candidate.candidate.personal_info.name}")

    print(
        f"Current Role: "
        f"{candidate.candidate.experience[0].title}"
    )

    print(
        f"Experience: "
        f"{candidate.candidate.total_experience_years} years"
    )

    print(
        f"Skills: "
        f"{', '.join(candidate.candidate.skills)}"
    )

    print()

    print(
        f"Lexical Score : "
        f"{candidate.lexical_score:.3f}"
    )

    print(
        f"Semantic Score: "
        f"{candidate.semantic_score:.3f}"
    )

    print(
        f"Final Score   : "
        f"{candidate.final_score:.3f}"
    )

    print()

    print(
        "Matched Skills:"
    )

    if candidate.matched_skills:
        for skill in candidate.matched_skills:
            print(f"  ✓ {skill}")
    else:
        print("  None")

    print()

    print(
        "Missing Skills:"
    )

    if candidate.missing_skills:
        for skill in candidate.missing_skills:
            print(f"  ✗ {skill}")
    else:
        print("  None")

    print("\nResume Preview:")

    print(
        candidate.candidate.resume_text[:150]
        + "..."
    )

    print("-" * 70)