"""Parse ``SPEC.md`` into addressable requirements.

The review interface shows the reviewer the slice of the specification that
bears on the trace in front of them. Two consumers need the specification in
structured form:

  - the mechanical floor in :mod:`spec_relevance`, which attaches ``TOOL-n``
    from the tools that actually ran, and
  - the requirement-id validator, which drops any id an LLM returns that does
    not exist in the specification.

The file is small (about 115 lines) and the LLM call receives it verbatim, so
this module exists for addressing and validation, not for summarization.

Requirement ids come from two places in the Markdown. Most are marked inline
as ``**RESP-1.**``; the ten tool requirements are table rows in section 4. A
tool requirement also carries its success and failure contract from the second
table, because the contract is what tells a reviewer whether a given
``ok: false`` result was the tool behaving correctly.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_PATH = REPO_ROOT / "SPEC.md"

# Inline requirement markers: **PURPOSE-1.**, **AUTH-1.**, **RESP-3.** ...
_MARKER = re.compile(r"\*\*([A-Z]+-\d+)\.\*\*")
# Section headings, which also terminate a requirement's body.
_HEADING = re.compile(r"^#{2,4}\s+(.*)$")
# Rows of the tools table: | TOOL-7 | `issue_refund` | ... |
_TOOL_ROW = re.compile(r"^\|\s*(TOOL-\d+)\s*\|\s*`([a-z_]+)`\s*\|(.*)\|\s*$")
# Rows of the success/failure contract table, keyed by tool name.
_CONTRACT_ROW = re.compile(r"^\|\s*`([a-z_]+)`\s*\|(.+?)\|(.+?)\|\s*$")
# The AUTH-1 access matrix header, which fixes the column order.
_MATRIX_HEADER = re.compile(r"^\|\s*Capability\s*\|", re.IGNORECASE)
_TABLE_DIVIDER = re.compile(r"^\|[\s\-|]+\|$")


@dataclass
class Requirement:
    """One addressable requirement from ``SPEC.md``."""

    id: str
    section: str
    text: str
    # Set only for TOOL-n: the tool this requirement governs, plus the
    # success/failure contract that decides whether a result is correct.
    tool: str | None = None
    contract: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "section": self.section,
            "text": self.text,
        }
        if self.tool:
            out["tool"] = self.tool
            out["contract"] = self.contract
        return out


@dataclass
class SpecIndex:
    """The parsed specification plus the hash that versions it.

    ``digest`` is part of every relevance cache key. A ``SPEC.md`` revision
    (which Homework 4 expects) therefore invalidates the cached attachments
    instead of leaving the panel quietly describing the old requirements.
    """

    raw: str
    digest: str
    requirements: dict[str, Requirement]
    # AUTH-1's access matrix, one entry per capability row.
    access_matrix: list[dict[str, str]] = field(default_factory=list)

    @property
    def ids(self) -> set[str]:
        return set(self.requirements)

    def by_tool(self, tool: str) -> Requirement | None:
        for req in self.requirements.values():
            if req.tool == tool:
                return req
        return None

    def get(self, req_id: str) -> Requirement | None:
        return self.requirements.get(req_id)

    def access_rows(self, role: str | None) -> list[dict[str, str]]:
        """The access matrix narrowed to one caller's column.

        AUTH-1 applies to every trace, so rendering the full four-column table
        each time turns it into wallpaper the reviewer stops reading. The
        caller's own column is the part that decides whether a tool result was
        correct, so the panel shows that and drops the rest.
        """
        if not role:
            return []
        key = role.strip().lower()
        out: list[dict[str, str]] = []
        for row in self.access_matrix:
            if key in row:
                out.append({"capability": row["capability"], "permission": row[key]})
        return out


def _contracts(lines: list[str]) -> dict[str, dict[str, str]]:
    """Map tool name -> its success and failure contract.

    Skips the header and separator rows by requiring the first cell to be a
    backticked identifier, which the header row ("Tool") is not.
    """
    out: dict[str, dict[str, str]] = {}
    for line in lines:
        match = _CONTRACT_ROW.match(line.strip())
        if not match:
            continue
        tool, success, failure = match.groups()
        out[tool] = {
            "on_success": success.strip(),
            "on_failure": failure.strip(),
        }
    return out


def _inline_requirements(lines: list[str]) -> dict[str, Requirement]:
    """Collect requirements marked ``**ID.**`` in the prose.

    A requirement's body runs from its marker to the next marker or the next
    heading, whichever comes first. That rule is what pulls the access matrix
    into AUTH-1 and the bullet lists into SCOPE-1, rather than truncating each
    at its first line.
    """
    out: dict[str, Requirement] = {}
    section = ""
    open_id: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal open_id, buffer
        if open_id:
            out[open_id] = Requirement(
                id=open_id,
                section=section,
                text="\n".join(buffer).strip(),
            )
        open_id, buffer = None, []

    for line in lines:
        heading = _HEADING.match(line)
        if heading:
            flush()
            section = heading.group(1).strip()
            continue
        marker = _MARKER.search(line)
        if marker:
            flush()
            open_id = marker.group(1)
            # Keep the marker in the text so the panel can render the id in
            # the same bold form the specification uses.
            buffer = [line.rstrip()]
            continue
        if open_id is not None:
            buffer.append(line.rstrip())
    flush()
    return out


def _tool_requirements(lines: list[str], section: str) -> dict[str, Requirement]:
    """Collect TOOL-n from the tools table, attaching each tool's contract."""
    contracts = _contracts(lines)
    out: dict[str, Requirement] = {}
    for line in lines:
        match = _TOOL_ROW.match(line.strip())
        if not match:
            continue
        req_id, tool, rest = match.groups()
        cells = [cell.strip() for cell in rest.split("|")]
        # Columns after the tool name: inputs, side effects, risk.
        inputs = cells[0] if cells else ""
        side_effects = cells[1] if len(cells) > 1 else ""
        risk = cells[2] if len(cells) > 2 else ""
        text = (
            f"**{req_id}.** `{tool}` — inputs: {inputs}. "
            f"Side effects: {side_effects}. Risk: {risk}."
        )
        out[req_id] = Requirement(
            id=req_id,
            section=section,
            text=text,
            tool=tool,
            contract=contracts.get(tool, {}),
        )
    return out


