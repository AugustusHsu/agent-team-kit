# 📋 待辦總表 (Backlog)

> **最後更新時間**：2026-08-16
> **工單來源目錄**：`docs/features/*/tasks/`
> **工單總數**：2 張

---

## 🏃‍♂️ 當前衝刺 (Current Sprint)

> 包含狀態為 `In Progress` 或 `Ready` 的工單。

*(無)*

---

## ⏳ 審查中 (In Review)

> 開發已完成，等待 Code Review 或驗收確認的工單。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | KIT-DEV-AGENT-001 | 回收 my_workstation 的文檔權威階序與指路檔，並建立 install.sh 升級路徑 | kit_sync | devops-engineer | In Review |

**小計**：1 張

---

## 🧊 產品待辦 (Product Backlog)

> 包含狀態為 `Pending` 的工單，等待前置條件完成或人為確認後方可開始。

*(無)*

---

## ✅ 近期結案 (Closed)

> 最近 7 天內完成的工單（上限 10 筆）。更早的結案工單可透過 `scan_backlog.py --format json` 查詢。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) | 完成時間 |
|---|---------|------|------|-------------------|---------------|----------|
| 1 | WTG-DEV-BE-001 | 補齊 worktree 防孤兒機制的登記欄位與對帳邏輯 | worktree_guard | backend-developer | 🚫 Canceled | 2026-08-16T01:03+08:00 |

**小計**：1 張（Done: 0 / Canceled: 1）

---

## 📊 統計摘要

### kit_sync

| 狀態 | 數量 | 佔比 |
|------|------|------|
| 🟡 In Review | 1 | 100.0% |
| **總計** | **1** | **100%** |

### process_evolution

| 狀態 | 數量 | 佔比 |
|------|------|------|
| **總計** | **0** | **100%** |

### worktree_guard

| 狀態 | 數量 | 佔比 |
|------|------|------|
| 🚫 Canceled | 1 | 100.0% |
| **總計** | **1** | **100%** |

---

## 🧊 冰箱 (Icebox)

> 暫時擱置、待未來進一步討論或需要先行更新架構文件 (PRD/API Specs) 的想法與功能點。
>
> 📌 **本區只放一行索引，實質內容在 design note**：
> [`docs/features/process_evolution/design_note.md`](../features/process_evolution/design_note.md)
> 每一項確定要做時，才畢業成 `PEV-*` 工單。

| 項目 | 描述 | 備註 |
|---|---|---|
| Draft PR + CI 閘門 | `In Progress` 即開 Draft PR，CI 從第一個 commit 就跑；`Done` = merged | design_note §3.1 ⬅ **最優先** |
| 負向對照自動化 | 新增測試若「還原目標 commit 後仍全綠」= 零鑑別力，CI 擋下 | design_note §3.2 |
| 審查與開發拆 context | 消除自我審查的獨立性不足 | design_note §3.3 |
| precheck 腳本 | 審查清單三分法：grep 能證明的不該給 AI 判斷 | design_note §3.4 |
| 工單瘦身 | 審查輪次與 HITL 問答移出工單檔案 | design_note §3.5 |
| worktree 重新設計 | 20 KB → 約 3 KB；本專案已停用，出貨版保留程度待定 | design_note §3.6 |
| design_note 規範化 | 落點、範本欄位、生命週期、與 Icebox 的一對一關係 | design_note §3.9（**元問題**） |
| Discord 通知／批准層 | 只推「只有人能決定」的第 4 類給使用者 | design_note §3.7 |
| 展示層生成 | 100% 從 source of truth 生成；Mermaid + 靜態站台，不放專案頁面 | design_note §3.8（排最後） |
| `DOCS_MAP.md` 是否該列為種子檔 | 其「功能模組」表本應由專案填寫，但 `is_seed_file()` 未涵蓋，升級時會走衝突路徑 | dogfooding 首次發現 |
| headroom 壓縮工具輸出的副作用 | code-reviewer 讀 diff 時可能讀到壓縮版，審查場景下是風險 | design_note §4.3，待查 |
| 背景任務 worktree 隔離守衛 | `.claude/settings.json` 的 `worktree.bgIsolation` 與本專案停用 worktree 相衝突 | 本次清理實地遇到 |
