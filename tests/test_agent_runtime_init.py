"""agent runtime 的設定分層、初始化與安全狀態。

所有帳號與 HOME 都是 tmp_path 裡的假資料；本檔不讀取開發者真實的 Claude、Codex 或 GitHub 狀態。
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


SCRIPT = ".agent/scripts/agent_runtime.py"


def _載入_runtime(kit_root: Path):
    spec = importlib.util.spec_from_file_location("agent_runtime", kit_root / SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _假環境(tmp_path: Path):
    return {
        "HOME": str(tmp_path / "home"),
        "XDG_STATE_HOME": str(tmp_path / "state"),
        "PATH": os.environ.get("PATH", ""),
    }


def _執行(專案: Path, tmp_path: Path, *args, input_text=None):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=專案,
        env=_假環境(tmp_path),
        input=input_text,
        capture_output=True,
        text=True,
        timeout=20,
    )


def _專案副本(bare_install: Path, tmp_path: Path):
    target = tmp_path / "project"
    shutil.copytree(bare_install, target)
    return target


def _初始化參數(root: Path, **overrides):
    values = {
        "root": root,
        "config": None,
        "project_name": None,
        "default_data_class": None,
        "cloud_policy": None,
        "connector_policy": None,
        "enable_profile": [],
        "prefer_profile": [],
        "verified_profile": ["codex-cli"],
        "non_interactive": True,
        "json": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_init_旗標模式建立共享政策與_xdg_狀態(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    result = _執行(
        project,
        tmp_path,
        "init",
        "--non-interactive",
        "--verified-profile",
        "codex-cli",
        "--prefer-profile",
        "codex-cli",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    policy = json.loads((project / ".agent/agent-runtime.json").read_text(encoding="utf-8"))
    state_path = tmp_path / "state/agent-team-kit/agent-runtime.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(policy["project_id"]) == 32
    assert policy["preferred_profiles"] == ["codex-cli"]
    assert state["profiles"]["codex-cli"]["status"] == "verified"
    assert output["state"] == str(state_path)
    serialized = json.dumps(state, ensure_ascii=False).lower()
    for forbidden in ("access_token", "cookie=", "private_key", "environment"):
        assert forbidden not in serialized


def test_init_互動模式可選本機_profile(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    result = _執行(project, tmp_path, "init", input_text="claude-code-cli\n")
    assert result.returncode == 0, result.stderr
    state = json.loads(
        (tmp_path / "state/agent-team-kit/agent-runtime.json").read_text(encoding="utf-8")
    )
    assert state["profiles"]["claude-code-cli"]["status"] == "verified"
    assert "請選擇至少一個" in result.stdout


def test_init_非互動模式未確認本機能力會明確失敗(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    result = _執行(project, tmp_path, "init", "--non-interactive")
    assert result.returncode == 2
    assert "至少要有一個本機開發 profile verified" in result.stderr
    assert "--verified-profile" in result.stderr


def test_init_設定檔模式可重跑且不覆蓋既有政策(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    config = tmp_path / "init.json"
    config.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_name": "第一個名稱",
                "enabled_profiles": ["claude-code-cli", "codex-cli"],
                "preferred_profiles": ["claude-code-cli"],
                "verified_profiles": ["claude-code-cli"],
            }
        ),
        encoding="utf-8",
    )
    first = _執行(project, tmp_path, "init", "--non-interactive", "--config", str(config))
    assert first.returncode == 0, first.stderr
    policy_path = project / ".agent/agent-runtime.json"
    original = policy_path.read_text(encoding="utf-8")

    config_data = json.loads(config.read_text(encoding="utf-8"))
    config_data["project_name"] = "候選名稱"
    config.write_text(json.dumps(config_data), encoding="utf-8")
    second = _執行(project, tmp_path, "init", "--non-interactive", "--config", str(config))

    assert second.returncode == 0, second.stderr
    assert policy_path.read_text(encoding="utf-8") == original
    candidate = Path(str(policy_path) + ".new")
    assert json.loads(candidate.read_text(encoding="utf-8"))["project_name"] == "候選名稱"
    assert "政策有差異，候選寫入" in second.stdout


def test_init_缺入口只產生_new_候選不改變_agent_行為(bare_install: Path, tmp_path: Path):
    project = _專案副本(bare_install, tmp_path)
    (project / "AGENTS.md").unlink()
    (project / "AGENTS.md.new").write_text("# 使用者已修改的候選\n", encoding="utf-8")
    result = _執行(
        project,
        tmp_path,
        "init",
        "--non-interactive",
        "--verified-profile",
        "codex-cli",
    )
    assert result.returncode == 0, result.stderr
    assert not (project / "AGENTS.md").exists()
    assert (project / "AGENTS.md.new").read_text(encoding="utf-8") == "# 使用者已修改的候選\n"
    assert (project / "AGENTS.md.new.2").read_bytes() == (
        project / ".agent/templates/AGENTS.md"
    ).read_bytes()


def test_global_state_與_repo_local_override_正確合併(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    root = tmp_path / "repo"
    shutil.copytree(kit_root, root)
    env = _假環境(tmp_path)
    runtime.init_runtime(
        _初始化參數(
            root,
            enable_profile=["claude-code-cli", "codex-cli", "codex-app-local"],
            prefer_profile=["claude-code-cli"],
        ),
        env=env,
        now=datetime(2026, 8, 26, tzinfo=timezone.utc),
    )
    (root / ".agent/agent-runtime.local.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "disabled_profiles": ["claude-code-cli"],
                "preferred_profiles": ["codex-app-local", "codex-cli"],
            }
        ),
        encoding="utf-8",
    )
    effective = runtime.effective_policy(root)
    state, state_path = runtime.load_state(root, env)
    assert effective["enabled_profiles"] == ["codex-cli", "codex-app-local"]
    assert effective["preferred_profiles"] == ["codex-app-local", "codex-cli"]
    assert effective["project_id"] == runtime.project_identity(root)
    assert state["profiles"]["codex-cli"]["status"] == "verified"
    assert state_path.is_relative_to(tmp_path)


def test_repo_local_override_的未知_profile_不會被靜默忽略(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    root = tmp_path / "repo"
    shutil.copytree(kit_root, root)
    runtime.init_runtime(_初始化參數(root), env=_假環境(tmp_path))
    path = root / ".agent/agent-runtime.local.json"
    path.write_text(
        json.dumps({"schema_version": 1, "disabled_profiles": ["typo-agent"]}),
        encoding="utf-8",
    )
    try:
        runtime.effective_policy(root)
    except runtime.RuntimeConfigError as error:
        assert str(path) in str(error)
        assert "$.disabled_profiles" in str(error)
        assert "typo-agent" in str(error)
    else:
        raise AssertionError("未知 profile 不得被靜默忽略")


def test_git_worktree_沿用同一個_portable_project_id(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    repo = tmp_path / "repo"
    shutil.copytree(kit_root, repo)
    runtime.init_runtime(_初始化參數(repo), env=_假環境(tmp_path))
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
    worktree = tmp_path / "worktree"
    subprocess.run(
        ["git", "worktree", "add", str(worktree), "-b", "ticket"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    assert runtime.project_identity(repo) == runtime.project_identity(worktree)


def test_json_損壞_schema_版本與未知欄位都指出檔案及路徑(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    broken = tmp_path / "broken.json"
    broken.write_text('{"schema_version":', encoding="utf-8")
    try:
        runtime.load_json(broken)
    except runtime.RuntimeConfigError as error:
        assert str(broken) in str(error)
        assert "JSON 損壞" in str(error)
    else:
        raise AssertionError("損壞 JSON 不得通過")

    root = tmp_path / "repo"
    shutil.copytree(kit_root, root)
    policy = {
        "schema_version": 99,
        "project_id": "0" * 32,
        "project_name": "repo",
        "enabled_profiles": [],
        "preferred_profiles": [],
        "default_data_class": "internal",
        "cloud_policy": "conditional",
        "connector_policy": "conditional",
        "capabilites": [],
    }
    (root / ".agent/agent-runtime.json").write_text(json.dumps(policy), encoding="utf-8")
    try:
        runtime.load_policy(root)
    except runtime.RuntimeConfigError as error:
        message = str(error)
        assert ".agent/agent-runtime.json" in message
        assert "$.schema_version" in message
        assert "$.capabilites：未知欄位" in message
    else:
        raise AssertionError("不支援的 schema 與未知欄位不得通過")
