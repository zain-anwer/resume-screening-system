from backend.src.adapters.candidate_adapter import CandidateAdapter
from backend.src.adapters.jd_adapter import JobDescriptionAdapter
from backend.src.preprocessing.document_builder import DocumentBuilder
from backend.src.services.bm25_engine import BM25Engine
from backend.src.services.ranking_service import RankingService

import json
from pathlib import Path

# ----------------------------
# Load Job Description
# ----------------------------

job = JobDescriptionAdapter.adapt(
    job_id="jd_001",
    file_path="backend/data/job_descriptions/ai_engineer.txt",
)

# ----------------------------
# Load Candidates
# ----------------------------

candidates = []

candidate_dir = Path("backend/data/candidates")

for file in sorted(candidate_dir.glob("*.json")):

    with open(file, encoding="utf-8") as f:
        raw = json.load(f)

    candidates.append(
        CandidateAdapter.adapt(raw)
    )

# ----------------------------
# Build Candidate Documents
# ----------------------------

candidate_documents = [
    DocumentBuilder.build_candidate(c)
    for c in candidates
]

candidate_ids = [
    c.id
    for c in candidates
]

# ----------------------------
# BM25
# ----------------------------

engine = BM25Engine()

engine.fit(
    candidate_ids,
    candidate_documents,
)

job_document = DocumentBuilder.build_job(job)

bm25_results = engine.search(
    job_document,
    top_k=5,
)

# Convert ids back to Candidate objects
candidate_lookup = {
    c.id: c
    for c in candidates
}

retrieved = [
    (
        candidate_lookup[candidate_id],
        score,
    )
    for candidate_id, score in bm25_results
]

# ----------------------------
# Hybrid Ranking
# ----------------------------

ranking = RankingService()

results = ranking.rank(
    job,
    retrieved,
)

print("=" * 60)
print("Final Hybrid Ranking")
print("=" * 60)

for result in results:

    print()

    print(result.rank)
    print(result.candidate.id)
    print(result.candidate.experience[0].title)

    print(
        "Lexical:",
        round(result.lexical_score, 3),
    )

    print(
        "Semantic:",
        round(result.semantic_score, 3),
    )

    print(
        "Final:",
        round(result.final_score, 3),
    )

    print(
        "Matched Skills:",
        result.matched_skills,
    )

    print("-" * 40)