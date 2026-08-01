"""Self-update: check the pinned GitHub releases on launch, replace the binary.

Deccan Convert ships as a downloaded, unsigned, per-user binary. There is no
package manager behind it, so without an updater an endpoint keeps whatever
build it first downloaded — including the design kit frozen inside it — until
somebody re-downloads by hand. That is how a fleet ends up generating
documents from a superseded slot template.

The update path is deliberately narrow:

- One source: the `converter-v*` releases of the pinned repository, over
  HTTPS, with the host restricted to GitHub.
- One artifact per platform, matched by exact file name.
- Every download is verified against the SHA-256 recorded in that release's
  own `SHA256SUMS.txt` before anything on disk is touched. A mismatch aborts
  and leaves the installed build alone.
- The verified artifact replaces the running one by rename; the previous
  build stays alongside as `.old` until a later launch cleans it up.

Nothing here executes downloaded code. The new binary runs only when the
user next launches the app (or when an idle GUI relaunches itself), never
in the middle of a conversion.

Failures are non-events: every entry point returns None / False instead of
raising, so an offline endpoint, a TLS-intercepting proxy, or a GitHub rate
limit costs a conversion nothing.

Opt out with `--no-update`, `DECCAN_CONVERT_NO_UPDATE=1`, or a
`.no-auto-update` marker file beside the binary — the last one is for fleets
where Intune or Jamf owns the installed version.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from deccan_convert import __version__

REPO = "kvkalidindi/deccan-design"
RELEASES_URL = f"https://api.github.com/repos/{REPO}/releases?per_page=20"
TAG_PREFIX = "converter-v"
CHECKSUMS_ASSET = "SHA256SUMS.txt"

# Exactly what release-converter.yml publishes, per platform.
ASSET_NAMES = {
    "win32": "deccan-convert-windows-x64.exe",
    "darwin": "deccan-convert-macos-arm64.zip",
}

# Release downloads redirect from github.com to a githubusercontent host.
_ALLOWED_HOSTS = frozenset({"github.com", "api.github.com"})
_ALLOWED_HOST_SUFFIX = ".githubusercontent.com"

NET_TIMEOUT = 8.0
MAX_ASSET_BYTES = 200 * 1024 * 1024
MAX_METADATA_BYTES = 4 * 1024 * 1024
CHECK_INTERVAL_SECONDS = 24 * 3600
MARKER_FILE = ".no-auto-update"
ENV_DISABLE = "DECCAN_CONVERT_NO_UPDATE"


class UpdateError(Exception):
    """Internal signal — never escapes this module's public functions."""


@dataclass(frozen=True)
class Update:
    version: str
    tag: str
    asset_name: str
    asset_url: str
    checksums_url: str
    page_url: str


@dataclass
class Staged:
    """A verified artifact waiting to replace the installed build."""

    update: Update
    path: Path
    target: Path


# --------------------------------------------------------------------------
# Where we are installed, and whether we are allowed to touch it
# --------------------------------------------------------------------------

def install_target() -> Path | None:
    """The path a new build replaces, or None when not a packaged build.

    On macOS the running executable lives inside `Deccan Convert.app`; the
    bundle directory is what gets swapped, not the inner binary.
    """
    if not getattr(sys, "frozen", False):
        return None
    exe = Path(sys.executable).resolve()
    for parent in exe.parents:
        if parent.suffix == ".app":
            return parent
    return exe


def disabled_reason(no_update: bool = False) -> str | None:
    """Why updates are off, or None when they are on."""
    if no_update:
        return "--no-update"
    if os.environ.get(ENV_DISABLE, "").strip() not in ("", "0", "false", "no"):
        return f"{ENV_DISABLE} is set"
    target = install_target()
    if target is None:
        return "not a packaged build"
    if sys.platform not in ASSET_NAMES:
        return f"no release artifact for {sys.platform}"
    if (target.parent / MARKER_FILE).exists():
        return f"{MARKER_FILE} marker present"
    if not os.access(target.parent, os.W_OK):
        return "install directory is not writable"
    return None


def _state_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "deccan-design" / "convert"


def _read_state() -> dict:
    try:
        return json.loads((_state_dir() / "update-state.json").read_text("utf-8"))
    except (OSError, ValueError):
        return {}


