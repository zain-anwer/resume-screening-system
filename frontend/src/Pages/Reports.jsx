import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card.jsx";
import ExportButton from "../components/ui/ExportButton.jsx";
import { fetchRankedCandidates, fetchDashboardData } from "../api/client.js";

export default function Reports() {
  const [ranking, setRanking] = useState([]);
  const [screenings, setScreenings] = useState([]);

  useEffect(() => {
    fetchRankedCandidates().then(setRanking).catch(() => setRanking([]));
    fetchDashboardData()
      .then((d) => setScreenings(d.recentScreenings))
      .catch(() => setScreenings([]));
  }, []);

  const reports = [
    { label: "Candidate Ranking Report", data: ranking, filename: "candidate_ranking_report.csv" },
    { label: "Resume Screening Report", data: screenings, filename: "resume_screening_report.csv" },
  ];

  return (
    <div>
      <div className="page-header">
        <h1>Reports</h1>
        <p>Export center for hiring data.</p>
      </div>
      <div className="grid grid-2">
        {reports.map((r) => (
          <Card key={r.label} className="stat-card" style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <span className="card-title">{r.label}</span>
            <ExportButton data={r.data} filename={r.filename} label="Export CSV" />
          </Card>
        ))}
      </div>
    </div>
  );
}
