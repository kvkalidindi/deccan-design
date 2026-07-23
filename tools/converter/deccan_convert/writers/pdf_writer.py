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
    # Chrome before Edge: Edge on macOS is unreliable in headless print mode
    # (it can hang without producing a PDF).
    apps = [
        "Google Chrome.app/Contents/MacOS/Google Chrome",
        "Chromium.app/Contents/MacOS/Chromium",
        "Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    roots = [Path("/Applications"), Path.home() / "Applications"]
    return [root / app for root in roots for app in apps]


def find_browsers() -> list[Path]:
    """All Chromium-family browsers on this machine, in preference order."""
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
    found: list[Path] = []
    env_override = os.environ.get("DECCAN_CONVERT_BROWSER")
    if env_override and Path(env_override).is_file():
        found.append(Path(env_override))
    for candidate in candidates:
        if candidate.is_file() and candidate not in found:
            found.append(candidate)
    for name in which_names:
        located = shutil.which(name)
        if located and Path(located) not in found:
            found.append(Path(located))
    return found


def find_browser() -> Path:
    browsers = find_browsers()
    if not browsers:
        raise BrowserNotFound(
            "No Microsoft Edge, Google Chrome, or Chromium installation was found."
        )
    return browsers[0]


def _run_render(args: list[str], log_path: Path) -> int:
    """Run a headless render without pipe capture.

    Chromium-family browsers (notably on macOS) leave helper processes
    holding the inherited stderr open after the main process exits; with
    capture_output=True, subprocess.run() then blocks on pipe EOF until the
    timeout even though the PDF was written. Redirecting to a file waits on
    the direct child only.
    """
    with open(log_path, "wb") as sink:
        result = subprocess.run(
            args, stdout=sink, stderr=subprocess.STDOUT, timeout=180
        )
    return result.returncode


def render_pdf_from_html(html_path: Path, pdf_path: Path, browser: Path) -> None:
    uri = html_path.resolve().as_uri()
    with tempfile.TemporaryDirectory(prefix="deccan-render-") as profile:
        base_args = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            # macOS: startup touches the system Keychain to set up cookie
            # encryption, which can block forever in headless/CI sessions.
            # Mock keychain + basic password store skip that path entirely
            # (no-ops on Windows/Linux).
            "--use-mock-keychain",
            "--password-store=basic",
            "--disable-sync",
            "--disable-extensions",
            "--mute-audio",
            # Security: block all network egress during the render. A correct
            # deccan document is fully self-contained (bundled CSS, inline
            # data: images), so nothing legitimate is fetched. This blackholes
            # any subresource that might survive input sanitization, defeating
            # beaconing / internal SSRF / tracking from an attacker document.
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--disable-features=Translate,OptimizationHints",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path.resolve()}",
            uri,
        ]
        log_path = Path(profile) / "render.log"
        returncode = _run_render(base_args, log_path)
        if returncode != 0 or not pdf_path.is_file():
            # The Chromium sandbox is a key defense when rendering untrusted
            # content, so --no-sandbox is never used automatically on an
            # end-user machine. Root/container CI images cannot run the
            # sandbox, so the retry is gated behind an explicit opt-in.
            if os.environ.get("DECCAN_CONVERT_ALLOW_NO_SANDBOX") == "1":
                retry = base_args[:1] + ["--no-sandbox"] + base_args[1:]
                returncode = _run_render(retry, log_path)
        if returncode != 0 or not pdf_path.is_file():
            tail = ""
            try:
                tail = log_path.read_text(errors="replace").strip()[-400:]
            except OSError:
                pass
            raise RuntimeError(f"Headless render failed (exit {returncode}): {tail}")


def write_pdf(
    ir: DocumentIR,
    path: Path,
    log: Callable[[str], None] | None = None,
    logo: bool = False,
) -> Path:
    say = log or (lambda _msg: None)
    html_content = render_html(ir, logo=logo)

    browsers = find_browsers()
    if not browsers:
        fallback = path.with_suffix(".html")
        fallback.write_text(html_content, encoding="utf-8")
        ir.warnings.append(
            "No Edge/Chrome/Chromium found, so the PDF could not be rendered. "
            f"Saved the styled HTML to {fallback} instead - open it in any "
            "browser and print to PDF with 'Print backgrounds' enabled."
        )
        say(ir.warnings[-1])
        return fallback

    with tempfile.TemporaryDirectory(prefix="deccan-html-") as tmp:
        html_path = Path(tmp) / "document.html"
        html_path.write_text(html_content, encoding="utf-8")
        last_error: Exception | None = None
        for browser in browsers:
            say(f"Rendering PDF via {browser.name}")
            try:
                render_pdf_from_html(html_path, path, browser)
                return path
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                # A browser can be present but broken for headless printing
                # (e.g. Edge on macOS hanging) — fall through to the next one.
                last_error = exc
                say(f"{browser.name} failed to render; trying the next browser")
    raise RuntimeError(f"All PDF render attempts failed: {last_error}")
