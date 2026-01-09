"""
CLI commands for environment path inspection
"""

import sys
import json
import argparse
from typing import Optional

# Mock imports for standalone execution
try:
    from hypersync.environment.fs_adapters import FileSystemAdapter
    from hypersync.environment.sandbox_manager import SandboxManager
except ImportError:
    print("Warning: HyperSync modules not found, using mock implementations")
    FileSystemAdapter = None
    SandboxManager = None


def cmd_path_info(args):
    """Show information about a path"""
    if not FileSystemAdapter:
        print("Error: FileSystemAdapter not available")
        return 1

    fs = FileSystemAdapter.for_host()

    try:
        if not fs.exists(args.path):
            print(f"Error: Path does not exist: {args.path}")
            return 1

        info = fs.get_info(args.path)

        if args.json:
            print(json.dumps(info.to_dict(), indent=2))
        else:
            print(f"Path: {info.path}")
            print(f"Name: {info.name}")
            print(f"Type: {'Directory' if info.is_dir else 'File'}")
            print(f"Size: {info.size:,} bytes")
            print(f"Permissions: {info.permissions}")
            print(f"Owner: {info.owner}")
            print(f"Group: {info.group}")
            print(f"Modified: {info.modified_at}")
            print(f"Created: {info.created_at}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_path_check(args):
    """Check if agent can access a path"""
    if not SandboxManager:
        print("Error: SandboxManager not available")
        return 1

    manager = SandboxManager()
    sandbox = manager.get_agent_sandbox(args.agent_id)

    if not sandbox:
        print(f"Error: No active sandbox for agent {args.agent_id}")
        return 1

    can_access = sandbox.check_access(args.path, args.operation, args.clearance)

    if args.json:
        result = {
            "agent_id": args.agent_id,
            "path": args.path,
            "operation": args.operation,
            "clearance": args.clearance,
            "allowed": can_access
        }
        print(json.dumps(result, indent=2))
    else:
        status = "ALLOWED" if can_access else "DENIED"
        print(f"Access check: {status}")
        print(f"  Agent: {args.agent_id}")
        print(f"  Path: {args.path}")
        print(f"  Operation: {args.operation}")
        print(f"  Clearance: {args.clearance}")

    return 0 if can_access else 1


def cmd_path_list(args):
    """List paths accessible by an agent"""
    if not SandboxManager:
        print("Error: SandboxManager not available")
        return 1

    manager = SandboxManager()
    sandbox = manager.get_agent_sandbox(args.agent_id)

    if not sandbox:
        print(f"Error: No active sandbox for agent {args.agent_id}")
        return 1

    policy = sandbox.policy

    if args.json:
        result = {
            "agent_id": args.agent_id,
            "sandbox_id": sandbox.sandbox_id,
            "allowed_paths": [
                {
                    "path": p.path,
                    "permissions": list(p.permissions),
                    "recursive": p.recursive,
                    "clearance_required": p.clearance_required
                }
                for p in policy.allowed_paths
            ],
            "denied_paths": policy.denied_paths,
            "default_dirs": policy.default_dirs
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Agent: {args.agent_id}")
        print(f"Sandbox: {sandbox.sandbox_id}")
        print(f"\nAllowed paths:")
        for p in policy.allowed_paths:
            perms = ", ".join(p.permissions)
            recursive = " (recursive)" if p.recursive else ""
            print(f"  {p.path} [{perms}]{recursive}")
            print(f"    Clearance required: {p.clearance_required}")

        if policy.denied_paths:
            print(f"\nDenied paths:")
            for p in policy.denied_paths:
                print(f"  {p}")

        if policy.default_dirs:
            print(f"\nDefault directories:")
            for d in policy.default_dirs:
                print(f"  {d}")

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="HyperSync environment path management"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # path info command
    info_parser = subparsers.add_parser('info', help='Show path information')
    info_parser.add_argument('path', help='Path to inspect')
    info_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # path check command
    check_parser = subparsers.add_parser('check', help='Check agent path access')
    check_parser.add_argument('agent_id', help='Agent ID')
    check_parser.add_argument('path', help='Path to check')
    check_parser.add_argument('--operation', default='read', 
                             choices=['read', 'write', 'execute', 'list', 'delete'],
                             help='Operation to check')
    check_parser.add_argument('--clearance', default='internal',
                             choices=['public', 'internal', 'confidential', 'restricted', 'critical'],
                             help='Agent clearance level')
    check_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # path list command
    list_parser = subparsers.add_parser('list', help='List agent accessible paths')
    list_parser.add_argument('agent_id', help='Agent ID')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Dispatch to command handler
    if args.command == 'info':
        return cmd_path_info(args)
    elif args.command == 'check':
        return cmd_path_check(args)
    elif args.command == 'list':
        return cmd_path_list(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
