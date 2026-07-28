from src.extraction.field_extraction import extract_fields
from pathlib import Path

CURR_DIR = Path(__file__).resolve().parent
INPUT_PATH = CURR_DIR / 'ingestion_output.json'
OUTPUT_PATH = CURR_DIR / 'extraction_output.json'

extract_fields(INPUT_PATH,OUTPUT_PATH)