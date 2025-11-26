import React, { useRef, useState } from "react";

export default function Dropzone({ onFile }) {
  const inputRef = useRef(null);
  const [hover, setHover] = useState(false);

  const onDrop = (e) => {
    e.preventDefault();
    setHover(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  };

  return (
    <div>
      <div
        className="dropzone"
        style={{ background: hover ? "#121a3f" : "" }}
        onDragOver={(e) => {
          e.preventDefault();
          setHover(true);
        }}
        onDragLeave={() => setHover(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <div>Drag & drop a file here, or click to pick</div>
        <div className="small">PDF, DOCX, TXT, MD</div>
      </div>

      <input
        ref={inputRef}
        type="file"
        style={{ display: "none" }}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
        }}
      />
    </div>
  );
}
