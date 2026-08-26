"""agent runtime 的雙入口安全遷移。"""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT = ".agent/scripts/agent_runtime.py"


def _專案副本(bare_install: Path, tmp_path: Path):
    target = tmp_path / "project"
    shutil.copytree(bare_install, target)
    return target


def _執行(project: Path, *args):
    return subprocess.run(
        [sys.executable, SCRIPT, "migrate", *args],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=20,
    )


def _工作區摘要(root: Path):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_migrate_dry_run_顯示候選與差異但完全不寫檔(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    common = tmp_path / "project-rules.md"
    common.write_text("# 真實專案規則\n\n不得遺漏這一條。\n", encoding="utf-8")
    before = _工作區摘要(project)

    result = _執行(project, "--dry-run", "--common-source", str(common), "--json")

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["dry_run"] is True
    assert _工作區摘要(project) == before
    assert not list(project.glob("*.new*"))
    agents = next(item for item in output["entries"] if item["target"].endswith("AGENTS.md"))
    assert agents["changed"] is True
    assert agents["candidate"] is None
    assert "不得遺漏這一條" in agents["diff"]


def test_migrate_正式模式只寫候選且保留既有入口(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    original_agents = "# 使用者現有 AGENTS\n"
    original_claude = "# 使用者現有 CLAUDE\n\n特殊規則\n"
    (project / "AGENTS.md").write_text(original_agents, encoding="utf-8")
    (project / "CLAUDE.md").write_text(original_claude, encoding="utf-8")
    common = tmp_path / "common.md"
    common.write_text("# 新共同真相\n\n特殊規則\n", encoding="utf-8")

    result = _執行(project, "--common-source", str(common), "--json")

    assert result.returncode == 0, result.stderr
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == original_agents
    assert (project / "CLAUDE.md").read_text(encoding="utf-8") == original_claude
    assert (project / "AGENTS.md.new").read_text(encoding="utf-8") == common.read_text(
        encoding="utf-8"
    )
    adapter = (project / "CLAUDE.md.new").read_text(encoding="utf-8")
    assert adapter.startswith("# Claude Code 專案 adapter\n\n@AGENTS.md")
    assert "特殊規則" not in adapter


def test_migrate_不覆寫使用者已修改的候選(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    (project / "AGENTS.md.new").write_text("# 使用者正在編輯的候選\n", encoding="utf-8")
    common = tmp_path / "common.md"
    common.write_text("# 新共同真相\n", encoding="utf-8")

    result = _執行(project, "--common-source", str(common), "--json")

    assert result.returncode == 0, result.stderr
    assert (project / "AGENTS.md.new").read_text(encoding="utf-8") == "# 使用者正在編輯的候選\n"
    assert (project / "AGENTS.md.new.2").read_text(encoding="utf-8") == "# 新共同真相\n"


def test_migrate_舊專案只有_claude_時以它保留共同規則(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    (project / "AGENTS.md").unlink()
    legacy = "# 舊 CLAUDE 入口\n\n不可遺漏的專案規則\n"
    (project / "CLAUDE.md").write_text(legacy, encoding="utf-8")

    result = _執行(project, "--json")

    assert result.returncode == 0, result.stderr
    assert not (project / "AGENTS.md").exists()
    assert (project / "AGENTS.md.new").read_text(encoding="utf-8") == legacy
    assert (project / "CLAUDE.md").read_text(encoding="utf-8") == legacy
    assert (project / "CLAUDE.md.new").read_text(encoding="utf-8").startswith(
        "# Claude Code 專案 adapter\n\n@AGENTS.md"
    )


def test_本_repo_雙入口保留必要規則且不含個人設定(repo_root: Path):
    """遷移不是把舊 CLAUDE.md 變短就算完成；會改變行為的專案規則必須仍在共同入口。"""
    agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    claude = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    required = (
        "uv run pytest",
        "--format backlog --output",
        "install.sh` 複製工作區",
        "tests/test_install.py::_是本機產生物()",
        "已廢除的流程規則",
        "agent-runtime.json",
        "不得版控",
        "合併回整合分支或主線前",
        "絕不主動 push",
        "git worktree remove",
    )
    missing = [item for item in required if item not in agents]
    assert not missing, "AGENTS.md 遷移漏掉會改變行為的規則：" + "、".join(missing)
    assert claude.startswith("# Claude Code 專案 adapter\n\n@AGENTS.md")
    for duplicated in ("uv run pytest", "git worktree remove", "絕不主動 push"):
        assert duplicated not in claude, f"CLAUDE.md 重複共同規則：{duplicated}"
    active = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            repo_root / "AGENTS.md",
            repo_root / "CLAUDE.md",
            repo_root / ".gitignore",
            repo_root / ".agent/agent-runtime.json",
        )
    )
    for forbidden in (
        "headroom",
        "ANTHROPIC_BASE_URL",
        "/home/augustushsu",
        "access_token",
        "cookie=",
        "PRIVATE KEY",
    ):
        assert forbidden not in active, f"現行入口或政策殘留個人／敏感設定：{forbidden}"
