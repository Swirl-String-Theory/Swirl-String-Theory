---
name: Clear Node20 CI Warnings
overview: Clear Node.js 20 deprecation annotations across wheels/PyPI and npm workflows by bumping actions to Node-24 runtimes, replacing the MSVC helper, and renaming npm.yml to build-npm.yml.
todos:
  - id: branch-from-master
    content: Work on current branch sstcore/colocate-node-bindings (no new branch)
    status: completed
  - id: bump-build-wheels
    content: Bump Node-24 actions + MSVC helper in build-wheels.yml
    status: completed
  - id: bump-release-pypi
    content: Bump matching pins in release-pypi.yml
    status: completed
  - id: rename-bump-npm
    content: Rename npm.yml → build-npm.yml; bump Node-24 actions + MSVC; update docs refs
    status: completed
  - id: bump-release-npm
    content: Bump matching pins in release-npm.yml
    status: completed
  - id: verify-ci
    content: Dispatch Build Wheels + Build npm; confirm Node 20 annotations are gone
    status: completed
isProject: false
---

# Clear Node 20 deprecation warnings (wheels + npm)

## Cause

These are **not** Python/Node build failures. GitHub forces JS actions onto Node 24, but workflows still pin majors whose `action.yml` declares `using: node20`. Annotations list:

- `actions/checkout@v4`
- `actions/setup-python@v5` / `actions/setup-node@v4`
- `actions/upload-artifact@v4` (+ matching `download-artifact@v4`)
- `ilammy/msvc-dev-cmd@v1` (Windows; upstream still node20)

## Approach

Execute on the **current branch** `sstcore/colocate-node-bindings` (user-approved; no separate branch from master). Bump all four workflows to Node-24 action majors. Keep step logic, matrices, and publish inputs unchanged.

Also rename [`npm.yml`](c:\workspace\projects\SSTcore\.github\workflows\npm.yml) → **`build-npm.yml`** and set workflow `name: Build npm` (parallel to `Build Wheels` / `Release (npm — manual)`).

| Current | Target | Why |
| --- | --- | --- |
| `actions/checkout@v4` | `actions/checkout@v5` | First major with `runs.using: node24`; same inputs we use |
| `actions/setup-python@v5` | `actions/setup-python@v6` | Node 24; `python-version` API unchanged |
| `actions/setup-node@v4` | `actions/setup-node@v6` | Node 24 action runtime; matrix `node-version: 18.x–24.x` stays (project under test, not the action runtime) |
| `actions/upload-artifact@v4` | `actions/upload-artifact@v7` | Node 24; keep `name` / `path` / `retention-days` |
| `actions/download-artifact@v4` | `actions/download-artifact@v7` | Node 24 pair for upload v6+; keep `pattern` / `merge-multiple` |
| `ilammy/msvc-dev-cmd@v1` | `TheMrMilchmann/setup-msvc-dev@v4` | Node 24 MSVC env; `arch: x64` |

Leave as-is (not in the annotation lists for these runs):

- `pypa/gh-action-pypi-publish@release/v1`
- `mymindstorm/setup-emsdk@v14` (may still warn on publish jobs; out of scope unless it appears after the bump)
- `actions/create-release@v1` in build-npm (legacy; separate cleanup)

## Files to change

1. [`build-wheels.yml`](c:\workspace\projects\SSTcore\.github\workflows\build-wheels.yml) — bump pins + MSVC helper
2. [`release-pypi.yml`](c:\workspace\projects\SSTcore\.github\workflows\release-pypi.yml) — same
3. **Rename** `npm.yml` → [`build-npm.yml`](c:\workspace\projects\SSTcore\.github\workflows\build-npm.yml):
   - `name: Build npm`
   - bump checkout / setup-node / upload-artifact / MSVC
   - update header comment to match `build-wheels.yml` naming
4. [`release-npm.yml`](c:\workspace\projects\SSTcore\.github\workflows\release-npm.yml) — bump checkout / setup-node
5. Docs that hard-code the old path/name:
   - [`docs/SETUP_NPM_PUBLISHING.md`](c:\workspace\projects\SSTcore\docs\SETUP_NPM_PUBLISHING.md) (`npm.yml` → `build-npm.yml`, “NPM package” → “Build npm”)

Example Windows MSVC step (wheels + build-npm):

```yaml
- name: Use x64 native MSVC (Windows)
  if: matrix.os == 'windows-latest'
  uses: TheMrMilchmann/setup-msvc-dev@v4
  with:
    arch: x64
```

## Verify

1. Push branch.
2. Dispatch **Build Wheels** and **Build npm** (`workflow_dispatch`).
3. Confirm run summaries have **no** “Node.js 20 is deprecated…” for checkout / setup-python / setup-node / upload-artifact / msvc.
4. Spot-check one Windows + one Linux job still passes on each workflow.

## Out of scope

- No Python/setup.py or npm package-name changes
- No Node test-matrix changes (18–24 stay)
- No merge to master until CI is green
- No `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` / insecure-node env hacks
