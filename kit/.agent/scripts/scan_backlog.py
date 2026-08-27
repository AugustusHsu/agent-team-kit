#!/usr/bin/env python3
"""
BACKLOG 自動掃描腳本

掃描 docs/features/*/tasks/ 下所有功能模組的工單 .md 檔案，
解析 metadata 並輸出結構化資料供 Agent 消費。

使用方式:
  python3 .agent/scripts/scan_backlog.py                          # 全部專案 JSON
  python3 .agent/scripts/scan_backlog.py --project example_module
  python3 .agent/scripts/scan_backlog.py --format summary
  python3 .agent/scripts/scan_backlog.py --format graph
  python3 .agent/scripts/scan_backlog.py --format backlog --recent-limit 10
  python3 .agent/scripts/scan_backlog.py --stale 14                # 停滯清單，只印 stdout
"""

import argparse
import heapq
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 定義台北時區 (UTC+8)
TZ_TAIPEI = timezone(timedelta(hours=8))

# 欄位值前面只吃水平空白：\s* 會連換行一起吃掉，欄位留空時
# 正則會跨行抓到下一行整行當值（PEV-DEV-AGENT-012）。
_H = r"[^\S\r\n]*"

# 工單 metadata 正則表達式
PATTERNS = {
    "task_id": re.compile(r"^#\s*\[Task ID:\s*([^\]]+)\]\s*(.+)$", re.MULTILINE),
    "parent_id": re.compile(rf"^\*\*🔗{_H}依附母任務{_H}\(Parent Task ID\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "task_type": re.compile(rf"^\*\*🏷️{_H}任務類型{_H}\(Task Type\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "assignee": re.compile(rf"^\*\*👤{_H}負責人{_H}\(Assignee\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "blocked_by": re.compile(rf"^\*\*⛓️{_H}前置工單{_H}\(Blocked By\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "write_scope": re.compile(rf"^\*\*✍️{_H}寫入範圍{_H}\(Write Scope\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "contract": re.compile(rf"^\*\*📜{_H}共用契約{_H}\(Contract\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "change_set": re.compile(rf"^\*\*🔁{_H}變更集合{_H}\(Change Set\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "phase": re.compile(rf"^\*\*🪜{_H}變更階段{_H}\(Phase\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "status": re.compile(rf"^\*\*🚥{_H}任務狀態{_H}\(Status\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "created": re.compile(rf"^\*\*📅{_H}建立時間{_H}\(Created\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "closed": re.compile(rf"^\*\*✅{_H}完成時間{_H}\(Closed\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
}

PLANNING_FIELDS = ("blocked_by", "write_scope", "contract", "change_set", "phase")
PLANNING_LABELS = {
    "blocked_by": "Blocked By",
    "write_scope": "Write Scope",
    "contract": "Contract",
    "change_set": "Change Set",
    "phase": "Phase",
}
EMPTY_METADATA = {"", "-", "—", "–", "None", "N/A", "TBD"}
TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}\b")
BACKTICK_RE = re.compile(r"`([^`]+)`")

ROUND_HEADER_RE = re.compile(r"^#\s*\[Round ID:\s*(ROUND-\d+)\]\s*(.+)$", re.MULTILINE)
ROUND_PATTERNS = {
    "status": re.compile(rf"^\*\*🚥{_H}輪次狀態{_H}\(Status\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "goal": re.compile(rf"^\*\*🎯{_H}輪次目標{_H}\(Goal\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "branch": re.compile(rf"^\*\*🌿{_H}輪次分支{_H}\(Branch\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "opening_base": re.compile(rf"^\*\*📍{_H}開輪基準{_H}\(Opening Base\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
    "review_target": re.compile(rf"^\*\*🔎{_H}整合審查對象{_H}\(Integration Review Target\):\*\*{_H}(\S.*?){_H}$", re.MULTILINE),
}
ROUND_SECTION_RE = re.compile(r"^##\s+1\.[^\n]*\n(.*?)(?=^##\s+2\.|\Z)", re.MULTILINE | re.DOTALL)
SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
VALID_PHASES = {"expand", "migrate", "contract"}

# Design Note (DN) 的 header 正則表達式
DN_ID_RE = re.compile(r"DN-(\d+)")
DN_TITLE_RE = re.compile(r"^#\s*\[(DN-\d+)\]\s*(.+?)\s*$", re.MULTILINE)
DN_STATUS_RE = re.compile(r"^\*\*🚥\s*狀態\s*\(Status\):\*\*\s*(.+?)\s*$", re.MULTILINE)
DN_DEPENDS_RE = re.compile(r"^\*\*🔗\s*依賴\s*\(Depends on\):\*\*\s*(.+?)\s*$", re.MULTILINE)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")

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


def is_empty_metadata(value):
    """`—（補充說明）` 仍是空值；補充文字不能被誤當成路徑或識別碼。"""
    if value is None:
        return True
    text = str(value).strip()
    return text in EMPTY_METADATA or text.startswith(("—", "–"))


def parse_item_list(value):
    """解析 backtick 清單或逗號／頓號清單，保留順序與重複值供驗證器判斷。"""
    if is_empty_metadata(value):
        return []
    text = str(value).strip()
    quoted = BACKTICK_RE.findall(text)
    if quoted:
        return [item.strip() for item in quoted if item.strip()]
    return [item.strip() for item in re.split(r"[,，、;；]", text) if item.strip()]


def parse_task_ids(value):
    """只取 Task ID；顯示用括號、Markdown 連結或分隔符不影響解析。"""
    if is_empty_metadata(value):
        return []
    return TASK_ID_RE.findall(str(value))


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
    basic_fields = ["parent_id", "task_type", "assignee", "status", "created", "closed"]
    for key in basic_fields:
        match = PATTERNS[key].search(content)
        if match:
            value = match.group(1).strip()
            # 清理可能的多餘空白與 \r
            result[key] = value.replace("\r", "")
        else:
            result[key] = None

    planning_matches = {key: PATTERNS[key].search(content) for key in PLANNING_FIELDS}
    result["planning_fields_present"] = any(planning_matches.values())
    result["planning_missing_fields"] = [
        PLANNING_LABELS[key] for key, match in planning_matches.items() if match is None
    ]
    raw_planning = {
        key: match.group(1).strip().replace("\r", "") if match else None
        for key, match in planning_matches.items()
    }
    result["blocked_by"] = parse_task_ids(raw_planning["blocked_by"])
    result["write_scope"] = (
        parse_item_list(raw_planning["write_scope"])
        if planning_matches["write_scope"]
        else None
    )
    result["contract"] = (
        parse_item_list(raw_planning["contract"])
        if planning_matches["contract"]
        else None
    )
    result["change_set"] = (
        None if is_empty_metadata(raw_planning["change_set"]) else raw_planning["change_set"]
    )
    result["phase"] = None if is_empty_metadata(raw_planning["phase"]) else raw_planning["phase"]

    # 標準化 status（移除多餘的描述文字，如「Canceled (因...）」）
    if result.get("status"):
        raw_status = result["status"]
        # 精確匹配已知的狀態值
        for known_status in STATUS_PRIORITY:
            if known_status in raw_status:
                result["status"] = known_status
                break

    return result


def parse_iso_datetime(value):
    """
    嘗試將日期欄位（Created／Closed）的字串解析為 datetime 物件
    支援 ISO 8601 格式（如 2026-04-22T16:04+08:00）
    回傳 datetime 或 None
    """
    if not value or value in ("—", "-", "N/A", "null"):
        return None
    try:
        # 嘗試帶時區的 ISO 格式
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ_TAIPEI)
        return dt
    except (ValueError, TypeError):
        pass
    try:
        # 嘗試簡單日期格式
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=TZ_TAIPEI)
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
        # 跳過骨架目錄（如 _TEMPLATE/）——它是拿來複製的樣板，不是功能模組
        if feature_dir.name.startswith("_"):
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


def planning_error(location, message, code):
    return {"code": code, "location": str(location), "message": message}


def flatten_tasks(all_project_tasks):
    return [task for tasks in all_project_tasks.values() for task in tasks]


def validate_task_graph(tasks):
    """驗證全域 Task DAG，回傳 deterministic topological view 與所有錯誤。"""
    errors = []
    by_id = {}
    for task in sorted(tasks, key=lambda item: item["task_id"]):
        task_id = task["task_id"]
        if task_id in by_id:
            errors.append(
                planning_error(
                    task["file"],
                    f"Task ID {task_id!r} 重複；另一份位於 {by_id[task_id]['file']}",
                    "duplicate_task_id",
                )
            )
        else:
            by_id[task_id] = task

    for task_id, task in sorted(by_id.items()):
        if task["planning_fields_present"] and task["planning_missing_fields"]:
            missing = "、".join(task["planning_missing_fields"])
            errors.append(
                planning_error(
                    task["file"],
                    f"新式規劃欄位不完整，缺少：{missing}；舊工單可五欄全無，但不可只填一部分",
                    "incomplete_planning_fields",
                )
            )
        deps = task["blocked_by"]
        duplicates = sorted({dep for dep in deps if deps.count(dep) > 1})
        if duplicates:
            errors.append(
                planning_error(
                    task["file"],
                    f"Blocked By 含重複依賴：{', '.join(duplicates)}",
                    "duplicate_dependency",
                )
            )
        if task_id in deps:
            errors.append(
                planning_error(task["file"], f"{task_id} 不得依賴自己", "self_dependency")
            )
        unknown = sorted({dep for dep in deps if dep not in by_id})
        if unknown:
            errors.append(
                planning_error(
                    task["file"],
                    f"Blocked By 指向不存在的 Task ID：{', '.join(unknown)}",
                    "unknown_dependency",
                )
            )

    blocks = {task_id: [] for task_id in by_id}
    indegree = {task_id: 0 for task_id in by_id}
    for task_id, task in by_id.items():
        for dep in sorted(set(task["blocked_by"])):
            if dep not in by_id or dep == task_id:
                continue
            blocks[dep].append(task_id)
            indegree[task_id] += 1
    for task_id in blocks:
        blocks[task_id].sort()

    ready = [task_id for task_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    topological_order = []
    while ready:
        task_id = heapq.heappop(ready)
        topological_order.append(task_id)
        for blocked in blocks[task_id]:
            indegree[blocked] -= 1
            if indegree[blocked] == 0:
                heapq.heappush(ready, blocked)

    if len(topological_order) != len(by_id):
        cyclic = sorted(task_id for task_id, degree in indegree.items() if degree > 0)
        errors.append(
            planning_error(
                "docs/features/*/tasks",
                f"Task DAG 含有向循環，涉及：{', '.join(cyclic)}",
                "dependency_cycle",
            )
        )

    waves = {}
    for task_id in topological_order:
        known_deps = [dep for dep in set(by_id[task_id]["blocked_by"]) if dep in waves]
        waves[task_id] = 1 + max((waves[dep] for dep in known_deps), default=0)

    return {
        "tasks": by_id,
        "topological_order": topological_order,
        "wave_by_task": waves,
        "blocks": blocks,
        "errors": errors,
    }


def _round_scalar(pattern, content):
    match = pattern.search(content)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith("`") and value.endswith("`") and value.count("`") == 2:
        value = value[1:-1]
    return value


def parse_round_file(filepath):
    """解析 Round Manifest 的來源欄位；wave 表不讀，避免把衍生快照當來源。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as error:
        return {"file": str(filepath), "read_error": str(error)}

    header = ROUND_HEADER_RE.search(content)
    result = {
        "file": str(filepath),
        "round_id": header.group(1) if header else None,
        "title": header.group(2).strip() if header else None,
    }
    for key, pattern in ROUND_PATTERNS.items():
        result[key] = _round_scalar(pattern, content)

    section = ROUND_SECTION_RE.search(content)
    task_ids = []
    if section:
        for line in section.group(1).splitlines():
            if not line.lstrip().startswith("|"):
                continue
            first_cell = line.split("|", 2)[1]
            match = TASK_ID_RE.search(first_cell)
            if match:
                task_ids.append(match.group(0))
    result["task_ids"] = task_ids
    return result


def scan_rounds(root):
    rounds_dir = root / "docs" / "development" / "rounds"
    if not rounds_dir.is_dir():
        return []
    return [
        parse_round_file(path)
        for path in sorted(rounds_dir.glob("ROUND-*.md"))
        if not path.name.startswith("_")
    ]


def _scope_prefix(value):
    text = value.strip().replace("\\", "/").removeprefix("./")
    if not text or text.startswith(("/", "~", "http://", "https://")):
        return None, True
    wildcard_at = min(
        (text.find(char) for char in "*?[]{" if char in text),
        default=len(text),
    )
    has_wildcard = wildcard_at < len(text)
    prefix = text[:wildcard_at].rstrip("/")
    return prefix, has_wildcard


def scopes_are_definitely_disjoint(left, right):
    """只有能證明不相交才回 True；glob 共用靜態前綴時視為不可判定。"""
    if left is None or right is None or not left or not right:
        return False
    for left_scope in left:
        left_prefix, left_wild = _scope_prefix(left_scope)
        if left_prefix is None:
            return False
        for right_scope in right:
            right_prefix, right_wild = _scope_prefix(right_scope)
            if right_prefix is None:
                return False
            if left_prefix == right_prefix:
                return False
            if left_prefix.startswith(right_prefix + "/"):
                return False
            if right_prefix.startswith(left_prefix + "/"):
                return False
            if (left_wild or right_wild) and left_prefix.split("/")[0] == right_prefix.split("/")[0]:
                # 同一頂層且帶 glob 時，靜態資訊不足以證明永不交集。
                return False
    return True


def scope_covers_path(scopes, path):
    if not scopes:
        return False
    target = path.strip().replace("\\", "/").removeprefix("./")
    for scope in scopes:
        prefix, wildcard = _scope_prefix(scope)
        if prefix is None:
            continue
        if target == prefix or target.startswith(prefix + "/"):
            return True
        if not wildcard and prefix.startswith(target + "/"):
            return True
    return False


def transitive_dependencies(task_id, by_id):
    seen = set()
    pending = list(by_id[task_id]["blocked_by"])
    while pending:
        dep = pending.pop()
        if dep in seen or dep not in by_id:
            continue
        seen.add(dep)
        pending.extend(by_id[dep]["blocked_by"])
    return seen


def path_exists_at_revision(root, revision, path, cache):
    key = (revision, path)
    if key not in cache:
        if not SHA40_RE.fullmatch(revision or "") or any(char in path for char in "*?[]{"):
            cache[key] = False
        else:
            try:
                result = subprocess.run(
                    ["git", "-C", str(root), "cat-file", "-e", f"{revision}:{path}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            except OSError:
                cache[key] = False
            else:
                cache[key] = result.returncode == 0
    return cache[key]


def contracts_are_ready(root, task, manifest, by_id, revision_cache):
    contracts = task["contract"]
    if contracts is None:
        return False
    if not contracts:
        return True
    ancestors = transitive_dependencies(task["task_id"], by_id)
    for contract in contracts:
        if path_exists_at_revision(root, manifest["opening_base"], contract, revision_cache):
            continue
        providers = [
            dep
            for dep in ancestors
            if dep in manifest["task_ids"] and scope_covers_path(by_id[dep]["write_scope"], contract)
        ]
        if not providers:
            return False
    return True


def external_side_effects_are_isolatable(task):
    """從來源欄位只能證明 repo-local 工作；部署、人工操作與 migration 預設不並行。"""
    scopes = task["write_scope"]
    task_id_parts = set(task["task_id"].split("-"))
    title = (task.get("title") or "").lower()
    if not scopes or task.get("task_type") == "manual_user":
        return False
    if task_id_parts & {"DEPLOY", "MANUAL"} or task.get("phase") in {"migrate", "contract"}:
        return False
    if re.search(r"\b(?:deploy|migration|migrate)\b|部署|遷移|外部副作用", title):
        return False
    return all(_scope_prefix(scope)[0] is not None for scope in scopes)


def validate_parallel_changes(by_id):
    errors = []
    groups = {}
    for task_id, task in sorted(by_id.items()):
        phase = task["phase"]
        change_set = task["change_set"]
        if phase and phase not in VALID_PHASES:
            errors.append(
                planning_error(
                    task["file"],
                    f"Phase {phase!r} 不合法；只接受 expand、migrate、contract",
                    "invalid_phase",
                )
            )
        if phase and not change_set:
            errors.append(
                planning_error(
                    task["file"], "填寫 Phase 時必須同時填 Change Set", "phase_without_change_set"
                )
            )
        if change_set and not phase:
            errors.append(
                planning_error(
                    task["file"], "填寫 Change Set 時必須指定 Phase", "change_set_without_phase"
                )
            )
        if change_set:
            groups.setdefault(change_set, []).append(task_id)

    for change_set, task_ids in sorted(groups.items()):
        phase_map = {
            phase: [task_id for task_id in task_ids if by_id[task_id]["phase"] == phase]
            for phase in VALID_PHASES
        }
        if len(phase_map["expand"]) != 1:
            errors.append(
                planning_error(
                    by_id[task_ids[0]]["file"],
                    f"Change Set {change_set!r} 必須恰有一張 expand 工單",
                    "parallel_change_expand_count",
                )
            )
        if not phase_map["migrate"]:
            errors.append(
                planning_error(
                    by_id[task_ids[0]]["file"],
                    f"Change Set {change_set!r} 至少需要一張 migrate 工單",
                    "parallel_change_missing_migrate",
                )
            )
        if len(phase_map["contract"]) != 1:
            errors.append(
                planning_error(
                    by_id[task_ids[0]]["file"],
                    f"Change Set {change_set!r} 必須在建立 expand 時一併建立一張 contract 工單",
                    "parallel_change_contract_count",
                )
            )
        if len(phase_map["contract"]) == 1:
            contract_id = phase_map["contract"][0]
            missing = sorted(set(phase_map["migrate"]) - set(by_id[contract_id]["blocked_by"]))
            if missing:
                errors.append(
                    planning_error(
                        by_id[contract_id]["file"],
                        f"contract 工單 {contract_id} 的 Blocked By 未涵蓋 migrate：{', '.join(missing)}",
                        "parallel_change_contract_dependencies",
                    )
                )
    return errors


def build_planning_view(root, all_project_tasks=None):
    """建立工單 DAG、Round 與保守並行候選的單一衍生視圖。"""
    all_project_tasks = all_project_tasks or scan_all_tasks(root)
    graph = validate_task_graph(flatten_tasks(all_project_tasks))
    errors = list(graph["errors"])
    by_id = graph["tasks"]
    errors.extend(validate_parallel_changes(by_id))

    manifests = scan_rounds(root)
    rounds_by_id = {}
    membership = {}
    for manifest in manifests:
        location = manifest["file"]
        round_id = manifest.get("round_id")
        if manifest.get("read_error"):
            errors.append(planning_error(location, manifest["read_error"], "round_read_error"))
            continue
        if not round_id:
            errors.append(planning_error(location, "找不到 Round ID header", "missing_round_id"))
            continue
        if round_id in rounds_by_id:
            errors.append(
                planning_error(location, f"Round ID {round_id} 全域重複", "duplicate_round_id")
            )
            continue
        rounds_by_id[round_id] = manifest
        if not Path(location).stem.startswith(round_id):
            errors.append(
                planning_error(location, f"檔名必須以 {round_id} 開頭", "round_filename_mismatch")
            )
        for field, label in (("goal", "Goal"), ("branch", "Branch"), ("opening_base", "Opening Base")):
            if is_empty_metadata(manifest.get(field)):
                errors.append(
                    planning_error(location, f"Round Manifest 缺少 {label}", f"missing_round_{field}")
                )
        if manifest.get("branch") and not manifest["branch"].startswith("feature/"):
            errors.append(
                planning_error(location, "Round branch 必須使用 feature/{topic}", "invalid_round_branch")
            )
        if not SHA40_RE.fullmatch(manifest.get("opening_base") or ""):
            errors.append(
                planning_error(location, "Opening Base 必須是 40 字元 SHA", "invalid_opening_base")
            )

        task_ids = manifest["task_ids"]
        duplicate_members = sorted({task_id for task_id in task_ids if task_ids.count(task_id) > 1})
        if duplicate_members:
            errors.append(
                planning_error(
                    location,
                    f"Round 封閉集合含重複 Task ID：{', '.join(duplicate_members)}",
                    "duplicate_round_member",
                )
            )
        if not 2 <= len(task_ids) <= 5:
            errors.append(
                planning_error(
                    location,
                    f"Round 封閉集合必須是 2～5 張，實際為 {len(task_ids)} 張",
                    "round_size",
                )
            )
        unknown = sorted({task_id for task_id in task_ids if task_id not in by_id})
        if unknown:
            errors.append(
                planning_error(
                    location,
                    f"Round 指向不存在的 Task ID：{', '.join(unknown)}",
                    "unknown_round_member",
                )
            )
        for task_id in set(task_ids):
            if task_id in membership:
                errors.append(
                    planning_error(
                        location,
                        f"Task {task_id} 已屬於 {membership[task_id]}，不得重複歸入 {round_id}",
                        "duplicate_round_membership",
                    )
                )
            else:
                membership[task_id] = round_id
        members = set(task_ids)
        for task_id in sorted(members & set(by_id)):
            outside = [
                dep
                for dep in by_id[task_id]["blocked_by"]
                if dep in by_id
                and dep not in members
                and by_id[dep].get("status") not in {"Done", "Canceled"}
            ]
            if outside:
                errors.append(
                    planning_error(
                        location,
                        f"Round 不是封閉集合：{task_id} 仍依賴輪外未結案工單 {', '.join(outside)}",
                        "round_not_closed",
                    )
                )

    revision_cache = {}
    round_views = {}
    for round_id, manifest in sorted(rounds_by_id.items()):
        members = [task_id for task_id in manifest["task_ids"] if task_id in by_id]
        member_set = set(members)
        round_order = [task_id for task_id in graph["topological_order"] if task_id in member_set]
        wave_by_task = {}
        reverse_blocks = {task_id: [] for task_id in members}
        for task_id in round_order:
            internal_deps = [dep for dep in by_id[task_id]["blocked_by"] if dep in member_set]
            wave_by_task[task_id] = 1 + max(
                (wave_by_task[dep] for dep in internal_deps if dep in wave_by_task), default=0
            )
            for dep in internal_deps:
                reverse_blocks[dep].append(task_id)
        for task_id in reverse_blocks:
            reverse_blocks[task_id].sort()

        candidates = []
        blockers = []
        ancestry = {task_id: transitive_dependencies(task_id, by_id) for task_id in members}
        for index, left_id in enumerate(sorted(members)):
            for right_id in sorted(members)[index + 1 :]:
                reasons = []
                if left_id in ancestry[right_id] or right_id in ancestry[left_id]:
                    reasons.append("dag_order")
                if wave_by_task.get(left_id) != wave_by_task.get(right_id):
                    reasons.append("different_wave")
                if not scopes_are_definitely_disjoint(
                    by_id[left_id]["write_scope"], by_id[right_id]["write_scope"]
                ):
                    reasons.append("write_scope_overlap_or_unknown")
                for task_id in (left_id, right_id):
                    if not contracts_are_ready(
                        root, by_id[task_id], manifest, by_id, revision_cache
                    ):
                        reasons.append(f"contract_not_ready:{task_id}")
                    if not external_side_effects_are_isolatable(by_id[task_id]):
                        reasons.append(f"external_side_effects_unknown:{task_id}")
                pair = [left_id, right_id]
                if reasons:
                    blockers.append({"tasks": pair, "reasons": sorted(set(reasons))})
                else:
                    candidates.append(pair)

        waves = {}
        for task_id, wave in sorted(wave_by_task.items(), key=lambda item: (item[1], item[0])):
            waves.setdefault(str(wave), []).append(task_id)
        round_views[round_id] = {
            "file": manifest["file"],
            "goal": manifest["goal"],
            "branch": manifest["branch"],
            "opening_base": manifest["opening_base"],
            "task_ids": manifest["task_ids"],
            "topological_order": round_order,
            "waves": waves,
            "blocks": reverse_blocks,
            "parallel_candidates": candidates,
            "parallel_blockers": blockers,
        }

    task_view = {
        task_id: {
            "blocked_by": task["blocked_by"],
            "blocks": graph["blocks"].get(task_id, []),
            "wave": graph["wave_by_task"].get(task_id),
            "write_scope": task["write_scope"],
            "contract": task["contract"],
            "change_set": task["change_set"],
            "phase": task["phase"],
        }
        for task_id, task in sorted(by_id.items())
    }
    return {
        "topological_order": graph["topological_order"],
        "tasks": task_view,
        "rounds": round_views,
        "task_round_membership": dict(sorted(membership.items())),
        "errors": errors,
    }


def format_graph(view):
    return json.dumps(view, ensure_ascii=False, indent=2)


def classify_tasks(tasks, recent_limit=10):
    """
    將工單依狀態分類為四大區塊
    近期結案區塊顯示最近結案的 N 張，其餘移入歸檔

    **不看「今天」是哪一天**：分類結果只由工單內容決定。時間窗會讓已結案工單
    自己從報表裡消失，使生成檔不再是輸入的純函數（見 documentation_conventions.md §5）。
    """

    classified = {
        "current_sprint": [],  # In Progress + Ready
        "in_review": [],  # In Review
        "product_backlog": [],  # Pending
        "recent_closed": [],  # 近期 Done/Canceled
        "archived": [],  # 超出顯示筆數的 Done/Canceled
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
            classified["recent_closed"].append(task)

    # 當前衝刺：In Progress 優先，其次 Ready，同狀態內按 Task ID 排序
    classified["current_sprint"].sort(
        key=lambda t: (
            STATUS_PRIORITY.get(t.get("status", ""), 99),
            t.get("task_id", ""),
        )
    )

    # 近期結案：按完成時間倒序排列，取前 N 筆（沒有完成時間的排最後）
    classified["recent_closed"].sort(
        key=lambda t: parse_iso_datetime(t.get("closed"))
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


def format_json(all_project_tasks, recent_limit):
    """
    輸出完整 JSON 格式，包含分類與統計
    """
    output = {}
    for project, tasks in all_project_tasks.items():
        classified = classify_tasks(tasks, recent_limit)
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
    ]
    # ⚠️ 這份預設值刻意**不以空字串結尾**：讀回既有內容那條路徑會 .strip()，
    # 兩邊尾端不一致的話，「首次建檔 → 重跑」就會生出一行空白 diff。
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


def parse_design_note(filepath):
    """
    解析單一 DN 檔案的 header，回傳 None 表示這不是一份 DN
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError:
        return None

    title_match = DN_TITLE_RE.search(content)
    if not title_match:
        return None

    status_match = DN_STATUS_RE.search(content)
    depends_match = DN_DEPENDS_RE.search(content)
    depends_raw = depends_match.group(1).strip() if depends_match else "—"
    # 依賴欄位裡的連結是相對於 design_notes/ 寫的，貼進 BACKLOG.md 會指到不存在的路徑，
    # 所以只留連結文字。順便跳脫 `|`，否則會把表格切斷。
    depends_text = MD_LINK_RE.sub(r"\1", depends_raw).replace("|", r"\|")

    return {
        "id": title_match.group(1),
        "title": title_match.group(2).replace("|", r"\|"),
        "status": status_match.group(1).strip() if status_match else "❓ 未標狀態",
        "depends": depends_text,
        "depends_ids": sorted({f"DN-{n}" for n in DN_ID_RE.findall(depends_raw)}),
        "filename": filepath.name,
    }


def scan_design_notes(root):
    """
    掃描 docs/design_notes/DN-*.md。目錄不存在（裝了 kit 但還沒開過 DN）時回傳空 list
    """
    dn_dir = root / "docs" / "design_notes"
    if not dn_dir.is_dir():
        return []

    notes = []
    for path in sorted(dn_dir.glob("DN-*.md")):
        note = parse_design_note(path)
        if note:
            notes.append(note)

    notes.sort(key=lambda n: int(DN_ID_RE.search(n["id"]).group(1)))
    return notes


def format_design_notes_section(notes):
    """
    DN 索引區塊

    刻意**不印任何時間相依值**（開了幾天、距今多久）：這份檔案納入版控，
    內容必須是輸入的純函數，否則每天重跑都會生出一份沒有語意的 diff。
    """
    if not notes:
        return []

    known = {note["id"] for note in notes}
    lines = [
        "---",
        "",
        "## 🧪 設計筆記 (Design Notes)",
        "",
        "> 開單前置關卡：AC 寫不出來時先開 DN，寫得出來就直接開工單。",
        "> **本節由 `scan_backlog.py` 生成，不要手動編輯。**",
        "",
        "| DN | 狀態 | 標題 | 依賴 |",
        "|---|---|---|---|",
    ]

    dangling = []
    for note in notes:
        link = f"[{note['id']}](../design_notes/{note['filename']})"
        lines.append(f"| {link} | {note['status']} | {note['title']} | {note['depends']} |")
        for dep in note["depends_ids"]:
            if dep not in known:
                dangling.append((note["id"], dep))

    lines.append("")
    if dangling:
        lines.append("> ⚠️ **懸空依賴**——依賴欄位指向的 DN 檔案不存在：")
        for source, dep in dangling:
            lines.append(f"> - {source} → `{dep}`")
        lines.append("")

    return lines


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


def format_backlog_markdown(root, all_project_tasks, recent_limit, output_path=None):
    """
    輸出符合 backlog_template 格式的完整 Markdown
    """
    all_tasks = []
    for tasks in all_project_tasks.values():
        all_tasks.extend(tasks)

    classified = classify_tasks(all_tasks, recent_limit)
    total = len(all_tasks)

    lines = []
    lines.append("# 📋 待辦總表 (Backlog)")
    lines.append("")
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
        f"> 最近結案的 {recent_limit} 張工單（依完成時間排序）。"
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

    # 設計筆記索引（開單前置關卡）——排在冰箱之前，因為它是「還沒變成工單」的東西
    lines.extend(format_design_notes_section(scan_design_notes(root)))

    # 冰箱區塊（保留既有內容的提示）
    lines.append("---")
    lines.append("")
    lines.append("## 🧊 冰箱 (Icebox)")
    lines.append("")

    icebox_lines = extract_existing_icebox(root, output_path)
    lines.extend(icebox_lines)
    lines.append("")

    return "\n".join(lines)


def format_stale(all_project_tasks, days):
    """
    列出建立超過 days 天仍未結案的工單（停滯清單）

    **這份輸出依賴「今天是哪一天」，因此只能印到 stdout。** 把它寫進版控的檔案，
    輸入沒變輸出卻天天變（見 docs/standards/documentation_conventions.md §5）。
    """
    now = datetime.now(TZ_TAIPEI)
    cutoff = now - timedelta(days=days)

    stale = []
    for project, tasks in all_project_tasks.items():
        for task in tasks:
            if task.get("status") in ("Done", "Canceled"):
                continue
            created = parse_iso_datetime(task.get("created"))
            if created and created < cutoff:
                stale.append((project, task, (now - created).days))
    stale.sort(key=lambda item: -item[2])

    lines = [f"🕰️  停滯清單：建立超過 {days} 天仍未結案（判定基準 {now:%Y-%m-%d %H:%M %z}）", ""]
    if not stale:
        lines.append(f"✅ 沒有停滯超過 {days} 天的工單。")
        return "\n".join(lines)

    lines.append("| Task ID | 專案 | 狀態 | 建立時間 | 停滯天數 |")
    lines.append("|---------|------|------|----------|----------|")
    for project, task, age in stale:
        icon = STATUS_ICONS.get(task.get("status", ""), "❓")
        lines.append(
            f"| {task.get('task_id')} | {project} | {icon} {task.get('status')} "
            f"| {task.get('created')} | {age} |"
        )
    lines.append("")
    lines.append(f"**小計**：{len(stale)} 張")
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
        choices=["json", "summary", "backlog", "graph"],
        default="json",
        help="輸出格式: json (預設), summary, backlog, graph (DAG／Round 衍生視圖)",
    )
    parser.add_argument(
        "--recent-limit",
        type=int,
        default=10,
        help="近期結案的最大顯示筆數（預設: 10 筆）",
    )

    parser.add_argument(
        "--stale",
        type=int,
        default=None,
        metavar="DAYS",
        help="列出建立超過 DAYS 天仍未結案的工單（只印 stdout，不可寫入檔案）",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="輸出至指定檔案（避免使用 > 導致讀取前被清空）",
    )

    args = parser.parse_args()

    if args.stale is not None and args.output:
        parser.error(
            "--stale 是時間相依的視圖，只能印到 stdout：寫進版控的生成檔"
            "必須是輸入的純函數（見 docs/standards/documentation_conventions.md §5）"
        )

    root = find_project_root()
    all_tasks = scan_all_tasks(root, args.project)

    if not all_tasks:
        print("⚠️ 未找到任何工單。", file=sys.stderr)
        sys.exit(1)

    planning_tasks = scan_all_tasks(root) if args.project else all_tasks
    planning = build_planning_view(root, planning_tasks)
    if planning["errors"]:
        for error in planning["errors"]:
            print(f"❌ {error['location']}：{error['message']}", file=sys.stderr)
        if args.format == "graph":
            print(format_graph(planning))
        return 1

    if args.stale is not None:
        print(format_stale(all_tasks, args.stale))
        return

    if args.format == "json":
        print(format_json(all_tasks, args.recent_limit))
    elif args.format == "summary":
        print(format_summary(all_tasks))
    elif args.format == "backlog":
        out_str = format_backlog_markdown(
            root, all_tasks, args.recent_limit, args.output
        )
        if args.output:
            Path(args.output).write_text(out_str, encoding="utf-8")
        else:
            print(out_str)
    elif args.format == "graph":
        print(format_graph(planning))


if __name__ == "__main__":
    sys.exit(main())
