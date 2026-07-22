"""Entry point: arguments mean CLI, no arguments means GUI."""

from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) > 1:
        from deccan_convert.cli import run_cli

        return run_cli(sys.argv[1:])
    from deccan_convert.gui import run_gui

    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
