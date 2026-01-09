#!/usr/bin/env python3
# Concrete Gate System - Proofs Manifest Verification
import json, glob
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ProofEntry:
    id: str; kind: str; artifact_pattern: str; verified: bool = False

class ConcreteGateSystem:
    def __init__(self, config_path: Path, receipts_base: Path):
        self.config = json.load(open(config_path)) if config_path.exists() else {}
        self.receipts_base = receipts_base; self.proofs_manifest: Dict[str, List[ProofEntry]] = {}
        self._initialize_proofs_manifest()

    def _initialize_proofs_manifest(self):
        for category, proofs in self.config.get('proofs_manifest', {}).items():
            self.proofs_manifest[category] = [ProofEntry(p['id'], p['kind'], p['artifact']) for p in proofs]

    def verify_proof(self, proof_id: str) -> bool:
        for category, proofs in self.proofs_manifest.items():
            for proof in proofs:
                if proof.id == proof_id:
                    matches = glob.glob(str(self.receipts_base / proof.artifact_pattern))
                    proof.verified = bool(matches); return proof.verified
        return False

    def verify_all_proofs_for_category(self, category: str) -> Dict[str, bool]:
        return {proof.id: self.verify_proof(proof.id) for proof in self.proofs_manifest.get(category, [])}

    def get_proofs_manifest_status(self) -> Dict:
        return {category: {proof.id: {"kind": proof.kind, "artifact": proof.artifact_pattern, "verified": proof.verified} for proof in proofs} for category, proofs in self.proofs_manifest.items()}

    def enforce_gate_with_proofs(self, gate_name: str, required_proofs: List[str]) -> bool:
        print(f"[GATE] Enforcing {gate_name}")
        all_verified = all(self.verify_proof(pid) for pid in required_proofs)
        print(f"[GATE] {gate_name} {'PASSED' if all_verified else 'FAILED'}"); return all_verified
