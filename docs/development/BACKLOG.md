# 📋 待辦總表 (Backlog)

> **最後更新時間**：2026-08-16
> **工單來源目錄**：`docs/features/*/tasks/`
> **工單總數**：4 張

---

## 🏃‍♂️ 當前衝刺 (Current Sprint)

> 包含狀態為 `In Progress` 或 `Ready` 的工單。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | PEV-DEV-AGENT-001 | 建立 git_workflow.md 並把 DN-003 的裁定落到出貨規範 | process_evolution | devops-engineer | 🟢 Ready |

**小計**：1 張（In Progress: 0 / Ready: 1）

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

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | PEV-DEV-AGENT-002 | README 補上 git 流程能力對照表，讓換 git server 的人一眼看懂 | process_evolution | devops-engineer | ⏳ Pending |

**小計**：1 張

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
| 🟢 Ready | 1 | 50.0% |
| ⏳ Pending | 1 | 50.0% |
| **總計** | **2** | **100%** |

### worktree_guard

| 狀態 | 數量 | 佔比 |
|------|------|------|
| 🚫 Canceled | 1 | 100.0% |
| **總計** | **1** | **100%** |

---

## 🧊 冰箱 (Icebox)

> 暫時擱置、待未來進一步討論或需要先行更新架構文件 (PRD/API Specs) 的想法與功能點。
>
> 📌 **Icebox 只放「還沒決定」的事**——一旦決定（做或不做）就離開這裡：
> 做 → 變成工單；不做 → 只剩 design note 裡的 `Dropped` 紀錄。這條規則讓本區永遠短。
>
> 📌 **不是每一項都要有 design note。** 依 [DN-001](../design_notes/DN-001_design_note_mechanism.md) §3.2：
> **當場寫得出可驗收的 AC → 直接開工單；寫不出來 → 才開 DN。**
> 沒有 DN 的項目，脈絡暫存在
> [`process_evolution/design_note.md`](../features/process_evolution/design_note.md)（待拆）。

| 項目 | 狀態 | 卡在哪 |
|---|---|---|
| [DN-001 Design Note 機制本身](../design_notes/DN-001_design_note_mechanism.md) | 🔍 Exploring | 範本欄位、索引生成腳本形狀，要實跑才知道 |
| [DN-002 Discord 通知與批准層](../design_notes/DN-002_discord_notification_layer.md) | 🌱 Seed | 尚未比方案；先等 CI 閘門定案 |

| 負向對照自動化 | 待開 DN | 要跑在 CI 上，依賴 DN-003 先定案。design_note §3.2 |
| 工單瘦身 | 待開 DN | 審查輪次與 HITL 問答移出工單檔案，落點未定。design_note §3.5 |
| worktree 重新設計 | 待開 DN | kit 內容已於 2026-08-16 整份移除、分支規則搬回 team_protocol §1.9。**必須排在 DN-003 之後**：導入 PR 後 worktree 的必要性會重估 |
| 展示層生成 | 待開 DN | 100% 從 source of truth 生成，Mermaid + 靜態站台。排最後。design_note §3.8 |
| 審查與開發拆 context | 待判定 | 若只有一種做法就直接開工單；若有 subagent／獨立 session／換模型之分則需 DN。design_note §3.3 |
| precheck 腳本 | 可直接開工單 | 審查清單三分法，做法單一。design_note §3.4 |
| 生成檔不得含時間相依值 | 可直接開工單 | 立規＋`scan_backlog.py --stale` 只輸出 stdout。理由見 DN-001 §5 |
| `DOCS_MAP.md` 是否列為種子檔 | 待你決定 | yes/no 一句話。牽涉「專案自填表 vs kit 維護的規範表」的取捨 |
| `scan_backlog.py` 的 Closed 欄位 regex 跨行誤配 | 可直接開工單 | `\s*` 會吃掉換行，Closed 留空時抓到下一行的 `## 1. 任務描述` 當值。實測 PEV-DEV-AGENT-001 |
| headroom 壓縮工具輸出 | 待調查 | code-reviewer 讀 diff 可能讀到壓縮版；本次對話已三度實地遇到。開 spike 工單 |
| 背景任務 worktree 隔離守衛 | 可直接開工單 | `.claude/settings.json` 的 `worktree.bgIsolation` 與本專案停用 worktree 相衝突 |
