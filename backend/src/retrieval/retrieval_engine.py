from __future__ import annotations
import json
import logging
from pathlib import Path

from models.candidate import Candidate
from models.job_description import JobDescription
from src.adapters.candidate_adapter import CandidateAdapter
from src.preprocessing.document_builder import DocumentBuilder
from src.retrieval.bm25_engine import BM25Engine
from src.retrieval.ranking_engine import RankingService
from models.ranked_candidate import RankedCandidate


logger=logging.getLogger(__name__)
class RetrievalService:
    def __init__(self)->None:
        self.engine = BM25Engine()
        self.ranking_service = RankingService()
        self.candidates: dict[str, Candidate] = {}
    def build_index(self,candidate_file: str| Path)->None:
        candidate_file = Path(candidate_file)
        with open(candidate_file, encoding="utf-8") as f:
           raw_candidates = json.load(f)
        if not isinstance(raw_candidates, list):
             raise ValueError(
        "Candidates file must contain a JSON array."
    )
        candidate_ids: list[str] = []
        candidate_documents: list[str] = []
        for raw in raw_candidates:

             candidate = CandidateAdapter.adapt(raw)

             self.candidates[candidate.id] = candidate

             candidate_ids.append(candidate.id)

             candidate_documents.append(
        DocumentBuilder.build_candidate(candidate)
    )
        self.engine.fit(
            candidate_ids,
            candidate_documents,
        )
        logger.info(
            "Indexed %d candidates.",
            len(candidate_ids),
        )
    def build_index_from_json(
    self,
    candidates_json: list[dict],
) -> None:
        if not isinstance(candidates_json, list):
         raise ValueError(
            "Candidates must be provided as a list of JSON objects."
        )
        candidate_ids: list[str] = []
        candidate_documents: list[str] = []
        for raw in candidates_json:
                     #if raw.get("overall_status") != "Eligible":
                      #  continue
                     candidate = CandidateAdapter.adapt(raw)
        
                     self.candidates[candidate.id] = candidate
        
                     candidate_ids.append(candidate.id)
        
                     candidate_documents.append(
                DocumentBuilder.build_candidate(candidate)
            )
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
