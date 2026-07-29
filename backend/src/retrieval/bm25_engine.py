"""
bm25_engine.py

Lexical retrieval engine using the BM25 algorithm.

Responsibilities
----------------
- Build a BM25 index from candidate documents.
- Perform fast keyword-based retrieval.
- Return the Top-K candidate IDs with BM25 scores.
"""

from __future__ import annotations

import logging

from rank_bm25 import BM25Okapi

from src.preprocessing.tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class BM25Engine:
    """
    BM25 lexical retrieval engine.

    This class indexes candidate documents and performs
    keyword-based retrieval using the BM25 ranking algorithm.
    """

    def __init__(self) -> None:
        """
        Initialize an empty BM25 engine.
        """

        self.candidate_ids: list[str] = []
        self.documents: list[str] = []
        self.tokenized_documents: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    def fit(
        self,
        candidate_ids: list[str],
        candidate_documents: list[str],
    ) -> None:
        """
        Build the BM25 index.

        Args:
            candidate_ids:
                List of candidate IDs.

            candidate_documents:
                List of candidate documents.
        """

        if not candidate_documents:
            raise ValueError(
                "Candidate document list cannot be empty."
            )

        if len(candidate_ids) != len(candidate_documents):
            raise ValueError(
                "candidate_ids and candidate_documents "
                "must have the same length."
            )

        logger.info(
            "Building BM25 index for %d candidates.",
            len(candidate_documents),
        )

        self.candidate_ids = candidate_ids
        self.documents = candidate_documents

        self.tokenized_documents = [
            Tokenizer.tokenize(document)
            for document in candidate_documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )

        logger.info(
            "BM25 index built successfully."
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """
        Search the BM25 index.

        Args:
            query:
                Job description document.

            top_k:
                Number of candidates to return.

        Returns:
            List of tuples:

            [
                ("candidate_001", 18.42),
                ("candidate_009", 15.73),
                ...
            ]
        """

        if self.bm25 is None:
            raise RuntimeError(
                "BM25 index has not been built."
            )

        query_tokens = Tokenizer.tokenize(query)

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_results = sorted(
            zip(
                self.candidate_ids,
                scores,
            ),
            key=lambda item: item[1],
            reverse=True,
        )

        logger.info(
            "Retrieved top %d candidates.",
            top_k,
        )

        return ranked_results[:top_k]