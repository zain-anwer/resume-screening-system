import re
import unicodedata


def clean_text(text):
    """
    Clean extracted resume text while preserving information.
    """

    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Convert Windows line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Normalize dashes
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove zero-width and invisible characters
    text = re.sub(r"[\u200b-\u200d\uFEFF]", "", text)

    # Remove multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove spaces before newline
    text = re.sub(r" +\n", "\n", text)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()