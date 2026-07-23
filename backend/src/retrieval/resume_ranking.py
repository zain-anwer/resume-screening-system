from __future__ import annotations

from backend.models.ranked_candidate import RankedCandidate
from backend.src.adapters.jd_adapter import JobDescriptionAdapter
from backend.src.retrieval.retrieval_engine import RetrievalService


def rank_candidates(
    job_description_path: str,
    candidates_json: list[dict],
    top_k: int = 10,
) -> list[RankedCandidate]:
    """
    Public entry point for Module 4.

    Args:
        job_description_path: Path to the job description (.txt)
        candidates_json: List of candidate JSON objects received from Module 3
        top_k: Number of top candidates to return

    Returns:
        List of ranked candidates.
    """

    service = RetrievalService()

    # Build BM25 index from Module 3 JSON
    service.build_index_from_json(candidates_json)

    # Parse the job description
    job = JobDescriptionAdapter.adapt(
        job_id="job_001",
        file_path=job_description_path,
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

    return response