#!/usr/bin/env python3
"""
BACKLOG 自動掃描腳本

掃描 docs/features/*/tasks/ 下所有功能模組的工單 .md 檔案，
解析 metadata 並輸出結構化資料供 Agent 消費。

使用方式:
  python3 .agent/scripts/scan_backlog.py                          # 全部專案 JSON
  python3 .agent/scripts/scan_backlog.py --project example_module
  python3 .agent/scripts/scan_backlog.py --format summary
  python3 .agent/scripts/scan_backlog.py --format backlog --recent-days 7 --recent-limit 10
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 定義台北時區 (UTC+8)
TZ_TAIPEI = timezone(timedelta(hours=8))

# 工單 metadata 正則表達式
PATTERNS = {
    "task_id": re.compile(r"^#\s*\[Task ID:\s*([^\]]+)\]\s*(.+)$", re.MULTILINE),
    "parent_id": re.compile(r"\*\*🔗\s*依附母任務\s*\(Parent Task ID\):\*\*\s*(.+)$", re.MULTILINE),
    "task_type": re.compile(r"\*\*🏷️\s*任務類型\s*\(Task Type\):\*\*\s*(.+)$", re.MULTILINE),
    "assignee": re.compile(r"\*\*👤\s*負責人\s*\(Assignee\):\*\*\s*(.+)$", re.MULTILINE),
    "status": re.compile(r"\*\*🚥\s*任務狀態\s*\(Status\):\*\*\s*(.+)$", re.MULTILINE),
    "created": re.compile(r"\*\*📅\s*建立時間\s*\(Created\):\*\*\s*(.+)$", re.MULTILINE),
    "closed": re.compile(r"\*\*✅\s*完成時間\s*\(Closed\):\*\*\s*(.+)$", re.MULTILINE),
}

# 狀態圖示對照
STATUS_ICONS = {
    "In Progress": "🔵",
    "Ready": "🟢",
    "In Review": "🟡",
    "Pending": "⏳",
    "Done": "✅",
    "Canceled": "🚫",
}

# 狀態排序優先級（用於分類）
STATUS_PRIORITY = {
    "In Progress": 0,
    "Ready": 1,
    "In Review": 2,
    "Pending": 3,
    "Done": 4,
    "Canceled": 5,
}


def find_project_root():
    """
    從腳本所在位置往上尋找專案根目錄
    以 docs/features/ 目錄的存在性作為判斷依據
    """
    # 嘗試從 CWD 開始
    candidates = [
        Path.cwd(),
        Path(__file__).resolve().parent.parent.parent,  # .agent/scripts/ → 根目錄
    ]
    for candidate in candidates:
        if (candidate / "docs" / "features").is_dir():
            return candidate
    print("❌ 無法定位專案根目錄，請確認從專案目錄內執行。", file=sys.stderr)
    sys.exit(1)


def parse_task_file(filepath):
    """
    解析單一工單 .md 檔案，提取 metadata 欄位
    回傳 dict 或 None（解析失敗時）
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️ 無法讀取 {filepath}: {e}", file=sys.stderr)
        return None

    result = {"file": str(filepath), "filename": filepath.stem}

    # 解析 Task ID 與標題（從 H1 標題行）
    match = PATTERNS["task_id"].search(content)
    if match:
        result["task_id"] = match.group(1).strip()
        result["title"] = match.group(2).strip()
    else:
        # 若標題格式不符，使用檔名作為 Task ID
        result["task_id"] = filepath.stem
        result["title"] = "(標題解析失敗)"

    # 解析其他 metadata 欄位
    for key in ["parent_id", "task_type", "assignee", "status", "created", "closed"]:
        match = PATTERNS[key].search(content)
        if match:
            value = match.group(1).strip()
            # 清理可能的多餘空白與 \r
            result[key] = value.replace("\r", "")
        else:
            result[key] = None

    # 標準化 status（移除多餘的描述文字，如「Canceled (因...）」）
    if result.get("status"):
        raw_status = result["status"]
        # 精確匹配已知的狀態值
        for known_status in STATUS_PRIORITY:
            if known_status in raw_status:
                result["status"] = known_status
                break

    return result


def parse_closed_datetime(closed_str):
    """
    嘗試將 Closed 欄位的字串解析為 datetime 物件
    支援 ISO 8601 格式（如 2026-04-22T16:04+08:00）
    回傳 datetime 或 None
    """
    if not closed_str or closed_str in ("—", "-", "N/A", "null"):
        return None
    try:
        # 嘗試帶時區的 ISO 格式
        dt = datetime.fromisoformat(closed_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ_TAIPEI)
        return dt
    except (ValueError, TypeError):
        pass
    try:
        # 嘗試簡單日期格式
        return datetime.strptime(closed_str, "%Y-%m-%d").replace(tzinfo=TZ_TAIPEI)
    except (ValueError, TypeError):
        return None


