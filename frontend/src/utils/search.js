// Simple name matching utility: case-insensitive, partial/fuzzy per-word match
export function matchName(name = "", query = "") {
  if (!query || !name) return true;
  const q = String(query).trim().toLowerCase();
  if (!q) return true;
  const qTokens = q.split(/\s+/).filter(Boolean);
  const nameLower = String(name).toLowerCase();
  const nameWords = nameLower.split(/\s+/).filter(Boolean);

  return qTokens.every((token) => {
    // token matches if it's a substring of any word in the name
    if (nameWords.some((w) => w.includes(token))) return true;
    // or token is substring of the full name
    return nameLower.includes(token);
  });
}

export default { matchName };
