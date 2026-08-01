"""Self-updater tests. No network: the transport is stubbed at _fetch."""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error

import pytest

from deccan_convert import update as up


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Keep the check-stamp out of the developer's real profile."""
    monkeypatch.setattr(up, "_state_dir", lambda: tmp_path / "state")
    yield


def _release(tag, assets, draft=False, prerelease=False):
    return {
        "tag_name": tag,
        "draft": draft,
        "prerelease": prerelease,
        "html_url": f"https://github.com/{up.REPO}/releases/tag/{tag}",
        "assets": [
            {"name": name, "browser_download_url": f"https://github.com/{up.REPO}/releases/download/{tag}/{name}"}
            for name in assets
        ],
    }


WIN_ASSET = up.ASSET_NAMES["win32"]
BOTH = [WIN_ASSET, up.ASSET_NAMES["darwin"], up.CHECKSUMS_ASSET]


class TestVersionComparison:
    @pytest.mark.parametrize(
        "candidate,current,expected",
        [
            ("1.0.3", "1.0.2", True),
            ("1.0.2", "1.0.2", False),
            ("1.0.1", "1.0.2", False),
            ("1.0.10", "1.0.9", True),   # not a string comparison
            ("1.10.0", "1.9.9", True),
            ("2.0.0", "1.99.99", True),
            ("1.1.0rc1", "1.0.9", True),  # suffixes are tolerated, not ranked
        ],
    )
    def test_is_newer(self, candidate, current, expected):
        assert up.is_newer(candidate, current) is expected

    def test_garbage_never_looks_newer(self):
        assert up.is_newer("not-a-version", "1.0.0") is False


