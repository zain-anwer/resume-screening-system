from backend.src.preprocessing.tokenizer import Tokenizer


def main():
    sample = """
    Senior Python Backend Engineer with 8 years of experience.

    Skills:
    Python, FastAPI, Docker, PostgreSQL,
    Redis, AWS, REST APIs.
    """

    print("=" * 50)
    print("Without Stopword Removal")
    print("=" * 50)

    tokens = Tokenizer.tokenize(sample)

    print(tokens)

    print("\n" + "=" * 50)
    print("With Stopword Removal")
    print("=" * 50)

    filtered = Tokenizer.tokenize(
        sample,
        remove_stopwords=True,
    )

    print(filtered)

    # Assertions
    assert "python" in tokens
    assert "fastapi" in tokens
    assert "postgresql" in tokens

    assert "with" not in filtered
    assert "the" not in filtered

    print("\n✅ Tokenizer test passed.")


if __name__ == "__main__":
    main()