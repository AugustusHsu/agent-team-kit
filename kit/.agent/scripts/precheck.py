#!/usr/bin/env python3
"""
第 1 層流程檢查腳本 (precheck.py)

檢查「流程有沒有被遵守」，不跑專案自己的單元測試——後者是第 2 層，
只有專案自己知道要跑什麼。本腳本的輸入全在 repo 內，跟技術棧無關。

七項檢查（見 docs/standards/git_workflow.md §8）：
  1. BACKLOG 是否過期——重跑產生器比對現檔
  2. 工單 Status 值是否合法
  3. Created / Closed 是否為 ISO 8601，且 Closed 不早於 Created
  4. 文件相對連結是否指向存在的檔案
  5. Status 為 Done 卻沒填 Closed
  6. AC 全數打勾卻還沒結案
  7. 未結案工單的 Assignee 是否對應得到實際存在的 skill

使用方式:
  python3 .agent/scripts/precheck.py            # 全部檢查
  python3 .agent/scripts/precheck.py --list     # 只列出檢查項目

全部通過回傳 0，任一項失敗回傳 1。各項互不短路，一次跑完一起回報。
只用標準函式庫：裝了 kit 的專案不一定有 uv 或任何第三方套件。
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scan_backlog as sb  # noqa: E402  （必須在 sys.path 調整之後）

BACKLOG_PATH = "docs/development/BACKLOG.md"

# 未結案的空值寫法。工單範本用「—」，但手寫時各種破折號都出現過。
EMPTY_VALUES = {"", "-", "—", "–", "None", "N/A", "TBD"}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")

# 樣板檔裡的佔位路徑不是真連結，例如 reviews/{TaskID}.md、<模組>/prd.md
PLACEHOLDER_CHARS = ("{", "}", "<", ">")
PLACEHOLDER_WORDS = {"路徑", "relative/path"}

# 工單的 AC 打勾格式：`- [ ] AC-01：…` / `- [x] …`
CHECKBOX_RE = re.compile(r"^\s*[-*] \[([ xX])\]", re.MULTILINE)

# 允許 AC 全打勾卻不是 Done 的狀態。Canceled 的工單常常是外部前提消失，
# 該做的都做了才被喊停，逼它把勾拿掉只會是造假。
AC_EXEMPT_STATUSES = {"Done", "Canceled"}

# 工單範本明列的非角色 Assignee：使用者親自處理。留空（EMPTY_VALUES）另行放行。
MANUAL_ASSIGNEE = "manual_user"


class Finding:
    """一筆檢查失敗。location 要能讓人直接跳到出問題的地方。"""

    def __init__(self, location, message):
        self.location = location
        self.message = message

    def __str__(self):
        return f"{self.location}：{self.message}"


def strip_code(text):
    """
    移除 fenced code block 與行內 code span，回傳與原文行數相同的文字。

    為什麼要做這件事：文件常把連結語法當成「例子」引用，例如
    PEV-DEV-AGENT-008 用 `[DN-007](DN-007_ci_gate.md)` 說明 DN 的依賴欄位長什麼樣。
    那不是連結，是被引用的字串——照抓會產生假紅燈，而假紅燈會逼作者
    改成不自然的寫法來閃避檢查（PEV-DEV-AGENT-016 就被逼過一次）。

    行數必須保持一致，否則回報的行號會對不上原始檔案。
    """
    out = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE_RE.sub("", line))
    return "\n".join(out)


def is_empty(value):
    return value is None or str(value).strip() in EMPTY_VALUES


def parse_iso(value):
    """
    回傳 (datetime, 是否只有日期)；解析失敗回傳 None。

    純日期（2026-08-16）本身就是合法 ISO 8601，不該判成格式錯誤。
    """
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed, "T" not in text


def check_backlog_current(root):
    """重跑產生器比對現檔。這是純函數檢查：同樣的工單一定生出同樣的 BACKLOG。"""
    backlog = root / BACKLOG_PATH
    if not backlog.exists():
        return [
            Finding(
                BACKLOG_PATH,
                "檔案不存在；請跑 "
                "`python3 .agent/scripts/scan_backlog.py --format backlog "
                f"--output {BACKLOG_PATH}`",
            )
        ]

    tasks = sb.scan_all_tasks(root)
    if not tasks:
        return []

    generated = sb.format_backlog_markdown(root, tasks, 10, output_path=str(backlog))
    if generated.rstrip("\n") == backlog.read_text(encoding="utf-8").rstrip("\n"):
        return []
    return [
        Finding(
            BACKLOG_PATH,
            "內容與工單現況不一致（改完工單忘了重生）；請跑 "
            "`python3 .agent/scripts/scan_backlog.py --format backlog "
            f"--output {BACKLOG_PATH}`",
        )
    ]


def check_status_values(root):
    """Status 打錯字不會讓任何東西壞掉，工單只是從所有視圖裡靜默消失。"""
    findings = []
    legal = sorted(sb.STATUS_ICONS)
    for task in iter_tasks(root):
        status = task.get("status")
        if status is None:
            findings.append(Finding(rel(root, task), "找不到 Status 欄位"))
        elif status not in sb.STATUS_ICONS:
            findings.append(
                Finding(rel(root, task), f"Status 值不合法：{status!r}；合法值為 {legal}")
            )
    return findings


def check_timestamps(root):
    """Created / Closed 要是 ISO 8601，且 Closed 不早於 Created。"""
    findings = []
    for task in iter_tasks(root):
        location = rel(root, task)
        parsed = {}
        for field in ("created", "closed"):
            raw = task.get(field)
            if is_empty(raw):
                continue
            result = parse_iso(raw)
            if result is None:
                findings.append(Finding(location, f"{field} 不是 ISO 8601：{raw!r}"))
            else:
                parsed[field] = result

        if "created" in parsed and "closed" in parsed:
            (created, created_is_date), (closed, closed_is_date) = (
                parsed["created"],
                parsed["closed"],
            )
            # 任一邊只有日期時降到日期粒度比較：精度較粗的那個值
            # 推不出「早於」，硬比會把 2026-08-16 當成午夜而產生假紅燈。
            if created_is_date or closed_is_date:
                out_of_order = closed.date() < created.date()
            else:
                out_of_order = aware(closed) < aware(created)
            if out_of_order:
                findings.append(
                    Finding(
                        location,
                        f"Closed 早於 Created：{task['closed']} < {task['created']}",
                    )
                )
    return findings


def check_dead_links(root):
    """只掃 docs/ 底下的 .md：專案根目錄可能有 node_modules 之類的大量無關檔案。"""
    findings = []
    for md in sorted((root / "docs").rglob("*.md")):
        text = strip_code(md.read_text(encoding="utf-8"))
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in LINK_RE.finditer(line):
                target = match.group(1).split("#")[0].strip()
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target in PLACEHOLDER_WORDS:
                    continue
                if any(char in target for char in PLACEHOLDER_CHARS):
                    continue
                if not (md.parent / target).exists():
                    findings.append(
                        Finding(f"{md.relative_to(root)}:{lineno}", f"連結指向不存在的檔案：{target}")
                    )
    return findings


def check_closed_filled(root):
    """Status 是 Done 卻沒填 Closed。

    這不會有任何錯誤：`scan_backlog.py` 照樣把它列進「近期結案」，只是完成時間欄空白，
    而排序用的鍵拿不到值——工單於是沉到列表底部，看起來像最舊的一張。
    PEV-DEV-AGENT-002 結案時就漏填過一次，當時四項檢查全綠。
    """
    findings = []
    for task in iter_tasks(root):
        if task.get("status") == "Done" and is_empty(task.get("closed")):
            findings.append(Finding(rel(root, task), "Status 為 Done 但 Closed 留空"))
    return findings


def check_ac_matches_status(root):
    """AC 全打勾卻還沒結案——做完了沒關帳，帳面上這張單還卡著。

    KIT-DEV-AGENT-001 的 14 條 AC 全部打勾、交付物全部進了主線，Status 卻在
    `In Review` 躺了兩天，直到人工清帳才發現。原本的四項檢查沒有一項看得到它。

    邊界：只看「全打勾」這個形狀，看不出勾是不是誠實打的——那要跑專案測試，
    屬第 2 層。這一項抓的是純粹的漏關帳。
    """
    findings = []
    for task in iter_tasks(root):
        status = task.get("status")
        if status is None or status in AC_EXEMPT_STATUSES:
            continue
        boxes = CHECKBOX_RE.findall(Path(task["file"]).read_text(encoding="utf-8"))
        if boxes and all(box.lower() == "x" for box in boxes):
            findings.append(
                Finding(
                    rel(root, task),
                    f"{len(boxes)} 個核取方塊全數打勾，Status 卻還是 {status!r}",
                )
            )
    return findings


def available_roles(root):
    """合法角色讀自 `.agent/skills/` 的實際目錄，回傳目錄名集合；沒有該目錄回傳 None。

    **不寫死清單**：kit 的定位是可安裝到任何專案，而專案可以自己加 skill。
    寫死的話，使用者新增一個自訂角色就會被判成不合法——那種誤報會讓人
    直接關掉整項檢查，比沒有這項檢查更糟。
    """
    skills = root / ".agent" / "skills"
    if not skills.is_dir():
        return None
    return {entry.name for entry in skills.iterdir() if entry.is_dir()}


def assignee_lineno(task):
    """Assignee 欄位所在行號；找不到時回 0（呼叫端會退回只指檔案）。"""
    text = Path(task["file"]).read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "負責人 (Assignee)" in line:
            return lineno
    return 0


def check_assignee_valid(root):
    """Assignee 填了不存在的角色——那張工單於是永遠不會被正確的角色接手。

    這是最容易自動檢查、也最不容易人工發現的一類缺陷：打錯不會有任何執行期錯誤，
    BACKLOG 照樣生成、其餘六項照樣全綠。PEV-DEV-AGENT-012／013 把
    `backend-developer` 寫成 `backend-engineer`，一路存活到 025 做全角色盤點才撞見。

    **只檢查未結案工單**：team_protocol.md §1.11 規定已結案工單是歷史紀錄，
    不改它也不引用它。涵蓋全部工單的話，012／013 會製造一個
    只能靠違反 §1.11 才解得掉的紅燈。沿用 AC_EXEMPT_STATUSES，不另立一套。

    邊界：只驗「這個角色存在嗎」，不驗「這個角色適合這張工單嗎」——
    後者是判斷不是事實，不該進閘門。
    """
    roles = available_roles(root)
    if roles is None:
        # 沒有 .agent/skills/ 就沒有判準。這不是錯誤：kit 尚未安裝完成時
        # 報一整排紅燈只會蓋掉真正的問題。
        return []

    legal = sorted(roles | {MANUAL_ASSIGNEE})
    findings = []
    for task in iter_tasks(root):
        if task.get("status") in AC_EXEMPT_STATUSES:
            continue
        assignee = task.get("assignee")
        if is_empty(assignee):
            continue
        value = str(assignee).strip()
        if value in roles or value == MANUAL_ASSIGNEE:
            continue
        lineno = assignee_lineno(task)
        location = f"{rel(root, task)}:{lineno}" if lineno else rel(root, task)
        findings.append(
            Finding(
                location,
                f"Assignee 不是實際存在的角色：{value!r}；"
                f"合法值為 {legal}，或留空填 —",
            )
        )
    return findings


def aware(value):
    return value if value.tzinfo else value.replace(tzinfo=sb.TZ_TAIPEI)


def iter_tasks(root):
    for tasks in sb.scan_all_tasks(root).values():
        for task in tasks:
            yield task


def rel(root, task):
    path = Path(task["file"])
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


CHECKS = [
    ("BACKLOG 是否為最新", check_backlog_current),
    ("工單 Status 值是否合法", check_status_values),
    ("工單時間戳是否正確", check_timestamps),
    ("文件是否有死連結", check_dead_links),
    ("結案工單是否填了 Closed", check_closed_filled),
    ("AC 全打勾的工單是否已結案", check_ac_matches_status),
    ("未結案工單的 Assignee 是否合法", check_assignee_valid),
]


def main():
    parser = argparse.ArgumentParser(
        description="第 1 層流程檢查 — 檢查流程有沒有被遵守，不跑專案自己的測試"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="只列出檢查項目，不實際執行",
    )
    args = parser.parse_args()

    if args.list:
        for name, _ in CHECKS:
            print(f"- {name}")
        return 0

    root = sb.find_project_root()
    failed = 0

    # 刻意不短路：一次跑完全部。第一項紅就停會讓修復迴圈變成一項跑一趟。
    for name, check in CHECKS:
        findings = check(root)
        if findings:
            failed += 1
            print(f"❌ {name}")
            for finding in findings:
                print(f"   {finding}")
        else:
            print(f"✅ {name}")

    if failed:
        print(f"\n{failed}/{len(CHECKS)} 項檢查未通過。", file=sys.stderr)
        return 1
    print(f"\n{len(CHECKS)} 項檢查全部通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
