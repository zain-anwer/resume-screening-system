import { useEffect, useState } from "react";
import { FileText, ScanLine, Star, Target } from "lucide-react";
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import { Card, StatCard } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import ExportButton from "../components/ui/ExportButton.jsx";
import { fetchDashboardData } from "../api/client.js";
import "../styles/cards.css";
import "../styles/table.css";

const ICONS = [FileText, ScanLine, Star, Target];
const PIE_COLORS = ["#14818E", "#2563EB", "#F59E0B", "#8B5CF6"];
const policyTone = { Pass: "success", Review: "warning", Fail: "danger" };

export default function Dashboard() {
  // TODO (you): this effect is where the real retrieval call happens.
  // fetchDashboardData() currently returns mock data — point it at
  // your backend endpoint once it's ready (see src/api/client.js).
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchDashboardData().then(setData);
  }, []);

  if (!data) return <div className="page-header"><p>Loading dashboard...</p></div>;

  const { kpis, pipeline, education, skills, experienceDist, recentScreenings } = data;
  const maxPipeline = pipeline[0]?.value || 1;

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Today's hiring overview.</p>
      </div>

      <div className="grid grid-4" style={{ marginBottom: 20 }}>
        {kpis.map((k, i) => <StatCard key={k.label} icon={ICONS[i]} {...k} />)}
      </div>

      <div className="grid grid-2" style={{ marginBottom: 20 }}>
        <Card title="Candidate Pipeline" subtitle="Flow across every hiring stage">
          {pipeline.map((p) => (
            <div className="pipeline-row" key={p.stage}>
              <span className="pipeline-label">{p.stage}</span>
              <div className="pipeline-track">
                <div className="pipeline-fill" style={{ width: `${(p.value / maxPipeline) * 100}%` }}>
                  {p.dropoff && <span>{p.dropoff} drop-off</span>}
                </div>
              </div>
              <span className="pipeline-value">{p.value.toLocaleString()}</span>
            </div>
          ))}
        </Card>

        <Card title="Education Breakdown">
          <ResponsiveContainer width="100%" height={230}>
            <PieChart>
              <Pie data={education} dataKey="value" nameKey="name" innerRadius={0} outerRadius={90}>
                {education.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginTop: 8, fontSize: 12.5 }}>
            {education.map((e, i) => (
              <span key={e.name} style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-600)" }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: PIE_COLORS[i % PIE_COLORS.length] }} />
                {e.name}
              </span>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 20 }}>
        <Card title="Top Skills Distribution" subtitle="Across all parsed resumes">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={skills} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
              <XAxis type="number" tickLine={false} axisLine={false} fontSize={11} />
              <YAxis dataKey="skill" type="category" width={90} tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip />
              <Bar dataKey="count" fill="#14818E" radius={[0, 6, 6, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Experience Distribution" subtitle="Years of professional experience">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={experienceDist}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
              <XAxis dataKey="range" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis tickLine={false} axisLine={false} fontSize={11} />
              <Tooltip />
              <Bar dataKey="count" fill="#2563EB" radius={[6, 6, 0, 0]} barSize={36} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card
        title="Recent Screenings"
        subtitle="Latest AI-processed candidates"
        headerRight={<ExportButton data={recentScreenings} filename="recent_screenings.csv" label="Export" />}
      >
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Role</th>
                <th>Match %</th>
                <th>Policy</th>
                <th>Exp.</th>
                <th>Skills</th>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentScreenings.map((c) => (
                <tr key={c.id}>
                  <td>
                    <div className="candidate-cell">
                      <div className="avatar-sm">{c.name.split(" ").map(w => w[0]).join("").slice(0, 2)}</div>
                      <div>
                        <div className="candidate-name">{c.name}</div>
                        <div className="candidate-sub">{c.email}</div>
                      </div>
                    </div>
                  </td>
                  <td>{c.role}</td>
                  <td>
                    <span className="match-bar-track">
                      <span className="match-bar-fill" style={{ width: `${c.match}%` }} />
                    </span>
                    {c.match}%
                  </td>
                  <td><Badge tone={policyTone[c.policy] || "neutral"}>{c.policy}</Badge></td>
                  <td>{c.exp}</td>
                  <td>{c.skills.map(s => <span key={s} className="chip">{s}</span>)}</td>
                  <td>{c.date}</td>
                  <td><Badge tone="info">{c.status}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
