import { Card } from "../components/ui/Card.jsx";

export default function About() {
  return (
    <div>
      <div className="page-header">
        <h1>About</h1>
        <p>ScreenIt — AI-powered resume screening and candidate ranking.</p>
      </div>
      <Card>
        <p style={{ fontSize: 13.5, color: "var(--text-600)", lineHeight: 1.6 }}>
          ScreenIt extracts candidate data via OCR, ranks resumes against job descriptions
          using BM25 + semantic scoring, and helps HR teams shortlist faster. Version 0.1.0.
        </p>
      </Card>
    </div>
  );
}
