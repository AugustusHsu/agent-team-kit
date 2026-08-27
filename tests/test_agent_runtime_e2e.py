"""混合代理從安裝、初始化、路由到失效交接的端到端矩陣。"""

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
    spec = importlib.util.spec_from_file_location("agent_runtime_e2e", kit_root / SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _環境(tmp_path: Path):
    return {
        "HOME": str(tmp_path / "home"),
        "XDG_STATE_HOME": str(tmp_path / "state"),
        "PATH": os.environ.get("PATH", ""),
    }


def _init_args(root: Path, verified="codex-cli"):
    return SimpleNamespace(
        root=root,
        config=None,
        project_name=None,
        default_data_class=None,
        cloud_policy=None,
        connector_policy=None,
        enable_profile=[],
        prefer_profile=[],
        verified_profile=[verified] if verified else [],
        non_interactive=True,
        json=False,
    )


def _route_args(root: Path, failed_profile=None, **overrides):
    values = {
        "root": root,
        "task_file": None,
        "task_profile": "implementation_local",
        "data_class": None,
        "require_capability": [],
        "override_profile": None,
        "override_scope": "single",
        "override_expires_at": None,
        "failed_profile": failed_profile,
        "task_id": "PEV-DEV-AGENT-042" if failed_profile else None,
        "branch": "PEV-DEV-AGENT-042" if failed_profile else None,
        "head": "abc1234" if failed_profile else None,
        "completed_ac": ["AC-01", "AC-02"] if failed_profile else [],
        "pending_ac": ["AC-03"] if failed_profile else [],
        "validation": ["pytest 200 passed"] if failed_profile else [],
        "failure_type": "quota" if failed_profile else None,
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
    now = datetime(2026, 8, 27, tzinfo=timezone.utc)
    runtime.init_runtime(_init_args(root), env=env, now=now)
    tasks, adapters = runtime.load_registry(root)
    del tasks
    state, state_path = runtime.load_state(root, env)
    return runtime, root, env, now, adapters, state, state_path


def _狀態(runtime, manifest, now, status="verified", expires_in=3600):
    record = runtime._verified_entry(manifest, now)
    record["status"] = status
    record["expires_at"] = (now + timedelta(seconds=expires_in)).isoformat()
    if status != "verified":
        record["error_class"] = "fixture_failure"
    return record


def _寫政策(root: Path, enabled, preferred, cloud_policy="conditional"):
    path = root / ".agent/agent-runtime.json"
    policy = json.loads(path.read_text(encoding="utf-8"))
    policy.update(
        enabled_profiles=enabled,
        preferred_profiles=preferred,
        cloud_policy=cloud_policy,
    )
    path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_新專案_install_init_可重跑且得到_verified_local_profile(
    bare_install: Path, tmp_path: Path
):
    project = tmp_path / "project"
    shutil.copytree(bare_install, project)
    env = _環境(tmp_path)
    command = [
        sys.executable,
        SCRIPT,
        "init",
        "--non-interactive",
        "--enable-profile",
        "claude-code-cli",
        "--enable-profile",
        "codex-cli",
        "--prefer-profile",
        "codex-cli",
        "--verified-profile",
        "codex-cli",
        "--json",
    ]
    first = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True, timeout=20)
    policy_before = (project / ".agent/agent-runtime.json").read_bytes()
    second = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True, timeout=20)
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert (project / ".agent/agent-runtime.json").read_bytes() == policy_before
    state = json.loads((tmp_path / "state/agent-team-kit/agent-runtime.json").read_text())
    assert state["profiles"]["codex-cli"]["status"] == "verified"


