import os
import re
import shutil
import unicodedata
from pathlib import Path

import fitz
import cv2
import pytesseract

try:
    import mammoth
except ImportError:
    mammoth = None

try:
    import docx
except ImportError:
    docx = None

try:
    import win32com.client
except ImportError:
    win32com = None


def find_tesseract_executable():
    """Locate Tesseract OCR on this machine."""

    candidates = []

    env_path = os.getenv("TESSERACT_EXE")
    if env_path:
        candidates.append(env_path)

    candidates.extend([
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "tesseract"
    ])

    for candidate in candidates:
        if not candidate:
            continue

        resolved = shutil.which(candidate)
        if resolved:
            return resolved

        if Path(candidate).exists():
            return str(candidate)

    return None


TESSERACT_EXE = find_tesseract_executable()
if TESSERACT_EXE:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".webp"
}
def get_all_candidates(jobs_folder):
    """
    Scan all job folders and candidate folders.

    Expected Structure:

    jobs/
        Manager_IT/
            manager_it_01/
                anything.pdf
                anything.png

        Worker_Grade_04/
            worker_grade4_01/
                my_cv.docx
                cnic_front.jpg

    Resume can have ANY filename.
    CNIC can have ANY filename.

    Resume = PDF / DOC / DOCX
    CNIC = Image
    """

    jobs_folder = Path(jobs_folder)

    candidates = []

    if not jobs_folder.exists():
        print(f"Folder not found: {jobs_folder}")
        return candidates

    for job_folder in jobs_folder.iterdir():

        if not job_folder.is_dir():
            continue

        job_category = job_folder.name

        for candidate_folder in job_folder.iterdir():

            if not candidate_folder.is_dir():
                continue

            resume_file = None
            cnic_file = None

            for file in candidate_folder.iterdir():

                if not file.is_file():
                    continue

                extension = file.suffix.lower()

                # Resume Files
                if extension in [".pdf", ".doc", ".docx"]:

                    if resume_file is None:
                        resume_file = file

                # CNIC Images
                elif extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:

                    if cnic_file is None:
                        cnic_file = file

            candidates.append({

                "job_category": job_category,

                "candidate_id": candidate_folder.name,

                "resume": resume_file,

                "cnic": cnic_file

            })

    return candidates
def get_resume_files(folder_path):
    """
    Scan the resume folder and return all supported files.
    """

    folder = Path(folder_path)

    resume_files = []

    for file in folder.iterdir():

        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            resume_files.append(file)

    return resume_files


def get_file_type(file):
    """
    Return the file type.
    """

    ext = file.suffix.lower()

    if ext == ".pdf":
        return "PDF"

    elif ext == ".docx":
        return "DOCX"

    elif ext == ".doc":
        return "DOC"

    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
        return "IMAGE"

    return "UNKNOWN"


