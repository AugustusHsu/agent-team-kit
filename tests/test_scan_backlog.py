"""scan_backlog.py 的解析與分類行為。"""

import json
from datetime import datetime, timedelta, timezone
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


def test_近期結案不看今天是哪一天(scanned):
    """400 天前結案的工單照樣進「近期結案」——分類只由工單內容決定。

    以前這裡是「最近 N 天」的時間窗，已結案工單會隨日期流逝自己消失，
    生成檔因此不是輸入的純函數（documentation_conventions.md §5）。
    """
    assert [t["task_id"] for t in scanned["another_module"]["classified"]["recent_closed"]] == [
        "XYZ-DEV-MANUAL-001"
    ]
    recent = [t["task_id"] for t in scanned["example_module"]["classified"]["recent_closed"]]
    assert set(recent) == {"ABC-DOC-EPIC-001", "ABC-TEST-QA-001"}
    assert scanned["example_module"]["classified"]["archived"] == []


def test_近期結案超出上限才移入封存(project: Path):
    """上限是唯一的分界；被擠出去的才進封存。"""
    result = run_script(project, "scan_backlog.py", "--format", "json", "--recent-limit", "1")
    data = json.loads(result.stdout)["example_module"]["classified"]
    assert [t["task_id"] for t in data["recent_closed"]] == ["ABC-TEST-QA-001"]
    assert [t["task_id"] for t in data["archived"]] == ["ABC-DOC-EPIC-001"]


def test_recent_days_旗標已移除(project: Path):
    """時間窗連同旗標一起下架，留著會讓人以為還能調分界。"""
    result = run_script(project, "scan_backlog.py", "--format", "json", "--recent-days", "500")
    assert result.returncode != 0
    assert "--recent-days" in result.stderr


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


