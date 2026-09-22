"""Local server for the trace map.

Same shape as ``analysis/review_app/server.py``: a standard-library HTTP server,
one HTML page with no build step, and a small JSON API over files in
``analysis/state/``.

``GET  /api/runs``         every clustering run, newest first
``GET  /api/runs/<id>``    one run: clusters, 2-D coordinates, summaries
``GET  /api/pool``         the conversation steps for every pool trace
``GET  /api/job``          the embedding job's status
``POST /api/embed``        start embedding the pool with the posted options

``/api/pool`` sends steps and session position only. The pool also carries
scenario expectations, derived flags and specification slices; the map is for
choosing what to read, and showing expected outcomes beside the points would
invite picking traces by the answer.
"""

from __future__ import annotations

import argparse
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from analysis.review_app.traces import read_pool
from observability.instrument import load_env

from . import runs

HERE = Path(__file__).resolve().parent
UI_DIR = HERE / "ui"
DEFAULT_PORT = 8766


def pool_view() -> dict[str, dict[str, Any]]:
    """Trace id -> what the detail pane shows. Nothing that grades the trace."""
    out: dict[str, dict[str, Any]] = {}
    for rec in read_pool():
        session = rec.get("session") or {}
        out[str(rec["trace_id"])] = {
            "timestamp": rec.get("timestamp"),
            "steps": rec.get("steps") or [],
            "session": {
                "session_id": session.get("session_id"),
                "turn_index": session.get("turn_index"),
                "turn_count": session.get("turn_count"),
                "prior_trace_ids": session.get("prior_trace_ids") or [],
            },
            "user_role": (rec.get("langfuse") or {}).get("user_role"),
        }
    return out


class MapHandler(BaseHTTPRequestHandler):
    jobs = runs.Jobs()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_page(self) -> None:
        body = (UI_DIR / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> Any:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return None

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send_page()
        elif path == "/api/runs":
            self._send_json(runs.list_runs())
        elif path.startswith("/api/runs/"):
            result = runs.load_run(path[len("/api/runs/"):])
            if result is None:
                self._send_json({"error": "no such run"}, status=404)
            else:
                self._send_json(result)
        elif path == "/api/pool":
            self._send_json(pool_view())
        elif path == "/api/job":
            self._send_json(self.jobs.status())
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/api/embed":
            self._send_json({"error": "not found"}, status=404)
            return
        try:
            opts = runs.Options.parse(self._body())
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        try:
            self._send_json(self.jobs.start(opts), status=202)
        except RuntimeError as exc:
            self._send_json({"error": str(exc)}, status=409)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cartwheel trace map")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    # Model backends (ollama, openai, llm summaries) read their settings from .env.
    load_env()
    url = f"http://{args.host}:{args.port}/"
    server = ThreadingHTTPServer((args.host, args.port), MapHandler)
    found = runs.list_runs()
    print(f"trace map on {url}  ({len(found)} runs found; ctrl-c to stop)")
    if not found:
        print("no clustering run yet: press Embed in the app, or run "
              "`uv run python -m analysis.trace_clusters`")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
