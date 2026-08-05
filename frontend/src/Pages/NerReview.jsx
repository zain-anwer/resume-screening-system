import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { matchName } from "../utils/search.js";
import { Card } from "../components/ui/Card.jsx";
import ExportButton from "../components/ui/ExportButton.jsx";
import Badge from "../components/ui/Badge.jsx";
import { fetchNerReviewCandidates, ApiError } from "../api/client.js";
import "../styles/forms.css";

function flattenCandidateForCsv(candidate) {
  const personal = candidate.personal_info || {};
  const metadata = candidate.metadata || {};
  const flags = candidate.flags || {};
  const reviewReasons = flags.ner_review_reasons || [];

  return {
    id: metadata.id || candidate.id || metadata.file_name || "",
    name: personal.name || "",
    email: personal.email || "",
    phone: personal.phone || "",
    file_name: metadata.file_name || metadata.source || "",
    source: metadata.source || "",
    status: candidate.overall_status || candidate.status || "",
    review_needed: flags.needs_ner_review ? "Yes" : "No",
    review_reasons: reviewReasons
      .map((reason) => (typeof reason === "string" ? reason : JSON.stringify(reason)))
      .join(" | "),
  };
}

export default function NerReview() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [searchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  const filtered = useMemo(() => candidates.filter((c) => matchName((c.personal_info || {}).name || "", q)), [candidates, q]);
  const csvRows = useMemo(() => filtered.map(flattenCandidateForCsv), [filtered]);

  useEffect(() => {
    const loadCandidates = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchNerReviewCandidates();
        setCandidates(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    loadCandidates();
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>NER Review</h1>
        <p>Review candidates that require manual NER/OCR verification.</p>
      </div>

      <Card
        title={`NER review candidates (${candidates.length})`}
        subtitle="Candidates flagged by the extraction pipeline for manual review"
        headerRight={
          <ExportButton
            data={csvRows}
            filename="ner_review_candidates.csv"
            label="Export CSV"
          />
        }
      >
        {error ? (
          <p style={{ color: "var(--text-600)" }}>
            {error instanceof ApiError
              ? `Couldn't load NER review candidates: ${error.detail || error.message}`
              : `Couldn't load NER review candidates: ${error?.message || "Unknown error"}`}
          </p>
        ) : loading ? (
          <p style={{ color: "var(--text-600)" }}>Loading candidates...</p>
        ) : filtered.length === 0 ? (
          <p style={{ color: "var(--text-600)" }}>
            No candidates currently require manual NER review{q ? ` matching "${q}"` : ""}.
          </p>
        ) : (
          <div className="table-wrap" style={{ marginTop: 12 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>File</th>
                  <th>Status</th>
                  <th>Review Reasons</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((candidate) => {
                  const personal = candidate.personal_info || {};
                  const metadata = candidate.metadata || {};
                  const flags = candidate.flags || {};
                  const reasons = flags.ner_review_reasons || [];

                  return (
                    <tr key={metadata.id || candidate.id || metadata.file_name || personal.name}>
                      <td>{personal.name || "Untitled candidate"}</td>
                      <td>{metadata.file_name || metadata.source || "Unknown file"}</td>
                      <td>
                        <Badge tone="warning">{candidate.overall_status || candidate.status || "Review"}</Badge>
                      </td>
                      <td style={{ fontSize: 13, color: "var(--text-700)" }}>
                        {reasons.length > 0
                          ? reasons.map((reason, index) => (
                              <div key={index}>{typeof reason === "string" ? reason : JSON.stringify(reason)}</div>
                            ))
                          : "Needs manual review"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
