from src.ingestion.resume_ingestion import ingest_resumes
from pathlib import Path


CURR_DIR = Path(__file__).resolve().parent

INPUT_PATH = CURR_DIR.parent / 'jobs'
OUTPUT_PATH = CURR_DIR / 'ingestion_output.json'

ingest_resumes(INPUT_PATH,OUTPUT_PATH)