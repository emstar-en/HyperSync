Op-JSON enablement and keyring migration - 2025-11-01T15:23:50.738996Z

Patched tools with add_common_args + load_envelope_op wiring (non-breaking):
- Patched tool: tools/attest.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/audit_tap_stub.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/blind_ticket_issuer.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/blind_ticket_validator.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/build_rasft_batch.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/causal_envelope.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/deploy.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/eval_grounding.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/f_check.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/f_erase.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/memory_compactor.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/persistent_mem_store.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/plan_factory.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/sign.py (add_common_args + load_envelope_op wiring)
- Patched tool: tools/validate_proposal.py (add_common_args + load_envelope_op wiring)

Examples added:
- spec-pack/examples/envelope_route_op.example.json
- spec-pack/examples/quorum_keyring.core.m2n3.example.json

MANIFEST updated with examples.
