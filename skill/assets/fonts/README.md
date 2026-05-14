# Fonts

This directory is intentionally empty.

The deccan-design v2.0 type stack is **OS-native by design** — no font binaries ship with the system or the installer.

## Why empty

- On Windows 11, the sans chain resolves to **Segoe UI Variable**, which ships with the operating system.
- On Windows 10, the chain falls back to the static **Segoe UI** faces, which are metric-compatible.
- On macOS, the chain resolves to **San Francisco** via `system-ui`.
- The mono chain resolves to **Cascadia Mono** (Windows 11, ships with Windows Terminal), Consolas (older Windows), or **SF Mono** (macOS).
- All chains terminate in `sans-serif` / `monospace` generic fallbacks.

No `.woff2`, no `.ttf`, no `.otf` is required to render a deccan-design artifact on a current corporate endpoint.

## What this avoids

- An MSI deployment to install third-party fonts on every endpoint.
- An Intune compliance lane to verify the install.
- An M365 / Office Font Service dependency.
- A commercial-licence programme for embedded fonts.
- Substitution surprises when a document is opened on a partner or contractor laptop.

## If a future revision needs font binaries

This directory carries a `.gitkeep` so the path persists. Drop the `.woff2` / `.ttf` files here and update `tokens.md` and the SKILL frontmatter to reference them. The repository tree does not need to change.
