import { useEffect, useState } from "react";
import { UploadCloud } from "lucide-react";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import { fetchScreeningQueue } from "../api/client.js";

const STATUS_TONE = { Uploaded: "neutral", Parsing: "info", OCR: "warning", Completed: "success", Failed: "danger" };

export default function ResumeScreening() {
  const [queue, setQueue] = useState([]);
  const [links, setLinks] = useState("");

  useEffect(() => {
    // TODO (you): replace with real polling against your OCR status endpoint.
    fetchScreeningQueue().then(setQueue);
  }, []);

  const handleSubmit = () => {
    // TODO (you): POST `links` (one per line: resume + CNIC) to your
    // ingestion endpoint, which triggers the OCR/extraction module.
    console.log("submit links to backend:", links.split("\n").filter(Boolean));
  };

  return (
    <div>
      <div className="page-header">
        <h1>Resume Screening</h1>
        <p>Add resume links. The OCR module extracts candidate data automatically.</p>
      </div>

      <Card title="Add candidate links" className="grid" style={{ marginBottom: 20 }}>
        <textarea
          rows={4}
          placeholder="Paste one resume link per line..."
          value={links}
          onChange={(e) => setLinks(e.target.value)}
          style={{
            width: "100%", border: "1px solid var(--border)", borderRadius: "var(--radius-md)",
            padding: 12, fontSize: 13.5, resize: "vertical", fontFamily: "inherit"
          }}
        />
        <button className="btn btn-primary" style={{ marginTop: 12, width: "fit-content" }} onClick={handleSubmit}>
          <UploadCloud size={15} /> Start OCR Extraction
        </button>
      </Card>

      <Card title="Processing Queue">
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
      </Card>
    </div>
  );
}
