"""Document intermediate representation for the document track (Track A).

The IR mirrors the eight slots of skill/assets/templates/document.html
(seven scalar metadata slots + BODY_HTML). Readers produce it; writers
consume it. body_html is a string of <section class="section"> blocks
restricted to the component vocabulary in skill/references/components.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

DOCUMENT_TYPES = (
    "Standard",
    "Specification",
    "Policy",
    "Memo",
    "Brief",
    "Report",
    "Letter",
    "Proposal",
    "Guide",
)

CLASSIFICATIONS = ("Public", "Internal", "Confidential", "Restricted")

_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def current_month_year() -> str:
    today = date.today()
    return f"{_MONTHS[today.month - 1]} {today.year}"


@dataclass
class Metadata:
    """The seven scalar slots of the document template.

    Slot policy (document-slots.md): never invent title, document_type, or
    prepared_by — leave them empty and let the caller (GUI/CLI) demand them.
    subtitle/version/date/classification carry the documented defaults.
    """

    title: str = ""
    subtitle: str = ""
    document_type: str = ""
    prepared_by: str = ""
    date: str = ""
    version: str = ""
    classification: str = ""

    def with_defaults(self) -> "Metadata":
        """Return a copy with the documented defaults applied to optional slots."""
        return Metadata(
            title=self.title,
            subtitle=self.subtitle,
            document_type=self.document_type,
            prepared_by=self.prepared_by,
            date=self.date or current_month_year(),
            version=self.version or "1.0",
            classification=self.classification or "Confidential",
        )

    def missing_required(self) -> list[str]:
        """Names of required slots that are empty and must come from the user."""
        missing = []
        if not self.title.strip():
            missing.append("title")
        if not self.document_type.strip():
            missing.append("document type")
        if not self.prepared_by.strip():
            missing.append("prepared by")
        return missing


@dataclass
class DocumentIR:
    metadata: Metadata = field(default_factory=Metadata)
    body_html: str = ""
    warnings: list[str] = field(default_factory=list)
