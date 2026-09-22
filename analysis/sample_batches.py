"""Select the Homework 4 review batches and record them in the manifest.

Part B asks for four batches drawn by different methods, with no trace counted
twice. This module draws them and appends each one to
``analysis/state/sample_manifest.json``.

Every pick comes from the starter selector in ``analysis.helpers.selection``:
``strategy="random"`` for the uniform batches and ``strategy="diversity"`` for
the cluster representatives, which clusters the five-number feature vector
(``turn_count``, ``tool_call_count``, ``distinct_tools``, ``has_retrieval``,
``tokens``) with the package's own deterministic k-means.

The embedding pipeline under ``analysis/trace_clusters/`` is deliberately not
used here and must not be imported. It groups traces by what the conversation
*means*; the starter selector groups them by conversation *shape*. Keeping the
sample on the starter selector alone means the manifest can be reproduced from
committed code with no model, no key and no daemon, and it keeps the two
methods separable when their results are compared later.

The manifest is append-only. Batch 3 (depth searches) and batch 4 (the final
uniform batch) are drawn after the taxonomy exists, and batch 4 is only a
stability check if it can be shown to have been selected last, so a rerun must
never quietly rewrite an earlier batch.

Usage::

    uv run python -m analysis.sample_batches --dry-run
    uv run python -m analysis.sample_batches
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from typing import Any

from analysis.helpers import _state, selection

POOL_FILE = "review_pool.json"
MANIFEST_FILE = "sample_manifest.json"

# The starter selector's default. Recorded per batch so a rerun reproduces it.
SEED = 7

# Batch 2 is 10 per role rather than proportional to the pool (which is 172
# shopper / 61 merchant / 34 support). Permission checks, refund thresholds and
# approval routing all key on role, so an even split buys more coverage of the
# rules than a proportional draw, which would have spent 19 of 30 slots on
# shoppers. The uniform batches carry the pool's real composition.
ROLE_STRATA = ("shopper", "merchant", "support")
PER_ROLE = 10

_REPRESENTATIVE = re.compile(r"^cluster \d+ representative$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_pool() -> list[dict[str, Any]]:
    """Load the enriched review pool."""
    pool = _state.read_json(_state.state_path(POOL_FILE), default=None)
    if not isinstance(pool, list) or not pool:
        raise ValueError(f"{POOL_FILE} is missing or empty; rebuild the review pool")
    return pool


def selector_records(pool: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Shape pool rows for ``selection.select``.

    The pool is not passed through ``selection.load_traces`` because
    ``normalize_traces`` merges traces that share a ``scenario_id`` into one
    conversation. Cartwheel writes one trace per user turn and the review
    interface reviews turns, so merging here would make the manifest name units
    that the interface never shows. The pool already carries the feature vector
    the selector needs, under ``langfuse.features``.
    """
    records = []
    for row in pool:
        features = (row.get("langfuse") or {}).get("features") or {}
        missing = set(selection._FEATURES) - set(features)
        if missing:
            raise ValueError(f"{row['trace_id']} is missing features: {sorted(missing)}")
        records.append({"id": row["trace_id"], "features": features})
    return records


def uniform_batch(
    records: list[dict[str, Any]], k: int, exclude: set[str], seed: int = SEED
) -> list[dict[str, str]]:
    """``k`` uniformly sampled traces."""
    return selection.select(records, k=k, strategy="random", exclude_ids=exclude, seed=seed)


def representative_batch(
    records: list[dict[str, Any]], k: int, exclude: set[str], seed: int = SEED
) -> list[dict[str, str]]:
    """``k`` cluster representatives, with the random picks discarded.

    ``strategy="diversity"`` returns two thirds representatives and one third
    random, because clustering never captures every dimension. The uniform
    batch already covers that, so asking for ``ceil(k * 3 / 2)`` and keeping
    only the representatives yields ``k`` pure ones without reimplementing the
    selector's clustering.
    """
    request = math.ceil(k * 3 / 2)
    picks = selection.select(
        records, k=request, strategy="diversity", exclude_ids=exclude, seed=seed
    )
    reps = [p for p in picks if _REPRESENTATIVE.match(p["reason"])]
    if len(reps) < k:
        raise ValueError(
            f"diversity selection returned {len(reps)} representatives, needed {k}; "
            "the pool may be too small or too uniform to form that many clusters"
        )
    return reps[:k]


