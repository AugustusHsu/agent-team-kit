"""precheck.py 的四項第 1 層流程檢查。

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


def _工單(status="Done", created="2026-01-01T09:00+08:00", closed="2026-01-02T09:00+08:00", 內文=""):
    return (
        "# [Task ID: MOD-DEV-BE-001] 測試工單\n\n"
        "**🔗 依附母任務 (Parent Task ID):** —\n"
        "**🏷️ 任務類型 (Task Type):** queue_agent\n"
        "**👤 負責人 (Assignee):** backend-engineer\n"
        f"**🚥 任務狀態 (Status):** {status}\n"
        f"**📅 建立時間 (Created):** {created}\n"
        f"**✅ 完成時間 (Closed):** {closed}\n"
        "**🔀 審查載體編號 (PR/MR):** —\n\n"
        "## 1. 任務描述 (Description)\n\n"
        + 內文
    )


@pytest.fixture
def 乾淨專案(bare_install: Path, tmp_path: Path) -> Path:
    """裝好 kit、鋪一張合法工單、BACKLOG 已重生——四項檢查都應該綠。"""
    target = tmp_path / "clean"
    shutil.copytree(bare_install, target)
    shutil.copytree(target / "docs/features/_TEMPLATE", target / "docs/features/my_module")
    (target / TASK).write_text(_工單(), encoding="utf-8")
    重生(target)
    return target


def 重生(專案: Path):
    result = run_script(專案, "scan_backlog.py", "--format", "backlog", "--output", BACKLOG)
    assert result.returncode == 0, result.stderr


def test_乾淨專案四項全綠(乾淨專案: Path):
    result = 跑(乾淨專案)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("✅") == 4, result.stdout


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


def test_四項互不短路(乾淨專案: Path):
    """第一項紅就停會讓修復迴圈變成跑四趟。"""
    (乾淨專案 / TASK).write_text(
        _工單(status="Doen", closed="2026年1月2日", 內文="[死的](沒有這個檔.md)\n"),
        encoding="utf-8",
    )
    # 刻意不重生 BACKLOG，讓四項同時紅
    result = 跑(乾淨專案)
    assert result.returncode != 0
    assert result.stdout.count("❌") == 4, result.stdout


# ── 防假紅燈的迴歸 ──────────────────────────────────────────────


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
