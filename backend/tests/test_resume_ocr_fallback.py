from pathlib import Path

from src.ingestion.utils.parser import extract_text


BASE = Path(__file__).resolve().parent.parent


def test_image_resumes_are_ocr_extracted_when_tesseract_missing():
    broken_files = [
        BASE / "jobs" / "manager_it" / "manager_it_03" / "resume.jpg",
        BASE / "jobs" / "manager_it" / "manager_it_04" / "resume.png",
        BASE / "jobs" / "worker_grade_04" / "worker_grade4_03" / "resume.jpg",
        BASE / "jobs" / "worker_grade_04" / "worker_grade4_07" / "resume.jpg",
        BASE / "jobs" / "worker_grade_04" / "worker_grade4_08" / "resume.png",
    ]

    for file_path in broken_files:
        result = extract_text(file_path)
        assert isinstance(result, dict), f"Expected dict OCR result for {file_path}"

        text = result.get("text", "")
        assert text.strip(), f"Expected OCR text for {file_path}"
        assert "\n" in text, f"Expected line breaks in OCR text for {file_path}"
