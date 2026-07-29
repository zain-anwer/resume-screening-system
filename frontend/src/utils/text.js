/**
 * Small shared text/file helpers used by both the Policy Builder and
 * the Job Description Builder — kept separate from yaml.js since
 * they're not YAML-specific.
 */

/** Converts "Senior Backend Engineer" -> "senior_backend_engineer" for filenames. */
export function slugify(str) {
  return (
    String(str || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "") || "untitled"
  );
}

/**
 * Splits a raw input string into trimmed, non-empty tokens on commas —
 * used for the skills chip inputs so "Oracle ERP, SAP, SQL" pasted in
 * one go becomes three chips instead of one.
 */
export function splitOnCommas(raw) {
  return String(raw || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

/** Triggers a browser download of a text blob. */
export function downloadText(content, filename, mimeType = "text/plain;charset=utf-8;") {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
