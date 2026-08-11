# AI assistance disclosure: drafted with OpenAI Codex and used for regression testing.
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/a"))

from mixed import A_B_THRESHOLD, a_b_edges, point_segment_distances  # noqa: E402


class MixedGeometryTests(unittest.TestCase):
    def test_point_segment_distance(self) -> None:
        points = np.array([[0.5, 2, 0], [2, 0, 0]], float)
        starts = np.array([[0, 0, 0], [0, 0, 0]], float)
        ends = np.array([[1, 0, 0], [1, 0, 0]], float)
        np.testing.assert_allclose(point_segment_distances(points, starts, ends), [2, 1])

    def test_a_b_broadphase(self) -> None:
        starts = np.array([[0, 0, 0], [1000, 1000, 1000]], float)
        ends = np.array([[500, 0, 0], [1500, 1000, 1000]], float)
        spheres = np.array([[250, A_B_THRESHOLD - 0.1, 0], [3000, 0, 0]], float)
        edges = a_b_edges(starts, ends, spheres)
        self.assertEqual({tuple(x) for x in edges}, {(0, 0)})


if __name__ == "__main__":
    unittest.main()
