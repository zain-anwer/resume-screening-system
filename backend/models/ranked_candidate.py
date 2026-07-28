from dataclasses import dataclass, field
from typing import List

from models.candidate import Candidate


@dataclass(slots=True)
class RankedCandidate:
    """
    Represents a ranked candidate after the scoring pipeline.
    """

    candidate: Candidate

    lexical_score: float

    semantic_score: float

    final_score: float

    rank: int = 0

    matched_skills: List[str] = field(default_factory=list)

    missing_skills: List[str] = field(default_factory=list)

    matched_preferred_skills: List[str] = field(default_factory=list)

    score_breakdown: dict = field(default_factory=dict)