class TestFindUpdate:
    @pytest.fixture(autouse=True)
    def as_windows(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")

    def _stub(self, monkeypatch, releases):
        monkeypatch.setattr(
            up, "_fetch",
            lambda url, max_bytes, digest=False: (json.dumps(releases).encode(), ""),
        )

    def test_picks_newest_converter_release(self, monkeypatch):
        self._stub(monkeypatch, [
            _release("converter-v1.0.2", BOTH),
            _release("converter-v1.2.0", BOTH),
            _release("converter-v1.1.0", BOTH),
        ])
        found = up.find_update(current="1.0.2")
        assert found is not None
        assert (found.version, found.asset_name) == ("1.2.0", WIN_ASSET)

    def test_ignores_design_system_releases(self, monkeypatch):
        """A v2.0.2 design-system tag is not a converter build."""
        self._stub(monkeypatch, [_release("v2.0.2", ["deccan-design-skill-bundle.zip", up.CHECKSUMS_ASSET])])
        assert up.find_update(current="1.0.2") is None

    def test_ignores_drafts_and_prereleases(self, monkeypatch):
        self._stub(monkeypatch, [
            _release("converter-v2.0.0", BOTH, draft=True),
            _release("converter-v1.9.0", BOTH, prerelease=True),
        ])
        assert up.find_update(current="1.0.2") is None

    def test_release_without_checksums_is_not_an_update(self, monkeypatch):
        self._stub(monkeypatch, [_release("converter-v1.3.0", [WIN_ASSET])])
        assert up.find_update(current="1.0.2") is None

    def test_current_version_yields_nothing(self, monkeypatch):
        self._stub(monkeypatch, [_release("converter-v1.0.2", BOTH)])
        assert up.find_update(current="1.0.2") is None


class TestDownloadVerification:
    def _update(self):
        return up.Update(
            version="1.3.0", tag="converter-v1.3.0", asset_name=WIN_ASSET,
            asset_url=f"https://github.com/{up.REPO}/releases/download/converter-v1.3.0/{WIN_ASSET}",
            checksums_url=f"https://github.com/{up.REPO}/releases/download/converter-v1.3.0/{up.CHECKSUMS_ASSET}",
            page_url="",
        )

    def _stub(self, monkeypatch, payload: bytes, sums: str):
        def fake_fetch(url, max_bytes, digest=False):
            if url.endswith(up.CHECKSUMS_ASSET):
                return sums.encode(), ""
            return payload, hashlib.sha256(payload).hexdigest()
        monkeypatch.setattr(up, "_fetch", fake_fetch)

    def test_matching_checksum_stages_the_asset(self, monkeypatch, tmp_path):
        payload = b"new build"
        sums = f"{hashlib.sha256(payload).hexdigest()}  {WIN_ASSET}\n"
        self._stub(monkeypatch, payload, sums)
        staged = up.download(self._update(), tmp_path / "staging")
        assert staged.read_bytes() == payload

    def test_mismatched_checksum_aborts(self, monkeypatch, tmp_path):
        self._stub(monkeypatch, b"tampered", f"{'0' * 64}  {WIN_ASSET}\n")
        with pytest.raises(up.UpdateError, match="checksum mismatch"):
            up.download(self._update(), tmp_path / "staging")
        assert not (tmp_path / "staging" / WIN_ASSET).exists()

    def test_asset_absent_from_checksums_aborts(self, monkeypatch, tmp_path):
        self._stub(monkeypatch, b"x", f"{'a' * 64}  something-else.exe\n")
        with pytest.raises(up.UpdateError, match="no SHA-256"):
            up.download(self._update(), tmp_path / "staging")

    def test_expected_digest_parsing(self):
        text = (
            "1111111111111111111111111111111111111111111111111111111111111111  a.exe\n"
            "2222222222222222222222222222222222222222222222222222222222222222 *b.zip\n"
            "not-a-digest  c.exe\n"
        )
        assert up.expected_digest(text, "a.exe") == "1" * 64
        assert up.expected_digest(text, "b.zip") == "2" * 64  # binary-mode marker
        assert up.expected_digest(text, "c.exe") is None
        assert up.expected_digest(text, "missing.exe") is None


class TestUrlPolicy:
    @pytest.mark.parametrize("url", [
        "http://github.com/x",                       # plaintext
        "https://evil.example.com/deccan.exe",       # off-GitHub
        "https://github.com.evil.example/deccan.exe",
    ])
    def test_rejected(self, url):
        with pytest.raises(up.UpdateError):
            up._check_url(url)

    @pytest.mark.parametrize("url", [
        "https://api.github.com/repos/x/y/releases",
        "https://github.com/x/y/releases/download/t/a.exe",
        "https://objects.githubusercontent.com/blob",
        "https://release-assets.githubusercontent.com/blob",
    ])
    def test_allowed(self, url):
        up._check_url(url)


class TestOptOut:
    def test_disabled_when_not_frozen(self):
        assert up.disabled_reason() == "not a packaged build"

    def test_flag_wins_before_anything_else(self):
        assert up.disabled_reason(no_update=True) == "--no-update"

    def test_env_var(self, monkeypatch):
        monkeypatch.setenv(up.ENV_DISABLE, "1")
        assert up.disabled_reason() == f"{up.ENV_DISABLE} is set"

    def test_env_var_off_values_do_not_disable(self, monkeypatch):
        monkeypatch.setenv(up.ENV_DISABLE, "0")
        assert up.disabled_reason() == "not a packaged build"  # falls through

    def test_marker_file_beside_the_binary(self, monkeypatch, tmp_path):
        target = tmp_path / "deccan-convert.exe"
        target.write_bytes(b"binary")
        (tmp_path / up.MARKER_FILE).touch()
        monkeypatch.setattr(up, "install_target", lambda: target)
        monkeypatch.setattr(sys, "platform", "win32")
        assert up.disabled_reason() == f"{up.MARKER_FILE} marker present"

    def test_prepare_returns_none_when_disabled(self, monkeypatch):
        called = []
        monkeypatch.setattr(up, "find_update", lambda *a, **k: called.append(1))
        assert up.prepare(force=True) is None
        assert not called

    def test_start_background_returns_none_when_disabled(self):
        assert up.start_background() is None


class TestThrottle:
    def test_first_run_checks(self):
        assert up.due_for_check() is True

    def test_recent_check_is_skipped(self, monkeypatch):
        up._write_state({"last_check": 1000.0})
        assert up.due_for_check(now=1000.0 + 60) is False
        assert up.due_for_check(now=1000.0 + up.CHECK_INTERVAL_SECONDS + 1) is True

    def test_unreadable_state_means_check(self, monkeypatch):
        monkeypatch.setattr(up, "_read_state", lambda: {"last_check": "corrupt"})
        assert up.due_for_check() is True


class TestApplyStaged:
    def test_swaps_binary_and_keeps_the_old_one(self, tmp_path):
        target = tmp_path / "deccan-convert.exe"
        target.write_bytes(b"old build")
        staged = tmp_path / "staging" / "deccan-convert-windows-x64.exe"
        staged.parent.mkdir()
        staged.write_bytes(b"new build")

        assert up.apply_staged(staged, target) is True
        assert target.read_bytes() == b"new build"
        assert (tmp_path / "deccan-convert.exe.old").read_bytes() == b"old build"

    def test_second_update_replaces_the_previous_old_copy(self, tmp_path):
        target = tmp_path / "deccan-convert.exe"
        target.write_bytes(b"v1")
        (tmp_path / "deccan-convert.exe.old").write_bytes(b"v0")
        staged = tmp_path / "s" / "deccan-convert-windows-x64.exe"
        staged.parent.mkdir()
        staged.write_bytes(b"v2")

        assert up.apply_staged(staged, target) is True
        assert (tmp_path / "deccan-convert.exe.old").read_bytes() == b"v1"

    def test_failure_leaves_the_installed_build_in_place(self, tmp_path, monkeypatch):
        target = tmp_path / "deccan-convert.exe"
        target.write_bytes(b"old build")
        staged = tmp_path / "s" / "deccan-convert-windows-x64.exe"
        staged.parent.mkdir()
        staged.write_bytes(b"new build")

        def boom(*_a, **_k):
            raise OSError("disk full")
        monkeypatch.setattr(up.shutil, "move", boom)

        assert up.apply_staged(staged, target) is False
        assert target.read_bytes() == b"old build"

    def test_missing_staged_file_is_not_a_crash(self, tmp_path):
        target = tmp_path / "deccan-convert.exe"
        target.write_bytes(b"old build")
        assert up.apply_staged(tmp_path / "s" / "absent.exe", target) is False
        assert target.read_bytes() == b"old build"

    def test_cleanup_removes_the_old_build(self, tmp_path):
        target = tmp_path / "deccan-convert.exe"
        target.write_bytes(b"current")
        old = tmp_path / "deccan-convert.exe.old"
        old.write_bytes(b"previous")
        up.cleanup_previous(target)
        assert not old.exists() and target.exists()

    def test_cleanup_with_nothing_to_clean(self, tmp_path):
        up.cleanup_previous(tmp_path / "deccan-convert.exe")  # must not raise


class TestInstallTarget:
    def test_none_when_running_from_source(self):
        assert up.install_target() is None

    def test_macos_app_bundle_is_the_target(self, monkeypatch, tmp_path):
        inner = tmp_path / "Deccan Convert.app" / "Contents" / "MacOS"
        inner.mkdir(parents=True)
        exe = inner / "deccan-convert"
        exe.write_bytes(b"binary")
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "executable", str(exe))
        assert up.install_target() == tmp_path / "Deccan Convert.app"

    def test_plain_binary_is_its_own_target(self, monkeypatch, tmp_path):
        exe = tmp_path / "deccan-convert.exe"
        exe.write_bytes(b"binary")
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "executable", str(exe))
        assert up.install_target() == exe


