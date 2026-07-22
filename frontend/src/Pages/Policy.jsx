import { Card } from "../components/ui/Card.jsx";

// TODO (you): load actual policy rules from your backend/config.
const policies = [
  { name: "Minimum Experience", value: "1 year" },
  { name: "Required Education", value: "Bachelor's or higher" },
  { name: "CNIC Verification", value: "Required" },
  { name: "Blacklist Check", value: "Enabled" }
];

export default function Policy() {
  return (
    <div>
      <div className="page-header">
        <h1>Screening Policy</h1>
        <p>Rules candidates are automatically checked against.</p>
      </div>
      <Card>
        <div className="table-wrap">
          <table className="data-table">
            <thead><tr><th>Rule</th><th>Value</th></tr></thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.name}><td>{p.name}</td><td>{p.value}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
