# 📋 待辦總表 (Backlog)

<!--
  📝 使用說明 (Instructions)
  ==========================
  本範本用於產出全域待辦總表，涵蓋所有專案。Scrum Master 在建立或更新 Backlog 時，
  請遵循以下步驟：

  1. 掃描 `docs/features/{功能模組名}/tasks/` 目錄下的所有專案子目錄。
  2. 從每張工單提取 metadata：Task ID、標題、專案、負責人 (Assignee)、狀態 (Status)、建立時間 (Created)、完成時間 (Closed)。
  3. 依照下方四大區塊的分類規則，將工單填入對應表格。
  4. 更新底部的「📊 統計摘要」（按專案分組）。

  💡 自動化輔助：
  可使用 `.agent/scripts/scan_backlog.py` 腳本自動掃描並產出結構化資料：
    python3 .agent/scripts/scan_backlog.py --format json        # JSON 完整輸出
    python3 .agent/scripts/scan_backlog.py --format summary     # 精簡摘要
    python3 .agent/scripts/scan_backlog.py --format backlog     # 完整 Markdown

  分類規則：
  - 🏃‍♂️ 當前衝刺：Status 為 Ready / In Progress
  - ⏳ 審查中：Status 為 In Review
  - 🧊 產品待辦：Status 為 Pending
  - ✅ 近期結案：Status 為 Done / Canceled（最近 7 天內，上限 10 筆）

  排序規則（當前衝刺區塊內）：
  - 先依狀態優先級排序：In Progress → Ready
  - 同狀態內依 Task ID 字母序排序

  狀態圖示對照：
  | 狀態 | 圖示 |
  |------|------|
  | In Progress | 🔵 |
  | Ready | 🟢 |
  | In Review | 🟡 |
  | Pending | ⏳ |
  | Done | ✅ |
  | Canceled | 🚫 |

  存放位置：
  - 產出的 BACKLOG.md 應放置於 `docs/development/BACKLOG.md`。
-->

> **最後更新時間**：{YYYY-MM-DD}
> **工單來源目錄**：`docs/features/{功能模組名}/tasks/`
> **工單總數**：{N} 張

---

## 🏃‍♂️ 當前衝刺 (Current Sprint)

> 包含狀態為 `In Progress` 或 `Ready` 的工單。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | {TASK-ID} | {工單標題} | {專案名} | {assignee} | 🔵 In Progress |
| 2 | {TASK-ID} | {工單標題} | {專案名} | {assignee} | 🟢 Ready |

**小計**：{n} 張（In Progress: {x} / Ready: {y}）

---

## ⏳ 審查中 (In Review)

> 開發已完成，等待 Code Review 或驗收確認的工單。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | {TASK-ID} | {工單標題} | {專案名} | {assignee} | 🟡 In Review |

**小計**：{n} 張

---

## 🧊 產品待辦 (Product Backlog)

> 包含狀態為 `Pending` 的工單，等待前置條件完成或人為確認後方可開始。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | {TASK-ID} | {工單標題} | {專案名} | {assignee} | ⏳ Pending |

**小計**：{n} 張

---

## ✅ 近期結案 (Closed)

> 最近 7 天內完成的工單（上限 10 筆）。更早的結案工單可透過 `scan_backlog.py --format json` 查詢。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) | 完成時間 |
|---|---------|------|------|-------------------|---------------|----------|
| 1 | {TASK-ID} | {工單標題} | {專案名} | {assignee} | ✅ Done | {YYYY-MM-DDTHH:MM+08:00} |
| 2 | {TASK-ID} | {工單標題} | {專案名} | {assignee} | 🚫 Canceled | {YYYY-MM-DDTHH:MM+08:00} |

**小計**：{n} 張（Done: {x} / Canceled: {y}）

> 📦 另有 {m} 張已歸檔工單未顯示。

---

## 📊 統計摘要

<!--
  統計摘要按專案分組顯示。每個專案獨立一張表格。
  若有多個專案，依專案名稱字母序排列。
-->

### {專案名稱}

| 狀態 | 數量 | 佔比 |
|------|------|------|
| 🔵 In Progress | {n} | {p}% |
| 🟢 Ready | {n} | {p}% |
| 🟡 In Review | {n} | {p}% |
| ⏳ Pending | {n} | {p}% |
| ✅ Done | {n} | {p}% |
| 🚫 Canceled | {n} | {p}% |
| **總計** | **{N}** | **100%** |

---

## 🧊 冰箱 (Icebox)

> 暫時擱置、待未來進一步討論或需要先行更新架構文件 (PRD/API Specs) 的想法與功能點。

| 項目 | 描述 | 備註 |
|---|---|---|
| {項目名稱} | {描述} | {備註} |