def normalize_text_for_extraction(text):
    """
    Normalize OCR text for field extraction while preserving line breaks.
    """

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_identity_fields(text):
    """
    Extract name, date of birth, and CNIC number from OCR text of a CNIC image.
    """

    if not text:
        return {"name": "", "dob": "", "cnic": ""}

    cleaned_text = normalize_text_for_extraction(text)
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    def find_value(labels):
        for index, line in enumerate(lines):
            lowered = line.lower()
            if not any(label in lowered for label in labels):
                continue

            for label in labels:
                match = re.search(rf"{re.escape(label)}\s*[:.-]?\s*(.+)$", line, flags=re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            if index + 1 < len(lines):
                next_line = re.sub(r"\s+", " ", lines[index + 1]).strip()
                if next_line:
                    return next_line

        return ""

    name = find_value(["name", "naam"])
    dob = find_value(["date of birth", "dob", "birth date", "dateofbirth"])

    cnic = ""
    for line in lines:
        match = re.search(r"\b(\d{5}-\d{7}-\d)\b", line)
        if match:
            cnic = match.group(1)
            break

    if not cnic:
        match = re.search(r"\b(\d{13})\b", cleaned_text)
        if match:
            cnic = match.group(1)

    return {
        "name": name.strip(),
        "dob": dob.strip(),
        "cnic": cnic.strip()
    }


def extract_cnic_details(cnic_path):
    """
    Run OCR on a CNIC image and return just the identity fields we need.
    """

    if not cnic_path:
        return {"name": "", "dob": "", "cnic": ""}

    cnic_result = extract_text(cnic_path)

    if isinstance(cnic_result, dict):
        ocr_text = cnic_result.get("text", "")
    else:
        ocr_text = cnic_result

    field_data = extract_identity_fields(ocr_text)
    field_data["raw_text"] = ocr_text

    return field_data


# ---------------- PDF ---------------- #

def extract_pdf_text(pdf_path):
    """
    Extract text from PDF using PyMuPDF.
    """

    text = ""

    try:

        doc = fitz.open(pdf_path)

        for page in doc:
            text += page.get_text()

        doc.close()

    except Exception as e:

        print(f"Error reading PDF: {e}")

    return text


# ---------------- DOCX ---------------- #

def extract_docx_text(docx_path):
    """
    Extract text from DOCX.
    """

    if mammoth is not None:
        try:
            with open(docx_path, "rb") as file:
                result = mammoth.extract_raw_text(file)
            return result.value
        except Exception as e:
            print(f"Error reading DOCX with mammoth: {e}")

    if docx is not None:
        try:
            document = docx.Document(docx_path)
            return "\n".join([paragraph.text for paragraph in document.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX with python-docx: {e}")

    print("DOCX extraction is unavailable. Install mammoth or python-docx.")
    return ""


# ---------------- DOC ---------------- #

def extract_doc_text(doc_path):

    if win32com is not None and getattr(win32com, "client", None) is not None:
        word = None

        try:
            word = win32com.client.gencache.EnsureDispatch("Word.Application")
            word.Visible = False

            document = word.Documents.Open(str(doc_path.resolve()))
            text = document.Content.Text
            document.Close(False)
            return text

        except Exception as e:
            print(f"Error reading DOC with pywin32: {e}")
        finally:
            if word:
                word.Quit()

    try:
        import docx2txt
        return docx2txt.process(str(doc_path)) or ""
    except Exception:
        pass

    try:
        import textract
        extracted = textract.process(str(doc_path))
        if isinstance(extracted, bytes):
            return extracted.decode("utf-8", errors="ignore")
        return str(extracted)
    except Exception:
        pass

    print("DOC parsing is unavailable. Install pywin32, docx2txt, or textract.")
    return ""

# ---------------- BLUR DETECTION ---------------- #

def is_blurry(image, threshold=120):
    """
    Detect if an image is blurry using Laplacian Variance.
    Returns:
        (is_blur, blur_score)
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    return blur_score < threshold, blur_score

# ---------------- IMAGE ---------------- #
def extract_image_text(image_path):
    """
    Extract text from image using OCR.
    Also detects blurry images.
    """

    try:

        if not TESSERACT_EXE:
            return {
                "text": "",
                "blurred": False,
                "blur_score": 0,
                "manual_review": True
            }

        image = cv2.imread(str(image_path))

        if image is None:

            return {
                "text": "",
                "blurred": False,
                "blur_score": 0,
                "manual_review": True
            }

        # ---------- Blur Detection ----------
        blurred, blur_score = is_blurry(image)

        # ---------- Image Preprocessing ----------

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Increase resolution
        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        # Remove noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Binarization
        gray = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        # OCR
        text = pytesseract.image_to_string(
            gray,
            lang="eng",
            config="--oem 3 --psm 3"
        )

        # ---------- Quality Check ----------

        manual_review = False

        if blurred:
            manual_review = True

        if len(text.strip()) < 250:
            manual_review = True

        return {
            "text": text,
            "blurred": blurred,
            "blur_score": round(blur_score, 2),
            "manual_review": manual_review
        }

    except Exception as e:

        print(f"Image OCR Error: {e}")

        return {
            "text": "",
            "blurred": False,
            "blur_score": 0,
            "manual_review": True
        }

# ---------------- Dispatcher ---------------- #

def extract_text(file_path):
    """
    Automatically choose the correct parser.
    """

    if not file_path:
        return ""

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    elif extension == ".doc":
        return extract_doc_text(file_path)

    elif extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
        return extract_image_text(file_path)

    return ""