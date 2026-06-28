#!/usr/bin/env python3
"""
CRUCIBLE build script.

Walks modules/*/data/*.json and produces:
  - shared/data/search-index.json   (the search corpus)
  - shared/data/colophon.json       (citation counts per source)

With --check, prints validation and per-module/source statistics.
With --bundle, writes a single self-contained crucible-bundle.html with
all CSS, JS, and data inlined. Uses an import map so the modular ES
module structure of the source survives bundling.

Usage:
    python3 build.py
    python3 build.py --check
    python3 build.py --bundle
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).parent
MODULES = ROOT / "modules"
SHARED_DATA = ROOT / "shared" / "data"
SHARED_JS = ROOT / "shared" / "js"
SHARED_STYLE = ROOT / "shared" / "style"


def collect_entries():
    entries = []
    for module_dir in sorted(MODULES.iterdir()):
        if not module_dir.is_dir():
            continue
        data_dir = module_dir / "data"
        if not data_dir.exists():
            continue
        for f in sorted(data_dir.glob("*.json")):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"  ! skip {f.relative_to(ROOT)}: {exc}", file=sys.stderr)
                continue
            entries.append(doc)
    return entries


def build_search_index(entries):
    out = {"version": 1, "built": "build.py", "entries": []}
    for e in entries:
        if not e.get("id"):
            continue
        excerpt = (e.get("body") or "").split("\n\n", 1)[0]
        excerpt = excerpt.replace("**", "")[:200]
        out["entries"].append({
            "id": e["id"], "module": e.get("module", ""), "kind": e.get("kind", ""),
            "title": e.get("title", ""), "symbol": e.get("symbol", ""),
            "subtitle": e.get("subtitle", ""), "tags": e.get("tags", []),
            "excerpt": excerpt,
        })
    return out


def build_colophon(entries):
    sources_doc = json.loads((SHARED_DATA / "sources.json").read_text())
    sources = sources_doc["sources"]
    citations = defaultdict(list)
    for e in entries:
        for src in e.get("sources", []) or []:
            citations[src].append({
                "id": e["id"], "title": e.get("title", ""), "module": e.get("module", ""),
            })
    out = {"version": 1, "built": "build.py", "sources": []}
    for key, meta in sources.items():
        cites = citations.get(key, [])
        out["sources"].append({
            "key": key,
            "short": meta.get("short", key),
            "full": meta.get("full", ""),
            "publisher": meta.get("publisher", ""),
            "edition": meta.get("edition", ""),
            "citationCount": len(cites),
            "citingEntries": sorted(cites, key=lambda c: c["id"]),
        })
    out["sources"].sort(key=lambda s: (-s["citationCount"], s["key"]))
    return out


def check(entries, verbose=True):
    sources = json.loads((SHARED_DATA / "sources.json").read_text())["sources"]
    manifest = json.loads((SHARED_DATA / "manifest.json").read_text())
    declared = {m["slug"]: set(m.get("entries", [])) for m in manifest["modules"]}

    ids = set()
    problems = []
    by_module = Counter()
    by_kind = Counter()
    source_use = Counter()

    for e in entries:
        eid = e.get("id")
        if not eid:
            problems.append(f"entry without id in {e.get('module')}")
            continue
        if eid in ids:
            problems.append(f"duplicate id {eid}")
        ids.add(eid)
        by_module[e.get("module", "?")] += 1
        by_kind[e.get("kind", "?")] += 1
        for src in e.get("sources", []) or []:
            source_use[src] += 1
            if src not in sources:
                problems.append(f"{eid} cites unknown source {src}")
    for e in entries:
        for rid in e.get("related", []) or []:
            if rid not in ids:
                problems.append(f"{e['id']} -> unknown related {rid}")
    for e in entries:
        slug = e["id"].split(":", 1)[1]
        d = declared.get(e.get("module"), set())
        if slug not in d:
            problems.append(f"{e['id']} not declared in manifest under {e.get('module')}")

    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  ! {p}", file=sys.stderr)
        return 1

    if verbose:
        print(f"OK . {len(ids)} entries, all references resolve.")
        print(f"\nPer module:")
        for slug in sorted(by_module):
            print(f"  {slug:>10s}: {by_module[slug]:>4d}")
        print(f"\nPer kind:")
        for kind in sorted(by_kind):
            print(f"  {kind:>20s}: {by_kind[kind]:>4d}")
        print(f"\nSource coverage ({len(source_use)} of {len(sources)} sources cited):")
        for src in sorted(source_use, key=lambda s: -source_use[s]):
            short = sources.get(src, {}).get("short", src)
            print(f"  {src:>16s} . {short:<28s}: {source_use[src]:>4d} citations")
        unused = sorted(set(sources) - set(source_use))
        if unused:
            print(f"\nDeclared but unused sources: {', '.join(unused)}")
    else:
        print(f"OK . {len(ids)} entries, all references resolve.")
    return 0


# =================== BUNDLE ===================

def virtual_path(rel_path):
    return "/__bundle__/" + str(rel_path).replace("\\", "/")


def rewrite_imports(src, src_rel_path):
    src_dir = Path(src_rel_path).parent

    def repl(match):
        quote = match.group("q")
        path = match.group("p")
        if not path.startswith("."):
            return match.group(0)
        resolved = (src_dir / path).resolve()
        try:
            rel = resolved.relative_to(ROOT.resolve())
        except ValueError:
            return match.group(0)
        return f'{match.group("pre")}{quote}{virtual_path(rel)}{quote}'

    pattern = re.compile(
        r'(?P<pre>from\s+|import\s*\()(?P<q>["\'])(?P<p>\.{1,2}/[^"\']+)(?P=q)'
    )
    return pattern.sub(repl, src)


def patch_data_js(src):
    shim = """
