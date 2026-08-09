/**
 * API CLIENT
 * -----------------------------------------------------------------
 * Talks to the FastAPI backend in main.py.
 * -----------------------------------------------------------------
 */

// Point this at your uvicorn server. Override with VITE_API_BASE_URL
// in a .env file if the backend isn't on localhost:8000.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function requestForm(path, formData) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    // No Content-Type header here on purpose — the browser sets the
    // correct multipart/form-data boundary automatically when the body
    // is a FormData instance. Setting it manually breaks the upload.
    body: formData,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* response wasn't JSON */
    }
    throw new ApiError(`Request to ${path} failed (${res.status})`, res.status, detail);
  }

  return res.json();
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* response wasn't JSON */
    }
    throw new ApiError(`Request to ${path} failed (${res.status})`, res.status, detail);
  }

  return res.json();
}

/**
 * Dashboard KPIs, pipeline, charts, recent screenings.
 * Throws ApiError with status 404 if no pipeline run has completed yet
 * — callers should catch this and show an empty/"run a job first" state.
 */
export async function fetchDashboardData() {
  return request("/dashboard/summary");
}

/** Ranked candidate list (BM25 + semantic scores). */
export async function fetchRankedCandidates() {
  return request("/ranking/latest");
}

/** Screening / extraction status per candidate file. */
export async function fetchScreeningQueue() {
  return request("/screening/queue");
}

export async function fetchNerReviewCandidates() {
  return request("/candidates/ner-review");
}

/** Backend + ranking-stage health check. */
export async function fetchHealth() {
  return request("/health");
}

/**
 * Kicks off ingestion -> extraction -> eligibility -> (ranking, if a
 * job description is supplied). Populates the in-memory run the other
 * GET endpoints read from. Ranking is optional here.
 *
 * folderPath / jobDescriptionPath are paths on the machine running the
 * backend (see KNOWN GAPS note in main.py) — not uploaded files or URLs.
 */
export async function runPipeline({ folderPath, jobDescriptionPath, topK = 20 }) {
  return request("/pipeline/run", {
    method: "POST",
    body: JSON.stringify({
      folder_path: folderPath,
      job_description_path: jobDescriptionPath || null,
      top_k: topK,
    }),
  });
}

/**
 * Runs the full pipeline (ranking required) and returns one merged
 * record per candidate: full profile + nested eligibility + ranking.
 * Useful for a candidate detail view.
 */
export async function processAndMergeCandidates({ folderPath, jobDescriptionPath, topK = 20 }) {
  return request("/candidates/process", {
    method: "POST",
    body: JSON.stringify({
      folder_path: folderPath,
      job_description_path: jobDescriptionPath,
      top_k: topK,
    }),
  });
}

/**
 * Saves a generated policy YAML to the backend, which should write it
 * to ./config/{job_name}.yaml (see main.py — this endpoint doesn't
 * exist yet and needs to be added there, e.g.:
 *
 *   @app.post("/api/policy/save")
 *   def save_policy(body: PolicySaveRequest):
 *       path = Path("config") / f"{body.job_name}.yaml"
 *       path.write_text(body.yaml)
 *       return { "path": str(path) }
 *
 * Until that route exists, callers should catch the ApiError/network
 * failure and fall back to a client-side download (see
 * PolicyBuilder.jsx, which already does this).
 */
export async function savePolicy({ jobName, yaml }) {
  return request("/policy/save", {
    method: "POST",
    body: JSON.stringify({ job_name: jobName, yaml }),
  });
}

/**
 * Saves a job description as a .docx file on the backend, which should
 * write it to ./job_descriptions/{job_title}.docx (see main.py — needs a matching
 * POST /api/jobs/save route, added the same way as /api/policy/save).
 */
export async function saveJobDescription(payload) {
  return request("/jobs/save", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Uploads a folder of resumes picked from the USER's own machine (via
 * <input type="file" webkitdirectory> — see PathPicker.jsx) to the
 * backend, which saves them under ./uploads/resumes/<id>/ preserving
 * the folder structure and returns the resulting server-side
 * `folder_path` to pass into runPipeline()/processAndMergeCandidates().
 * Needs a matching POST /api/upload/resumes route in main.py.
 */
export async function uploadResumesFolder(fileList) {
  const formData = new FormData();
  for (const file of fileList) {
    // The third argument keeps each file's relative path (e.g.
    // "manager_it/candidate_01/resume.pdf") so the backend can
    // reconstruct the original folder structure.
    formData.append("files", file, file.webkitRelativePath || file.name);
  }
  return requestForm("/upload/resumes", formData);
}

/**
 * Uploads a single job description file picked from the user's own
 * machine. Needs a matching POST /api/upload/job-description route.
 */
export async function uploadJobDescriptionFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  return requestForm("/upload/job-description", formData);
}

export { ApiError };

export default {
  fetchDashboardData,
  fetchRankedCandidates,
  fetchScreeningQueue,
  fetchHealth,
  runPipeline,
  processAndMergeCandidates,
  savePolicy,
  saveJobDescription,
  uploadResumesFolder,
  uploadJobDescriptionFile,
};
