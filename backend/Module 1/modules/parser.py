import os
import re
import shutil
import struct
import unicodedata
from pathlib import Path

import fitz

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    Image = None
    ImageFilter = None
    ImageOps = None

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
if TESSERACT_EXE and pytesseract is not None:
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

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}


def is_probable_cnic_file(file_path):
    """
    Prefer explicit CNIC filenames over treating every image as identity proof.
    """

    name = file_path.stem.lower()
    return any(keyword in name for keyword in ["cnic", "id_card", "identity", "nic"])


def is_probable_resume_file(file_path):
    """
    Resume files can be PDFs, Word docs, or scanned images named resume/cv.
    """

    extension = file_path.suffix.lower()
    name = file_path.stem.lower()

    if extension in DOCUMENT_EXTENSIONS:
        return True

    if extension in IMAGE_EXTENSIONS:
        return any(keyword in name for keyword in ["resume", "cv", "curriculum"])

    return False


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
            image_files = []

            for file in candidate_folder.iterdir():

                if not file.is_file():
                    continue

                extension = file.suffix.lower()

                if extension not in SUPPORTED_EXTENSIONS:
                    continue

                if extension in IMAGE_EXTENSIONS:
                    image_files.append(file)

                if is_probable_resume_file(file):
                    if resume_file is None:
                        resume_file = file

                elif is_probable_cnic_file(file):
                    if cnic_file is None:
                        cnic_file = file

            if cnic_file is None:
                for image_file in image_files:
                    if image_file != resume_file:
                        cnic_file = image_file
                        break

            if resume_file is None:
                for image_file in image_files:
                    if image_file != cnic_file:
                        resume_file = image_file
                        break

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

OLE_FREE_SECTOR = 0xFFFFFFFF
OLE_END_OF_CHAIN = 0xFFFFFFFE


