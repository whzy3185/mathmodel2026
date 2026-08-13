from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinalResultConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((ROOT / "outputs/data/final_results.json").read_text(encoding="utf-8"))
        cls.paper = (ROOT / "paper/paper.md").read_text(encoding="utf-8")

    def test_q1_matches_official_row_interpretation(self) -> None:
        self.assertEqual([row["connected"] for row in self.results["Q1"]], [False, True, True])
        for row in self.results["Q1"][1:]:
            inter_edges = [edge for edge in row["path_certificates"] if edge["type"] != "electrode_contact"]
            self.assertTrue(inter_edges)
            self.assertTrue(all(edge["flat_cylinder_sufficient"] for edge in inter_edges))

    def test_q3_is_analytic_not_sample_selected(self) -> None:
        self.assertGreater(self.results["Q3"]["selected_lower_bound"], 0.90)
        self.assertLess(self.results["Q3"]["lower_neighbor_upper_bound"], 0.90)
        self.assertNotIn("replications", self.results["Q3"])

    def test_q4_global_and_positive_domains_are_closed(self) -> None:
        q4 = self.results["Q4"]
        self.assertEqual(q4["cheaper_integer_candidate_count"], 216)
        self.assertLess(q4["maximum_upper_bound_among_cheaper"]["conduction_upper_bound"], 0.90)
        self.assertEqual(q4["strictly_positive_mixture"]["cheaper_integer_candidate_count"], 164)

    def test_paper_contains_corrected_headlines(self) -> None:
        for text in ("组1不导通", "组2和组3导通", "0A+57B", "1A+50B", "216个", "164个"):
            self.assertIn(text, self.paper)
        self.assertNotIn("三组微构体均导通", self.paper)


if __name__ == "__main__":
    unittest.main()
