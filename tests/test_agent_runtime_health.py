"""doctor／refresh 的無副作用探針、TTL 與錯誤分類。"""

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
    spec = importlib.util.spec_from_file_location("agent_runtime_health", kit_root / SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _寫執行檔(path: Path, body: str):
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(0o755)


def _環境(tmp_path: Path, fake_bin: Path):
    return {
        "HOME": str(tmp_path / "home"),
        "XDG_STATE_HOME": str(tmp_path / "state"),
        "PATH": f"{fake_bin}:{os.environ.get('PATH', '')}",
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


def _health_args(root: Path, command="doctor", **overrides):
    values = {
        "root": root,
        "command": command,
        "online": False,
        "profile": [],
        "probe": [],
        "integration": [],
        "manual_profile": [],
        "manual_integration": [],
        "json": False,
        "force": command == "doctor",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _準備(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    root = tmp_path / "repo"
    shutil.copytree(kit_root, root)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    env = _環境(tmp_path, fake_bin)
    runtime.init_runtime(_init_args(root), env=env, now=datetime(2026, 8, 26, tzinfo=timezone.utc))
    return runtime, root, fake_bin, env


def _正常_clis(fake_bin: Path):
    _寫執行檔(
        fake_bin / "claude",
        'echo "$*" >> "$PROBE_LOG"\n'
        'case "$*" in *"-p"*) echo AGENT_RUNTIME_PROBE_OK;; *"auth status"*) echo "{}";; *) echo 1.0;; esac\n',
    )
    _寫執行檔(
        fake_bin / "codex",
        'echo "$*" >> "$PROBE_LOG"\n'
        'case "$*" in *"exec"*) echo AGENT_RUNTIME_PROBE_OK;; *"login status"*) echo logged-in;; *) echo 1.0;; esac\n',
    )
    _寫執行檔(fake_bin / "git", 'echo "$*" >> "$PROBE_LOG"\necho remote-ok\n')
    _寫執行檔(fake_bin / "gh", 'echo "$*" >> "$PROBE_LOG"\necho test-user\n')


def test_offline_doctor_不執行任何_online_read_probe(kit_root: Path, tmp_path: Path):
    runtime, root, fake_bin, env = _準備(kit_root, tmp_path)
    _正常_clis(fake_bin)
    log = tmp_path / "probes.log"
    env["PROBE_LOG"] = str(log)
    output = runtime.health_runtime(_health_args(root), env=env)
    calls = log.read_text(encoding="utf-8")
    assert "--version" in calls
    assert "auth status" in calls and "login status" in calls
    assert "exec" not in calls and "-p" not in calls
    assert "ls-remote" not in calls and "api user" not in calls
    assert output["profiles"]["codex-cli"]["status"] == "unknown"
    assert output["integrations"]["git_remote_read"]["status"] == "unknown"


def test_metadata_失敗但功能成功會保留兩份證據並標_degraded(kit_root: Path, tmp_path: Path):
    runtime, root, fake_bin, env = _準備(kit_root, tmp_path)
    _正常_clis(fake_bin)
    _寫執行檔(
        fake_bin / "codex",
        'case "$*" in *"login status"*) echo "not logged in" >&2; exit 1;; '
        '*"exec"*) echo AGENT_RUNTIME_PROBE_OK;; *) echo 1.0;; esac\n',
    )
    env["PROBE_LOG"] = str(tmp_path / "unused.log")
    output = runtime.health_runtime(
        _health_args(root, online=True, profile=["codex-cli"]), env=env
    )
    item = output["profiles"]["codex-cli"]
    assert item["status"] == "degraded"
    assert item["error_class"] == "evidence_conflict"
    assert item["probes"]["auth"]["status"] == "unavailable"
    assert item["probes"]["auth"]["error_class"] == "auth"
    assert item["probes"]["functional"]["status"] == "verified"


def test_github_六種能力分開且讀成功不推出寫入或_connector(kit_root: Path, tmp_path: Path):
    runtime, root, fake_bin, env = _準備(kit_root, tmp_path)
    _正常_clis(fake_bin)
    env["PROBE_LOG"] = str(tmp_path / "probes.log")
    output = runtime.health_runtime(
        _health_args(root, online=True, profile=["codex-cli"]), env=env
    )
    integrations = output["integrations"]
    assert integrations["git_remote_read"]["status"] == "verified"
    assert integrations["github_api_read"]["status"] == "verified"
    for key in ("git_remote_write", "github_api_write", "codex_cloud_connector", "automated_review"):
        assert integrations[key]["status"] == "unknown", key


def test_app_connector_可人工確認且有到期時間(kit_root: Path, tmp_path: Path):
    runtime, root, fake_bin, env = _準備(kit_root, tmp_path)
    _正常_clis(fake_bin)
    env["PROBE_LOG"] = str(tmp_path / "probes.log")
    now = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)
    output = runtime.health_runtime(
        _health_args(
            root,
            profile=["codex-app-local"],
            manual_profile=["codex-app-local=verified"],
            manual_integration=["codex_cloud_connector=verified"],
        ),
        env=env,
        now=now,
    )
    profile = output["profiles"]["codex-app-local"]
    connector = output["integrations"]["codex_cloud_connector"]
    assert profile["status"] == "verified"
    assert connector["status"] == "verified"
    assert profile["evidence"]["kind"] == "manual_confirmation"
    assert datetime.fromisoformat(connector["expires_at"]) == now + timedelta(seconds=1800)


def test_refresh_只重跑過期或指定_probe(kit_root: Path, tmp_path: Path):
    runtime, root, fake_bin, env = _準備(kit_root, tmp_path)
    _正常_clis(fake_bin)
    log = tmp_path / "probes.log"
    env["PROBE_LOG"] = str(log)
    now = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)
    runtime.health_runtime(
        _health_args(root, online=True, profile=["codex-cli"]), env=env, now=now
    )
    first_calls = log.read_text(encoding="utf-8").splitlines()
    runtime.health_runtime(
        _health_args(root, command="refresh", online=True, profile=["codex-cli"]),
        env=env,
        now=now + timedelta(minutes=5),
    )
    assert log.read_text(encoding="utf-8").splitlines() == first_calls
    runtime.health_runtime(
        _health_args(
            root,
            command="refresh",
            online=True,
            profile=["codex-cli"],
            probe=["codex_login_status"],
        ),
        env=env,
        now=now + timedelta(minutes=5),
    )
    assert len(log.read_text(encoding="utf-8").splitlines()) == len(first_calls) + 1


def test_probe_錯誤分類涵蓋未安裝_auth_quota_permission_timeout(kit_root: Path, tmp_path: Path):
    runtime = _載入_runtime(kit_root)
    root = tmp_path / "repo"
    root.mkdir()
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    env = _環境(tmp_path, fake_bin)
    now = datetime(2026, 8, 26, tzinfo=timezone.utc)
    missing = runtime.run_probe(
        {"command": ["does-not-exist"], "summary": "missing"}, 60, now, root, env
    )
    assert missing["error_class"] == "not_installed"
    cases = {
        "auth": "echo 'not logged in' >&2; exit 1\n",
        "quota": "echo 'quota exceeded' >&2; exit 1\n",
        "permission": "echo 'permission denied' >&2; exit 1\n",
    }
    for expected, body in cases.items():
        executable = fake_bin / expected
        _寫執行檔(executable, body)
        record = runtime.run_probe(
            {"command": [expected], "summary": expected}, 60, now, root, env
        )
        assert record["error_class"] == expected
    sleeper = fake_bin / "sleeper"
    _寫執行檔(sleeper, "sleep 1\n")
    timeout = runtime.run_probe(
        {"command": ["sleeper"], "summary": "timeout"},
        60,
        now,
        root,
        env,
        timeout=0.01,
    )
    assert timeout["error_class"] == "timeout"


def test_probe_registry_沒有外部寫入命令(kit_root: Path):
    runtime = _載入_runtime(kit_root)
    commands = [
        definition["command"]
        for definition in [*runtime.PROBE_DEFINITIONS.values(), *runtime.GITHUB_INTEGRATIONS.values()]
        if "command" in definition
    ]
    text = "\n".join(" ".join(command) for command in commands)
    for forbidden in ("git push", "gh pr create", "gh issue create", "purchase", "subscribe"):
        assert forbidden not in text
    assert "git ls-remote" in text
    assert "gh api user" in text


def test_cli_明確接受_offline_旗標而且不跑網路(bare_install: Path, tmp_path: Path):
    project = tmp_path / "project"
    shutil.copytree(bare_install, project)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _正常_clis(fake_bin)
    env = _環境(tmp_path, fake_bin)
    env["PROBE_LOG"] = str(tmp_path / "probes.log")
    init = subprocess.run(
        [sys.executable, SCRIPT, "init", "--non-interactive", "--verified-profile", "codex-cli"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert init.returncode == 0, init.stderr
    result = subprocess.run(
        [sys.executable, SCRIPT, "doctor", "--offline", "--profile", "codex-cli", "--json"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    calls = (tmp_path / "probes.log").read_text(encoding="utf-8")
    assert output["mode"] == "offline"
    assert "exec" not in calls and "ls-remote" not in calls and "api user" not in calls
