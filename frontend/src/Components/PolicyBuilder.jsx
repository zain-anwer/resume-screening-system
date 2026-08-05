import { useMemo, useState } from "react";
import { Plus, X, Trash2, Eye, EyeOff } from "lucide-react";
import { Card } from "../components/ui/Card.jsx";
import { savePolicy, ApiError } from "../api/client.js";
import { toYaml, deepClean, slugify, downloadYaml } from "../utils/yaml.js";
import "../styles/forms.css";

const genId = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;

// Converts "" / whitespace-only to "" and everything else to a Number,
// or "" if it isn't a valid number — so half-filled numeric fields
// don't crash the form and get cleanly dropped by deepClean().
const toNum = (v) => {
  if (v === "" || v === null || v === undefined) return "";
  const n = Number(v);
  return Number.isNaN(n) ? "" : n;
};

const emptyRegional = () => ({ id: genId(), region: "", years: "" });
const emptySubField = () => ({ id: genId(), label: "", description: "" });
const emptyOtherPolicy = () => ({ id: genId(), name: "", description: "", subFields: [] });

// ---------------------------------------------------------------------
// Education level options
// ---------------------------------------------------------------------
// These map 1:1 onto the canonical LEVELS keys in eligibility.py, via
// the alias table in rules_adapter.py (_LEVEL_ALIASES). Each `value`
// below is one of the recognized aliases, so it normalizes cleanly
// server-side instead of risking "Unrecognized minimum education
// level" from a free-typed value. Keep this list in sync with
// _LEVEL_ALIASES if the backend adds a new level.
const EDUCATION_LEVEL_OPTIONS = [
  { value: "Matric", label: "Matric / SSC" },
  { value: "Intermediate", label: "Intermediate / FSc / A-Level" },
  { value: "Diploma", label: "Diploma / Associate Degree" },
  { value: "Bachelors", label: "Bachelor's" },
  { value: "Masters", label: "Master's" },
  { value: "MPhil", label: "M.Phil" },
  { value: "PhD", label: "PhD / Doctorate" },
];

// "Preferred Skills" is the only Additional Policy name with a
// registered, automated handler in policy_registry.py (it checks each
// sub-field label against the candidate's parsed skills). Any other
// name is accepted too — it's just recorded for manual review instead
// of automated pass/fail — so this stays a free-text field with a
// suggestion rather than a locked dropdown.
const SUGGESTED_POLICY_NAMES = ["Preferred Skills"];

