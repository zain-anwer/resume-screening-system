import { Search, Bell, Moon } from "lucide-react";
import "../styles/topbar.css";

export default function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-search">
        <Search size={15} color="var(--text-400)" />
        <input placeholder="Search candidates, jobs..." />
      </div>

      <div className="topbar-actions">
        <button className="topbar-icon-btn">
          <Moon size={18} />
        </button>
        <h4>Screenit</h4>
        </div>
    </header>
  );
}
