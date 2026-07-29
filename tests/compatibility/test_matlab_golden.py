from __future__ import annotations

import json
from pathlib import Path

import pytest

GOLDEN_DIRECTORY = Path(__file__).parents[1] / "golden"
MANIFEST = GOLDEN_DIRECTORY / "manifest.json"


@pytest.mark.compatibility
def test_matlab_golden_corpus_is_explicitly_gated() -> None:
    if not MANIFEST.exists():
        pytest.skip(
            "MATLAB golden corpus is unavailable; equivalence remains unclaimed. "
            "See VALIDATION.md."
        )
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["reference_commit"] == "16adb481b5b0223a5d97622e4df61ed6fc5b0c93"
    assert manifest["matlab_release"]
    assert manifest["symbolic_math_toolbox_version"]
    assert manifest["cases"]
