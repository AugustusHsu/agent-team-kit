"""scan_backlog.py 的解析與分類行為。"""

import json
from pathlib import Path

import pytest

from conftest import run_script


@pytest.fixture(scope="module")
def scanned(project: Path):
    result = run_script(project, "scan_backlog.py", "--format", "json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _flatten(module: dict) -> dict:
    return {t["task_id"]: t for items in module["classified"].values() for t in items}


def test_底線開頭的檔案不被當成工單(scanned):
    """`_INDEX.md` 是索引不是工單；fixture 裡共 8 個 .md，只有 7 張算數。"""
    assert scanned["example_module"]["total"] == 7
    assert "_INDEX" not in _flatten(scanned["example_module"])


def test_metadata_欄位解析正確(scanned):
    task = _flatten(scanned["example_module"])["ABC-DEV-BE-001"]
    assert task["title"] == "實作角色與權限資料表"
    assert task["parent_id"] == "ABC-DOC-EPIC-001"
    assert task["assignee"] == "backend-developer"
    assert task["status"] == "In Progress"
    assert task["created"] == "2026-01-06T10:00+08:00"


def test_標題格式不符時回退為檔名(scanned):
    """H1 解析失敗不該讓整張工單消失，而是以檔名當 Task ID。"""
    task = _flatten(scanned["example_module"])["ABC-DEV-BE-003"]
    assert task["title"] == "(標題解析失敗)"


def test_狀態附註說明會被正規化(scanned):
    """`Canceled (改由 ... 統一涵蓋)` 應正規化為 `Canceled`。"""
    task = _flatten(scanned["example_module"])["ABC-TEST-QA-001"]
    assert task["status"] == "Canceled"


def test_四大區塊分類正確(scanned):
    classified = scanned["example_module"]["classified"]
    ids = {k: [t["task_id"] for t in v] for k, v in classified.items()}
    assert ids["current_sprint"] == ["ABC-DEV-BE-001", "ABC-DEV-BE-002", "ABC-DEV-BE-003"]
    assert ids["in_review"] == ["ABC-DEV-FE-001"]
    assert ids["product_backlog"] == ["ABC-DEV-FE-002"]


def test_近期結案依_closed_時間切分(scanned):
    """1 天前結案的進近期結案，400 天前的落到已封存。"""
    assert [t["task_id"] for t in scanned["another_module"]["classified"]["recent_closed"]] == [
        "XYZ-DEV-MANUAL-001"
    ]
    archived = [t["task_id"] for t in scanned["example_module"]["classified"]["archived"]]
    assert set(archived) == {"ABC-DOC-EPIC-001", "ABC-TEST-QA-001"}
    assert scanned["example_module"]["classified"]["recent_closed"] == []


def test_recent_days_可調整分界(project: Path):
    result = run_script(project, "scan_backlog.py", "--format", "json", "--recent-days", "500")
    data = json.loads(result.stdout)
    recent = [t["task_id"] for t in data["example_module"]["classified"]["recent_closed"]]
    assert set(recent) == {"ABC-DOC-EPIC-001", "ABC-TEST-QA-001"}


def test_project_可篩選單一模組(project: Path):
    result = run_script(project, "scan_backlog.py", "--format", "json", "--project", "example_module")
    data = json.loads(result.stdout)
    assert list(data) == ["example_module"]


def test_summary_格式輸出統計(project: Path):
    result = run_script(project, "scan_backlog.py", "--format", "summary")
    assert result.returncode == 0, result.stderr
    assert "example_module (共 7 張)" in result.stdout
    assert "In Progress: 1" in result.stdout
    assert "Canceled: 1" in result.stdout


def test_backlog_格式寫出_markdown(project: Path, tmp_path: Path):
    out = tmp_path / "BACKLOG.md"
    result = run_script(project, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    assert result.returncode == 0, result.stderr
    text = out.read_text(encoding="utf-8")
    assert "ABC-DEV-BE-001" in text
    assert "🧊 冰箱 (Icebox)" in text
    assert "_INDEX" not in text


def test_backlog_保留既有冰箱內容(project: Path, tmp_path: Path):
    """Icebox 由人工維護，腳本重跑不得覆寫。"""
    out = tmp_path / "BACKLOG_icebox.md"
    run_script(project, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    text = out.read_text(encoding="utf-8")
    marker = "| 改用事件驅動架構 | 需先更新 HLD | 等 Q3 再議 |"
    out.write_text(text.replace("| *(此區塊需手動維護，腳本不會覆寫)* | — | — |", marker), "utf-8")

    run_script(project, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    assert marker in out.read_text(encoding="utf-8")


def test_剛安裝完還沒建模組時以非零狀態碼結束(bare_install: Path):
    """kit 只帶骨架目錄，所以全新安裝掃不到任何模組——這時該明說，而不是給一份空報表。"""
    result = run_script(bare_install, "scan_backlog.py", "--format", "json")
    assert result.returncode == 1
    assert "未找到任何工單" in result.stderr


def test_由骨架複製出的模組會被掃到(bare_install: Path, tmp_path: Path):
    """照 install.sh 指示複製 `_TEMPLATE/` 出來後，新模組必須立刻出現在報表中。"""
    import shutil

    target = tmp_path / "copied"
    shutil.copytree(bare_install, target)
    shutil.copytree(target / "docs/features/_TEMPLATE", target / "docs/features/my_module")

    result = run_script(target, "scan_backlog.py", "--format", "json")
    assert result.returncode == 0, result.stderr
    assert list(json.loads(result.stdout)) == ["my_module"]


def test_底線開頭的目錄不被當成功能模組(scanned):
    """kit 自己帶的 `_TEMPLATE/` 是拿來複製的骨架，不該以模組身分出現在報表裡。"""
    assert "_TEMPLATE" not in scanned
    assert set(scanned) == {"another_module", "example_module"}
