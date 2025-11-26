// Fetch available backend capabilities (like if transformers are installed)
export async function getCapabilities() {
  const r = await fetch("/api/capabilities");
  return r.json();
}

// Send text to backend summarizer
export async function summarizeText(payload) {
  const r = await fetch("/api/summarize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error((await r.json()).detail || "Request failed");
  return r.json();
}

// Upload a file to backend for summarization
export async function uploadFile(file, params) {
  const fd = new FormData();
  fd.append("file", file);
  Object.entries(params).forEach(([k, v]) => fd.append(k, v));
  const r = await fetch("/api/upload", { method: "POST", body: fd });
  if (!r.ok) throw new Error((await r.json()).detail || "Upload failed");
  return r.json();
}
