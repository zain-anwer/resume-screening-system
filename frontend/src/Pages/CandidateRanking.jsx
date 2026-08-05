import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { matchName } from "../utils/search.js";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import ExportButton from "../components/ui/ExportButton.jsx";
import { fetchRankedCandidates, ApiError } from "../api/client.js";

const policyTone = { Pass: "success", Review: "warning", Fail: "danger" };
const statusTone = { Shortlisted: "success", Screened: "info", Rejected: "danger" };

export default function CandidateRanking() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);
  const [searchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  useEffect(() => {
    fetchRankedCandidates()
      .then(setRows)
      .catch((err) => setError(err));
  }, []);

  if (error) {
    return (
      <div className="page-header">
        <h1>Candidate Ranking</h1>
        <p>
          {error instanceof ApiError && (error.status === 404 || error.status === 409)
            ? error.detail || "No ranking available yet. Run a pipeline job with a job description first."
            : `Couldn't load ranking: ${error.detail || error.message}`}
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1>Candidate Ranking</h1>
          <p>BM25 + semantic ranking against the selected job description.</p>
        </div>
        <ExportButton data={rows} filename="candidate_ranking.csv" label="Export CSV" />
      </div>

      <Card>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th><th>Candidate</th><th>Overall</th><th>Semantic</th><th>BM25</th>
                <th>Experience</th><th>Education</th><th>Policy</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.filter((r) => matchName(r.candidate || "", q)).map((r) => (
                <tr key={r.rank}>
                  <td style={{ fontWeight: 600, color: "var(--text-900)" }}>#{r.rank}</td>
                  <td className="candidate-name">{r.candidate}</td>
                  <td>{r.overall}%</td>
                  <td>{r.semantic}%</td>
                  <td>{r.bm25}%</td>
                  <td>{r.experience}</td>
                  <td>{r.education}</td>
                  <td><Badge tone={policyTone[r.policy] || "neutral"}>{r.policy}</Badge></td>
                  <td><Badge tone={statusTone[r.status] || "neutral"}>{r.status}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
