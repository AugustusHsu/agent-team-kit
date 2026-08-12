"""migrate_dates.py 的預覽模式行為（預設不改檔案）。"""

from pathlib import Path

from conftest import run_script


def test_預設為預覽模式且不修改任何檔案(project: Path):
    ticket = project / "docs/features/example_module/tasks/ABC-DEV-BE-001.md"
    before = ticket.read_bytes()

    result = run_script(project, "migrate_dates.py")

    assert result.returncode == 0, result.stderr
    assert "預覽模式" in result.stdout
    assert ticket.read_bytes() == before


def test_可篩選單一模組(project: Path):
    result = run_script(project, "migrate_dates.py", "--project", "another_module")
    assert result.returncode == 0, result.stderr
    assert "example_module" not in result.stdout


def test_找不到_docs_features_時給出明確錯誤(tmp_path: Path):
    """`find_project_root()` 就是靠 `docs/features/` 定位專案根目錄。"""
    import shutil
    import subprocess

    from conftest import INSTALL_SH

    target = tmp_path / "nodocs"
    target.mkdir()
    subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)
    shutil.rmtree(target / "docs" / "features")

    result = run_script(target, "migrate_dates.py")
    assert result.returncode == 1
    assert "無法定位專案根目錄" in result.stderr
