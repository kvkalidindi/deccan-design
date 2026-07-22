from deccan_convert.readers.docx_reader import read_docx
from deccan_convert.readers.html_reader import read_html
from deccan_convert.readers.md_reader import read_md
from deccan_convert.readers.pdf_reader import read_pdf


def test_md_front_matter_and_sections(sample_md):
    ir = read_md(sample_md)
    assert ir.metadata.title == "Solvent Recovery Audit"
    assert ir.metadata.document_type == "Report"
    assert ir.metadata.prepared_by == "QHSE Team"
    assert ir.metadata.classification == "Internal"
    assert ir.body_html.count('<section class="section">') == 2
    assert '<span class="num">01</span>' in ir.body_html
    assert '<div class="callout">' in ir.body_html
    assert '<pre class="code-block">' in ir.body_html
    assert "<thead>" in ir.body_html
    assert '<a href="https://example.com/plan">' in ir.body_html


def test_md_title_from_first_heading(tmp_path):
    path = tmp_path / "plain.md"
    path.write_text("# The Title\n\n## First section\n\nBody.\n", encoding="utf-8")
    ir = read_md(path)
    assert ir.metadata.title == "The Title"
    # H2 promoted to H1 section heading after the title is consumed.
    assert "<h1>" in ir.body_html and "First section" in ir.body_html


def test_foreign_html_sanitised(sample_html):
    ir = read_html(sample_html)
    assert ir.metadata.title == "Maintenance Notice"
    assert ir.metadata.prepared_by == "Plant Ops"
    assert "script" not in ir.body_html
    assert "<strong>Friday</strong>" in ir.body_html
    # Title-duplicating heading dropped; content still sectioned.
    assert ir.body_html.count("Maintenance Notice") == 0
    assert "<li>Drain loop</li>" in ir.body_html


def test_deccan_html_roundtrip(sample_md, tmp_path):
    from deccan_convert.writers.html_writer import write_html

    ir = read_md(sample_md)
    html_path = write_html(ir, tmp_path / "doc.html")
    ir2 = read_html(html_path)
    assert ir2.metadata.title == ir.metadata.title
    assert ir2.metadata.classification == "Internal"
    assert ir2.metadata.document_type == "Report"
    assert ir2.body_html.count('<section class="section">') == 2
    assert "condenser retrofit" in ir2.body_html


def test_docx_reader(sample_docx):
    ir = read_docx(sample_docx)
    assert ir.metadata.title == "Vendor Assessment"
    assert ir.metadata.prepared_by == "Procurement"
    assert "<h1" in ir.body_html and "Scope" in ir.body_html
    assert "<strong>quality</strong>" in ir.body_html
    assert "<li>Vendor one</li>" in ir.body_html
    assert "Acme" in ir.body_html


def test_pdf_reader(sample_pdf):
    ir = read_pdf(sample_pdf)
    assert ir.warnings, "fidelity warning must always be attached"
    assert "Findings" in ir.body_html
    assert "condenser retrofit" in ir.body_html
    # Running footers must not leak into content.
    assert "Confidential 2" not in ir.body_html


def test_pdf_reader_rejects_empty(tmp_path):
    import pypdf

    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    path = tmp_path / "blank.pdf"
    with open(path, "wb") as fh:
        writer.write(fh)
    import pytest

    with pytest.raises(ValueError, match="no extractable text"):
        read_pdf(path)
