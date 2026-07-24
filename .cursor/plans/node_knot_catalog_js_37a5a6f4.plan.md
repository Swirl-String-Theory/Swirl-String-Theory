---
name: Node knot catalog JS
overview: Rename VortexLab knot catalog JS files to knots_data_*, add a typed Node/TS loader + example, ship in npm, and test all three catalogs in SSTcore_full_probe.js (load/lookup checks + JSON summaries; knotplot no longer skipped).
todos:
  - id: rename
    content: git mv three catalog JS files to knots_data_{fourier,ideal,knotplot}.js in SSTcore/resources
    status: completed
  - id: loader
    content: Add resources/load_knot_catalogs.js + load_knot_catalogs.d.ts (typed Node/TS load API)
    status: completed
  - id: example
    content: Add examples/example_knot_catalogs.ts (+ package.json script); show JS require and TS import usage
    status: completed
  - id: pack
    content: Add knots_data_*.js + loader (+ .d.ts) to package.json files[]
    status: completed
  - id: probe
    content: Extend SSTcore_full_probe.js to load+test all three JS catalogs (ideal/fseries/knotplot); print + JSON summaries; fail checks if load/lookup broken
    status: completed
  - id: docs-verify
    content: Document load patterns; run example + SSTcore_full_probe.js --json-out and confirm js_catalog fields
    status: completed
isProject: false
---

# Node knot catalog resources (VortexLab parity)

## Why

VortexLab loads these as classic browser scripts and reads `IDEAL_KNOT_*`, `FSERIES_KNOT_*`, `KNOTPLOT_KNOT_*`. In SSTcore they live under `resources/` but are awkward to use from Node and are not shipped in the npm pack.

**Chosen approach:** rename to `knots_data_<source>.js`, add a typed on-demand loader usable from JS and TS, ship an example, and **exercise the catalogs in [`SSTcore_full_probe.js`](c:/workspace/projects/SSTcore/SSTcore_full_probe.js)** so Node CI/manual probes catch missing or broken data. Do **not** attach the full DBs to `require('sst-core')`.

## Rename (canonical in SSTcore)

| Current | New |
|---------|-----|
| `fourier_knots_data.js` | [`resources/knots_data_fourier.js`](c:/workspace/projects/SSTcore/resources/knots_data_fourier.js) |
| `ideal_knots_data.js` | [`resources/knots_data_ideal.js`](c:/workspace/projects/SSTcore/resources/knots_data_ideal.js) |
| `knotplot_knots_data.js` | [`resources/knots_data_knotplot.js`](c:/workspace/projects/SSTcore/resources/knots_data_knotplot.js) |

- `git mv` for history; keep global symbol names (`IDEAL_KNOT_DB`, etc.) unchanged.
- Workbench VortexLab copies/script tags stay on old filenames (separate sync).

## How to load in JS / TS

### Loader module

Add [`resources/load_knot_catalogs.js`](c:/workspace/projects/SSTcore/resources/load_knot_catalogs.js) + matching [`resources/load_knot_catalogs.d.ts`](c:/workspace/projects/SSTcore/resources/load_knot_catalogs.d.ts).

Implementation: `vm.runInNewContext` on each catalog script (sandbox with `window` for knotplot), return `{ source, ids, db }` without rewriting the generated files to `module.exports`.

**Types (sketch):**

```ts
export type KnotCatalogSource = 'ideal' | 'fseries' | 'knotplot';

export interface KnotCatalogEntry {
  knotId?: string;
  label?: string;
  components?: unknown[];
  // other VortexLab fields present; coeffs stay opaque to consumers that only need metadata
  [key: string]: unknown;
}

export interface KnotCatalog {
  source: KnotCatalogSource;
  ids: string[];
  db: Record<string, KnotCatalogEntry>;
}

export function loadIdealCatalog(): KnotCatalog;
export function loadFseriesCatalog(): KnotCatalog;
export function loadKnotplotCatalog(): KnotCatalog;
export function loadAllKnotCatalogs(): {
  ideal: KnotCatalog;
  fseries: KnotCatalog;
  knotplot: KnotCatalog;
};
export function catalogPaths(): Record<KnotCatalogSource, string>;
```

Lazy: each `load*Catalog()` parses only that file (knotplot ~1.1 MB only when asked).

### Usage — CommonJS (JS)

```js
const {
  loadIdealCatalog,
  loadFseriesCatalog,
  loadKnotplotCatalog,
} = require('sst-core/resources/load_knot_catalogs');

const ideal = loadIdealCatalog();
const trefoil = ideal.db['3:1:1'];
console.log(ideal.ids.length, trefoil?.label ?? trefoil?.knotId);
```

### Usage — TypeScript (ESM / tsx, same as other examples)

```ts
import {
  loadIdealCatalog,
  loadFseriesCatalog,
  loadKnotplotCatalog,
} from '../resources/load_knot_catalogs';
// or after install: 'sst-core/resources/load_knot_catalogs'

const fseries = loadFseriesCatalog();
const entry = fseries.db['3_1'];
console.log(fseries.source, fseries.ids.includes('3_1'), entry?.components?.length);
```

