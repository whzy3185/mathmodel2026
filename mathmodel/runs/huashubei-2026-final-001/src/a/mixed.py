# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Mixed A-cylinder/B-sphere graph kernel for problem A, question 4."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

from geometry import (
    AXIS_THRESHOLD,
    BOX_HALF,
    GAP,
    ROD_RADIUS,
    UnionFind,
    face_contacts,
    generate_fragments,
    sampled_broadphase_edges,
    segment_distances,
    BOX_SIDE,
)


SPHERE_RADIUS = 200.0
A_B_THRESHOLD = ROD_RADIUS + SPHERE_RADIUS + GAP
B_B_THRESHOLD = 2 * SPHERE_RADIUS + GAP


def point_segment_distances(points: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    delta = ends - starts
    denom = np.einsum("ij,ij->i", delta, delta)
    t = np.divide(
        np.einsum("ij,ij->i", points - starts, delta),
        denom,
        out=np.zeros(len(points)),
        where=denom > 0,
    )
    t = np.clip(t, 0, 1)
    closest = starts + t[:, None] * delta
    return np.linalg.norm(points - closest, axis=1)


def a_b_edges(
    starts: np.ndarray,
    ends: np.ndarray,
    sphere_centers: np.ndarray,
    *,
    sample_spacing: float = 100.0,
) -> np.ndarray:
    if len(starts) == 0 or len(sphere_centers) == 0:
        return np.empty((0, 2), dtype=np.int64)
    sample_points: list[np.ndarray] = []
    owners: list[np.ndarray] = []
    for idx, (start, end) in enumerate(zip(starts, ends)):
        length = float(np.linalg.norm(end - start))
        count = max(2, int(np.ceil(length / sample_spacing)) + 1)
        t = np.linspace(0.0, 1.0, count)
        sample_points.append(start + t[:, None] * (end - start))
        owners.append(np.full(count, idx, dtype=np.int64))
    points = np.vstack(sample_points)
    owner = np.concatenate(owners)
    sphere_tree = cKDTree(sphere_centers + BOX_HALF, boxsize=BOX_SIDE)
    neighbors = sphere_tree.query_ball_point(
        points + BOX_HALF, A_B_THRESHOLD + sample_spacing / 2
    )
    encoded: set[int] = set()
    n_spheres = len(sphere_centers)
    for point_idx, sphere_ids in enumerate(neighbors):
        a_id = int(owner[point_idx])
        for b_id in sphere_ids:
            encoded.add(a_id * n_spheres + int(b_id))
    if not encoded:
        return np.empty((0, 2), dtype=np.int64)
    values = np.fromiter(encoded, dtype=np.int64)
    pairs = np.column_stack((values // n_spheres, values % n_spheres))
    segment_midpoints = (starts[pairs[:, 0]] + ends[pairs[:, 0]]) / 2
    sphere_images = sphere_centers[pairs[:, 1]].copy()
    sphere_images -= BOX_SIDE * np.round((sphere_images - segment_midpoints) / BOX_SIDE)
    distance = point_segment_distances(
        sphere_images, starts[pairs[:, 0]], ends[pairs[:, 0]]
    )
    return pairs[distance <= A_B_THRESHOLD + 1e-10]


@dataclass
class MixedGraph:
    a_fragment_rods: np.ndarray
    a_left: np.ndarray
    a_right: np.ndarray
    aa_edges: np.ndarray
    a_periodic_x_bridge: np.ndarray
    ab_edges: np.ndarray
    b_left: np.ndarray
    b_right: np.ndarray
    bb_edges: np.ndarray


def build_mixed_graph(
    a_centers: np.ndarray,
    a_directions: np.ndarray,
    b_centers: np.ndarray,
) -> MixedGraph:
    starts, ends, a_rods = generate_fragments(a_centers, a_directions)
    aa, _, _ = sampled_broadphase_edges(starts, ends)
    a_left, a_right = face_contacts(starts, ends)
    a_radial_x = ROD_RADIUS * np.sqrt(np.maximum(0.0, 1 - a_directions[:, 0] ** 2))
    a_periodic_x_bridge = (
        np.abs(a_centers[:, 0])
        + 2500.0 * np.abs(a_directions[:, 0])
        + a_radial_x
        >= BOX_HALF
    )
    ab = a_b_edges(starts, ends, b_centers)
    bb = (
        cKDTree(b_centers + BOX_HALF, boxsize=BOX_SIDE)
        .query_pairs(B_B_THRESHOLD, output_type="ndarray")
        .astype(np.int64)
        if len(b_centers)
        else np.empty((0, 2), dtype=np.int64)
    )
    touches_left = b_centers[:, 0] - SPHERE_RADIUS <= -BOX_HALF + GAP
    touches_right = b_centers[:, 0] + SPHERE_RADIUS >= BOX_HALF - GAP
    periodic_x_bridge = np.abs(b_centers[:, 0]) + SPHERE_RADIUS >= BOX_HALF
    b_left = touches_left | periodic_x_bridge
    b_right = touches_right | periodic_x_bridge
    return MixedGraph(
        a_rods, a_left, a_right, aa, a_periodic_x_bridge, ab, b_left, b_right, bb
    )


def critical_b_for_a_counts(
    graph: MixedGraph,
    a_counts: list[int],
    max_b: int,
) -> list[int]:
    n_frag = len(graph.a_fragment_rods)
    source, target = n_frag + max_b, n_frag + max_b + 1
    fragments_by_rod: dict[int, list[int]] = {}
    for fragment, rod in enumerate(graph.a_fragment_rods):
        fragments_by_rod.setdefault(int(rod), []).append(fragment)
    bb_events: list[list[tuple[int, int]]] = [[] for _ in range(max_b)]
    for b1, b2 in graph.bb_edges:
        bb_events[int(max(b1, b2))].append((int(b1), int(b2)))
    ab_events: list[list[tuple[int, int]]] = [[] for _ in range(max_b)]
    for a_fragment, b in graph.ab_edges:
        ab_events[int(b)].append((int(a_fragment), int(b)))

    output: list[int] = []
    for a_count in a_counts:
        uf = UnionFind(n_frag + max_b + 2)
        active_a = graph.a_fragment_rods < a_count
        for fragment in np.flatnonzero(active_a):
            if graph.a_left[fragment]:
                uf.union(int(fragment), source)
            if graph.a_right[fragment]:
                uf.union(int(fragment), target)
        for fragments in fragments_by_rod.values():
            active_fragments = [fragment for fragment in fragments if active_a[fragment]]
            for fragment in active_fragments[1:]:
                uf.union(active_fragments[0], fragment)
        for rod in range(a_count):
            if graph.a_periodic_x_bridge[rod]:
                fragments = fragments_by_rod.get(rod, [])
                if fragments:
                    uf.union(fragments[0], source)
                    uf.union(fragments[0], target)
        for f1, f2 in graph.aa_edges:
            if active_a[f1] and active_a[f2]:
                uf.union(int(f1), int(f2))
        if uf.connected(source, target):
            output.append(0)
            continue
        critical = max_b + 1
        for b in range(max_b):
            node = n_frag + b
            if graph.b_left[b]:
                uf.union(node, source)
            if graph.b_right[b]:
                uf.union(node, target)
            for b1, b2 in bb_events[b]:
                uf.union(n_frag + b1, n_frag + b2)
            for a_fragment, b_id in ab_events[b]:
                if active_a[a_fragment]:
                    uf.union(a_fragment, n_frag + b_id)
            if uf.connected(source, target):
                critical = b + 1
                break
        output.append(critical)
    return output
