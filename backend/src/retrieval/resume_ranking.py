from __future__ import annotations
import json

from models.ranked_candidate import RankedCandidate
from src.adapters.jd_adapter import JobDescriptionAdapter
from src.retrieval.retrieval_engine import RetrievalService



def rank_candidates(JOB_DESCRIPTION_PATH: str, INPUT_FILE_PATH: str, OUTPUT_FILE_PATH : str, top_k: int = 10) -> list[RankedCandidate]:

    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        candidates_json = json.load(f)

    service = RetrievalService()

    # Build BM25 index from Module 3 JSON
    service.build_index_from_json(candidates_json)

    # Parse the job description
    job = JobDescriptionAdapter.adapt(
        job_id="job_001",
        file_path=JOB_DESCRIPTION_PATH,
    )

    # Retrieve and rank candidates
    results = service.retrieve(
        job,
        top_k,
    )
    response = []

    for candidate in results:
     response.append(
        {
            "rank": candidate.rank,
            "candidate_id": candidate.candidate.id,
            "candidate_name": candidate.candidate.personal_info.name,
            "job_title": candidate.candidate.experience[0].title
            if candidate.candidate.experience
            else "",
            "lexical_score": round(candidate.lexical_score, 3),
            "semantic_score": round(candidate.semantic_score, 3),
            "final_score": round(candidate.final_score, 3),
            "matched_skills": candidate.matched_skills,
            "missing_skills": candidate.missing_skills,
            "matched_preferred_skills": candidate.matched_preferred_skills,
        }
    )

    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4)