"""scan_backlog.py 的解析與分類行為。"""

import json
import subprocess
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


# ---------------------------------------------------------------------------
# 工單 DAG、Round Manifest 與 Parallel Change
# ---------------------------------------------------------------------------


@pytest.fixture
def 規劃專案(bare_install: Path, tmp_path: Path) -> Path:
    """全新安裝後只建立一個真實模組；測試自行寫 Markdown，不 mock parser。"""
    import shutil

    target = tmp_path / "planning"
    shutil.copytree(bare_install, target)
    shutil.copytree(target / "docs/features/_TEMPLATE", target / "docs/features/my_module")
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-qm", "planning base"], cwd=target, check=True)
    return target


def _規劃工單(
    task_id: str,
    *,
    blocked_by: str = "—",
    write_scope: str = "`src/default.py`",
    external_effects: str | None = "—",
    contract: str = "—",
    change_set: str = "—",
    phase: str = "—",
    task_type: str = "queue_backend",
    status: str = "Pending",
) -> str:
    external_effects_line = (
        "" if external_effects is None else f"**🌐 外部副作用 (External Effects):** {external_effects}\n"
    )
    return (
        f"# [Task ID: {task_id}] {task_id} 測試工單\n\n"
        "**🔗 依附母任務 (Parent Task ID):** Independent\n"
        f"**🏷️ 任務類型 (Task Type):** {task_type}\n"
        "**👤 負責人 (Assignee):** backend-developer\n"
        f"**⛓️ 前置工單 (Blocked By):** {blocked_by}\n"
        f"**✍️ 寫入範圍 (Write Scope):** {write_scope}\n"
        f"{external_effects_line}"
        f"**📜 共用契約 (Contract):** {contract}\n"
        f"**🔁 變更集合 (Change Set):** {change_set}\n"
        f"**🪜 變更階段 (Phase):** {phase}\n"
        f"**🚥 任務狀態 (Status):** {status}\n"
        "**📅 建立時間 (Created):** 2026-08-27T10:00+08:00\n"
        "**✅ 完成時間 (Closed):** —\n"
        "**🔀 審查載體編號 (PR/MR):** —\n"
    )


def _寫規劃工單(專案: Path, task_id: str, **kwargs) -> None:
    path = 專案 / f"docs/features/my_module/tasks/{task_id}.md"
    path.write_text(_規劃工單(task_id, **kwargs), encoding="utf-8")


def _寫_round(
    專案: Path,
    round_id: str,
    task_ids: list[str],
    *,
    goal: str | None = "驗證規劃圖",
    branch: str | None = "feature/planning-test",
    opening_base: str | None = "HEAD",
    review_target: str | None = "—",
) -> None:
    if opening_base == "HEAD":
        opening_base = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=專案,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    metadata = [f"# [Round ID: {round_id}] 測試輪次", "", "**🚥 輪次狀態 (Status):** Open"]
    if goal is not None:
        metadata.append(f"**🎯 輪次目標 (Goal):** {goal}")
    if branch is not None:
        metadata.append(f"**🌿 輪次分支 (Branch):** `{branch}`")
    if opening_base is not None:
        metadata.append(f"**📍 開輪基準 (Opening Base):** `{opening_base}`")
    if review_target is not None:
        metadata.append(
            f"**🔎 整合審查對象 (Integration Review Target):** {review_target}"
        )
    metadata.extend(
        [
            "",
            "## 1. 封閉工單集合（唯一來源）",
            "",
            "| Task ID | 目標 | 初始狀態 |",
            "|---|---|---|",
            *[f"| `{task_id}` | 測試 | Pending |" for task_id in task_ids],
            "",
            "## 2. 衍生視圖",
            "",
            "由掃描器產生。",
            "",
        ]
    )
    rounds = 專案 / "docs/development/rounds"
    rounds.mkdir(parents=True, exist_ok=True)
    (rounds / f"{round_id}_test.md").write_text("\n".join(metadata), encoding="utf-8")


