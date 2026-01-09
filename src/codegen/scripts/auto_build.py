
#!/usr/bin/env python3
"""One-shot automation: render, (optionally) test, and package the HyperSync runtime."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RENDER_SCRIPT = ROOT / "codegen" / "scripts" / "render_runtime.py"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print(f"[auto-build] $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")


def render(out_dir: Path) -> Path:
    from importlib import util

    spec = util.spec_from_file_location("render_runtime", RENDER_SCRIPT)
    if not spec or not spec.loader:
        raise RuntimeError("Cannot load render_runtime script")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render(out_dir)


def package_runtime(source_dir: Path, out_dir: Path, *, formats: list[str]) -> list[Path]:
    artifacts: list[Path] = []
    out_dir.mkdir(parents=True, exist_ok=True)

    if "zip" in formats:
        zip_path = out_dir / "hypersync-runtime.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(source_dir.rglob("*")):
                if file.is_file():
                    zf.write(file, file.relative_to(source_dir))
        artifacts.append(zip_path)

    if "tar" in formats:
        tar_path = out_dir / "hypersync-runtime.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tf:
            for file in sorted(source_dir.rglob("*")):
                tf.add(file, arcname=file.relative_to(source_dir))
        artifacts.append(tar_path)

    if "wheel" in formats or "sdist" in formats:
        # ensure build module exists
        run([sys.executable, "-m", "pip", "install", "build>=1.0"], cwd=source_dir)
        build_cmd = [sys.executable, "-m", "build"]
        if "sdist" not in formats:
            build_cmd.append("--wheel")
        if "wheel" not in formats:
            build_cmd.append("--sdist")
        run(build_cmd, cwd=source_dir)
        dist_dir = source_dir / "dist"
        for artifact in dist_dir.glob("*"):
            shutil.copy2(artifact, out_dir / artifact.name)
            artifacts.append(out_dir / artifact.name)

    return artifacts


def write_manifest(meta_path: Path, *, render_dir: Path, artifacts: list[Path], tested: bool, test_log: list[str]) -> None:
    meta = {
        "rendered_at": render_dir.as_posix(),
        "artifacts": [path.name for path in artifacts],
        "tests_ran": tested,
        "test_log": test_log,
    }
    meta_path.write_text(json.dumps(meta, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Full automation: render, test, package HyperSync runtime")
    parser.add_argument("--workspace", type=Path, default=Path("build/runtime"), help="Directory to render the runtime into")
    parser.add_argument("--artifact-dir", type=Path, default=Path("build/artifacts"), help="Directory to write packaged outputs")
    parser.add_argument("--formats", nargs="*", default=["zip"], choices=["zip", "tar", "wheel", "sdist"], help="Package formats to produce")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running pytest after rendering")
    parser.add_argument("--pytest-args", nargs=argparse.REMAINDER, help="Additional arguments passed to pytest")
    args = parser.parse_args(argv)

    workspace = args.workspace.resolve()
    artifact_dir = args.artifact_dir.resolve()

    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)

    print(f"[auto-build] Rendering runtime into {workspace}")
    render_dir = render(workspace)

    test_log: list[str] = []
    if not args.skip_tests:
        pytest_cmd = [sys.executable, "-m", "pytest"]
        if args.pytest_args:
            pytest_cmd.extend(args.pytest_args)
        try:
            run(pytest_cmd, cwd=render_dir)
            test_log.append("pytest: success")
        except RuntimeError as exc:
            test_log.append(f"pytest: FAILED ({exc})")
            raise

    print(f"[auto-build] Packaging formats: {args.formats}")
    artifacts = package_runtime(render_dir, artifact_dir, formats=args.formats)

    meta_path = artifact_dir / "codegen-summary.json"
    write_manifest(meta_path, render_dir=render_dir, artifacts=artifacts, tested=not args.skip_tests, test_log=test_log)

    print(f"[auto-build] Generated {len(artifacts)} artifact(s) -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
