from pydantic import BaseModel, Field
from typing import Optional, List


class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Raw text to summarize")
    method: str = Field("simple", description="'simple' or 'transformers'")
    length: str = Field("medium", description="'short' | 'medium' | 'long'")
    chunk_chars: int = Field(8000, description="Rough max characters per chunk")


class SummarizeChunk(BaseModel):
    chunk_index: int
    original_chars: int
    summary: str


class SummarizeResponse(BaseModel):
    summary: str
    chunks: Optional[List[SummarizeChunk]] = None
    method_used: str
    length: str
    total_chars: int


class Capabilities(BaseModel):
    transformers_available: bool
