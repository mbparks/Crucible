# CRUCIBLE Conventions

Pinned decisions for this instrument. Defers to the series-wide `CONVENTIONS.md` for anything not addressed here.

## Identity

- **Slug**: `crucible`
- **Series**: Field Instruments
- **Number**: FI-047
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

Each `stats` entry should carry a stable `key` (camelCase) so module renderers can look values up by identity rather than by parsing labels. Established keys so far:

- Core (any kind): `atomicNumber`, `atomicMass`, `density`, `meltingPoint`, `boilingPoint`
- Element-specific: `electronegativity`, `crystalStructure`, `electronConfig`, `thermalConductivity`, `resistivity`
- Mechanical (alloys and elements): `youngsModulus`, `mohs`, `yieldStrength`, `tensileStrength`, `elongation`, `hardness`
- Alloy-specific: `machinability`, `cte`, `meltingRange`, `maxServiceTemp`, plus composition entries keyed `comp_<element>` (e.g., `comp_c`, `comp_cr`)
- Temper schedule: `austenitizeTemp`, `soakTime`, `quench`, `asQuenchedHardness`, `temperTemp`, `caseHardness`, `coreHardness`
- Solder: `solidus`, `liquidus`, `plasticRange`, plus `comp_<element>`
- Reagent: `formula`, `molarMass`, `concentration`, `stockMolarity`, `pka`, `pka1`, `pka2`, `pka3`, `pka4`, `pkb`, `solubility`
- Buffer: `pKa`, `phRange`, `acidForm`, `acidMW`, `baseForm`, `baseMW`
- Electro: `potential`, `capacity`, `currentDensity`, `voltage`, `thickness`, `ph`
- Darkroom developer: `type`, `stockPh`, `stockKeeping`, `dilutions`, `refTemp`, `capacityStock`, `speedGain`, `pushFactor`
- Phase reference: `liquidus`, `eutectic`, `eutectoid`, `peritectic`, `a3Line`, `acmLine`, `alphaMax`, `gammaMax`
- Hazard reference: `triggerTime`, `eyewashDuration`, `showerDuration`, `flowEye`, `flowShower` (safety-station specs); free-form labels for incompatibility pairs

When the same physical quantity appears across modules, reuse the same key.

For the `element` kind specifically, additional top-level fields are required: `Z` (atomic number), `category` (one of the eleven element categories used by ASSAY), `group` (null for f-block), `period`, `block` (s/p/d/f). The seeder populates all of these.

For the `alloy` kind, a top-level `family` field categorizes the entry (one of `carbon-steel`, `alloy-steel`, `tool-steel`, `stainless`, `aluminum`, `copper-alloy`, `titanium`, `nickel-superalloy`, `cast-iron`, `magnesium-alloy`). For the `solder` kind, a top-level `category` field categorizes the entry (`electronics-leaded`, `electronics-lead-free`, `plumbing`, `silver-braze`, `phos-copper-braze`, `specialty`, `jewelry`).

For the `buffer-recipe` kind, additional top-level fields drive the BUFFER module's Henderson-Hasselbalch solver: `pKa`, `phMin`, `phMax`, `acidName`, `acidFormula`, `acidMW`, `acidIsLiquid` (boolean), `acidDensity`, `acidPercent`, `baseName`, `baseFormula`, `baseMW`. When `acidIsLiquid` is true, the solver outputs a stock-volume in mL using density and percent; otherwise it outputs grams.

The DARKROOM module uses two id prefixes for distinct kinds: developer cards take `developer:<slug>` (kind `developer`), while process-reference cards take `darkroom:<slug>` (kind `reference`). The router maps both prefixes to the darkroom module folder.

The PHASE module's interactive Fe-Fe₃C diagram lives entirely in `modules/phase/module.js` as a single self-contained custom view. Phase boundary functions are piecewise-linear approximations from the published Fe-Fe₃C metastable diagram (ASM Vol. 3); region classification and lever-rule fraction calculations are analytical. The `binary-diagram` kind is used for the three companion phase-diagram reference cards (Cu-Zn, Al-Si, Pb-Sn) which document the system but do not render their own diagrams.

The HAZARD module's `safety-reference` kind covers the seven shop safety cards. The cards lean on stats more than on body prose, because emergency reference works best as scannable lists rather than paragraphs.

See `modules/assay/data/fe.json`, `modules/alloy/data/aisi-4140.json`, `modules/temper/data/4140-ht.json`, `modules/solder/data/sac305.json`, `modules/hardness/data/rockwell.json`, `modules/reagent/data/hcl-conc.json`, `modules/buffer/data/acetate.json`, `modules/etch/data/nital.json`, `modules/electro/data/galvanic-series.json`, `modules/darkroom/data/d-76.json`, `modules/phase/data/fe-c-key.json`, `modules/hazard/data/nfpa-704.json` as canonical examples of the kinds in use through Phase 5.

## Custom module views

A module can replace the default card-grid view by declaring `"customView": true` in its manifest entry and providing `modules/<slug>/module.js` that exports an async `render(rootElement, ctx)` function. The router will dynamically import the module's JS (and inject `modules/<slug>/module.css` if present) when the user navigates to `#/<slug>`.

The `ctx` argument provides three loaders: `manifest`, `loadEntry(id)`, `loadEntriesForModule(slug)`. The module is responsible for clearing and populating the root element.

