from pathlib import Path
import json

from backend.src.adapters.candidate_adapter import CandidateAdapter
from backend.src.adapters.jd_adapter import JobDescriptionAdapter
from backend.src.preprocessing.document_builder import DocumentBuilder


# Candidate

with open(
    "backend/data/candidates/candidate_001.json",
    encoding="utf-8",
) as f:
    raw = json.load(f)

candidate = CandidateAdapter.adapt(raw)

print("=" * 60)
print("Candidate Document")
print("=" * 60)

print(DocumentBuilder.build_candidate(candidate))


# Job

job = JobDescriptionAdapter.adapt(
    "jd_001",
    "backend/data/job_descriptions/ai_engineer.txt",
)

print("\n" + "=" * 60)
print("Job Document")
print("=" * 60)

print(DocumentBuilder.build_job(job))