def test_雙供應商_單一供應商與訂閱失效都能正常降級(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, state_path = _準備(kit_root, tmp_path)
    for profile_id in ("claude-code-cli", "codex-cli"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    runtime.write_json(state_path, state)
    _寫政策(root, ["claude-code-cli", "codex-cli"], ["codex-cli", "claude-code-cli"])
    both = runtime.route_decision(root, "implementation_local", now=now, env=env)
    assert both["selected_profile"] == "codex-cli"
    assert all(item["eligible"] for item in both["candidates"] if item["id"] in {"claude-code-cli", "codex-cli"})

    state["profiles"]["codex-cli"] = _狀態(runtime, adapters["codex-cli"], now, expires_in=-1)
    runtime.write_json(state_path, state)
    expired = runtime.route_decision(root, "implementation_local", now=now, env=env)
    assert expired["selected_profile"] == "claude-code-cli"

    for only in ("claude-code-cli", "codex-cli"):
        state["profiles"][only] = _狀態(runtime, adapters[only], now)
        runtime.write_json(state_path, state)
        _寫政策(root, [only], [only])
        assert runtime.route_decision(root, "implementation_local", now=now, env=env)[
            "selected_profile"
        ] == only


def test_claude_與_codex_雙向失效都保留完整_handoff(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, state_path = _準備(kit_root, tmp_path)
    for profile_id in ("claude-code-cli", "codex-cli"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    runtime.write_json(state_path, state)
    _寫政策(root, ["claude-code-cli", "codex-cli"], ["codex-cli", "claude-code-cli"])
    for failed, expected in (
        ("codex-cli", "claude-code-cli"),
        ("claude-code-cli", "codex-cli"),
    ):
        decision = runtime.route_runtime(_route_args(root, failed), env=env, now=now)
        handoff = decision["handoff"]
        assert decision["selected_profile"] == expected
        assert handoff == {
            "task_id": "PEV-DEV-AGENT-042",
            "branch": "PEV-DEV-AGENT-042",
            "head": "abc1234",
            "failure_type": "quota",
            "completed_ac": ["AC-01", "AC-02"],
            "pending_ac": ["AC-03"],
            "validations": ["pytest 200 passed"],
            "failed_profile": failed,
            "suggested_profile": expected,
            "external_side_effects": False,
            "auto_handoff_allowed": False,
            "requires_user_confirmation": True,
        }


def test_cloud_forbid_且_connector_unknown_仍選本機不偷降級(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, state_path = _準備(kit_root, tmp_path)
    for profile_id in ("codex-cli", "codex-cloud"):
        state["profiles"][profile_id] = _狀態(runtime, adapters[profile_id], now)
    state["integrations"]["codex_cloud_connector"] = runtime._manual_record(
        "unknown", "fixture connector unknown", now, 1800
    )
    runtime.write_json(state_path, state)
    _寫政策(root, ["codex-cli", "codex-cloud"], ["codex-cloud"], cloud_policy="forbid")
    decision = runtime.route_decision(root, "implementation_local", now=now, env=env)
    assert decision["selected_profile"] == "codex-cli"
    cloud = next(item for item in decision["candidates"] if item["id"] == "codex-cloud")
    assert not cloud["eligible"]
    assert any("cloud policy=forbid" in reason for reason in cloud["excluded_reasons"])


def test_沒有_app_只裝_codex_cli_仍符合最低門檻(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, state_path = _準備(kit_root, tmp_path)
    state["profiles"] = {"codex-cli": _狀態(runtime, adapters["codex-cli"], now)}
    runtime.write_json(state_path, state)
    _寫政策(root, ["codex-cli"], ["codex-cli"])
    assert runtime.route_decision(root, "implementation_local", now=now, env=env)[
        "selected_profile"
    ] == "codex-cli"


def test_第三方_provider_只加_manifest_不改核心程式(kit_root: Path, tmp_path: Path):
    runtime, root, env, now, adapters, state, state_path = _準備(kit_root, tmp_path)
    script_hash = (root / SCRIPT).read_bytes()
    third = dict(adapters["codex-cli"])
    third.update(id="acme-cli", provider="acme", title="Acme CLI")
    manifest = root / ".agent/resources/agent_runtime/adapters/acme-cli.json"
    manifest.write_text(json.dumps(third, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _, reloaded = runtime.load_registry(root)
    state["profiles"]["acme-cli"] = _狀態(runtime, reloaded["acme-cli"], now)
    runtime.write_json(state_path, state)
    _寫政策(root, ["acme-cli"], ["acme-cli"])
    assert runtime.route_decision(root, "implementation_local", now=now, env=env)[
        "selected_profile"
    ] == "acme-cli"
    assert (root / SCRIPT).read_bytes() == script_hash
