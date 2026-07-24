import json
from pathlib import Path

from src.policy_engine.eligibility import load_rules, evaluate_candidate


# ----------------------------------------------------
# Select YAML according to Job Category
# ----------------------------------------------------

def get_yaml_file(job_category, config_folder):
    job = job_category.lower()

    mapping = {
        "manager_it": "manager_it.yaml",
        "worker_grade4": "worker_grade_4.yaml",
        "worker_grade_4": "worker_grade_4.yaml",
        "worker_grade_04": "worker_grade_4.yaml",
    }

    yaml_name = mapping.get(job)

    if yaml_name:
        return config_folder / yaml_name

    return None


# ----------------------------------------------------
# Eligibility Evaluation Wrapper
# ----------------------------------------------------

def evaluate_candidates(input_path, output_path):
    """
    Load candidates from a JSON file, evaluate their eligibility
    using job-specific YAML rules, and save the results to another
    JSON file.

    Parameters
    ----------
    input_path : str | Path
        Path to the input JSON file containing extracted candidates.

    output_path : str | Path
        Path where the eligibility results JSON file should be saved.

    Returns
    -------
    list
        A list containing the eligibility evaluation results.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    # Configuration folder relative to this module
    current_dir = Path(__file__).resolve()
    project_root = current_dir.parents[2]
    config_folder = project_root / "configs"

    # ------------------------------------------------
    # Load Candidates
    # ------------------------------------------------

    with open(input_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    print("=" * 70)
    print(f"Found {len(candidates)} Candidates")
    print("=" * 70)

    results = []

    # ------------------------------------------------
    # Process Every Candidate
    # ------------------------------------------------

    for candidate in candidates:

        job_category = candidate["metadata"]["job_category"]

        yaml_file = get_yaml_file(
            job_category,
            config_folder
        )

        if yaml_file is None:

            print(
                f"\nSkipping Candidate: "
                f"{candidate['metadata']['candidate_id']}"
            )

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
            f"Education      : "
            f"{'PASS' if result['education']['status'] else 'FAIL'}"
        )
        print(f"Reason         : {result['education']['reason']}")

        print()

        print(
            f"Experience     : "
            f"{'PASS' if result['experience']['status'] else 'FAIL'}"
        )
        print(f"Reason         : {result['experience']['reason']}")

        print()

        print(
            f"Supervisory    : "
            f"{'PASS' if result['supervisory']['status'] else 'FAIL'}"
        )
        print(f"Reason         : {result['supervisory']['reason']}")

        print()

        print(
            f"Age            : "
            f"{'PASS' if result['age']['status'] else 'FAIL'}"
        )
        print(f"Candidate Age  : {result['age']['candidate_age']}")
        print(f"Allowed Age    : {result['age']['allowed_age']}")
        print(f"Reason         : {result['age']['reason']}")

        print()

        matched_skills = result["preferred_skills"]["matched"]

        if matched_skills:

            print("Preferred Skills Matched:")

            for skill in matched_skills:
                print(f"   - {skill}")

        else:

            print("Preferred Skills Matched : None")

        print("=" * 70)

    # ------------------------------------------------
    # Ensure Output Directory Exists
    # ------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ------------------------------------------------
    # Save Results
    # ------------------------------------------------

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(
            results,
            f,
            indent=4
        )

    print()

    print("=" * 70)
    print("Eligibility checking completed.")
    print(f"Results saved to:\n{output_path}")
    print("=" * 70)

    return results