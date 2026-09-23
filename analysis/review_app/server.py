"""Local review server for the Homework 4 open-coding workflow.

Retained from the reference interface (``analysis/server.py``): a standard
library HTTP server with a plain table mapping each API path to one file under
``analysis/state/``. GET reads the file, POST overwrites it. The whole contract
stays inspectable, there is no build step, and the state files remain readable
and diffable on disk.

Changed from the reference:

*The trace pool is prebuilt.* The reference served ``samples.json``; this
serves the enriched pool from ``traces.py``, which already carries the session
grouping, the scenario join, the derived evidence pointers, and the
specification slice. The server does no enrichment, so it never stalls.

*Labels are append-only and separate from annotations.* The reference stored a
binary verdict on the annotation record itself. Homework 4 separates the two
passes: open coding writes a free-form note with no mode attached, and
structured labeling later writes one present/absent judgment per trace and
mode. Merging them would lose the sequence from observation to category, which
the handout requires stay inspectable.

*Local write first, then Langfuse.* The reference syncs to Langfuse and falls
back to a local copy when that fails. This appends locally first, because a
human judgment that survived the reading is the expensive artifact; the score
write is a mirror that can be retried.
"""

from __future__ import annotations

import argparse
import json
import webbrowser
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from analysis.helpers import _state
from observability.instrument import load_env

from .spec_index import load_spec
from .traces import CACHE_FILE

HERE = Path(__file__).resolve().parent
UI_DIR = HERE / "ui"

# API path -> the state file behind it. Same plain table as the reference.
API_FILES: dict[str, str] = {
    "/api/annotations": "annotations.json",
    "/api/patterns": "patterns.json",
    "/api/suggestions": "suggestions.json",
    "/api/manifest": "sample_manifest.json",
}

# Default document per endpoint, so a fresh checkout serves valid JSON.
API_DEFAULTS: dict[str, Any] = {
    "/api/annotations": {"annotations": []},
    "/api/patterns": {"modes": []},
    "/api/suggestions": [],
    "/api/manifest": {"batches": []},
}

_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _labels_path(mode: str) -> Path:
    return _state.state_path("labels", f"{mode}.jsonl")


def _live_labels(mode: str) -> dict[str, dict[str, Any]]:
    """Collapse a mode's append-only log to the current label per trace.

    Matches ``analysis/helpers/tools._load_labels``: a record carrying
    ``superseded_by`` is dead, and among the survivors for a trace the last one
    written wins. The full flip history stays in the file.
    """
    live: dict[str, dict[str, Any]] = {}
    for row in _state.read_jsonl(_labels_path(mode)):
        if row.get("superseded_by"):
            continue
        trace_id = row.get("trace_id")
        if trace_id:
            live[str(trace_id)] = row
    return live


def _mode_names() -> list[str]:
    """Modes that have a label file, whether or not the taxonomy still lists them."""
    root = _state.state_path("labels")
    if not root.is_dir():
        return []
    return sorted(path.stem for path in root.glob("*.jsonl"))


GRAPH_FILE = ("trace_clusters", "latest.json")


def graph_payload() -> dict[str, Any]:
    """The 2D projection from the last clustering run, trimmed for the map view.

    ``latest.json`` carries a full LLM summary per trace (~400 KB). The map
    needs only position, cluster, and a one-line title for the hover, so the
    rest stays on disk. An absent run returns empty lists rather than an error,
    so the map can say what to run instead of failing.
    """
    run = _state.read_json(_state.state_path(*GRAPH_FILE), default=None)
    if not run:
        return {"nodes": [], "clusters": [], **_graph_method({})}
    nodes = []
    for trace_id, rec in (run.get("traces") or {}).items():
        if rec.get("x") is None or rec.get("y") is None:
            continue
        summary = rec.get("summary") or {}
        nodes.append(
            {
                "trace_id": trace_id,
                "x": rec["x"],
                "y": rec["y"],
                "cluster": rec.get("cluster", -1),
                "title": summary.get("title") if isinstance(summary, dict) else None,
            }
        )
    clusters = [
        {
            "cluster": c.get("cluster"),
            "label": c.get("label", ""),
            "size": c.get("size", 0),
            "representatives": c.get("representatives", []),
        }
        for c in run.get("clusters") or []
    ]
    return {"nodes": nodes, "clusters": clusters, **_graph_method(run)}


def _graph_method(run: dict[str, Any]) -> dict[str, Any]:
    """How the map was made, for its caption and footer."""
    backends = run.get("backends") or {}
    return {
        "reducer": backends.get("reducer"),
        "summarizer": backends.get("summarizer"),
        "embedder": backends.get("embedder"),
        "min_cluster_size": (run.get("params") or {}).get("min_cluster_size"),
    }


