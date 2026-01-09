from __future__ import annotations
from pathlib import Path
import json
from typing import Iterable
from .model import ModelNode, HyperEdge, HyperGraph

class SpecGraphBuilder:
    def __init__(self, spec_root: Path):
        self.spec_root = spec_root

    def iter_operator_specs(self) -> Iterable[Path]:
        ops = self.spec_root / 'operators'
        for p in sorted(ops.glob('op_*.json')):
            yield p

    def build(self, include_tags: set[str] | None = None) -> HyperGraph:
        g = HyperGraph()
        for op_path in self.iter_operator_specs():
            try:
                meta = json.loads(op_path.read_text())
            except Exception:
                meta = {}
            op_id = meta.get('id') or meta.get('op_id') or meta.get('name') or op_path.stem.replace('op_', 'op://').replace('_v', '@v')
            caps = [op_id]
            if include_tags:
                tags = [t for t in caps if any(tag in t for tag in include_tags)]
                if not tags:
                    continue
            node = ModelNode(id=op_id, kind='operator', capabilities=caps, meta={'op': op_id})
            g.add_node(node)
        # fully connect lightly via a small number of random hyperedges for demo; real edges come from rules/plugins
        ids = list(g.nodes.keys())
        for i in range(0, len(ids), 8):
            chunk = ids[i:i+8]
            if len(chunk) >= 2:
                g.add_edge(HyperEdge(label='ops', nodes=chunk, weight=1.0))
        return g




