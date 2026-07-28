import "../../styles/cards.css";

const TONE_CLASS = {
  success: "badge-success",
  warning: "badge-warning",
  danger: "badge-danger",
  info: "badge-info",
  neutral: "badge-neutral"
};

export default function Badge({ tone = "neutral", children }) {
  return <span className={`badge ${TONE_CLASS[tone] || TONE_CLASS.neutral}`}>{children}</span>;
}