def _sync_score(trace_id: str, mode: str, label: int, note: str | None) -> str | None:
    """Mirror one judgment to Langfuse as a score named after the mode.

    Returns the Langfuse trace id, or None when Langfuse is not configured.
    Raises on a real Langfuse error so the caller can report the failed mirror
    without losing the local record.
    """
    from analysis.helpers import langfuse_io

    if not langfuse_io.is_configured():
        return None
    return langfuse_io.write_label_score(
        trace_id=trace_id, mode=mode, label=int(label), comment=note
    )


class ReviewHandler(BaseHTTPRequestHandler):
    """Serves the UI, the prebuilt pool, and the file-backed state API."""

    def log_message(self, format: str, *args: Any) -> None:
        """Quiet by default; the access log is noise during a review session."""
        return

    # -- plumbing ---------------------------------------------------------

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.is_file():
            self._send_json({"error": f"not found: {path.name}"}, status=404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _CONTENT_TYPES.get(path.suffix, "text/plain"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> Any:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return None
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return None

    # -- routes -----------------------------------------------------------

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]

        if path in ("/", "/index.html"):
            self._send_file(UI_DIR / "index.html")
            return

        if path.startswith("/ui/"):
            asset = (UI_DIR / path[len("/ui/"):]).resolve()
            if asset.is_file() and UI_DIR.resolve() in asset.parents:
                self._send_file(asset)
                return
            self._send_json({"error": "not found"}, status=404)
            return

        if path == "/api/pool":
            pool = _state.read_json(_state.state_path(CACHE_FILE), default=None)
            if pool is None:
                self._send_json(
                    {"error": "no review pool; run python -m analysis.review_app.traces"},
                    status=503,
                )
                return
            self._send_json(pool)
            return

        if path == "/api/spec":
            spec = load_spec()
            self._send_json(
                {
                    "digest": spec.digest,
                    "raw": spec.raw,
                    "requirements": {
                        req_id: req.as_dict()
                        for req_id, req in spec.requirements.items()
                    },
                }
            )
            return

        if path == "/api/reference":
            from . import reference

            self._send_json(reference.payload())
            return

        if path == "/api/labels":
            self._send_json({mode: _live_labels(mode) for mode in _mode_names()})
            return

        if path == "/api/graph":
            self._send_json(graph_payload())
            return

        if path in API_FILES:
            data = _state.read_json(
                _state.state_path(API_FILES[path]), default=API_DEFAULTS[path]
            )
            self._send_json(data)
            return

        self._send_json({"error": f"unknown path: {path}"}, status=404)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        data = self._body()
        if data is None:
            self._send_json({"error": "expected a JSON body"}, status=400)
            return

        if path == "/api/labels":
            self._post_label(data)
            return

        if path not in API_FILES:
            self._send_json({"error": f"cannot POST to {path}"}, status=404)
            return

        _state.write_json(_state.state_path(API_FILES[path]), data)
        self._send_json({"ok": True})

    def _post_label(self, data: Any) -> None:
        """Append one present/absent judgment and mirror it to Langfuse.

        The local append happens first and unconditionally. A judgment the
        reviewer produced by reading a trace is the costly artifact here; the
        score is a mirror, and a failed mirror is reported rather than allowed
        to discard the label.
        """
        trace_id = str(data.get("trace_id") or "")
        mode = str(data.get("mode") or "")
        label = data.get("label")
        if not trace_id or not mode or label not in (0, 1):
            self._send_json(
                {"error": "need trace_id, mode, and label of 0 or 1"}, status=400
            )
            return

        note = data.get("note") or None
        existing = _live_labels(mode)
        prior = existing.get(trace_id)
        record = {
            "trace_id": trace_id,
            "label": int(label),
            "source": "human",
            "ts": _now(),
            "label_id": f"{trace_id}#{len(_state.read_jsonl(_labels_path(mode)))}",
        }
        if note:
            record["note"] = note
        if prior:
            # Keep the flip visible: the new record wins by being last, and
            # this records what it replaced without rewriting the old line.
            record["replaces"] = prior.get("label_id")
        _state.append_jsonl(_labels_path(mode), record)

        result: dict[str, Any] = {"ok": True, "label_id": record["label_id"]}
        try:
            langfuse_id = _sync_score(trace_id, mode, int(label), note)
            result["langfuse"] = langfuse_id
        except Exception as exc:  # noqa: BLE001 - the local record already survived
            result["langfuse_error"] = f"{type(exc).__name__}: {exc}"[:200]
        self._send_json(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cartwheel HW4 review interface")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    load_env()
    pool_path = _state.state_path(CACHE_FILE)
    if not pool_path.exists():
        print(f"no review pool at {pool_path}")
        print("build it first: uv run python -m analysis.review_app.traces")

    url = f"http://{args.host}:{args.port}/"
    server = ThreadingHTTPServer((args.host, args.port), ReviewHandler)
    print(f"review interface on {url}  (ctrl-c to stop)")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
