"""Support-matrix integration tests: every supported pair converts, every
rejected pair raises with a human message."""

import subprocess
import sys
from pathlib import Path

import pytest

from deccan_convert import matrix
from deccan_convert.convert import convert
from deccan_convert.ir import Metadata
from deccan_convert.matrix import UnsupportedConversion

from .conftest import browser_available

_METADATA = Metadata(
    title="Matrix Test",
    document_type="Report",
    prepared_by="Test Suite",
)


@pytest.fixture
def inputs(sample_md, sample_html, sample_docx, sample_xlsx, sample_pptx, sample_pdf):
    return {
        "md": sample_md,
        "html": sample_html,
        "docx": sample_docx,
        "xlsx": sample_xlsx,
        "pptx": sample_pptx,
        "pdf": sample_pdf,
    }


@pytest.mark.parametrize("pair", sorted(matrix.SUPPORTED_PAIRS))
def test_supported_pair_converts(pair, inputs, tmp_path):
    src_fmt, dst_fmt = pair
    if dst_fmt == "pdf" and not browser_available():
        pytest.skip("no Chromium-family browser on this machine")
    out = tmp_path / f"out-{src_fmt}.{dst_fmt}"
    result = convert(inputs[src_fmt], out, metadata=_METADATA, verify=False)
    assert result.output_path.is_file()
    assert result.output_path.stat().st_size > 0


@pytest.mark.parametrize(
    "pair",
    sorted(
        (src, dst)
        for src in matrix.FORMATS
        for dst in matrix.FORMATS
        if (src, dst) not in matrix.SUPPORTED_PAIRS
    ),
)
def test_unsupported_pair_rejects(pair, inputs, tmp_path):
    src_fmt, dst_fmt = pair
    out = tmp_path / f"out.{dst_fmt}"
    with pytest.raises(UnsupportedConversion):
        convert(inputs[src_fmt], out, metadata=_METADATA)


def test_output_equal_to_input_rejected(sample_xlsx):
    with pytest.raises(ValueError, match="not overwritten"):
        convert(sample_xlsx, sample_xlsx)


def test_cli_subprocess(sample_md, tmp_path):
    out = tmp_path / "cli.html"
    proc = subprocess.run(
        [sys.executable, "-m", "deccan_convert", str(sample_md), "-o", str(out)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[1],
    )
    assert proc.returncode == 0, proc.stderr
    assert out.is_file()
    assert "Wrote" in proc.stdout


def test_cli_rejection_exit_code(sample_xlsx, tmp_path):
    proc = subprocess.run(
        [
            sys.executable, "-m", "deccan_convert",
            str(sample_xlsx), "-o", str(tmp_path / "no.pdf"),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[1],
    )
    assert proc.returncode == 2
    assert "not supported" in proc.stdout


def test_missing_required_metadata_fails_clearly(sample_html, tmp_path):
    # sample_html has a title+author but no document type; without user input
    # the document track must refuse rather than invent one.
    with pytest.raises(ValueError, match="document type"):
        convert(sample_html, tmp_path / "out.html")
