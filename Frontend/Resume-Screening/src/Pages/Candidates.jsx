import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import { fetchDashboardData } from "../api/client.js";

export default function Candidates() {
  const [candidates, setCandidates] = useState([]);

  useEffect(() => {
    // TODO (you): replace with a dedicated /api/candidates call once
    // your backend exposes the full candidate list (not just recents).
    fetchDashboardData().then((d) => setCandidates(d.recentScreenings));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Candidates</h1>
        <p>All screened candidates across every job.</p>
      </div>
      <Card>
        <div className="grid grid-3">
          {candidates.map((c) => (
            <div key={c.id} className="card" style={{ padding: 16 }}>
              <div className="candidate-cell" style={{ marginBottom: 12 }}>
                <div className="avatar-sm">{c.name.split(" ").map(w => w[0]).join("").slice(0, 2)}</div>
                <div>
                  <div className="candidate-name">{c.name}</div>
                  <div className="candidate-sub">{c.role}</div>
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 13.5, color: "var(--text-600)" }}>{c.match}% match</span>
                <Badge tone="info">{c.status}</Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
