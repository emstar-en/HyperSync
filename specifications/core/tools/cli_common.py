import argparse, json, os

def _has_option(ap: argparse.ArgumentParser, opt: str) -> bool:
    try:
        for act in getattr(ap, '_actions', []) or []:
            if opt in getattr(act, 'option_strings', []) or opt == getattr(act, 'dest', None):
                return True
    except Exception:
        pass
    return False

def add_common_args(ap: argparse.ArgumentParser):
    opts = [
        ('--domain-id', {}),
        ('--frame-id', {}),
        ('--input', {"dest": "input", "short": "-i"}),
        ('--output', {"dest": "output", "short": "-o"}),
        ('--issue', {"action": "store_true"}),
        ('--validate', {"action": "store_true"}),
        ('--op-json', {"dest": "op_json"}),
    ]
    for opt, cfg in opts:
        dest = cfg.get('dest') or opt.lstrip('-').replace('-', '_')
        if _has_option(ap, opt) or _has_option(ap, dest):
            continue
        short = cfg.get('short')
        args = [opt] if not short else [short, opt]
        kwargs = {k:v for k,v in cfg.items() if k not in ('dest','short')}
        if dest:
            kwargs['dest'] = dest
        try:
            ap.add_argument(*args, **kwargs)
        except Exception:
            # Ignore duplicate or parser-specific errors
            pass
    return ap

def load_envelope_op(args):
    """
    Attempts to load an EnvelopeRouteOp JSON payload from --op-json.
    Returns a dict if present and valid JSON; otherwise None.
    """
    op_path = getattr(args, 'op_json', None)
    if not op_path:
        return None
    if not os.path.exists(op_path):
        return None
    try:
        with open(op_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


# ============================================================================
# DOMAIN CLI INTEGRATION - Added by Pass 3
# ============================================================================

def register_domain_commands(subparsers):
    """Register domain management commands"""
    domain_parser = subparsers.add_parser('domain', help='Domain management')
    domain_subparsers = domain_parser.add_subparsers(dest='domain_command')

    # List domains
    list_parser = domain_subparsers.add_parser('list', help='List domains')
    list_parser.add_argument('--type', help='Filter by type')
    list_parser.add_argument('--curvature', help='Filter by curvature')

    # Inspect domain
    inspect_parser = domain_subparsers.add_parser('inspect', help='Inspect domain')
    inspect_parser.add_argument('domain_id', help='Domain ID')

    # Create domain
    create_parser = domain_subparsers.add_parser('create', help='Create domain')
    create_parser.add_argument('type', help='Domain type')
    create_parser.add_argument('--params', help='Parameters (JSON)')

    return domain_parser


def execute_domain_command(args):
    """Execute a domain management command"""
    from codegen.templates.runtime.hypersync.routing.domain_cli import DomainCLI

    cli = DomainCLI()

    if args.domain_command == 'list':
        return cli.cmd_list(args)
    elif args.domain_command == 'inspect':
        return cli.cmd_inspect(args)
    elif args.domain_command == 'create':
        return cli.cmd_create(args)
    else:
        print(f"Unknown domain command: {args.domain_command}")
        return 1

