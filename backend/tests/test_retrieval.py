from backend.src.adapters.jd_adapter import JobDescriptionAdapter
from backend.src.services.retrieval_service import RetrievalService


service = RetrievalService()

service.build_index(
    "backend/data/candidates"
)

job = JobDescriptionAdapter.adapt(
    "jd_001",
    "backend/data/job_descriptions/ai_engineer.txt",
)

results = service.retrieve(
    job,
    top_k=5,
)

print("=" * 60)
print("Top Candidates")
print("=" * 60)

for candidate in results:

    print(candidate.id)

    print(candidate.experience[0].title)

    print(candidate.skills)

    print("-" * 40)