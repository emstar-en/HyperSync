Consolidation -11-01T15:19:52.291643Z

Added base schemas:
- spec-pack/schemas/common/ReceiptBase.schema.json
- spec-pack/schemas/geometry/EncodedEntityBase.schema.json
- spec-pack/schemas/common/TransportEnvelopeBase.schema.json
- spec-pack/schemas/common/QuorumKeyring.schema.json
- spec-pack/schemas/ops/EnvelopeRouteOp.schema.json

Files created:
- spec-pack/schemas/common/ReceiptBase.schema.json
- spec-pack/schemas/geometry/EncodedEntityBase.schema.json
- spec-pack/schemas/common/TransportEnvelopeBase.schema.json
- spec-pack/schemas/common/QuorumKeyring.schema.json
- spec-pack/schemas/ops/EnvelopeRouteOp.schema.json
- spec-pack/tools/cli_common.py
- spec-pack/tools/ops_router.py

Files modified:
- spec-pack/schemas/geom/CausalEnvelopeReceipt.schema.json
- spec-pack/schemas/privacy/PresenceReceipt.schema.json
- spec-pack/schemas/privacy/AnonymousEntryReceipt.schema.json
- spec-pack/schemas/systemf/SystemFReceipt.schema.json
- spec-pack/schemas/systemf/SystemFErasureReceipt.schema.json
- spec-pack/MANIFEST.json
- spec-pack/modules/ico-sync/module.json

Receipts updated to extend ReceiptBase (and transport where applicable).
Encoded geometry schemas updated to extend EncodedEntityBase.
MANIFEST capsules updated (common_bases, ops) and aliases added.
Module arrays updated to include new schemas/tools.
