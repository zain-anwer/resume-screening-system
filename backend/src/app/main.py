import json
from pathlib import Path
from extraction.text_normalization import normalize_ocr_text
from extraction.section_segregation import segregate_text
from extraction.parsers.header_parser import personal_info_parser

CURRENT_DIR = Path(__file__).resolve().parent
data_path = CURRENT_DIR.parent / 'extraction/all_candidates.json'

with open(data_path,'r',encoding='utf-8') as file:
    candidate_data = json.load(file) 


for entry in candidate_data:
    resume_json = {}
    cleaned_text = normalize_ocr_text(entry['resume_text'])
    segregated_text = segregate_text(cleaned_text)
    personal_info, urls = personal_info_parser(segregated_text['header'])
    resume_json['personal_info'] = personal_info
    resume_json['urls'] = urls
    print(resume_json)