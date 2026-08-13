"""Deterministic row-level geometry for 2026 Huashu Cup problem A, Q1."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree


BOX_HALF = 5_000.0
ROD_RADIUS = 30.0
GAP = 1.8
AXIS_THRESHOLD = 2 * ROD_RADIUS + GAP


def segment_distance_certificates(
    p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return exact paired segment distances and minimizing parameters."""
    p0, p1, q0, q1 = [np.asarray(value, dtype=float) for value in (p0, p1, q0, q1)]
    u, v, w = p1 - p0, q1 - q0, p0 - q0
    a = np.einsum("ij,ij->i", u, u); b = np.einsum("ij,ij->i", u, v)
    c = np.einsum("ij,ij->i", v, v); d = np.einsum("ij,ij->i", u, w)
    e = np.einsum("ij,ij->i", v, w); det = a * c - b * b
    eps = 1e-14
    candidates: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    def add(s: np.ndarray, t: np.ndarray, valid: np.ndarray | None = None) -> None:
        s = np.clip(s, 0, 1); t = np.clip(t, 0, 1)
        delta = w + s[:, None] * u - t[:, None] * v
        squared = np.einsum("ij,ij->i", delta, delta)
        if valid is not None:
            squared = squared.copy(); squared[~valid] = np.inf
        candidates.append((squared, s, t))

    add(np.zeros_like(e), np.divide(e, c, out=np.zeros_like(e), where=c > eps))
    add(np.ones_like(e), np.divide(b + e, c, out=np.zeros_like(e), where=c > eps))
    add(np.divide(-d, a, out=np.zeros_like(d), where=a > eps), np.zeros_like(d))
    add(np.divide(b - d, a, out=np.zeros_like(d), where=a > eps), np.ones_like(d))
    s = np.divide(b * e - c * d, det, out=np.zeros_like(det), where=det > eps)
    t = np.divide(a * e - b * d, det, out=np.zeros_like(det), where=det > eps)
    add(s, t, (det > eps) & (s >= 0) & (s <= 1) & (t >= 0) & (t <= 1))
    squared = np.vstack([item[0] for item in candidates])
    winner = np.argmin(squared, axis=0); columns = np.arange(len(winner))
    best_s = np.vstack([item[1] for item in candidates])[winner, columns]
    best_t = np.vstack([item[2] for item in candidates])[winner, columns]
    return np.sqrt(np.maximum(0.0, squared[winner, columns])), best_s, best_t


def segment_distances(p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray) -> np.ndarray:
    return segment_distance_certificates(p0, p1, q0, q1)[0]


def face_contacts(starts: np.ndarray, ends: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    axis = ends - starts; lengths = np.linalg.norm(axis, axis=1)
    ux = np.divide(axis[:, 0], lengths, out=np.zeros_like(lengths), where=lengths > 0)
    radial_x = ROD_RADIUS * np.sqrt(np.maximum(0.0, 1 - ux * ux))
    xmin = np.minimum(starts[:, 0], ends[:, 0]) - radial_x
    xmax = np.maximum(starts[:, 0], ends[:, 0]) + radial_x
    return xmin <= -BOX_HALF + GAP, xmax >= BOX_HALF - GAP


def all_pair_edges(starts: np.ndarray, ends: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    i, j = np.triu_indices(len(starts), 1)
    distances = segment_distances(starts[i], ends[i], starts[j], ends[j])
    keep = distances <= AXIS_THRESHOLD + 1e-10
    return np.column_stack((i[keep], j[keep])).astype(np.int64), distances[keep]


def sampled_broadphase_edges(
    starts: np.ndarray, ends: np.ndarray, *, sample_spacing: float = 100.0
) -> tuple[np.ndarray, np.ndarray, int]:
    """Conservative non-periodic broad phase for the official row-level Q1 input."""
    if len(starts) < 2:
        return np.empty((0, 2), dtype=np.int64), np.empty(0), 0
    points, owners = [], []
    for idx, (start, end) in enumerate(zip(starts, ends)):
        count = max(2, int(np.ceil(np.linalg.norm(end - start) / sample_spacing)) + 1)
        t = np.linspace(0, 1, count)
        points.append(start + t[:, None] * (end - start))
        owners.append(np.full(count, idx, dtype=np.int64))
    cloud, owner = np.vstack(points), np.concatenate(owners)
    raw = cKDTree(cloud).query_pairs(AXIS_THRESHOLD + sample_spacing, output_type="ndarray")
    if not len(raw):
        return np.empty((0, 2), dtype=np.int64), np.empty(0), 0
    pairs = np.unique(np.sort(np.column_stack((owner[raw[:, 0]], owner[raw[:, 1]])), axis=1), axis=0)
    pairs = pairs[pairs[:, 0] != pairs[:, 1]]
    distances = segment_distances(starts[pairs[:, 0]], ends[pairs[:, 0]], starts[pairs[:, 1]], ends[pairs[:, 1]])
    keep = distances <= AXIS_THRESHOLD + 1e-10
    return pairs[keep], distances[keep], len(pairs)


@dataclass
class ConnectivityResult:
    connected: bool
    path: list[int | str]
    edge_count: int
    left_contacts: int
    right_contacts: int


def connectivity(starts: np.ndarray, ends: np.ndarray, *, use_broadphase: bool = False) -> ConnectivityResult:
    edges = sampled_broadphase_edges(starts, ends)[0] if use_broadphase else all_pair_edges(starts, ends)[0]
    left, right = face_contacts(starts, ends); n = len(starts); source, target = n, n + 1
    adjacency: list[list[int]] = [[] for _ in range(n + 2)]
    for a, b in edges:
        adjacency[int(a)].append(int(b)); adjacency[int(b)].append(int(a))
    for idx in np.flatnonzero(left): adjacency[source].append(int(idx)); adjacency[int(idx)].append(source)
    for idx in np.flatnonzero(right): adjacency[target].append(int(idx)); adjacency[int(idx)].append(target)
    queue = deque([source]); parent = {source: -1}
    while queue and target not in parent:
        node = queue.popleft()
        for neighbor in adjacency[node]:
            if neighbor not in parent:
                parent[neighbor] = node; queue.append(neighbor)
    path: list[int | str] = []
    if target in parent:
        node = target; raw = []
        while node != -1: raw.append(node); node = parent[node]
        raw.reverse()
        path = ["LEFT" if x == source else "RIGHT" if x == target else x + 1 for x in raw]
    return ConnectivityResult(target in parent, path, int(len(edges)), int(left.sum()), int(right.sum()))


def path_certificates(starts: np.ndarray, ends: np.ndarray, path: list[int | str]) -> list[dict]:
    certificates = []
    for left_node, right_node in zip(path[:-1], path[1:]):
        if isinstance(left_node, str) or isinstance(right_node, str):
            certificates.append({"from": left_node, "to": right_node, "type": "electrode_contact"})
            continue
        i, j = left_node - 1, right_node - 1
        distance, s, t = segment_distance_certificates(
            starts[[i]], ends[[i]], starts[[j]], ends[[j]]
        )
        interior = bool(1e-9 < s[0] < 1 - 1e-9 and 1e-9 < t[0] < 1 - 1e-9)
        certificates.append({
            "from": left_node, "to": right_node, "type": "interior_side_to_side" if interior else "capsule_only_unverified",
            "axis_distance_nm": float(distance[0]), "surface_gap_nm": float(max(0, distance[0] - 2 * ROD_RADIUS)),
            "segment_parameters": [float(s[0]), float(t[0])],
            "flat_cylinder_sufficient": bool(interior and distance[0] <= AXIS_THRESHOLD),
        })
    return certificates