def _write_state(state: dict) -> None:
    try:
        path = _state_dir()
        path.mkdir(parents=True, exist_ok=True)
        (path / "update-state.json").write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass  # a read-only profile just means we check every launch


def due_for_check(now: float | None = None, interval: float = CHECK_INTERVAL_SECONDS) -> bool:
    """True when the last check is older than the interval.

    Throttled because unauthenticated GitHub API calls are rate-limited per
    source address — a NAT'd office would otherwise burn the quota by lunch.
    """
    last = _read_state().get("last_check")
    if not isinstance(last, (int, float)):
        return True
    return (time.time() if now is None else now) - last >= interval


# --------------------------------------------------------------------------
# Version comparison
# --------------------------------------------------------------------------

def _version_tuple(text: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in text.strip().lstrip("v").split("."):
        digits = ""
        for ch in chunk:
            if not ch.isdigit():
                break
            digits += ch
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) or (0,)


def is_newer(candidate: str, current: str = __version__) -> bool:
    return _version_tuple(candidate) > _version_tuple(current)


# --------------------------------------------------------------------------
# Network
# --------------------------------------------------------------------------

def _check_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise UpdateError(f"refusing non-HTTPS url: {url}")
    if host not in _ALLOWED_HOSTS and not host.endswith(_ALLOWED_HOST_SUFFIX):
        raise UpdateError(f"refusing off-GitHub host: {host}")


def _fetch(url: str, max_bytes: int, digest: bool = False) -> tuple[bytes, str]:
    """GET a URL, capped, optionally hashing as it streams.

    Release downloads redirect off github.com to a githubusercontent host, so
    the URL the response actually came from is checked too — a redirect that
    leaves GitHub fails before a byte is read.
    """
    _check_url(url)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/octet-stream, application/vnd.github+json",
            "User-Agent": f"deccan-convert/{__version__}",
        },
    )
    sha = hashlib.sha256()
    chunks: list[bytes] = []
    total = 0
    with urllib.request.urlopen(request, timeout=NET_TIMEOUT) as response:
        _check_url(response.geturl())
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise UpdateError(f"asset exceeds {max_bytes // 1048576} MB cap")
            chunks.append(chunk)
            if digest:
                sha.update(chunk)
    return b"".join(chunks), (sha.hexdigest() if digest else "")


def find_update(current: str = __version__) -> Update | None:
    """The newest `converter-v*` release that is newer than `current`."""
    asset_name = ASSET_NAMES.get(sys.platform)
    if not asset_name:
        return None  # no artifact for this platform — do not even ask GitHub
    payload, _ = _fetch(RELEASES_URL, MAX_METADATA_BYTES)
    releases = json.loads(payload.decode("utf-8"))

    best: Update | None = None
    for release in releases:
        tag = release.get("tag_name") or ""
        if not tag.startswith(TAG_PREFIX) or release.get("draft") or release.get("prerelease"):
            continue
        version = tag[len(TAG_PREFIX):]
        if not is_newer(version, current):
            continue
        if best is not None and not is_newer(version, best.version):
            continue
        assets = {a.get("name"): a.get("browser_download_url") for a in release.get("assets", [])}
        if asset_name not in assets or CHECKSUMS_ASSET not in assets:
            continue  # an incomplete release is not an update
        best = Update(
            version=version,
            tag=tag,
            asset_name=asset_name,
            asset_url=assets[asset_name],
            checksums_url=assets[CHECKSUMS_ASSET],
            page_url=release.get("html_url", ""),
        )
    return best


def expected_digest(checksums_text: str, asset_name: str) -> str | None:
    """Pull one asset's SHA-256 out of a `sha256sum` listing."""
    for line in checksums_text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == asset_name:
            candidate = parts[0].strip().lower()
            if len(candidate) == 64 and all(c in "0123456789abcdef" for c in candidate):
                return candidate
    return None


def download(update: Update, into: Path) -> Path:
    """Download and verify one release artifact. Raises UpdateError on any doubt."""
    checksums, _ = _fetch(update.checksums_url, MAX_METADATA_BYTES)
    want = expected_digest(checksums.decode("utf-8", "replace"), update.asset_name)
    if not want:
        raise UpdateError(f"no SHA-256 for {update.asset_name} in {CHECKSUMS_ASSET}")

    payload, got = _fetch(update.asset_url, MAX_ASSET_BYTES, digest=True)
    if got != want:
        raise UpdateError(f"checksum mismatch for {update.asset_name}: {got} != {want}")

    into.mkdir(parents=True, exist_ok=True)
    staged = into / update.asset_name
    staged.write_bytes(payload)
    return staged


