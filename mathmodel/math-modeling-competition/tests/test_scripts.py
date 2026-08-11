from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from init_workspace import initialize  # noqa: E402


class WorkspaceTests(unittest.TestCase):
    def test_initialize_is_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = initialize(root, "cumcm")
            first = state.read_text(encoding="utf-8")
            state.write_text(first.replace('"decisions": []', '"decisions": ["keep"]'), encoding="utf-8")
            initialize(root, "mcm")
            self.assertIn('"keep"', state.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
