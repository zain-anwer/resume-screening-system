import { Card } from "../components/ui/Card.jsx";

// TODO (you): replace with real aggregate metrics from your backend.
const metrics = [
  { label: "Time to Hire", value: "18 days" },
  { label: "Avg Resume Score", value: "82.4%" },
  { label: "Acceptance Rate", value: "64%" },
  { label: "Top Source", value: "LinkedIn" }
];

export default function Analytics() {
  return (
    <div>
      <div className="page-header">
        <h1>Analytics</h1>
        <p>Executive hiring metrics.</p>
      </div>
      <div className="grid grid-4">
        {metrics.map((m) => (
          <Card key={m.label}>
            <div className="stat-card-label">{m.label}</div>
            <div className="stat-card-value" style={{ marginTop: 8 }}>{m.value}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
