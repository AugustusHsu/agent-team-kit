#!/usr/bin/env python3
"""
工單日期回填腳本 (Migration Script)

透過 git log 推算每張工單的建立時間與完成時間，批次回填至工單 .md 檔案。

建立時間 (Created)：取該檔案首次被 git commit 的時間
完成時間 (Closed)：取該檔案 Status 最新一次被改為 Done 或 Canceled 的 commit 時間
  - 若工單曾被重新開啟再關閉，以最新的關閉時間為準

使用方式:
  python3 .agent/scripts/migrate_dates.py                    # 預覽模式（不修改）
  python3 .agent/scripts/migrate_dates.py --apply            # 實際執行修改
  python3 .agent/scripts/migrate_dates.py --project example_module --apply
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 定義台北時區 (UTC+8)
TZ_TAIPEI = timezone(timedelta(hours=8))

# 正則：匹配工單中的 Status、Created、Closed 欄位
RE_STATUS = re.compile(r"^\*\*🚥\s*任務狀態\s*\(Status\):\*\*\s*(.+)$", re.MULTILINE)
RE_CREATED = re.compile(r"^\*\*📅\s*建立時間\s*\(Created\):\*\*\s*(.+)$", re.MULTILINE)
RE_CLOSED = re.compile(r"^\*\*✅\s*完成時間\s*\(Closed\):\*\*\s*(.+)$", re.MULTILINE)


def find_project_root():
    """從腳本位置往上尋找專案根目錄"""
    candidates = [
        Path.cwd(),
        Path(__file__).resolve().parent.parent.parent,
    ]
    for candidate in candidates:
        if (candidate / "docs" / "features").is_dir():
            return candidate
    print("❌ 無法定位專案根目錄。", file=sys.stderr)
    sys.exit(1)


def git_first_commit_date(filepath, root):
    """取得檔案首次被 git commit 的時間"""
    try:
        # --follow 追蹤重新命名，--diff-filter=A 只看新增
        result = subprocess.run(
            [
                "git",
                "log",
                "--follow",
                "--diff-filter=A",
                "--format=%aI",
                "--",
                str(filepath),
            ],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        if result.returncode == 0 and result.stdout.strip():
            # 可能有多行（重命名情況），取最早的一行（最後一行）
            lines = result.stdout.strip().split("\n")
            date_str = lines[-1].strip()
            return datetime.fromisoformat(date_str).astimezone(TZ_TAIPEI)
    except Exception as e:
        print(f"  ⚠️ git log 失敗 ({filepath}): {e}", file=sys.stderr)
    return None


def git_latest_done_date(filepath, root):
    """
    取得檔案 Status 最近一次被改為 Done 或 Canceled 的 commit 時間。
    策略：逐筆檢查 commit 的 diff，找到包含 Status 改為 Done/Canceled 的最新 commit。
    為求效率，使用 git log -S 搜尋包含 'Done' 或 'Canceled' 的 commit。
    以最新為主（處理重複開啟的情況）。
    """
    try:
        # 方法 1：用 git log -S 搜尋包含 Status 關鍵字的 commit
        result = subprocess.run(
            [
                "git",
                "log",
                "-n",
                "1",
                "--format=%aI",
                "-S",
                "Done",
                "--",
                str(filepath),
            ],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        done_date = None
        if result.returncode == 0 and result.stdout.strip():
            done_date = datetime.fromisoformat(result.stdout.strip().split("\n")[0]).astimezone(
                TZ_TAIPEI
            )

        # 同樣搜尋 Canceled
        result2 = subprocess.run(
            [
                "git",
                "log",
                "-n",
                "1",
                "--format=%aI",
                "-S",
                "Canceled",
                "--",
                str(filepath),
            ],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        canceled_date = None
        if result2.returncode == 0 and result2.stdout.strip():
            canceled_date = datetime.fromisoformat(
                result2.stdout.strip().split("\n")[0]
            ).astimezone(TZ_TAIPEI)

        # 取最新的日期（處理可能同時有 Done 和 Canceled 記錄的情況）
        candidates = [d for d in [done_date, canceled_date] if d is not None]
        if candidates:
            return max(candidates)

    except Exception as e:
        print(f"  ⚠️ git log 失敗 ({filepath}): {e}", file=sys.stderr)

    # 方法 2（Fallback）：若 git -S 找不到，使用最後修改時間
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-n",
                "1",
                "--format=%aI",
                "--",
                str(filepath),
            ],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        if result.returncode == 0 and result.stdout.strip():
            return datetime.fromisoformat(result.stdout.strip().split("\n")[0]).astimezone(
                TZ_TAIPEI
            )
    except Exception:
        pass

    return None


def format_datetime(dt):
    """將 datetime 格式化為 ISO 8601（精確到分鐘 + 時區）"""
    if dt is None:
        return None
    # 格式：2026-04-22T16:04+08:00
    return dt.strftime("%Y-%m-%dT%H:%M") + "+08:00"


def process_task_file(filepath, root, apply=False):
    """
    處理單一工單檔案，推算日期並回填
    回傳 (task_id, created, closed, was_modified)
    """
    content = filepath.read_text(encoding="utf-8")

    # 取得現有 Status
    status_match = RE_STATUS.search(content)
    status = status_match.group(1).strip() if status_match else ""

    # 判斷是否需要回填
    created_match = RE_CREATED.search(content)
    closed_match = RE_CLOSED.search(content)

    # 檢查是否已有欄位
    has_created_field = created_match is not None
    has_closed_field = closed_match is not None

    # 取得當前值
    current_created = created_match.group(1).strip() if created_match else None
    current_closed = closed_match.group(1).strip() if closed_match else None

    # 判斷是否需要推算
    need_created = (
        not has_created_field
        or not current_created
        or current_created in ("—", "-", "{YYYY-MM-DDTHH:MM+08:00}")
    )
    need_closed = status in ("Done", "Canceled") and (
        not has_closed_field or not current_closed or current_closed in ("—", "-")
    )

    created_str = None
    closed_str = None
    modified = False

    # 推算建立時間
    if need_created:
        created_dt = git_first_commit_date(filepath, root)
        created_str = format_datetime(created_dt)

    # 推算完成時間（僅 Done/Canceled）
    if need_closed:
        closed_dt = git_latest_done_date(filepath, root)
        closed_str = format_datetime(closed_dt)

    # 回填至檔案
    if apply and (created_str or closed_str):
        new_content = content

        if created_str:
            if has_created_field:
                # 替換既有欄位值
                new_content = RE_CREATED.sub(
                    f"**📅 建立時間 (Created):** {created_str}",
                    new_content,
                )
            else:
                # 在 Status 欄位後插入新欄位
                new_content = RE_STATUS.sub(
                    lambda m: (f"{m.group(0)}\n" f"**📅 建立時間 (Created):** {created_str}"),
                    new_content,
                )

        if closed_str:
            if has_closed_field:
                new_content = RE_CLOSED.sub(
                    f"**✅ 完成時間 (Closed):** {closed_str}",
                    new_content,
                )
            else:
                # 在 Created 欄位後插入（若有）或在 Status 後插入
                if RE_CREATED.search(new_content):
                    new_content = RE_CREATED.sub(
                        lambda m: (f"{m.group(0)}\n" f"**✅ 完成時間 (Closed):** {closed_str}"),
                        new_content,
                    )
                else:
                    new_content = RE_STATUS.sub(
                        lambda m: (f"{m.group(0)}\n" f"**✅ 完成時間 (Closed):** {closed_str}"),
                        new_content,
                    )

        if new_content != content:
            filepath.write_text(new_content, encoding="utf-8")
            modified = True

    return {
        "file": filepath.stem,
        "status": status,
        "created": created_str or current_created,
        "closed": closed_str or current_closed,
        "modified": modified,
        "needed_created": need_created,
        "needed_closed": need_closed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="工單日期回填腳本 — 透過 git log 推算並回填建立與完成時間"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="僅處理指定專案",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="實際執行修改（未指定時為預覽模式）",
    )

    args = parser.parse_args()
    root = find_project_root()
    features_base = root / "docs" / "features"

    if not features_base.is_dir():
        print(f"❌ 功能模組目錄不存在: {features_base}", file=sys.stderr)
        sys.exit(1)

    mode = "🔧 執行模式" if args.apply else "👀 預覽模式（加 --apply 執行修改）"
    print(f"\n{'=' * 60}")
    print(f"  工單日期回填腳本 — {mode}")
    print(f"{'=' * 60}\n")

    total_files = 0
    total_modified = 0
    total_need_created = 0
    total_need_closed = 0

    for feature_dir in sorted(features_base.iterdir()):
        if not feature_dir.is_dir():
            continue
        # 跳過骨架目錄（如 _TEMPLATE/）——與底下「檔名以 _ 開頭者不算工單」同一條規則
        if feature_dir.name.startswith("_"):
            continue
        tasks_dir = feature_dir / "tasks"
        if not tasks_dir.is_dir():
            continue
        if args.project and feature_dir.name != args.project:
            continue

        print(f"📁 功能模組: {feature_dir.name}")
        print(f"   {'—' * 40}")

        for md_file in sorted(tasks_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            total_files += 1
            result = process_task_file(md_file, root, apply=args.apply)

            # 僅顯示需要修改的檔案
            if result["needed_created"] or result["needed_closed"]:
                marker = "✏️" if result["modified"] else "📋"
                if result["modified"]:
                    total_modified += 1
                print(f"   {marker} {result['file']}: " f"Status={result['status']}")
                if result["needed_created"]:
                    total_need_created += 1
                    print(f"      Created → {result['created'] or '(無法推算)'}")
                if result["needed_closed"]:
                    total_need_closed += 1
                    print(f"      Closed  → {result['closed'] or '(無法推算)'}")

        print()

    print(f"{'=' * 60}")
    print("  📊 統計")
    print(f"  掃描檔案: {total_files}")
    print(f"  需回填 Created: {total_need_created}")
    print(f"  需回填 Closed: {total_need_closed}")
    if args.apply:
        print(f"  已修改檔案: {total_modified}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