def scan_all_tasks(root, project_filter=None):
    """
    掃描 docs/features/*/tasks/ 下所有（或指定）功能模組的工單
    回傳 {feature_name: [task_dict, ...], ...}
    """
    features_base = root / "docs" / "features"
    results = {}

    if not features_base.is_dir():
        print(f"❌ 功能模組目錄不存在: {features_base}", file=sys.stderr)
        sys.exit(1)

    # 遍歷功能模組子目錄
    for feature_dir in sorted(features_base.iterdir()):
        if not feature_dir.is_dir():
            continue
        tasks_dir = feature_dir / "tasks"
        if not tasks_dir.is_dir():
            continue
        feature_name = feature_dir.name

        # 若指定了專案篩選
        if project_filter and feature_name != project_filter:
            continue

        tasks = []
        for md_file in sorted(tasks_dir.glob("*.md")):
            # 跳過索引檔案
            if md_file.name.startswith("_"):
                continue
            task = parse_task_file(md_file)
            if task:
                task["project"] = feature_name
                tasks.append(task)

        results[feature_name] = tasks

    return results


def classify_tasks(tasks, recent_days=7, recent_limit=10):
    """
    將工單依狀態分類為四大區塊
    近期結案區塊僅顯示最近 N 天內的工單，上限 M 筆
    """
    now = datetime.now(TZ_TAIPEI)
    cutoff = now - timedelta(days=recent_days)

    classified = {
        "current_sprint": [],  # In Progress + Ready
        "in_review": [],  # In Review
        "product_backlog": [],  # Pending
        "recent_closed": [],  # 近期 Done/Canceled
        "archived": [],  # 超出近期範圍的 Done/Canceled
    }

    for task in tasks:
        status = task.get("status", "")
        if status in ("In Progress", "Ready"):
            classified["current_sprint"].append(task)
        elif status == "In Review":
            classified["in_review"].append(task)
        elif status == "Pending":
            classified["product_backlog"].append(task)
        elif status in ("Done", "Canceled"):
            closed_dt = parse_closed_datetime(task.get("closed"))
            if closed_dt and closed_dt >= cutoff:
                classified["recent_closed"].append(task)
            else:
                classified["archived"].append(task)

    # 當前衝刺：In Progress 優先，其次 Ready，同狀態內按 Task ID 排序
    classified["current_sprint"].sort(
        key=lambda t: (
            STATUS_PRIORITY.get(t.get("status", ""), 99),
            t.get("task_id", ""),
        )
    )

    # 近期結案：按完成時間倒序排列，取前 N 筆
    classified["recent_closed"].sort(
        key=lambda t: parse_closed_datetime(t.get("closed"))
        or datetime.min.replace(tzinfo=TZ_TAIPEI),
        reverse=True,
    )
    # 超出上限的移入歸檔
    if len(classified["recent_closed"]) > recent_limit:
        classified["archived"].extend(classified["recent_closed"][recent_limit:])
        classified["recent_closed"] = classified["recent_closed"][:recent_limit]

    return classified


def compute_stats(all_project_tasks):
    """
    計算按專案分組的統計摘要
    回傳 {project_name: {status: count, ...}, ...}
    """
    stats = {}
    for project, tasks in all_project_tasks.items():
        project_stats = {}
        for task in tasks:
            status = task.get("status", "Unknown")
            project_stats[status] = project_stats.get(status, 0) + 1
        stats[project] = project_stats
    return stats


def format_json(all_project_tasks, recent_days, recent_limit):
    """
    輸出完整 JSON 格式，包含分類與統計
    """
    output = {}
    for project, tasks in all_project_tasks.items():
        classified = classify_tasks(tasks, recent_days, recent_limit)
        output[project] = {
            "total": len(tasks),
            "classified": {
                k: [
                    {
                        "task_id": t["task_id"],
                        "title": t["title"],
                        "assignee": t.get("assignee"),
                        "status": t.get("status"),
                        "parent_id": t.get("parent_id"),
                        "created": t.get("created"),
                        "closed": t.get("closed"),
                    }
                    for t in v
                ]
                for k, v in classified.items()
            },
            "stats": {},
        }
        # 統計各狀態數量
        for task in tasks:
            s = task.get("status", "Unknown")
            output[project]["stats"][s] = output[project]["stats"].get(s, 0) + 1

    return json.dumps(output, ensure_ascii=False, indent=2)


