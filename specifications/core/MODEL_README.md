# MODEL_README

This pack is optimized for LLM tooling. Key files:

- MANIFEST.json: high-level index and entry points.
- index.json: map of path -> {id, type, size}.
- bundle.jsonl: one JSON object per line with {path, id, content}.
- checksums.txt: SHA-256 hashes for integrity.

Guidelines:
- Favor geometry-native algorithms; no Euclidean intermediates.
- Use ALG-212/213/214 for exp/log/transport with curvature scaling.
- Proof API schemas under schemas/proof_api.schema.json.
