#!/bin/bash
# deccan-design v2.0 — Outlook signature configuration for new Outlook for Mac.
#
# Reads the unconfigured signature template installed by the .pkg, prompts for
# Name / Role / Email / Phone, substitutes the placeholders, and writes a
# configured signature to the Outlook signatures directory.
#
# Idempotent — running again overwrites the previous configuration.
#
# Repository: https://github.com/kvkalidindi/deccan-design

set -e

USER_HOME="${HOME:-$(eval echo "~$USER")}"
SIGS_DIR="${SIGNATURES_DIR:-$USER_HOME/Library/Containers/com.microsoft.Outlook/Data/Library/Signatures}"

HTML_TEMPLATE="$SIGS_DIR/deccan-signature-template.htm"
TXT_TEMPLATE="$SIGS_DIR/deccan-signature-template.txt"
HTML_OUT="$SIGS_DIR/Deccan.htm"
TXT_OUT="$SIGS_DIR/Deccan.txt"

if [ ! -f "$HTML_TEMPLATE" ]; then
    echo "Error: signature template not found at:"
    echo "  $HTML_TEMPLATE"
    echo ""
    echo "Has the deccan-design .pkg been installed? Re-run the installer."
    exit 1
fi

echo ""
echo "deccan-design v2.0 — Outlook signature configuration"
echo "-----------------------------------------------------"
echo ""

prompt_nonempty() {
    local prompt="$1"
    local var=""
    while [ -z "$var" ]; do
        read -r -p "$prompt: " var
        if [ -z "$var" ]; then
            echo "  Value is required."
        fi
    done
    echo "$var"
}

NAME="$(prompt_nonempty 'Your full name')"
ROLE="$(prompt_nonempty 'Your role / title')"
EMAIL="$(prompt_nonempty 'Your work email')"
PHONE="$(prompt_nonempty 'Office line')"

html_escape() {
    printf '%s' "$1" \
        | sed -e 's/&/\&amp;/g' \
              -e 's/</\&lt;/g' \
              -e 's/>/\&gt;/g' \
              -e 's/"/\&quot;/g'
}

E_NAME=$(html_escape "$NAME")
E_ROLE=$(html_escape "$ROLE")
E_EMAIL=$(html_escape "$EMAIL")
E_PHONE=$(html_escape "$PHONE")

sed -e "s|{{NAME}}|$E_NAME|g" \
    -e "s|{{ROLE}}|$E_ROLE|g" \
    -e "s|{{EMAIL}}|$E_EMAIL|g" \
    -e "s|{{PHONE}}|$E_PHONE|g" \
    "$HTML_TEMPLATE" > "$HTML_OUT"

if [ -f "$TXT_TEMPLATE" ]; then
    sed -e "s|{{NAME}}|$NAME|g" \
        -e "s|{{ROLE}}|$ROLE|g" \
        -e "s|{{EMAIL}}|$EMAIL|g" \
        -e "s|{{PHONE}}|$PHONE|g" \
        "$TXT_TEMPLATE" > "$TXT_OUT"
fi

echo ""
echo "Wrote:"
echo "  $HTML_OUT"
[ -f "$TXT_OUT" ] && echo "  $TXT_OUT"
echo ""
echo "Next step in new Outlook for Mac:"
echo "  Outlook -> Settings -> Signatures."
echo "  Select 'Deccan' as the default for new messages and replies / forwards."
echo ""
