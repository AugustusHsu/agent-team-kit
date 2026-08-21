"""precheck.py 的七項第 1 層流程檢查。

每一項都有負向對照（造出違規輸入，確認會紅），另有兩支防假紅燈的迴歸：
檢查器誤把合法內容判成違規，比漏抓更糟——它會逼作者改成不自然的寫法來閃避。
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_script

BACKLOG = "docs/development/BACKLOG.md"
TASK = "docs/features/my_module/tasks/MOD-DEV-BE-001.md"


def 跑(專案: Path):
    return run_script(專案, "precheck.py")


def _工單(
    status="Done",
    created="2026-01-01T09:00+08:00",
    closed="2026-01-02T09:00+08:00",
    內文="",
    打勾=None,
    assignee="backend-developer",
):
    return (
        "# [Task ID: MOD-DEV-BE-001] 測試工單\n\n"
        "**🔗 依附母任務 (Parent Task ID):** —\n"
        "**🏷️ 任務類型 (Task Type):** queue_agent\n"
        f"**👤 負責人 (Assignee):** {assignee}\n"
        f"**🚥 任務狀態 (Status):** {status}\n"
        f"**📅 建立時間 (Created):** {created}\n"
        f"**✅ 完成時間 (Closed):** {closed}\n"
        "**🔀 審查載體編號 (PR/MR):** —\n\n"
        "## 1. 任務描述 (Description)\n\n"
        + 內文
        + (
            "\n## 3. 驗收標準 (Acceptance Criteria)\n\n"
            + "".join(f"- [{'x' if 打勾 else ' '}] AC-0{i}：條件 {i}\n" for i in (1, 2))
            if 打勾 is not None
            else ""
        )
    )


def 檢查項數(專案: Path) -> int:
    """項數取自腳本自己的 --list，不寫死——寫死就是第二份表述，加檢查時必然忘記改。"""
    result = run_script(專案, "precheck.py", "--list")
    assert result.returncode == 0, result.stderr
    return len([l for l in result.stdout.splitlines() if l.startswith("- ")])


@pytest.fixture
def 乾淨專案(bare_install: Path, tmp_path: Path) -> Path:
    """裝好 kit、鋪一張合法工單、BACKLOG 已重生——每一項檢查都應該綠。"""
    target = tmp_path / "clean"
    shutil.copytree(bare_install, target)
    shutil.copytree(target / "docs/features/_TEMPLATE", target / "docs/features/my_module")
    (target / TASK).write_text(_工單(), encoding="utf-8")
    重生(target)
    return target


def 重生(專案: Path):
    result = run_script(專案, "scan_backlog.py", "--format", "backlog", "--output", BACKLOG)
    assert result.returncode == 0, result.stderr


def test_乾淨專案每項全綠(乾淨專案: Path):
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("✅") == 檢查項數(乾淨專案), result.stdout


def test_backlog_過期會紅(乾淨專案: Path):
    """改完工單忘了重生 BACKLOG——CLAUDE.md 已載明這是人反覆踩的坑。"""
    (乾淨專案 / TASK).write_text(_工單(status="In Progress", closed="—"), encoding="utf-8")
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert BACKLOG in result.stdout
    # 訊息要講得出怎麼修，不能只說「失敗」
    assert "scan_backlog.py" in result.stdout


def test_status_值不合法會紅(乾淨專案: Path):
    """打錯字不會讓任何東西壞掉，工單只是從所有視圖裡靜默消失。"""
    (乾淨專案 / TASK).write_text(_工單(status="Doen"), encoding="utf-8")
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert "Doen" in result.stdout
    assert TASK in result.stdout, "沒指出是哪個檔案"


def test_closed_早於_created_會紅(乾淨專案: Path):
    (乾淨專案 / TASK).write_text(
        _工單(created="2026-01-05T09:00+08:00", closed="2026-01-02T09:00+08:00"),
        encoding="utf-8",
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert "Closed 早於 Created" in result.stdout


def test_時間戳不是_iso_8601_會紅(乾淨專案: Path):
    (乾淨專案 / TASK).write_text(_工單(closed="2026年1月2日"), encoding="utf-8")
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert "ISO 8601" in result.stdout


def test_死連結會紅(乾淨專案: Path):
    (乾淨專案 / TASK).write_text(
        _工單(內文="參見 [設計文件](hld_不存在.md)。\n"), encoding="utf-8"
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert "hld_不存在.md" in result.stdout


def test_各項互不短路(乾淨專案: Path):
    """第一項紅就停會讓修復迴圈變成一項跑一趟。

    這張輸入同時違反前四項；後兩項（Closed 留空、AC 全打勾未結案）與 Status
    的合法值互斥，湊不進同一張單，所以只斷言「四紅、其餘綠、加起來等於總項數」。
    """
    (乾淨專案 / TASK).write_text(
        _工單(status="Doen", closed="2026年1月2日", 內文="[死的](沒有這個檔.md)\n"),
        encoding="utf-8",
    )
    # 刻意不重生 BACKLOG，讓四項同時紅
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert result.stdout.count("❌") == 4, result.stdout
    assert result.stdout.count("✅") + result.stdout.count("❌") == 檢查項數(乾淨專案)


def test_done_沒填_closed_會紅(乾淨專案: Path):
    """PEV-DEV-AGENT-002 結案時真的漏填過一次，當時四項檢查全綠。"""
    (乾淨專案 / TASK).write_text(_工單(closed="—"), encoding="utf-8")
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert "Closed 留空" in result.stdout
    assert TASK in result.stdout, "沒指出是哪個檔案"


def test_ac_全打勾但未結案會紅(乾淨專案: Path):
    """KIT-DEV-AGENT-001 的形狀：14 條 AC 全打勾、東西全進了主線，Status 卻沒動。"""
    (乾淨專案 / TASK).write_text(
        _工單(status="In Review", closed="—", 打勾=True), encoding="utf-8"
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert "全數打勾" in result.stdout
    assert "In Review" in result.stdout


def test_assignee_不是實際存在的角色會紅(乾淨專案: Path):
    """PEV-DEV-AGENT-012／013 的形狀：Assignee 寫 `backend-engineer`，
    但 `.agent/skills/` 底下那個角色叫 `backend-developer`——差一個字，
    工單於是永遠等不到正確的角色接手，而其餘六項檢查全綠。

    訊息要同時說出四件事，少一件就得回去翻檔案：
    哪張工單、哪一行、填了什麼、合法值有哪些。
    """
    (乾淨專案 / TASK).write_text(
        _工單(status="In Progress", closed="—", assignee="backend-engineer"),
        encoding="utf-8",
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    行 = [line for line in result.stdout.splitlines() if "backend-engineer" in line]
    assert 行, "訊息沒提到填錯的值：\n" + result.stdout
    訊息 = "\n".join(行)
    assert TASK in 訊息, "沒指出是哪張工單"
    assert "backend-developer" in 訊息, "沒列出合法值，看不出該改成什麼"
    行號 = int(訊息.split(TASK + ":")[1].split("：")[0].split()[0])
    原文 = (乾淨專案 / TASK).read_text(encoding="utf-8").splitlines()
    assert "負責人 (Assignee)" in 原文[行號 - 1], f"回報行號 {行號} 指到 {原文[行號 - 1]!r}"


# ── 防假紅燈的迴歸 ──────────────────────────────────────────────


def test_canceled_工單允許_ac_全打勾(乾淨專案: Path):
    """取消常常是外部前提消失，該做的都做完了才喊停——逼它把勾拿掉只會是造假。"""
    (乾淨專案 / TASK).write_text(
        _工單(status="Canceled", closed="—", 打勾=True), encoding="utf-8"
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_ac_還有沒打勾的不算違規(乾淨專案: Path):
    (乾淨專案 / TASK).write_text(
        _工單(status="In Progress", closed="—", 打勾=False), encoding="utf-8"
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_底線開頭的範例工單不會誤觸新檢查(乾淨專案: Path):
    """`_EXAMPLE-DEV-BE-001.md` 的 Status 是「Pending / Ready / …」說明文字、
    AC 全部沒打勾。它靠 `scan_all_tasks` 跳過底線開頭的檔名而不被掃到——
    這件事要實測，不能只從 `iter_tasks()` 的實作推論。
    """
    範例 = 乾淨專案 / "docs/features/my_module/tasks/_EXAMPLE-DEV-BE-001.md"
    assert 範例.is_file(), "樣板的範例工單沒被複製過來，這個測試就沒在測東西"
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "_EXAMPLE-DEV-BE-001" not in result.stdout


def test_日期粒度混用不算違規(乾淨專案: Path):
    """PEV-DEV-AGENT-001 的形狀：Closed 只有日期、Created 有時分。

    純日期本身就是合法 ISO 8601。把它當成午夜 00:00 去比會判成
    「Closed 早於 Created」，但精度較粗的值推不出先後違規。
    """
    (乾淨專案 / TASK).write_text(
        _工單(created="2026-01-02T14:06+08:00", closed="2026-01-02"), encoding="utf-8"
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_行內程式碼裡的連結不算死連結(乾淨專案: Path):
    """PEV-DEV-AGENT-008 的形狀：連結語法被當成「例子」引用。"""
    (乾淨專案 / TASK).write_text(
        _工單(內文="依賴欄位長這樣：`[DN-007](DN-007_ci_gate.md)`，會被拆成純文字。\n"),
        encoding="utf-8",
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_程式碼區塊裡的連結不算死連結(乾淨專案: Path):
    (乾淨專案 / TASK).write_text(
        _工單(內文="```markdown\n[範例](../reviews/不存在.md)\n```\n"), encoding="utf-8"
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_未結案工單的空_closed_不算格式錯誤(乾淨專案: Path):
    (乾淨專案 / TASK).write_text(_工單(status="In Progress", closed="—"), encoding="utf-8")
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_死連結行號指得回原始檔案(乾淨專案: Path):
    """strip_code 會把程式碼區塊換成空行以維持行數；行號對不上就沒有可用性。"""
    內文 = "```\n忽略\n```\n\n第五行之後\n\n[壞的](沒有.md)\n"
    (乾淨專案 / TASK).write_text(_工單(內文=內文), encoding="utf-8")
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode != 0
    行號 = int(
        [line for line in result.stdout.splitlines() if "沒有.md" in line][0]
        .split(":")[1]
        .split("：")[0]
    )
    原文 = (乾淨專案 / TASK).read_text(encoding="utf-8").splitlines()
    assert "[壞的](沒有.md)" in 原文[行號 - 1], f"回報行號 {行號} 指到 {原文[行號 - 1]!r}"


def test_合法角色讀自_skills_目錄而不是寫死清單(乾淨專案: Path):
    """kit 可以裝到任何專案，專案可以自己加角色。寫死清單的實作會在這裡轉紅——
    而且是最糟的那種紅：專案愈認真擴充自己的團隊，紅得愈厲害。
    """
    新角色 = 乾淨專案 / ".agent/skills/data-engineer"
    新角色.mkdir()
    (新角色 / "SKILL.md").write_text("# 專案自訂角色\n", encoding="utf-8")
    (乾淨專案 / TASK).write_text(
        _工單(status="In Progress", closed="—", assignee="data-engineer"),
        encoding="utf-8",
    )
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr


def test_留空與_manual_user_的_assignee_不算違規(乾淨專案: Path):
    """`—` 是還沒指派，`manual_user` 是工單範本明列的「使用者親自處理」。
    兩者都不是打錯字，判紅只會逼人隨便填一個角色進去閃避。
    """
    for 值 in ("—", "manual_user"):
        (乾淨專案 / TASK).write_text(
            _工單(status="In Progress", closed="—", assignee=值), encoding="utf-8"
        )
        重生(乾淨專案)
        result = 跑(乾淨專案)
        assert result.returncode == 0, f"{值}：\n" + result.stdout + result.stderr


def test_已結案工單的錯誤_assignee_不算違規(乾淨專案: Path):
    """team_protocol.md §1.11：已結案工單是歷史紀錄，不改它、也不引用它。

    涵蓋全部工單會製造一個只能靠違反 §1.11 才解得掉的紅燈——本 repo 的
    `012`／`013` 正是這個形狀：Assignee 確實填錯，但兩張都已 Done。
    """
    (乾淨專案 / TASK).write_text(_工單(assignee="backend-engineer"), encoding="utf-8")
    重生(乾淨專案)
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr
