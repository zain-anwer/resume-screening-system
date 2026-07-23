from pathlib import Path
import json

from backend.src.retrieval.resume_ranking import rank_candidates

CURR_DIR = Path(__file__).resolve().parent

JOB_DESCRIPTION = (
    CURR_DIR.parent
    / "data"
    / "job_descriptions"
    / "it_engineer.txt"
)

CANDIDATES = (
    CURR_DIR.parent
    / "data"
    / "extraction_output.json"
)

OUTPUT_FILE = (
    CURR_DIR
    / "ranking_output.json"
)

with open(CANDIDATES, "r", encoding="utf-8") as f:
    candidates_json = json.load(f)

results = rank_candidates(
    job_description_path=str(JOB_DESCRIPTION),
    candidates_json=candidates_json,
    top_k=5,
)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("Ranking completed successfully.")
print(f"Results saved to: {OUTPUT_FILE}")