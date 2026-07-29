import { useRef, useState } from "react";
import { FolderOpen, UploadCloud, Loader2 } from "lucide-react";
import { uploadResumesFolder, uploadJobDescriptionFile, ApiError } from "../api/client.js";
import "../styles/picker.css";

/**
 * Text input + native "Choose folder/file" button.
 *
 * The button opens the browser's own OS file dialog (via a hidden
 * <input type="file">) so the user picks straight from their own
 * computer — the browser never exposes a real filesystem path for
 * that selection, so the picked files are uploaded to the backend,
 * which saves them and returns the server-side path it used. That
 * path is what fills the field.
 *
 * The text input itself stays fully editable/pastable, for cases
 * where the resumes/job description already live on the server and
 * typing or pasting the existing path is faster than re-uploading.
 */
export default function PathPicker({
  id,
  label,
  value,
  onChange,
  placeholder,
  mode = "folder", // "folder" | "file"
  extensions, // e.g. ".docx,.txt" — file mode only, used as the dialog's `accept`
}) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadNote, setUploadNote] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const openPicker = () => fileInputRef.current?.click();

  const handleFilesSelected = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadNote(null);
    setUploadError(null);

    try {
      if (mode === "folder") {
        const res = await uploadResumesFolder(files);
        onChange(res.folder_path);
        setUploadNote(
          `Uploaded ${res.files_received} file${res.files_received === 1 ? "" : "s"} to the server.`
        );
      } else {
        const file = files[0];
        const res = await uploadJobDescriptionFile(file);
        onChange(res.file_path);
        setUploadNote(`Uploaded "${file.name}" to the server.`);
      }
    } catch (err) {
      setUploadError(err);
    } finally {
      setUploading(false);
      e.target.value = ""; // lets the same file/folder be re-picked later if needed
    }
  };

  return (
    <div className="form-field">
      {label && <label htmlFor={id}>{label}</label>}

      <div className="path-picker-row">
        <input
          id={id}
          type="text"
          className="form-input"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
        <button type="button" className="browse-btn" onClick={openPicker} disabled={uploading}>
          {uploading ? (
            <Loader2 size={15} className="spin" />
          ) : mode === "folder" ? (
            <FolderOpen size={15} />
          ) : (
            <UploadCloud size={15} />
          )}
          {uploading ? "Uploading..." : mode === "folder" ? "Choose folder" : "Choose file"}
        </button>
      </div>

      <p className="path-picker-hint">
        {mode === "folder"
          ? "Pick a folder from your computer, or paste a path if it's already on the server."
          : "Pick a file from your computer, or paste a path if it's already on the server."}
      </p>

      {mode === "folder" ? (
        <input
          ref={fileInputRef}
          type="file"
          webkitdirectory="true"
          directory="true"
          multiple
          hidden
          onChange={handleFilesSelected}
        />
      ) : (
        <input
          ref={fileInputRef}
          type="file"
          accept={extensions}
          hidden
          onChange={handleFilesSelected}
        />
      )}

      {uploadNote && <p className="path-picker-status path-picker-status-success">{uploadNote}</p>}
      {uploadError && (
        <p className="path-picker-status path-picker-status-error">
          {uploadError instanceof ApiError
            ? uploadError.detail || uploadError.message
            : uploadError.message}
        </p>
      )}
    </div>
  );
}
