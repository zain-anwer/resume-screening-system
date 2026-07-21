import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ResumeScreening from "./pages/ResumeScreening.jsx";
import CandidateRanking from "./pages/CandidateRanking.jsx";
import Candidates from "./pages/Candidates.jsx";
import JobDescriptions from "./pages/JobDescriptions.jsx";
import Analytics from "./pages/Analytics.jsx";
import Reports from "./pages/Reports.jsx";
import Policy from "./pages/Policy.jsx";
import About from "./pages/About.jsx";
import "./styles/global.css";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="screening" element={<ResumeScreening />} />
        <Route path="ranking" element={<CandidateRanking />} />
        <Route path="candidates" element={<Candidates />} />
        <Route path="jobs" element={<JobDescriptions />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="reports" element={<Reports />} />
        <Route path="policy" element={<Policy />} />
        <Route path="about" element={<About />} />
      </Route>
    </Routes>
  );
}
