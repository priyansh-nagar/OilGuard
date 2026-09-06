/**
 * Single place that talks to the backend.
 * The rest of the UI only cares about the JSON shape, not how it was produced.
 */
const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function analyzeImage(file) {
  const form = new FormData();
  form.append("image", file);

  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    let detail = "Analysis failed.";
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }

  return response.json();
}
