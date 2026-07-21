"""Common helpers for the application package."""

from __future__ import annotations

from pathlib import Path
from typing import List


def read_text_file(path: str | Path) -> str:
    """Read and return the contents of a text file."""
    return Path(path).read_text(encoding="utf-8")


def list_text_files(folder: str | Path) -> List[str]:
    """Return text files found in a directory."""
    root = Path(folder)
    if not root.exists():
        return []
    return [str(path) for path in sorted(root.rglob("*.txt")) if path.is_file()]