// === BUNDLE SHIM injected by build.py --bundle ===
const __CB_DATA__ = (typeof window !== "undefined" && window.__CRUCIBLE_DATA__) || null;
const __origFetch = (typeof window !== "undefined") ? window.fetch.bind(window) : fetch;
async function __cb_fetch(path) {
  if (__CB_DATA__) {
    const key = path.startsWith("/") ? path.slice(1) : path;
    if (key in __CB_DATA__) {
      const v = __CB_DATA__[key];
      return { ok: true, json: () => Promise.resolve(v), text: () => Promise.resolve(JSON.stringify(v)) };
    }
  }
  return __origFetch(path);
}
// === END SHIM ===
"""
    patched = re.sub(r'\bfetch\s*\(', '__cb_fetch(', src)
    return shim + patched


def patch_router_js(src):
    shim = """
// === BUNDLE SHIM injected by build.py --bundle ===
async function __cb_loadModule(virtualPath) {
  const reg = (typeof window !== "undefined") ? window.__CRUCIBLE_MODULES_SRC__ : null;
  if (reg && virtualPath in reg) {
    const blob = new Blob([reg[virtualPath]], { type: "application/javascript" });
    const url = URL.createObjectURL(blob);
    return import(/* @vite-ignore */ url);
  }
  return import(/* @vite-ignore */ virtualPath);
}
// === END SHIM ===
"""
    patched = src.replace(
        "const mod = await import(",
        "const mod = await __cb_loadModule(",
    )
    return shim + patched


def collect_bundle_data():
    data = {}
    for f in SHARED_DATA.glob("*.json"):
        rel = f.relative_to(ROOT).as_posix()
        data[rel] = json.loads(f.read_text(encoding="utf-8"))
    for mod_dir in MODULES.iterdir():
        if not mod_dir.is_dir():
            continue
        data_dir = mod_dir / "data"
        if not data_dir.exists():
            continue
        for f in data_dir.glob("*.json"):
            rel = f.relative_to(ROOT).as_posix()
            data[rel] = json.loads(f.read_text(encoding="utf-8"))
    return data


def collect_shared_js_sources():
    sources = {}
    for f in sorted(SHARED_JS.glob("*.js")):
        rel = f.relative_to(ROOT).as_posix()
        src = f.read_text(encoding="utf-8")
        src = rewrite_imports(src, rel)
        if f.name == "data.js":
            src = patch_data_js(src)
        if f.name == "router.js":
            src = patch_router_js(src)
        sources[virtual_path(rel)] = src
    return sources


def collect_module_js_sources():
    sources = {}
    for mod_dir in sorted(MODULES.iterdir()):
        mod_file = mod_dir / "module.js"
        if not mod_file.exists():
            continue
        rel = mod_file.relative_to(ROOT).as_posix()
        src = mod_file.read_text(encoding="utf-8")
        src = rewrite_imports(src, rel)
        sources[virtual_path(rel)] = src
    return sources


def collect_css():
    parts = []
    base = SHARED_STYLE / "base.css"
    if base.exists():
        parts.append(f"/* base.css */\n{base.read_text(encoding='utf-8')}")
    for theme in sorted((SHARED_STYLE / "themes").glob("*.css")):
        parts.append(f"/* themes/{theme.name} */\n{theme.read_text(encoding='utf-8')}")
    for mod_dir in sorted(MODULES.iterdir()):
        css = mod_dir / "module.css"
        if css.exists():
            parts.append(f"/* modules/{mod_dir.name}/module.css */\n{css.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def build_bundle():
    print("Building single-file bundle...")
    entries = collect_entries()
    si = build_search_index(entries)
    (SHARED_DATA / "search-index.json").write_text(json.dumps(si, indent=2, ensure_ascii=False) + "\n")
    col = build_colophon(entries)
    (SHARED_DATA / "colophon.json").write_text(json.dumps(col, indent=2, ensure_ascii=False) + "\n")

    css = collect_css()
    shared_sources = collect_shared_js_sources()
    module_sources = collect_module_js_sources()
    data = collect_bundle_data()

    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    index_html = re.sub(r'<link\s+rel="stylesheet"\s+href="shared/style/[^"]+"\s*>\s*', "", index_html)
    index_html = re.sub(r'<script\s+type="module"\s+src="shared/js/app\.js"\s*></script>\s*', "", index_html)

    boot = []
    boot.append("// Inlined data")
    boot.append("window.__CRUCIBLE_DATA__ = " + json.dumps(data, ensure_ascii=False) + ";")
    boot.append("// Inlined module sources for dynamic import via blob URLs")
    boot.append("window.__CRUCIBLE_MODULES_SRC__ = " + json.dumps(module_sources, ensure_ascii=False) + ";")
    boot.append("(function() {")
    boot.append("  const sources = " + json.dumps(shared_sources, ensure_ascii=False) + ";")
    boot.append("  const map = { imports: {} };")
    boot.append("  for (const [path, src] of Object.entries(sources)) {")
    boot.append("    const blob = new Blob([src], { type: 'application/javascript' });")
    boot.append("    map.imports[path] = URL.createObjectURL(blob);")
    boot.append("  }")
    boot.append("  const el = document.createElement('script');")
    boot.append("  el.type = 'importmap';")
    boot.append("  el.textContent = JSON.stringify(map);")
    boot.append("  document.head.appendChild(el);")
    boot.append("  const entryEl = document.createElement('script');")
    boot.append("  entryEl.type = 'module';")
    boot.append("  entryEl.textContent = 'import \"" + virtual_path("shared/js/app.js") + "\";';")
    boot.append("  document.head.appendChild(entryEl);")
    boot.append("})();")
    boot_js = "\n".join(boot)

    inlined_style = f"<style>\n{css}\n</style>"
    inlined_boot = f"<script>\n{boot_js}\n</script>"

    if "</head>" in index_html:
        replacement = inlined_style + "\n" + inlined_boot + "\n</head>"
        index_html = index_html.replace("</head>", replacement, 1)
    else:
        print("WARN: index.html has no </head>; bundle may not render", file=sys.stderr)

    out = ROOT / "crucible-bundle.html"
    out.write_text(index_html, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"Wrote {out.name} ({size_kb:.1f} KB)")
    print(f"  CSS: {len(css)/1024:.1f} KB")
    print(f"  shared JS files: {len(shared_sources)}")
    print(f"  module JS files: {len(module_sources)}")
    print(f"  data entries: {len(data)}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--bundle", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    entries = collect_entries()
    if not args.quiet and not args.bundle:
        print(f"Collected {len(entries)} entries across {len(list(MODULES.iterdir()))} module folders.")

    if args.check:
        return check(entries, verbose=not args.quiet)

    if args.bundle:
        return build_bundle()

    si = build_search_index(entries)
    si_path = SHARED_DATA / "search-index.json"
    si_path.write_text(json.dumps(si, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {si_path.relative_to(ROOT)} ({len(si['entries'])} indexed).")

    col = build_colophon(entries)
    col_path = SHARED_DATA / "colophon.json"
    col_path.write_text(json.dumps(col, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    nz = sum(1 for s in col["sources"] if s["citationCount"] > 0)
    print(f"Wrote {col_path.relative_to(ROOT)} ({nz} of {len(col['sources'])} sources cited).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
