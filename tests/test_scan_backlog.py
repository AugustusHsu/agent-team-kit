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


def test_沒有任何工單時以非零狀態碼結束(tmp_path: Path):
    import subprocess

    from conftest import INSTALL_SH

    target = tmp_path / "empty"
    target.mkdir()
    subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)
    # kit 只帶 _TEMPLATE（本身沒有可掃描的工單），刪掉後就完全沒有 features
    import shutil

    shutil.rmtree(target / "docs" / "features")
    (target / "docs" / "features").mkdir()

    result = run_script(target, "scan_backlog.py", "--format", "json")
    assert result.returncode == 1
    assert "未找到任何工單" in result.stderr


def test_kit_內建的_TEMPLATE_模組不含可掃描工單(scanned):
    """`_TEMPLATE/tasks/` 下的範例工單以 `_` 開頭，因此不會被算進統計。

    附帶效果：`_TEMPLATE` 這個模組本身仍會以 0 張出現在輸出中。
    這是目前的行為（目錄名不受底線規則影響），在此釘住以免無意間改動。
    """
    assert scanned["_TEMPLATE"]["total"] == 0
