#!/usr/bin/env python3
"""Regression test for the token budget comparison script."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals" / "context_budget.py"


def main() -> int:
    result = subprocess.run(
        ["uv", "run", "--with", "tiktoken", "python", str(SCRIPT)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "total_docs_plus_tracker" in result.stdout

    match = re.search(r"total_docs_plus_tracker,\d+,\d+,\d+,([0-9.]+)%", result.stdout)
    assert match, result.stdout
    assert float(match.group(1)) >= 5.0, result.stdout
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
