from __future__ import annotations
import json
import logging
from pathlib import Path

from backend.models.candidate import Candidate
from backend.models.job_description import JobDescription
from backend.src.adapters.candidate_adapter import CandidateAdapter
from backend.src.preprocessing.document_builder import DocumentBuilder
from backend.src.services.bm25_engine import BM25Engine
from backend.src.services.ranking_engine import RankingService
from backend.models.ranked_candidate import RankedCandidate


logger=logging.getLogger(__name__)
class RetrievalService:
    def __init__(self)->None:
        self.engine = BM25Engine()
        self.ranking_service = RankingService()
        self.candidates: dict[str, Candidate] = {}
    def build_index(self,candidate_folder: str| Path)->None:
        candidate_folder=Path(candidate_folder)
        candidate_ids: list[str] = []
        candidate_documents: list[str] = []
        for file in sorted(candidate_folder.glob("*.json")):
            with open(file,encoding="utf-8") as f:
                raw=json.load(f)
            candidate = CandidateAdapter.adapt(raw)  
            self.candidates[candidate.id] = candidate
            candidate_ids.append(candidate.id)
            candidate_documents.append(
                DocumentBuilder.build_candidate(candidate))
        self.engine.fit(
            candidate_ids,
            candidate_documents,
        )
        logger.info(
            "Indexed %d candidates.",
            len(candidate_ids),
        )
    def retrieve(
        self,
        job: JobDescription,
        top_k: int = 10,
    ) ->  list[RankedCandidate]:
        job_document = DocumentBuilder.build_job(job)
        results = self.engine.search(
            job_document,
            top_k,
        )
        retrieved = []
        for candidate_id, score in results:
           retrieved.append(
        (
            self.candidates[candidate_id],
            score,
        )
    )

        return self.ranking_service.rank(
    job,
    retrieved,
)
