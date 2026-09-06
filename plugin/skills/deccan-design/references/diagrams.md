# Figures and diagrams

How a Deccan document acquires a diagram, which tool draws it, and how that tool's
output is brought onto Deccan tokens. The design system does not render diagrams
itself; it delegates to `archify` and conforms what comes back.

## When a figure earns its place

A figure is warranted when the content is a **relationship between parts** that prose
would have to serialise and a table would have to flatten: what calls what, what
happens in which order, where data moves, which states a thing passes through.

A figure is not warranted for content that is already linear or already tabular. The
common failure is diagramming something that was a list.

| Content | Correct component |
|---|---|
| A comparison across attributes | Table |
| A single quantity or threshold | Callout |
| An ordered procedure with no branching | Numbered list |
| A definition or a rule | Body prose |
| A relationship, sequence, flow, or state machine | Figure |

## Routing

Five figure kinds are delegated to `archify`. Everything else stays in the document's
own components.

| Figure kind | Draws | Delegate to |
|---|---|---|
| `architecture` | Components, services, cloud and security boundaries, infrastructure | `archify` |
| `workflow` | Processes, approval gates, runbooks, CI/CD | `archify` |
| `sequence` | API call order, request/response exchanges | `archify` |
| `dataflow` | Pipelines, ETL/ELT, lineage | `archify` |
| `lifecycle` | State machines, request lifecycles, retry and failure paths | `archify` |
| Two or three boxes and an arrow | — | Hand-authored inline SVG on Deccan tokens |
| Anything in the table above | — | The named component |

A two- or three-node relationship is cheaper hand-drawn than as a specification
round-trip. Delegate when the diagram has enough parts to benefit from a layout engine.

## Delegating to archify

Use the `archify` skill. It is a separate skill with its own instructions; follow them
for authoring the specification, and apply the constraints below on top.

- **Omit `meta.visual_preset`.** The default `classic` preset is the only one the
  conformance layer is written against. `signal-flow`, `blueprint` and `editorial`
  carry their own palettes and page chrome, some of it hard-coded outside the custom
  properties the layer overrides.
- **Set `meta.quality_profile` to `"showcase"`** unless the figure is a dense reference
  map. Showcase acceptance requires all nine artifact checks to pass with zero
  composition errors and zero warnings.
- **Validate, then deliver.** A non-zero exit is never a success. Never edit a
  specification after its final validation passes.
- Keep to one clear main path, short side branches, sparse labels, and at most twelve
  primary nodes. Deccan documents favour a figure that is read at a glance.

### Probe before promising

archify is a Node program: everything runs through `node bin/archify.mjs`, and it
requires Node 18 or newer. A surface may list the skill and still be unable to execute
it. Establish which rung applies by running the tool, not by observing that the skill
exists, and only then state how the figure will be produced. Announcing archify and
then falling back reads worse than going to the fallback directly.

| Surface | Skill present | Executes Node | Rung |
|---|---|---|---|
| Claude Code | Yes | Yes | 1 |
| Claude.ai, Claude Desktop | Yes | Probe decides | 1 or 2 |
| Claude mobile | Yes | No | 2 |

**Rung 1 — archify.** Author, validate, deliver, then apply the conformance layer.

**Rung 2 — Mermaid.** Claude artifacts render Mermaid natively with no library, and
archify accepts Mermaid `flowchart`, `sequenceDiagram` and `stateDiagram` as input, so
a Mermaid figure upgrades losslessly the next time it is touched on a surface that can
run Node. Apply the Deccan Mermaid theme below.

**Rung 3 — inline SVG.** Hand-authored on Deccan tokens. Also the correct choice for a
figure destined for print, where interactivity is worthless.

State which rung produced the figure. A Mermaid figure on a surface that should have
managed archify is a fact worth surfacing, not one to absorb silently.

## Conformance — mandatory on every archify figure

archify output does not arrive on Deccan tokens and cannot be configured onto them: no
schema field, CLI flag or `meta` key controls theme, colour, typeface or corner radius.
Delivered HTML ships `data-theme="dark"`, a hard-coded JetBrains Mono chain fetched from
Google Fonts at view time, and structural corners at `rx="6"` to `rx="12"`. Conformance
is therefore applied after delivery, in two mechanical steps.

