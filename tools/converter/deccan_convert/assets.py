"""Resolve bundled design assets in both dev checkouts and frozen binaries.

Assets live in deccan_convert/assets_data/, populated from the repository's
single sources of truth by tools/converter/sync_assets.py. Under PyInstaller
the directory is unpacked to sys._MEIPASS/assets_data.
"""

from __future__ import annotations

import sys
from pathlib import Path


def assets_dir() -> Path:
    frozen_base = getattr(sys, "_MEIPASS", None)
    if frozen_base is not None:
        return Path(frozen_base) / "assets_data"
    return Path(__file__).parent / "assets_data"


def asset_path(name: str) -> Path:
    path = assets_dir() / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Bundled asset '{name}' not found at {path}. "
            "In a dev checkout run: python tools/converter/sync_assets.py"
        )
    return path


def asset_text(name: str) -> str:
    return asset_path(name).read_text(encoding="utf-8")
