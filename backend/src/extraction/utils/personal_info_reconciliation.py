from rapidfuzz import fuzz
from dateutil import parser


def dates_are_equal(date_1, date_2):
    try:
        return (parser.parse(date_1, fuzzy=True).date() == parser.parse(date_2, fuzzy=True).date())

    except (ValueError, TypeError, OverflowError):
        return False


def reconcile_personal_info(personal_info,input_dict):
    
    flags = {
        "missing_fields": [],
        "low_confidence_fields": [],
        "mismatched_fields": [],
        "ner_review_needed": False
    }

    if ((input_dict['cnic_number'] == None or input_dict['cnic_number'].strip() == '')
        and (input_dict['cnic_name'] == None or input_dict['cnic_name'].strip() == '')
        and (input_dict['cnic_dob'] == None or input_dict['cnic_dob'].strip() == '')):
        return personal_info, flags

    
    if personal_info['name']:
        if fuzz.ratio(personal_info['name'].lower(),input_dict['cnic_name'].lower()) < 80:
            personal_info['name'] = input_dict['cnic_name']
            print('ERROR: Name mismatch detected!')
            flags['low_confidence_fields'].append('name')
            flags['mismatched_fields'].append('name')
            flags['ner_review_needed'] = True
        else:
            personal_info['name'] = input_dict['cnic_name']
    else:
        personal_info['name'] = input_dict['cnic_name']

    if personal_info['cnic']:
        if personal_info['cnic'] != input_dict['cnic_number']:
            print('ERROR: CNIC number mismatch detected')
            flags['low_confidence_fields'].append('cnic')
            flags['mismatched_fields'].append('cnic')
            flags['ner_review_needed'] = True
    else:
        personal_info['cnic'] = input_dict['cnic_number']

    if personal_info['date_of_birth']:
        if not dates_are_equal(personal_info['date_of_birth'],input_dict['cnic_dob']):
            print('ERROR: date of birth mismatch detected')
            flags['low_confidence_fields'].append('date_of_birth')
            flags['mismatched_fields'].append('date_of_birth')
            flags['ner_review_needed'] = True
    else:
        personal_info['date_of_birth'] = input_dict['cnic_dob']

    if not personal_info['gender'] and personal_info['cnic']:
        last_digit = int(personal_info['cnic'][-1])
        personal_info['gender'] = 'Male' if last_digit % 2 else 'Female'

    # appending missing fields from personal information
    for key in personal_info.keys():
        if not personal_info[key]:
            flags['missing_fields'].append(key)

    return personal_info, flags