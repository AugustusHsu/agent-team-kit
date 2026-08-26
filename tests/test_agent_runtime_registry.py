"""多代理 task profile registry 的資料契約。

這裡刻意不用 jsonschema 套件：kit 的出貨原則是標準函式庫即可驗證，
而本階段要守的是 registry 自己的結構與引用，不是實作完整 JSON Schema 引擎。
"""

import copy
import json
from pathlib import Path


REGISTRY = ".agent/resources/agent_runtime/task_profiles.json"
SCHEMA = ".agent/resources/agent_runtime/task_profiles.schema.json"


def _載入(kit_root: Path, rel: str):
    return json.loads((kit_root / rel).read_text(encoding="utf-8"))


def _驗證(data: dict, schema: dict) -> list[str]:
    """回傳可直接定位到 JSON 路徑的問題；空陣列代表通過。"""
    問題 = []
    根必要 = set(schema["required"])
    根允許 = set(schema["properties"])
    for key in sorted(根必要 - set(data)):
        問題.append(f"$.{key}：缺少必要欄位")
    for key in sorted(set(data) - 根允許):
        問題.append(f"$.{key}：未知欄位")
    if data.get("schema_version") != schema["properties"]["schema_version"]["const"]:
        問題.append(f"$.schema_version：不支援 {data.get('schema_version')!r}")

    capabilities = data.get("capabilities", {})
    if not isinstance(capabilities, dict) or not capabilities:
        問題.append("$.capabilities：必須是非空物件")
        capabilities = {}
    else:
        for key, description in capabilities.items():
            if not isinstance(description, str) or not description.strip():
                問題.append(f"$.capabilities.{key}：說明必須是非空字串")

    data_classes = data.get("data_classes", [])
    if not isinstance(data_classes, list) or not data_classes:
        問題.append("$.data_classes：必須是非空陣列")
        data_classes = []
    elif len(data_classes) != len(set(data_classes)):
        問題.append("$.data_classes：不得重複")

    profile_schema = schema["properties"]["profiles"]["items"]
    profile_required = set(profile_schema["required"])
    profile_allowed = set(profile_schema["properties"])
    policies = set(profile_schema["properties"]["cloud_policy"]["enum"])
    reasoning_classes = set(profile_schema["properties"]["reasoning_class"]["enum"])
    seen = set()

    profiles = data.get("profiles", [])
    if not isinstance(profiles, list) or not profiles:
        問題.append("$.profiles：必須是非空陣列")
        return 問題

    for index, profile in enumerate(profiles):
        path = f"$.profiles[{index}]"
        if not isinstance(profile, dict):
            問題.append(f"{path}：必須是物件")
            continue
        for key in sorted(profile_required - set(profile)):
            問題.append(f"{path}.{key}：缺少必要欄位")
        for key in sorted(set(profile) - profile_allowed):
            問題.append(f"{path}.{key}：未知欄位")

        profile_id = profile.get("id")
        if profile_id in seen:
            問題.append(f"{path}.id：重複的 profile ID {profile_id!r}")
        seen.add(profile_id)

        required = profile.get("required_capabilities", [])
        optional = profile.get("optional_capabilities", [])
        for key in [*required, *optional]:
            if key not in capabilities:
                問題.append(f"{path}：引用未知 capability {key!r}")
        overlap = sorted(set(required) & set(optional))
        if overlap:
            問題.append(f"{path}：必備與選配能力重複 {overlap}")
        if profile.get("default_data_class") not in data_classes:
            問題.append(f"{path}.default_data_class：引用未知資料級別")
        for key in ("cloud_policy", "connector_policy"):
            if profile.get(key) not in policies:
                問題.append(f"{path}.{key}：必須是 {sorted(policies)}")
        if profile.get("reasoning_class") not in reasoning_classes:
            問題.append(f"{path}.reasoning_class：必須是 {sorted(reasoning_classes)}")
    return 問題


def test_task_profile_registry_符合資料契約(kit_root: Path):
    data = _載入(kit_root, REGISTRY)
    schema = _載入(kit_root, SCHEMA)
    assert not (問題 := _驗證(data, schema)), "registry 不合法：\n" + "\n".join(問題)
    assert [profile["id"] for profile in data["profiles"]] == [
        "design_research",
        "implementation_local",
        "parallel_long_running",
        "review_security",
        "test_verification",
        "visual_interactive",
        "automation_batch",
        "external_integration",
    ]


def test_registry_未知欄位會指出_json_路徑(kit_root: Path):
    data = _載入(kit_root, REGISTRY)
    schema = _載入(kit_root, SCHEMA)
    data["profiles"][0]["capabilites"] = []
    assert "$.profiles[0].capabilites：未知欄位" in _驗證(data, schema)


def test_registry_重複_profile_id_會失敗(kit_root: Path):
    data = _載入(kit_root, REGISTRY)
    schema = _載入(kit_root, SCHEMA)
    duplicate = copy.deepcopy(data["profiles"][0])
    data["profiles"].append(duplicate)
    problems = _驗證(data, schema)
    assert any("重複的 profile ID 'design_research'" in problem for problem in problems)


def test_registry_未知能力會失敗(kit_root: Path):
    data = _載入(kit_root, REGISTRY)
    schema = _載入(kit_root, SCHEMA)
    data["profiles"][0]["required_capabilities"].append("telepathy")
    problems = _驗證(data, schema)
    assert any("引用未知 capability 'telepathy'" in problem for problem in problems)


def test_registry_新增輪廓只需新增資料(kit_root: Path):
    """擴充點是 registry record，不是 Python enum 或供應商分支。"""
    data = _載入(kit_root, REGISTRY)
    schema = _載入(kit_root, SCHEMA)
    added = copy.deepcopy(data["profiles"][0])
    added.update(id="documentation_only", title="純文件", description="只讀寫專案文件")
    data["profiles"].append(added)
    assert not (問題 := _驗證(data, schema)), "新增資料後不該要求改程式：\n" + "\n".join(問題)


def test_task_profile_不承載供應商名稱(kit_root: Path):
    data = _載入(kit_root, REGISTRY)
    serialized = json.dumps(data, ensure_ascii=False).lower()
    for vendor in ("claude", "anthropic", "codex", "openai"):
        assert vendor not in serialized, f"task profile registry 不得綁定供應商：{vendor}"
