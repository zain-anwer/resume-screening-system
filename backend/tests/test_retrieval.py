from backend.src.services.embedding_service import EmbeddingService
from backend.src.services.similarity_service import SimilarityService

embedding_service = EmbeddingService()

text1 = """
Python Machine Learning Engineer
PyTorch
Transformers
LLMs
"""

text2 = """
AI Engineer
Python
Deep Learning
Transformers
"""

text3 = """
Flutter Developer
Dart
Firebase
Android
"""

embedding1 = embedding_service.encode(text1)
embedding2 = embedding_service.encode(text2)
embedding3 = embedding_service.encode(text3)

score1 = SimilarityService.cosine_similarity(
    embedding1,
    embedding2,
)

score2 = SimilarityService.cosine_similarity(
    embedding1,
    embedding3,
)

print("=" * 60)
print("Semantic Similarity")
print("=" * 60)

print()

print("AI vs AI")
print(score1)

print()

print("AI vs Flutter")
print(score2)