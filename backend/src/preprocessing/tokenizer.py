from __future__ import annotations
from typing import List
from backend.src.preprocessing.text_cleaner import TextCleaner
class Tokenizer:
    STOP_WORDS={
        "a",
        "an",
        "the",
        "is",
        "are",
        "of",
        "to",
        "and",
        "for",
        "in",
        "on",
        "with",
        "at",
        "by",
    }
    @classmethod
    def tokenize(
        cls,text:str, remove_stopwords: bool = False,
    )->  List[str]:
         cleaned = TextCleaner.clean(text)

         import string

         tokens = [
    token.strip(string.punctuation)
    for token in cleaned.split()
]

         tokens = [token for token in tokens if token]

         if remove_stopwords:
            tokens = [
                token
                for token in tokens
                if token not in cls.STOP_WORDS
            ]

         return tokens