"""Command-line interface.

    deccan-convert INPUT [-o OUTPUT | --to FORMAT] [--title ...] [...]

The GUI covers interactive use; this mode exists for scripting and CI. On
the windowed Windows build stdout may not be attached — output then also
goes to a log file next to the converted document.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from deccan_convert import __version__, matrix
from deccan_convert.convert import convert
from deccan_convert.ir import CLASSIFICATIONS, DOCUMENT_TYPES, Metadata
from deccan_convert.matrix import UnsupportedConversion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deccan-convert",
        description=(
            "Convert a document to a deccan-design v2.0 artifact. "
            "Supported formats: md, html, docx, xlsx, pptx, pdf. "
            "Google Docs/Sheets/Slides: download as docx/xlsx/pptx first."
        ),
    )
    parser.add_argument("input", help="input file (.md .html .docx .xlsx .pptx .pdf)")
    out = parser.add_mutually_exclusive_group()
    out.add_argument("-o", "--output", help="output file path (format from extension)")
    out.add_argument(
        "--to", choices=matrix.FORMATS, help="output format (writes next to the input)"
    )
    parser.add_argument("--title", default="", help="document title")
    parser.add_argument("--subtitle", default="", help="document subtitle")
    parser.add_argument(
        "--type", default="", choices=("",) + DOCUMENT_TYPES, metavar="TYPE",
        help=f"document type: one of {', '.join(DOCUMENT_TYPES)}",
    )
    parser.add_argument("--prepared-by", default="", help="author / owning office")
    parser.add_argument("--date", default="", help='document date (e.g. "July 2026")')
    parser.add_argument("--version", default="", help="document version string")
    parser.add_argument(
        "--classification", default="", choices=("",) + CLASSIFICATIONS,
        metavar="CLASS", help=f"one of {', '.join(CLASSIFICATIONS)}",
    )
    parser.add_argument(
        "--no-verify", action="store_true",
        help="skip the print-contract verification after PDF output",
    )
    parser.add_argument(
        "--tool-version", action="version", version=f"deccan-convert {__version__}"
    )
    return parser


def run_cli(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if args.output:
        output_path = Path(args.output)
    elif args.to:
        output_path = matrix.default_output_path(input_path, args.to)
    else:
        parser.error("specify an output with -o FILE or --to FORMAT")

    # On the windowed Windows build there is no console: stdout is None.
    # CLI output then goes to a .log file next to the converted document.
    has_console = sys.stdout is not None
    log_lines: list[str] = []

    def say(message: str) -> None:
        log_lines.append(message)
        if has_console:
            try:
                print(message)
            except OSError:
                pass

    metadata = Metadata(
        title=args.title,
        subtitle=args.subtitle,
        document_type=args.type,
        prepared_by=args.prepared_by,
        date=args.date,
        version=args.version,
        classification=args.classification,
    )

    try:
        result = convert(
            input_path,
            output_path,
            metadata=metadata,
            log=say,
            verify=not args.no_verify,
        )
    except (UnsupportedConversion, FileNotFoundError, ValueError) as exc:
        say(f"error: {exc}")
        if not has_console:
            _write_log(output_path, log_lines)
        return 2
    except Exception as exc:  # unexpected — still surface it cleanly
        say(f"error: {type(exc).__name__}: {exc}")
        if not has_console:
            _write_log(output_path, log_lines)
        return 1

    for warning in result.warnings:
        say(f"warning: {warning}")
    if not has_console:
        _write_log(result.output_path, log_lines)
    return 0 if "FAIL" not in result.verification else 3


def _write_log(output_path: Path, lines: list[str]) -> None:
    if not lines:
        return
    try:
        log_path = output_path.with_suffix(output_path.suffix + ".log")
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass
