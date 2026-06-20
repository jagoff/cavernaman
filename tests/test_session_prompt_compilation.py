#!/usr/bin/env python3
"""Regression test for the compiled SessionStart prompt."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "src" / "hooks" / "caveman-activate.js"


def token_count(text: str) -> int:
    script = """
from pathlib import Path
import sys
import tiktoken
enc = tiktoken.get_encoding('o200k_base')
text = sys.stdin.read()
print(len(enc.encode(text)))
"""
    out = subprocess.check_output(
        ["uv", "run", "--with", "tiktoken", "python", "-c", script],
        cwd=ROOT,
        input=text.encode("utf-8"),
    )
    return int(out.decode("utf-8").strip())


def run_hook(mode: str = "full") -> str:
    with tempfile.TemporaryDirectory() as tmp:
        claude_dir = Path(tmp) / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}", encoding="utf-8")
        out = subprocess.check_output(
            ["node", str(HOOK)],
            cwd=ROOT,
            env={**os.environ, "HOME": tmp, "CLAUDE_CONFIG_DIR": str(claude_dir), "CAVEMAN_DEFAULT_MODE": mode},
        )
        return out.decode("utf-8")


def main() -> int:
    full = run_hook("full")
    ultra = run_hook("ultra")

    assert "CAVERNAMAN MODE ACTIVE" in full
    assert "CAVERNAMAN MODE ACTIVE" in ultra
    assert token_count(full) < 300, token_count(full)
    assert token_count(ultra) < 300, token_count(ultra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
