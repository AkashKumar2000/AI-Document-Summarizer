import io
import pdfplumber
from docx import Document

SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}


def extract_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            text_parts.append(txt)
    return "\n".join(text_parts).strip()


def extract_from_docx(file_bytes: bytes) -> str:
    bio = io.BytesIO(file_bytes)
    doc = Document(bio)
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_from_text(file_bytes: bytes) -> str:
    # Try utf-8 first, fall back to latin-1
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_from_pdf(file_bytes)
    if lower.endswith(".docx"):
        return extract_from_docx(file_bytes)
    if lower.endswith(".txt") or lower.endswith(".md"):
        return extract_from_text(file_bytes)
    raise ValueError(f"Unsupported file type for {filename}")