Document both patterns in [`docs/VORTEXLAB_NODE_CAPABILITIES.md`](c:/workspace/projects/SSTcore/docs/VORTEXLAB_NODE_CAPABILITIES.md) under a short “Knot catalog JS (Node)” section.

## Example

Add [`examples/example_knot_catalogs.ts`](c:/workspace/projects/SSTcore/examples/example_knot_catalogs.ts) (same style as [`examples/example_knot.ts`](c:/workspace/projects/SSTcore/examples/example_knot.ts)):

1. Load ideal + fseries + knotplot via the loader.
2. Print id counts and a few sample keys.
3. For one entry per catalog, print metadata only (`knotId`, `label`, component count, `L`/`D` if present) — **do not** print full coefficient arrays.
4. Optionally look up one id and pass a compact note that native `loadKnot` / embedded ideal APIs remain the C++ path for dynamics.

Wire:

- `package.json` script: `"example:knot-catalogs": "tsx examples/example_knot_catalogs.ts"`
- Include in [`scripts/run_node_examples.js`](c:/workspace/projects/SSTcore/scripts/run_node_examples.js) / examples README list if other examples are listed there.

## Ship in npm package

Add to [`package.json`](c:/workspace/projects/SSTcore/package.json) `files`:

- `resources/knots_data_ideal.js`
- `resources/knots_data_fourier.js`
- `resources/knots_data_knotplot.js`
- `resources/load_knot_catalogs.js`
- `resources/load_knot_catalogs.d.ts`

Ensure `require('sst-core/resources/load_knot_catalogs')` resolves after install (path under package root; no need to put catalogs on `main`).

## Probe tests (`SSTcore_full_probe.js`)

The full probe is the automated check that the catalogs load and look sane. Extend the existing catalog sections (today knotplot is skipped):

```572:578:c:/workspace/projects/SSTcore/SSTcore_full_probe.js
function probeKnotplotCatalog() {
  return {
    catalog_ok: null,
    skipped: true,
    skip_reason: 'knotplot filesystem catalog is Python-package specific; Node uses embedded ideal/fseries APIs',
    errors: [],
  };
}
```

### Shared helper

- `require('./resources/load_knot_catalogs')` (repo root; same layout when packaged beside the probe).
- `summarizeJsCatalog(catalog, sampleIds)` → `{ load_ok, source, path, id_count, sample_hits: [{ id, present, component_count, L, D, label }], error }` — **no** coeffs / full `db` in the report.

### Per-section checks

| Section | Keep (native) | Add (JS catalog tests) |
|---------|---------------|-------------------------|
| `probeIdealCatalog` | `getEmbeddedIdealFiles` + topology lookups | Load `knots_data_ideal.js`; assert `ids.length > 0`; samples `3:1:1`, `4:1:1`, `L2a1` present in `db` with `components.length >= 1` |
| `probeKnotsFourierSeriesCatalog` | `getEmbeddedKnotFiles` / `loadKnot` | Load `knots_data_fourier.js`; assert ids non-empty; samples `3_1`, `4_1`, `5_2` in `db` |
| `probeKnotplotCatalog` | remove skip stub | Load `knots_data_knotplot.js`; assert ids non-empty; samples `knot_3.1`, `torus_6.9` in `db`; record `family`/`status` if present |

`catalog_ok` for each section becomes true only when **both** native path (where applicable) **and** JS catalog checks pass (for knotplot: JS-only). Push load/lookup failures into `errors[]`.

### Console + JSON

- Print headers like `Ideal catalog (JS)` / update knotplot header to show `js_id_count`, `js_load_ok`, sample hit lines (not `skipped`).
- `--json-out` includes `ideal_catalog.js_catalog`, `knots_fourier_series_catalog.js_catalog`, `knotplot_catalog.js_catalog` as summaries only.
- Guard: if someone accidentally assigns full `db` into the report object, strip/summarize before `JSON.stringify` (same pattern as embedded knot dump hardening).

### Run as verification

```bash
node SSTcore_full_probe.js --json-out output/sstcore_probe_node_catalogs.json
```

Expect exit 0, `knotplot_catalog.catalog_ok === true`, and `js_catalog.load_ok === true` on all three sections; JSON file stays small (no multi‑MB dump).

## Out of scope

- Rewriting generated catalog bodies to `module.exports`.
- Workbench/VortexLab filename migration.
- Binding catalogs into C++ / changing `ParticleEvaluator` defaults.

## Verify

- Renamed files only under `knots_data_*.js`.
- `node -e "require('./resources/load_knot_catalogs').loadIdealCatalog()"` → non-empty `ids`.
- `npm run example:knot-catalogs` prints summaries.
- **`node SSTcore_full_probe.js --json-out …`** exercises and reports all three JS catalogs; knotplot no longer skipped.
