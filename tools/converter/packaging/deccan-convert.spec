# PyInstaller spec for deccan-convert — Windows 11 and macOS builds.
#
# Build (from tools/converter/):
#   pyinstaller packaging/deccan-convert.spec
#
# Windows: dist/deccan-convert.exe            (onefile, windowed)
# macOS:   dist/deccan-convert                (onefile binary)
#          dist/Deccan Convert.app            (app bundle for Finder users)
#
# Unsigned by design, mirroring the repo's MSI/PKG installers. Per-user,
# no admin rights needed to run.

import sys
from pathlib import Path

SPEC_DIR = Path(SPECPATH).resolve()
PKG_DIR = SPEC_DIR.parent

# Single source of truth for the shipped version — the updater compares the
# release tag against it, so a stale literal here would make macOS builds
# advertise the wrong version in Finder.
sys.path.insert(0, str(PKG_DIR))
from deccan_convert import __version__ as APP_VERSION

block_cipher = None

_icon_ico = SPEC_DIR / "icon.ico"
_icon_icns = SPEC_DIR / "icon.icns"

a = Analysis(
    [str(PKG_DIR / "deccan_convert" / "__main__.py")],
    pathex=[str(PKG_DIR)],
    binaries=[],
    datas=[(str(PKG_DIR / "deccan_convert" / "assets_data"), "assets_data")],
    hiddenimports=[
        # lazy imports inside the dispatchers
        "deccan_convert.cli",
        "deccan_convert.gui",
        "deccan_convert.update",
        "deccan_convert.readers.md_reader",
        "deccan_convert.readers.html_reader",
        "deccan_convert.readers.docx_reader",
        "deccan_convert.readers.pdf_reader",
        "deccan_convert.writers.html_writer",
        "deccan_convert.writers.md_writer",
        "deccan_convert.writers.docx_writer",
        "deccan_convert.writers.pdf_writer",
        "deccan_convert.writers.xlsx_writer",
        "deccan_convert.writers.pptx_writer",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "PIL.ImageQt"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="deccan-convert",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # Windowed: double-click opens the GUI without a console flash. CLI use
    # writes a .log beside the output when no console is attached.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(_icon_ico) if sys.platform == "win32" and _icon_ico.is_file() else (
        str(_icon_icns) if sys.platform == "darwin" and _icon_icns.is_file() else None
    ),
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="Deccan Convert.app",
        icon=str(_icon_icns) if _icon_icns.is_file() else None,
        bundle_identifier="com.deccanchemicals.deccan-convert",
        info_plist={
            "CFBundleShortVersionString": APP_VERSION,
            "NSHighResolutionCapable": True,
        },
    )
