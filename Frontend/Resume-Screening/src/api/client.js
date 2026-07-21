/**
 * API CLIENT
 * -----------------------------------------------------------------
 * This is the single place the frontend talks to your backend.
 * Replace the bodies of these functions with real fetch/axios calls
 * to your FastAPI endpoints once they're ready.
 * -----------------------------------------------------------------
 */

const BASE_URL = "/api"; // adjust if your backend runs elsewhere

/**
 * Fetch dashboard summary data (KPIs, pipeline, charts, recent screenings).
 * TODO: replace with a real call, e.g.:
 *   const res = await fetch(`${BASE_URL}/dashboard/summary`);
 *   return res.json();
 */
export async function fetchDashboardData() {
  // Placeholder — swap for your retrieval function's response.
  const { dashboardMock } = await import("../data/mockData.js");
  return dashboardMock;
}

/**
 * Fetch the ranked candidate list (from your BM25 module output,
 * already parsed into JSON on the backend).
 * TODO: replace with:
 *   const res = await fetch(`${BASE_URL}/ranking/latest`);
 *   return res.json();
 */
export async function fetchRankedCandidates() {
  const { candidateRanking } = await import("../data/mockData.js");
  return candidateRanking;
}

/**
 * Fetch resume screening queue / OCR processing status.
 * TODO: replace with a real polling call to your OCR status endpoint.
 */
export async function fetchScreeningQueue() {
  const { screeningQueue } = await import("../data/mockData.js");
  return screeningQueue;
}

export default { fetchDashboardData, fetchRankedCandidates, fetchScreeningQueue };