def _讀_graph(專案: Path):
    result = run_script(專案, "scan_backlog.py", "--format", "graph")
    return result, json.loads(result.stdout)


def test_graph_舊工單沒有原五欄仍可讀(project: Path):
    result, graph = _讀_graph(project)
    assert result.returncode == 0, result.stderr
    task = graph["tasks"]["ABC-DEV-BE-001"]
    assert task["blocked_by"] == []
    assert task["write_scope"] is None
    assert task["contract"] is None
    assert task["external_effects"] is None


def test_graph_過渡工單只有原五欄仍可讀但外部副作用未知(規劃專案: Path):
    path = 規劃專案 / "docs/features/my_module/tasks/MOD-DEV-BE-001.md"
    content = _規劃工單("MOD-DEV-BE-001", external_effects=None)
    path.write_text(content, encoding="utf-8")

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    assert graph["tasks"]["MOD-DEV-BE-001"]["external_effects"] is None


def test_graph_合法_dag_穩定推導順序_wave_與反向_blocks(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`src/a.py`")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="MOD-DEV-BE-001",
        write_scope="`src/b.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="MOD-DEV-BE-001",
        write_scope="`src/c.py`",
    )

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    assert graph["topological_order"] == [
        "MOD-DEV-BE-001",
        "MOD-DEV-BE-002",
        "MOD-DEV-BE-003",
    ], "同一張 DAG 每次都必須產生相同的字典序拓撲"
    assert graph["tasks"]["MOD-DEV-BE-001"]["blocks"] == [
        "MOD-DEV-BE-002",
        "MOD-DEV-BE-003",
    ]
    assert graph["tasks"]["MOD-DEV-BE-001"]["wave"] == 1
    assert graph["tasks"]["MOD-DEV-BE-002"]["wave"] == 2


