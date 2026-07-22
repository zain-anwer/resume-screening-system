import json
from pathlib import Path

from eligibility import load_rules, evaluate_candidate


# ----------------------------------------------------
# Paths
# ----------------------------------------------------

CURRENT_DIR = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_DIR.parents[2]

CANDIDATE_FOLDER = PROJECT_ROOT / "data" / "candidates"

CONFIG_FOLDER = PROJECT_ROOT / "configs"

OUTPUT_FILE = PROJECT_ROOT / "data" / "eligibility_results.json"


# ----------------------------------------------------
# Select YAML according to Job Category
# ----------------------------------------------------

def get_yaml_file(job_category):

    job = job_category.lower()

    mapping = {

        "manager_it": "manager_it.yaml",

        "worker_grade4": "worker_grade_4.yaml",

        "worker_grade_4": "worker_grade_4.yaml",

        "worker_grade_04": "worker_grade_4.yaml",

    }

    yaml_name = mapping.get(job)

    if yaml_name:

        return CONFIG_FOLDER / yaml_name

    return None

# ----------------------------------------------------
# Load all Candidate JSONs
# ----------------------------------------------------

candidate_files = list(CANDIDATE_FOLDER.glob("*.json"))

print("=" * 70)
print(f"Found {len(candidate_files)} Candidate JSON files")
print("=" * 70)

results = []


# ----------------------------------------------------
# Process Every Candidate
# ----------------------------------------------------

for file in candidate_files:

    with open(file, "r", encoding="utf-8") as f:

        candidate = json.load(f)

    job_category = candidate["metadata"]["job_category"]

    yaml_file = get_yaml_file(job_category)

    if yaml_file is None:

        print(f"\nSkipping {file.name}")

        print(f"No YAML found for {job_category}")

        continue

    rules = load_rules(yaml_file)

    result = evaluate_candidate(candidate, rules)

    results.append(result)

    print("\n" + "=" * 70)

    print(f"Candidate : {result['candidate_id']}")

    print(f"Job       : {result['job']}")

    print(f"Result    : {result['overall_status']}")

    print("-" * 70)

    print(

        f"Education      : {'PASS' if result['education']['status'] else 'FAIL'}"

    )

    print(

        f"Reason         : {result['education']['reason']}"

    )

    print()

    print(

        f"Experience     : {'PASS' if result['experience']['status'] else 'FAIL'}"

    )

    print(

        f"Reason         : {result['experience']['reason']}"

    )

    print()

    print(

        f"Supervisory    : {'PASS' if result['supervisory']['status'] else 'FAIL'}"

    )

    print(

        f"Reason         : {result['supervisory']['reason']}"

    )

    print()

    print(

        f"Age            : {'PASS' if result['age']['status'] else 'FAIL'}"

    )

    print(

        f"Candidate Age  : {result['age']['candidate_age']}"

    )

    print(

        f"Allowed Age    : {result['age']['allowed_age']}"

    )

    print(

        f"Reason         : {result['age']['reason']}"

    )

    print()

    if len(result["preferred_skills"]["matched"]) > 0:

        print("Preferred Skills Matched:")

        for skill in result["preferred_skills"]["matched"]:

            print(f"   - {skill}")

    else:

        print("Preferred Skills Matched : None")

    print("=" * 70)


# ----------------------------------------------------
# Save Results
# ----------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    json.dump(

        results,

        f,

        indent=4

    )

print()

print("=" * 70)
print("Eligibility checking completed.")
print(f"Results saved to:\n{OUTPUT_FILE}")
print("=" * 70)
