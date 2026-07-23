"""deccan-design v2.0 tokens for the template build/verify scripts.

Single source: skill/references/tokens.md. Opacity blends are the RGBA
tiers of Deccan Blue composited on paper (#FFFFFF), since OOXML has no
alpha-on-solid concept.
"""

DECCAN_BLUE = "164999"
BLUE_90 = "2D5BA3"   # rgba(22,73,153,.90) on white
BLUE_60 = "7392C2"   # .60 on white
BLUE_30 = "B9C8E0"   # .30 on white
BLUE_15 = "DCE4F0"   # .15 on white
DECCAN_GREEN = "71BF4D"  # logo + sustainability content ONLY — never written by these scripts

STONE = {
    50: "FAFAF9", 100: "F5F5F4", 200: "E7E5E4", 300: "D6D3D1", 400: "A8A29E",
    500: "78716C", 600: "57534E", 700: "44403C", 800: "292524", 900: "1C1917",
}
PAPER = "FFFFFF"

SANS_DISPLAY = "Segoe UI Variable Display"
SANS_TEXT = "Segoe UI Variable Text"
MONO = "Cascadia Mono"

FOOTER_TEXT = "Deccan Fine Chemicals · Confidential"
COMPANY = "Deccan Fine Chemicals"

# Banned faces (tokens.md + SKILL.md). "Courier" also matches "Courier New".
# Cambria is not on the published ban list but is the stale Office theme serif;
# the verify scan treats it as banned so the stock theme can never creep back.
BANNED_FACES = [
    "Helvetica", "Univers", "Arial", "Calibri", "Cambria", "Verdana",
    "Times", "Garamond", "Georgia", "Courier", "Lucida Console",
]

# Stale Office hexes that must not appear anywhere after remediation.
STALE_HEXES = [
    "4F81BD", "1F497D", "243F60", "17365D", "365F91",   # office blues
    "C0504D", "943634", "9E3A38",                        # reds
    "9BBB59", "76923C", "7E9C40",                        # office greens
    "8064A2", "5F497A", "664E82",                        # purples
    "4BACC6", "31849B", "348DA5",                        # teals
    "F79646", "E36C0A", "F2730A",                        # oranges
    "EEECE1",                                            # stock lt2
    "0000FF", "800080",                                  # stock hyperlink colours
]

# Deterministic remap for Word styles.xml gallery styles. The system is
# single-accent: every foreign accent hue collapses to Deccan Blue.
HEX_REMAP = {
    "17365D": DECCAN_BLUE,
    "1F497D": DECCAN_BLUE,
    "4F81BD": DECCAN_BLUE,
    "365F91": DECCAN_BLUE,
    "243F60": BLUE_90,
    "C0504D": DECCAN_BLUE,
    "943634": DECCAN_BLUE,
    "9E3A38": DECCAN_BLUE,
    "9BBB59": DECCAN_BLUE,
    "76923C": DECCAN_BLUE,
    "7E9C40": DECCAN_BLUE,
    "8064A2": DECCAN_BLUE,
    "5F497A": DECCAN_BLUE,
    "664E82": DECCAN_BLUE,
    "4BACC6": DECCAN_BLUE,
    "31849B": DECCAN_BLUE,
    "348DA5": DECCAN_BLUE,
    "F79646": DECCAN_BLUE,
    "E36C0A": DECCAN_BLUE,
    "F2730A": DECCAN_BLUE,
    "404040": STONE[700],
    "808080": STONE[500],
    "EEECE1": STONE[100],
    "0000FF": DECCAN_BLUE,
    "800080": BLUE_60,
}

# The only hexes allowed to remain in a remediated styles.xml.
ALLOWED_HEXES = {
    DECCAN_BLUE, BLUE_90, BLUE_60, BLUE_30, BLUE_15,
    *STONE.values(), PAPER, "000000", "auto",
}


def tint_fallback(hex_value: str) -> str:
    """Map a leftover light tint deterministically: bluish -> blue/15 wash,
    otherwise the stone-100 fill."""
    r, g, b = (int(hex_value[i : i + 2], 16) for i in (0, 2, 4))
    return BLUE_15 if b > r and b >= g else STONE[100]


# Canonical theme fragments — replace the <a:clrScheme> and <a:fontScheme>
# elements of every template's theme1.xml. srgbClr everywhere (no sysClr) so
# exports are deterministic. The stock per-script fallback font lists are
# dropped: they carry Times New Roman / Arial.
CLR_SCHEME = (
    '<a:clrScheme name="Deccan">'
    f'<a:dk1><a:srgbClr val="{STONE[900]}"/></a:dk1>'
    f'<a:lt1><a:srgbClr val="{PAPER}"/></a:lt1>'
    f'<a:dk2><a:srgbClr val="{STONE[700]}"/></a:dk2>'
    f'<a:lt2><a:srgbClr val="{STONE[100]}"/></a:lt2>'
    f'<a:accent1><a:srgbClr val="{DECCAN_BLUE}"/></a:accent1>'
    f'<a:accent2><a:srgbClr val="{BLUE_90}"/></a:accent2>'
    f'<a:accent3><a:srgbClr val="{BLUE_60}"/></a:accent3>'
    f'<a:accent4><a:srgbClr val="{BLUE_30}"/></a:accent4>'
    f'<a:accent5><a:srgbClr val="{BLUE_15}"/></a:accent5>'
    f'<a:accent6><a:srgbClr val="{STONE[500]}"/></a:accent6>'
    f'<a:hlink><a:srgbClr val="{DECCAN_BLUE}"/></a:hlink>'
    f'<a:folHlink><a:srgbClr val="{BLUE_60}"/></a:folHlink>'
    "</a:clrScheme>"
)

FONT_SCHEME = (
    '<a:fontScheme name="Deccan">'
    "<a:majorFont>"
    f'<a:latin typeface="{SANS_DISPLAY}"/>'
    '<a:ea typeface=""/><a:cs typeface=""/>'
    "</a:majorFont>"
    "<a:minorFont>"
    f'<a:latin typeface="{SANS_TEXT}"/>'
    '<a:ea typeface=""/><a:cs typeface=""/>'
    "</a:minorFont>"
    "</a:fontScheme>"
)
