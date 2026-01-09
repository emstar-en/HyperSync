from __future__ import annotations
import json
import click
from pathlib import Path
from rich import print
from rich.table import Table

from .utils.fs import resolve_root
from .spec_loader import SpecLoader
from .schema_validator import SchemaValidator
from .conformance.runner import ConformanceRunner
from .routing.registry import RoutingRegistry
from .diagnostics.diag import Diagnostics
from .service import ServiceTierRegistry


from .nvm.hvs_cli import hvs_cli
@click.group()
@click.option('--spec-root', type=click.Path(exists=False, file_okay=False, dir_okay=True), default=None, help='Path to unzipped spec pack root (defaults to ./spec_pack or $HYPERSYNC_SPEC_ROOT).')
@click.pass_context
def cli(ctx, spec_root):
    ctx.ensure_object(dict)
    ctx.obj['spec_root'] = spec_root



# Register HVS commands
cli.add_command(hvs_cli)
@cli.command()
@click.pass_context
def inspect(ctx):
    loader = SpecLoader(ctx.obj['spec_root'])
    dirs = loader.dirs()
    schemas = loader.list_schemas()
    vectors = loader.list_vectors()
    ops = loader.list_operators()
    tiers = loader.list_service_tier_caps()
    rr = RoutingRegistry(loader.root)

    table = Table(title='HyperSync Spec Pack Summary')
    table.add_column('Category')
    table.add_column('Path')
    table.add_column('Count')
    table.add_row('schemas', str(dirs.get('schemas')), str(len(schemas)))
    table.add_row('vectors', str(dirs.get('vectors')), str(len(vectors)))
    table.add_row('operators', str(dirs.get('operators')), str(len(ops)))
    table.add_row('service.tiers', 'refs/caps', str(len(tiers)))
    table.add_row('routing.plugins', 'planner/registry/plugins.json', str(rr.summary().get('num_plugins', 0)))
    table.add_row('routing.rules', 'planner/routing/geometric_unified.rules.json', str(rr.summary().get('num_rules', 0)))
    print(table)

@cli.group()
@click.pass_context
def list(ctx):
    pass

@list.command('schemas')
@click.pass_context
def list_schemas(ctx):
    loader = SpecLoader(ctx.obj['spec_root'])
    for p in loader.list_schemas()[:200]:
        print(p)
    if len(loader.list_schemas()) > 200:
        print(f"... ({len(loader.list_schemas()) - 200} more)")

@list.command('vectors')
@click.pass_context
def list_vectors(ctx):
    loader = SpecLoader(ctx.obj['spec_root'])
    for p in loader.list_vectors()[:200]:
        print(p)
    if len(loader.list_vectors()) > 200:
        print(f"... ({len(loader.list_vectors()) - 200} more)")

@list.command('operators')
@click.pass_context
def list_ops(ctx):
    loader = SpecLoader(ctx.obj['spec_root'])
    for p in loader.list_operators()[:200]:
        print(p)
    if len(loader.list_operators()) > 200:
        print(f"... ({len(loader.list_operators()) - 200} more)")

@list.command('tiers')
@click.pass_context
def list_tiers(ctx):
    loader = SpecLoader(ctx.obj['spec_root'])
    registry = ServiceTierRegistry(loader)
    for tier in registry.tiers():
        print(tier)

@cli.command()
@click.option('--file', 'file_', type=click.Path(exists=True, dir_okay=False), required=True)
@click.option('--schema', 'schema_', type=click.Path(exists=True, dir_okay=False), required=True)
@click.pass_context
def validate(ctx, file_, schema_):
    """Validate a JSON file against a JSON Schema from the spec pack."""
    ok, err = SchemaValidator().validate(Path(file_), Path(schema_))
    if ok:
        print("[green]OK[/green] validation passed")
    else:
        print(f"[red]FAIL[/red] {err}")