class TestFullCycle:
    """check -> download -> verify -> swap, against a stand-in installation."""

    @pytest.fixture
    def installed(self, tmp_path, monkeypatch):
        target = tmp_path / "install" / "deccan-convert.exe"
        target.parent.mkdir()
        target.write_bytes(b"installed 1.0.2")
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr(up, "install_target", lambda: target)
        return target

    def _serve(self, monkeypatch, payload: bytes, sums_digest: str | None = None):
        releases = [_release("converter-v1.3.0", BOTH)]
        digest = sums_digest or hashlib.sha256(payload).hexdigest()

        def fake_fetch(url, max_bytes, digest_wanted=False, **kw):
            if url.startswith(up.RELEASES_URL[:40]) and "releases?" in url:
                return json.dumps(releases).encode(), ""
            if url.endswith(up.CHECKSUMS_ASSET):
                return f"{digest}  {WIN_ASSET}\n".encode(), ""
            return payload, hashlib.sha256(payload).hexdigest()

        monkeypatch.setattr(
            up, "_fetch",
            lambda url, max_bytes, digest=False: fake_fetch(url, max_bytes, digest),
        )

    def test_new_release_is_staged_and_installed(self, installed, monkeypatch):
        self._serve(monkeypatch, b"installed 1.3.0")
        staged = up.prepare(force=True)
        assert staged is not None and staged.update.version == "1.3.0"
        assert up.apply_staged(staged.path, staged.target) is True
        assert installed.read_bytes() == b"installed 1.3.0"
        assert installed.with_name(installed.name + ".old").read_bytes() == b"installed 1.0.2"

    def test_tampered_asset_never_reaches_disk(self, installed, monkeypatch):
        self._serve(monkeypatch, b"trojan", sums_digest="0" * 64)
        assert up.prepare(force=True) is None
        assert installed.read_bytes() == b"installed 1.0.2"

    def test_network_failure_is_a_non_event(self, installed, monkeypatch):
        def boom(*_a, **_k):
            raise urllib.error.URLError("proxy refused")
        monkeypatch.setattr(up, "_fetch", boom)
        assert up.prepare(force=True) is None
        assert installed.read_bytes() == b"installed 1.0.2"

    def test_throttle_skips_an_unforced_check(self, installed, monkeypatch):
        self._serve(monkeypatch, b"installed 1.3.0")
        up._write_state({"last_check": time.time()})
        assert up.prepare() is None
        assert installed.read_bytes() == b"installed 1.0.2"


class TestCliIntegration:
    def test_conversion_still_runs_with_updates_disabled(self, sample_md, tmp_path, monkeypatch):
        """The updater must be invisible to a normal scripted run."""
        monkeypatch.setenv(up.ENV_DISABLE, "1")
        from deccan_convert.cli import run_cli

        out = tmp_path / "out.html"
        assert run_cli([str(sample_md), "-o", str(out)]) == 0
        assert out.is_file()

    def test_check_update_reports_and_exits(self, capsys, monkeypatch):
        from deccan_convert.cli import run_cli

        monkeypatch.setenv(up.ENV_DISABLE, "1")
        assert run_cli(["--check-update"]) == 0
        assert "skipped" in capsys.readouterr().out.lower()

    def test_no_update_flag_parses(self):
        from deccan_convert.cli import build_parser

        args = build_parser().parse_args(["in.md", "-o", "out.html", "--no-update"])
        assert args.no_update is True
