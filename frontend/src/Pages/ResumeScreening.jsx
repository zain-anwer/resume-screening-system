import { useEffect, useState } from "react";
import { UploadCloud } from "lucide-react";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import { fetchScreeningQueue, runPipeline, ApiError } from "../api/client.js";

const STATUS_TONE = { Parsing: "info", "Review Needed": "warning", Completed: "success" };

export default function ResumeScreening() {
  const [queue, setQueue] = useState([]);
  const [queueError, setQueueError] = useState(null);

  // Backend contract (main.py POST /api/pipeline/run) takes paths on the
  // machine running the FastAPI server, e.g.:
  //   folder_path:          C:\Users\intern\resume-screening-system\backend\jobs\manager_it
  //   job_description_path: C:\Users\intern\resume-screening-system\backend\ads\manager_it.docx
  const [folderPath, setFolderPath] = useState("");
  const [jdPath, setJdPath] = useState("");
  const [topK, setTopK] = useState(20);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState(null);
  const [runResult, setRunResult] = useState(null);

  const loadQueue = () => {
    fetchScreeningQueue()
      .then((q) => {
        setQueue(q);
        setQueueError(null);
      })
      .catch((err) => setQueueError(err));
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleSubmit = async () => {
    if (!folderPath.trim()) return;
    setRunning(true);
    setRunError(null);
    setRunResult(null);
    try {
      const result = await runPipeline({
        folderPath: folderPath.trim(),
        jobDescriptionPath: jdPath.trim() || undefined,
        topK: Number(topK) || 20,
      });
      setRunResult(result);
      loadQueue();
    } catch (err) {
      setRunError(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Resume Screening</h1>
        <p>Run the ingestion &rarr; extraction &rarr; eligibility &rarr; ranking pipeline on a folder of resumes.</p>
      </div>

      <Card title="Run a pipeline job" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <label style={{ fontSize: 13.5 }}>
            Resumes folder path (on the backend server)
            <input
              type="text"
              placeholder="C:\Users\intern\resume-screening-system\backend\jobs\manager_it"
              value={folderPath}
              onChange={(e) => setFolderPath(e.target.value)}
              style={inputStyle}
            />
          </label>
          <label style={{ fontSize: 13.5 }}>
            Job description path (optional — required for ranking)
            <input
              type="text"
              placeholder="C:\Users\intern\resume-screening-system\backend\ads\manager_it.docx"
              value={jdPath}
              onChange={(e) => setJdPath(e.target.value)}
              style={inputStyle}
            />
          </label>
          <label style={{ fontSize: 13.5, width: 120 }}>
            Top K
            <input
              type="number"
              min={1}
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
              style={inputStyle}
            />
          </label>
          <button
            className="btn btn-primary"
            style={{ width: "fit-content" }}
            onClick={handleSubmit}
            disabled={running || !folderPath.trim()}
          >
            <UploadCloud size={15} /> {running ? "Running..." : "Run Pipeline"}
          </button>

          {runError && (
            <p style={{ color: "var(--danger, #dc2626)", fontSize: 13 }}>
              {runError instanceof ApiError
                ? runError.detail || runError.message
                : runError.message}
            </p>
          )}
          {runResult && (
            <p style={{ fontSize: 13, color: "var(--text-600)" }}>
              Run {runResult.run_id}: processed {runResult.candidates_processed} candidates.
              {runResult.ranking_error && ` Ranking issue: ${runResult.ranking_error}`}
            </p>
          )}
        </div>
      </Card>

      <Card title="Processing Queue">
        {queueError ? (
          <p style={{ color: "var(--text-600)" }}>
            {queueError instanceof ApiError && queueError.status === 404
              ? "No pipeline run yet — run a job above first."
              : `Couldn't load queue: ${queueError.detail || queueError.message}`}
          </p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr><th>File</th><th>Status</th></tr>
              </thead>
              <tbody>
                {queue.map((q) => (
                  <tr key={q.id}>
                    <td>{q.file}</td>
                    <td><Badge tone={STATUS_TONE[q.status] || "neutral"}>{q.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}

const inputStyle = {
  display: "block",
  width: "100%",
  marginTop: 4,
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-md)",
  padding: 10,
  fontSize: 13.5,
  fontFamily: "inherit",
};
