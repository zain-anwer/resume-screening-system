import { Card } from "../components/ui/Card.jsx";
import ExportButton from "../components/ui/ExportButton.jsx";
import { candidateRanking, recentScreenings } from "../data/mockData.js";

// TODO (you): each ExportButton's `data` prop should come from the
// relevant retrieval function's parsed output, not the mock imports below.
const REPORTS = [
  { label: "Candidate Ranking Report", data: candidateRanking, filename: "candidate_ranking_report.csv" },
  { label: "Resume Screening Report", data: recentScreenings, filename: "resume_screening_report.csv" }
];

export default function Reports() {
  return (
    <div>
      <div className="page-header">
        <h1>Reports</h1>
        <p>Export center for hiring data.</p>
      </div>
      <div className="grid grid-2">
        {REPORTS.map((r) => (
          <Card key={r.label} className="stat-card" style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <span className="card-title">{r.label}</span>
            <ExportButton data={r.data} filename={r.filename} label="Export CSV" />
          </Card>
        ))}
      </div>
    </div>
  );
}
