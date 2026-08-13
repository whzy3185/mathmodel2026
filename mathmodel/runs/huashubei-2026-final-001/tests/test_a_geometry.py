from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/a"))

from geometry import (  # noqa: E402
    all_pair_edges,
    connectivity,
    sampled_broadphase_edges,
    segment_distance_certificates,
    segment_distances,
)


class GeometryTests(unittest.TestCase):
    def test_segment_distance_cases(self) -> None:
        p0 = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], float)
        p1 = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]], float)
        q0 = np.array([[0.5, -1, 0], [0, 2, 0], [2, 0, 0]], float)
        q1 = np.array([[0.5, 1, 0], [1, 2, 0], [3, 0, 0]], float)
        np.testing.assert_allclose(segment_distances(p0, p1, q0, q1), [0, 2, 1])

    def test_endpoint_order_invariance(self) -> None:
        rng = np.random.default_rng(7)
        p0, p1, q0, q1 = [rng.normal(size=(100, 3)) for _ in range(4)]
        d1 = segment_distances(p0, p1, q0, q1)
        d2 = segment_distances(p1, p0, q1, q0)
        np.testing.assert_allclose(d1, d2, atol=1e-12)

    def test_certificate_identifies_interior_contact(self) -> None:
        p0 = np.array([[0, 0, 0]], float); p1 = np.array([[10, 0, 0]], float)
        q0 = np.array([[5, -1, 0]], float); q1 = np.array([[5, 1, 0]], float)
        distance, s, t = segment_distance_certificates(p0, p1, q0, q1)
        np.testing.assert_allclose(distance, [0]); np.testing.assert_allclose(s, [0.5]); np.testing.assert_allclose(t, [0.5])

    def test_broadphase_matches_all_pairs(self) -> None:
        rng = np.random.default_rng(11)
        starts = rng.uniform(-1000, 1000, size=(30, 3))
        ends = starts + rng.normal(size=(30, 3)) * 200
        exact, _ = all_pair_edges(starts, ends)
        broad, _, _ = sampled_broadphase_edges(starts, ends)
        self.assertEqual({tuple(x) for x in exact}, {tuple(x) for x in broad})

    def test_no_unconditional_periodic_minimum_image(self) -> None:
        starts = np.array([[-100, 4990, 0], [-100, -4990, 0]], float)
        ends = np.array([[100, 4990, 0], [100, -4990, 0]], float)
        edges, _ = all_pair_edges(starts, ends)
        self.assertEqual(edges.tolist(), [])

    def test_rows_are_not_merged_by_matching_seams(self) -> None:
        starts = np.array([[-5000, 1, 2], [100, 3, 4]], float)
        ends = np.array([[-100, 3, 4], [5000, 1, 2]], float)
        result = connectivity(starts, ends)
        self.assertFalse(result.connected)


if __name__ == "__main__":
    unittest.main()