@cli.command('conformance-smoke')
@click.option('--limit', type=int, default=20, help='Max files to display')
@click.pass_context
def conf_smoke(ctx, limit):
    loader = SpecLoader(ctx.obj['spec_root'])
    runner = ConformanceRunner(loader.dirs()['vectors'])
    runner.smoke(limit=limit)

@cli.command("run-intent")
@click.option("--intent", "intent_path", type=click.Path(exists=True, dir_okay=False), required=True, help="Path to an intent JSON")
@click.option("--policy", "policy_path", type=click.Path(exists=True, dir_okay=False), required=False, help="Path to a policy JSON (ICOP)")
@click.pass_context
def run_intent_cmd(ctx, intent_path, policy_path):
    """Run a single intent end-to-end through policy -> router -> stub operator -> receipt."""
    from .engine.runtime import Runtime
    from pathlib import Path
    import json
    spec_root = resolve_root(ctx.obj["spec_root"])
    runtime = Runtime(spec_root, Path(policy_path) if policy_path else None)
    intent = json.loads(Path(intent_path).read_text())
    receipt = runtime.run_intent(intent)
    print(receipt.model_dump_json(indent=2, by_alias=True))





@cli.command("run-intent-save")
@click.option("--intent", "intent_path", type=click.Path(exists=True, dir_okay=False), required=True, help="Path to an intent JSON")
@click.option("--policy", "policy_path", type=click.Path(exists=True, dir_okay=False), required=False, help="Path to a policy JSON (ICOP)")
@click.option("--save-receipt", "save_path", type=click.Path(dir_okay=False), required=True, help="Path to save the receipt JSON")
@click.pass_context
def run_intent_save_cmd(ctx, intent_path, policy_path, save_path):
    """Run intent and save the receipt to a file."""
    from .engine.runtime import Runtime
    from pathlib import Path
    import json
    spec_root = resolve_root(ctx.obj["spec_root"])
    runtime = Runtime(spec_root, Path(policy_path) if policy_path else None)
    intent = json.loads(Path(intent_path).read_text())
    receipt = runtime.run_intent(intent)
    Path(save_path).write_text(receipt.model_dump_json(indent=2, by_alias=True))
    print(f"[green]Saved[/green] receipt to {save_path}")

@cli.command("sign-receipt")
@click.option("--receipt", "receipt_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--secret", type=str, required=False, help="HMAC secret (or set HYPERSYNC_HMAC_SECRET)")
@click.pass_context
def sign_receipt_cmd(ctx, receipt_path, secret):
    import json, os
    from .receipts.codec import sign_receipt
    from .core.models import Receipt
    secret = secret or os.getenv("HYPERSYNC_HMAC_SECRET")
    if not secret:
        raise click.UsageError("Provide --secret or set HYPERSYNC_HMAC_SECRET")
    obj = json.loads(Path(receipt_path).read_text())
    rcpt = Receipt.model_validate(obj)
    rcpt = sign_receipt(rcpt, secret)
    Path(receipt_path).write_text(rcpt.model_dump_json(indent=2, by_alias=True))
    print(f"[green]Signed[/green] {receipt_path}")

@cli.command("verify-receipt")
@click.option("--receipt", "receipt_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--secret", type=str, required=False, help="HMAC secret (or set HYPERSYNC_HMAC_SECRET)")
@click.pass_context
def verify_receipt_cmd(ctx, receipt_path, secret):
    import json, os
    from .receipts.codec import verify_receipt
    from .core.models import Receipt
    secret = secret or os.getenv("HYPERSYNC_HMAC_SECRET")
    if not secret:
        raise click.UsageError("Provide --secret or set HYPERSYNC_HMAC_SECRET")
    obj = json.loads(Path(receipt_path).read_text())
    rcpt = Receipt.model_validate(obj)
    ok, err = verify_receipt(rcpt, secret)
    if ok:
        print("[green]OK[/green] receipt signature valid")
    else:
        print(f"[red]FAIL[/red] {err}")

