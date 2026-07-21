// Placeholder data shaped like what your retrieval/ranking functions
// should eventually return. Replace usages of this file with real
// API calls via src/api/client.js once your backend is wired up.

export const kpis = [
  { label: "Total Resumes", value: "12,483", delta: "+8.2%", up: true },
  { label: "Screened", value: "9,821", delta: "+5.4%", up: true },
  { label: "Shortlisted", value: "1,247", delta: "+3.1%", up: true },
  { label: "Avg Match Score", value: "82.4%", delta: "+1.6%", up: true }
];

export const pipeline = [
  { stage: "Applied", value: 12483, dropoff: null },
  { stage: "Parsed", value: 11902, dropoff: "5%" },
  { stage: "Screened", value: 9821, dropoff: "17%" },
  { stage: "Ranked", value: 4210, dropoff: "57%" },
  { stage: "Shortlisted", value: 1247, dropoff: "70%" },
  { stage: "Interview", value: 428, dropoff: "66%" },
  { stage: "Hired", value: 92, dropoff: "78%" }
];

export const education = [
  { name: "Bachelor", value: 55 },
  { name: "Masters", value: 30 },
  { name: "Diploma", value: 10 },
  { name: "PhD", value: 5 }
];

export const skills = [
  { skill: "Python", count: 6000 },
  { skill: "SQL", count: 4800 },
  { skill: "React", count: 4200 },
  { skill: "AI/ML", count: 3600 },
  { skill: "Java", count: 3300 },
  { skill: "Node", count: 2600 },
  { skill: "Data Analysis", count: 2100 },
  { skill: "Flutter", count: 1400 }
];

export const experienceDist = [
  { range: "0-2 yrs", count: 4600 },
  { range: "2-5 yrs", count: 5100 },
  { range: "5-8 yrs", count: 1900 },
  { range: "8+ yrs", count: 1200 }
];

export const recentScreenings = [
  { id: "c1", name: "Rachel Patel", email: "rachel.patel@mail.com", role: "Senior Frontend Engineer", match: 95, policy: "Pass", exp: "1y", skills: ["React", "Docker"], date: "2026-07-15", status: "Shortlisted" },
  { id: "c2", name: "Liam Silva", email: "liam.silva@mail.com", role: "Product Manager", match: 96, policy: "Pass", exp: "2y", skills: ["Figma", "Python"], date: "2026-07-14", status: "Shortlisted" },
  { id: "c3", name: "Isabella Al-Sayed", email: "isabella.al-sayed@mail.com", role: "Backend Engineer", match: 96, policy: "Pass", exp: "3y", skills: ["PyTorch", "Go"], date: "2026-07-13", status: "Shortlisted" },
  { id: "c4", name: "Marcus Kowalski", email: "marcus.kowalski@mail.com", role: "UX Designer", match: 91, policy: "Review", exp: "4y", skills: ["Docker", "GraphQL"], date: "2026-07-12", status: "Shortlisted" },
  { id: "c5", name: "Sofia Rossi", email: "sofia.rossi@mail.com", role: "Senior Frontend Engineer", match: 92, policy: "Fail", exp: "5y", skills: ["Python", "TensorFlow"], date: "2026-07-11", status: "Shortlisted" },
  { id: "c6", name: "Raj Okafor", email: "raj.okafor@mail.com", role: "Product Manager", match: 93, policy: "Pass", exp: "6y", skills: ["Go", "AWS"], date: "2026-07-10", status: "Shortlisted" }
];

export const candidateRanking = [
  { rank: 1, candidate: "Rachel Patel", overall: 95, semantic: 94, bm25: 96, experience: "1 yr", education: "Bachelor", policy: "Pass", status: "Shortlisted" },
  { rank: 2, candidate: "Isabella Al-Sayed", overall: 96, semantic: 95, bm25: 97, experience: "3 yrs", education: "Masters", policy: "Pass", status: "Shortlisted" },
  { rank: 3, candidate: "Liam Silva", overall: 96, semantic: 93, bm25: 98, experience: "2 yrs", education: "Bachelor", policy: "Pass", status: "Shortlisted" },
  { rank: 4, candidate: "Raj Okafor", overall: 93, semantic: 90, bm25: 95, experience: "6 yrs", education: "Bachelor", policy: "Pass", status: "Shortlisted" },
  { rank: 5, candidate: "Marcus Kowalski", overall: 91, semantic: 88, bm25: 93, experience: "4 yrs", education: "Masters", policy: "Review", status: "Screened" }
];

export const screeningQueue = [
  { id: "s1", file: "rachel_patel_resume.pdf", status: "Completed" },
  { id: "s2", file: "liam_silva_resume.docx", status: "Parsing" },
  { id: "s3", file: "marcus_k_cnic.jpg", status: "OCR" },
  { id: "s4", file: "sofia_rossi_resume.pdf", status: "Failed" }
];

export const dashboardMock = { kpis, pipeline, education, skills, experienceDist, recentScreenings };
