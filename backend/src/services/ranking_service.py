from __future__ import annotations
from backend.models.candidate import Candidate
from backend.models.job_description import JobDescription
from backend.models.ranked_candidate import RankedCandidate
from backend.src.preprocessing.document_builder import DocumentBuilder
from backend.src.services.embedding_service import EmbeddingService
from backend.src.services.similarity_service import SimilarityService
class RankingService:
    from backend.configs.config import (
    LEXICAL_WEIGHT,
    SEMANTIC_WEIGHT,
)
    def __init__(self):
        self.embedding_service=EmbeddingService()
    def rank(self,job:JobDescription,bm25_results: list[tuple[Candidate, float]])->list[RankedCandidate]:
        if not bm25_results:
            return []
        job_document=DocumentBuilder.build_job(job)
        job_embedding=self.embedding_service.encode(job_document)
        bm25_scores = [score for _, score in bm25_results]
        normalized_scores=self.normalize_scores(bm25_scores)
        ranked_candidates=[]
        for (candidate,lexical_score), normalized_score in zip (bm25_results,normalized_scores,):
            candidate_document=DocumentBuilder.build_candidate(candidate)
            candidate_embedding=self.embedding_service.encode(candidate_document)
            semantic_score=(SimilarityService.cosine_similarity(job_embedding,candidate_embedding))
            final_score=(self.LEXICAL_WEIGHT*normalized_score+self.SEMANTIC_WEIGHT*semantic_score)
            candidate_skills=set(candidate.skills)
            required_skills=set(skill.lower() for skill in job.required_skills)
            prefferd_skills=set(skill.lower() for skill in job.preferred_skills)
            matched_skills=sorted(candidate_skills & required_skills)
            missing_skills=sorted(required_skills-candidate_skills)
            matched_preffered=sorted(candidate_skills & prefferd_skills)
            ranked_candidates.append(RankedCandidate(candidate=candidate,lexical_score=lexical_score,semantic_score=semantic_score,final_score=final_score,
                                                    matched_skills=matched_skills,missing_skills=missing_skills,matched_preferred_skills=matched_preffered,  score_breakdown={
                        "raw_bm25": lexical_score,
                        "normalized_bm25": normalized_score,
                        "semantic_similarity": semantic_score,
                        "lexical_weight": self.LEXICAL_WEIGHT,
                        "semantic_weight": self.SEMANTIC_WEIGHT,
                    },))
        ranked_candidates.sort(key=lambda x:x.final_score,reverse=True)
        for rank,candidate in enumerate(ranked_candidates,start=1):
            candidate.rank=rank
        return ranked_candidates
    @staticmethod
    def normalize_scores(scores:list[float])->list[float]:
        if not scores:
            return []
        minimum = min(scores)
        maximum = max(scores)
        if maximum == minimum:
            return [1.0] * len(scores)
        return [
            (score - minimum) / (maximum - minimum)
            for score in scores
        ]