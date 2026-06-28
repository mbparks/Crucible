# CRUCIBLE

Field Instrument #047. Chemistry and materials bench. A Field Instrument by Green Shoe Garage.

CRUCIBLE is a reference bench for chemistry and materials engineering work. It pairs a periodic table loaded with engineering data against a set of bench-chemistry modules (reagents, buffers, etchants, electroplating, photographic chemistry, hazards). Any sample tag from any module can be added to a vitrine and printed as 2.5 by 3.5 inch specimen cards, nine per US Letter sheet, with crop marks and source citations on the verso.

## Status

Phase 6 of 6. **All 12 modules active and CRUCIBLE is feature-complete.** Phase 6 added polish on top of the Phase 5 catalog: a third theme (**Telegraph**, a brass-key-on-oak-desk aesthetic with monospace display type and cream telegraph-paper cards), a **colophon page** at `#/colophon` listing every cited source with citation counts and the cards that draw from each, **cross-instrument bridges** on the landing page linking to companion Field Instruments (MAKER ALMANAC, HACKER ALMANAC, PANELWRIGHT, OSCILLOGRAPH), enriched build statistics in `build.py --check` (per-module and per-kind entry counts, per-source citation tallies, unused-source warnings), and a **single-file bundle** produced by `python3 build.py --bundle` (writes a self-contained `crucible-bundle.html` of about 770 KB with all CSS, JS, data, and module sources inlined using an import map and blob URLs so the modular ES module structure survives bundling). 254 total entries indexed across all 12 modules. Five custom-view modules: ASSAY (periodic table), HARDNESS (ASTM E140 converter), BUFFER (Henderson-Hasselbalch solver), ELECTRO (galvanic couple checker), PHASE (interactive Fe-Fe₃C diagram).

## The two tracks

Materials track: ASSAY, ALLOY, TEMPER, PHASE, HARDNESS, SOLDER.

Chemistry track: REAGENT, BUFFER, ETCH, ELECTRO, DARKROOM, HAZARD.

VITRINE and global search live in the shell.

## Data sources

Engineering data is canonically from the ASM Handbook series. Chemistry is canonically from the CRC Handbook of Chemistry and Physics. Photographic chemistry follows Anchell and Troop, *The Film Developing Cookbook*. Etchants follow ASTM E407. Every card carries its sources in a footer that keys into `shared/data/sources.json`.

## Repo layout

```
crucible/
  index.html                     shell, theme picker, search, vitrine
  build.py                       static builder, walks modules and rebuilds the search index
  shared/
    style/
      base.css                   layout, typography, print stylesheet
      themes/
        alchemy.css              17th c. alchemist's bench
        assay.css                modern metallurgical assay bench
    js/
      app.js                     entry point
      router.js                  hash-based router, custom-view dispatcher
      data.js                    JSON loader
      card.js                    specimen card renderer
      theme.js                   theme persistence
      search.js                  global search overlay
      vitrine.js                 vitrine state and share link
      toast.js                   ephemeral messages
    data/
      manifest.json              modules and their entries
      sources.json               canonical source registry
      search-index.json          built by build.py
  modules/
    assay/                       active: periodic table with engineering overlays
      module.js                  custom view (periodic table renderer)
      module.css                 table styles
      data/<sym>.json            one file per element, 118 total
    alloy/                       active: 34 alloys across nine families
      data/<slug>.json
    temper/                      active: 11 heat-treat schedules and references
      data/<slug>.json
    hardness/                    active: ASTM E140 converter + 5 scale references
      module.js                  custom view (converter + reference grid)
      module.css
      data/{mohs,rockwell,brinell,vickers,shore}.json
    solder/                      active: 15 solder and braze alloys
      data/<slug>.json
    reagent/                     active: 12 reagents + dilution math + serial dilution
      data/<slug>.json
    buffer/                      active: 8 buffer systems with H-H solver
      module.js                  custom view (H-H recipe calculator)
      module.css
      data/<slug>.json
    etch/                        active: 12 etchants, PCB etchants, patinas
      data/<slug>.json
    electro/                     active: galvanic series, plating baths, couple checker
      module.js                  custom view (galvanic couple checker)
      module.css
      data/<slug>.json
    darkroom/                    active: 8 developers + 4 process references
      data/<slug>.json
    phase/                       active: interactive Fe-C diagram + binary references
      module.js                  custom view (Fe-Fe₃C tool + lever rule)
      module.css
      data/<slug>.json
    hazard/                      active: 7 shop safety reference cards
      data/<slug>.json
  tools/
    seed_elements.py             118 element JSONs from one Python data table
    seed_alloys.py               33 alloy JSONs across nine families
    seed_temper.py               11 heat-treat schedule JSONs
    seed_solder.py               15 solder and braze JSONs
    seed_reagents.py             12 reagent JSONs + 2 reference cards
    seed_buffers.py              8 buffer system JSONs for the H-H solver
    seed_etchants.py             12 etchant JSONs
    seed_electro.py              11 electrochemistry JSONs for the couple checker
    seed_darkroom.py             8 developer JSONs + 4 process reference cards
    seed_phase.py                7 phase-diagram reference cards
    seed_hazard.py               7 safety reference cards
```

## Themes

Alchemy and Assay are the two flagship themes. Alchemy lights the bench with copper, soot, ember, and an IM Fell display face. Assay is a modern metallurgical lab, graph paper, brushed steel, IBM Plex typography. Additional themes (FOUNDRY, APOTHECARY, BLUEPRINT, FIELD) are planned for Phase 6.

## Specimen cards

Cards are 2.5 by 3.5 inches, nine per US Letter sheet. Front carries title, symbol, key engineering data, tags, and hazard chips. Verso carries extended body text, full data table, cross-links to related entries in other modules, and a source citation footer. The print sheet alternates front and back pages with the back ordered mirrored row-by-row so a long-edge duplex print aligns.

## Vitrine

Open any card and tap "add to vitrine" to collect specimens. The vitrine overlay supports drag-to-reorder, remove, clear, and two shipping options: print sheet (opens the print preview) and share link (copies a URL with the entire vitrine encoded in its hash, so the recipient sees the same card set on load).

## Local development

Static files. No build step required to run, but local browsers refuse `fetch()` against `file://` for security. Use any local server:

```
python3 -m http.server 8000
# then visit http://localhost:8000/
```

When data files change, regenerate the search index:

```
python3 build.py
python3 build.py --check    # verify all references resolve
```

## Hosting

Deploys to mbparks.com/crucible/ as static HTML on x10hosting with Cloudflare for DNS and CDN. No PHP, no WordPress, no server-side anything. (If a future module needs network calls, route through a Cloudflare Worker as elsewhere on mbparks.com.)

## License

GPL-3.0
