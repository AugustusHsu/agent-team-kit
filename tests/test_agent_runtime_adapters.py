"""跨代理入口與 execution profile adapters 的一致性。"""

import copy
import json
import re
from pathlib import Path


RUNTIME = ".agent/resources/agent_runtime"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_adapter(data: dict, schema: dict, capabilities: set[str]) -> list[str]:
    problems = []
    required = set(schema["required"])
    allowed = set(schema["properties"])
    for key in sorted(required - set(data)):
        problems.append(f"$.{key}：缺少必要欄位")
    for key in sorted(set(data) - allowed):
        problems.append(f"$.{key}：未知欄位")
    if data.get("schema_version") != schema["properties"]["schema_version"]["const"]:
        problems.append(f"$.schema_version：不支援 {data.get('schema_version')!r}")
    if data.get("execution_location") not in {"local", "cloud"}:
        problems.append("$.execution_location：必須是 local 或 cloud")

    listed = data.get("capabilities", [])
    for capability in listed:
        if capability not in capabilities:
            problems.append(f"$.capabilities：引用未知 capability {capability!r}")
    if len(listed) != len(set(listed)):
        problems.append("$.capabilities：不得重複")

    manual = data.get("manual_capabilities", [])
    for capability in manual:
        if capability not in listed:
            problems.append(f"$.manual_capabilities：{capability!r} 不在 capabilities")

    for group in ("probes", "ttl_seconds"):
        values = data.get(group, {})
        if set(values) != {"install", "auth", "functional"}:
            problems.append(f"$.{group}：必須剛好有 install／auth／functional")
    return problems


def test_五個初始_execution_profiles_符合_schema(kit_root: Path):
    root = kit_root / RUNTIME
    schema = _load(root / "execution_profiles.schema.json")
    tasks = _load(root / "task_profiles.json")
    capabilities = set(tasks["capabilities"])
    manifests = sorted((root / "adapters").glob("*.json"))
    assert [path.stem for path in manifests] == [
        "claude-code-cli",
        "codex-app-local",
        "codex-app-worktree",
        "codex-cli",
        "codex-cloud",
    ]
    ids = []
    for path in manifests:
        data = _load(path)
        ids.append(data["id"])
        assert not (problems := _validate_adapter(data, schema, capabilities)), (
            f"{path.name} 不合法：\n" + "\n".join(problems)
        )
    assert len(ids) == len(set(ids)), "execution profile ID 不得重複"


def test_第三家供應商只需新增_manifest(kit_root: Path):
    root = kit_root / RUNTIME
    schema = _load(root / "execution_profiles.schema.json")
    tasks = _load(root / "task_profiles.json")
    base = _load(root / "adapters/codex-cli.json")
    third_party = copy.deepcopy(base)
    third_party.update(id="future-agent-cli", provider="future-vendor", title="Future Agent CLI")
    assert not _validate_adapter(third_party, schema, set(tasks["capabilities"]))


def test_adapter_不含憑證_絕對路徑或跨供應商環境變數(kit_root: Path):
    root = kit_root / RUNTIME
    paths = [*(root / "adapters").glob("*.json"), kit_root / "AGENTS.md", kit_root / "CLAUDE.md"]
    secret_value = re.compile(
        r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|password|cookie)\s*[:=]\s*['\"]?[A-Za-z0-9]"
    )
    absolute_home = re.compile(r"(?:/home/|/Users/|[A-Za-z]:\\Users\\)")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert not secret_value.search(text), f"{path} 疑似含秘密值"
        assert not absolute_home.search(text), f"{path} 含個人家目錄絕對路徑"
    adapter_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "adapters").glob("*.json"))
    assert "ANTHROPIC_BASE_URL" not in adapter_text
    assert "OPENAI_API_KEY" not in adapter_text


def test_共同規則只在_agents_由_claude_匯入(kit_root: Path):
    agents = (kit_root / "AGENTS.md").read_text(encoding="utf-8")
    claude = (kit_root / "CLAUDE.md").read_text(encoding="utf-8")
    template_agents = (kit_root / ".agent/templates/AGENTS.md").read_text(encoding="utf-8")
    template_claude = (kit_root / ".agent/templates/CLAUDE.md").read_text(encoding="utf-8")

    assert claude.splitlines()[2] == "@AGENTS.md"
    assert template_claude.splitlines()[2] == "@AGENTS.md"
    required_fragments = [
        "工單分支上的 commit 直接做",
        "禁止 AI 署名 trailer",
        "docs/standards/agent_runtime.md",
        "§1.10 Commit 閘門",
        "§1.12 取證通道保真",
    ]
    for fragment in required_fragments:
        assert fragment in agents, f"AGENTS.md 缺共同規則：{fragment}"
        assert fragment in template_agents, f"AGENTS 模板缺共同規則：{fragment}"
    assert "工單分支上的 commit 直接做" not in claude, "CLAUDE.md 不得複製共同 commit 規則"
    assert "工單分支上的 commit 直接做" not in template_claude


def test_codex_cli_是基線而_app_能力需人工確認(kit_root: Path):
    root = kit_root / RUNTIME / "adapters"
    cli = _load(root / "codex-cli.json")
    app = _load(root / "codex-app-worktree.json")
    cloud = _load(root / "codex-cloud.json")
    assert cli["execution_location"] == "local"
    assert cli["manual_capabilities"] == []
    assert "isolated_workspace" in app["manual_capabilities"]
    assert cloud["execution_location"] == "cloud"
    assert "github_access" in cloud["manual_capabilities"]