@cli.command("run-batch")
@click.option("--intents", "intents_path", type=click.Path(exists=True, dir_okay=False), required=True, help="Path to JSONL intents file")
@click.option("--policy", "policy_path", type=click.Path(exists=True, dir_okay=False), required=False)
@click.option("--out", "out_path", type=click.Path(dir_okay=False), required=True, help="Path to write receipts JSONL")
@click.pass_context
def run_batch_cmd(ctx, intents_path, policy_path, out_path):
    from .engine.runtime import Runtime
    import json
    spec_root = resolve_root(ctx.obj["spec_root"])
    runtime = Runtime(spec_root, Path(policy_path) if policy_path else None)
    with open(intents_path, 'r', encoding='utf-8') as inf, open(out_path, 'w', encoding='utf-8') as outf:
        for line in inf:
            if not line.strip():
                continue
            intent = json.loads(line)
            rcpt = runtime.run_intent(intent)
            outf.write(rcpt.model_dump_json() + '\n')
    print(f"[green]Wrote[/green] receipts to {out_path}")

def main():
    cli(obj={})


@cli.command('plan-intent')
@click.option('--intent', 'intent_path', type=click.Path(exists=True, dir_okay=False), required=True)
@click.pass_context
def plan_intent_cmd(ctx, intent_path):
    from .engine.runtime import Runtime
    import json
    spec_root = resolve_root(ctx.obj['spec_root'])
    rt = Runtime(spec_root)
    intent = json.loads(Path(intent_path).read_text())
    op = rt.router.resolve(intent.get('op'))
    why = 'router'
    if not op:
        op, why = rt.planner.plan(intent)
    print({'operator': op, 'why': why})


@cli.command('replay-artifact')
@click.option('--manifest', 'manifest_path', type=click.Path(exists=True, dir_okay=False), required=True)
@click.option('--policy', 'policy_path', type=click.Path(exists=True, dir_okay=False), required=False)
@click.pass_context
def replay_artifact_cmd(ctx, manifest_path, policy_path):
    import json
    spec_root = resolve_root(ctx.obj['spec_root'])
    man = json.loads(Path(manifest_path).read_text())
    intent = json.loads(Path(man.get('intent_path')).read_text())
    from .engine.runtime import Runtime
    rt = Runtime(spec_root, Path(policy_path) if policy_path else None)
    rcpt = rt.run_intent(intent)
    print(rcpt.model_dump_json(indent=2, by_alias=True))


@cli.command("retrieval-hybrid")
@click.option('--config', 'config_path', type=click.Path(exists=True, dir_okay=False), required=True)
@click.option('--data', 'data_path', type=click.Path(exists=True, dir_okay=False), required=True, help='JSON file with query+items')
@click.option('--index-commitment', type=str, required=True)
@click.option('--query-commitment', type=str, required=True)
@click.option('--codebook-commitment', type=str, required=False)
@click.option('--out', 'out_path', type=click.Path(dir_okay=False), required=False)
@click.option('--seed', type=int, required=False)
@click.pass_context
def retrieval_hybrid_cmd(ctx, config_path, data_path, index_commitment, query_commitment, codebook_commitment, out_path, seed):
    import json
    from datetime import datetime, timezone
    spec_root = resolve_root(ctx.obj['spec_root'])
    from .retrieval import (
        HybridRetrievalConfig,
        HybridRetrievalEngine,
        RetrievalItem,
        build_exactness_receipt,
        sign_exactness_receipt,
    )
    cfg_path = Path(config_path)
    if not cfg_path.is_absolute():
        cfg_path = spec_root / cfg_path
    data_path = Path(data_path)
    if not data_path.is_absolute():
        data_path = spec_root / data_path
    config = HybridRetrievalConfig.from_file(cfg_path)
    payload = json.loads(data_path.read_text())
    query_vec = payload.get('query')
    if query_vec is None:
        raise click.UsageError('Dataset must include "query" vector')
    items_payload = payload.get('items') or []
    if not items_payload:
        raise click.UsageError('Dataset must include at least one item in "items"')
    items = [
        RetrievalItem(
            id=str(entry['id']),
            vector=entry['vector'],
            metadata={k: v for k, v in entry.items() if k not in {'id', 'vector'}}
        )
        for entry in items_payload
    ]
    engine = HybridRetrievalEngine(config)
    run = engine.run(query=query_vec, items=items, seed=seed)
    result = {
        'results': [
            {'id': res.id, 'distance': res.distance, 'rank': res.rank, 'metadata': res.metadata}
            for res in run.results
        ],
        'candidate_count': run.candidate_count,
        'diagnostics': run.diagnostics,
    }
    if config.receipts.wants_exactness_receipt():
        receipt = build_exactness_receipt(
            config,
            run,
            query_commitment=query_commitment,
            index_commitment=index_commitment,
            codebook_commitment=codebook_commitment,
            timestamp=datetime.now(timezone.utc),
        )
        sign_exactness_receipt(receipt)
        result['exactness_receipt'] = receipt.model_dump(mode='json', by_alias=True, exclude_none=True)
    if out_path:
        Path(out_path).write_text(json.dumps(result, indent=2))
        print(f"[green]Wrote[/green] retrieval output to {out_path}")
    else:
        print(json.dumps(result, indent=2))


