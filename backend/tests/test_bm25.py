import json
from pathlib import Path

from backend.src.adapters.candidate_adapter import CandidateAdapter
from backend.src.adapters.jd_adapter import JobDescriptionAdapter
from backend.src.preprocessing.document_builder import DocumentBuilder
from backend.src.services.bm25_engine import BM25Engine


candidate_docs = []

candidate_ids = []

candidate_folder = Path(
    "backend/data/candidates"
)

for file in sorted(candidate_folder.glob("*.json")):

    with open(file, encoding="utf-8") as f:
        raw = json.load(f)

    candidate = CandidateAdapter.adapt(raw)

    candidate_docs.append(
        DocumentBuilder.build_candidate(candidate)
    )

    candidate_ids.append(candidate.id)


job = JobDescriptionAdapter.adapt(
    "jd_001",
    "backend/data/job_descriptions/ai_engineer.txt",
)

query = DocumentBuilder.build_job(job)


engine = BM25Engine()
engine.fit(
    candidate_ids,
    candidate_docs,
)
results = engine.search(
    query,
    top_k=5,
)

print("=" * 60)

print("Top Candidates")

print("=" * 60)

for candidate_id, score in results:
    print(candidate_id, round(score, 3))