# preprocessing imports
from layout_reconstruction import reconstruct_resume_layout
from section_segregation import segregate_text
from text_normalization import normalize_ocr_text

# parser imports
from parsers.certifications_parser import parse_certifications_section
from parsers.education_parser import parse_education_section
from parsers.experience_parser import parse_experience_section
from parsers.header_parser import parse_header_section
from parsers.projects_parser import parse_projects_section
from parsers.references_parser import parse_references
from parsers.skills_parser import parse_skills_section

import json
from pathlib import Path

CURR_DIR = Path(__file__).resolve().parent

with open(CURR_DIR / 'all_candidates.json','r',encoding='utf-8') as file:
    inputs = json.load(file)

inputs = reconstruct_resume_layout(inputs)
outputs = []


for input in inputs:
    output = {}
    segregated_text = segregate_text(input['resume_text'])
    output['personal_info'], output['urls'] = parse_header_section(segregated_text['header'])
    output['eductaion'] = parse_education_section(segregated_text['education'])
    output['experience'] = parse_experience_section(segregated_text['experience'])
    output['skills'] = parse_skills_section(segregated_text['skills'])
    output['projects'] = parse_projects_section(segregated_text['projects'],output['skills'])
    output['certifications'] = parse_certifications_section(segregated_text['certifications'])
    output['references'] = parse_references(segregated_text['references'])
    outputs.append(output)

with open('extraction_output.json','w',encoding='utf-8') as file:
    json.dump(outputs,file,indent=4)