@cli.group()
@click.pass_context
def tiers(ctx):
    """Inspect service tier specifications."""
    pass

@tiers.command('summary')
@click.pass_context
def tiers_summary(ctx):
    registry = ServiceTierRegistry(ctx.obj['spec_root'])
    table = Table(title='HyperSync Service Tiers')
    table.add_column('Tier')
    table.add_column('Max Dim')
    table.add_column('Node Limit')
    table.add_column('DB Adapters')
    table.add_column('Orchestrators')
    for name in registry.tiers():
        profile = registry.get(name)
        table.add_row(
            profile.tier,
            str(profile.max_dim or '-'),
            str(profile.node_limit or '-'),
            ', '.join(profile.db_adapters) or '-',
            ', '.join(profile.orchestrators) or '-',
        )
    print(table)

@tiers.command('show')
@click.argument('tier')
@click.option('--compact', is_flag=True, help='Emit a compact JSON object')
@click.pass_context
def tiers_show(ctx, tier, compact):
    registry = ServiceTierRegistry(ctx.obj['spec_root'])
    payload = registry.as_dict(tier)
    if compact:
        print(json.dumps(payload, separators=(',', ':')))
    else:
        print(json.dumps(payload, indent=2))


@tiers.command('export')
@click.option('--out', 'out_path', type=click.Path(dir_okay=False, path_type=Path), required=True, help='Destination file for tier profiles')
@click.option('--format', 'fmt', type=click.Choice(['json', 'yaml']), default='json', show_default=True)
@click.pass_context
def tiers_export(ctx, out_path: Path, fmt: str):
    registry = ServiceTierRegistry(ctx.obj['spec_root'])
    payload = {profile.tier: profile.model_dump_with_source() for profile in registry}
    if fmt == 'json':
        out_path.write_text(json.dumps(payload, indent=2))
    else:
        import yaml
        out_path.write_text(yaml.safe_dump(payload, sort_keys=False))
    print(f'[green]Wrote[/green] {len(payload)} tier profiles to {out_path} as {fmt}')

@cli.command('run-program')
@click.option('--task', required=True, help='Task tag for hyperbolic routing')
@click.option('--payload', required=False, default='{}', help='JSON dict payload for message content')
@click.option('--steps', type=int, default=4, help='Max routing steps')
@click.pass_context
def run_program_cmd(ctx, task, payload, steps):
    import json
    from .engine.program import ProgramEngine
    spec_root = resolve_root(ctx.obj['spec_root'])
    pe = ProgramEngine(spec_root)
    py = json.loads(payload) if isinstance(payload, str) else payload
    out = pe.run(task=task, payload=py, max_steps=steps)
    print(out)
