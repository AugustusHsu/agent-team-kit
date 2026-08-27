#!/usr/bin/env python3
"""跨 Claude／Codex 的本機 runtime 管理器。

037 先提供共用載入、驗證、狀態分層與 ``init``。後續工單在同一支腳本加入
``doctor``／``refresh``／``route``／``explain``／``migrate``，不得另造第二套狀態格式。

只使用標準函式庫；任何已安裝 kit 的專案都能直接執行。
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCHEMA_VERSION = 1
RUNTIME_REL = Path(".agent/resources/agent_runtime")
POLICY_REL = Path(".agent/agent-runtime.json")
LOCAL_OVERRIDE_REL = Path(".agent/agent-runtime.local.json")
ENTRY_TEMPLATES = ("AGENTS.md", "CLAUDE.md")
POLICIES = {"allow", "conditional", "forbid"}
STATUSES = {"verified", "degraded", "unavailable", "unknown"}
TASK_RUNTIME_FIELDS = {
    "task_profile": "任務輪廓 (Task Profile)",
    "required_capabilities": "必備能力覆寫 (Required Capabilities)",
    "data_class": "資料分級 (Data Class)",
    "execution_override": "Execution 覆寫 (Execution Override)",
}
PROBE_TIMEOUT_SECONDS = 15

# 這是 probe ID → 無副作用命令的 registry，不是 provider if/else。adapter manifest 只引用 ID；
# 第三家供應商可新增 manifest 與 probe record，不需改 task profile 或路由器。
PROBE_DEFINITIONS = {
    "claude_version": {
        "command": ["claude", "--version"],
        "online": False,
        "summary": "Claude Code CLI 版本檢查通過",
    },
    "claude_auth_status": {
        "command": ["claude", "auth", "status", "--json"],
        "online": False,
        "summary": "Claude Code auth metadata 可讀",
    },
    "claude_readonly_prompt": {
        "command": [
            "claude",
            "-p",
            "Reply exactly AGENT_RUNTIME_PROBE_OK and do not use tools.",
            "--output-format",
            "text",
            "--permission-mode",
            "plan",
        ],
        "online": True,
        "summary": "Claude Code 唯讀功能探針通過",
        "marker": "AGENT_RUNTIME_PROBE_OK",
    },
    "codex_version": {
        "command": ["codex", "--version"],
        "online": False,
        "summary": "Codex CLI 版本檢查通過",
    },
    "codex_login_status": {
        "command": ["codex", "login", "status"],
        "online": False,
        "summary": "Codex CLI login metadata 可讀",
    },
    "codex_readonly_exec": {
        "command": [
            "codex",
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--color",
            "never",
            "Reply exactly AGENT_RUNTIME_PROBE_OK and do not use tools.",
        ],
        "online": True,
        "summary": "Codex CLI 唯讀功能探針通過",
        "marker": "AGENT_RUNTIME_PROBE_OK",
    },
    "codex_app_manual": {"manual": True, "summary": "Codex App 安裝狀態需人工確認"},
    "chatgpt_session_manual": {"manual": True, "summary": "ChatGPT session 需人工確認"},
    "codex_app_local_manual": {"manual": True, "summary": "Codex App Local 需人工確認"},
    "codex_app_worktree_manual": {"manual": True, "summary": "Codex App Worktree 需人工確認"},
    "codex_cloud_manual": {"manual": True, "summary": "Codex Cloud 需人工確認"},
    "codex_github_connector_manual": {
        "manual": True,
        "summary": "Codex Cloud Connector 需人工確認",
    },
}

# GitHub 能力刻意拆開；SSH read 成功不能推出 API write 或 Codex Connector 成功。
GITHUB_INTEGRATIONS = {
    "git_remote_url": {
        "command": ["git", "remote", "get-url", "origin"],
        "online": False,
        "summary": "Git remote URL 可讀",
        "ttl_seconds": 1800,
    },
    "git_remote_read": {
        "command": ["git", "ls-remote", "--heads", "origin"],
        "online": True,
        "summary": "Git remote read 通過",
        "ttl_seconds": 1800,
    },
    "git_remote_write": {
        "manual": True,
        "summary": "Git remote write 不以 push 作健康檢查",
        "ttl_seconds": 1800,
    },
    "github_api_read": {
        "command": ["gh", "api", "user", "--jq", ".login"],
        "online": True,
        "summary": "GitHub API read 通過",
        "ttl_seconds": 1800,
    },
    "github_ssh_read": {
        "command": ["ssh", "-T", "git@github.com"],
        "online": True,
        "summary": "GitHub SSH 驗證通過",
        "ttl_seconds": 1800,
        "marker": "successfully authenticated",
        # GitHub 驗證成功仍刻意回 1，因為它不提供 shell；必須再驗 marker。
        "success_returncodes": [0, 1],
    },
    "github_api_write": {
        "manual": True,
        "summary": "GitHub API write 不以外部寫入作健康檢查",
        "ttl_seconds": 1800,
    },
    "codex_cloud_connector": {
        "manual": True,
        "summary": "Codex Cloud Connector 目前不可自動觀察",
        "ttl_seconds": 1800,
    },
    "automated_review": {
        "manual": True,
        "summary": "automated review 需人工確認平台設定",
        "ttl_seconds": 1800,
    },
}


class RuntimeConfigError(Exception):
    """設定檔可定位的錯誤；訊息可以直接交給使用者修正。"""


def _json_path(parent, key):
    if isinstance(key, int):
        return f"{parent}[{key}]"
    return f"{parent}.{key}"


def validate_schema(value, schema, path="$"):
    """驗證本工具使用到的 JSON Schema 子集合，回傳帶 JSON path 的問題。"""
    problems = []
    expected = schema.get("type")
    if isinstance(expected, list):
        types = tuple(expected)
    elif expected:
        types = (expected,)
    else:
        types = ()
    mapping = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "null": type(None),
    }
    if types and not any(isinstance(value, mapping[item]) and not (item == "integer" and isinstance(value, bool)) for item in types):
        problems.append(f"{path}：型別應為 {'／'.join(types)}")
        return problems
    if "const" in schema and value != schema["const"]:
        problems.append(f"{path}：不支援 {value!r}，期望 {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        problems.append(f"{path}：必須是 {schema['enum']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            problems.append(f"{path}：不得為空")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            problems.append(f"{path}：格式不符 {schema['pattern']!r}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            problems.append(f"{path}：項目不足")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(serialized) != len(set(serialized)):
                problems.append(f"{path}：不得重複")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                problems.extend(validate_schema(item, item_schema, _json_path(path, index)))
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        for key in sorted(required - set(value)):
            problems.append(f"{_json_path(path, key)}：缺少必要欄位")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child = _json_path(path, key)
            if key in properties:
                problems.extend(validate_schema(item, properties[key], child))
            elif additional is False:
                problems.append(f"{child}：未知欄位")
            elif isinstance(additional, dict):
                problems.extend(validate_schema(item, additional, child))
    return problems


def load_json(path, schema_path=None):
    """讀取 JSON；損壞、缺檔與 schema 問題都指出檔名及欄位。"""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise RuntimeConfigError(f"{path}：檔案不存在") from error
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise RuntimeConfigError(
            f"{path}:{error.lineno}:{error.colno}：JSON 損壞：{error.msg}"
        ) from error
    if schema_path:
        schema = load_json(schema_path)
        problems = validate_schema(data, schema)
        if problems:
            raise RuntimeConfigError(f"{path}：格式不合法\n" + "\n".join(problems))
    return data


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json_candidate(path, data):
    """既有候選也可能已被使用者修改；內容不同就遞增尾碼，絕不覆寫。"""
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    candidate = path
    index = 2
    while candidate.exists() and candidate.read_text(encoding="utf-8") != content:
        candidate = Path(f"{path}.{index}")
        index += 1
    if not candidate.exists():
        candidate.write_text(content, encoding="utf-8")
    return candidate


def write_text_candidate(path, content):
    """文字候選也遵守不覆寫原檔與既有候選的規則。"""
    candidate = path
    index = 2
    while candidate.exists() and candidate.read_text(encoding="utf-8") != content:
        candidate = Path(f"{path}.{index}")
        index += 1
    if not candidate.exists():
        candidate.write_text(content, encoding="utf-8")
    return candidate


def runtime_root(root):
    return root / RUNTIME_REL


def load_registry(root):
    base = runtime_root(root)
    tasks = load_json(base / "task_profiles.json", base / "task_profiles.schema.json")
    adapters = {}
    schema = base / "execution_profiles.schema.json"
    for path in sorted((base / "adapters").glob("*.json")):
        manifest = load_json(path, schema)
        profile_id = manifest["id"]
        if profile_id in adapters:
            raise RuntimeConfigError(f"{path}:$.id：重複的 execution profile {profile_id!r}")
        adapters[profile_id] = manifest
    if not adapters:
        raise RuntimeConfigError(f"{base / 'adapters'}：找不到 execution profile manifest")
    capabilities = set(tasks["capabilities"])
    for profile_id, manifest in adapters.items():
        unknown = sorted(set(manifest["capabilities"]) - capabilities)
        if unknown:
            raise RuntimeConfigError(
                f"{base / 'adapters' / (profile_id + '.json')}:$.capabilities：未知能力 {unknown}"
            )
    profile_ids = {profile["id"] for profile in tasks["profiles"]}
    for task_type, profile_id in tasks["task_type_defaults"].items():
        if profile_id is not None and profile_id not in profile_ids:
            raise RuntimeConfigError(
                f"{base / 'task_profiles.json'}:$.task_type_defaults.{task_type}："
                f"引用未知 task profile {profile_id!r}"
            )
    return tasks, adapters


def xdg_state_path(env=None):
    env = os.environ if env is None else env
    home = Path(env.get("HOME", str(Path.home())))
    state_home = Path(env.get("XDG_STATE_HOME", home / ".local/state"))
    return state_home / "agent-team-kit/agent-runtime.json"


def empty_state():
    return {"schema_version": SCHEMA_VERSION, "profiles": {}, "integrations": {}}


def load_state(root, env=None):
    path = xdg_state_path(env)
    if not path.exists():
        return empty_state(), path
    schema = runtime_root(root) / "runtime_state.schema.json"
    state = load_json(path, schema)
    state.setdefault("integrations", {})
    return state, path


def load_policy(root):
    path = root / POLICY_REL
    schema = runtime_root(root) / "project_policy.schema.json"
    return load_json(path, schema)


def load_local_override(root):
    path = root / LOCAL_OVERRIDE_REL
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION}
    schema = runtime_root(root) / "local_override.schema.json"
    return load_json(path, schema)


def effective_policy(root):
    """合併版控政策與本機 override；本機層不能改 project identity。"""
    tasks, adapters = load_registry(root)
    policy = load_policy(root)
    override = load_local_override(root)
    _validate_profile_lists(override, adapters, tasks)
    result = dict(policy)
    enabled = override.get("enabled_profiles", result["enabled_profiles"])
    disabled = set(override.get("disabled_profiles", []))
    unknown_disabled = sorted(disabled - set(adapters))
    if unknown_disabled:
        raise RuntimeConfigError(
            f"{root / LOCAL_OVERRIDE_REL}:$.disabled_profiles："
            f"未知 execution profile {unknown_disabled}"
        )
    result["enabled_profiles"] = [item for item in enabled if item not in disabled]
    for key in ("preferred_profiles", "default_data_class", "cloud_policy", "connector_policy"):
        if key in override:
            result[key] = override[key]
    return result


def _git_common_dir(root):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return Path(result.stdout.strip()).resolve()


def project_identity(root):
    """有政策用 portable ID；初始化前則讓同一 git repo 的 worktree 得到同一 ID。"""
    policy_path = root / POLICY_REL
    if policy_path.exists():
        return load_policy(root)["project_id"]
    source = _git_common_dir(root) or root.resolve()
    return hashlib.sha256(str(source).encode()).hexdigest()[:32]


def _safe_summary(value):
    """狀態只收短摘要；拒收常見憑證形狀，不保存完整 stdout 或環境。"""
    text = " ".join(str(value).split())[:160]
    secret = re.compile(
        r"(?i)(token|password|cookie|secret|private[_ -]?key|authorization)\s*[:=]"
    )
    if secret.search(text):
        raise RuntimeConfigError("evidence summary 疑似含 credential；請只寫錯誤分類與短摘要")
    return text


def _error_class(text):
    """把命令錯誤壓成穩定分類；原始 stderr／stdout 不寫進 state。"""
    lowered = text.lower()
    patterns = (
        ("quota", ("quota", "rate limit", "usage limit", "insufficient credits")),
        ("permission", ("permission denied", "forbidden", "status 403", "http 403")),
        ("auth", ("unauthorized", "not logged in", "login required", "status 401", "http 401")),
        ("network", ("network", "dns", "connection refused", "connection reset", "timed out")),
    )
    for category, needles in patterns:
        if any(needle in lowered for needle in needles):
            return category
    return "command_failed"


def _probe_record(status, kind, summary, now, ttl_seconds, error_class=None):
    checked = now.astimezone(timezone.utc).replace(microsecond=0)
    return {
        "status": status,
        "checked_at": checked.isoformat(),
        "expires_at": (checked + timedelta(seconds=ttl_seconds)).isoformat(),
        "evidence": {"kind": kind, "summary": _safe_summary(summary)},
        "error_class": error_class,
    }


def run_probe(definition, ttl_seconds, now, root, env=None, timeout=PROBE_TIMEOUT_SECONDS):
    """執行一個無副作用 probe；回傳可安全寫入 state 的摘要，不含完整命令輸出。"""
    if definition.get("manual"):
        return _probe_record(
            "unknown",
            "manual_confirmation_required",
            definition["summary"],
            now,
            ttl_seconds,
        )
    command = definition["command"]
    try:
        result = subprocess.run(
            command,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return _probe_record(
            "unavailable",
            "command_probe",
            f"{command[0]} 未安裝或不在 PATH",
            now,
            ttl_seconds,
            "not_installed",
        )
    except subprocess.TimeoutExpired:
        return _probe_record(
            "unavailable",
            "command_probe",
            f"{command[0]} probe 超過 {timeout:g} 秒",
            now,
            ttl_seconds,
            "timeout",
        )
    combined = f"{result.stdout}\n{result.stderr}"
    success_returncodes = definition.get("success_returncodes", [0])
    if result.returncode not in success_returncodes:
        category = _error_class(combined)
        return _probe_record(
            "unavailable",
            "command_probe",
            f"{definition['summary']}失敗（{category}）",
            now,
            ttl_seconds,
            category,
        )
    marker = definition.get("marker")
    if marker and marker not in combined:
        return _probe_record(
            "unavailable",
            "command_probe",
            f"{definition['summary']}但缺少預期標記",
            now,
            ttl_seconds,
            "capability_mismatch",
        )
    return _probe_record(
        "verified",
        "command_probe",
        definition["summary"],
        now,
        ttl_seconds,
    )


def _is_fresh(record, now):
    if not record:
        return False
    try:
        return datetime.fromisoformat(record["expires_at"]) > now.astimezone(timezone.utc)
    except (KeyError, TypeError, ValueError):
        return False


def _aggregate_profile(profile_id, probes, now):
    """保留各 probe 後再彙總；metadata 與功能矛盾時明確標 degraded。"""
    install = probes.get("install", {})
    auth = probes.get("auth", {})
    functional = probes.get("functional", {})
    statuses = {key: value.get("status") for key, value in probes.items()}
    if functional.get("status") == "verified" and auth.get("status") == "unavailable":
        status, error = "degraded", "evidence_conflict"
        summary = f"{profile_id} 功能探針成功，但 auth metadata 失敗"
    elif install.get("status") == "unavailable":
        status, error = "unavailable", install.get("error_class")
        summary = f"{profile_id} 安裝探針失敗"
    elif functional.get("status") == "verified":
        status, error = "verified", None
        summary = f"{profile_id} 功能探針已驗證"
    elif any(value == "degraded" for value in statuses.values()):
        status, error = "degraded", "partial_failure"
        summary = f"{profile_id} 僅部分能力可用"
    elif any(value == "unavailable" for value in statuses.values()):
        failed = next(value for value in probes.values() if value.get("status") == "unavailable")
        status, error = "unavailable", failed.get("error_class")
        summary = f"{profile_id} probe 失敗"
    else:
        status, error = "unknown", None
        summary = f"{profile_id} 尚無有效功能探針"
    expirations = [
        datetime.fromisoformat(value["expires_at"])
        for value in probes.values()
        if value.get("expires_at")
    ]
    expires = min(expirations) if expirations else now.astimezone(timezone.utc)
    checked = now.astimezone(timezone.utc).replace(microsecond=0)
    return {
        "status": status,
        "checked_at": checked.isoformat(),
        "expires_at": expires.isoformat(),
        "evidence": {"kind": "probe_aggregate", "summary": _safe_summary(summary)},
        "error_class": error,
        "disabled_until": None,
        "probes": probes,
    }


def _manual_record(status, summary, now, ttl_seconds):
    if status not in STATUSES:
        raise RuntimeConfigError(f"人工確認狀態必須是 {sorted(STATUSES)}，收到 {status!r}")
    return _probe_record(
        status,
        "manual_confirmation",
        summary,
        now,
        ttl_seconds,
        None if status in {"verified", "unknown"} else "manual_status",
    )


def _parse_assignments(values, label):
    result = {}
    for value in values:
        if "=" not in value:
            raise RuntimeConfigError(f"{label}：格式應為 ID=STATUS，收到 {value!r}")
        key, status = value.split("=", 1)
        if not key or status not in STATUSES:
            raise RuntimeConfigError(f"{label}：格式應為 ID={sorted(STATUSES)}")
        result[key] = status
    return result


def _verified_entry(profile, now):
    ttl = profile["ttl_seconds"]["functional"]
    checked = now.astimezone(timezone.utc).replace(microsecond=0)
    return {
        "status": "verified",
        "checked_at": checked.isoformat(),
        "expires_at": (checked + timedelta(seconds=ttl)).isoformat(),
        "evidence": {
            "kind": "init_user_confirmation",
            "summary": _safe_summary("使用者於 init 確認可完成本機開發"),
        },
        "error_class": None,
        "disabled_until": None,
    }


def _read_init_config(path):
    data = load_json(path)
    allowed = {
        "schema_version",
        "project_name",
        "enabled_profiles",
        "preferred_profiles",
        "verified_profiles",
        "default_data_class",
        "cloud_policy",
        "connector_policy",
    }
    for key in sorted(set(data) - allowed):
        raise RuntimeConfigError(f"{path}:$.{key}：未知欄位")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeConfigError(
            f"{path}:$.schema_version：不支援 {data.get('schema_version')!r}"
        )
    return data


def _candidate_entry_files(root):
    created = []
    for name in ENTRY_TEMPLATES:
        target = root / name
        template = root / ".agent/templates" / name
        if target.exists() or not template.exists():
            continue
        candidate = root / f"{name}.new"
        content = template.read_text(encoding="utf-8")
        if candidate.exists() and candidate.read_text(encoding="utf-8") != content:
            index = 2
            while (next_candidate := root / f"{name}.new.{index}").exists():
                index += 1
            candidate = next_candidate
        if not candidate.exists():
            candidate.write_text(content, encoding="utf-8")
        created.append(candidate.name)
    return created


def _migration_sources(root, common_source=None):
    """產生雙入口的期望內容；既有規則優先於通用模板。"""
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"
    templates = root / ".agent/templates"
    if common_source:
        common = common_source.read_text(encoding="utf-8")
        common_origin = common_source
    elif agents.exists():
        common = agents.read_text(encoding="utf-8")
        common_origin = agents
    elif claude.exists():
        common = claude.read_text(encoding="utf-8")
        common_origin = claude
    else:
        common_origin = templates / "AGENTS.md"
        common = common_origin.read_text(encoding="utf-8")
    claude_origin = templates / "CLAUDE.md"
    return {
        agents: (common, common_origin),
        claude: (claude_origin.read_text(encoding="utf-8"), claude_origin),
    }


def _unified_diff(path, before, after):
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=str(path),
            tofile=f"{path}.new",
        )
    )


def migrate_runtime(args):
    """預覽或寫出安全候選；永不直接覆寫既有入口。"""
    root = args.root.resolve()
    results = []
    for target, (desired, source) in _migration_sources(root, args.common_source).items():
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        changed = current != desired
        candidate = None
        if changed and not args.dry_run:
            candidate = write_text_candidate(Path(f"{target}.new"), desired)
        results.append(
            {
                "target": str(target),
                "source": str(source),
                "changed": changed,
                "candidate": str(candidate) if candidate else None,
                "diff": _unified_diff(target, current, desired) if changed else "",
            }
        )
    output = {"dry_run": args.dry_run, "entries": results}
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        mode = "預覽" if args.dry_run else "候選已產生"
        print(f"✅ migrate {mode}；原始入口未覆寫")
        for item in results:
            if not item["changed"]:
                print(f"   已一致：{item['target']}")
                continue
            destination = item["candidate"] or f"{item['target']}.new（預覽）"
            print(f"   來源：{item['source']}")
            print(f"   候選：{destination}")
            print(item["diff"], end="")
    return output


def _choose_interactively(adapters, input_fn=input):
    local = [item for item in adapters.values() if item["execution_location"] == "local"]
    print("請選擇至少一個已確認可完成本機開發的 execution profile：")
    for profile in local:
        print(f"  - {profile['id']}: {profile['title']}")
    answer = input_fn("profile ID（多個用逗號分隔）：").strip()
    return [item.strip() for item in answer.split(",") if item.strip()]


def _validate_profile_lists(config, adapters, tasks):
    for key in ("enabled_profiles", "preferred_profiles", "verified_profiles"):
        unknown = sorted(set(config.get(key, [])) - set(adapters))
        if unknown:
            raise RuntimeConfigError(f"init:$.{key}：未知 execution profile {unknown}")
    unknown_data = config.get("default_data_class")
    if unknown_data is not None and unknown_data not in tasks["data_classes"]:
        raise RuntimeConfigError(f"init:$.default_data_class：未知資料級別 {unknown_data!r}")
    for key in ("cloud_policy", "connector_policy"):
        if key in config and config[key] not in POLICIES:
            raise RuntimeConfigError(f"init:$.{key}：必須是 {sorted(POLICIES)}")


def _has_verified_local_development(state, enabled, adapters, tasks, now):
    required = next(
        set(item["required_capabilities"])
        for item in tasks["profiles"]
        if item["id"] == "implementation_local"
    )
    for profile_id in enabled:
        manifest = adapters[profile_id]
        item = state["profiles"].get(profile_id, {})
        expires = item.get("expires_at")
        try:
            fresh = expires and datetime.fromisoformat(expires) > now.astimezone(timezone.utc)
        except ValueError:
            fresh = False
        if (
            manifest["execution_location"] == "local"
            and required <= set(manifest["capabilities"])
            and item.get("status") == "verified"
            and fresh
        ):
            return True
    return False


def init_runtime(args, input_fn=input, env=None, now=None):
    root = args.root.resolve()
    tasks, adapters = load_registry(root)
    config = {"schema_version": SCHEMA_VERSION}
    if args.config:
        config.update(_read_init_config(args.config))
    for key, value in (
        ("project_name", args.project_name),
        ("default_data_class", args.default_data_class),
        ("cloud_policy", args.cloud_policy),
        ("connector_policy", args.connector_policy),
    ):
        if value is not None:
            config[key] = value
    for key, value in (
        ("enabled_profiles", args.enable_profile),
        ("preferred_profiles", args.prefer_profile),
        ("verified_profiles", args.verified_profile),
    ):
        if value:
            config[key] = value
    _validate_profile_lists(config, adapters, tasks)

    state, state_path = load_state(root, env)
    unknown_state = sorted(set(state["profiles"]) - set(adapters))
    if unknown_state:
        raise RuntimeConfigError(
            f"{state_path}:$.profiles：未知 execution profile {unknown_state}"
        )
    now = now or datetime.now(timezone.utc)
    verified = list(config.get("verified_profiles", []))
    existing_policy = (root / POLICY_REL).exists()
    if existing_policy:
        base = load_policy(root)
    else:
        base = {
            "schema_version": SCHEMA_VERSION,
            "project_id": uuid.uuid4().hex,
            "project_name": root.name,
            "enabled_profiles": list(adapters),
            "preferred_profiles": [],
            "default_data_class": "internal",
            "cloud_policy": "conditional",
            "connector_policy": "conditional",
        }
    desired = dict(base)
    for key in (
        "project_name",
        "enabled_profiles",
        "preferred_profiles",
        "default_data_class",
        "cloud_policy",
        "connector_policy",
    ):
        if key in config:
            desired[key] = config[key]
    _validate_profile_lists(desired, adapters, tasks)

    if not verified and not _has_verified_local_development(
        state, desired["enabled_profiles"], adapters, tasks, now
    ):
        if args.non_interactive:
            raise RuntimeConfigError(
                "init：至少要有一個本機開發 profile verified；"
                "請加 --verified-profile 或在設定檔提供 verified_profiles"
            )
        verified = _choose_interactively(adapters, input_fn)
        config["verified_profiles"] = verified
        _validate_profile_lists(config, adapters, tasks)

    for profile_id in verified:
        manifest = adapters[profile_id]
        if manifest["execution_location"] != "local":
            raise RuntimeConfigError(f"init:$.verified_profiles：{profile_id!r} 不是本機 profile")
        state["profiles"][profile_id] = _verified_entry(manifest, now)

    if not _has_verified_local_development(
        state, desired["enabled_profiles"], adapters, tasks, now
    ):
        raise RuntimeConfigError("init：已確認的 profile 無法滿足 implementation_local 的硬性能力")

    policy_path = root / POLICY_REL
    candidate = None
    if existing_policy and desired != base:
        candidate = write_json_candidate(Path(str(policy_path) + ".new"), desired)
    elif not existing_policy:
        write_json(policy_path, desired)
    write_json(state_path, state)
    entry_candidates = _candidate_entry_files(root)
    result = {
        "project_id": base["project_id"],
        "policy": str(policy_path),
        "policy_candidate": str(candidate) if candidate else None,
        "state": str(state_path),
        "verified_profiles": sorted(
            key for key, item in state["profiles"].items() if item["status"] == "verified"
        ),
        "entry_candidates": entry_candidates,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"✅ runtime 初始化完成：{result['project_id']}")
        print(f"   本機狀態：{state_path}")
        if candidate:
            print(f"   政策有差異，候選寫入：{candidate}")
        for name in entry_candidates:
            print(f"   入口不存在，候選寫入：{name}")
    return result


def _select_profiles(args, policy, adapters):
    selected = args.profile or policy["enabled_profiles"]
    unknown = sorted(set(selected) - set(adapters))
    if unknown:
        raise RuntimeConfigError(f"{args.command}:$.profile：未知 execution profile {unknown}")
    return selected


def _probe_should_run(existing, now, force, explicitly_selected):
    if explicitly_selected or force:
        return True
    return not _is_fresh(existing, now)


def _refresh_profile(
    manifest,
    previous,
    now,
    root,
    env,
    online,
    force,
    requested_probes,
    timeout,
):
    probes = dict(previous.get("probes", {}))
    for stage in ("install", "auth", "functional"):
        probe_id = manifest["probes"][stage]
        if requested_probes and probe_id not in requested_probes:
            continue
        definition = PROBE_DEFINITIONS.get(probe_id)
        if definition is None:
            raise RuntimeConfigError(
                f"adapter {manifest['id']}:$.probes.{stage}：未知 probe ID {probe_id!r}"
            )
        existing = probes.get(stage)
        if definition.get("online") and not online:
            if existing is None:
                probes[stage] = _probe_record(
                    "unknown",
                    "offline_skipped",
                    f"{probe_id} 需要 online read，這次未執行",
                    now,
                    0,
                )
            continue
        explicit = probe_id in requested_probes
        if not _probe_should_run(existing, now, force, explicit):
            continue
        probes[stage] = run_probe(
            definition,
            manifest["ttl_seconds"][stage],
            now,
            root,
            env,
            timeout,
        )
    return _aggregate_profile(manifest["id"], probes, now)


def _refresh_integrations(previous, now, root, env, online, force, requested, timeout):
    result = dict(previous)
    for integration_id, definition in GITHUB_INTEGRATIONS.items():
        if requested and integration_id not in requested:
            continue
        existing = result.get(integration_id)
        if definition.get("online") and not online:
            if existing is None:
                result[integration_id] = _probe_record(
                    "unknown",
                    "offline_skipped",
                    f"{integration_id} 需要 online read，這次未執行",
                    now,
                    0,
                )
            continue
        if not _probe_should_run(existing, now, force, integration_id in requested):
            continue
        result[integration_id] = run_probe(
            definition,
            definition["ttl_seconds"],
            now,
            root,
            env,
            timeout,
        )
    return result


def health_runtime(args, env=None, now=None, timeout=PROBE_TIMEOUT_SECONDS):
    """doctor／refresh 共用引擎；兩者差在是否強制重跑已在 TTL 內的 probe。"""
    root = args.root.resolve()
    tasks, adapters = load_registry(root)
    del tasks  # 這張只驗 execution profiles；route 才會使用 task profiles。
    policy = effective_policy(root)
    state, state_path = load_state(root, env)
    now = now or datetime.now(timezone.utc)
    selected = _select_profiles(args, policy, adapters)
    requested = set(args.probe)
    known_probe_ids = {
        probe_id for manifest in adapters.values() for probe_id in manifest["probes"].values()
    }
    unknown_probes = sorted(requested - known_probe_ids)
    if unknown_probes:
        raise RuntimeConfigError(f"{args.command}:$.probe：未知 probe ID {unknown_probes}")
    force = args.command == "doctor" or args.force
    for profile_id in selected:
        previous = state["profiles"].get(profile_id, {})
        state["profiles"][profile_id] = _refresh_profile(
            adapters[profile_id],
            previous,
            now,
            root,
            env,
            args.online,
            force,
            requested,
            timeout,
        )

    manual_profiles = _parse_assignments(args.manual_profile, "--manual-profile")
    for profile_id, status in manual_profiles.items():
        if profile_id not in adapters:
            raise RuntimeConfigError(f"--manual-profile：未知 execution profile {profile_id!r}")
        ttl = adapters[profile_id]["ttl_seconds"]["functional"]
        record = _manual_record(status, f"使用者人工確認 {profile_id}", now, ttl)
        previous = state["profiles"].get(profile_id, {})
        state["profiles"][profile_id] = {
            **record,
            "disabled_until": previous.get("disabled_until"),
            "probes": previous.get("probes", {}),
        }

    requested_integrations = set(args.integration)
    unknown_integrations = sorted(requested_integrations - set(GITHUB_INTEGRATIONS))
    if unknown_integrations:
        raise RuntimeConfigError(
            f"{args.command}:$.integration：未知 GitHub integration {unknown_integrations}"
        )
    state["integrations"] = _refresh_integrations(
        state.get("integrations", {}),
        now,
        root,
        env,
        args.online,
        force,
        requested_integrations,
        timeout,
    )
    manual_integrations = _parse_assignments(args.manual_integration, "--manual-integration")
    for integration_id, status in manual_integrations.items():
        if integration_id not in GITHUB_INTEGRATIONS:
            raise RuntimeConfigError(f"--manual-integration：未知 integration {integration_id!r}")
        definition = GITHUB_INTEGRATIONS[integration_id]
        state["integrations"][integration_id] = _manual_record(
            status,
            f"使用者人工確認 {integration_id}",
            now,
            definition["ttl_seconds"],
        )

    write_json(state_path, state)
    output = {
        "project_id": policy["project_id"],
        "mode": "online-read" if args.online else "offline",
        "profiles": {profile_id: state["profiles"][profile_id] for profile_id in selected},
        "integrations": state["integrations"],
        "state": str(state_path),
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"agent runtime {args.command}（{output['mode']}）")
        for profile_id, item in output["profiles"].items():
            print(f"  {item['status']:11} {profile_id} — {item['evidence']['summary']}")
        print("GitHub／外部整合：")
        for integration_id, item in output["integrations"].items():
            print(f"  {item['status']:11} {integration_id} — {item['evidence']['summary']}")
    return output


def _add_health_arguments(command):
    network = command.add_mutually_exclusive_group()
    network.add_argument("--online", action="store_true", help="允許無外部寫入的 online read probe")
    network.add_argument(
        "--offline",
        action="store_false",
        dest="online",
        help="只跑零網路 probe（預設）",
    )
    command.set_defaults(online=False)
    command.add_argument("--profile", action="append", default=[])
    command.add_argument("--probe", action="append", default=[])
    command.add_argument("--integration", action="append", default=[])
    command.add_argument("--manual-profile", action="append", default=[], metavar="ID=STATUS")
    command.add_argument("--manual-integration", action="append", default=[], metavar="ID=STATUS")
    command.add_argument("--json", action="store_true")


def _profile_by_id(tasks, profile_id):
    for profile in tasks["profiles"]:
        if profile["id"] == profile_id:
            return profile
    raise RuntimeConfigError(f"route:$.task_profile：未知 task profile {profile_id!r}")


def _markdown_field(text, label):
    match = re.search(rf"^\*\*[^\n]*{re.escape(label)}:\*\*\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _empty_runtime_value(value):
    return value is None or value.strip() in {"", "-", "—", "–", "None", "N/A", "TBD"}


def parse_execution_override(value, location="task"):
    if _empty_runtime_value(value):
        return None
    result = {}
    for part in value.split(";"):
        if "=" not in part:
            raise RuntimeConfigError(f"{location}:Execution Override：每段必須是 key=value")
        key, item = (piece.strip() for piece in part.split("=", 1))
        if key not in {"profile", "scope", "expires"}:
            raise RuntimeConfigError(f"{location}:Execution Override：未知欄位 {key!r}")
        result[key] = item
    if "profile" not in result:
        raise RuntimeConfigError(f"{location}:Execution Override：缺少 profile")
    result.setdefault("scope", "single")
    if result["scope"] not in {"single", "round", "project"}:
        raise RuntimeConfigError(
            f"{location}:Execution Override：scope 必須是 single／round／project"
        )
    if result["scope"] != "single" and not result.get("expires"):
        raise RuntimeConfigError(
            f"{location}:Execution Override：round／project 必須提供 expires"
        )
    return result


def parse_task_routing(path, tasks):
    """讀新欄位；舊工單沒有欄位時由 Task Type 的 registry mapping 提供預設。"""
    text = path.read_text(encoding="utf-8")
    task_type = _markdown_field(text, "任務類型 (Task Type)")
    explicit_profile = _markdown_field(text, TASK_RUNTIME_FIELDS["task_profile"])
    if _empty_runtime_value(explicit_profile):
        if task_type not in tasks["task_type_defaults"]:
            raise RuntimeConfigError(f"{path}:Task Type：沒有預設 task profile：{task_type!r}")
        task_profile = tasks["task_type_defaults"][task_type]
        source = f"Task Type mapping：{task_type}"
    else:
        task_profile = explicit_profile
        source = "工單明示"
    if task_profile is None:
        raise RuntimeConfigError(f"{path}:Task Type {task_type!r} 是人工工作，不進 agent route")
    _profile_by_id(tasks, task_profile)
    capabilities_value = _markdown_field(text, TASK_RUNTIME_FIELDS["required_capabilities"])
    capabilities = []
    if not _empty_runtime_value(capabilities_value):
        capabilities = [item.strip() for item in capabilities_value.split(",") if item.strip()]
    unknown = sorted(set(capabilities) - set(tasks["capabilities"]))
    if unknown:
        raise RuntimeConfigError(f"{path}:Required Capabilities：未知能力 {unknown}")
    data_class = _markdown_field(text, TASK_RUNTIME_FIELDS["data_class"])
    if _empty_runtime_value(data_class):
        data_class = None
    elif data_class not in tasks["data_classes"]:
        raise RuntimeConfigError(f"{path}:Data Class：未知資料級別 {data_class!r}")
    override_value = _markdown_field(text, TASK_RUNTIME_FIELDS["execution_override"])
    override = parse_execution_override(override_value, str(path))
    return {
        "task_type": task_type,
        "task_profile": task_profile,
        "task_profile_source": source,
        "required_capabilities": capabilities,
        "data_class": data_class,
        "execution_override": override,
    }


def _effective_availability(item, now):
    if not item:
        return "unknown", "沒有本機 probe state"
    disabled = item.get("disabled_until")
    if disabled:
        try:
            if datetime.fromisoformat(disabled) > now.astimezone(timezone.utc):
                return "unavailable", f"使用者停用到 {disabled}"
        except ValueError:
            return "unavailable", "disabled_until 格式損壞"
    if not _is_fresh(item, now):
        return "unknown", f"cache 已於 {item.get('expires_at', '未知時間')} 到期"
    return item.get("status", "unknown"), item.get("evidence", {}).get("summary", "沒有摘要")


def _policy_allows(policy, data_class, data_classes):
    if policy == "forbid":
        return False
    if policy == "allow":
        return True
    # conditional：public／internal 可自動通過；sensitive／restricted 必須另有 allow。
    return data_classes.index(data_class) < data_classes.index("sensitive")


def _is_pure_local_read(required):
    side_effects = {
        "repo_write",
        "shell_execute",
        "test_execute",
        "external_connectors",
        "github_access",
        "visual_interaction",
        "long_running",
        "noninteractive",
    }
    return not (set(required) & side_effects)


def _score_candidate(manifest, task, availability, preferred):
    """簡單且可逐項解釋的層內分數；它永遠不讓已排除候選復活。"""
    details = []
    score = 100
    availability_score = {"verified": 30, "degraded": 10, "unknown": -20}[availability]
    score += availability_score
    details.append({"factor": "availability", "delta": availability_score})
    if manifest["id"] in preferred:
        preference_score = max(1, 20 - preferred.index(manifest["id"]))
        score += preference_score
        details.append({"factor": "project_preference", "delta": preference_score})
    optional = len(set(task["optional_capabilities"]) & set(manifest["capabilities"]))
    score += optional
    details.append({"factor": "optional_capabilities", "delta": optional})
    # registry 尚未宣告可比較的實際價格／latency；誠實記 0，不用供應商印象偷排。
    details.extend(
        [
            {"factor": "cost_metadata_unknown", "delta": 0},
            {"factor": "latency_metadata_unknown", "delta": 0},
            {"factor": "context_metadata_unknown", "delta": 0},
        ]
    )
    return score, details


def route_decision(
    root,
    task_profile_id,
    data_class=None,
    required_overrides=None,
    override_profile=None,
    failed_profile=None,
    now=None,
    env=None,
):
    """純函數式路由核心：相同 registry／policy／state 輸入必定得到相同結果。"""
    tasks, adapters = load_registry(root)
    policy = effective_policy(root)
    state, _ = load_state(root, env)
    task = _profile_by_id(tasks, task_profile_id)
    now = now or datetime.now(timezone.utc)
    data_class = data_class or task["default_data_class"]
    if data_class not in tasks["data_classes"]:
        raise RuntimeConfigError(f"route:$.data_class：未知資料級別 {data_class!r}")
    required = list(dict.fromkeys([*task["required_capabilities"], *(required_overrides or [])]))
    unknown_capabilities = sorted(set(required) - set(tasks["capabilities"]))
    if unknown_capabilities:
        raise RuntimeConfigError(f"route:$.require_capability：未知能力 {unknown_capabilities}")
    preferred = policy["preferred_profiles"]
    candidates = []
    for profile_id in sorted(adapters):
        manifest = adapters[profile_id]
        excluded = []
        notes = []
        if profile_id not in policy["enabled_profiles"]:
            excluded.append("未在專案政策啟用")
        if profile_id == failed_profile:
            excluded.append("本次失效 profile 已停用並等待重新探測")
        missing = sorted(set(required) - set(manifest["capabilities"]))
        if missing:
            excluded.append(f"缺少硬性能力：{missing}")
        if manifest["execution_location"] == "cloud":
            if not _policy_allows(task["cloud_policy"], data_class, tasks["data_classes"]):
                excluded.append(f"task cloud policy={task['cloud_policy']} 不允許 {data_class}")
            if not _policy_allows(policy["cloud_policy"], data_class, tasks["data_classes"]):
                excluded.append(f"project cloud policy={policy['cloud_policy']} 不允許 {data_class}")
        if "external_connectors" in required:
            if not _policy_allows(task["connector_policy"], data_class, tasks["data_classes"]):
                excluded.append(f"task connector policy={task['connector_policy']} 不允許 {data_class}")
            if not _policy_allows(policy["connector_policy"], data_class, tasks["data_classes"]):
                excluded.append(f"project connector policy={policy['connector_policy']} 不允許 {data_class}")
        availability, availability_reason = _effective_availability(
            state["profiles"].get(profile_id), now
        )
        notes.append(f"availability={availability}：{availability_reason}")
        if availability == "unavailable":
            excluded.append("目前已確認 unavailable")
        elif availability == "unknown":
            allow_unknown = (
                manifest["execution_location"] == "local" and _is_pure_local_read(required)
            )
            if not allow_unknown:
                excluded.append("沒有 fresh verified／degraded 證據")
            else:
                notes.append("純本機唯讀任務依政策容許 unknown 候選，但會受分數懲罰")
        eligible = not excluded
        score = None
        score_details = []
        if eligible:
            score, score_details = _score_candidate(
                manifest, task, availability, preferred
            )
        candidates.append(
            {
                "id": profile_id,
                "eligible": eligible,
                "availability": availability,
                "score": score,
                "score_details": score_details,
                "excluded_reasons": excluded,
                "notes": notes,
            }
        )
    eligible = [item for item in candidates if item["eligible"]]
    eligible.sort(key=lambda item: (-item["score"], item["id"]))
    selected = eligible[0]["id"] if eligible else None
    override = None
    if override_profile:
        item = next((candidate for candidate in candidates if candidate["id"] == override_profile), None)
        if item is None:
            raise RuntimeConfigError(f"route:$.override_profile：未知 profile {override_profile!r}")
        if not item["eligible"]:
            raise RuntimeConfigError(
                f"route:$.override_profile：{override_profile!r} 不合格，"
                + "；".join(item["excluded_reasons"])
            )
        selected = override_profile
        override = {"profile": override_profile, "applied": True}
    return {
        "task_profile": task_profile_id,
        "data_class": data_class,
        "required_capabilities": required,
        "selected_profile": selected,
        "candidates": candidates,
        "override": override,
    }


def _handoff_from_args(args, selected_profile, required_capabilities):
    if not args.failed_profile:
        return None
    required = {
        "task_id": args.task_id,
        "branch": args.branch,
        "head": args.head,
        "failure_type": args.failure_type,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise RuntimeConfigError(
            "reroute：使用 --failed-profile 時還缺 " + "、".join(f"--{key.replace('_', '-')}" for key in missing)
        )
    auto_allowed = (
        args.allow_auto_read_handoff
        and not args.external_side_effects
        and selected_profile is not None
        and _is_pure_local_read(required_capabilities)
    )
    return {
        **required,
        "completed_ac": args.completed_ac,
        "pending_ac": args.pending_ac,
        "validations": args.validation,
        "failed_profile": args.failed_profile,
        "suggested_profile": selected_profile,
        "external_side_effects": args.external_side_effects,
        "auto_handoff_allowed": auto_allowed,
        "requires_user_confirmation": not auto_allowed,
    }


def _validate_override_args(args):
    if not args.override_profile:
        if args.override_scope != "single" or args.override_expires_at:
            raise RuntimeConfigError("route：override scope／到期條件需要同時提供 --override-profile")
        return None
    if args.override_scope != "single" and not args.override_expires_at:
        raise RuntimeConfigError(
            "route：round／project override 必須明示 --override-expires-at 或到期條件"
        )
    return {
        "profile": args.override_profile,
        "scope": args.override_scope,
        "expires_at": args.override_expires_at,
    }


def route_runtime(args, env=None, now=None):
    root = args.root.resolve()
    task_fields = None
    if args.task_file:
        tasks, _ = load_registry(root)
        task_path = args.task_file if args.task_file.is_absolute() else root / args.task_file
        task_fields = parse_task_routing(task_path, tasks)
        args.task_profile = task_fields["task_profile"]
        args.data_class = args.data_class or task_fields["data_class"]
        args.require_capability = [
            *task_fields["required_capabilities"],
            *args.require_capability,
        ]
        if task_fields["execution_override"] and not args.override_profile:
            task_override = task_fields["execution_override"]
            args.override_profile = task_override["profile"]
            args.override_scope = task_override["scope"]
            args.override_expires_at = task_override.get("expires")
    override = _validate_override_args(args)
    decision = route_decision(
        root,
        args.task_profile,
        data_class=args.data_class,
        required_overrides=args.require_capability,
        override_profile=args.override_profile,
        failed_profile=args.failed_profile,
        now=now,
        env=env,
    )
    if override:
        decision["override"] = {**override, "applied": True}
    decision["task_profile_source"] = (
        task_fields["task_profile_source"] if task_fields else "CLI 明示"
    )
    decision["task_file"] = str(args.task_file) if args.task_file else None
    decision["handoff"] = _handoff_from_args(
        args, decision["selected_profile"], decision["required_capabilities"]
    )
    if args.json:
        print(json.dumps(decision, ensure_ascii=False, indent=2))
    else:
        print(f"task profile：{decision['task_profile']}（{decision['data_class']}）")
        if args.explain:
            print(f"來源：{decision['task_profile_source']}")
        print(f"建議 execution profile：{decision['selected_profile'] or '無合格候選'}")
        for item in decision["candidates"]:
            if item["eligible"]:
                print(f"  ✅ {item['id']} score={item['score']} availability={item['availability']}")
            else:
                print(f"  ❌ {item['id']} — {'；'.join(item['excluded_reasons'])}")
    return decision


def explain_runtime(args, env=None, now=None):
    decision = route_decision(
        args.root.resolve(),
        args.task_profile,
        data_class=args.data_class,
        required_overrides=args.require_capability,
        now=now,
        env=env,
    )
    item = next(
        (candidate for candidate in decision["candidates"] if candidate["id"] == args.execution_profile),
        None,
    )
    if item is None:
        raise RuntimeConfigError(f"explain：未知 execution profile {args.execution_profile!r}")
    output = {
        "task_profile": decision["task_profile"],
        "data_class": decision["data_class"],
        "required_capabilities": decision["required_capabilities"],
        "execution_profile": item,
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"{item['id']}：{'合格' if item['eligible'] else '不合格'}")
        for reason in item["excluded_reasons"]:
            print(f"  排除：{reason}")
        for note in item["notes"]:
            print(f"  證據：{note}")
        for detail in item["score_details"]:
            print(f"  分數：{detail['factor']} {detail['delta']:+d}")
    return output


def build_parser():
    parser = argparse.ArgumentParser(description="跨代理 runtime 管理器")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help=argparse.SUPPRESS,
    )
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="建立共享政策與本機啟用狀態")
    init.add_argument("--non-interactive", action="store_true")
    init.add_argument("--config", type=Path)
    init.add_argument("--project-name")
    init.add_argument("--enable-profile", action="append", default=[])
    init.add_argument("--prefer-profile", action="append", default=[])
    init.add_argument("--verified-profile", action="append", default=[])
    init.add_argument("--default-data-class")
    init.add_argument("--cloud-policy", choices=sorted(POLICIES))
    init.add_argument("--connector-policy", choices=sorted(POLICIES))
    init.add_argument("--json", action="store_true")
    migrate = commands.add_parser("migrate", help="安全遷移既有 Claude／Codex 專案入口")
    migrate.add_argument("--dry-run", action="store_true", help="只顯示候選與差異，不寫檔")
    migrate.add_argument(
        "--common-source",
        type=Path,
        help="共同規則來源；省略時依序採用 AGENTS.md、CLAUDE.md、內建模板",
    )
    migrate.add_argument("--json", action="store_true")
    doctor = commands.add_parser("doctor", help="檢查安裝、設定與無副作用功能探針")
    _add_health_arguments(doctor)
    doctor.set_defaults(force=True)
    refresh = commands.add_parser("refresh", help="重跑過期或指定的探針")
    _add_health_arguments(refresh)
    refresh.add_argument("--force", action="store_true", help="忽略 TTL，重跑選定探針")
    route = commands.add_parser("route", help="依能力、政策與可用性選擇 execution profile")
    route_source = route.add_mutually_exclusive_group(required=True)
    route_source.add_argument("--task-profile")
    route_source.add_argument("--task-file", type=Path)
    route.add_argument("--data-class")
    route.add_argument("--require-capability", action="append", default=[])
    route.add_argument("--override-profile")
    route.add_argument("--override-scope", choices=["single", "round", "project"], default="single")
    route.add_argument("--override-expires-at")
    route.add_argument("--failed-profile")
    route.add_argument("--task-id")
    route.add_argument("--branch")
    route.add_argument("--head")
    route.add_argument("--completed-ac", action="append", default=[])
    route.add_argument("--pending-ac", action="append", default=[])
    route.add_argument("--validation", action="append", default=[])
    route.add_argument("--failure-type")
    route.add_argument("--external-side-effects", action="store_true")
    route.add_argument("--allow-auto-read-handoff", action="store_true")
    route.add_argument("--explain", action="store_true", help="顯示 task profile 的來源")
    route.add_argument("--json", action="store_true")
    explain = commands.add_parser("explain", help="解釋單一 execution profile 為何合格或被排除")
    explain.add_argument("--task-profile", required=True)
    explain.add_argument("--execution-profile", required=True)
    explain.add_argument("--data-class")
    explain.add_argument("--require-capability", action="append", default=[])
    explain.add_argument("--json", action="store_true")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init_runtime(args)
        elif args.command == "migrate":
            migrate_runtime(args)
        elif args.command in {"doctor", "refresh"}:
            health_runtime(args)
        elif args.command == "route":
            decision = route_runtime(args)
            if decision["selected_profile"] is None:
                return 3
        elif args.command == "explain":
            explain_runtime(args)
    except RuntimeConfigError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
