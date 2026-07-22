from pathlib import Path

import pytest

from deccan_convert import matrix
from deccan_convert.matrix import UnsupportedConversion


def test_every_format_has_at_least_one_output():
    for fmt in matrix.FORMATS:
        if fmt == "pdf":
            continue  # pdf is input-only into other formats
        assert matrix.outputs_for(fmt)


def test_document_formats_cross_convert():
    for src in matrix.DOCUMENT_FORMATS:
        for dst in matrix.DOCUMENT_FORMATS:
            if (src, dst) in ((("md"), ("md")), ("pdf", "pdf")):
                continue
            if src == "md" and dst == "md":
                continue
            assert (src, dst) in matrix.SUPPORTED_PAIRS


def test_tracks_never_cross():
    for doc_fmt in matrix.DOCUMENT_FORMATS:
        assert (doc_fmt, "xlsx") not in matrix.SUPPORTED_PAIRS
        assert (doc_fmt, "pptx") not in matrix.SUPPORTED_PAIRS
        assert ("xlsx", doc_fmt) not in matrix.SUPPORTED_PAIRS
        assert ("pptx", doc_fmt) not in matrix.SUPPORTED_PAIRS


@pytest.mark.parametrize(
    "pair", [("xlsx", "pdf"), ("pptx", "pdf"), ("pdf", "pdf"), ("md", "md"), ("xlsx", "pptx")]
)
def test_rejected_pairs_raise_with_message(pair):
    with pytest.raises(UnsupportedConversion) as exc_info:
        matrix.check_pair(*pair)
    assert "not supported" in str(exc_info.value) or "no-op" in str(exc_info.value)


def test_detect_format():
    assert matrix.detect_format("a/b/report.DOCX") == "docx"
    assert matrix.detect_format("notes.markdown") == "md"
    assert matrix.detect_format("page.htm") == "html"
    with pytest.raises(UnsupportedConversion) as exc_info:
        matrix.detect_format("data.csv")
    assert "Google" in str(exc_info.value)


def test_default_output_path_never_clobbers_input(tmp_path):
    src = tmp_path / "book.xlsx"
    src.touch()
    out = matrix.default_output_path(src, "xlsx")
    assert out != src
    assert out.name == "book-deccan.xlsx"
    assert matrix.default_output_path(Path("doc.md"), "pdf").name == "doc.pdf"