def extract_existing_icebox(root, output_path=None):
    """
    從現有的 BACKLOG.md 中提取 Icebox 區塊的內容，若不存在則回傳預設內容
    """
    if output_path:
        backlog_path = Path(output_path)
    else:
        backlog_path = root / "docs" / "development" / "BACKLOG.md"
    default_icebox = [
        "> 暫時擱置、待未來進一步討論或需要先行更新架構文件 (PRD/API Specs) " "的想法與功能點。",
        "",
        "| 項目 | 描述 | 備註 |",
        "|---|---|---|",
        "| *(此區塊需手動維護，腳本不會覆寫)* | — | — |",
        "",
    ]
    if not backlog_path.exists():
        return default_icebox

    try:
        content = backlog_path.read_text(encoding="utf-8")
        parts = content.split("## 🧊 冰箱 (Icebox)")
        if len(parts) > 1:
            icebox_content_raw = parts[1]
            # 尋找下一個 ## 標題，若有則截斷
            next_header_idx = icebox_content_raw.find("\n## ")
            if next_header_idx != -1:
                icebox_content = icebox_content_raw[:next_header_idx].strip()
            else:
                icebox_content = icebox_content_raw.strip()

            if icebox_content:
                return icebox_content.split("\n")
    except Exception:
        pass

    return default_icebox


def format_summary(all_project_tasks):
    """
    輸出精簡文字摘要
    """
    lines = ["📊 BACKLOG 統計摘要", "=" * 40]
    stats = compute_stats(all_project_tasks)

    for project, project_stats in stats.items():
        total = sum(project_stats.values())
        lines.append(f"\n### {project} (共 {total} 張)")
        # 依狀態優先級排序
        for status in sorted(project_stats.keys(), key=lambda s: STATUS_PRIORITY.get(s, 99)):
            count = project_stats[status]
            icon = STATUS_ICONS.get(status, "❓")
            pct = f"{count / total * 100:.1f}%" if total > 0 else "0%"
            lines.append(f"  {icon} {status}: {count} ({pct})")

    return "\n".join(lines)


