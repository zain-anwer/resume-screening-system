import { Card } from "../components/ui/Card.jsx";

// TODO (you): replace with real job description data from your backend.
const jobs = [
  { id: "jd1", role: "Senior Frontend Engineer", dept: "Engineering", applicants: 214, avgMatch: 78 },
  { id: "jd2", role: "Product Manager", dept: "Product", applicants: 158, avgMatch: 71 },
  { id: "jd3", role: "Backend Engineer", dept: "Engineering", applicants: 96, avgMatch: 83 }
];

export default function JobDescriptions() {
  return (
    <div>
      <div className="page-header">
        <h1>Job Descriptions</h1>
        <p>Manage roles candidates are matched against.</p>
      </div>
      <div className="grid grid-3">
        {jobs.map((j) => (
          <Card key={j.id} title={j.role} subtitle={j.dept}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, color: "var(--text-600)", marginBottom: 14 }}>
              <span>{j.applicants} applicants</span>
              <span>{j.avgMatch}% avg match</span>
            </div>
            <button className="btn btn-primary btn-sm" style={{ width: "100%" }}>View Matching Candidates</button>
          </Card>
        ))}
      </div>
    </div>
  );
}
