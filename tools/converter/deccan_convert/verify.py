"""Print-contract verification for rendered PDFs.

Python port of the -Verify mode of tools/Render-DeccanDocumentPdf.ps1,
using pypdf instead of pdftotext so no external tool is required. Contract
(skill/references/print-rules.md): the cover (page 1) and the end page
(last page) carry no footer; every body page carries the running footer
"Deccan Fine Chemicals · Confidential" with a bare integer page number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

_FOOTER_RE = re.compile(r"Deccan Fine Chemicals.{1,3}Confidential")


@dataclass
class VerificationResult:
    page_count: int = 0
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def summary(self) -> str:
        if self.passed:
            return f"Print contract: PASS ({self.page_count} pages)"
        return (
            f"Print contract: FAIL ({self.page_count} pages) - "
            + "; ".join(self.failures)
        )


def verify_pdf(path: Path) -> VerificationResult:
    reader = PdfReader(str(path))
    result = VerificationResult(page_count=len(reader.pages))

    for index, page in enumerate(reader.pages):
        page_no = index + 1
        text = page.extract_text() or ""
        has_footer = _FOOTER_RE.search(text) is not None
        is_cover = page_no == 1
        is_end = page_no == result.page_count
        expect_footer = not (is_cover or is_end)

        role = "cover" if is_cover else ("end" if is_end else "body")
        state = "has footer" if has_footer else "no footer"
        result.notes.append(f"page {page_no} ({role}): {state}")

        if has_footer != expect_footer:
            if expect_footer:
                result.failures.append(f"page {page_no} (body) is missing the footer")
            else:
                result.failures.append(f"page {page_no} ({role}) must not have a footer")

    if result.page_count < 3:
        result.notes.append(
            "document has fewer than 3 pages; cover/body/end roles overlap"
        )
    return result
