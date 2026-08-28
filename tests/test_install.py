"""install.sh 的行為：1:1 複製、不覆寫既有檔案、--force 可強制覆寫、--upgrade 安全升級。"""

import hashlib
import subprocess
from pathlib import Path

from conftest import INSTALL_SH, KIT_ROOT

MANIFEST_REL = ".agent/.kit-manifest"


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _讀基準線(target: Path) -> dict[str, str]:
    entries = {}
    for line in (target / MANIFEST_REL).read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        entries[rel] = digest
    return entries


def _安裝(target: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(INSTALL_SH), str(target), *args], check=True, capture_output=True, text=True
    )


def test_安裝後檔案與_kit_完全一致(bare_install: Path):
    """安裝 = 原封不動複製，不做任何改名；額外只多一份升級用的基準線。"""
    installed = sorted(
        p.relative_to(bare_install).as_posix() for p in bare_install.rglob("*") if p.is_file()
    )
    assert installed == sorted([*kit_relative_files(), MANIFEST_REL])


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


# ── 升級模式（--upgrade）─────────────────────────────────────────────
#
# 升級的難處在於：安裝後使用者一定會改東西（模組前綴表、自訂規範），
# 但套件的流程規範又必須能推進去。靠 .kit-manifest 記下「裝進去時長什麼樣」，
# 才能把「使用者改過的」與「還是原版的」分開處理。


def test_安裝後產生基準線且涵蓋所有檔案(bare_install: Path):
    entries = _讀基準線(bare_install)
    assert set(entries) == set(kit_relative_files())
    for rel, digest in entries.items():
        assert digest == _sha256(KIT_ROOT / rel), rel


def _裝成舊版(target: Path, rel: str, 舊內容: str) -> None:
    """偽造「上一版 kit 裝進來的就是這個內容，使用者沒動過」的狀態。"""
    (target / rel).write_text(舊內容, encoding="utf-8")
    manifest = target / MANIFEST_REL
    lines = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#") and line.split(maxsplit=1)[1:] == [rel]:
            lines.append(f"{hashlib.sha256(舊內容.encode()).hexdigest()}  {rel}")
        else:
            lines.append(line)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_升級會更新使用者沒改過的檔案(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)

    rel = "docs/standards/qa_testing_spec.md"
    _裝成舊版(target, rel, "上一版 kit 的內容\n")

    result = _安裝(target, "--upgrade")
    assert (target / rel).read_bytes() == (KIT_ROOT / rel).read_bytes()
    assert "⬆️  更新" in result.stdout
    assert not (target / f"{rel}.new").exists()


def test_升級不覆蓋使用者改過的檔案而是另存_new(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)

    rel = "docs/standards/qa_testing_spec.md"
    # 先讓 kit 版本與目標端不同（模擬套件有新版），再讓使用者也改過同一檔
    _裝成舊版(target, rel, "上一版 kit 的內容\n")
    (target / rel).write_text("我自己加的專案規範\n", encoding="utf-8")

    result = _安裝(target, "--upgrade")
    assert (target / rel).read_text(encoding="utf-8") == "我自己加的專案規範\n"
    assert (target / f"{rel}.new").read_bytes() == (KIT_ROOT / rel).read_bytes()
    assert "待合併" in result.stdout


def test_升級保留種子檔(tmp_path: Path):
    """專案入口、規劃資料與模組登記表安裝後由專案接手，升級不得動。"""
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)

    種子 = {
        "AGENTS.md": "# 我的共同專案規則\n",
        "CLAUDE.md": "# 我的專案\n",
        ".gitignore": "node_modules/\n",
        "docs/development/BACKLOG.md": "# 我的 BACKLOG\n",
        "docs/development/overlap_zones.md": "# 我的長期重疊熱區\n",
        "docs/features/README.md": "# 我的模組登記表\n",
    }
    for rel, 內容 in 種子.items():
        (target / rel).write_text(內容, encoding="utf-8")

    _安裝(target, "--upgrade")
    for rel, 內容 in 種子.items():
        assert (target / rel).read_text(encoding="utf-8") == 內容, rel
        assert not (target / f"{rel}.new").exists(), rel


def test_升級不直接補缺少的種子檔而是提示_migrate(tmp_path: Path):
    """新入口若在 upgrade 時突然出現，會在尚未拆分共同規則前改變 agent 行為。"""
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)
    missing_seeds = ("AGENTS.md", "docs/development/overlap_zones.md")
    for rel in missing_seeds:
        (target / rel).unlink()

    result = _安裝(target, "--upgrade")

    for rel in missing_seeds:
        assert not (target / rel).exists(), rel
        assert not (target / f"{rel}.new").exists(), rel
        assert f"缺少種子檔，請執行 migrate：{rel}" in result.stdout


def test_升級對沒有基準線的舊安裝採保守處理(tmp_path: Path):
    """舊版 install.sh 裝的專案沒有 manifest，無從判斷改過與否 → 一律不覆蓋。"""
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)

    rel = "docs/standards/qa_testing_spec.md"
    (target / rel).write_text("不知道是誰改的\n", encoding="utf-8")
    (target / MANIFEST_REL).unlink()

    _安裝(target, "--upgrade")
    assert (target / rel).read_text(encoding="utf-8") == "不知道是誰改的\n"
    assert (target / f"{rel}.new").read_bytes() == (KIT_ROOT / rel).read_bytes()


def test_dry_run_不寫入任何檔案(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)

    rel = "docs/standards/qa_testing_spec.md"
    _裝成舊版(target, rel, "上一版 kit 的內容\n")
    before = {p: p.read_bytes() for p in target.rglob("*") if p.is_file()}

    result = _安裝(target, "--upgrade", "--dry-run")
    after = {p: p.read_bytes() for p in target.rglob("*") if p.is_file()}
    assert before == after
    assert "dry-run" in result.stdout


def test_升級會補上新增的檔案(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    _安裝(target)

    rel = "docs/standards/qa_testing_spec.md"
    (target / rel).unlink()

    result = _安裝(target, "--upgrade")
    assert (target / rel).read_bytes() == (KIT_ROOT / rel).read_bytes()
    assert "➕ 新增" in result.stdout


def test_dry_run_不可單獨使用(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    result = subprocess.run(
        [str(INSTALL_SH), str(target), "--dry-run"], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "--dry-run 只能搭配 --upgrade" in result.stderr


def test_未知選項會報錯(tmp_path: Path):
    target = tmp_path / "proj"
    target.mkdir()
    result = subprocess.run(
        [str(INSTALL_SH), str(target), "--wat"], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "未知的選項" in result.stderr
