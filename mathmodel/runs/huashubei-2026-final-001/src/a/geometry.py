# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Geometry and graph kernel for 2026 Huashu Cup problem A.

The official material A is a flat-ended cylinder. The contest-scale primary
model uses the standard axis-segment surrogate: two radius-r cylinders are
connected when their axis distance is at most 2r+gap. Boundary-wrapped axis
pieces are separate graph nodes, matching the fragment structure in attachment 1.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.spatial import cKDTree


BOX_SIDE = 10_000.0
BOX_HALF = BOX_SIDE / 2
ROD_LENGTH = 5_000.0
ROD_RADIUS = 30.0
GAP = 1.8
AXIS_THRESHOLD = 2 * ROD_RADIUS + GAP


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = np.arange(n, dtype=np.int64)
        self.rank = np.zeros(n, dtype=np.int8)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = int(self.parent[x])
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)


def segment_distances(
    p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray
) -> np.ndarray:
    """Exact Euclidean distances between paired finite axis segments.

    The convex quadratic over [0,1]^2 is solved by testing its valid interior
    stationary point and the four box boundaries. Inputs have shape (m, 3).
    """
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)
    u, v, w = p1 - p0, q1 - q0, p0 - q0
    a = np.einsum("ij,ij->i", u, u)
    b = np.einsum("ij,ij->i", u, v)
    c = np.einsum("ij,ij->i", v, v)
    d = np.einsum("ij,ij->i", u, w)
    e = np.einsum("ij,ij->i", v, w)
    eps = 1e-14

    candidates: list[np.ndarray] = []

    def squared(s: np.ndarray, t: np.ndarray) -> np.ndarray:
        delta = w + s[:, None] * u - t[:, None] * v
        return np.einsum("ij,ij->i", delta, delta)

    t = np.divide(e, c, out=np.zeros_like(e), where=c > eps)
    candidates.append(squared(np.zeros_like(t), np.clip(t, 0, 1)))
    t = np.divide(b + e, c, out=np.zeros_like(e), where=c > eps)
    candidates.append(squared(np.ones_like(t), np.clip(t, 0, 1)))
    s = np.divide(-d, a, out=np.zeros_like(d), where=a > eps)
    candidates.append(squared(np.clip(s, 0, 1), np.zeros_like(s)))
    s = np.divide(b - d, a, out=np.zeros_like(d), where=a > eps)
    candidates.append(squared(np.clip(s, 0, 1), np.ones_like(s)))

    det = a * c - b * b
    s = np.divide(b * e - c * d, det, out=np.zeros_like(det), where=det > eps)
    t = np.divide(a * e - b * d, det, out=np.zeros_like(det), where=det > eps)
    valid = (det > eps) & (s >= 0) & (s <= 1) & (t >= 0) & (t <= 1)
    interior = squared(s, t)
    interior[~valid] = np.inf
    candidates.append(interior)
    return np.sqrt(np.maximum(0.0, np.min(np.vstack(candidates), axis=0)))


