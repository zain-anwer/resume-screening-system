import { Search, Bell, Moon } from "lucide-react";
import { useLocation, useSearchParams } from "react-router-dom";
import "../styles/topbar.css";

const VISIBLE_PATHS = ["/candidates", "/ranking", "/ner-review"];

export default function Topbar() {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  const showSearch = VISIBLE_PATHS.some((p) => location.pathname.startsWith(p));

  const onChange = (e) => {
    const v = e.target.value || "";
    if (v) setSearchParams({ ...Object.fromEntries(searchParams.entries()), q: v });
    else {
      // remove q
      const entries = Object.fromEntries(searchParams.entries());
      delete entries.q;
      setSearchParams(entries);
    }
  };

  return (
    <header className="topbar">
      {showSearch && (
        <div className="topbar-search">
          <Search size={15} color="var(--text-400)" />
          <input placeholder="Search by name..." value={q} onChange={onChange} />
        </div>
      )}

      <div className="topbar-actions">
        <button className="topbar-icon-btn">
          <Moon size={18} />
        </button>
        <h4>Screenit</h4>
      </div>
    </header>
  );
}
