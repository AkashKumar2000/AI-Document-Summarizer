import React, { useEffect, useRef, useState } from "react";
import { getCapabilities, summarizeText, uploadFile } from "./api";
import Dropzone from "./components/Dropzone";
import Slider from "./components/Slider";
import SummaryCard from "./components/SummaryCard";

export default function App() {
  const [text, setText] = useState("");
  const [method, setMethod] = useState("simple");
  const [length, setLength] = useState("medium");
  const [chunkChars, setChunkChars] = useState(8000);
  const [busy, setBusy] = useState(false);
  const [resp, setResp] = useState(null);
  const [caps, setCaps] = useState({ transformers_available: false });
  const dlRef = useRef(null);

  useEffect(() => {
    getCapabilities()
      .then(setCaps)
      .catch(() => {});
  }, []);

  const canTransformers = caps.transformers_available;

  const goSummarize = async () => {
    if (!text.trim()) return;
    setBusy(true);
    setResp(null);
    try {
      const r = await summarizeText({
        text,
        method,
        length,
        chunk_chars: chunkChars,
      });
      setResp(r);
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  };

  const onFile = async (file) => {
    setBusy(true);
    setResp(null);
    try {
      const r = await uploadFile(file, {
        method,
        length,
        chunk_chars: chunkChars,
      });
      setResp(r);
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  };

  const downloadTxt = () => {
    if (!resp) return;
    const blob = new Blob([resp.summary], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "summary.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container">
      <h1>AI Document Summarizer</h1>
      <div className="small">
        Paste text or upload a document. Choose a method and length. Works
        offline; will use transformers if available.
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="row">
          <div>
            <label>Paste text</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste or type here..."
            />
            <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
              <button onClick={goSummarize} disabled={busy || !text.trim()}>
                Summarize
              </button>
              <button
                className="copy"
                onClick={() => setText("")}
                disabled={busy || !text}
              >
                Clear
              </button>
              <button className="copy" onClick={downloadTxt} disabled={!resp}>
                Download
              </button>
            </div>
          </div>

          <div>
            <label>Upload a file</label>
            <Dropzone onFile={onFile} />
          </div>
        </div>

        <hr />

        <div className="row">
          <div>
            <label>Method</label>
            <select value={method} onChange={(e) => setMethod(e.target.value)}>
              <option value="simple">Simple (fast, local)</option>
              <option value="transformers" disabled={!canTransformers}>
                Transformers{" "}
                {canTransformers ? "(available)" : "(not installed)"}
              </option>
            </select>
          </div>

          <div>
            <label>Summary length</label>
            <select value={length} onChange={(e) => setLength(e.target.value)}>
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </div>
        </div>

        <div style={{ marginTop: 12 }}>
          <label>Chunk size (characters): {chunkChars}</label>
          <Slider value={chunkChars} onChange={setChunkChars} />
        </div>

        <div style={{ marginTop: 12 }} className="mono">
          Status: {busy ? "Working…" : "Idle"}
        </div>
      </div>

      <SummaryCard response={resp} />

      <footer className="small" style={{ marginTop: 16 }}>
        Tip: For very long PDFs, increase chunk size for fewer passes. For
        concise summaries, choose Short.
      </footer>
    </div>
  );
}