def _access_matrix(lines: list[str]) -> list[dict[str, str]]:
    """Parse the AUTH-1 capability table into one dict per row.

    Column names come from the header rather than being hardcoded, so a role
    added to the specification appears without a code change here.
    """
    out: list[dict[str, str]] = []
    columns: list[str] = []
    for line in lines:
        stripped = line.strip()
        if _MATRIX_HEADER.match(stripped):
            columns = [cell.strip().lower() for cell in stripped.strip("|").split("|")]
            continue
        if not columns:
            continue
        if _TABLE_DIVIDER.match(stripped):
            continue
        if not stripped.startswith("|"):
            # The table ended; stop rather than picking up a later table.
            break
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != len(columns):
            break
        out.append(dict(zip(columns, cells, strict=True)))
    return out


def load_spec(path: Path | None = None) -> SpecIndex:
    """Parse ``SPEC.md`` into a :class:`SpecIndex`."""
    spec_path = path or SPEC_PATH
    raw = spec_path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    requirements = _inline_requirements(lines)
    requirements.update(_tool_requirements(lines, section="4. Tools"))

    return SpecIndex(
        raw=raw,
        digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16],
        requirements=requirements,
        access_matrix=_access_matrix(lines),
    )


if __name__ == "__main__":  # pragma: no cover - manual inspection
    index = load_spec()
    print(f"SPEC.md digest {index.digest}: {len(index.requirements)} requirements")
    for req in sorted(index.requirements.values(), key=lambda r: (r.section, r.id)):
        head = req.text.replace("\n", " ")[:88]
        print(f"  {req.id:12s} [{req.section[:22]:22s}] {head}")
