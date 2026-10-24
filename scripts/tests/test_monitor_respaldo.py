"""Pruebas del monitor de respaldo: unitarias + integracion con un repo git temporal."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import monitor_respaldo as mon  # noqa: E402


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path: Path):
    root = tmp_path / "proj"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@t.t")
    _git(root, "config", "user.name", "t")
    (root / ".gitignore").write_text("*.db\n.env\n", encoding="utf-8")
    (root / "codigo.py").write_text("print(1)\n", encoding="utf-8")
    (root / "datos.db").write_bytes(b"v1")
    (root / ".env").write_text("K=1\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "init")
    return root, tmp_path / "manifest.json"


def test_self_test_passes():
    assert mon.run_self_test() == mon.EXIT_OK


def test_baseline_lists_only_ignored_data(repo):
    root, manifest = repo
    assert mon.cmd_baseline(root, manifest, force=False) == mon.EXIT_OK
    assert sorted(mon.load_manifest(manifest)) == [".env", "datos.db"]


def test_baseline_refuses_overwrite_without_force(repo):
    root, manifest = repo
    mon.cmd_baseline(root, manifest, force=False)
    with pytest.raises(mon.MonitorError):
        mon.cmd_baseline(root, manifest, force=False)
    assert mon.cmd_baseline(root, manifest, force=True) == mon.EXIT_OK


def test_check_clean_then_detects_modify_add_delete(repo):
    root, manifest = repo
    mon.cmd_baseline(root, manifest, force=False)
    assert mon.cmd_check(root, manifest) == mon.EXIT_OK
    (root / "datos.db").write_bytes(b"v2-distinto")   # modificado (otro tamano)
    (root / "nuevo.db").write_bytes(b"x")              # agregado
    (root / ".env").unlink()                           # eliminado
    changes, _, _ = mon.evaluate(root, manifest)
    assert changes.modified == ["datos.db"] and changes.added == ["nuevo.db"] and changes.deleted == [".env"]
    assert mon.cmd_check(root, manifest) == mon.EXIT_CHANGES


def test_same_size_content_change_is_detected(repo):
    root, manifest = repo
    mon.cmd_baseline(root, manifest, force=False)
    (root / "datos.db").write_bytes(b"v9")  # mismo tamano (2 bytes), distinto contenido
    changes, _, _ = mon.evaluate(root, manifest, cache={})  # sin cache: rehash completo
    assert changes.modified == ["datos.db"]


def test_code_changes_reported(repo):
    root, manifest = repo
    mon.cmd_baseline(root, manifest, force=False)
    (root / "codigo.py").write_text("print(2)\n", encoding="utf-8")
    status = mon.code_status(root)
    assert status.dirty_files == ("codigo.py",) and status.unpushed_commits is None
    assert mon.cmd_check(root, manifest) == mon.EXIT_CHANGES


def test_missing_baseline_is_error_exit_2(repo):
    root, manifest = repo
    assert mon.main(["--root", str(root), "--manifest", str(manifest), "--log", str(root.parent / "l.log"), "--check"]) == mon.EXIT_ERROR


def test_not_a_git_repo_is_error(tmp_path):
    with pytest.raises(mon.MonitorError):
        mon.list_data_files(tmp_path)


def test_watch_rejects_tiny_interval(repo):
    root, manifest = repo
    mon.cmd_baseline(root, manifest, force=False)
    assert mon.main(["--root", str(root), "--manifest", str(manifest), "--log", str(root.parent / "l.log"), "--watch", "1"]) == mon.EXIT_ERROR
