"""能力路由、可解釋分數、覆寫與中途失效交接。"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


SCRIPT = ".agent/scripts/agent_runtime.py"


def _載入_runtime(kit_root: Path):
    spec = importlib.util.spec_from_file_location("agent_runtime_routing", kit_root / SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _環境(tmp_path: Path):
    return {
        "HOME": str(tmp_path / "home"),
        "XDG_STATE_HOME": str(tmp_path / "state"),
        "PATH": os.environ.get("PATH", ""),
    }


def _init_args(root: Path):
    return SimpleNamespace(
        root=root,
        config=None,
        project_name=None,
        default_data_class=None,
        cloud_policy=None,
        connector_policy=None,
        enable_profile=[],
        prefer_profile=[],
        verified_profile=["codex-cli"],
        non_interactive=True,
        json=False,
    )


def _route_args(root: Path, **overrides):
    values = {
        "root": root,
        "task_file": None,
        "task_profile": "implementation_local",
        "data_class": None,
        "require_capability": [],
        "override_profile": None,
        "override_scope": "single",
        "override_expires_at": None,
        "failed_profile": None,
        "task_id": None,
        "branch": None,
        "head": None,
        "completed_ac": [],
        "pending_ac": [],
        "validation": [],
        "failure_type": None,
        "external_side_effects": False,
        "allow_auto_read_handoff": False,
        "explain": False,
        "json": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _準備(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    root = tmp_path / "repo"
    shutil.copytree(kit_root, root)
    env = _環境(tmp_path)
    now = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)
    runtime.init_runtime(_init_args(root), env=env, now=now)
    tasks, adapters = runtime.load_registry(root)
    del tasks
    state, path = runtime.load_state(root, env)
    return runtime, root, env, now, adapters, state, path


def _狀態(runtime, manifest, now, status="verified", expires_in=3600):
    record = runtime._verified_entry(manifest, now)
    record["status"] = status
    record["expires_at"] = (now + timedelta(seconds=expires_in)).isoformat()
    record["evidence"]["summary"] = f"fixture {status}"
    if status not in {"verified", "unknown"}:
        record["error_class"] = "fixture_failure"
    return record


def _寫狀態(runtime, path, state):
    runtime.write_json(path, state)


def _改政策(root: Path, **changes):
    path = root / ".agent/agent-runtime.json"
    policy = json.loads(path.read_text(encoding="utf-8"))
    policy.update(changes)
    path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_硬性能力先排除且單一供應商不會自動通過(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(root, enabled_profiles=["codex-cli"])
    state["profiles"]["codex-cli"] = _狀態(runtime, adapters["codex-cli"], now)
    _寫狀態(runtime, path, state)
    decision = runtime.route_decision(
        root,
        "implementation_local",
        required_overrides=["visual_interaction"],
        now=now,
        env=env,
    )
    assert decision["selected_profile"] is None
    codex = next(item for item in decision["candidates"] if item["id"] == "codex-cli")
    assert any("visual_interaction" in reason for reason in codex["excluded_reasons"])


def test_cloud_forbid_在可用性與分數之前排除(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(root, enabled_profiles=["codex-cloud"], cloud_policy="forbid")
    state["profiles"]["codex-cloud"] = _狀態(runtime, adapters["codex-cloud"], now)
    _寫狀態(runtime, path, state)
    decision = runtime.route_decision(root, "parallel_long_running", now=now, env=env)
    cloud = next(item for item in decision["candidates"] if item["id"] == "codex-cloud")
    assert decision["selected_profile"] is None
    assert cloud["score"] is None
    assert any("project cloud policy=forbid" in reason for reason in cloud["excluded_reasons"])


def test_偏好只在合格候選間加分且相同輸入決策相同(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(
        root,
        enabled_profiles=["claude-code-cli", "codex-cli"],
        preferred_profiles=["codex-cli", "claude-code-cli"],
    )
    for profile_id in ("claude-code-cli", "codex-cli"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    _寫狀態(runtime, path, state)
    first = runtime.route_decision(root, "implementation_local", now=now, env=env)
    second = runtime.route_decision(root, "implementation_local", now=now, env=env)
    assert first == second
    assert first["selected_profile"] == "codex-cli"
    codex = next(item for item in first["candidates"] if item["id"] == "codex-cli")
    assert {item["factor"] for item in codex["score_details"]} >= {
        "availability",
        "project_preference",
        "optional_capabilities",
        "cost_metadata_unknown",
        "latency_metadata_unknown",
        "context_metadata_unknown",
    }


def test_使用者覆寫可改合格排序但不能繞過硬能力或政策(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(
        root,
        enabled_profiles=["claude-code-cli", "codex-cli"],
        preferred_profiles=["codex-cli"],
    )
    for profile_id in ("claude-code-cli", "codex-cli"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    _寫狀態(runtime, path, state)
    decision = runtime.route_decision(
        root,
        "implementation_local",
        override_profile="claude-code-cli",
        now=now,
        env=env,
    )
    assert decision["selected_profile"] == "claude-code-cli"
    try:
        runtime.route_decision(
            root,
            "visual_interactive",
            override_profile="codex-cli",
            now=now,
            env=env,
        )
    except runtime.RuntimeConfigError as error:
        assert "不合格" in str(error) and "visual_interaction" in str(error)
    else:
        raise AssertionError("使用者覆寫不得繞過硬性能力")


def test_round_與_project_override_必須明示到期條件(kit_root: Path, tmp_path: Path):
    runtime, root, *_ = _準備(kit_root, tmp_path)
    args = _route_args(root, override_profile="codex-cli", override_scope="round")
    try:
        runtime._validate_override_args(args)
    except runtime.RuntimeConfigError as error:
        assert "--override-expires-at" in str(error)
    else:
        raise AssertionError("整輪覆寫沒有到期條件不得通過")
    args.override_expires_at = "本輪 merge 完成"
    assert runtime._validate_override_args(args)["scope"] == "round"


def test_過期_cache_只有純本機唯讀任務可當_unknown_候選(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(root, enabled_profiles=["codex-cli"])
    state["profiles"]["codex-cli"] = _狀態(
        runtime, adapters["codex-cli"], now, expires_in=-1
    )
    _寫狀態(runtime, path, state)
    read = runtime.route_decision(root, "design_research", now=now, env=env)
    write = runtime.route_decision(root, "implementation_local", now=now, env=env)
    assert read["selected_profile"] == "codex-cli"
    assert write["selected_profile"] is None


def test_中途失效保留同一工單並產生可交接資料(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(root, enabled_profiles=["claude-code-cli", "codex-cli"])
    for profile_id in ("claude-code-cli", "codex-cli"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    _寫狀態(runtime, path, state)
    args = _route_args(
        root,
        failed_profile="codex-cli",
        task_id="PEV-DEV-AGENT-039",
        branch="PEV-DEV-AGENT-039",
        head="abc1234",
        completed_ac=["AC-01"],
        pending_ac=["AC-02"],
        validation=["pytest 12 passed"],
        failure_type="quota",
        allow_auto_read_handoff=True,
    )
    decision = runtime.route_runtime(args, env=env, now=now)
    assert decision["selected_profile"] == "claude-code-cli"
    handoff = decision["handoff"]
    assert handoff["task_id"] == "PEV-DEV-AGENT-039"
    assert handoff["branch"] == "PEV-DEV-AGENT-039"
    assert handoff["head"] == "abc1234"
    assert handoff["completed_ac"] == ["AC-01"]
    assert handoff["validations"] == ["pytest 12 passed"]
    assert handoff["suggested_profile"] == "claude-code-cli"
    assert handoff["auto_handoff_allowed"] is False, "有 repo_write 的任務不能自動接手"
    assert handoff["requires_user_confirmation"] is True


def test_純讀失效才可由明示政策允許自動接手(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(root, enabled_profiles=["claude-code-cli", "codex-cli"])
    for profile_id in ("claude-code-cli", "codex-cli"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    _寫狀態(runtime, path, state)
    args = _route_args(
        root,
        task_profile="design_research",
        failed_profile="codex-cli",
        task_id="DN-012",
        branch="DN-012",
        head="def5678",
        failure_type="auth",
        allow_auto_read_handoff=True,
    )
    decision = runtime.route_runtime(args, env=env, now=now)
    assert decision["handoff"]["auto_handoff_allowed"] is True
    assert decision["handoff"]["requires_user_confirmation"] is False


def test_explain_輸出單一候選的排除理由(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, *_ = _準備(kit_root, tmp_path)
    args = SimpleNamespace(
        root=root,
        task_profile="visual_interactive",
        execution_profile="codex-cli",
        data_class=None,
        require_capability=[],
        json=False,
    )
    output = runtime.explain_runtime(args, env=env, now=now)
    item = output["execution_profile"]
    assert item["eligible"] is False
    assert any("visual_interaction" in reason for reason in item["excluded_reasons"])


def test_route_cli_同時提供_json_與零候選非零_exit(bare_install: Path, tmp_path: Path):
    project = tmp_path / "project"
    shutil.copytree(bare_install, project)
    env = _環境(tmp_path)
    init = subprocess.run(
        [sys.executable, SCRIPT, "init", "--non-interactive", "--verified-profile", "codex-cli"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert init.returncode == 0, init.stderr
    route = subprocess.run(
        [sys.executable, SCRIPT, "route", "--task-profile", "implementation_local", "--json"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert route.returncode == 0, route.stderr
    output = json.loads(route.stdout)
    assert output["selected_profile"] == "codex-cli"
    assert output["candidates"]
    impossible = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "route",
            "--task-profile",
            "implementation_local",
            "--require-capability",
            "visual_interaction",
            "--require-capability",
            "noninteractive",
            "--json",
        ],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert impossible.returncode == 3
    assert json.loads(impossible.stdout)["selected_profile"] is None


def test_舊工單可由_task_type_映射並用_route_explain_顯示來源(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, path = _準備(kit_root, tmp_path)
    _改政策(root, enabled_profiles=["codex-cli"])
    state["profiles"]["codex-cli"] = _狀態(runtime, adapters["codex-cli"], now)
    _寫狀態(runtime, path, state)
    task = root / "legacy-task.md"
    task.write_text(
        "# [Task ID: LEG-DEV-BE-001] 舊工單\n\n"
        "**🏷️ 任務類型 (Task Type):** queue_backend\n"
        "**👤 負責人 (Assignee):** backend-developer\n",
        encoding="utf-8",
    )
    args = _route_args(root, task_file=Path("legacy-task.md"), task_profile=None, explain=True)
    decision = runtime.route_runtime(args, env=env, now=now)
    assert decision["task_profile"] == "implementation_local"
    assert decision["task_profile_source"] == "Task Type mapping：queue_backend"
    assert decision["selected_profile"] == "codex-cli"


def test_工單與審查模板保留完整路由證據但_assignee_仍是角色(kit_root: Path):
    task = (
        kit_root / "docs/features/_TEMPLATE/tasks/_EXAMPLE-DEV-BE-001.md"
    ).read_text(encoding="utf-8")
    review = (
        kit_root / "docs/features/_TEMPLATE/reviews/_REVIEW_TEMPLATE.md"
    ).read_text(encoding="utf-8")
    protocol = (kit_root / ".agent/resources/team_protocol.md").read_text(encoding="utf-8")
    for field in (
        "Task Profile",
        "Required Capabilities",
        "Data Class",
        "Execution Override",
    ):
        assert field in task
    for evidence in (
        "選中 Execution Profile",
        "候選與排除理由",
        "Probe 證據時間",
        "使用過期 cache",
        "中途交接",
    ):
        assert evidence in review
    assert "`Assignee` 仍然只填**角色**" in protocol
    assert "不得填 Claude／Codex 等供應商" in protocol
