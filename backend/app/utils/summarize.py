from __future__ import annotations
import re
import math
from typing import List
import nltk
from nltk.corpus import stopwords

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


# ----------------------------------------------------
#  TRANSFORMERS PIPE (Improved version)
# ----------------------------------------------------
_transformers_pipe = None

TRANSFORMER_MODEL_NAME = "sshleifer/distilbart-cnn-6-6"
# Alternative: "google/pegasus-xsum"

def get_transformers_pipe():
    """
    Load HuggingFace summarization pipeline safely on CPU.
    Works without accelerate, device_map, or GPU.
    """
    global _transformers_pipe
    if _transformers_pipe is not None:
        return _transformers_pipe

    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

        model_name = "sshleifer/distilbart-cnn-6-6"   # or "google/pegasus-xsum"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        _transformers_pipe = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            device=-1,  # force CPU
            truncation=True,
        )
        return _transformers_pipe

    except Exception as e:
        print("TRANSFORMER INIT FAILED:", e)
        return None


# ----------------------------------------------------
# NLTK SAFE LOAD
# ----------------------------------------------------
def ensure_nltk():
    try:
        _ = stopwords.words("english")
    except LookupError:
        nltk.download("stopwords")


# ----------------------------------------------------
# Simple summarizer
# ----------------------------------------------------
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z']+")


class SimpleSummarizer:
    def __init__(self):
        ensure_nltk()
        self.stop = set(stopwords.words("english"))

    def sentence_tokenize(self, text: str) -> List[str]:
        sents = SENT_SPLIT.split(text.strip())
        return [s.strip() for s in sents if s.strip()]

    def word_tokenize(self, text: str):
        return [w.lower() for w in WORD_RE.findall(text)]

    def summarize(self, text: str, length="medium") -> str:
        if not text.strip():
            return ""

        sents = self.sentence_tokenize(text)
        if len(sents) <= 3:
            return " ".join(sents)

        words = self.word_tokenize(text)
        freq = {}
        for w in words:
            if w not in self.stop:
                freq[w] = freq.get(w, 0) + 1

        if not freq:
            return " ".join(sents[:3])

        max_f = max(freq.values())
        for w in freq:
            freq[w] /= max_f

        scores = []
        for i, s in enumerate(sents):
            ws = self.word_tokenize(s)
            score = sum(freq.get(w, 0) for w in ws) / (len(ws) + 1e-9)
            score *= 1.0 + 0.15 * math.exp(-i / 8)
            scores.append((score, i, s))

        scores.sort(reverse=True)

        k = {"short": 3, "medium": 5, "long": 8}.get(length, 5)
        chosen = sorted(scores[:k], key=lambda t: t[1])
        return " ".join(s for (_, _, s) in chosen)


# ----------------------------------------------------
# CHUNKING
# ----------------------------------------------------
def chunk_text(text: str, chunk_chars: int):
    if len(text) <= chunk_chars:
        return [text]

    sents = SENT_SPLIT.split(text)
    chunks = []
    cur, length = [], 0

    for s in sents:
        if not s.strip():
            continue
        if length + len(s) + 1 > chunk_chars and cur:
            chunks.append(" ".join(cur).strip())
            cur, length = [], 0
        cur.append(s)
        length += len(s) + 1

    if cur:
        chunks.append(" ".join(cur).strip())
    return chunks


# ----------------------------------------------------
# Hierarchical summarization
# ----------------------------------------------------
def summarize_hierarchical(text, method="simple", length="medium", chunk_chars=8000):
    text = text.strip()
    if not text:
        return "simple", [], ""

    chunks = chunk_text(text, chunk_chars)
    simple = SimpleSummarizer()

    # check transformers availability
    used = method
    pipe = None
    if method == "transformers":
        pipe = get_transformers_pipe()
        if pipe is None:
            used = "simple"
        else:
            used = "transformers"

    out_chunks = []

    # per-chunk summary
    for idx, ch in enumerate(chunks):
        if used == "transformers":
            max_len = {"short": 200,"medium": 350,"long": 500}[length]
            min_len = {"short": 60, "medium": 120, "long": 200}[length]

            try:
                res = pipe(
                    ch,
                    max_length=max_len,
                    min_length=min_len,
                    do_sample=False,
                )
                piece = res[0]["summary_text"].strip()
            except Exception as e:
                print("Chunk transformer failed:", e)
                piece = simple.summarize(ch, length)
                used = "simple"
        else:
            piece = simple.summarize(ch, length)

        out_chunks.append((idx, len(ch), piece))

    # combine all chunk summaries
    if len(out_chunks) == 1:
        final = out_chunks[0][2]
    else:
        combined = "\n".join(p for (_, _, p) in out_chunks)

        if used == "transformers":
            try:
                res = pipe(
                    combined,
                    max_len = {"short": 200,"medium": 350,"long": 500}[length],
                    min_len = {"short": 60, "medium": 120, "long": 200}[length],
                    do_sample=False,
                )
                final = res[0]["summary_text"].strip()
            except Exception as e:
                print("Final transformer failed:", e)
                final = simple.summarize(combined, length)
                used = "simple"
        else:
            final = simple.summarize(combined, length)

    return used, out_chunks, final
