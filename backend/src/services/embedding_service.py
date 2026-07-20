from __future__ import annotations
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.configs.config import EMBEDDING_MODEL

logger=logging.getLogger(__name__)
class EmbeddingService:
   # MODEL_NAME = "all-MiniLM-L6-v2"
    #first load the embedding model
    def __init__(self)->None:
        logger.info(
            "Loading embedding model '%s'...",
            self.MODEL_NAME,)
        self.model = SentenceTransformer(
    EMBEDDING_MODEL
)
        logger.info(
            "Embedding model loaded successfully.")
    def encode(self,text:str,)->np.array:
        if not text.strip():
            raise ValueError(
                "Input text cannot be empty."
            )
        embedding=self.model.encode(text,convert_to_numpy=True,normalize_embeddings=True)
        return embedding
    def encode_batch(
        self,
        texts: list[str],
    ) -> np.ndarray:
        if not texts:
            raise ValueError(
                "Text list cannot be empty."
            )
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings
          