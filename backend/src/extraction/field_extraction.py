# preprocessing imports
from src.extraction.utils.layout_reconstruction import reconstruct_resume_layout
from src.extraction.utils.section_segregation import segregate_text
from src.extraction.utils.text_normalization import normalize_ocr_text
from src.extraction.utils.personal_info_reconciliation import reconcile_personal_info

# parser imports
from src.extraction.parsers.certifications_parser import parse_certifications_section
from src.extraction.parsers.education_parser import parse_education_section
from src.extraction.parsers.experience_parser import parse_experience_section
from src.extraction.parsers.header_parser import parse_header_section
from src.extraction.parsers.projects_parser import parse_projects_section
from src.extraction.parsers.references_parser import parse_references
from src.extraction.parsers.skills_parser import parse_skills_section

# postprocessing import
from src.extraction.utils.experience_years_computation import get_total_experience_years

import json

def extract_fields(input_path : str, output_path : str):

    with open(input_path,'r',encoding='utf-8') as file:
        inputs = json.load(file)

    inputs = reconstruct_resume_layout(inputs)
    outputs = []


    for input in inputs:
        output = {}
        input['resume_text'] = normalize_ocr_text(input['resume_text'])
        segregated_text = segregate_text(input['resume_text'])
        personal_info, urls = parse_header_section(segregated_text['header'])

        # reconciliation layer on header section only
        personal_info, flags = reconcile_personal_info(personal_info,input)

        education = parse_education_section(segregated_text['education'])
        experience = parse_experience_section(segregated_text['experience'])
        skills = parse_skills_section(segregated_text['skills'])
        projects = parse_projects_section(segregated_text['projects'],skills)
        certifications = parse_certifications_section(segregated_text['certifications'])
        references = parse_references(segregated_text['references'])

        output['id']             = input['hash_id']
        output['personal_info']  = personal_info
        output['education']      = education
        output['experience']     = experience
        output['projects']       = projects
        output['skills']         = skills
        output['certifications'] = certifications
        output['achievements']   = []
        output['publications']   = []
        output['languages']      = []
        output['urls']           = urls
        output['summary']        = None
        output['total_experience_years'] = get_total_experience_years(experience)
        output['additional_sections'] = {}
        output['additional_sections']['references'] = references
        output['additional_sections']['interests']  = []
        output['flags']                             = flags
        output['metadata'] = {}
        output['metadata']['job_category']          = input['job_category']
    
        outputs.append(output)

    with open(output_path,'w',encoding='utf-8') as file:
        json.dump(outputs,file,indent=2)