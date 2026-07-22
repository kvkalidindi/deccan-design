"""End-to-end print-contract test: render a real PDF and verify the footer
contract from skill/references/print-rules.md. Requires a Chromium-family
browser; runs as the post-build smoke stage on the Windows/macOS CI jobs."""

import pytest

from deccan_convert.convert import convert
from deccan_convert.verify import verify_pdf

from .conftest import browser_available

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(not browser_available(), reason="no Chromium-family browser"),
]


def test_rendered_pdf_honours_print_contract(sample_md, tmp_path):
    out = tmp_path / "contract.pdf"
    result = convert(sample_md, out, verify=True)
    assert result.output_path == out
    assert "PASS" in result.verification

    verification = verify_pdf(out)
    assert verification.passed, verification.failures
    # Cover + at least one body page + end page.
    assert verification.page_count >= 3


def test_verifier_catches_missing_footer(tmp_path, sample_md):
    """Render with a slot template stripped of @page rules; verify must FAIL."""
    from deccan_convert.readers.md_reader import read_md
    from deccan_convert.writers import html_writer
    from deccan_convert.writers.pdf_writer import find_browser, render_pdf_from_html

    ir = read_md(sample_md)
    html = html_writer.render_html(ir)
    broken = html.replace('content: "Deccan Fine Chemicals · Confidential";', "")
    html_path = tmp_path / "broken.html"
    html_path.write_text(broken, encoding="utf-8")
    pdf_path = tmp_path / "broken.pdf"
    render_pdf_from_html(html_path, pdf_path, find_browser())

    verification = verify_pdf(pdf_path)
    assert not verification.passed
