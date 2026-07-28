import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card.jsx";
import { fetchDashboardData, ApiError } from "../api/client.js";

export default function Analytics() {
  const [kpis, setKpis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // NOTE: reuses /api/dashboard/summary's kpis — there's no separate
    // analytics endpoint. "Time to Hire" and "Top Source" from the old
    // static mock are dropped: nothing in main.py tracks timestamps or
    // application source, so they can't be shown honestly.
    fetchDashboardData()
      .then((d) => setKpis(d.kpis))
      .catch((err) => setError(err));
  }, []);

  if (error) {
    return (
      <div className="page-header">
        <h1>Analytics</h1>
        <p>
          {error instanceof ApiError && error.status === 404
            ? "No pipeline run yet. Go to Resume Screening and run a job first."
            : `Couldn't load analytics: ${error.detail || error.message}`}
        </p>
      </div>
    );
  }

  if (!kpis) return <div className="page-header"><p>Loading analytics...</p></div>;

  return (
    <div>
      <div className="page-header">
        <h1>Analytics</h1>
        <p>Hiring metrics from the latest pipeline run.</p>
      </div>
      <div className="grid grid-4">
        {kpis.map((k) => (
          <Card key={k.label}>
            <div className="stat-card-label">{k.label}</div>
            <div className="stat-card-value" style={{ marginTop: 8 }}>{k.value}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
