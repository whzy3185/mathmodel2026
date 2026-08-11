# AI assistance disclosure: drafted with OpenAI Codex and used for regression testing.
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/a"))

from geometry import (  # noqa: E402
    ROD_LENGTH,
    all_pair_edges,
    sampled_broadphase_edges,
    seeded_a_configuration,
    infer_periodic_identity_edges,
    segment_distances,
    split_wrapped_axis,
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

    def test_wrapping_conserves_length(self) -> None:
        direction = np.array([1.0, 2.0, 3.0])
        pieces = split_wrapped_axis(np.array([4900.0, 4900.0, 4900.0]), direction)
        total = sum(np.linalg.norm(b - a) for a, b in pieces)
        self.assertAlmostEqual(total, ROD_LENGTH, places=7)
        self.assertTrue(all(np.max(np.abs(np.r_[a, b])) <= 5000 for a, b in pieces))

    def test_broadphase_matches_all_pairs(self) -> None:
        rng = np.random.default_rng(11)
        starts = rng.uniform(-1000, 1000, size=(30, 3))
        ends = starts + rng.normal(size=(30, 3)) * 200
        exact, _ = all_pair_edges(starts, ends)
        broad, _, _ = sampled_broadphase_edges(starts, ends)
        self.assertEqual({tuple(x) for x in exact}, {tuple(x) for x in broad})

    def test_seeded_configuration_is_prefix_stable(self) -> None:
        centers_small, directions_small = seeded_a_configuration(20260811, 10)
        centers_large, directions_large = seeded_a_configuration(20260811, 20)
        np.testing.assert_array_equal(centers_small, centers_large[:10])
        np.testing.assert_array_equal(directions_small, directions_large[:10])

    def test_periodic_identity_edge_inference(self) -> None:
        starts = np.array([[-5000, 1, 2], [100, 3, 4]], float)
        ends = np.array([[-100, 3, 4], [5000, 1, 2]], float)
        edges = infer_periodic_identity_edges(starts, ends)
        self.assertEqual(edges.tolist(), [[0, 1]])


if __name__ == "__main__":
    unittest.main()
