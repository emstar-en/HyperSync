
# HyperSync Code Generation Workflow

This directory makes the spec pack self-contained for rebuilding the HyperSync Python runtime.

## Contents

- `manifest.json` — high-level blueprint for the runtime assets.
- `templates/runtime/` — canonical project tree (package, tests, `pyproject.toml`, README).
- `scripts/render_runtime.py` — idempotent copier that materializes the runtime into a destination directory.
- `scripts/auto_build.py` — one-shot automation that renders, (optionally) tests, and packages the runtime.

## Fast path (single command)

```bash
python codegen/scripts/auto_build.py --workspace ./build/runtime --artifact-dir ./build/artifacts --formats zip wheel
```

This produces a fresh runtime under `build/runtime/`, runs `pytest` (unless `--skip-tests` is supplied), and deposits the requested package formats (zip, tar, sdist, wheel) in `build/artifacts/` alongside a `codegen-summary.json` manifest.

## Manual rendering

```bash
python codegen/scripts/render_runtime.py --out ./build/hypersync
cd build/hypersync
pip install -e .
pytest
```

## Regenerating templates

If you update the runtime, run the helper below to refresh the templates before archiving the spec pack:

```bash
python tools/export_runtime_templates.py --source ../../workspace --dest codegen/templates/runtime
```

(This helper is not included in the spec pack; keep it in your local automation scripts.)
