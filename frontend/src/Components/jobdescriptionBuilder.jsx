import { useState } from "react";
import { Plus, X } from "lucide-react";
import { Card } from "../components/ui/Card.jsx";
import { saveJobDescription, ApiError } from "../api/client.js";
import { slugify, splitOnCommas } from "../utils/text.js";
import "../styles/forms.css";

const genId = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;

const EMPLOYMENT_TYPES = ["Permanent", "Outsourced", "Contractual", "Internship", "Apprenticeship"];

export default function JobDescriptionBuilder() {
  const [jobTitle, setJobTitle] = useState("");
  const [department, setDepartment] = useState("");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState(EMPLOYMENT_TYPES[0]);

  const [experienceRequired, setExperienceRequired] = useState("");
  const [educationRequired, setEducationRequired] = useState("");

  const [requiredSkills, setRequiredSkills] = useState([]);
  const [requiredSkillInput, setRequiredSkillInput] = useState("");
  const [preferredSkills, setPreferredSkills] = useState([]);
  const [preferredSkillInput, setPreferredSkillInput] = useState("");

  const [responsibilities, setResponsibilities] = useState([{ id: genId(), text: "" }]);

  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState(null); // { filename }
  const [saveError, setSaveError] = useState(null);

  // ---- skills chip inputs (comma-separated or one at a time) ----
  const addSkills = (raw, setList) => {
    const tokens = splitOnCommas(raw);
    if (!tokens.length) return;
    setList((prev) => Array.from(new Set([...prev, ...tokens])));
  };
  const skillKeyHandler = (setInput, addFn) => (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addFn();
    }
  };

  const addRequiredSkills = () => {
    addSkills(requiredSkillInput, setRequiredSkills);
    setRequiredSkillInput("");
  };
  const removeRequiredSkill = (i) => setRequiredSkills((s) => s.filter((_, idx) => idx !== i));

  const addPreferredSkills = () => {
    addSkills(preferredSkillInput, setPreferredSkills);
    setPreferredSkillInput("");
  };
  const removePreferredSkill = (i) => setPreferredSkills((s) => s.filter((_, idx) => idx !== i));

  // ---- responsibilities (bullet list) ----
  const addResponsibility = () =>
    setResponsibilities((r) => [...r, { id: genId(), text: "" }]);
  const updateResponsibility = (id, text) =>
    setResponsibilities((r) => r.map((row) => (row.id === id ? { ...row, text } : row)));
  const removeResponsibility = (id) =>
    setResponsibilities((r) => (r.length > 1 ? r.filter((row) => row.id !== id) : r));

  const canSubmit = jobTitle.trim().length > 0 && !saving;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;
    setSaveResult(null);
    setSaveError(null);
    setSaving(true);

    const payload = {
      job_title: jobTitle.trim(),
      department: department.trim(),
      location: location.trim(),
      employment_type: employmentType,
      experience_required: experienceRequired.trim(),
      education_required: educationRequired.trim(),
      required_skills: requiredSkills,
      preferred_skills: preferredSkills,
      responsibilities: responsibilities.map((r) => r.text.trim()).filter(Boolean),
    };

    try {
      // The backend writes this to ./ads/{job_title}.docx — see
      // api/client.js saveJobDescription() for the expected contract.
      // Unlike the policy YAML form, there's no client-side fallback
      // here: generating a real .docx in the browser needs its own
      // dependency, so if this fails, the backend route is the thing
      // to check first.
      const result = await saveJobDescription(payload);
      setSaveResult({ filename: result?.path ? result.path.split(/[\\/]/).pop() : `${slugify(jobTitle)}.docx` });
    } catch (err) {
      setSaveError(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card
      title="Create a Job Description"
      subtitle="Fill this in once per opening — it gets saved as a .docx ad your screening pipeline reads from."
    >
      <form className="policy-form" onSubmit={handleSubmit}>
        {/* Basics */}
        <div className="form-section">
          <div className="form-grid-2">
            <div className="form-field">
              <label>
                Job title<span className="form-field-optional-tag">used as the filename</span>
              </label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Senior IT Manager"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>
            <div className="form-field">
              <label>Department</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Information Technology"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
              />
            </div>
          </div>
          <div className="form-grid-2" style={{ marginTop: 14 }}>
            <div className="form-field">
              <label>Location</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Karachi, Pakistan"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
            <div className="form-field">
              <label>Employment type</label>
              <select
                className="form-select"
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
              >
                {EMPLOYMENT_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Experience & education */}
        <div className="form-section">
          <div className="form-field">
            <label>Experience required</label>
          </div>
          <p className="form-hint">Free text — e.g. "8+ years of IT experience with at least 5 years in a managerial role."</p>
          <textarea
            className="form-textarea"
            placeholder="Describe the experience needed..."
            value={experienceRequired}
            onChange={(e) => setExperienceRequired(e.target.value)}
          />

          <div className="form-field" style={{ marginTop: 18 }}>
            <label>Education required</label>
          </div>
          <p className="form-hint">Free text — e.g. "Bachelor's or Master's degree in Computer Science or related field."</p>
          <textarea
            className="form-textarea"
            placeholder="Describe the education needed..."
            value={educationRequired}
            onChange={(e) => setEducationRequired(e.target.value)}
          />
        </div>

        {/* Required skills */}
        <div className="form-section">
          <div className="form-field">
            <label>Required skills</label>
          </div>
          <p className="form-hint">Add one at a time, or paste several separated by commas.</p>
          <div className="chip-input-row">
            <input
              type="text"
              className="form-input"
              placeholder="e.g. SQL, Python, Networking"
              value={requiredSkillInput}
              onChange={(e) => setRequiredSkillInput(e.target.value)}
              onKeyDown={skillKeyHandler(setRequiredSkillInput, addRequiredSkills)}
            />
            <button type="button" className="btn btn-outline btn-sm" onClick={addRequiredSkills}>
              <Plus size={14} /> Add
            </button>
          </div>
          <div className="chip-list">
            {requiredSkills.map((s, i) => (
              <span className="chip-removable" key={`${s}-${i}`}>
                {s}
                <button type="button" onClick={() => removeRequiredSkill(i)} aria-label={`Remove ${s}`}>
                  <X size={11} />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Preferred skills */}
        <div className="form-section">
          <div className="form-field">
            <label>
              Preferred skills <span className="form-field-optional-tag">optional</span>
            </label>
          </div>
          <p className="form-hint">Nice-to-haves — same as above, one at a time or comma-separated.</p>
          <div className="chip-input-row">
            <input
              type="text"
              className="form-input"
              placeholder="e.g. AWS, Azure, Project Management"
              value={preferredSkillInput}
              onChange={(e) => setPreferredSkillInput(e.target.value)}
              onKeyDown={skillKeyHandler(setPreferredSkillInput, addPreferredSkills)}
            />
            <button type="button" className="btn btn-outline btn-sm" onClick={addPreferredSkills}>
              <Plus size={14} /> Add
            </button>
          </div>
          <div className="chip-list">
            {preferredSkills.map((s, i) => (
              <span className="chip-removable" key={`${s}-${i}`}>
                {s}
                <button type="button" onClick={() => removePreferredSkill(i)} aria-label={`Remove ${s}`}>
                  <X size={11} />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Responsibilities */}
        <div className="form-section">
          <div className="form-field">
            <label>Responsibilities</label>
          </div>
          <p className="form-hint">One bullet per line — these become the bullet list in the generated document.</p>
          {responsibilities.map((row, i) => (
            <div className="repeatable-row" key={row.id}>
              <input
                type="text"
                className="form-input"
                placeholder={`e.g. ${i === 0 ? "Lead ERP implementation projects." : "Manage enterprise IT infrastructure."}`}
                value={row.text}
                onChange={(e) => updateResponsibility(row.id, e.target.value)}
              />
              <button
                type="button"
                className="icon-btn"
                onClick={() => removeResponsibility(row.id)}
                aria-label="Remove responsibility"
              >
                <X size={15} />
              </button>
            </div>
          ))}
          <button type="button" className="dashed-add-btn" onClick={addResponsibility}>
            <Plus size={14} /> Add bullet
          </button>
        </div>

        {/* Footer */}
        <div className="form-footer">
          <div>
            {saveResult && (
              <p className="form-status form-status-success">
                Saved to ./ads/{saveResult.filename}
              </p>
            )}
            {saveError && (
              <p className="form-status form-status-error">
                {saveError instanceof ApiError
                  ? saveError.detail || saveError.message
                  : saveError.message}
                <span className="form-status-note">
                  Make sure the backend is running and POST /api/jobs/save exists (see api/client.js).
                </span>
              </p>
            )}
          </div>
          <div className="form-footer-actions">
            <button type="submit" className="btn btn-primary" disabled={!canSubmit}>
              {saving ? "Saving..." : "Add Job"}
            </button>
          </div>
        </div>
      </form>
    </Card>
  );
}
