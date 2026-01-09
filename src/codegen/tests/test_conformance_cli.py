import pytest

from hypersync.conformance.cli import main as conformance_main


@pytest.mark.usefixtures("no_spec_env")
def test_conformance_cli_smoke(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    conformance_main(["smoke", "--limit", "1"])
    out = capsys.readouterr().out
    assert "Conformance" in out or out == ""


@pytest.fixture
def no_spec_env(monkeypatch):
    monkeypatch.delenv("HYPERSYNC_SPEC_ROOT", raising=False)
