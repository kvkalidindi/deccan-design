"""Format support matrix — the single source of truth for what converts to what.

Both the GUI (dropdown filtering) and the CLI (validation) read this module.
Track A (document track): md / html / docx / pdf cross-convert through the
HTML canonical intermediate. Track B (restyle track): xlsx and pptx restyle
in place only — the two tracks never cross.
"""

from __future__ import annotations

from pathlib import Path

FORMATS = ("md", "html", "docx", "pdf", "xlsx", "pptx")

DOCUMENT_FORMATS = ("md", "html", "docx", "pdf")

_EXTENSIONS = {
    ".md": "md",
    ".markdown": "md",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
    ".pdf": "pdf",
    ".xlsx": "xlsx",
    ".pptx": "pptx",
}

# (input, output) pairs the converter supports.
SUPPORTED_PAIRS = frozenset(
    [
        # Track A — md/html/docx read into the document IR, write to any
        # document format. PDF is read-only (text extraction) and cannot be
        # regenerated from itself.
        *[
            (src, dst)
            for src in DOCUMENT_FORMATS
            for dst in DOCUMENT_FORMATS
            if not (src == "md" and dst == "md") and not (src == "pdf" and dst == "pdf")
        ],
        # Track B — same-format restyle only.
        ("xlsx", "xlsx"),
        ("pptx", "pptx"),
    ]
)

# Human explanations for the deliberate gaps, shown when a pair is rejected.
_REJECTION_REASONS = {
    ("xlsx", "pdf"): (
        "xlsx to pdf is not supported. Convert to a restyled .xlsx, open it in "
        "Excel, and use File > Export > Create PDF/XPS (the deccan-design print "
        "policy forbids automated Office rendering)."
    ),
    ("pptx", "pdf"): (
        "pptx to pdf is not supported. Convert to a restyled .pptx, open it in "
        "PowerPoint, and use File > Export > Create PDF/XPS (the deccan-design "
        "print policy forbids automated Office rendering)."
    ),
    ("pdf", "pdf"): (
        "pdf to pdf is not supported. PDF input is text extraction only; "
        "convert the original source document instead."
    ),
    ("md", "md"): (
        "md to md would be a no-op. Markdown carries no visual styling; choose "
        "html, docx, or pdf as the output to apply the design system."
    ),
}


class UnsupportedConversion(ValueError):
    """Raised when an (input, output) pair is outside the support matrix."""


def detect_format(path: str | Path) -> str:
    """Map a file path to a format key by extension.

    Raises UnsupportedConversion for unrecognised extensions.
    """
    suffix = Path(path).suffix.lower()
    fmt = _EXTENSIONS.get(suffix)
    if fmt is None:
        supported = ", ".join(sorted(set(_EXTENSIONS)))
        raise UnsupportedConversion(
            f"Unrecognised file type '{suffix or path}'. Supported extensions: {supported}. "
            "Google Docs/Sheets/Slides: download as .docx/.xlsx/.pptx first "
            "(File > Download in Google Workspace)."
        )
    return fmt


def outputs_for(input_format: str) -> list[str]:
    """Ordered list of output formats valid for the given input format."""
    return [dst for dst in FORMATS if (input_format, dst) in SUPPORTED_PAIRS]


def check_pair(input_format: str, output_format: str) -> None:
    """Raise UnsupportedConversion with a human message for invalid pairs."""
    if (input_format, output_format) in SUPPORTED_PAIRS:
        return
    reason = _REJECTION_REASONS.get((input_format, output_format))
    if reason is None:
        valid = ", ".join(outputs_for(input_format)) or "none"
        if input_format in ("xlsx", "pptx"):
            reason = (
                f"{input_format} to {output_format} is not supported. Spreadsheets "
                f"and decks restyle to their own format only (valid output: {valid})."
            )
        else:
            reason = (
                f"{input_format} to {output_format} is not supported. "
                f"Valid outputs for {input_format}: {valid}."
            )
    raise UnsupportedConversion(reason)


def default_extension(output_format: str) -> str:
    return "." + output_format


def default_output_path(input_path: str | Path, output_format: str) -> Path:
    """Default output path next to the input; never the input path itself.

    Same-format restyles (xlsx -> xlsx) get a '-deccan' stem suffix so the
    source file is never clobbered.
    """
    input_path = Path(input_path)
    candidate = input_path.with_suffix(default_extension(output_format))
    if candidate.resolve() == input_path.resolve():
        candidate = input_path.with_name(
            input_path.stem + "-deccan" + default_extension(output_format)
        )
    return candidate