**Step 1 — remove the webfont links.** Delete every `<link>` to `fonts.googleapis.com`
and `fonts.gstatic.com` (there are three). The figure then makes no outbound request
when opened.

**Step 2 — append the conformance layer** as the last element in `<head>`, after
archify's own `<style>` block.

```css
/* deccan-design conformance layer for archify output.
   Written against archify 2.17. Declares at :root with !important so it
   outranks every html[data-preset][data-theme] pair (archify ships 14 of
   them) and applies at first paint, which is what removes the dark flash.
   Both themes resolve to the same Deccan values, so the viewer's theme
   toggle and OS preference cannot move the figure off brand. */

:root {
  /* Ground and structure */
  --bg:              #FFFFFF !important;
  --panel:           #FFFFFF !important;
  --panel-border:    #E7E5E4 !important;
  --grid:            #F5F5F4 !important;
  --mask:            #FFFFFF !important;
  --lane-fill:       #FAFAF9 !important;
  --lane-stroke:     #E7E5E4 !important;

  /* Type — stone ladder */
  --text:            #1C1917 !important;
  --text-muted:      #44403C !important;
  --text-dim:        #57534E !important;
  --text-faint:      #78716C !important;

  /* Semantic strokes: one accent, distinguished by opacity, never by hue.
     External is stone because it denotes what sits outside the system. */
  --frontend-stroke:   #164999 !important;
  --backend-stroke:    rgba(22, 73, 153, 0.86) !important;
  --security-stroke:   rgba(22, 73, 153, 0.72) !important;
  --database-stroke:   rgba(22, 73, 153, 0.58) !important;
  --messagebus-stroke: rgba(22, 73, 153, 0.44) !important;
  --cloud-stroke:      rgba(22, 73, 153, 0.34) !important;
  --external-stroke:   #78716C !important;

  /* Fills stay near-paper so label text keeps its contrast */
  --frontend-fill:   rgba(22, 73, 153, 0.10) !important;
  --backend-fill:    rgba(22, 73, 153, 0.08) !important;
  --security-fill:   rgba(22, 73, 153, 0.07) !important;
  --database-fill:   rgba(22, 73, 153, 0.06) !important;
  --messagebus-fill: rgba(22, 73, 153, 0.05) !important;
  --cloud-fill:      rgba(22, 73, 153, 0.04) !important;
  --external-fill:   #F5F5F4 !important;

  /* Connectors */
  --arrow:           #78716C !important;
  --arrow-emphasis:  #164999 !important;

  /* Chrome */
  --toolbar-bg:      #FFFFFF !important;
  --toolbar-border:  #E7E5E4 !important;
  --toolbar-text:    #44403C !important;
  --toolbar-hover:   #F5F5F4 !important;
  --toolbar-menu-bg: #FFFFFF !important;
}

/* Type stack. archify hard-codes a JetBrains Mono chain on body and svg;
   the Google Fonts link is removed separately so nothing is fetched. */
html body,
html body button,
html body input,
html .diagram-container,
html svg,
html svg text {
  font-family: 'Segoe UI Variable Display', 'Segoe UI Variable Text',
               'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system,
               BlinkMacSystemFont, sans-serif !important;
}

html code,
html pre,
html .mono {
  font-family: 'Cascadia Mono', 'Cascadia Code', Consolas, 'SF Mono', Menlo,
               'DejaVu Sans Mono', 'Liberation Mono', ui-monospace,
               monospace !important;
}

/* No rounded structural corners. CSS geometry properties outrank the rx/ry
   presentation attributes archify emits (verified in-browser). */
html svg rect,
html svg .card,
html svg foreignObject {
  rx: 0 !important;
  ry: 0 !important;
}

html .diagram-container,
html .toolbar,
html .panel,
html .legend,
html button {
  border-radius: 0 !important;
}

/* Paper ground regardless of theme attribute */
html,
html body {
  background: #FFFFFF !important;
  color: #1C1917 !important;
}

/* Literals archify sets directly on the selector rather than through a
   custom property, so the :root override cannot reach them. */
html svg .c-region            { fill: rgba(22, 73, 153, 0.04) !important; }
html svg .brand-mark-frame    { stroke: #D6D3D1 !important; }
html svg .brand-mark-fallback { stroke: #57534E !important; }
```

