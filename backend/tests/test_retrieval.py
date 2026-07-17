from backend.src.preprocessing.text_cleaner import TextCleaner

sample = """
Senior Python Backend Engineer with 8 years of experience.

Skills:
Python, FastAPI, Docker, PostgreSQL,
Redis, AWS, REST APIs.

• Built scalable systems.
• Optimized APIs.
"""

cleaned = TextCleaner.clean(sample)

print(cleaned)