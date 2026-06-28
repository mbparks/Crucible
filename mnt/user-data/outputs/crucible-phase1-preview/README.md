# CRUCIBLE

Chemistry and materials bench. A Field Instrument by Green Shoe Garage.

CRUCIBLE is a reference bench for chemistry and materials engineering work. It pairs a periodic table loaded with engineering data against a set of bench-chemistry modules (reagents, buffers, etchants, electroplating, photographic chemistry, hazards). Any sample tag from any module can be added to a vitrine and printed as 2.5 by 3.5 inch specimen cards, nine per US Letter sheet, with crop marks and source citations on the verso.

## Status

Phase 1 of 6. Shell and infrastructure are in place. Three placeholder cards exercise the pipeline end to end: iron (element), AISI 1018 (alloy), Kodak D-76 (developer). Module data lands in subsequent phases.

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
      router.js                  hash-based router and views
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
    assay/      alloy/   temper/    phase/     hardness/  solder/
    reagent/    buffer/  etch/      electro/   darkroom/  hazard/
    <each contains data/*.json sample tag files>
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
