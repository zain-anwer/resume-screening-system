from __future__ import annotations
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from configs.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates semantic embeddings using a SentenceTransformer model.
    """

    def __init__(self) -> None:
        logger.info(
            "Loading embedding model '%s'...",
            EMBEDDING_MODEL,
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        logger.info(
            "Embedding model loaded successfully."
        )

    def encode(
        self,
        text: str,
    ) -> np.ndarray:

        if not text.strip():
            raise ValueError(
                "Input text cannot be empty."
            )

        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    def encode_batch(
        self,
        texts: list[str],
    ) -> np.ndarray:

        if not texts:
            raise ValueError(
                "Text list cannot be empty."
            )

        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )