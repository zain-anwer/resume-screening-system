import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import PolicyBuilder from "../components/PolicyBuilder.jsx";
import { fetchDashboardData, ApiError } from "../api/client.js";

const policyTone = { Pass: "success", Review: "warning", Fail: "danger" };

export default function Policy() {
  const [counts, setCounts] = useState(null);
  const [sampleSize, setSampleSize] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    // NOTE: there's no dedicated policy/rules endpoint, so this tallies
    // the "policy" field (Pass/Fail/Review) already returned per-candidate
    // by /api/dashboard/summary. That list is capped at the 20 most
    // recent candidates (see dashboard_summary() in main.py), so this is
    // a snapshot of recent outcomes, not every candidate ever evaluated.
    fetchDashboardData()
      .then((d) => {
        const rows = d.recentScreenings || [];
        const tally = { Pass: 0, Fail: 0, Review: 0 };
        for (const c of rows) {
          if (tally[c.policy] != null) tally[c.policy] += 1;
        }
        setCounts(tally);
        setSampleSize(rows.length);
      })
      .catch((err) => setError(err));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Screening Policy</h1>
        <p>Define eligibility rules per job, and review recent outcomes against them.</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        <PolicyBuilder />
      </div>

      {error ? (
        <Card>
          <p style={{ color: "var(--text-600)" }}>
            {error instanceof ApiError && error.status === 404
              ? "No pipeline run yet. Go to Resume Screening and run a job first."
              : `Couldn't load policy data: ${error.detail || error.message}`}
          </p>
        </Card>
      ) : !counts ? (
        <Card>
          <p style={{ color: "var(--text-600)" }}>Loading policy data...</p>
        </Card>
      ) : (
        <Card
          title="Recent Screening Outcomes"
          subtitle={`Eligibility outcomes among the ${sampleSize} most recent screenings.`}
        >
          <div className="table-wrap">
            <table className="data-table">
              <thead><tr><th>Outcome</th><th>Candidates</th></tr></thead>
              <tbody>
                {Object.entries(counts).map(([label, count]) => (
                  <tr key={label}>
                    <td><Badge tone={policyTone[label] || "neutral"}>{label}</Badge></td>
                    <td>{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
