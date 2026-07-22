"""Conversion façade shared by the CLI and the GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from deccan_convert import matrix
from deccan_convert.ir import DocumentIR, Metadata


@dataclass
class ConversionResult:
    output_path: Path
    warnings: list[str] = field(default_factory=list)
    verification: str = ""


def extract_metadata(input_path: Path) -> Metadata:
    """Read just the metadata of a document-track input (GUI pre-fill)."""
    fmt = matrix.detect_format(input_path)
    if fmt not in matrix.DOCUMENT_FORMATS:
        return Metadata()
    from deccan_convert.readers import read_document

    return read_document(input_path, fmt).metadata


def convert(
    input_path: Path,
    output_path: Path,
    metadata: Metadata | None = None,
    log: Callable[[str], None] | None = None,
    verify: bool = True,
) -> ConversionResult:
    say = log or (lambda _msg: None)
    input_path = Path(input_path)
    output_path = Path(output_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path.exists() and output_path.resolve() == input_path.resolve():
        raise ValueError(
            "The output path is the input file itself; choose a different "
            "name so the source is not overwritten."
        )

    in_fmt = matrix.detect_format(input_path)
    out_fmt = matrix.detect_format(output_path)
    matrix.check_pair(in_fmt, out_fmt)

    if in_fmt in matrix.DOCUMENT_FORMATS:
        return _convert_document(
            input_path, output_path, in_fmt, out_fmt, metadata, say, verify
        )
    return _restyle(input_path, output_path, in_fmt, say)


def _convert_document(
    input_path: Path,
    output_path: Path,
    in_fmt: str,
    out_fmt: str,
    metadata: Metadata | None,
    say: Callable[[str], None],
    verify: bool,
) -> ConversionResult:
    from deccan_convert.readers import read_document
    from deccan_convert.writers import write_document

    say(f"Reading {in_fmt}: {input_path.name}")
    ir = read_document(input_path, in_fmt)

    if metadata is not None:
        ir.metadata = _merge_metadata(ir.metadata, metadata)

    say("Applying deccan-design v2.0")
    written = write_document(ir, output_path, out_fmt, log=say)

    result = ConversionResult(output_path=written, warnings=list(ir.warnings))

    if out_fmt == "pdf" and verify and written.suffix.lower() == ".pdf":
        from deccan_convert.verify import verify_pdf

        verification = verify_pdf(written)
        result.verification = verification.summary()
        say(result.verification)

    say(f"Wrote {written}")
    return result


def _merge_metadata(extracted: Metadata, provided: Metadata) -> Metadata:
    """User-provided values win; extracted values fill the gaps."""
    return Metadata(
        title=provided.title or extracted.title,
        subtitle=provided.subtitle or extracted.subtitle,
        document_type=provided.document_type or extracted.document_type,
        prepared_by=provided.prepared_by or extracted.prepared_by,
        date=provided.date or extracted.date,
        version=provided.version or extracted.version,
        classification=provided.classification or extracted.classification,
    )


def _restyle(
    input_path: Path, output_path: Path, in_fmt: str, say: Callable[[str], None]
) -> ConversionResult:
    say(f"Restyling {in_fmt}: {input_path.name}")
    if in_fmt == "xlsx":
        from deccan_convert.writers.xlsx_writer import restyle_xlsx

        written, warnings = restyle_xlsx(input_path, output_path, log=say)
    else:
        from deccan_convert.writers.pptx_writer import restyle_pptx

        written, warnings = restyle_pptx(input_path, output_path, log=say)
    say(f"Wrote {written}")
    return ConversionResult(output_path=written, warnings=warnings)
