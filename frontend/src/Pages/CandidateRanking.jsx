import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import ExportButton from "../components/ui/ExportButton.jsx";
import { fetchRankedCandidates } from "../api/client.js";

const policyTone = { Pass: "success", Review: "warning", Fail: "danger" };
const statusTone = { Shortlisted: "success", Screened: "info", Rejected: "danger" };

export default function CandidateRanking() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    // TODO (you): fetchRankedCandidates() should call your backend
    // endpoint that runs BM25 and returns the PARSED ranking JSON
    // (rank, candidate, overall/semantic/bm25 scores, etc.) — see
    // the comment inside src/api/client.js for where that plugs in.
    fetchRankedCandidates().then(setRows);
  }, []);

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
              {rows.map((r) => (
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
