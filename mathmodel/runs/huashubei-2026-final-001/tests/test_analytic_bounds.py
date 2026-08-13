from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/a"))

from analytic_bounds import (  # noqa: E402
    IntegerCandidate,
    cheaper_frontier,
    direct_bridge_probability,
    enumerate_cheaper_than,
    prove_q3,
    prove_q4,
)


class AnalyticBoundsTests(unittest.TestCase):
    def test_q3_is_strictly_proved(self) -> None:
        proof = prove_q3()
        self.assertGreater(proof["selected_lower_bound"], 0.90)
        self.assertLess(proof["lower_neighbor_upper_bound"], 0.90)

    def test_q4_enumerates_entire_cheaper_integer_domain(self) -> None:
        selected = IntegerCandidate(0, 57)
        cheaper = enumerate_cheaper_than(selected)
        self.assertEqual(len(cheaper), 216)
        self.assertTrue(all(candidate.cost < selected.cost for candidate in cheaper))
        self.assertTrue(all(candidate.upper < 0.90 for candidate in cheaper))

    def test_q4_frontier_is_complete(self) -> None:
        frontier = [(x.a_count, x.b_count) for x in cheaper_frontier(IntegerCandidate(0, 57))]
        self.assertEqual(frontier, [(0, 56), (1, 48), (2, 39), (3, 30), (4, 21), (5, 12), (6, 3)])

    def test_selected_q4_is_sufficient(self) -> None:
        proof = prove_q4()
        self.assertGreater(proof["selected"]["direct_bridge_lower_bound"], 0.90)
        self.assertLess(proof["maximum_upper_bound_among_cheaper"]["conduction_upper_bound"], 0.90)
        positive = proof["strictly_positive_mixture"]
        self.assertEqual((positive["selected"]["a_count"], positive["selected"]["b_count"]), (1, 50))
        self.assertGreater(positive["selected"]["direct_bridge_lower_bound"], 0.90)
        self.assertLess(positive["maximum_upper_bound_among_cheaper"]["conduction_upper_bound"], 0.90)

    def test_direct_bridge_is_monotone(self) -> None:
        self.assertLess(direct_bridge_probability(7, 0), direct_bridge_probability(8, 0))
        self.assertLess(direct_bridge_probability(0, 56), direct_bridge_probability(0, 57))


if __name__ == "__main__":
    unittest.main()
