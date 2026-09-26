"""Embed summary text.

``TfidfEmbedder`` is the offline default: it needs no key and no network, and it
groups by shared vocabulary, which for structured summaries mostly means shared
tool names, statuses and request wording. The other two group by meaning, so
"where is my package" and "did order 1312 ever arrive" can land together:

``OllamaEmbedder``
    An open model served by a local Ollama daemon. Traces never leave the
    machine and there is no per-token cost. Qwen3-Embedding-0.6B is the default.
``LiteLLMEmbedder``
    A hosted model (OpenAI by default). Needs the provider key in ``.env``.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Protocol

import numpy as np

DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_OLLAMA_MODEL = "qwen3-embedding:0.6b"
BATCH = 96


class Embedder(Protocol):
    """Anything that maps a list of texts to a row-per-text matrix."""

    name: str
    # Where the text goes, for the run report: "offline", "local model" or
    # "live (hosted)".
    where: str
    # A corpus-fitted embedder (TF-IDF) gives a different vector for the same
    # text once the corpus changes, so its output must not be cached per trace.
    cacheable: bool

    def embed(self, texts: list[str]) -> np.ndarray: ...


class TfidfEmbedder:
    """Sparse lexical vectors, densified. Offline and deterministic."""

    name = "tfidf"
    where = "offline"
    cacheable = False

    def embed(self, texts: list[str]) -> np.ndarray:
        from sklearn.feature_extraction.text import TfidfVectorizer

        # min_df=2 drops one-off tokens (order numbers, names) that would make
        # every trace look unique; with a tiny corpus that would leave nothing.
        vectorizer = TfidfVectorizer(
            sublinear_tf=True,
            ngram_range=(1, 2),
            min_df=2 if len(texts) >= 10 else 1,
            token_pattern=r"[A-Za-z_][A-Za-z_]+",
        )
        return np.asarray(vectorizer.fit_transform(texts).todense(), dtype=float)


class LiteLLMEmbedder:
    """Hosted embeddings through LiteLLM. Live: needs the provider key in .env."""

    where = "live (hosted)"
    cacheable = True

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.name = f"litellm:{model}"

    def embed(self, texts: list[str]) -> np.ndarray:
        import litellm

        rows: list[list[float]] = []
        for start in range(0, len(texts), BATCH):
            response = litellm.embedding(
                model=self.model, input=texts[start : start + BATCH]
            )
            rows.extend(item["embedding"] for item in response.data)
        return np.asarray(rows, dtype=float)


class OllamaEmbedder:
    """Open embedding model served by a local Ollama daemon.

    Talks to Ollama's ``/api/embed`` directly, so it adds no dependency. The
    host comes from ``OLLAMA_HOST`` (default ``http://localhost:11434``).

    Summaries are documents, not search queries, so they are sent as plain text.
    Qwen3-Embedding's instruction prefix is for the query side of retrieval and
    would only add noise to a clustering run.
    """

    where = "local model"
    cacheable = True

    def __init__(self, model: str = DEFAULT_OLLAMA_MODEL, host: str | None = None) -> None:
        self.model = model
        self.name = f"ollama:{model}"
        base = host or os.environ.get("OLLAMA_HOST") or "http://localhost:11434"
        self.url = (base if "://" in base else f"http://{base}").rstrip("/") + "/api/embed"

    def _post(self, texts: list[str]) -> list[list[float]]:
        request = urllib.request.Request(
            self.url,
            data=json.dumps({"model": self.model, "input": texts}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.load(response)["embeddings"]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:200]
            hint = (
                f" Pull it with `ollama pull {self.model}`." if exc.code == 404 else ""
            )
            raise RuntimeError(f"Ollama returned {exc.code}: {detail}{hint}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"cannot reach Ollama at {self.url} ({exc.reason}). Start it with "
                "`ollama serve`, or set OLLAMA_HOST."
            ) from exc

    def embed(self, texts: list[str]) -> np.ndarray:
        rows: list[list[float]] = []
        for start in range(0, len(texts), BATCH):
            rows.extend(self._post(texts[start : start + BATCH]))
        return np.asarray(rows, dtype=float)


EMBEDDERS = ("tfidf", "ollama", "openai")


def build(kind: str, model: str | None = None) -> Embedder:
    """The embedder a CLI flag or app request names, with its default model."""
    if kind == "ollama":
        return OllamaEmbedder(model or DEFAULT_OLLAMA_MODEL)
    if kind == "openai":
        return LiteLLMEmbedder(model or DEFAULT_MODEL)
    if kind == "tfidf":
        return TfidfEmbedder()
    raise ValueError(f"unknown embedder: {kind!r}")
