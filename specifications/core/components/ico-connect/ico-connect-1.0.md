# ICO Connect 1.0 (Draft)

Purpose
- Network/interoperability profile for ICO. Negotiates geometry profiles (E/H/S), models, numeric policy, and attestation.

Handshake (high level)
1) ConnectHello: { icod_local, wants, attest_req? }
2) ConnectAccept: { chosen_profile, model, policy, attest? , session_id }
3) Optional Rekey/Renegotiate on policy change.

Session Envelope (normative fields)
- headers: { session_id, profile, model, policy_hash, seq, ts }
- payload: ICO Core objects per negotiated profile
- errors: policy_violation | out_of_domain | not_supported | attestation_failed

Policy Interaction
- Enforce no-Euclidean-intermediates when geometry_mode=native.
- Deterministic mode required for conformance.

Security
- mTLS or equivalent, mutual attestation optional via POL-ICO-ATTEST.

