import React from "react";

export default function SummaryCard({ response }) {
  if (!response) return null;

  return (
    <div className="card" style={{ marginTop: 16 }}>
      {/* Header with summary info */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div className="badge">Method: {response.method_used}</div>
        <button
          className="copy"
          onClick={() => {
            navigator.clipboard.writeText(response.summary);
          }}
        >
          Copy
        </button>
      </div>

      <hr />

      {/* Main summary */}
      <div className="summary">{response.summary}</div>

      {/* Show chunk summaries if multiple */}
      {response.chunks?.length > 1 && (
        <>
          <hr />
          <div className="mono">Chunk summaries ({response.chunks.length})</div>
          <ul>
            {response.chunks.map((c) => (
              <li
                key={c.chunk_index}
                className="small"
                style={{ marginTop: 8 }}
              >
                <details>
                  <summary>
                    Chunk {c.chunk_index + 1} — {c.original_chars} chars
                  </summary>
                  <div style={{ marginTop: 6, whiteSpace: "pre-wrap" }}>
                    {c.summary}
                  </div>
                </details>
              </li>
            ))}
          </ul>
        </>
      )}

      <hr />
      <div className="small">Total input chars: {response.total_chars}</div>
    </div>
  );
}
