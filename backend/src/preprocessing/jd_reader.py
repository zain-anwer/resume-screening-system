from pathlib import Path
import fitz          
from docx import Document


class JobDescriptionReader:

    @staticmethod
    def read(file_path: str) -> str:
        path = Path(file_path)

        suffix = path.suffix.lower()

        if suffix == ".txt":
            return path.read_text(encoding="utf-8")

        elif suffix == ".pdf":
            text = ""
            pdf = fitz.open(path)

            for page in pdf:
                text += page.get_text()

            return text

        elif suffix == ".docx":
            doc = Document(path)
            return "\n".join(
                paragraph.text
                for paragraph in doc.paragraphs
            )

        else:
            raise ValueError(
                f"Unsupported file: {suffix}"
            )