def split_wrapped_axis(center: np.ndarray, direction: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    """Cut an unwrapped 5000 nm axis at box planes and translate pieces inside."""
    center = np.asarray(center, dtype=float)
    direction = np.asarray(direction, dtype=float)
    direction = direction / np.linalg.norm(direction)
    start = center - 0.5 * ROD_LENGTH * direction
    delta = ROD_LENGTH * direction
    cuts = [0.0, 1.0]
    for axis in range(3):
        if abs(delta[axis]) < 1e-14:
            continue
        low, high = sorted((start[axis], start[axis] + delta[axis]))
        k0 = int(np.floor((low + BOX_HALF) / BOX_SIDE)) - 1
        k1 = int(np.ceil((high + BOX_HALF) / BOX_SIDE)) + 1
        for k in range(k0, k1 + 1):
            plane = -BOX_HALF + k * BOX_SIDE
            t = (plane - start[axis]) / delta[axis]
            if 1e-12 < t < 1 - 1e-12:
                cuts.append(float(t))
    cuts = sorted(set(round(value, 14) for value in cuts))
    pieces: list[tuple[np.ndarray, np.ndarray]] = []
    for ta, tb in zip(cuts[:-1], cuts[1:]):
        a = start + ta * delta
        b = start + tb * delta
        midpoint = (a + b) / 2
        shift = -BOX_SIDE * np.floor((midpoint + BOX_HALF) / BOX_SIDE)
        a, b = a + shift, b + shift
        a = np.clip(a, -BOX_HALF, BOX_HALF)
        b = np.clip(b, -BOX_HALF, BOX_HALF)
        if np.linalg.norm(b - a) > 1e-9:
            pieces.append((a, b))
    total = sum(np.linalg.norm(b - a) for a, b in pieces)
    if not np.isclose(total, ROD_LENGTH, atol=1e-6):
        raise AssertionError(f"wrapped length not conserved: {total}")
    return pieces


def generate_fragments(
    centers: np.ndarray, directions: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    starts: list[np.ndarray] = []
    ends: list[np.ndarray] = []
    rod_ids: list[int] = []
    for rod_id, (center, direction) in enumerate(zip(centers, directions)):
        for start, end in split_wrapped_axis(center, direction):
            starts.append(start)
            ends.append(end)
            rod_ids.append(rod_id)
    return (
        np.asarray(starts, dtype=float).reshape(-1, 3),
        np.asarray(ends, dtype=float).reshape(-1, 3),
        np.asarray(rod_ids, dtype=np.int64),
    )


def face_contacts(starts: np.ndarray, ends: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(starts) == 0:
        return np.zeros(0, dtype=bool), np.zeros(0, dtype=bool)
    axis = ends - starts
    lengths = np.linalg.norm(axis, axis=1)
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


def infer_periodic_identity_edges(
    starts: np.ndarray,
    ends: np.ndarray,
    *,
    seam_magnitudes: tuple[float, ...] = (500.0, 5000.0),
    tolerance: float = 1e-6,
) -> np.ndarray:
    """Infer attachment fragments belonging to one wrapped conductor.

    Official rows omit a rod identifier. Exact endpoint matches across opposite
    seam coordinates are therefore used as a deterministic identity key.
    """
    endpoints = np.stack((starts, ends), axis=1)
    edges: set[tuple[int, int]] = set()
    for i in range(len(starts)):
        for j in range(i):
            matched = False
            for pi in endpoints[i]:
                for pj in endpoints[j]:
                    for axis in range(3):
                        others = [value for value in range(3) if value != axis]
                        if not np.allclose(pi[others], pj[others], atol=tolerance, rtol=0):
                            continue
                        for magnitude in seam_magnitudes:
                            if (
                                np.isclose(pi[axis], magnitude, atol=tolerance)
                                and np.isclose(pj[axis], -magnitude, atol=tolerance)
                            ) or (
                                np.isclose(pi[axis], -magnitude, atol=tolerance)
                                and np.isclose(pj[axis], magnitude, atol=tolerance)
                            ):
                                edges.add((j, i))
                                matched = True
                                break
                        if matched:
                            break
                    if matched:
                        break
                if matched:
                    break
    return np.asarray(sorted(edges), dtype=np.int64).reshape(-1, 2)


def sampled_broadphase_edges(
    starts: np.ndarray,
    ends: np.ndarray,
    *,
    sample_spacing: float = 100.0,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Conservative sampled-point broad phase followed by exact axis distance."""
    if len(starts) < 2:
        return np.empty((0, 2), dtype=np.int64), np.empty(0), 0
    points: list[np.ndarray] = []
    owners: list[np.ndarray] = []
    for idx, (start, end) in enumerate(zip(starts, ends)):
        length = float(np.linalg.norm(end - start))
        count = max(2, int(np.ceil(length / sample_spacing)) + 1)
        t = np.linspace(0.0, 1.0, count)
        points.append(start + t[:, None] * (end - start))
        owners.append(np.full(count, idx, dtype=np.int64))
    cloud = np.vstack(points)
    owner = np.concatenate(owners)
    raw = cKDTree(cloud).query_pairs(AXIS_THRESHOLD + sample_spacing, output_type="ndarray")
    if len(raw) == 0:
        return np.empty((0, 2), dtype=np.int64), np.empty(0), 0
    pairs = np.sort(np.column_stack((owner[raw[:, 0]], owner[raw[:, 1]])), axis=1)
    pairs = pairs[pairs[:, 0] != pairs[:, 1]]
    if len(pairs) == 0:
        return np.empty((0, 2), dtype=np.int64), np.empty(0), len(raw)
    pairs = np.unique(pairs, axis=0)
    distances = segment_distances(
        starts[pairs[:, 0]], ends[pairs[:, 0]], starts[pairs[:, 1]], ends[pairs[:, 1]]
    )
    keep = distances <= AXIS_THRESHOLD + 1e-10
    return pairs[keep], distances[keep], len(pairs)


@dataclass
class ConnectivityResult:
    connected: bool
    path: list[int | str]
    edge_count: int
    left_contacts: int
    right_contacts: int
    minimum_margin_nm: float | None


def connectivity(
    starts: np.ndarray,
    ends: np.ndarray,
    *,
    use_broadphase: bool = False,
    identity_edges: np.ndarray | None = None,
) -> ConnectivityResult:
    edges, distances = (
        sampled_broadphase_edges(starts, ends)[:2]
        if use_broadphase
        else all_pair_edges(starts, ends)
    )
    left, right = face_contacts(starts, ends)
    n = len(starts)
    source, target = n, n + 1
    adjacency: list[list[int]] = [[] for _ in range(n + 2)]
    for a, b in edges:
        adjacency[int(a)].append(int(b))
        adjacency[int(b)].append(int(a))
    if identity_edges is not None:
        for a, b in identity_edges:
            adjacency[int(a)].append(int(b))
            adjacency[int(b)].append(int(a))
    for idx in np.flatnonzero(left):
        adjacency[source].append(int(idx)); adjacency[int(idx)].append(source)
    for idx in np.flatnonzero(right):
        adjacency[target].append(int(idx)); adjacency[int(idx)].append(target)
    queue = deque([source])
    parent = {source: -1}
    while queue and target not in parent:
        node = queue.popleft()
        for neighbor in adjacency[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    path: list[int | str] = []
    if target in parent:
        node = target
        raw: list[int] = []
        while node != -1:
            raw.append(node)
            node = parent[node]
        raw.reverse()
        path = ["LEFT" if x == source else "RIGHT" if x == target else x + 1 for x in raw]
    margin = float(np.min(np.abs(distances - AXIS_THRESHOLD))) if len(distances) else None
    return ConnectivityResult(
        connected=target in parent,
        path=path,
        edge_count=int(len(edges) + (0 if identity_edges is None else len(identity_edges))),
        left_contacts=int(left.sum()),
        right_contacts=int(right.sum()),
        minimum_margin_nm=margin,
    )


def critical_prefix(
    centers: np.ndarray,
    directions: np.ndarray,
) -> tuple[int, dict[str, int]]:
    """Earliest original-rod prefix that spans, or max_rods+1 if none."""
    starts, ends, rod_ids = generate_fragments(centers, directions)
    edges, _, broadphase_pairs = sampled_broadphase_edges(starts, ends)
    left, right = face_contacts(starts, ends)
    n_frag = len(starts)
    source, target = n_frag, n_frag + 1
    uf = UnionFind(n_frag + 2)
    events: list[list[tuple[int, int]]] = [[] for _ in range(len(centers))]
    for a, b in edges:
        activation = int(max(rod_ids[a], rod_ids[b]))
        events[activation].append((int(a), int(b)))
    fragment_by_rod: list[list[int]] = [[] for _ in range(len(centers))]
    for fragment, rod in enumerate(rod_ids):
        fragment_by_rod[int(rod)].append(fragment)
    radial_x = ROD_RADIUS * np.sqrt(np.maximum(0.0, 1 - directions[:, 0] ** 2))
    periodic_x_bridge = (
        np.abs(centers[:, 0]) + 0.5 * ROD_LENGTH * np.abs(directions[:, 0]) + radial_x
        >= BOX_HALF
    )
    for rod in range(len(centers)):
        for fragment in fragment_by_rod[rod]:
            if left[fragment]:
                uf.union(fragment, source)
            if right[fragment]:
                uf.union(fragment, target)
        fragments = fragment_by_rod[rod]
        for fragment in fragments[1:]:
            uf.union(fragments[0], fragment)
        if periodic_x_bridge[rod] and fragments:
            uf.union(fragments[0], source)
            uf.union(fragments[0], target)
        for a, b in events[rod]:
            uf.union(a, b)
        if uf.connected(source, target):
            return rod + 1, {
                "fragments": n_frag,
                "conductive_edges": int(len(edges)),
                "broadphase_pairs": int(broadphase_pairs),
            }
    return len(centers) + 1, {
        "fragments": n_frag,
        "conductive_edges": int(len(edges)),
        "broadphase_pairs": int(broadphase_pairs),
    }


def isotropic_directions(rng: np.random.Generator, n: int) -> np.ndarray:
    directions = rng.normal(size=(n, 3))
    return directions / np.linalg.norm(directions, axis=1)[:, None]


def seeded_a_configuration(seed: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate prefix-stable centers and directions from independent substreams."""
    center_seed, direction_seed = np.random.SeedSequence(seed).spawn(2)
    center_rng = np.random.default_rng(center_seed)
    direction_rng = np.random.default_rng(direction_seed)
    centers = center_rng.uniform(-BOX_HALF, BOX_HALF, size=(n, 3))
    directions = isotropic_directions(direction_rng, n)
    return centers, directions