# --------------------------------------------------------------------------
# Applying
# --------------------------------------------------------------------------

def cleanup_previous(target: Path | None = None) -> None:
    """Remove the `.old` build a previous update left behind. Best effort."""
    target = target or install_target()
    if target is None:
        return
    old = target.with_name(target.name + ".old")
    try:
        if old.is_dir():
            shutil.rmtree(old, ignore_errors=True)
        elif old.exists():
            old.unlink()
    except OSError:
        pass  # still running from it, or locked — next launch tries again


def _unpack_app(archive: Path, into: Path) -> Path:
    """Extract a macOS .app zip, preserving the executable bit.

    `ditto` is used in preference to zipfile: the standard library drops
    permission bits, which would leave Contents/MacOS/deccan-convert
    non-executable and the bundle dead on arrival.
    """
    into.mkdir(parents=True, exist_ok=True)
    if shutil.which("ditto"):
        subprocess.run(
            ["ditto", "-x", "-k", str(archive), str(into)],
            check=True, capture_output=True, timeout=180,
        )
    else:
        import zipfile

        with zipfile.ZipFile(archive) as zf:
            zf.extractall(into)
        for path in into.rglob("Contents/MacOS/*"):
            if path.is_file():
                path.chmod(0o755)
    apps = [p for p in into.iterdir() if p.suffix == ".app"]
    if not apps:
        raise UpdateError("downloaded archive contains no .app bundle")
    return apps[0]


def apply_staged(staged: Path, target: Path) -> bool:
    """Swap the verified artifact into place. True when the swap happened.

    The running build is renamed aside rather than deleted: on Windows the
    executing image cannot be overwritten but can be renamed, and on either
    platform the `.old` copy is what a failed swap is rolled back from.
    """
    workdir = staged.parent
    try:
        replacement = staged
        if target.suffix == ".app":
            replacement = _unpack_app(staged, workdir / "unpacked")

        old = target.with_name(target.name + ".old")
        if old.is_dir():
            shutil.rmtree(old, ignore_errors=True)
        elif old.exists():
            old.unlink()

        target.rename(old)
        try:
            shutil.move(str(replacement), str(target))
            if target.is_file():
                target.chmod(0o755)
        except OSError:
            if not target.exists():
                old.rename(target)  # put the old build back
            raise
        return True
    except (OSError, UpdateError, subprocess.SubprocessError):
        return False


def relaunch(target: Path, args: list[str] | None = None) -> bool:
    """Start the freshly installed build and let this process exit."""
    try:
        if target.suffix == ".app":
            subprocess.Popen(["/usr/bin/open", "-n", str(target)], close_fds=True)
        else:
            subprocess.Popen([str(target), *(args or [])], close_fds=True)
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def prepare(force: bool = False, no_update: bool = False) -> Staged | None:
    """Check, download, verify, stage. Returns None when there is nothing to do.

    Safe to call from a daemon thread on launch: it never raises, and it
    touches nothing on disk beyond a temp directory and the check stamp.
    """
    reason = disabled_reason(no_update)
    if reason is not None:
        return None
    if not force and not due_for_check():
        return None
    target = install_target()
    if target is None:
        return None
    try:
        _write_state({**_read_state(), "last_check": time.time()})
        update = find_update()
        if update is None:
            return None
        staged = download(update, Path(tempfile.mkdtemp(prefix="deccan-convert-update-")))
        return Staged(update=update, path=staged, target=target)
    except (UpdateError, urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        return None
    except Exception:  # a surprise here must never break a conversion
        return None


def start_background(no_update: bool = False) -> "_BackgroundCheck | None":
    """Kick off prepare() on a daemon thread; poll the handle for the result."""
    if disabled_reason(no_update) is not None:
        return None
    handle = _BackgroundCheck()
    handle.start()
    return handle


class _BackgroundCheck:
    def __init__(self) -> None:
        self.result: Staged | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        self.result = prepare()

    def start(self) -> None:
        self._thread.start()

    def done(self) -> bool:
        return not self._thread.is_alive()

    def wait(self, timeout: float) -> Staged | None:
        self._thread.join(timeout)
        return self.result if self.done() else None
