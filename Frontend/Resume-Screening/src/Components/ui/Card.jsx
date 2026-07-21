import "../../styles/cards.css";

export function Card({ title, subtitle, headerRight, children, className = "" }) {
  return (
    <div className={`card ${className}`}>
      {(title || headerRight) && (
        <div className="card-header">
          <div>
            {title && <div className="card-title">{title}</div>}
            {subtitle && <div className="card-subtitle">{subtitle}</div>}
          </div>
          {headerRight}
        </div>
      )}
      {children}
    </div>
  );
}

export function StatCard({ icon: Icon, label, value, delta, up }) {
  return (
    <div className="card stat-card">
      <div className="stat-card-top">
        <span className="stat-card-label">{label}</span>
        {Icon && (
          <div className="stat-card-icon">
            <Icon size={16} />
          </div>
        )}
      </div>
      <div className="stat-card-value">{value}</div>
      <div className={`stat-card-delta ${up ? "up" : "down"}`}>{delta} vs last month</div>
    </div>
  );
}
