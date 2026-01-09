
from __future__ import annotations

import argparse
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hypersync.nvm import (
    BlockDescriptor,
    BlockWriteReceipt,
    build_block_write_receipt,
    load_block_descriptor,
    sign_block_write_receipt,
    verify_block_write_receipt,
)
from hypersync.spec_loader import SpecLoader


ISO_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
)


def _resolve_path(value: str, base: Optional[Path] = None) -> Path:
    candidate = Path(value)
    if candidate.exists():
        return candidate
    if base is not None:
        candidate = (base / value).resolve()
        if candidate.exists():
            return candidate
    return Path(value)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ISO_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported timestamp format: {value}")


def _load_descriptor(path: Path) -> BlockDescriptor:
    return load_block_descriptor(path)


def _emit_summary(receipt: BlockWriteReceipt) -> str:
    return json.dumps(
        {
            "ok": True,
            "block_id": receipt.block_id,
            "receipt_kind": receipt.receipt_kind,
            "hash": receipt.hash,
            "signature": receipt.signature,
        }
    )


def cmd_list(args: argparse.Namespace) -> int:
    try:
        loader = SpecLoader(args.spec_root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    examples = loader.find_examples("artifacts", "nvm", "examples", pattern="*.json")
    if not examples:
        print("No NVM examples found", file=sys.stderr)
        return 1
    for path in examples:
        print(path)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    spec_base = Path(args.spec_root).expanduser().resolve() if args.spec_root else None
    descriptor_path = _resolve_path(args.block, spec_base)
    try:
        descriptor = _load_descriptor(descriptor_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "block_id": descriptor.block_id,
                "class": descriptor.class_,
                "payload_commitment": descriptor.compute_payload_commitment(),
            }
        )
    )
    return 0


def cmd_commit(args: argparse.Namespace) -> int:
    spec_base = Path(args.spec_root).expanduser().resolve() if args.spec_root else None
    descriptor_path = _resolve_path(args.block, spec_base)
    descriptor = _load_descriptor(descriptor_path)
    ts = _parse_timestamp(args.timestamp)
    receipt = build_block_write_receipt(
        descriptor,
        writer=args.writer,
        profile=args.profile,
        input_commitments=args.inputs,
        policy_hits=args.policy_hit,
        timestamp=ts,
    )
    if args.sign_key:
        sign_block_write_receipt(receipt, args.sign_key)
    elif args.use_env_secret:
        secret = os.environ.get("HYPERSYNC_HMAC_SECRET")
        if secret:
            sign_block_write_receipt(receipt, secret)
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(args.output_dir or descriptor_path.parent)
        stamp = (ts or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
        output_path = output_dir / f"{descriptor.block_id.replace('://', '_').replace('/', '_')}.{stamp}.receipt.json"
    _ensure_parent(output_path)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(receipt.model_dump(mode="json", by_alias=True, exclude_none=True), handle, indent=2)
    print(_emit_summary(receipt))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HyperSync NVM CLI")
    parser.add_argument("--spec-root", help="Path to extracted spec pack", default=None)
    parser.add_argument(
        "--use-env-secret",
        action="store_true",
        help="Sign receipts using HYPERSYNC_HMAC_SECRET if available",
    )
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="List available NVM block descriptors from spec pack")
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser("validate", help="Validate a block descriptor JSON")
    p_validate.add_argument("--block", required=True, help="Path to descriptor JSON")
    p_validate.set_defaults(func=cmd_validate)

    p_commit = sub.add_parser("commit", help="Emit a BlockWriteReceipt for a descriptor")
    p_commit.add_argument("--block", required=True, help="Path to descriptor JSON")
    p_commit.add_argument("--writer", required=True, help="Writer identifier (entity://)")
    p_commit.add_argument("--profile", default="ADVANCED", help="Profile label")
    p_commit.add_argument("--inputs", nargs="*", default=None, help="Input commitments")
    p_commit.add_argument(
        "--policy-hit",
        action="append",
        default=None,
        help="Specify policy hits (can repeat)",
    )
    p_commit.add_argument("--timestamp", help="ISO timestamp for the receipt")
    p_commit.add_argument("--output", help="Write receipt JSON to this path")
    p_commit.add_argument("--output-dir", help="Directory for receipts when --output is omitted")
    p_commit.add_argument("--sign-key", help="Secret key for signing")
    p_commit.set_defaults(func=cmd_commit)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