def stratified_batch(
    pool: list[dict[str, Any]],
    records: list[dict[str, Any]],
    per_role: int,
    exclude: set[str],
    seed: int = SEED,
) -> list[dict[str, str]]:
    """``per_role`` uniform picks inside each role.

    Stratification is applied by restricting the selector's input to one role
    at a time, so the picks within a stratum still come from the starter
    selector rather than a second sampler written here.
    """
    role_by_id = {row["trace_id"]: (row.get("scenario") or {}).get("role") for row in pool}
    picks: list[dict[str, str]] = []
    taken = set(exclude)
    for role in ROLE_STRATA:
        stratum = [r for r in records if role_by_id.get(r["id"]) == role]
        drawn = selection.select(
            stratum, k=per_role, strategy="random", exclude_ids=taken, seed=seed
        )
        if len(drawn) < per_role:
            raise ValueError(
                f"role {role!r} has {len(drawn)} selectable traces, needed {per_role}"
            )
        for pick in drawn:
            picks.append({**pick, "reason": f"uniform within role={role}", "role": role})
            taken.add(pick["trace_id"])
    return picks


def read_manifest() -> dict[str, Any]:
    manifest = _state.read_json(_state.state_path(MANIFEST_FILE), default=None)
    if manifest is None:
        return {"schema": 1, "batches": []}
    if not isinstance(manifest, dict) or not isinstance(manifest.get("batches"), list):
        raise ValueError(f"{MANIFEST_FILE} exists but is not a batched manifest")
    return manifest


def add_batch(manifest: dict[str, Any], batch: dict[str, Any]) -> dict[str, Any]:
    """Append ``batch``, refusing a name the manifest already carries."""
    existing = {b["name"] for b in manifest["batches"]}
    if batch["name"] in existing:
        raise ValueError(
            f"batch {batch['name']!r} is already in the manifest. Selecting it "
            "again would replace a record of what was reviewed; edit the "
            "manifest by hand if that is really intended."
        )
    manifest["batches"].append(batch)
    return manifest


def _batch(name: str, method: str, picks: list[dict[str, str]], **extra: Any) -> dict[str, Any]:
    return {
        "name": name,
        "method": method,
        "seed": SEED,
        "selected_at": _now(),
        "size": len(picks),
        "picks": picks,
        **extra,
    }


def select_batches(pool: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Draw batches 1 to 3. Batches 4 and 5 are drawn later, by hand."""
    records = selector_records(pool)
    taken: set[str] = set()
    batches = []

    uniform = uniform_batch(records, k=15, exclude=taken)
    taken.update(p["trace_id"] for p in uniform)
    batches.append(
        _batch("1-uniform", "selection.select(strategy='random')", uniform)
    )

    reps = representative_batch(records, k=15, exclude=taken)
    taken.update(p["trace_id"] for p in reps)
    batches.append(
        _batch(
            "2-cluster-representatives",
            "selection.select(strategy='diversity'), random picks discarded",
            reps,
            requested=math.ceil(15 * 3 / 2),
        )
    )

    stratified = stratified_batch(pool, records, per_role=PER_ROLE, exclude=taken)
    taken.update(p["trace_id"] for p in stratified)
    batches.append(
        _batch(
            "3-role-stratified",
            "selection.select(strategy='random') within each role",
            stratified,
            dimension="scenario.role",
            per_stratum=PER_ROLE,
            strata=list(ROLE_STRATA),
            chosen_before_outcomes=True,
        )
    )

    # The handout forbids counting one trace toward two batches, and a
    # duplicate would also inflate the reviewed total.
    ids = [p["trace_id"] for b in batches for p in b["picks"]]
    if len(ids) != len(set(ids)):
        raise AssertionError("batches overlap; a trace was selected twice")
    return batches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true", help="print the batches without writing"
    )
    args = parser.parse_args()

    pool = load_pool()
    batches = select_batches(pool)

    for batch in batches:
        print(f"{batch['name']}: {batch['size']} traces via {batch['method']}")
        for pick in batch["picks"]:
            print(f"  {pick['trace_id']}  {pick['reason']}")

    if args.dry_run:
        print("\ndry run: nothing written")
        return

    manifest = read_manifest()
    manifest["pool"] = POOL_FILE
    manifest["pool_size"] = len(pool)
    for batch in batches:
        add_batch(manifest, batch)
    path = _state.state_path(MANIFEST_FILE)
    _state.write_json(path, manifest)
    total = sum(b["size"] for b in manifest["batches"])
    print(f"\nwrote {path} ({len(manifest['batches'])} batches, {total} traces)")


if __name__ == "__main__":  # pragma: no cover
    main()
