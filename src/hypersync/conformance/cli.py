from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from hypersync.utils.fs import resolve_root

from .runner import ConformanceRunner


DEFAULT_MODE = "smoke"


def _default_vectors(spec_root: Path) -> Path:
    return spec_root / "conformance" / "vectors"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run HyperSync conformance routines")
    parser.add_argument("mode", nargs="?", default=DEFAULT_MODE, choices=["smoke"], help="Which runner mode to execute")
    parser.add_argument("--spec-root", dest="spec_root", help="Explicit spec root to use")
    parser.add_argument("--vectors", dest="vectors", help="Override path to conformance vectors")
    parser.add_argument("--limit", dest="limit", type=int, default=20, help="Limit for smoke listing")

    args = parser.parse_args(argv)

    spec_root = Path(args.spec_root).expanduser() if args.spec_root else resolve_root(None)
    vectors_dir = Path(args.vectors).expanduser() if args.vectors else _default_vectors(spec_root)

    runner = ConformanceRunner(vectors_dir)

    if args.mode == "smoke":
        runner.smoke(limit=args.limit)
    else:
        raise SystemExit(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()
