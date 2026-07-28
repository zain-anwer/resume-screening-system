import { useState } from "react";
import { Download } from "lucide-react";
import "../../styles/buttons.css";

/**
 * ExportButton
 * -----------------------------------------------------------------
 * Generic "export current data to CSV and download it" button.
 *
 * Usage:
 *   <ExportButton data={rankedCandidates} filename="candidate_ranking.csv" />
 *
 * `data` should be an array of flat objects (one row per candidate).
 * If you'd rather have the backend generate the CSV (e.g. because
 * ranking output needs heavier parsing), swap the body of
 * `handleExport` for a fetch call — see the commented alternative
 * below.
 * -----------------------------------------------------------------
 */
export default function ExportButton({ data, filename = "export.csv", label = "Export Report" }) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      // ------------------------------------------------------------
      // OPTION A — client-side CSV (works with data already in state)
      // ------------------------------------------------------------
      // TODO (you): if `data` isn't already the exact shape you want
      // in the CSV, parse/flatten your retrieval function's response
      // here before calling arrayToCsv().
      const csv = arrayToCsv(data);
      downloadCsv(csv, filename);

      // ------------------------------------------------------------
      // OPTION B — let the backend generate the CSV instead
      // (use this if the ranking/parsing logic lives server-side)
      // ------------------------------------------------------------
      // const res = await fetch("/api/export/ranking/latest/csv");
      // const blob = await res.blob();
      // const url = window.URL.createObjectURL(blob);
      // const link = document.createElement("a");
      // link.href = url;
      // link.download = filename;
      // link.click();
      // window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
      // TODO (you): surface a toast/error state here
    } finally {
      setLoading(false);
    }
  };

  return (
    <button className="btn btn-outline btn-sm" onClick={handleExport} disabled={loading || !data?.length}>
      <Download size={14} />
      {loading ? "Exporting..." : label}
    </button>
  );
}

// Converts an array of flat objects into a CSV string.
function arrayToCsv(rows) {
  if (!rows || !rows.length) return "";
  const headers = Object.keys(rows[0]);
  const escape = (val) => {
    const str = String(val ?? "");
    return /[",\n]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
  };
  const lines = [
    headers.join(","),
    ...rows.map((row) => headers.map((h) => escape(row[h])).join(","))
  ];
  return lines.join("\n");
}

function downloadCsv(csvString, filename) {
  const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
