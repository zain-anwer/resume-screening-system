from backend.src.adapters.jd_adapter import JobDescriptionAdapter

job = JobDescriptionAdapter.adapt(
    job_id="jd_001",
    file_path="backend/data/job_descriptions/ai_engineer.txt",
)

print(job)