ASSAY, HARDNESS, BUFFER, ELECTRO, and PHASE use this pattern through Phase 5. ASSAY's render produces a periodic table. HARDNESS's render produces a converter form plus a reference-card grid. BUFFER's render is a Henderson-Hasselbalch recipe solver above the buffer-system card grid. ELECTRO's render is a galvanic couple checker above the reference-card grid. PHASE's render is an interactive Fe-Fe₃C phase diagram with click-to-query region identification and analytical lever-rule fraction calculation, above the reference-card grid.

## Bulk data: seeder pattern

For modules with large, structured data sets (ASSAY's 118 elements, ALLOY's catalog of engineering alloys, SOLDER's filler-metal table, TEMPER's heat-treat schedules, REAGENT's lab chemicals, BUFFER's buffer systems, ETCH's etchant formulas, ELECTRO's electrochemistry references, DARKROOM's developers and process references, PHASE's reference cards, HAZARD's safety cards), generate JSON files from a single Python data table under `tools/`. Each seeder is idempotent and rerunnable: hand edits to individual JSON files will be overwritten, so per-entry refinements should go back into the seeder data table. See `tools/seed_elements.py`, `tools/seed_alloys.py`, `tools/seed_temper.py`, `tools/seed_solder.py`, `tools/seed_reagents.py`, `tools/seed_buffers.py`, `tools/seed_etchants.py`, `tools/seed_electro.py`, `tools/seed_darkroom.py`, `tools/seed_phase.py`, and `tools/seed_hazard.py` as references.

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

1. **Phase 1, scaffold** (shipped). Shell, router, themes, card renderer, vitrine, print system, search, sources registry, three placeholder cards.
2. **Phase 2, ASSAY** (shipped). Custom-view dispatch in router. Full periodic table with engineering overlays. 118 element JSON files generated by `tools/seed_elements.py`.
3. **Phase 3, materials core** (shipped). ALLOY (34 alloys, nine families), TEMPER (11 schedules and references), HARDNESS (custom-view ASTM E140 converter and five scale-reference cards), SOLDER (15 alloys across electronics, plumbing, silver brazing, phos-copper brazing, specialty, and jewelry).
4. **Phase 4, chemistry core** (shipped). REAGENT (12 reagents plus dilution-math and serial-dilution references), BUFFER (custom-view H-H solver over 8 buffer systems), ETCH (12 metallographic and patina formulas), ELECTRO (custom-view galvanic couple checker over 11 reference cards: galvanic series, standard reduction potentials, sacrificial anodes, plating baths, anodize baths, electroless nickel).
5. **Phase 5, specialty** (shipped). PHASE (custom-view interactive Fe-Fe₃C diagram with click-to-query region identification and lever-rule fractions, plus 7 reference cards including three companion binary systems), DARKROOM (8 B&W film developers expanded from the Phase 1 placeholder, plus 4 process-reference cards on dilution math, time/temperature compensation, push/pull, and agitation protocols), HAZARD (7 shop safety reference cards: NFPA 704, GHS pictograms, DOT placards, chemical incompatibility matrix, spill response, PPE selection, eyewash and emergency shower).
6. **Phase 6, polish** (current). Telegraph theme (third theme), colophon route at `#/colophon` with citation counts per source, cross-instrument bridges on the landing page (companion Field Instruments), enriched `build.py --check` statistics, single-file bundle via `build.py --bundle` (inlined CSS + JS + data via import map and blob URLs).

## Bundle distribution

`python3 build.py --bundle` writes a single `crucible-bundle.html` (about 770 KB) that opens directly from disk or any static host with no other files needed. The bundle works by:

1. Inlining all CSS (base + three themes + five module stylesheets) in a single `<style>` block.
2. Reading every shared `shared/js/*.js` source and rewriting relative imports to absolute virtual paths under `/__bundle__/`.
3. Patching `data.js` with a `__cb_fetch` shim that intercepts requests for paths present in `window.__CRUCIBLE_DATA__`.
4. Patching `router.js` so its dynamic `import()` call consults `window.__CRUCIBLE_MODULES_SRC__` first, creating blob URLs on demand for inlined module source.
5. Building an `<script type="importmap">` at boot, with one entry per shared JS file mapping the virtual path to a fresh blob URL.
6. Triggering the entry import once the import map is in place.

This preserves the entire ES module structure (no concatenation, no namespace flattening). Each shared file remains an independent module; the only difference is its host. Module custom views (`modules/*/module.js`) are looked up by virtual path the same way.

The dev workflow (`python3 -m http.server`) and the bundle workflow produce identical runtime behavior. Build the bundle on demand for distribution; keep iterating on the source tree the rest of the time.

## Themes

Themes are CSS files under `shared/style/themes/`, registered in `shared/js/theme.js` (the VALID set) and `index.html` (the theme picker buttons). Each theme defines a complete set of CSS custom properties (palette, typography, textures) on `html[data-theme="<name>"]`, and may add theme-specific selectors for component flourishes.

Through Phase 6 the available themes are:
- **Alchemy** (default): 17th-century alchemist's bench. Firelight, copper, soot, parchment. IM Fell English and EB Garamond.
- **Assay**: clean engineering blueprint. Graph paper, blueprint blue, IBM Plex Sans/Mono.
- **Telegraph**: 1920s telegraph operator's desk. Walnut desk under cream telegraph-paper cards, brass accents, IBM Plex Mono display type. Added in Phase 6.

Adding a new theme: create `shared/style/themes/<name>.css` with the full custom-property set, add `<name>` to `VALID` in `theme.js`, add a `<link>` tag in `index.html` and a theme picker button.
