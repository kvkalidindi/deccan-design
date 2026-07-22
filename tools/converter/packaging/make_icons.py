#!/usr/bin/env python3
"""Generate the application icons from the bundled Deccan logo.

Run at build time (CI) — outputs icon.ico (Windows) and icon.icns (macOS)
into this directory from deccan_convert/assets_data/logo.png. Requires
Pillow (the 'build' extra).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / "deccan_convert" / "assets_data" / "logo.png"


def main() -> None:
    img = Image.open(LOGO).convert("RGBA")
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2))

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    canvas.save(HERE / "icon.ico", sizes=ico_sizes)
    print(f"wrote {HERE / 'icon.ico'}")

    icns = canvas.resize((1024, 1024), Image.LANCZOS)
    icns.save(HERE / "icon.icns")
    print(f"wrote {HERE / 'icon.icns'}")


if __name__ == "__main__":
    main()
