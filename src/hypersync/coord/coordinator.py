from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Protocol, runtime_checkable, Optional, Tuple
from pathlib import Path
import time

from ..core.models import Intent
from ..planner.prefs import Preferences
from ..router.simple_router import OperatorRegistry
from ..receipts.codec import make_receipt, ReceiptProvenance
from ..operators.executor import OperatorExecutor
from ..hypergraph.model import HyperGraph, ModelNode
from ..hypergraph.embed import EmbeddingStore

@dataclass
class Message:
    role: str
    content: Any
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Envelope:
    src: str
    dst: str
    msg: Message
    ts: float = field(default_factory=lambda: time.time())

@dataclass
class Session:
    id: str
    graph: HyperGraph
    log: List[Envelope] = field(default_factory=list)
    scratch: Dict[str, Any] = field(default_factory=dict)

@runtime_checkable
class ModelAdapter(Protocol):
    def id(self) -> str: ...
    def capabilities(self) -> List[str]: ...
    def handle(self, env: Envelope, session: Session) -> Tuple[Any, Dict[str, Any]]: ...

class OperatorModel:
    def __init__(self, node: ModelNode, spec_root: Path):
        self.node = node
        self.exec = OperatorExecutor(spec_root)
    def id(self) -> str:
        return self.node.id
    def capabilities(self) -> List[str]:
        return self.node.capabilities
    def handle(self, env: Envelope, session: Session):
        # Expect env.msg.content to be Intent-like {op, params, meta}
        payload = env.msg.content if isinstance(env.msg.content, dict) else {}
        op = payload.get('op') or (self.node.meta.get('op') if self.node.meta else None)
        if not op:
            raise ValueError('OperatorModel needs op in content or node.meta.op')
        intent = Intent.model_validate({
            'op': op,
            'params': payload.get('params') or {},
            'meta': payload.get('meta') or {}
        })
        out = self.exec.run(op, intent)
        return out, {'type': 'operator', 'op': op}

class FunctionModel:
    def __init__(self, node: ModelNode, spec_root: Path):
        self.node = node
        self.spec_root = spec_root
    def id(self) -> str:
        return self.node.id
    def capabilities(self) -> List[str]:
        return self.node.capabilities
    def handle(self, env: Envelope, session: Session):
        # meta.func = 'tools/path.py:function_name' (relative to spec root)
        func_ref = (self.node.meta or {}).get('func')
        if not func_ref:
            raise ValueError('FunctionModel requires meta.func')
        rel, fn = func_ref.split(':', 1)
        from importlib.util import spec_from_file_location, module_from_spec
        mp = Path(self.spec_root) / rel
        spec = spec_from_file_location(f'hypersync_user.{mp.stem}', mp)
        if spec is None or spec.loader is None:
            raise ImportError(f'Cannot load {mp}')
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        f = getattr(mod, fn, None)
        if f is None:
            raise AttributeError(f'Function {fn} not found in {mp}')
        res = f(env.msg.content, session)
        return res, {'type': 'function', 'func': func_ref}

class Coordinator:
    def __init__(self, spec_root: Path, graph: HyperGraph, adapters: Dict[str, ModelAdapter], seed: int = 0, prefs: Preferences | None = None, gate=None):
        self.spec_root = spec_root
        self.graph = graph
        self.adapters = adapters
        self.embed = EmbeddingStore(8, -1.0, 0.98, seed)
        self.prefs = prefs
        self.gate = gate
        self.registry = OperatorRegistry(spec_root / "operators")

    def _score(self, current: str, candidate: str, task_tag: str | None) -> float:
        # Smaller is better (distance). Use hyperbolic distance between capability tags and task tag.
        # If task_tag not provided, use node ids for distance.
        a = task_tag or current
        b = candidate
        try:
            return self.embed.distance(a, b)
        except Exception:
            return 1e9

    def step(self, session: Session, src: str, candidates: List[str], message: Message, task_tag: str | None = None) -> Envelope:
        from ..routing.ops_routing import RoutingOps
        router = RoutingOps(seed=0, prefs=self.prefs, gate=self.gate, registry=self.registry)
        dst = router.next_hop(src, candidates, task_tag or src)
        env = Envelope(src=src, dst=dst, msg=message)
        adapter = self.adapters[dst]
        out, meta = adapter.handle(env, session)
        session.log.append(env)
        session.scratch[f'last.{dst}'] = {'out': out, 'meta': meta, 'ts': env.ts}
        return env

    def run_program(self, start: str, task: str, payload: Dict[str, Any], max_steps: int = 5) -> Dict[str, Any]:
        sess = Session(id=f'sess-{int(time.time()*1000)}', graph=self.graph)
        cur = start
        msg = Message(role='user', content=payload, meta={'task': task})
        for _ in range(max_steps):
            nbrs = self.graph.neighbors(cur)
            if not nbrs:
                break
            env = self.step(sess, cur, nbrs, msg, task_tag=task)
            cur = env.dst
            # termination: if node declares terminal
            node = self.graph.nodes.get(cur)
            if node and node.meta.get('terminal'):
                break
        return {
            'session_id': sess.id,
            'last_node': cur,
            'transcript': [e.__dict__ for e in sess.log],
            'scratch': sess.scratch,
        }
