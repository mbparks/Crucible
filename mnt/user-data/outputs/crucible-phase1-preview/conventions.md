# CRUCIBLE Conventions

Pinned decisions for this instrument. Defers to the series-wide `CONVENTIONS.md` for anything not addressed here.

## Identity

- **Slug**: `crucible`
- **Series**: Field Instruments
- **Number**: TBD on ship (not yet numbered)
- **Tagline**: "chemistry and materials bench"
- **Glyph**: ⚗

## Architecture

- **Folder per module**. Each of the twelve modules has its own folder under `modules/` containing `data/*.json` sample tags.
- **Shared shell**. The shell (`index.html`), router, card renderer, search, vitrine, theme system, and print pipeline live in `shared/`. Modules add data, not chrome.
- **Static JSON data**. No databases, no APIs, no server-side rendering. Build pipeline produces `search-index.json` from per-module JSON files.
- **VITRINE is a global feature**, not a module. The overlay and state live in `shared/`.

## Routing

Hash-based, like SEMAPHORE.

- `#/` → bench landing (module grid)
- `#/<module-slug>` → module view (entry list)
- `#/card/<global-id>` → card detail (front + back side by side)
- `#/vitrine` → opens vitrine overlay
- `#/print` → print sheet of current vitrine
- `#/print/<global-id>` → print a single card
- `#/v/<base64>` → load a shared vitrine from the URL hash payload

Global IDs follow `<kind>:<slug>`, for example `element:fe`, `alloy:aisi-1018`, `developer:d-76`.

## Themes

Two flagship themes, picker scaffolded for expansion. Theme stored in `localStorage` under `crucible.theme`.

- **Alchemy** (`alchemy.css`). 17th c. alchemist's bench. IM Fell English display, EB Garamond body, copper-ember accent, soot background, parchment foreground. Small-caps titles.
- **Assay** (`assay.css`). Modern metallurgical lab. IBM Plex typography, graph-paper background, blueprint-blue accent, red marking-ink secondary.

Future themes (Phase 6): FOUNDRY, APOTHECARY, BLUEPRINT, FIELD.

## Specimen cards

- **Size**: 2.5 by 3.5 inches (poker/tarot scale).
- **Layout per sheet**: nine cards per US Letter, 3 columns × 3 rows, centered on page.
- **Crop marks**: hairline rules on every card edge for trimming.
- **Duplex layout**: front sheet in normal order, back sheet with each row's order mirrored (left-right) so long-edge duplex aligns front-to-back per card.
- **Source footer**: every card cites its sources via shorthand keys defined in `shared/data/sources.json`.

## Sample tag schema

Every entry is one JSON file. Required fields: `id`, `module`, `kind`, `title`, `subtitle`, `stats`. Optional: `symbol`, `tags`, `body`, `hazards`, `related`, `sources`.

See `modules/assay/data/iron.json`, `modules/alloy/data/aisi-1018.json`, `modules/darkroom/data/d-76.json` as canonical examples for the three main kinds used in Phase 1.

## Data sourcing

- **Materials**: ASM Handbook series. Vol. 1 for irons and steels properties, Vol. 2 for nonferrous, Vol. 3 for phase diagrams (PHASE module), Vol. 4 for heat treating (TEMPER), Vol. 9 for metallography (ETCH support).
- **Chemistry**: CRC Handbook of Chemistry and Physics, 104th ed. NIST WebBook as secondary check.
- **Etchants**: ASTM E407.
- **Photographic chemistry**: Anchell & Troop, *The Film Developing Cookbook* (2nd ed.).

When sources disagree, prefer the one closer to the engineering context (ASM beats CRC for engineering moduli, CRC beats ASM for pKa values). Flag the disagreement in the card body.

## Search

- Trigger: slash key (`/`), unless a text input is focused.
- Index is `shared/data/search-index.json`, built by `build.py`.
- Scoring: title exact > title prefix > title contains > symbol > tag exact > subtitle > excerpt.

## Standing rules from the series

- **No em dashes**. Use commas, parentheses, periods, or sentence restructuring.
- **README must include GPL-3.0 license section as plain text, no hyperlink.**
- **Always update conventions and supporting docs** when code or schema changes.
- **PAPERWORK is FI-010**, not #006. (Not relevant here, but worth carrying forward across instruments.)
- **mbparks.com is static HTML on x10hosting with Cloudflare**. No WordPress, no PHP. Server-side anything goes through a Cloudflare Worker.

## Build order

1. **Phase 1, scaffold** (current). Shell, router, themes, card renderer, vitrine, print system, search, sources registry, three placeholder cards.
2. **Phase 2, ASSAY**. Full periodic table with engineering overlays.
3. **Phase 3, materials core**. ALLOY, TEMPER, HARDNESS, SOLDER.
4. **Phase 4, chemistry core**. REAGENT, BUFFER, ETCH, ELECTRO.
5. **Phase 5, specialty**. PHASE, DARKROOM, HAZARD.
6. **Phase 6, polish**. Additional themes, cross-links, single-file bundle, README and conventions sync.
