from __future__ import annotations

from pathlib import Path

from .. import __version__
from .paths import version_file_candidates


def _read_version_file(path: Path) -> str | None:
    try:
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8").strip()
        return text or None
    except OSError:
        return None


def resolve_app_version() -> str:
    for candidate in version_file_candidates():
        value = _read_version_file(candidate)
        if value:
            return value
    return __version__