class SpecGraphBuilderRules(SpecGraphBuilder):
    def _load_tag_rules(self):
        import json
        p = self.spec_root / 'planner' / 'registry' / 'plugins.json'
        try:
            data = json.loads(p.read_text())
            tag_rules = data.get('plugins', [])
            tags = {}
            for pl in tag_rules:
                if isinstance(pl, dict) and 'tag_rules' in pl:
                    for k,v in (pl.get('tag_rules') or {}).items():
                        tags[k] = list(v) if isinstance(v, list) else []
            return tags
        except Exception:
            return {}

    def _load_routing_rules(self):
        import json
        p = self.spec_root / 'planner' / 'routing' / 'geometric_unified.rules.json'
        try:
            data = json.loads(p.read_text())
            return data
        except Exception:
            return {}

    def _load_ext_solver_manifests(self):
        manifests = {}
        try:
            base = self.spec_root / 'ext' / 'solvers'
            if base.exists():
                for m in base.rglob('*.json'):
                    try:
                        data = json.loads(m.read_text())
                        sid = data.get('impl_id') or data.get('id')
                        if sid:
                            manifests[sid] = data
                    except Exception:
                        continue
        except Exception:
            pass
        return manifests

    def _family_prefix(self, fam_key: str) -> str:
        key = fam_key.split('*', 1)[0]
        return key.rstrip('_').lower()

    def _belongs_family(self, node_id: str, fam_prefix: str) -> bool:
        s = (node_id or '').lower()
        return (f'://{fam_prefix}/' in s) or (f'://{fam_prefix}_' in s) or (f'/{fam_prefix}/' in s)

    def _apply_tags(self, node, tag_rules: dict):
        idl = (node.id or '').lower()
        tags = []
        flags = []
        for tg, subs in (tag_rules or {}).items():
            try:
                if any(str(s).lower() in idl for s in subs):
                    tags.append(tg)
                    if str(tg).endswith('_preferred'):
                        flags.append(tg)
            except Exception:
                continue
        meta = node.meta or {}
        meta['tags'] = sorted(set((meta.get('tags') or []) + tags))
        if flags:
            meta['flags'] = sorted(set((meta.get('flags') or []) + flags))
        node.meta = meta

    def _mark_conformance_exact(self, g: HyperGraph):
        # Exact-ish: search node ids in vector JSON contents and filenames
        import json
        base = self.spec_root / 'conformance'
        if not base.exists():
            return
        vec_files = list(base.rglob('*.vector.json'))
        if not vec_files:
            return
        # Precompute search forms for ids
        def forms(s: str):
            s = s.lower()
            yield s
            if '://' in s:
                yield s.split('://',1)[1]
            yield s.replace('op://','').replace('solver://','')
            yield s.replace('@v',' ').replace('@',' ')
        for nid, node in g.nodes.items():
            nid_forms = set(forms(nid))
            found=False
            for vf in vec_files:
                try:
                    txt=vf.read_text().lower()
                except Exception:
                    continue
                for f in nid_forms:
                    if f and f in txt:
                        found=True
                        break
                if found:
                    break
            if found:
                node.meta.setdefault('flags', [])
                if 'has_conformance' not in node.meta['flags']:
                    node.meta['flags'].append('has_conformance')

    def build(self, include_tags: set[str] | None = None) -> HyperGraph:
        g = HyperGraph()
        tag_rules = self._load_tag_rules()
        rules = self._load_routing_rules()
        families = (rules.get('task_family_patterns') or {}) if isinstance(rules, dict) else {}
        fallback_map = ((rules.get('selection') or {}).get('fallbacks') or {}) if isinstance(rules, dict) else {}
        ext_man = self._load_ext_solver_manifests()

        # 1) Build operator nodes from operators specs
        op_nodes = []
        for op_path in self.iter_operator_specs():
            try:
                meta = json.loads(op_path.read_text())
            except Exception:
                meta = {}
            op_id = meta.get('id') or meta.get('op_id') or meta.get('name') or op_path.stem.replace('op_', 'op://').replace('_v', '@v')
            node = ModelNode(id=op_id, kind='operator', capabilities=[op_id], meta={'op': op_id})
            if isinstance(meta, dict):
                for k in ('estimated_cost', 'deterministic', 'precision', 'deny_tiers'):
                    if k in meta:
                        node.meta[k] = meta[k]
            self._apply_tags(node, tag_rules)
            g.add_node(node)
            op_nodes.append(node.id)

        # 2) Add solver nodes per families and connect via rule-derived edges
        solver_nodes = set()
        for fam_key, obj in families.items():
            if not isinstance(obj, dict):
                continue
            fam_prefix = self._family_prefix(fam_key)
            candidates = list(obj.get('candidates') or [])
            prefer_tags = list(obj.get('prefer_tags') or [])
            deny_tiers = set(obj.get('deny_tiers') or [])

            # create solver nodes
            for sid in candidates:
                if sid not in g.nodes:
                    s_meta = {'tags': prefer_tags or []}
                    if deny_tiers:
                        s_meta['deny_tiers'] = sorted(list(deny_tiers))
                    # merge ext manifest if available
                    man = ext_man.get(sid)
                    if isinstance(man, dict):
                        if man.get('precision'): s_meta['precision']=man['precision']
                        if man.get('tags'): s_meta['tags']=sorted(set(s_meta.get('tags',[])+list(man['tags'])))
                        if man.get('geodesic_preferred'):
                            s_meta.setdefault('flags', [])
                            s_meta['flags'].append('geodesic_preferred')
                    g.add_node(ModelNode(id=sid, kind='solver', capabilities=[sid], meta=s_meta))
                    solver_nodes.add(sid)
            # connect operators of this family to candidate solvers
            fam_ops = [nid for nid in op_nodes if self._belongs_family(nid, fam_prefix)]
            if fam_ops and candidates:
                for nid in fam_ops:
                    g.add_edge(HyperEdge(label=f'family:{fam_prefix}', nodes=sorted(set([nid] + candidates)), weight=1.0))

            # also connect fallbacks if specified for a family alias (exact prefix match)
            fb = fallback_map.get(fam_prefix) or []
            if fb:
                for sid in fb:
                    if sid not in g.nodes:
                        g.add_node(ModelNode(id=sid, kind='solver', capabilities=[sid], meta={'tags': prefer_tags or []}))
                        solver_nodes.add(sid)
                for nid in fam_ops:
                    g.add_edge(HyperEdge(label=f'fallback:{fam_prefix}', nodes=sorted(set([nid] + list(fb))), weight=1.0))

        # 3) Secondary tag-based edges
        by_tag = {}
        for nid, n in g.nodes.items():
            for t in (n.meta or {}).get('tags') or []:
                by_tag.setdefault(t, []).append(nid)
        for t, ids in by_tag.items():
            uniq = sorted(set(ids))
            if len(uniq) >= 2:
                g.add_edge(HyperEdge(label=f'tag:{t}', nodes=uniq, weight=0.5))

        # 4) Exact conformance mapping
        self._mark_conformance_exact(g)

        return g
