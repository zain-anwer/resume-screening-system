import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card.jsx";
import JobDescriptionBuilder from "../components/JobDescriptionBuilder.jsx";
import { fetchDashboardData, ApiError } from "../api/client.js";

export default function JobDescriptions() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // NOTE: there's no dedicated /api/jobs endpoint, so this groups the
    // dashboard's recentScreenings by role. That list is capped at the
    // 20 most recent candidates (see dashboard_summary() in main.py), so
    // applicant counts/avg match below only reflect that recent slice,
    // not every candidate in the run.
    fetchDashboardData()
      .then((d) => {
        const groups = {};
        for (const c of d.recentScreenings || []) {
          const role = c.role || "Uncategorized";
          const g = groups[role] || { applicants: 0, matches: [] };
          g.applicants += 1;
          if (c.match != null) g.matches.push(c.match);
          groups[role] = g;
        }
        setJobs(
          Object.entries(groups).map(([role, g], i) => ({
            id: `jd${i}`,
            role,
            applicants: g.applicants,
            avgMatch: g.matches.length
              ? Math.round(g.matches.reduce((a, b) => a + b, 0) / g.matches.length)
              : null,
          }))
        );
      })
      .catch((err) => setError(err));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Job Descriptions</h1>
        <p>Create job ads, and see roles seen among the most recent screenings.</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        <JobDescriptionBuilder />
      </div>

      {error && (
        <p style={{ color: "var(--text-600)" }}>
          {error instanceof ApiError && error.status === 404
            ? "No pipeline run yet. Go to Resume Screening and run a job first."
            : `Couldn't load job descriptions: ${error.detail || error.message}`}
        </p>
      )}

      <div className="grid grid-3">
        {jobs.map((j) => (
          <Card key={j.id} title={j.role}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, color: "var(--text-600)", marginBottom: 14 }}>
              <span>{j.applicants} recent applicants</span>
              <span>{j.avgMatch != null ? `${j.avgMatch}% avg match` : "no match data"}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
