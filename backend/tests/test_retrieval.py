from src.retrieval.resume_ranking import rank_candidates
from pathlib import Path


CURR_DIR = Path(__file__).resolve().parent

JOB_DESCRIPTION = CURR_DIR.parent/"data/job_descriptions/it_engineer.txt"
INPUT_FILE = CURR_DIR.parent / "data" / "extraction_output.json"
OUTPUT_FILE = CURR_DIR / "ranking_output.json"

rank_candidates(
    JOB_DESCRIPTION_PATH=JOB_DESCRIPTION,
    INPUT_FILE_PATH=INPUT_FILE,         
    OUTPUT_FILE_PATH=OUTPUT_FILE,
    top_k=10
)

print("Ranking completed successfully.")
print(f"Results saved to: {OUTPUT_FILE}")