def format_backlog_markdown(root, all_project_tasks, recent_days, recent_limit, output_path=None):
    """
    輸出符合 backlog_template 格式的完整 Markdown
    """
    now = datetime.now(TZ_TAIPEI)
    all_tasks = []
    for tasks in all_project_tasks.values():
        all_tasks.extend(tasks)

    classified = classify_tasks(all_tasks, recent_days, recent_limit)
    total = len(all_tasks)

    lines = []
    lines.append("# 📋 待辦總表 (Backlog)")
    lines.append("")
    lines.append(f"> **最後更新時間**：{now.strftime('%Y-%m-%d')}")
    lines.append("> **工單來源目錄**：`docs/features/*/tasks/`")
    lines.append(f"> **工單總數**：{total} 張")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 當前衝刺
    lines.append("## 🏃‍♂️ 當前衝刺 (Current Sprint)")
    lines.append("")
    lines.append("> 包含狀態為 `In Progress` 或 `Ready` 的工單。")
    lines.append("")
    sprint = classified["current_sprint"]
    if sprint:
        lines.append("| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |")
        lines.append("|---|---------|------|------|-------------------|---------------|")
        in_progress_count = 0
        ready_count = 0
        for i, t in enumerate(sprint, 1):
            icon = STATUS_ICONS.get(t["status"], "❓")
            proj = t.get("project", "—")
            lines.append(
                f"| {i} | {t['task_id']} | {t['title']} | {proj} "
                f"| {t.get('assignee', '—')} | {icon} {t['status']} |"
            )
            if t["status"] == "In Progress":
                in_progress_count += 1
            elif t["status"] == "Ready":
                ready_count += 1
        lines.append("")
        lines.append(
            f"**小計**：{len(sprint)} 張"
            f"（In Progress: {in_progress_count} / Ready: {ready_count}）"
        )
    else:
        lines.append("*(無)*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 審查中
    lines.append("## ⏳ 審查中 (In Review)")
    lines.append("")
    lines.append("> 開發已完成，等待 Code Review 或驗收確認的工單。")
    lines.append("")
    review = classified["in_review"]
    if review:
        lines.append("| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |")
        lines.append("|---|---------|------|------|-------------------|---------------|")
        for i, t in enumerate(review, 1):
            proj = t.get("project", "—")
            lines.append(
                f"| {i} | {t['task_id']} | {t['title']} | {proj} "
                f"| {t.get('assignee', '—')} | In Review |"
            )
        lines.append("")
        lines.append(f"**小計**：{len(review)} 張")
    else:
        lines.append("*(無)*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 產品待辦
    lines.append("## 🧊 產品待辦 (Product Backlog)")
    lines.append("")
    lines.append("> 包含狀態為 `Pending` 的工單，等待前置條件完成或人為確認後方可開始。")
    lines.append("")
    backlog = classified["product_backlog"]
    if backlog:
        lines.append("| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |")
        lines.append("|---|---------|------|------|-------------------|---------------|")
        for i, t in enumerate(backlog, 1):
            proj = t.get("project", "—")
            lines.append(
                f"| {i} | {t['task_id']} | {t['title']} | {proj} "
                f"| {t.get('assignee', '—')} | ⏳ Pending |"
            )
        lines.append("")
        lines.append(f"**小計**：{len(backlog)} 張")
    else:
        lines.append("*(無)*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 近期結案
    lines.append("## ✅ 近期結案 (Closed)")
    lines.append("")
    lines.append(
        f"> 最近 {recent_days} 天內完成的工單（上限 {recent_limit} 筆）。"
        f"更早的結案工單可透過 `scan_backlog.py --format json` 查詢。"
    )
    lines.append("")
    recent = classified["recent_closed"]
    archived_count = len(classified["archived"])
    if recent:
        lines.append(
            "| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) " "| 完成時間 |"
        )
        lines.append(
            "|---|---------|------|------|-------------------|---------------" "|----------|"
        )
        done_count = sum(1 for t in recent if t.get("status") == "Done")
        canceled_count = sum(1 for t in recent if t.get("status") == "Canceled")
        for i, t in enumerate(recent, 1):
            icon = STATUS_ICONS.get(t["status"], "❓")
            proj = t.get("project", "—")
            closed = t.get("closed", "—") or "—"
            lines.append(
                f"| {i} | {t['task_id']} | {t['title']} | {proj} "
                f"| {t.get('assignee', '—')} | {icon} {t['status']} | {closed} |"
            )
        lines.append("")
        lines.append(
            f"**小計**：{len(recent)} 張" f"（Done: {done_count} / Canceled: {canceled_count}）"
        )
    else:
        lines.append("*(無近期結案工單)*")
    if archived_count > 0:
        lines.append("")
        lines.append(f"> 📦 另有 {archived_count} 張已歸檔工單未顯示。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 統計摘要 - 按專案分組
    lines.append("## 📊 統計摘要")
    lines.append("")
    stats = compute_stats(all_project_tasks)
    for project, project_stats in stats.items():
        proj_total = sum(project_stats.values())
        lines.append(f"### {project}")
        lines.append("")
        lines.append("| 狀態 | 數量 | 佔比 |")
        lines.append("|------|------|------|")
        for status in sorted(project_stats.keys(), key=lambda s: STATUS_PRIORITY.get(s, 99)):
            count = project_stats[status]
            icon = STATUS_ICONS.get(status, "❓")
            pct = f"{count / proj_total * 100:.1f}%" if proj_total > 0 else "0%"
            lines.append(f"| {icon} {status} | {count} | {pct} |")
        lines.append(f"| **總計** | **{proj_total}** | **100%** |")
        lines.append("")

    # 冰箱區塊（保留既有內容的提示）
    lines.append("---")
    lines.append("")
    lines.append("## 🧊 冰箱 (Icebox)")
    lines.append("")

    icebox_lines = extract_existing_icebox(root, output_path)
    lines.extend(icebox_lines)
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="BACKLOG 自動掃描腳本 — 解析工單 metadata 並輸出結構化資料"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="僅掃描指定專案（例如: example_module）",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "summary", "backlog"],
        default="json",
        help="輸出格式: json (預設), summary (精簡摘要), backlog (完整 Markdown)",
    )
    parser.add_argument(
        "--recent-days",
        type=int,
        default=7,
        help="近期結案的天數範圍（預設: 7 天）",
    )
    parser.add_argument(
        "--recent-limit",
        type=int,
        default=10,
        help="近期結案的最大顯示筆數（預設: 10 筆）",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="輸出至指定檔案（避免使用 > 導致讀取前被清空）",
    )

    args = parser.parse_args()

    root = find_project_root()
    all_tasks = scan_all_tasks(root, args.project)

    if not all_tasks:
        print("⚠️ 未找到任何工單。", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(format_json(all_tasks, args.recent_days, args.recent_limit))
    elif args.format == "summary":
        print(format_summary(all_tasks))
    elif args.format == "backlog":
        out_str = format_backlog_markdown(
            root, all_tasks, args.recent_days, args.recent_limit, args.output
        )
        if args.output:
            Path(args.output).write_text(out_str, encoding="utf-8")
        else:
            print(out_str)


if __name__ == "__main__":
    main()
