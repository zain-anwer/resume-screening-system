from src.policy_engine.candidate_evaluation import evaluate_candidates
from pathlib import Path

evaluate_candidates(
    input_path=Path("tests/extraction_output.json"),
    output_path=Path("tests/eligibility_results.json")
)