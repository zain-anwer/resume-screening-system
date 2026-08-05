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
          Pakistan Security Printing Corporation (PSPC) is a state-owned enterprise
          responsible for the secure printing of Pakistan's currency notes, passports,
          postage stamps, and other sensitive government documents. Given the nature of
          its work, PSPC follows strict eligibility and security policies when hiring for
          its various programs, including PLIP batches.
        </p>
        <p style={{ fontSize: 13.5, color: "var(--text-600)", lineHeight: 1.6, marginTop: 12 }}>
          ScreenIt was built to address a specific gap: PSPC's existing hiring website
          accepts and stores resumes but does not extract candidate details or verify them
          against eligibility policy — meaning there was no automated way to confirm
          whether an applicant actually qualifies before reaching the interview stage.
        </p>
        <p style={{ fontSize: 13.5, color: "var(--text-600)", lineHeight: 1.6, marginTop: 12 }}>
          This application closes that gap. It:
        </p>
        <ul style={{ fontSize: 13.5, color: "var(--text-600)", lineHeight: 1.6, marginTop: 8, paddingLeft: 20 }}>
          <li><strong>Extracts structured data</strong> from submitted resumes (including scanned/OCR'd documents), pulling out fields like CNIC, job title, education, and experience.</li>
          <li><strong>Validates against policy</strong> by applying configurable eligibility rules (built through policy forms) to automatically determine whether a candidate meets PLIP batch requirements.</li>
          <li><strong>Filters and ranks candidates</strong>, scoring and ordering eligible applicants using BM25 + semantic matching so reviewers can focus on the strongest matches first.</li>
          <li><strong>Flags matched skills</strong>, giving interviewers an additional layer of insight to speed up and improve decision-making at the interview stage.</li>
          <li><strong>Surfaces manual review flags</strong> for cases needing human attention — blurry scans, invalid field extraction, or outright extraction failures — so nothing gets silently misjudged.</li>
          <li><strong>Exports everything to CSV</strong>, keeping results portable and easy to plug into existing HR workflows.</li>
        </ul>
        <p style={{ fontSize: 13.5, color: "var(--text-600)", lineHeight: 1.6, marginTop: 12 }}>
          In short, ScreenIt adds a policy-aware screening and ranking layer on top of
          PSPC's hiring pipeline — reducing manual effort while making eligibility
          decisions more consistent and interview shortlisting more informed.
        </p>
        <p style={{ fontSize: 12, color: "var(--text-600)", lineHeight: 1.6, marginTop: 16, opacity: 0.7 }}>
          Version 0.1.0.
        </p>
      </Card>
    </div>
  );
}