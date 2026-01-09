
#!/usr/bin/env python3
"""Render the HyperSync runtime skeleton from the spec pack blueprints."""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "codegen" / "templates" / "runtime"


def copy_tree(src: Path, dst: Path, *, clean: bool = True):
    if not src.exists():
        raise FileNotFoundError(f"Missing template path: {src}")
    if dst.exists() and clean:
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_file(src: Path, dst: Path):
    if not src.exists():
        raise FileNotFoundError(f"Missing template file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def render(out_dir: Path, *, clean: bool = True) -> Path:
    """Materialize the runtime template into ``out_dir`` and return the resolved path."""
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    copy_file(TEMPLATE_ROOT / "pyproject.toml", out_dir / "pyproject.toml")
    copy_file(TEMPLATE_ROOT / "README.md", out_dir / "README.md")
    copy_tree(TEMPLATE_ROOT / "hypersync", out_dir / "hypersync", clean=clean)
    copy_tree(TEMPLATE_ROOT / "tests", out_dir / "tests", clean=clean)

    print(f"Rendered HyperSync runtime to {out_dir}")
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render HyperSync runtime from spec pack templates.")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for rendered project")
    parser.add_argument("--no-clean", action="store_true", help="Do not delete existing directory contents before copying")
    args = parser.parse_args(argv)

    render(args.out, clean=not args.no_clean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
