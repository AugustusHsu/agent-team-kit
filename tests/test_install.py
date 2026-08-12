"""install.sh 的行為：1:1 複製、不覆寫既有檔案、--force 可強制覆寫。"""

import subprocess
from pathlib import Path

from conftest import INSTALL_SH, KIT_ROOT


def _是本機產生物(rel: str) -> bool:
    """與 install.sh 的排除規則一致：kit/ 是工作區，跑過測試會留下 __pycache__。"""
    return (
        "__pycache__/" in rel
        or ".pytest_cache/" in rel
        or rel.endswith((".pyc", ".pyo", ".pyd", ".DS_Store"))
    )


def kit_relative_files():
    return sorted(
        rel
        for rel in (p.relative_to(KIT_ROOT).as_posix() for p in KIT_ROOT.rglob("*") if p.is_file())
        if not _是本機產生物(rel)
    )


def test_安裝後檔案與_kit_完全一致(bare_install: Path):
    """安裝 = 原封不動複製，不做任何改名。"""
    installed = sorted(
        p.relative_to(bare_install).as_posix() for p in bare_install.rglob("*") if p.is_file()
    )
    assert installed == kit_relative_files()


def test_安裝後內容逐位元組相同(bare_install: Path):
    for rel in kit_relative_files():
        assert (bare_install / rel).read_bytes() == (KIT_ROOT / rel).read_bytes(), rel


def test_腳本具備執行權限(bare_install: Path):
    scripts = sorted((bare_install / ".agent" / "scripts").glob("*.py"))
    assert scripts, "安裝結果中找不到任何腳本"
    for s in scripts:
        assert s.stat().st_mode & 0o111, f"{s.name} 沒有執行權限"


def test_重複安裝不覆寫既有檔案(tmp_path: Path):
    """使用者改過的檔案不能被第二次安裝洗掉。"""
    target = tmp_path / "proj"
    target.mkdir()
    subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)

    touched = target / "docs" / "standards" / "security_audit.md"
    touched.write_text("使用者自己改過的內容\n", encoding="utf-8")

    result = subprocess.run(
        [str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True
    )
    assert touched.read_text(encoding="utf-8") == "使用者自己改過的內容\n"
    assert "略過既有檔案" in result.stdout


def test_force_強制覆寫(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)

    touched = target / "docs" / "standards" / "security_audit.md"
    touched.write_text("會被蓋掉\n", encoding="utf-8")

    subprocess.run(
        [str(INSTALL_SH), str(target), "--force"], check=True, capture_output=True, text=True
    )
    assert touched.read_bytes() == (KIT_ROOT / "docs" / "standards" / "security_audit.md").read_bytes()


def test_目標目錄不存在時拒絕安裝(tmp_path: Path):
    """打錯路徑時應該直接報錯，而不是默默建出一個空專案。"""
    target = tmp_path / "typo"
    result = subprocess.run([str(INSTALL_SH), str(target)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "目標目錄不存在" in result.stderr
    assert not target.exists()


def test_不複製本機產生物(tmp_path: Path):
    """kit/ 是工作區，跑過 pytest 就會留下 __pycache__——那不該跟著裝進使用者專案。"""
    junk_dir = KIT_ROOT / ".agent" / "scripts" / "__pycache__"
    junk_file = junk_dir / "_installtest.cpython-999.pyc"
    created_dir = not junk_dir.exists()
    junk_dir.mkdir(parents=True, exist_ok=True)
    junk_file.write_bytes(b"\x00fake bytecode")
    try:
        target = tmp_path / "proj"
        target.mkdir()
        subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)

        assert not (target / ".agent" / "scripts" / "__pycache__").exists()
        assert not list(target.rglob("*.pyc"))
        # 排除產生物不能連正常檔案一起漏掉
        assert (target / ".agent" / "scripts" / "scan_backlog.py").is_file()
    finally:
        junk_file.unlink(missing_ok=True)
        if created_dir and junk_dir.exists() and not any(junk_dir.iterdir()):
            junk_dir.rmdir()


def test_未給參數時列出用法():
    result = subprocess.run([str(INSTALL_SH)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "用法" in result.stderr
