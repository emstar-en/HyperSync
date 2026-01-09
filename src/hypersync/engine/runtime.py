from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
from pydantic import ValidationError
import json
from jsonschema import Draft7Validator, Draft202012Validator

from ..core.models import Intent
from ..receipts.codec import make_receipt, ReceiptProvenance
from ..router.simple_router import OperatorRegistry, SimpleRouter
from ..planner.rules import RulesPlanner
from ..policy.gate import PolicyGate
from ..operators.executor import OperatorExecutor
from ..utils.artifacts import ArtifactStore

class OperatorHandler:
    """Stub operator execution. Replace per-op with real logic."""
    def __init__(self, op_id: str):
        self.op_id = op_id

    def run(self, intent: Intent) -> Dict[str, Any]:
        return {
            "echo_params": intent.params,
            "context_keys": sorted(list(intent.context.keys())),
            "op_id": self.op_id,
            "note": "stub-execution",
        }

class Runtime:


    def _validate_output_schema(self, op_meta: dict, outputs: dict) -> tuple[bool, str|None]:
        schema = None
        if isinstance(op_meta, dict):
            schema = op_meta.get('output_schema')
        if isinstance(schema, str):
            sp = self.spec_root / schema
            try:
                if sp.exists():
                    with open(sp, 'r', encoding='utf-8') as f:
                        import json as _json
                        schema = _json.load(f)
            except Exception:
                schema = None
        if not isinstance(schema, dict):
            return True, None
        try:
            validator = Draft202012Validator(schema) if ('$schema' in schema and '2020-12' in schema['$schema']) else Draft7Validator(schema)
            validator.validate(outputs)
            return True, None
        except Exception as e:
            return False, str(e)

    def _validate_operator_schema(self, op_meta: dict, params: dict) -> tuple[bool, str|None]:
        schema = None
        # inline schema
        if isinstance(op_meta, dict):
            schema = op_meta.get('input_schema') or op_meta.get('schema')
        # schema as path
        if isinstance(schema, str):
            sp = self.spec_root / schema
            try:
                if sp.exists():
                    with open(sp, 'r', encoding='utf-8') as f:
                        import json as _json
                        schema = _json.load(f)
            except Exception:
                schema = None
        if not isinstance(schema, dict):
            return True, None
        try:
            validator = Draft202012Validator(schema) if ('$schema' in schema and '2020-12' in schema['$schema']) else Draft7Validator(schema)
            validator.validate(params)
            return True, None
        except Exception as e:
            return False, str(e)


    def _validate_operator_params(self, op_meta: dict, params: dict) -> tuple[bool, str|None]:
        # Expect shape: op_meta.get('params', {}).get('required', [...])
        req = []
        try:
            req = op_meta.get('params', {}).get('required', []) if isinstance(op_meta, dict) else []
        except Exception:
            req = []
        missing = [k for k in req if k not in params]
        if missing:
            return False, f"Missing required params: {', '.join(missing)}"
        return True, None

    def __init__(self, spec_root: Path, policy_path: Path | None = None):
        self.spec_root = spec_root
        operators_dir = spec_root / "operators"
        self.registry = OperatorRegistry(operators_dir)
        self.router = SimpleRouter(self.registry)
        self.planner = RulesPlanner(spec_root)
        self.gate = PolicyGate(policy_path)
        self.executor = OperatorExecutor(spec_root)
        self.artifacts = ArtifactStore()

    def run_intent(self, intent_dict: Dict[str, Any]):
        try:
            intent = Intent.model_validate(intent_dict)
        except ValidationError as e:
            outputs = {"validation_error": e.errors()}
            return make_receipt(Intent(), op="N/A", outputs=outputs, status="FAIL")

        allow, reason = self.gate.check(intent.model_dump())
        if not allow:
            outputs = {"denied": True, "reason": reason}
            return make_receipt(intent, op="N/A", outputs=outputs, status="FAIL")

        op = self.router.resolve(intent.op)
        if not op:
            # attempt to plan from routing rules and builtin mappings
            op, why = self.planner.plan(intent.model_dump())
        if not op:
            outputs = {"error": "No operator resolved", "hint": intent.op}
            return make_receipt(intent, op="N/A", outputs=outputs, status="FAIL")
        # Apply planner parameter injections if provided
        try:
            plan_set = getattr(self.planner, 'last_set', {}) or {}
            if isinstance(plan_set, dict):
                add_params = (plan_set.get('params') or {}) if isinstance(plan_set.get('params'), dict) else {}
                if add_params:
                    intent.params.update({k:v for k,v in add_params.items() if k not in intent.params})
        except Exception:
            pass

        # Load operator metadata to enforce policy constraints
        op_meta = {}
        op_path = self.registry.get(op)
        if op_path:
            import json
            try:
                op_meta = json.loads(op_path.read_text())
            except Exception:
                op_meta = {}
        ok_op, reason_op = getattr(self.gate, "check_operator", lambda m: (True, None))(op_meta)
        if not ok_op:
            outputs = {"denied": True, "reason": reason_op}
            return make_receipt(intent, op=op, outputs=outputs, status="FAIL")
        # Validate operator required params if available
        ok_params, errp = self._validate_operator_params(op_meta, intent.params)
        if not ok_params:
            outputs = {"error": "InvalidParameters", "message": errp}
            return make_receipt(intent, op=op, outputs=outputs, status="FAIL")
        ok_schema, errs = self._validate_operator_schema(op_meta, intent.params)
        if not ok_schema:
            outputs = {"error": "SchemaValidation", "message": errs}
            return make_receipt(intent, op=op, outputs=outputs, status="FAIL")
        # Execute via operator executor
        try:
            outputs = self.executor.run(op, intent)
            prov = ReceiptProvenance(operator=op, policy=str(self.gate.policy_path) if getattr(self.gate, "policy_path", None) else None)
            # optional artifact save
            try:
                meta = intent.meta or {}
                import os as _os
                if meta.get('save_artifacts') or _os.getenv('HYPERSYNC_ARTIFACTS_DIR'):
                    ip = self.artifacts.put_json(intent.model_dump(), subdir='intents')
                    opmp = self.artifacts.put_json(op_meta or {}, subdir='operators')
                    outp = self.artifacts.put_json(outputs, subdir='outputs')
                    self.artifacts.write_manifest({'intent_path': str(ip), 'operator': op, 'op_meta_path': str(opmp), 'outputs_path': str(outp)})
            except Exception:
                pass
            ok_out, erro = self._validate_output_schema(op_meta, outputs)
            if not ok_out:
                return make_receipt(intent, op=op, outputs={'error':'OutputSchemaValidation','message':erro}, status='FAIL', provenance=prov)
            return make_receipt(intent, op=op, outputs=outputs, status='OK', provenance=prov)
        except Exception as e:
            outputs = {"error": type(e).__name__, "message": str(e)}
            return make_receipt(intent, op=op, outputs=outputs, status="FAIL")