"""PDF writer: DocumentIR -> styled HTML -> PDF via a headless Chromium browser.

Cross-platform port of tools/Render-DeccanDocumentPdf.ps1. The print policy
(skill/references/print-rules.md) allows browser print-to-PDF; Office COM
automation is banned. Headless Chromium prints backgrounds by default, so
the stone-tinted callouts and code blocks render correctly.

If no Chromium-family browser is found, the writer falls back to saving the
styled HTML next to the requested output with instructions — it never fails
silently and never requires admin rights.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

from deccan_convert.ir import DocumentIR
from deccan_convert.writers.html_writer import render_html


class BrowserNotFound(RuntimeError):
    """No Chromium-family browser available for PDF rendering."""


def _windows_candidates() -> list[Path]:
    roots = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("LOCALAPPDATA", ""),  # per-user installs — no admin
    ]
    subpaths = [
        r"Microsoft\Edge\Application\msedge.exe",
        r"Google\Chrome\Application\chrome.exe",
        r"Chromium\Application\chrome.exe",
    ]
    return [Path(root) / sub for root in roots if root for sub in subpaths]


def _macos_candidates() -> list[Path]:
    apps = [
        "Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "Google Chrome.app/Contents/MacOS/Google Chrome",
        "Chromium.app/Contents/MacOS/Chromium",
    ]
    roots = [Path("/Applications"), Path.home() / "Applications"]
    return [root / app for root in roots for app in apps]


def find_browser() -> Path:
    if sys.platform == "win32":
        candidates = _windows_candidates()
        which_names = ["msedge", "chrome"]
    elif sys.platform == "darwin":
        candidates = _macos_candidates()
        which_names = ["chromium", "google-chrome"]
    else:
        candidates = []
        which_names = [
            "chromium", "chromium-browser", "google-chrome",
            "google-chrome-stable", "microsoft-edge",
        ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    for name in which_names:
        found = shutil.which(name)
        if found:
            return Path(found)
    env_override = os.environ.get("DECCAN_CONVERT_BROWSER")
    if env_override and Path(env_override).is_file():
        return Path(env_override)
    raise BrowserNotFound(
        "No Microsoft Edge, Google Chrome, or Chromium installation was found."
    )


def render_pdf_from_html(html_path: Path, pdf_path: Path, browser: Path) -> None:
    uri = html_path.resolve().as_uri()
    with tempfile.TemporaryDirectory(prefix="deccan-render-") as profile:
        base_args = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path.resolve()}",
            uri,
        ]
        result = subprocess.run(
            base_args, capture_output=True, text=True, timeout=180
        )
        if result.returncode != 0 or not pdf_path.is_file():
            # Root/container environments (CI) need --no-sandbox; end-user
            # machines do not, so it is retry-only, never the default.
            retry = base_args[:1] + ["--no-sandbox"] + base_args[1:]
            result = subprocess.run(
                retry, capture_output=True, text=True, timeout=180
            )
        if result.returncode != 0 or not pdf_path.is_file():
            raise RuntimeError(
                f"Headless render failed (exit {result.returncode}): "
                f"{(result.stderr or '').strip()[-400:]}"
            )


def write_pdf(
    ir: DocumentIR, path: Path, log: Callable[[str], None] | None = None
) -> Path:
    say = log or (lambda _msg: None)
    html_content = render_html(ir)

    try:
        browser = find_browser()
    except BrowserNotFound:
        fallback = path.with_suffix(".html")
        fallback.write_text(html_content, encoding="utf-8")
        ir.warnings.append(
            "No Edge/Chrome/Chromium found, so the PDF could not be rendered. "
            f"Saved the styled HTML to {fallback} instead - open it in any "
            "browser and print to PDF with 'Print backgrounds' enabled."
        )
        say(ir.warnings[-1])
        return fallback

    say(f"Rendering PDF via {browser.name}")
    with tempfile.TemporaryDirectory(prefix="deccan-html-") as tmp:
        html_path = Path(tmp) / "document.html"
        html_path.write_text(html_content, encoding="utf-8")
        render_pdf_from_html(html_path, path, browser)
    return path
