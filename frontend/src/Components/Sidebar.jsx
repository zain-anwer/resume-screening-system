import { NavLink } from "react-router-dom";
import {
  LayoutGrid, ScanLine, ListOrdered, Users, FileText,
  BarChart3, FileOutput, ShieldCheck, Info
} from "lucide-react";
import "../styles/sidebar.css";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutGrid, end: true },
  { to: "/screening", label: "Resume Screening", icon: ScanLine },
  { to: "/ranking", label: "Candidate Ranking", icon: ListOrdered },
  { to: "/candidates", label: "Candidates", icon: Users },
  { to: "/jobs", label: "Job Descriptions", icon: FileText },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileOutput },
  { to: "/policy", label: "Policy", icon: ShieldCheck },
  { to: "/about", label: "About", icon: Info }
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        {/*
       <div className="sidebar-logo-mark" />
  */}
        <span>ScreenIt</span>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-tip">
          <strong>Pro tip</strong>
          Connect a resume folder to auto-screen new CVs the moment they land.
        </div>
      </div>
    </aside>
  );
}
