from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import SummarizeRequest, SummarizeResponse, SummarizeChunk, Capabilities
from .utils.extract import extract_text
from .utils.summarize import summarize_hierarchical, get_transformers_pipe

app = FastAPI(title="AI Document Summarizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"ok": True}

@app.get("/api/capabilities", response_model=Capabilities)
async def capabilities():
    return Capabilities(transformers_available=(get_transformers_pipe() is not None))

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="'text' is required")
    method_used, chunk_info, final = summarize_hierarchical(
        text=req.text,
        method=req.method.lower(),
        length=req.length.lower(),
        chunk_chars = max(10000, int(req.chunk_chars or 12000)),

    )
    chunks = [SummarizeChunk(chunk_index=i, original_chars=n, summary=s) for i, n, s in chunk_info]
    return SummarizeResponse(
        summary=final,
        chunks=chunks,
        method_used=method_used,
        length=req.length,
        total_chars=len(req.text),
    )

@app.post("/api/upload", response_model=SummarizeResponse)
async def upload(
    file: UploadFile = File(...),
    method: str = "simple",
    length: str = "medium",
    chunk_chars: int = 8000
):
    data = await file.read()
    try:
        text = extract_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))
    method_used, chunk_info, final = summarize_hierarchical(
        text=text,
        method=method,
        length=length,
        chunk_chars=chunk_chars,
    )
    chunks = [SummarizeChunk(chunk_index=i, original_chars=n, summary=s) for i, n, s in chunk_info]
    return SummarizeResponse(
        summary=final,
        chunks=chunks,
        method_used=method_used,
        length=length,
        total_chars=len(text),
    )
