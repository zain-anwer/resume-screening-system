import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { matchName } from "../utils/search.js";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import { fetchDashboardData, ApiError } from "../api/client.js";

export default function Candidates() {
  const [candidates, setCandidates] = useState([]);
  const [error, setError] = useState(null);
  const [searchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  useEffect(() => {
    // NOTE: main.py has no dedicated /api/candidates list endpoint yet,
    // so this reuses dashboard/summary's recentScreenings (top 20 from
    // the latest run). Swap for a real /api/candidates call if you add one.
    fetchDashboardData()
      .then((d) => setCandidates(d.recentScreenings))
      .catch((err) => setError(err));
  }, []);

  const filtered = candidates.filter((c) => matchName(c.name || "", q));

  return (
    <div>
      <div className="page-header">
        <h1>Candidates</h1>
        <p>All screened candidates across every job.</p>
      </div>
      {error && (
        <p style={{ color: "var(--text-600)" }}>
          {error instanceof ApiError && error.status === 404
            ? "No pipeline run yet. Go to Resume Screening and run a job first."
            : `Couldn't load candidates: ${error.detail || error.message}`}
        </p>
      )}
      <Card>
        <div className="grid grid-3">
          {filtered.map((c) => (
            <div key={c.id} className="card" style={{ padding: 16 }}>
              <div className="candidate-cell" style={{ marginBottom: 12 }}>
                <div className="avatar-sm">{c.name.split(" ").map(w => w[0]).join("").slice(0, 2)}</div>
                <div>
                  <div className="candidate-name">{c.name}</div>
                  <div className="candidate-sub">{c.role}</div>
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 13.5, color: "var(--text-600)" }}>{(c.match)? `${c.match}% match` : 'Ineligible'}</span>
                <Badge tone="info">{c.status}</Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
