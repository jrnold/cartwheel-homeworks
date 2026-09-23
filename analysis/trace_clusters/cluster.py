"""Reduce embeddings and cluster them with HDBSCAN.

HDBSCAN needs no cluster count and leaves outliers unassigned (label -1), which
suits a review sample: an outlier is a trace no group explains, so it is worth a
human's time in its own right. Density clustering degrades in hundreds of
dimensions, so vectors are reduced first. UMAP is the default because it
separates clusters of summary embeddings better than PCA: on the 267-trace
review pool it left 1 trace unclustered where PCA left 47. PCA remains as
``--reducer pca`` for a deterministic, numba-free run.

The 2-D projection for plotting is separate from the clustering reduction:
``projection`` picks it, and defaults to the reducer. The trace map uses UMAP
for both, as two fits: many components packed tightly for HDBSCAN, and two
components spread out for the scatter.

``extra`` vectors (the trace map's policies, stores, tools and spec items) are
placed into the fitted 2-D layout with ``transform`` and never clustered, so
they cannot move a trace or change a cluster.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np


@dataclass
class ClusterResult:
    labels: np.ndarray  # one int per trace, -1 = unclustered
    coords: np.ndarray  # n x 2 projection for plotting
    distance: np.ndarray  # distance of each trace to its cluster centroid
    reducer: str
    extra_coords: np.ndarray | None = None  # m x 2 for ``extra``; never clustered


def _normalize(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.where(norms == 0, 1, norms)


def _reduce(x: np.ndarray, reducer: str, n_components: int, seed: int) -> np.ndarray:
    n_components = max(1, min(n_components, x.shape[0] - 1, x.shape[1]))
    if reducer == "none":
        return x
    if reducer == "pca":
        from sklearn.decomposition import PCA

        return PCA(n_components=n_components, random_state=seed).fit_transform(x)
    if reducer == "umap":
        import umap

        return umap.UMAP(
            n_components=n_components,
            n_neighbors=min(15, x.shape[0] - 1),
            min_dist=0.0,  # pack neighbors tightly; density clustering prefers it
            metric="cosine",
            random_state=seed,
        ).fit_transform(x)
    raise ValueError(f"unknown reducer: {reducer!r}")


def _project_2d(
    x: np.ndarray,
    reducer: str,
    seed: int,
    *,
    extra: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray | None]:
    """2-D layout fitted on ``x``, plus ``extra`` placed into it."""
    if x.shape[1] < 2 or x.shape[0] < 3:
        return np.zeros((x.shape[0], 2)), None if extra is None else np.zeros((len(extra), 2))
    if reducer == "umap":
        import umap

        model = umap.UMAP(
            n_components=2,
            n_neighbors=min(15, x.shape[0] - 1),
            min_dist=0.1,  # spread points so the scatter stays readable
            metric="cosine",
            random_state=seed,
        )
        coords = model.fit_transform(x)
        return coords, None if extra is None else np.asarray(model.transform(extra))
    from sklearn.decomposition import PCA

    pca = PCA(n_components=2, random_state=seed)
    coords = pca.fit_transform(x)
    return coords, None if extra is None else pca.transform(extra)


def cluster(
    vectors: np.ndarray,
    *,
    reducer: str = "umap",
    n_components: int = 15,
    min_cluster_size: int = 5,
    min_samples: int | None = None,
    seed: int = 0,
    projection: str | None = None,
    extra: np.ndarray | None = None,
) -> ClusterResult:
    """Cluster ``vectors`` (one row per trace) and lay them out in 2-D.

    ``extra`` rows share the layout but not the clustering: they are placed
    with the fitted projection's ``transform`` after everything else is done.

    Too few traces to form even one cluster of ``min_cluster_size`` returns
    everything as unclustered instead of raising, so a small export still runs.
    """
    from sklearn.cluster import HDBSCAN

    n = vectors.shape[0]
    x = _normalize(np.asarray(vectors, dtype=float))
    ex = None if extra is None else _normalize(np.asarray(extra, dtype=float))
    if n < max(min_cluster_size, 3):
        coords, extra_coords = _project_2d(x, "pca", seed, extra=ex)
        return ClusterResult(np.full(n, -1), coords, np.zeros(n), reducer, extra_coords)
    reduced = _reduce(x, reducer, n_components, seed)
    with warnings.catch_warnings():
        # scikit-learn 1.9 warns that HDBSCAN's `copy` default changes in 1.10.
        # The parameter does not exist on the 1.3 floor, so it cannot be set.
        warnings.simplefilter("ignore", FutureWarning)
        labels = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            cluster_selection_method="eom",
        ).fit_predict(reduced)

    distance = np.zeros(n)
    for label in set(labels.tolist()) - {-1}:
        members = labels == label
        centroid = reduced[members].mean(axis=0)
        distance[members] = np.linalg.norm(reduced[members] - centroid, axis=1)
    layout, extra_coords = _project_2d(x, projection or reducer, seed, extra=ex)
    return ClusterResult(labels, layout, distance, reducer, extra_coords)


def representatives(result: ClusterResult, per_cluster: int = 3) -> dict[int, list[int]]:
    """Row indexes closest to each cluster's centroid, nearest first."""
    out: dict[int, list[int]] = {}
    for label in sorted(set(result.labels.tolist()) - {-1}):
        members = np.flatnonzero(result.labels == label)
        order = members[np.argsort(result.distance[members], kind="stable")]
        out[label] = [int(i) for i in order[:per_cluster]]
    return out


def pick(result: ClusterResult, total: int) -> list[int]:
    """``total`` row indexes spread across clusters, largest cluster first.

    Round-robin by nearness to the centroid, so one large cluster cannot take
    the whole batch. Unclustered traces are excluded: they are outliers, not
    representatives, and belong in a separate look.
    """
    sizes = {
        label: int((result.labels == label).sum())
        for label in set(result.labels.tolist()) - {-1}
    }
    queues = {
        label: list(rows)
        for label, rows in representatives(result, per_cluster=max(sizes.values(), default=0)).items()
    }
    picked: list[int] = []
    while len(picked) < total and any(queues.values()):
        for label in sorted(queues, key=lambda k: (-sizes[k], k)):
            if queues[label] and len(picked) < total:
                picked.append(queues[label].pop(0))
    return picked
