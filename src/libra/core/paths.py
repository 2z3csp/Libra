from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Libra"


def appdata_root() -> Path:
    base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or str(Path.home())
    root = Path(base) / APP_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def config_dir() -> Path:
    path = appdata_root() / "config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = appdata_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> Path:
    path = appdata_root() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def registry_path() -> Path:
    return config_dir() / "registry.json"


def settings_path() -> Path:
    return config_dir() / "settings.json"


def user_checks_path() -> Path:
    return cache_dir() / "user_checks.json"


def runtime_libra_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / "libra"
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    return runtime_libra_dir() / "resources" / Path(*parts)


def checked_resource_path(*parts: str) -> Path:
    path = resource_path(*parts)
    if not path.exists():
        base = runtime_libra_dir()
        raise FileNotFoundError(f"Resource not found: {path} (runtime_libra_dir={base})")
    return path


def executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def version_file_candidates() -> list[Path]:
    return [
        executable_dir() / "VERSION.txt",
        runtime_libra_dir() / "VERSION.txt",
    ]
