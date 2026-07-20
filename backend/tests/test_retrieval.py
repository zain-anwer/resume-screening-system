from backend.src.services.embedding_service import EmbeddingService

service = EmbeddingService()

text = """
AI Engineer with experience in Python,
PyTorch, Transformers and Machine Learning.
"""

embedding = service.encode(text)

print("=" * 60)
print("Embedding")
print("=" * 60)

print(type(embedding))
print()

print("Shape:", embedding.shape)
print()

print("First 10 values:")

print(embedding[:10])