export default function PolicyBuilder() {
  const [jobName, setJobName] = useState("");
  const [maxAge, setMaxAge] = useState("");

  const [regional, setRegional] = useState([]);
  const [employeeRelax, setEmployeeRelax] = useState({ applicable: false, years: "" });

  const [eduYears, setEduYears] = useState("");
  const [eduLevel, setEduLevel] = useState("");
  const [degrees, setDegrees] = useState([]);
  const [degreeInput, setDegreeInput] = useState("");

  const [minExperience, setMinExperience] = useState("");

  const [otherPolicies, setOtherPolicies] = useState([]);

  const [showPreview, setShowPreview] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState(null); // { mode: "server" | "download", filename }
  const [saveError, setSaveError] = useState(null);

  // ---- regional relaxation ----
  const addRegional = () => setRegional((r) => [...r, emptyRegional()]);
  const updateRegional = (id, field, value) =>
    setRegional((r) => r.map((row) => (row.id === id ? { ...row, [field]: value } : row)));
  const removeRegional = (id) => setRegional((r) => r.filter((row) => row.id !== id));

  // ---- degree chips ----
  const addDegree = () => {
    const val = degreeInput.trim();
    if (!val) return;
    setDegrees((d) => (d.includes(val) ? d : [...d, val]));
    setDegreeInput("");
  };
  const removeDegree = (index) => setDegrees((d) => d.filter((_, i) => i !== index));

  // ---- other policies ----
  const addOtherPolicy = () => setOtherPolicies((p) => [...p, emptyOtherPolicy()]);
  const updateOtherPolicy = (id, field, value) =>
    setOtherPolicies((p) => p.map((pol) => (pol.id === id ? { ...pol, [field]: value } : pol)));
  const removeOtherPolicy = (id) => setOtherPolicies((p) => p.filter((pol) => pol.id !== id));

  const addSubField = (policyId) =>
    setOtherPolicies((p) =>
      p.map((pol) =>
        pol.id === policyId ? { ...pol, subFields: [...pol.subFields, emptySubField()] } : pol
      )
    );
  const updateSubField = (policyId, subId, field, value) =>
    setOtherPolicies((p) =>
      p.map((pol) =>
        pol.id !== policyId
          ? pol
          : {
              ...pol,
              subFields: pol.subFields.map((sf) =>
                sf.id === subId ? { ...sf, [field]: value } : sf
              ),
            }
      )
    );
  const removeSubField = (policyId, subId) =>
    setOtherPolicies((p) =>
      p.map((pol) =>
        pol.id === policyId
          ? { ...pol, subFields: pol.subFields.filter((sf) => sf.id !== subId) }
          : pol
      )
    );

  // ---- build the plain object that becomes YAML ----
  const buildPolicyObject = () => ({
    job_name: jobName.trim(),
    age: { maximum: toNum(maxAge) },
    age_relaxation: {
      regional: regional
        .filter((r) => r.region.trim() || r.years !== "")
        .map((r) => ({ region: r.region.trim(), relaxation_years: toNum(r.years) })),
      employees: employeeRelax.applicable
        ? { applicable: true, relaxation_years: toNum(employeeRelax.years) }
        : {},
    },
    education: {
      minimum_years: toNum(eduYears),
      level: eduLevel,
      degrees,
    },
    experience: { minimum_years: toNum(minExperience) },
    other_policies: otherPolicies
      .filter((p) => p.name.trim() || p.description.trim() || p.subFields.length)
      .map((p) => ({
        name: p.name.trim(),
        description: p.description.trim(),
        sub_fields: p.subFields
          .filter((sf) => sf.label.trim() || sf.description.trim())
          .map((sf) => ({ label: sf.label.trim(), description: sf.description.trim() })),
      })),
  });

  const previewYaml = useMemo(
    () => toYaml(deepClean(buildPolicyObject())),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      jobName, maxAge, regional, employeeRelax,
      eduYears, eduLevel, degrees,
      minExperience, otherPolicies,
    ]
  );

  const canSubmit = jobName.trim().length > 0 && !saving;

  const resetStatus = () => {
    setSaveResult(null);
    setSaveError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobName.trim()) return;
    resetStatus();
    setSaving(true);

    const cleaned = deepClean(buildPolicyObject());
    const yamlStr = toYaml(cleaned);
    const filename = `${slugify(jobName)}.yaml`;

    try {
      // Primary path: ask the backend to write ./config/{job_name}.yaml.
      await savePolicy({ jobName: slugify(jobName), yaml: yamlStr });
      setSaveResult({ mode: "server", filename });
    } catch (err) {
      // Backend route isn't implemented yet (see api/client.js savePolicy
      // for the expected contract) — download the file directly instead
      // so the work isn't lost. Move this file into ./config yourself.
      downloadYaml(yamlStr, filename);
      setSaveResult({ mode: "download", filename });
      if (!(err instanceof ApiError && err.status === 404)) {
        setSaveError(err);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card
      title="Build a Hiring Policy"
      subtitle="Define eligibility rules for a job opening. Fields left blank are simply omitted from the saved policy."
      headerRight={
        <button
          type="button"
          className="btn btn-outline btn-sm"
          onClick={() => setShowPreview((v) => !v)}
        >
          {showPreview ? <EyeOff size={14} /> : <Eye size={14} />}
          {showPreview ? "Hide YAML" : "Preview YAML"}
        </button>
      }
    >
      <form className="policy-form" onSubmit={handleSubmit}>
        {/* Job name */}
        <div className="form-section">
          <div className="form-field">
            <label htmlFor="policy-job-name">
              Job name<span className="form-field-optional-tag">used as the filename</span>
            </label>
            <input
              id="policy-job-name"
              type="text"
              className="form-input"
              placeholder="e.g. Senior Backend Engineer"
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
            />
          </div>
        </div>

        {/* 1. Maximum age */}
        <div className="form-section">
          <div className="form-section-header">
            <h3>1. Maximum Age</h3>
            <span className="form-badge form-badge-required">Required</span>
          </div>
          <div className="form-row">
            <div className="form-field">
              <label>Maximum age an employee is allowed to be</label>
              <input
                type="number"
                min={0}
                className="form-input"
                placeholder="e.g. 30"
                value={maxAge}
                onChange={(e) => setMaxAge(e.target.value)}
              />
            </div>
            <span className="form-row-suffix">years</span>
          </div>
        </div>

        {/* 2. Age relaxation */}
        <div className="form-section">
          <div className="form-section-header">
            <h3>2. Relaxation on Age</h3>
            <span className="form-badge form-badge-required">Required</span>
          </div>
          <p className="form-hint">Exceptions to the maximum age above. Leave a subsection empty if it doesn't apply.</p>

          <div className="form-subsection">
            <div className="form-subsection-title">Regional relaxation</div>
            <p className="form-hint">
              Region names are free text — they're matched directly against whatever province
              string a candidate's record contains, so there's no fixed list to choose from.
            </p>
            {regional.map((row) => (
              <div className="repeatable-row" key={row.id}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Region (e.g. Balochistan)"
                  value={row.region}
                  onChange={(e) => updateRegional(row.id, "region", e.target.value)}
                />
                <input
                  type="number"
                  className="form-input narrow"
                  placeholder="Years"
                  value={row.years}
                  onChange={(e) => updateRegional(row.id, "years", e.target.value)}
                />
                <button
                  type="button"
                  className="icon-btn"
                  onClick={() => removeRegional(row.id)}
                  aria-label="Remove region"
                >
                  <X size={15} />
                </button>
              </div>
            ))}
            <button type="button" className="dashed-add-btn" onClick={addRegional}>
              <Plus size={14} /> Add region
            </button>
          </div>

          <div className="form-subsection">
            <label className="form-checkbox-label">
              <input
                type="checkbox"
                checked={employeeRelax.applicable}
                onChange={(e) =>
                  setEmployeeRelax((s) => ({ ...s, applicable: e.target.checked }))
                }
              />
              Applies to current employees applying internally
            </label>
            {employeeRelax.applicable && (
              <div className="form-row" style={{ marginTop: 12 }}>
                <div className="form-field">
                  <label>Relaxation for internal employees</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="e.g. 3"
                    value={employeeRelax.years}
                    onChange={(e) =>
                      setEmployeeRelax((s) => ({ ...s, years: e.target.value }))
                    }
                  />
                </div>
                <span className="form-row-suffix">years</span>
              </div>
            )}
          </div>
        </div>

        {/* 3. Education */}
        <div className="form-section">
          <div className="form-section-header">
            <h3>3. Minimum Education</h3>
            <span className="form-badge form-badge-required">Required</span>
          </div>

          <div className="form-grid-2">
            <div className="form-field">
              <label>Years of education</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 16"
                value={eduYears}
                onChange={(e) => setEduYears(e.target.value)}
              />
            </div>
            <div className="form-field">
              <label>Level of education</label>
              <select
                className="form-input"
                value={eduLevel}
                onChange={(e) => setEduLevel(e.target.value)}
              >
                <option value="">Select a level...</option>
                {EDUCATION_LEVEL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <p className="form-hint">
            Limited to the levels the eligibility engine recognizes — anything else would fail
            every candidate with "Unrecognized minimum education level".
          </p>

          <div className="form-field" style={{ marginTop: 14 }}>
            <label>
              Degree name(s) <span className="form-field-optional-tag">optional</span>
            </label>
          </div>
          <p className="form-hint">
            Add specific degrees (e.g. BSCS, BS IT), type "Relevant" to accept any related
            degree, or leave this empty to only require the level above (e.g. any Bachelor's).
            There's no fixed degree list on the backend — it does a loose substring match
            against whatever a candidate's parsed education record contains, so this stays
            free text.
          </p>
          <div className="chip-input-row">
            <input
              type="text"
              className="form-input"
              placeholder="e.g. BSCS"
              value={degreeInput}
              onChange={(e) => setDegreeInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addDegree();
                }
              }}
            />
            <button type="button" className="btn btn-outline btn-sm" onClick={addDegree}>
              <Plus size={14} /> Add
            </button>
          </div>
          <div className="chip-list">
            {degrees.map((d, i) => (
              <span className="chip-removable" key={`${d}-${i}`}>
                {d}
                <button type="button" onClick={() => removeDegree(i)} aria-label={`Remove ${d}`}>
                  <X size={11} />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* 4. Experience */}
        <div className="form-section">
          <div className="form-section-header">
            <h3>4. Minimum Experience</h3>
            <span className="form-badge form-badge-required">Required</span>
          </div>
          <div className="form-row">
            <div className="form-field">
              <label>Minimum work experience</label>
              <input
                type="number"
                min={0}
                className="form-input"
                placeholder="e.g. 2"
                value={minExperience}
                onChange={(e) => setMinExperience(e.target.value)}
              />
            </div>
            <span className="form-row-suffix">years</span>
          </div>
        </div>

        {/* 5. Other / HR-defined policies */}
        <div className="form-section">
          <div className="form-section-header">
            <h3>Additional Policies</h3>
            <span className="form-badge form-badge-optional">Optional</span>
          </div>
          <p className="form-hint">
            Add any other rule HR wants to define — give it a name, a description, and
            optionally break it down into labeled sub-fields. Name it "Preferred Skills" (one
            sub-field label per skill) to get automated matching against a candidate's parsed
            skills — any other name is recorded for manual review instead, since the backend
            has no way to auto-evaluate a policy it doesn't have logic for yet.
          </p>

          <datalist id="other-policy-name-suggestions">
            {SUGGESTED_POLICY_NAMES.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>

          {otherPolicies.map((policy) => (
            <div className="policy-block" key={policy.id}>
              <div className="policy-block-header">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Policy name (e.g. Preferred Skills)"
                  list="other-policy-name-suggestions"
                  value={policy.name}
                  onChange={(e) => updateOtherPolicy(policy.id, "name", e.target.value)}
                />
                <button
                  type="button"
                  className="icon-btn"
                  onClick={() => removeOtherPolicy(policy.id)}
                  aria-label="Remove policy"
                >
                  <Trash2 size={15} />
                </button>
              </div>
              {policy.name.trim().toLowerCase() === "preferred skills" && (
                <p className="form-hint">
                  This name is automated: each sub-field label below is checked against the
                  candidate's parsed skills list. It's informational only and never blocks
                  eligibility on its own.
                </p>
              )}
              <textarea
                className="form-textarea"
                placeholder="Description"
                value={policy.description}
                onChange={(e) => updateOtherPolicy(policy.id, "description", e.target.value)}
              />

              <div className="policy-block-subfields">
                <div className="policy-block-subfields-title">Sub-fields (optional)</div>
                {policy.subFields.map((sf) => (
                  <div className="repeatable-row" key={sf.id}>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Label"
                      value={sf.label}
                      onChange={(e) =>
                        updateSubField(policy.id, sf.id, "label", e.target.value)
                      }
                    />
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Description"
                      value={sf.description}
                      onChange={(e) =>
                        updateSubField(policy.id, sf.id, "description", e.target.value)
                      }
                    />
                    <button
                      type="button"
                      className="icon-btn"
                      onClick={() => removeSubField(policy.id, sf.id)}
                      aria-label="Remove sub-field"
                    >
                      <X size={15} />
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  className="dashed-add-btn"
                  onClick={() => addSubField(policy.id)}
                >
                  <Plus size={14} /> Add sub-field
                </button>
              </div>
            </div>
          ))}

          <button type="button" className="dashed-add-btn" onClick={addOtherPolicy}>
            <Plus size={15} /> Add Other Policy
          </button>
        </div>

        {/* Footer */}
        <div className="form-footer">
          <div>
            {saveResult && (
              <p className="form-status form-status-success">
                {saveResult.mode === "server"
                  ? `Saved to ./config/${saveResult.filename}`
                  : `Downloaded ${saveResult.filename}`}
                {saveResult.mode === "download" && (
                  <span className="form-status-note">
                    The backend save endpoint isn't reachable yet, so the file was downloaded
                    instead — move it into ./config manually, or wire up POST /api/policy/save
                    (see api/client.js).
                  </span>
                )}
              </p>
            )}
            {saveError && (
              <p className="form-status form-status-error">
                {saveError instanceof ApiError
                  ? saveError.detail || saveError.message
                  : saveError.message}
              </p>
            )}
          </div>
          <div className="form-footer-actions">
            <button type="submit" className="btn btn-primary" disabled={!canSubmit}>
              {saving ? "Saving..." : "Add Policy"}
            </button>
          </div>
        </div>

        {showPreview && (
          <div className="yaml-preview-wrap">
            <pre className="yaml-preview">{previewYaml || "# fill in the form to see a preview"}</pre>
          </div>
        )}
      </form>
    </Card>
  );
}