def test_backlog_不含生成時間(project: Path, tmp_path: Path):
    """生成檔必須是輸入的純函數：嵌了生成時間，換一天重跑就有 diff，
    「重跑看有沒有 diff ＝ 判斷是否過期」這條檢查會永遠回答「過期」。"""
    out = tmp_path / "BACKLOG_pure.md"
    run_script(project, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    assert "最後更新時間" not in out.read_text(encoding="utf-8")


def test_stale_不得寫入檔案(project: Path, tmp_path: Path):
    """時間相依的視圖只能走 stdout，腳本要自己擋，不是靠人記得。"""
    out = tmp_path / "stale.md"
    result = run_script(project, "scan_backlog.py", "--stale", "30", "--output", str(out))
    assert result.returncode != 0
    assert "stdout" in result.stderr
    assert not out.exists()


def test_stale_列出建立過久仍未結案的工單(有模組的專案: Path):
    很久以前 = (datetime.now(timezone(timedelta(hours=8))) - timedelta(days=100)).isoformat(
        timespec="minutes"
    )
    (有模組的專案 / "docs/features/my_module/tasks/MOD-DEV-BE-002.md").write_text(
        f"# [Task ID: MOD-DEV-BE-002] 放很久的工單\n\n"
        f"**🚥 任務狀態 (Status):** In Progress\n"
        f"**📅 建立時間 (Created):** {很久以前}\n"
        f"**✅ 完成時間 (Closed):**\n",
        encoding="utf-8",
    )
    result = run_script(有模組的專案, "scan_backlog.py", "--stale", "30")
    assert result.returncode == 0, result.stderr
    assert "MOD-DEV-BE-002" in result.stdout
    assert "100" in result.stdout


def test_stale_不列入已結案工單(有模組的專案: Path):
    很久以前 = (datetime.now(timezone(timedelta(hours=8))) - timedelta(days=100)).isoformat(
        timespec="minutes"
    )
    (有模組的專案 / "docs/features/my_module/tasks/MOD-DEV-BE-003.md").write_text(
        f"# [Task ID: MOD-DEV-BE-003] 早就結案了\n\n"
        f"**🚥 任務狀態 (Status):** Done\n"
        f"**📅 建立時間 (Created):** {很久以前}\n"
        f"**✅ 完成時間 (Closed):** {很久以前}\n",
        encoding="utf-8",
    )
    result = run_script(有模組的專案, "scan_backlog.py", "--stale", "30")
    assert "MOD-DEV-BE-003" not in result.stdout


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


@pytest.fixture
def 有模組的專案(bare_install: Path, tmp_path: Path) -> Path:
    """由骨架複製出一個模組，讓測試可以自己塞工單進去。"""
    import shutil

    target = tmp_path / "with_module"
    shutil.copytree(bare_install, target)
    shutil.copytree(target / "docs/features/_TEMPLATE", target / "docs/features/my_module")
    return target


def _工單內文(closed_行: str, 後續: str) -> str:
    return (
        "# [Task ID: MOD-DEV-BE-001] 測試工單\n\n"
        "**🔗 依附母任務 (Parent Task ID):** —\n"
        "**🏷️ 任務類型 (Task Type):** queue_agent\n"
        "**👤 負責人 (Assignee):** backend-engineer\n"
        "**🚥 任務狀態 (Status):** In Progress\n"
        "**📅 建立時間 (Created):** 2026-01-01T00:00+08:00\n"
        + closed_行
        + 後續
    )


def _掃一張工單(專案: Path, 內文: str) -> dict:
    (專案 / "docs/features/my_module/tasks/MOD-DEV-BE-001.md").write_text(內文, encoding="utf-8")
    result = run_script(專案, "scan_backlog.py", "--format", "json")
    assert result.returncode == 0, result.stderr
    return _flatten(json.loads(result.stdout)["my_module"])["MOD-DEV-BE-001"]


def test_欄位留空時不會抓到下一行(有模組的專案: Path):
    """Closed 留空是進行中工單的常態，不能把下一行整行當成完成時間。"""
    task = _掃一張工單(
        有模組的專案,
        _工單內文("**✅ 完成時間 (Closed):**\n", "**🔀 審查載體編號 (PR/MR):** —\n"),
    )
    assert task["closed"] is None
    assert task["status"] == "In Progress"


def test_欄位留空且後接空行時不會跨行(有模組的專案: Path):
    """空白行也是 \\s 的一員；跨過空行抓到下一段內容同樣是誤配。"""
    task = _掃一張工單(
        有模組的專案,
        _工單內文("**✅ 完成時間 (Closed):**   \n", "\n## 1. 任務描述 (Description)\n\n內文\n"),
    )
    assert task["closed"] is None



def test_底線開頭的目錄不被當成功能模組(scanned):
    """kit 自己帶的 `_TEMPLATE/` 是拿來複製的骨架，不該以模組身分出現在報表裡。"""
    assert "_TEMPLATE" not in scanned
    assert set(scanned) == {"another_module", "example_module"}
# ---------------------------------------------------------------------------
# 設計筆記 (Design Notes) 索引
# ---------------------------------------------------------------------------


def _寫一份_dn(dn_dir: Path, 編號: str, 標題: str, 狀態: str, 依賴: str) -> None:
    dn_dir.mkdir(parents=True, exist_ok=True)
    (dn_dir / f"{編號}_fixture.md").write_text(
        f"# [{編號}] {標題}\n\n"
        f"**🚥 狀態 (Status):** {狀態}\n"
        f"**📅 建立 (Created):** 2026-01-01\n"
        f"**🔗 依賴 (Depends on):** {依賴}\n"
        f"**📌 來源 (Origin):** 測試 fixture\n",
        encoding="utf-8",
    )


@pytest.fixture
def 有_dn_的專案(project: Path, tmp_path: Path) -> Path:
    """把 session 級的 project 複製一份再鋪 DN，避免污染其他測試。"""
    import shutil

    dest = tmp_path / "proj_with_dn"
    shutil.copytree(project, dest)
    dn_dir = dest / "docs" / "design_notes"
    _寫一份_dn(dn_dir, "DN-001", "第一份設計筆記", "🌱 Seed", "—")
    _寫一份_dn(dn_dir, "DN-002", "第二份設計筆記", "🔍 Exploring", "DN-001（格式）")
    return dest


def test_backlog_列出設計筆記且排在冰箱之前(有_dn_的專案: Path, tmp_path: Path):
    out = tmp_path / "BACKLOG_dn.md"
    result = run_script(有_dn_的專案, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    assert result.returncode == 0, result.stderr
    text = out.read_text(encoding="utf-8")

    assert "🧪 設計筆記 (Design Notes)" in text
    assert "DN-001" in text and "第一份設計筆記" in text
    assert "🔍 Exploring" in text
    assert "../design_notes/DN-002_fixture.md" in text
    # 開單前置關卡排在冰箱之前：DN 是「還沒變成工單」的東西，冰箱是「決定不做」的東西
    assert text.index("🧪 設計筆記") < text.index("🧊 冰箱")


def test_backlog_標出懸空的_dn_依賴(有_dn_的專案: Path, tmp_path: Path):
    """依賴指向一份不存在的 DN 時要自己浮出來——DN-002 曾懸空六份 DN 的時間都沒人發現。"""
    dn_dir = 有_dn_的專案 / "docs" / "design_notes"
    _寫一份_dn(dn_dir, "DN-003", "指向不存在的依賴", "🌱 Seed", "DN-099（根本沒這份）")

    out = tmp_path / "BACKLOG_dangling.md"
    run_script(有_dn_的專案, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    text = out.read_text(encoding="utf-8")

    assert "懸空依賴" in text
    assert "DN-003 → `DN-099`" in text
    # 存在的依賴不該被誤報
    assert "`DN-001`" not in text.split("懸空依賴")[1]


def test_backlog_沒有_dn_時整段省略(project: Path, tmp_path: Path):
    """裝了 kit 但還沒開過 DN 的專案不該看到一張空表，也不該報錯。"""
    out = tmp_path / "BACKLOG_no_dn.md"
    result = run_script(project, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    assert result.returncode == 0, result.stderr
    text = out.read_text(encoding="utf-8")

    assert "🧪 設計筆記" not in text
    assert "🧊 冰箱 (Icebox)" in text


def test_backlog_的設計筆記區塊不含時間相依值(有_dn_的專案: Path, tmp_path: Path):
    """納入版控的生成檔內容必須是輸入的純函數，否則每天重跑都生出假 diff。"""
    第一次 = tmp_path / "BACKLOG_pure_1.md"
    run_script(有_dn_的專案, "scan_backlog.py", "--format", "backlog", "--output", str(第一次))
    區塊 = 第一次.read_text(encoding="utf-8").split("🧪 設計筆記")[1].split("🧊 冰箱")[0]

    for 時間詞 in ("天前", "距今", "已開", "days"):
        assert 時間詞 not in 區塊, f"設計筆記區塊不得出現時間相依值：{時間詞}"


def test_backlog_重跑不改變設計筆記區塊(有_dn_的專案: Path, tmp_path: Path):
    """就地重跑必須冪等——冰箱是人工維護的，DN 索引是生成的，兩者都不能在重跑時漂移。"""
    out = tmp_path / "BACKLOG_idem.md"
    run_script(有_dn_的專案, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    第一次 = out.read_text(encoding="utf-8")

    run_script(有_dn_的專案, "scan_backlog.py", "--format", "backlog", "--output", str(out))
    assert out.read_text(encoding="utf-8") == 第一次


def test_reviews_目錄不會被當成工單掃描(有模組的專案: Path):
    """審查檔與工單同名、同格式，只差在目錄——掃描器一旦改用 rglob 就會多算一張。

    PEV-DEV-AGENT-016 把完整審查報告從工單移到 `reviews/<TaskID>.md`，
    「只掃 tasks/」從實作細節升格成規範前提，需要有測試釘住。
    """
    模組 = 有模組的專案 / "docs/features/my_module"
    (模組 / "tasks/MOD-DEV-BE-004.md").write_text(
        "# [Task ID: MOD-DEV-BE-004] 進行中的工單\n\n"
        "**🚥 任務狀態 (Status):** In Progress\n"
        "**📅 建立時間 (Created):** 2026-04-20T10:00+08:00\n"
        "**✅ 完成時間 (Closed):**\n",
        encoding="utf-8",
    )
    (模組 / "reviews/MOD-DEV-BE-004.md").write_text(
        "# [Task ID: MOD-DEV-BE-004] 審查紀錄\n\n"
        "**🚥 任務狀態 (Status):** Done\n"
        "**📅 建立時間 (Created):** 2026-04-21T10:00+08:00\n"
        "**✅ 完成時間 (Closed):** 2026-04-22T16:04+08:00\n",
        encoding="utf-8",
    )

    result = run_script(有模組的專案, "scan_backlog.py", "--format", "json")
    assert result.returncode == 0, result.stderr
    tasks = _flatten(json.loads(result.stdout)["my_module"])

    assert list(tasks) == ["MOD-DEV-BE-004"], "審查檔被當成第二張工單掃進來了"
    assert tasks["MOD-DEV-BE-004"]["status"] == "In Progress", (
        "工單狀態被審查檔的 Done 蓋掉"
    )
