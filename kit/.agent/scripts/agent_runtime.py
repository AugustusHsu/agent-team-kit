#!/usr/bin/env python3
"""跨 Claude／Codex 的本機 runtime 管理器。

037 先提供共用載入、驗證、狀態分層與 ``init``。後續工單在同一支腳本加入
``doctor``／``refresh``／``route``／``explain``／``migrate``，不得另造第二套狀態格式。

只使用標準函式庫；任何已安裝 kit 的專案都能直接執行。
"""

import argparse
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
    return tasks, adapters


def xdg_state_path(env=None):
    env = os.environ if env is None else env
    home = Path(env.get("HOME", str(Path.home())))
    state_home = Path(env.get("XDG_STATE_HOME", home / ".local/state"))
    return state_home / "agent-team-kit/agent-runtime.json"


def empty_state():
    return {"schema_version": SCHEMA_VERSION, "profiles": {}}


def load_state(root, env=None):
    path = xdg_state_path(env)
    if not path.exists():
        return empty_state(), path
    schema = runtime_root(root) / "runtime_state.schema.json"
    return load_json(path, schema), path


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
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init_runtime(args)
    except RuntimeConfigError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