### Why the layer is shaped this way

- **`:root` with `!important`, not `html[data-theme]`.** archify ships fourteen theme
  blocks — a light and a dark pair for each visual preset — and a preset-qualified
  selector outranks a theme-only one. Declaring at `:root` with `!important` wins
  against all of them and applies at first paint, so no dark frame is ever shown.
- **Both themes resolve identically.** The viewer's theme button and the operating
  system preference remain functional but produce no visual change. The figure cannot
  be moved off brand by the reader.
- **Semantic distinction by opacity, never by hue.** Seven component types are separated
  along one accent. `external` is stone because it denotes what lies outside the system,
  which is a neutral statement rather than a second accent.
- **Three selector-level literals need their own rules.** `.c-region` sets an amber fill
  directly rather than through a custom property; the two brand-mark strokes are slate.
  The `:root` override cannot reach any of them.

### Verifying a conformed figure

Open it and confirm all six. The first is the one that regresses silently.

- [ ] No dark rendering with the operating system in dark mode, and no dark flash before paint.
- [ ] Accent resolves to `#164999`; no second hue anywhere.
- [ ] Every structural corner square.
- [ ] Type resolves to Segoe UI Variable, mono to Cascadia Mono.
- [ ] No request to `fonts.googleapis.com` in the network panel.
- [ ] Region and boundary fills are blue tints, not amber.

## Mermaid fallback

Rung 2. Apply this theme block so the figure carries Deccan colour.

```
%%{init: {'theme':'base','themeVariables':{
  'background':'#FFFFFF',
  'primaryColor':'#FFFFFF',
  'primaryBorderColor':'#164999',
  'primaryTextColor':'#1C1917',
  'lineColor':'#78716C',
  'secondaryColor':'#F5F5F4',
  'secondaryBorderColor':'rgba(22,73,153,0.58)',
  'tertiaryColor':'#FAFAF9',
  'tertiaryBorderColor':'#E7E5E4',
  'fontFamily':'Segoe UI Variable Display, Segoe UI, system-ui, sans-serif',
  'fontSize':'14px'
}}}%%
```

Mermaid rounds node corners by default. Use the square node forms — `id[label]` for
process, `id[[label]]` for subroutine — and avoid `id(label)` and `id((label))`, which
are rounded and circular respectively.

## Placing a figure in a document

A figure is a block-level component. It carries a caption; a figure without one forces
the reader to infer what they are looking at.

```html
<figure class="figure">
  <img src="…" alt="…">
  <figcaption>Request path from edge to database.</figcaption>
</figure>
```

An archify figure delivered as standalone HTML is referenced, not inlined — it is a
complete document with its own toolbar and scripts. Embed a static export (SVG or PNG)
in the document and link the interactive artifact alongside it. Do not lift archify's
`<svg>` element out of its page: every fill and stroke resolves through custom
properties declared on `<html>`, so an extracted SVG arrives with its geometry intact
and its colour gone.

Caption text is body register — a statement of what the figure shows, not a title.
Numbering is used only when the document refers to figures by number.

## What is not a figure

- A screenshot of a terminal. Use a code block.
- A logo or brand mark. Those are covered in `components.md`.
- Decorative imagery. The system has no decorative image component and does not want one.
- A table with boxes drawn around it.

## Version pinning

The conformance layer is written against **archify 2.17** and depends on four
properties of its output: the `--*-stroke` and `--*-fill` custom-property names, the
`[data-theme]` attribute on `<html>`, the `c-*` semantic class names on SVG elements,
and `rx`/`ry` being expressed as presentation attributes rather than inline styles. If a
future archify release changes any of these, figures revert to archify's own palette
rather than failing loudly. The verification list above is the check that catches it.
