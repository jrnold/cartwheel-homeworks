"""Write ``latest.json`` and ``latest.md`` from a pipeline result."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from analysis.helpers import _state

from .run import CACHE_DIR


def _line(trace_id: str, entry: dict[str, Any]) -> str:
    summary = entry["summary"]
    return f"`{trace_id[:8]}` {summary['title']}"


def render_markdown(result: dict[str, Any]) -> str:
    """A readable cluster overview: backends first, then each cluster."""
    backends = result["backends"]
    traces = result["traces"]
    out = [
        "# Trace clusters",
        "",
        f"{result['n_traces']} traces from `{result['source']}`. "
        f"{len(result['clusters'])} clusters, {len(result['unclustered'])} unclustered.",
        "",
        "## How this was produced",
        "",
        f"- summarizer: {backends['summarizer']}",
        f"- embedder: {backends['embedder']}",
        f"- cluster labels: {backends['labeler']}",
        f"- reducer: {backends['reducer']}, min_cluster_size {result['params']['min_cluster_size']}",
    ]
    if backends["summary_fallbacks"]:
        out.append(
            f"- **{backends['summary_fallbacks']} summaries fell back to the "
            "heuristic summarizer after the model failed twice.**"
        )
    out += [
        "",
        "Clusters are a sampling aid. They say which traces resemble each other, "
        "not which ones failed. Read the traces before naming a failure.",
        "",
    ]
    for c in result["clusters"]:
        out += [f"## Cluster {c['cluster']} ({c['size']} traces): {c['label']}", ""]
        out += [f"- {_line(t, traces[t])}" for t in c["representatives"]]
        out.append("")
    if result["unclustered"]:
        out += [
            f"## Unclustered ({len(result['unclustered'])})",
            "",
            "No group explains these. Each is worth a look on its own.",
            "",
        ]
        out += [f"- {_line(t, traces[t])}" for t in result["unclustered"][:20]]
        if len(result["unclustered"]) > 20:
            out.append(f"- … and {len(result['unclustered']) - 20} more in latest.json")
        out.append("")
    if result["review_batch"]:
        out += [
            f"## Review batch ({len(result['review_batch'])})",
            "",
            "Spread across clusters, nearest the centre first. Do not count a "
            "trace toward more than one handout batch.",
            "",
        ]
        out += [f"- {_line(t, traces[t])}" for t in result["review_batch"]]
        out.append("")
    return "\n".join(out)


def write(result: dict[str, Any]) -> tuple[Path, Path]:
    """Write both files under ``analysis/state/trace_clusters/``."""
    json_path = _state.state_path(CACHE_DIR, "latest.json")
    md_path = _state.state_path(CACHE_DIR, "latest.md")
    _state.write_json(json_path, result)
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return json_path, md_path
