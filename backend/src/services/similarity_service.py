from __future__ import annotations
import numpy as np
class SimilarityService:
    @staticmethod
    def cosine_similarity(embedding1:np.ndarray,embedding2:np.ndarray)->float:
        if (embedding1.shape!=embedding2.shape):
            raise ValueError("Embedding dimensions do not match.")
        similarity=np.dot(embedding1,embedding2)
        return float(similarity)