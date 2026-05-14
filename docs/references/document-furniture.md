# Document furniture

The eight rules every Deccan document follows, and the tone-and-voice ban-list with replacement examples.

## The eight document-furniture rules

1. **Cover page mandatory and self-contained.** Logo + title + subtitle + author + version + date + classification. No header, no footer, no page number. **Must fit on exactly one physical page in print** — see "Cover sizing in print" below.
2. **End page mandatory and self-contained.** No header, no footer, no page number. Must fit on exactly one physical page in print.
3. **Every H1 starts on a new page** (`page-break-before: always`).
4. **Body fills the live content area.** No 60ch artificial cap in print; the live area is ≥ 80% of paper width (0.8" outside margins on Letter).
5. **End page after a hard page break.**
6. **Footer page numbers are bare integers**, right-aligned, mono 8.5pt stone-500. Never "Page X of Y".
7. **Pure white print background.** Stone tints only inside callouts, code blocks, banded table rows, chips.
8. **Mono and stone travel together.** Inline `<code>` and code blocks always carry the mono face and stone-100 fill. (Per v2.0, the mono face is **Cascadia Mono / Consolas / SF Mono**, not IBM Plex Mono. The rule is identical otherwise.)

## Cover sizing in print

The cover (and the end page) must each render on **exactly one physical page**. The naïve `min-height: 100vh` rule that fills the viewport on screen will cause the cover to overflow in print, because `100vh` resolves to the **full paper height** (e.g. 1056 px on Letter), not the live content area after margins (~883 px on Letter at 0.8" outside / 1" bottom).

When the cover overflows, two visible failures occur:
- The cover title or metadata strip pages out to a second physical page.
- The overflow page picks up the body footer (because `@page :first` only suppresses page 1).

Every implementation of the cover and end page must include the print overrides documented in `skill/references/print-rules.md` → "Cover and end-page sizing in print". The slot-fill template `skill/assets/templates/document.html` and all four `deccan-*.dotx` Word templates ship these rules. Custom documents that re-derive cover composition must inherit them.

## Tone and voice ban-list

The patterns below are not acceptable in any document issued under this system. Each is paired with a corrective rewrite.

### 1. Conversational subtitles in headings

| Banned | Correct |
|---|---|
| `## Python version selection: in plain English` | `## Python version selection` |
| `## Document furniture: the rules` | `## Document furniture` |

### 2. First-person narrator asides

| Banned | Correct |
|---|---|
| "Let me walk you through the rollout plan." | "The rollout proceeds in four waves." |
| "I want to show you the colour tokens." | "The colour tokens are listed in §1.3." |

### 3. Filler openings

| Banned | Correct |
|---|---|
| "Here's the thing: the installer is unsigned." | "The installer is unsigned." |
| "It's worth noting that SmartScreen will warn the user." | "SmartScreen warns the user on first run." |

### 4. Casual transitions

| Banned | Correct |
|---|---|
| "That said, the green is reserved." | (Use a section break.) "Deccan Green is reserved for sustainability content." |
| "Now, let's look at the print rules." | "## Print rules" |

### 5. Decorative emoji

Banned in body content. Use words: "Required", "Prohibited", "Note", "Warning".

### 6. Exclamation marks in body prose

Banned. Use a period.

### 7. "Deep dive" / "let's dive in" / "rabbit hole" / "TL;DR"

Banned. Use plain language.

| Banned | Correct |
|---|---|
| "TL;DR: the system is OS-native." | "Summary: the system uses an OS-native type stack." |
| "Let's dive deeper into Segoe UI Variable." | "## Segoe UI Variable" |

### 8. Mental-exercise framings

| Banned | Correct |
|---|---|
| "Imagine if every Deccan document looked different." | "Without a standard, every document re-litigates the same decisions." |
| "Think of the type stack as a fallback chain." | "The type stack is a fallback chain." |

### 9. Self-reference to the document

| Banned | Correct |
|---|---|
| "This guide will teach you the colour tokens." | (Remove the sentence.) |
| "By the end of this section you'll know how to install." | (Remove the sentence.) |

### 10. Em-dash narrator interjections

| Banned | Correct |
|---|---|
| "The installer is unsigned — and here's the kicker — SmartScreen will warn the user." | "The installer is unsigned. SmartScreen warns the user on first run." |

## The read-aloud test

If a sentence would feel out of place in a board paper, an audit response, or a regulator submission, rewrite it.
