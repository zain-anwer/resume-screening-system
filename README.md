# Screenit — Resume Screening & Ranking System

Screenit takes a folder of scanned/OCR'd resumes and turns them into structured, ranked candidate data. It extracts key fields (like name, CNIC, job title, and section content) from raw resume text, checks each candidate against eligibility rules, and ranks the eligible ones using BM25-based retrieval — all served through a FastAPI backend and a React/Vite frontend.

## How It Works

1. **Ingestion** — Resume text (from OCR) is normalized and cleaned.
2. **Extraction** — A segregator groups lines into sections (Experience, Education, etc.), and section-specific parsers (regex + NER) pull out structured fields into a JSON template.
3. **Policy Engine** — Extracted candidates are checked against eligibility rules (built-in and HR-defined), and stamped as eligible or not.
4. **Ranking** — Eligible candidates are ranked via BM25 retrieval against the job requirements.
5. **Frontend** — A dashboard displays the ranked list, screening queue status, and summary stats, pulling from the FastAPI backend.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### OCR Setup (Windows)

1. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
2. Add `C:\Program Files\Tesseract-OCR` (the folder containing `tesseract.exe`, **not** the `.exe` itself) to your Windows **System/User `Path`** environment variable.
3. Restart your terminal/VS Code so the updated `Path` takes effect.
4. Verify the install:
   ```bash
   tesseract --version
   tesseract --list-langs
   ```
   Make sure `eng` shows up in the language list.

## Setup & Running the App

### 1. Clone the repository

```bash
git clone <repo-url>
cd resume_screening_system
```

### 2. Run the setup script

The setup script (in the project root) installs dependencies and prepares the environment for both backend and frontend.

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Start the backend

```bash
cd backend
source .venv/Scripts/activate   # on Mac/Linux use: source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`.

### 4. Start the frontend

Open a new terminal window/tab for this step (keep the backend running).

```bash
cd frontend
npm run dev
```

The app will be live at the URL Vite prints in the terminal (typically `http://localhost:5173`).

## Usage

1. Place a folder of scanned resumes (with OCR'd text) where the backend expects them.
2. Open the frontend dashboard.
3. Trigger a screening run — the backend will extract, validate, apply eligibility rules, and rank candidates.
4. View the ranked candidate list and screening queue status on the dashboard.

## Notes

- Both the backend and frontend must be running simultaneously for the app to work.
- If Tesseract isn't found, double-check the `Path` variable and restart your terminal — this is the most common setup issue.
