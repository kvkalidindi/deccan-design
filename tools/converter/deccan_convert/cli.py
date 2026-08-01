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
    parser.add_argument(
        "input", nargs="?", help="input file (.md .html .docx .xlsx .pptx .pdf)"
    )
    out = parser.add_mutually_exclusive_group()
    out.add_argument("-o", "--output", help="output file path (format from extension)")
    out.add_argument(
        "--to", choices=matrix.FORMATS, help="output format (writes next to the input)"
    )
    parser.add_argument(
        "--template",
        default="document",
        choices=("document", "technical-spec", "policy", "customer-letter"),
        help="Word template flavor (docx output only; default: document)",
    )
    parser.add_argument(
        "--logo", action="store_true",
        help="use the graphical Deccan wordmark on the cover (bundled asset, "
             "embedded - nothing is fetched)",
    )
    parser.add_argument(
        "--export-kit", metavar="DIR",
        help="write the bundled design kit (all templates, signatures, and the "
             "Claude skill) to DIR/deccan-design-kit and exit",
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
        "--no-update", action="store_true",
        help="skip the launch-time update check (same as DECCAN_CONVERT_NO_UPDATE=1)",
    )
    parser.add_argument(
        "--check-update", action="store_true",
        help="check for a newer build, install it, and exit",
    )
    parser.add_argument(
        "--tool-version", action="version", version=f"deccan-convert {__version__}"
    )
    return parser


def run_cli(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    from deccan_convert import update as updater

    updater.cleanup_previous()

    if args.check_update:
        return _check_update_now(updater, force=True, no_update=args.no_update)

    # The check runs alongside the requested work and is applied only once
    # that work has finished: a scripted run is never delayed, interrupted,
    # or restarted by it. The new build takes effect on the next invocation.
    update_check = updater.start_background(no_update=args.no_update)
    try:
        return _run(parser, args)
    finally:
        _apply_background_update(updater, update_check)


def _console(message: str) -> None:
    """Print only when a console is attached (the Windows build is windowed)."""
    if sys.stdout is None:
        return
    try:
        print(message)
    except OSError:
        pass


def _apply_background_update(updater, update_check) -> None:
    if update_check is None:
        return
    staged = update_check.wait(timeout=2.0)
    if staged is None:
        return  # still downloading, nothing found, or the check failed
    if updater.apply_staged(staged.path, staged.target):
        _console(
            f"deccan-convert updated to {staged.update.version} — "
            "it takes effect on the next run."
        )


def _check_update_now(updater, force: bool, no_update: bool) -> int:
    reason = updater.disabled_reason(no_update)
    if reason is not None:
        _console(f"Update check skipped: {reason}.")
        return 0
    staged = updater.prepare(force=force, no_update=no_update)
    if staged is None:
        _console(f"deccan-convert {__version__} is current (or the check could not run).")
        return 0
    if not updater.apply_staged(staged.path, staged.target):
        _console(
            f"error: could not install {staged.update.version}; "
            "the current build is intact"
        )
        return 1
    _console(f"Updated to deccan-convert {staged.update.version} ({staged.update.page_url}).")
    return 0


def _run(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    if args.export_kit:
        from deccan_convert.kit import export_kit

        try:
            target = export_kit(Path(args.export_kit))
        except (FileNotFoundError, FileExistsError, OSError) as exc:
            print(f"error: {exc}")
            return 2
        print(f"Design kit written to {target}")
        return 0

    if not args.input:
        parser.error("input file required (or use --export-kit DIR)")

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
            template=args.template,
            logo=args.logo,
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
