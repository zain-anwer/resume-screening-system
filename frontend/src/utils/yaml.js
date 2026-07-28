/**
 * MINI YAML SERIALIZER
 * -----------------------------------------------------------------
 * Turns a plain JS object (strings/numbers/booleans/arrays/nested
 * objects) into a YAML string, with no external dependency.
 *
 * It only needs to cover the shapes the Policy Builder produces:
 * nested maps, arrays of maps, and arrays of scalars. It is not a
 * general-purpose YAML writer (no anchors, multiline strings, etc).
 * -----------------------------------------------------------------
 */

const INDENT = "  ";
const pad = (level) => INDENT.repeat(level);

function needsQuotes(str) {
  if (str === "") return true;
  if (/^\s|\s$/.test(str)) return true;
  if (/^(true|false|null|yes|no|on|off|~)$/i.test(str)) return true;
  if (/^-?\d+(\.\d+)?$/.test(str)) return true;
  if (/^[-?:,[\]{}#&*!|>'"%@`]/.test(str)) return true;
  if (/: |:$/.test(str)) return true;
  if (/ #/.test(str)) return true;
  if (/\n/.test(str)) return true;
  return false;
}

function scalar(value) {
  if (value === null || value === undefined) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return String(value);
  const str = String(value);
  return needsQuotes(str) ? JSON.stringify(str) : str;
}

function isEmptyValue(v) {
  if (v === null || v === undefined) return true;
  if (typeof v === "string") return v.trim() === "";
  if (Array.isArray(v)) return v.length === 0;
  if (typeof v === "object") return Object.keys(v).length === 0;
  return false;
}

// Renders `key: value` (or `key:` + nested block) at the given indent.
function stringifyEntry(key, val, indent) {
  const lead = pad(indent);
  if (val !== null && typeof val === "object") {
    if (isEmptyValue(val)) {
      return lead + key + ": " + (Array.isArray(val) ? "[]" : "{}") + "\n";
    }
    return lead + key + ":\n" + stringifyBlock(val, indent + 1);
  }
  return lead + key + ": " + scalar(val) + "\n";
}

// Renders a mapping's entries, or an array's items, at the given indent.
function stringifyBlock(value, indent) {
  if (Array.isArray(value)) {
    return value.map((item) => stringifyListItem(item, indent)).join("");
  }
  return Object.entries(value)
    .map(([key, val]) => stringifyEntry(key, val, indent))
    .join("");
}

// Renders one `- ...` list item at the given indent.
function stringifyListItem(item, indent) {
  if (Array.isArray(item)) {
    if (isEmptyValue(item)) return pad(indent) + "- []\n";
    return pad(indent) + "-\n" + stringifyBlock(item, indent + 1);
  }
  if (item !== null && typeof item === "object") {
    return Object.entries(item)
      .map(([k, v], i) => {
        const entryStr = stringifyEntry(k, v, indent + 1);
        if (i === 0) {
          // Swap the first line's indent for a "- " dash so the block
          // reads as one list item instead of a nested map.
          const fullPad = pad(indent + 1);
          return pad(indent) + "- " + entryStr.slice(fullPad.length);
        }
        return entryStr;
      })
      .join("");
  }
  return pad(indent) + "- " + scalar(item) + "\n";
}

/** Serializes a plain object to a YAML string. */
export function toYaml(obj) {
  if (isEmptyValue(obj)) return "{}\n";
  return stringifyBlock(obj, 0).trimEnd() + "\n";
}

/**
 * Recursively strips empty strings / empty arrays / empty objects /
 * null / undefined from an object so the generated YAML only shows
 * fields the user actually filled in. Booleans and 0 are kept since
 * they're meaningful values, not "empty".
 */
export function deepClean(value) {
  if (Array.isArray(value)) {
    return value.map(deepClean).filter((v) => !isEmptyValue(v));
  }
  if (value !== null && typeof value === "object") {
    const out = {};
    for (const [k, v] of Object.entries(value)) {
      const cleaned = deepClean(v);
      if (!isEmptyValue(cleaned) || typeof cleaned === "boolean" || cleaned === 0) {
        out[k] = cleaned;
      }
    }
    return out;
  }
  if (typeof value === "string") return value.trim();
  return value;
}

/** Converts "Senior Backend Engineer" -> "senior_backend_engineer" for filenames. */
export function slugify(str) {
  return String(str || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "") || "policy";
}

/** Triggers a browser download of a YAML string. */
export function downloadYaml(yamlString, filename) {
  const blob = new Blob([yamlString], { type: "text/yaml;charset=utf-8;" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}