def test_graph_拒絕未知_自我_重複依賴與循環(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        blocked_by="MOD-DEV-BE-001",
        write_scope="`src/a.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="MOD-DEV-BE-099, MOD-DEV-BE-099",
        write_scope="`src/b.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="MOD-DEV-BE-004",
        write_scope="`src/c.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-004",
        blocked_by="MOD-DEV-BE-003",
        write_scope="`src/d.py`",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    for 訊息 in ("不得依賴自己", "不存在的 Task ID", "重複依賴", "有向循環"):
        assert 訊息 in result.stderr, f"缺少 {訊息!r} 的明確錯誤：\n{result.stderr}"


def test_graph_拒絕被丟棄或截短的非法依賴_token(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", blocked_by="TBD")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", blocked_by="MOD-DEV-BE-099x")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="`MOD-DEV-BE-001`、hidden",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "非法 Task ID token" in result.stderr
    for token in ("TBD", "MOD-DEV-BE-099x", "hidden"):
        assert token in result.stderr, f"非法 token {token!r} 被靜默丟棄：\n{result.stderr}"


def test_graph_拒絕破折號與其他來源_token_混用(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", blocked_by="—、TBD")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="—、MOD-DEV-BE-001",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        external_effects="—、deploy:prod",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-004",
        external_effects="—、N/A",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "Blocked By 含非法 Task ID token" in result.stderr
    assert "External Effects 必須使用 category:resource" in result.stderr
    for token in ("TBD", "N/A"):
        assert token in result.stderr, f"混合空值中的 {token!r} 被靜默丟棄：\n{result.stderr}"
    graph = json.loads(result.stdout)
    assert graph["tasks"]["MOD-DEV-BE-002"]["blocked_by"] == ["MOD-DEV-BE-001"]
    assert graph["tasks"]["MOD-DEV-BE-003"]["external_effects"] == ["—", "deploy:prod"]


def test_round_manifest_產出輪內_wave_blocks_與並行候選(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`src/base.py`")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="MOD-DEV-BE-001",
        write_scope="`src/left.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="MOD-DEV-BE-001",
        write_scope="`tests/right.py`",
    )
    _寫規劃工單(規劃專案, "MOD-DEV-BE-004", write_scope="`docs/independent.md`")
    _寫_round(
        規劃專案,
        "ROUND-001",
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002", "MOD-DEV-BE-003", "MOD-DEV-BE-004"],
    )

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    round_view = graph["rounds"]["ROUND-001"]
    assert round_view["waves"] == {
        "1": ["MOD-DEV-BE-001", "MOD-DEV-BE-004"],
        "2": ["MOD-DEV-BE-002", "MOD-DEV-BE-003"],
    }
    assert round_view["blocks"]["MOD-DEV-BE-001"] == [
        "MOD-DEV-BE-002",
        "MOD-DEV-BE-003",
    ]
    assert ["MOD-DEV-BE-002", "MOD-DEV-BE-003"] in round_view["parallel_candidates"]
    blockers = {tuple(item["tasks"]): item["reasons"] for item in round_view["parallel_blockers"]}
    assert "different_wave" in blockers[("MOD-DEV-BE-002", "MOD-DEV-BE-004")]


def test_round_manifest_拒絕缺欄_超額_未知與重複歸屬(規劃專案: Path):
    ids = [f"MOD-DEV-BE-00{i}" for i in range(1, 7)]
    for index, task_id in enumerate(ids, start=1):
        _寫規劃工單(規劃專案, task_id, write_scope=f"`src/{index}.py`")
    _寫_round(規劃專案, "ROUND-001", ids[:2])
    first_round = 規劃專案 / "docs/development/rounds/ROUND-001_test.md"
    (first_round.parent / "ROUND-009_duplicate.md").write_text(
        first_round.read_text(encoding="utf-8"), encoding="utf-8"
    )
    _寫_round(規劃專案, "ROUND-002", [*ids, "MOD-DEV-BE-099"])
    _寫_round(
        規劃專案,
        "ROUND-003",
        ids[2:4],
        goal=None,
        branch=None,
        opening_base=None,
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    for 訊息 in (
        "全域重複",
        "缺少 Goal",
        "缺少 Branch",
        "缺少 Opening Base",
        "2～5 張",
        "不存在的 Task ID",
        "不得重複歸入",
    ):
        assert 訊息 in result.stderr, f"缺少 {訊息!r} 的 manifest 錯誤：\n{result.stderr}"


def test_round_manifest_拒絕缺_review_target_空_topic_與不存在_base(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002")
    _寫_round(
        規劃專案,
        "ROUND-001",
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002"],
        branch="feature/",
        opening_base="1" * 40,
        review_target=None,
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    for 訊息 in ("缺少 Integration Review Target", "feature/{topic}", "不是此 repo 中存在的 commit"):
        assert 訊息 in result.stderr, f"缺少 {訊息!r} 的 Round 錯誤：\n{result.stderr}"


def test_round_manifest_拒絕非法資料列與重複表格結構(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002")
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-001", "MOD-DEV-BE-002"])
    path = 規劃專案 / "docs/development/rounds/ROUND-001_test.md"
    content = path.read_text(encoding="utf-8").replace(
        "| `MOD-DEV-BE-001` | 測試 | Pending |\n",
        "| `MOD-DEV-BE-001` | 測試 | Pending |\n"
        "| Task ID | 目標 | 初始狀態 |\n"
        "|---|---|---|\n"
        "| TBD | 不合法但仍在封閉集合 | Pending |\n"
        "| MOD-DEV-BE-099x | 截短 ID | Pending |\n"
        "| `MOD-DEV-BE-002` hidden | backtick 外殘留 | Pending |\n",
    )
    path.write_text(content, encoding="utf-8")

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "重複或錯位的 header" in result.stderr
    assert "重複或錯位的 separator" in result.stderr
    for token in ("TBD", "MOD-DEV-BE-099x", "hidden"):
        assert token in result.stderr, f"Round 非法來源 {token!r} 被靜默丟棄：\n{result.stderr}"
    round_view = json.loads(result.stdout)["rounds"]["ROUND-001"]
    assert round_view["parallel_candidates"] == []
    assert "invalid_planning_source" in round_view["parallel_blockers"][0]["reasons"]


def test_新式規劃欄位不可只填一部分(規劃專案: Path):
    path = 規劃專案 / "docs/features/my_module/tasks/MOD-DEV-BE-001.md"
    path.write_text(
        "# [Task ID: MOD-DEV-BE-001] 欄位缺漏\n\n"
        "**🏷️ 任務類型 (Task Type):** queue_backend\n"
        "**👤 負責人 (Assignee):** backend-developer\n"
        "**⛓️ 前置工單 (Blocked By):** —\n"
        "**🚥 任務狀態 (Status):** Pending\n"
        "**📅 建立時間 (Created):** 2026-08-27T10:00+08:00\n"
        "**✅ 完成時間 (Closed):** —\n",
        encoding="utf-8",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "新式規劃欄位不完整" in result.stderr
    assert "Write Scope" in result.stderr and "Phase" in result.stderr


def test_來源驗證錯誤的工單不得出現在並行候選(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        blocked_by="TBD",
        write_scope="`src/a.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        write_scope="`tests/b.py`",
        change_set="—、N/A",
        phase="—",
    )
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-001", "MOD-DEV-BE-002"])

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "非法 Task ID token" in result.stderr
    assert "填寫 Change Set 時必須指定 Phase" in result.stderr
    round_view = json.loads(result.stdout)["rounds"]["ROUND-001"]
    assert round_view["parallel_candidates"] == []
    assert round_view["parallel_blockers"] == [
        {
            "tasks": ["MOD-DEV-BE-001", "MOD-DEV-BE-002"],
            "reasons": ["invalid_planning_source"],
        }
    ]


def test_任一成員來源無效會使整個_round_的候選失效(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        blocked_by="TBD",
        write_scope="`src/invalid.py`",
    )
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", write_scope="`src/left.py`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-003", write_scope="`tests/right.py`")
    _寫_round(
        規劃專案,
        "ROUND-001",
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002", "MOD-DEV-BE-003"],
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    round_view = json.loads(result.stdout)["rounds"]["ROUND-001"]
    assert round_view["parallel_candidates"] == []
    blockers = {tuple(item["tasks"]): item["reasons"] for item in round_view["parallel_blockers"]}
    assert "invalid_planning_source" in blockers[("MOD-DEV-BE-002", "MOD-DEV-BE-003")]


def test_重複歸屬會同時使所有涉入_round_的候選失效(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`src/shared.py`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", write_scope="`tests/first.py`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-003", write_scope="`docs/second.md`")
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-001", "MOD-DEV-BE-002"])
    _寫_round(規劃專案, "ROUND-002", ["MOD-DEV-BE-001", "MOD-DEV-BE-003"])

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "不得重複歸入 ROUND-002" in result.stderr
    graph = json.loads(result.stdout)
    for round_id in ("ROUND-001", "ROUND-002"):
        round_view = graph["rounds"][round_id]
        assert round_view["parallel_candidates"] == []
        assert "invalid_planning_source" in round_view["parallel_blockers"][0]["reasons"]


def test_round_拒絕輪外未結案前置所以集合必須封閉(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`src/outside.py`")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="MOD-DEV-BE-001",
        write_scope="`src/inside.py`",
    )
    _寫規劃工單(規劃專案, "MOD-DEV-BE-003", write_scope="`src/peer.py`")
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-002", "MOD-DEV-BE-003"])

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "不是封閉集合" in result.stderr
    assert "MOD-DEV-BE-001" in result.stderr


def test_並行候選四項任一不確定就不放行(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`src/a.py`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", write_scope="`tests/b.py`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-003", write_scope="`src/a.py`")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-004",
        write_scope="`docs/d.py`",
        contract="`docs/contracts/missing.md`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-MANUAL-005",
        write_scope="`ops/e.txt`",
        external_effects=None,
        task_type="manual_user",
    )
    ids = [
        "MOD-DEV-BE-001",
        "MOD-DEV-BE-002",
        "MOD-DEV-BE-003",
        "MOD-DEV-BE-004",
        "MOD-DEV-MANUAL-005",
    ]
    _寫_round(規劃專案, "ROUND-001", ids)

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    round_view = graph["rounds"]["ROUND-001"]
    assert ["MOD-DEV-BE-001", "MOD-DEV-BE-002"] in round_view["parallel_candidates"]
    blockers = {tuple(item["tasks"]): item["reasons"] for item in round_view["parallel_blockers"]}
    assert "write_scope_overlap_or_unknown" in blockers[("MOD-DEV-BE-001", "MOD-DEV-BE-003")]
    assert any("contract_not_ready" in reason for reason in blockers[("MOD-DEV-BE-001", "MOD-DEV-BE-004")])
    assert "external_effects_overlap_or_unknown" in blockers[("MOD-DEV-BE-001", "MOD-DEV-MANUAL-005")]


def test_write_scope_根目錄_glob_無法證明與實際檔案不重疊(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`*.md`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", write_scope="`README.md`")
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-001", "MOD-DEV-BE-002"])

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    round_view = graph["rounds"]["ROUND-001"]
    assert round_view["parallel_candidates"] == []
    assert "write_scope_overlap_or_unknown" in round_view["parallel_blockers"][0]["reasons"]


def test_write_scope_與_contract_拒絕_backtick_外殘留路徑(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        write_scope="`src/a.py`、tests/shared.py",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        write_scope="`tests/shared.py`",
        contract="`docs/contracts/api.md`、docs/contracts/hidden.md",
    )
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-001", "MOD-DEV-BE-002"])

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "Write Scope 含非法或不完整路徑 token：tests/shared.py" in result.stderr
    assert "Contract 含非法或不完整契約路徑 token：docs/contracts/hidden.md" in result.stderr
    round_view = json.loads(result.stdout)["rounds"]["ROUND-001"]
    assert round_view["parallel_candidates"] == []
    reasons = round_view["parallel_blockers"][0]["reasons"]
    assert "write_scope_overlap_or_unknown" in reasons
    assert "contract_not_ready:MOD-DEV-BE-002" in reasons


def test_write_scope_與_contract_拒絕_placeholder_及混合空值(規劃專案: Path):
    cases = (
        ("ROUND-001", 1, {"write_scope": "TBD"}),
        ("ROUND-002", 3, {"write_scope": "N/A"}),
        ("ROUND-003", 5, {"write_scope": "None"}),
        ("ROUND-004", 7, {"write_scope": "—、src/hidden.py"}),
        ("ROUND-005", 9, {"contract": "TBD"}),
        ("ROUND-006", 11, {"contract": "N/A"}),
    )
    for round_id, start, invalid_kwargs in cases:
        invalid_id = f"MOD-DEV-BE-{start:03d}"
        peer_id = f"MOD-DEV-BE-{start + 1:03d}"
        _寫規劃工單(規劃專案, invalid_id, **invalid_kwargs)
        _寫規劃工單(
            規劃專案,
            peer_id,
            write_scope=f"`tests/{peer_id}.py`",
        )
        _寫_round(規劃專案, round_id, [invalid_id, peer_id])

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    for token in ("TBD", "N/A", "None", "—"):
        assert token in result.stderr, f"placeholder {token!r} 沒有被來源驗證攔截"
    graph = json.loads(result.stdout)
    for round_id, *_ in cases:
        assert graph["rounds"][round_id]["parallel_candidates"] == []


def test_external_effects_缺來源或作用域重疊時不列並行候選(規劃專案: Path):
    _寫規劃工單(規劃專案, "MOD-DEV-BE-001", write_scope="`src/a.py`")
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", write_scope="`tests/b.py`")
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        write_scope="`docs/c.md`",
        external_effects=None,
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-004",
        write_scope="`ops/d.py`",
        external_effects="`account:vendor`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-005",
        write_scope="`config/e.py`",
        external_effects="`account:vendor/project`",
    )
    ids = [f"MOD-DEV-BE-00{index}" for index in range(1, 6)]
    _寫_round(規劃專案, "ROUND-001", ids)

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    round_view = graph["rounds"]["ROUND-001"]
    assert ["MOD-DEV-BE-001", "MOD-DEV-BE-002"] in round_view["parallel_candidates"]
    blockers = {tuple(item["tasks"]): item["reasons"] for item in round_view["parallel_blockers"]}
    assert "external_effects_overlap_or_unknown" in blockers[("MOD-DEV-BE-001", "MOD-DEV-BE-003")]
    assert "external_effects_overlap_or_unknown" in blockers[("MOD-DEV-BE-004", "MOD-DEV-BE-005")]


def test_external_effects_具名作用域可證不重疊時允許並行(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        write_scope="`src/a.py`",
        external_effects="`deploy:staging/blue`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        write_scope="`tests/b.py`",
        external_effects="`deploy:staging/green`",
    )
    _寫_round(規劃專案, "ROUND-001", ["MOD-DEV-BE-001", "MOD-DEV-BE-002"])

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    assert graph["rounds"]["ROUND-001"]["parallel_candidates"] == [
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002"]
    ]


def test_external_effects_拒絕未命名作用域與_glob(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        external_effects="`第三方帳號`、`deploy:*`、hidden",
    )
    _寫規劃工單(規劃專案, "MOD-DEV-BE-002", external_effects="TBD")

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "External Effects 必須使用 category:resource" in result.stderr
    for token in ("第三方帳號", "deploy:*", "hidden", "TBD"):
        assert token in result.stderr, f"非法外部作用域 {token!r} 被靜默丟棄：\n{result.stderr}"


def test_external_effects_出貨標準_ADR_與模板保持同一六欄語意(bare_install: Path):
    paths = (
        "docs/standards/parallel_development.md",
        "docs/standards/adr/ADR-001_task_dag_and_ownership.md",
        ".agent/resources/task_template.md",
        "docs/features/_TEMPLATE/tasks/_EXAMPLE-DEV-BE-001.md",
    )
    contents = {
        path: (bare_install / path).read_text(encoding="utf-8")
        for path in paths
    }
    for path, content in contents.items():
        assert "External Effects" in content, f"{path} 漏掉第六個來源欄位"
        assert "單一識別碼" in content, f"{path} 漏掉 Change Set 單值規則"
        assert "path/**" in content, f"{path} 漏掉目錄 Write Scope 的明確 glob 表示"
    assert "六個來源欄位" in contents["docs/standards/adr/ADR-001_task_dag_and_ownership.md"]


def test_contract_存在於_opening_base_才能直接放行並行(規劃專案: Path):
    contract = 規劃專案 / "docs/contracts/api.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text("# API contract\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=規劃專案, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=規劃專案, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=規劃專案, check=True)
    subprocess.run(["git", "add", "docs/contracts/api.md"], cwd=規劃專案, check=True)
    subprocess.run(["git", "commit", "-qm", "test contract"], cwd=規劃專案, check=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=規劃專案,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        write_scope="`src/a.py`",
        contract="`docs/contracts/api.md`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        write_scope="`tests/b.py`",
        contract="`docs/contracts/api.md`",
    )
    _寫_round(
        規劃專案,
        "ROUND-001",
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002"],
        opening_base=base,
    )

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    assert graph["rounds"]["ROUND-001"]["parallel_candidates"] == [
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002"]
    ]


def test_contract_同_wave_peer_正在修改時不得沿用_base_舊版(規劃專案: Path):
    contract = 規劃專案 / "docs/contracts/api.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text("# API contract\n", encoding="utf-8")
    subprocess.run(["git", "add", "docs/contracts/api.md"], cwd=規劃專案, check=True)
    subprocess.run(["git", "commit", "-qm", "contract base"], cwd=規劃專案, check=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=規劃專案,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        write_scope="`docs/contracts/api.md`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        write_scope="`src/consumer.py`",
        contract="`docs/contracts/api.md`",
    )
    _寫_round(
        規劃專案,
        "ROUND-001",
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002"],
        opening_base=base,
    )

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    round_view = graph["rounds"]["ROUND-001"]
    assert round_view["parallel_candidates"] == []
    assert "contract_changed_by_peer" in round_view["parallel_blockers"][0]["reasons"]


def test_contract_前置_glob_必須實際匹配完整路徑才算已提供(規劃專案: Path):
    cases = (
        ("ROUND-001", 1, "docs/r3/*.md", "docs/r3/api.json", False),
        ("ROUND-002", 4, "docs/r3/*.md", "docs/r3/nested/api.md", False),
        ("ROUND-003", 7, "docs/r3/{api,event}.md", "docs/r3/api.md", False),
        ("ROUND-004", 10, "docs/r3/*.md", "docs/r3/api.md", True),
        ("ROUND-005", 13, "docs/r3/**", "docs/r3/nested/api.md", True),
    )
    consumer_pairs = {}
    for round_id, start, provider_scope, contract, should_match in cases:
        provider = f"MOD-DEV-BE-{start:03d}"
        left = f"MOD-DEV-BE-{start + 1:03d}"
        right = f"MOD-DEV-BE-{start + 2:03d}"
        _寫規劃工單(
            規劃專案,
            provider,
            write_scope=f"`{provider_scope}`",
        )
        _寫規劃工單(
            規劃專案,
            left,
            blocked_by=provider,
            write_scope=f"`src/{left}.py`",
            contract=f"`{contract}`",
        )
        _寫規劃工單(
            規劃專案,
            right,
            blocked_by=provider,
            write_scope=f"`tests/{right}.py`",
            contract=f"`{contract}`",
        )
        _寫_round(規劃專案, round_id, [provider, left, right])
        consumer_pairs[round_id] = ([left, right], should_match)

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    for round_id, (pair, should_match) in consumer_pairs.items():
        round_view = graph["rounds"][round_id]
        if should_match:
            assert pair in round_view["parallel_candidates"], (
                f"{round_id} 的實際 glob match 沒有提供 Contract"
            )
        else:
            assert pair not in round_view["parallel_candidates"], (
                f"{round_id} 只靠靜態前綴就誤認 Contract 已提供"
            )
            blockers = {tuple(item["tasks"]): item["reasons"] for item in round_view["parallel_blockers"]}
            assert f"contract_not_ready:{pair[0]}" in blockers[tuple(pair)]
            assert f"contract_not_ready:{pair[1]}" in blockers[tuple(pair)]


def test_contract_前置_literal_只接受完整路徑相等(規劃專案: Path):
    cases = (
        ("ROUND-001", 1, "docs/contracts/api.md/child", False),
        ("ROUND-002", 4, "docs/contracts/api.md", True),
    )
    expected = {}
    for round_id, start, provider_scope, should_match in cases:
        provider = f"MOD-DEV-BE-{start:03d}"
        left = f"MOD-DEV-BE-{start + 1:03d}"
        right = f"MOD-DEV-BE-{start + 2:03d}"
        _寫規劃工單(規劃專案, provider, write_scope=f"`{provider_scope}`")
        _寫規劃工單(
            規劃專案,
            left,
            blocked_by=provider,
            write_scope=f"`src/{left}.py`",
            contract="`docs/contracts/api.md`",
        )
        _寫規劃工單(
            規劃專案,
            right,
            blocked_by=provider,
            write_scope=f"`tests/{right}.py`",
            contract="`docs/contracts/api.md`",
        )
        _寫_round(規劃專案, round_id, [provider, left, right])
        expected[round_id] = ([left, right], should_match)

    result, graph = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr
    for round_id, (pair, should_match) in expected.items():
        round_view = graph["rounds"][round_id]
        if should_match:
            assert pair in round_view["parallel_candidates"]
        else:
            assert pair not in round_view["parallel_candidates"]
            blockers = {
                tuple(item["tasks"]): item["reasons"]
                for item in round_view["parallel_blockers"]
            }
            assert f"contract_not_ready:{pair[0]}" in blockers[tuple(pair)]
            assert f"contract_not_ready:{pair[1]}" in blockers[tuple(pair)]


def test_parallel_change_合法三階段通過(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        change_set="auth-v2",
        phase="expand",
        write_scope="`src/expand.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="MOD-DEV-BE-001",
        change_set="auth-v2",
        phase="migrate",
        write_scope="`src/migrate.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="MOD-DEV-BE-002",
        change_set="auth-v2",
        phase="contract",
        write_scope="`src/contract.py`",
    )

    result, _ = _讀_graph(規劃專案)
    assert result.returncode == 0, result.stderr


def test_parallel_change_拒絕_migrate_未位於_expand_之後(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        change_set="auth-v2",
        phase="expand",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        change_set="auth-v2",
        phase="migrate",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="MOD-DEV-BE-002",
        change_set="auth-v2",
        phase="contract",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "migrate 必須位於 expand MOD-DEV-BE-001 之後" in result.stderr


def test_parallel_change_拒絕破折號與階段內容混用(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        change_set="—、auth-v2",
        phase="—",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        change_set="—",
        phase="—、expand",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "填寫 Change Set 時必須指定 Phase" in result.stderr
    assert "Phase '—、expand' 不合法" in result.stderr


def test_parallel_change_完整三階段仍拒絕非法_change_set_識別碼(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        change_set="—、auth-v2",
        phase="expand",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        blocked_by="MOD-DEV-BE-001",
        change_set="—、auth-v2",
        phase="migrate",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        blocked_by="MOD-DEV-BE-002",
        change_set="—、auth-v2",
        phase="contract",
    )
    _寫規劃工單(規劃專案, "MOD-DEV-BE-004", write_scope="`docs/independent.md`")
    _寫_round(
        規劃專案,
        "ROUND-001",
        ["MOD-DEV-BE-001", "MOD-DEV-BE-002", "MOD-DEV-BE-003", "MOD-DEV-BE-004"],
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    assert "Change Set 必須是單一識別碼，非法值：—、auth-v2" in result.stderr
    assert json.loads(result.stdout)["rounds"]["ROUND-001"]["parallel_candidates"] == []


def test_parallel_change_拒絕非法_phase_缺_contract_與漏列_migrate(規劃專案: Path):
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-001",
        change_set="broken-phase",
        phase="expnad",
        write_scope="`src/a.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-002",
        change_set="missing-contract",
        phase="expand",
        write_scope="`src/b.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-003",
        change_set="missing-contract",
        phase="migrate",
        write_scope="`src/c.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-004",
        change_set="missing-dependency",
        phase="expand",
        write_scope="`src/d.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-005",
        blocked_by="MOD-DEV-BE-004",
        change_set="missing-dependency",
        phase="migrate",
        write_scope="`src/e.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-006",
        blocked_by="MOD-DEV-BE-004",
        change_set="missing-dependency",
        phase="contract",
        write_scope="`src/f.py`",
    )
    _寫規劃工單(
        規劃專案,
        "MOD-DEV-BE-007",
        change_set="missing-phase",
        write_scope="`src/g.py`",
    )

    result = run_script(規劃專案, "scan_backlog.py", "--format", "graph")
    assert result.returncode != 0
    for 訊息 in (
        "Phase 'expnad' 不合法",
        "一併建立一張 contract",
        "未涵蓋 migrate",
        "必須指定 Phase",
    ):
        assert 訊息 in result.stderr, f"缺少 {訊息!r} 的 Parallel Change 錯誤：\n{result.stderr}"
