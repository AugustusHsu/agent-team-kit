"""check_versions.py 的階段一（自我驗證與一致性驗證）行為。

刻意只測階段一。階段二會連 DockerHub / PyPI / npm / GitHub API，在 CI 裡不可靠；
fixture 的 `source_type: local` 會讓階段二直接回 `UNSUPPORTED SOURCE`，不發任何網路請求。
"""

from pathlib import Path

from conftest import run_script

VALID = "docs/standards/third_party_versions.yaml"
BROKEN = "docs/standards/third_party_versions_broken.yaml"
INCONSISTENT = "docs/standards/third_party_versions_inconsistent.yaml"


def test_宣告與實體檔案相符時通過自我驗證(project: Path):
    result = run_script(project, "check_versions.py", "--config", VALID)
    assert "✅ [python-base-image] 檔案模式存在校驗 OK" in result.stdout
    assert "✅ [node-base-image] 檔案模式存在校驗 OK" in result.stdout
    assert "階段二" in result.stdout, "自我驗證通過後應繼續進入上游巡檢"


def test_不需網路即可完成(project: Path):
    """source_type 非已知來源時直接判為 UNSUPPORTED SOURCE，不觸發任何 HTTP 請求。"""
    result = run_script(project, "check_versions.py", "--config", VALID, timeout=20)
    assert "UNSUPPORTED SOURCE" in result.stdout
    assert result.returncode == 1  # 查詢失敗即視為不通過


def test_宣告版本與實體檔案不符時失敗(project: Path):
    result = run_script(project, "check_versions.py", "--config", BROKEN)
    assert result.returncode == 1
    assert "自我驗證失敗" in result.stdout
    assert "階段二" not in result.stdout, "階段一失敗就該中止，不應繼續巡檢上游"


def test_關聯項目版本不一致時失敗(project: Path):
    result = run_script(project, "check_versions.py", "--config", INCONSISTENT)
    assert result.returncode == 1
    assert "一致性驗證失敗" in result.stdout


def test_找不到宣告檔時給出明確訊息(project: Path):
    result = run_script(project, "check_versions.py", "--config", "docs/standards/nope.yaml")
    assert result.returncode == 1
    assert "找不到版本宣告檔" in result.stdout


def test_無_PyYAML_時的備用解析器結果一致(project: Path, kit_root: Path):
    """`parse_yaml_fallback()` 是沒裝 PyYAML 時的退路，解析結果必須與 PyYAML 相同。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "check_versions", kit_root / ".agent" / "scripts" / "check_versions.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    text = (project / VALID).read_text(encoding="utf-8")
    parsed = module.parse_yaml_fallback(text)

    entries = {e["name"]: e for e in parsed["versions"]}
    assert set(entries) == {"python-base-image", "node-base-image"}
    assert entries["python-base-image"]["current_version"] == "3.12.7"
    assert entries["python-base-image"]["source_type"] == "local"
    assert entries["python-base-image"]["declared_in"] == {
        "file": "devenv/Dockerfile",
        "pattern": "FROM python:{version}-slim",
    }