class OleCompoundFile:
    """
    Minimal OLE reader for old Word .doc files.

    This is a fallback for simple binary Word documents when Word/pywin32,
    docx2txt, and textract are not available.
    """

    def __init__(self, file_path):
        self.data = Path(file_path).read_bytes()

        if self.data[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
            raise ValueError("Not an OLE compound file")

        header = self.data[:512]
        self.sector_size = 1 << struct.unpack_from("<H", header, 30)[0]
        self.mini_sector_size = 1 << struct.unpack_from("<H", header, 32)[0]
        self.first_directory_sector = struct.unpack_from("<I", header, 48)[0]
        self.mini_stream_cutoff = struct.unpack_from("<I", header, 56)[0]
        self.first_minifat_sector = struct.unpack_from("<I", header, 60)[0]

        self.fat = []
        for sector_id in struct.unpack_from("<109I", header, 76):
            if sector_id in (OLE_FREE_SECTOR, OLE_END_OF_CHAIN):
                continue
            sector = self._read_sector(sector_id)
            self.fat.extend(struct.unpack(f"<{self.sector_size // 4}I", sector))

        self.directory_entries = {}
        self.root_entry = None
        self._read_directory()
        self.minifat = self._read_minifat()
        self.mini_stream = b""

        if self.root_entry:
            self.mini_stream = self._read_sector_chain(self.root_entry["start"])

    def _read_sector(self, sector_id):
        offset = 512 + sector_id * self.sector_size
        return self.data[offset:offset + self.sector_size]

    def _read_sector_chain(self, start_sector):
        stream = bytearray()
        sector_id = start_sector
        seen = set()

        while (
            sector_id not in (OLE_FREE_SECTOR, OLE_END_OF_CHAIN)
            and sector_id < len(self.fat)
            and sector_id not in seen
        ):
            seen.add(sector_id)
            stream.extend(self._read_sector(sector_id))
            sector_id = self.fat[sector_id]

        return bytes(stream)

    def _read_minisector_chain(self, start_sector):
        stream = bytearray()
        sector_id = start_sector
        seen = set()

        while (
            sector_id not in (OLE_FREE_SECTOR, OLE_END_OF_CHAIN)
            and sector_id < len(self.minifat)
            and sector_id not in seen
        ):
            seen.add(sector_id)
            offset = sector_id * self.mini_sector_size
            stream.extend(self.mini_stream[offset:offset + self.mini_sector_size])
            sector_id = self.minifat[sector_id]

        return bytes(stream)

    def _read_directory(self):
        directory_stream = self._read_sector_chain(self.first_directory_sector)

        for offset in range(0, len(directory_stream), 128):
            entry = directory_stream[offset:offset + 128]
            if len(entry) < 128:
                continue

            name_length = struct.unpack_from("<H", entry, 64)[0]
            if name_length < 2:
                continue

            name = entry[:name_length - 2].decode("utf-16le", errors="ignore")
            stream_info = {
                "start": struct.unpack_from("<I", entry, 116)[0],
                "size": struct.unpack_from("<Q", entry, 120)[0],
                "type": entry[66],
            }
            self.directory_entries[name] = stream_info

            if name == "Root Entry":
                self.root_entry = stream_info

    def _read_minifat(self):
        if self.first_minifat_sector in (OLE_FREE_SECTOR, OLE_END_OF_CHAIN):
            return []

        minifat_stream = self._read_sector_chain(self.first_minifat_sector)
        usable_length = len(minifat_stream) - (len(minifat_stream) % 4)
        return list(struct.unpack(f"<{usable_length // 4}I", minifat_stream[:usable_length]))

    def read_stream(self, name):
        stream_info = self.directory_entries.get(name)
        if not stream_info:
            return b""

        if stream_info["size"] < self.mini_stream_cutoff:
            stream = self._read_minisector_chain(stream_info["start"])
        else:
            stream = self._read_sector_chain(stream_info["start"])

        return stream[:stream_info["size"]]


def extract_doc_binary_text(doc_path):
    """
    Recover plain text from simple legacy Word .doc files.
    """

    try:
        ole_file = OleCompoundFile(doc_path)
        word_stream = ole_file.read_stream("WordDocument")
    except Exception as e:
        print(f"Error reading DOC binary stream: {e}")
        return ""

    decoded_text = word_stream.decode("utf-16le", errors="ignore")
    runs = re.findall(r"[\w@.+#,/&()|:;'\-\s]{3,}", decoded_text, flags=re.UNICODE)

    cleaned_runs = []
    for run in runs:
        run = re.sub(r"[ \t]+", " ", run)
        run = re.sub(r"\n{3,}", "\n\n", run)
        run = run.strip()

        if len(run) >= 3 and re.search(r"[A-Za-z0-9]", run):
            cleaned_runs.append(run)

    return "\n".join(cleaned_runs)


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

    fallback_text = extract_doc_binary_text(doc_path)
    if fallback_text:
        return fallback_text

    print("DOC parsing is unavailable. Install pywin32, docx2txt, or textract.")
    return ""

# ---------------- BLUR DETECTION ---------------- #

def is_blurry(image, threshold=120):
    """
    Detect if an image is blurry using Laplacian Variance.
    Returns:
        (is_blur, blur_score)
    """

    if cv2 is None:
        return False, 0

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

        if not TESSERACT_EXE or pytesseract is None:
            return {
                "text": "",
                "blurred": False,
                "blur_score": 0,
                "manual_review": True
            }

        if cv2 is None:
            if Image is None:
                return {
                    "text": "",
                    "blurred": False,
                    "blur_score": 0,
                    "manual_review": True
                }

            image = Image.open(image_path)
            image = ImageOps.grayscale(image)
            image = image.resize((image.width * 2, image.height * 2))
            image = image.filter(ImageFilter.SHARPEN)
            text = pytesseract.image_to_string(
                image,
                lang="eng",
                config="--oem 3 --psm 3"
            )

            return {
                "text": text,
                "blurred": False,
                "blur_score": 0,
                "manual_review": len(text.strip()) < 250
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
