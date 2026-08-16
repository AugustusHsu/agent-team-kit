# 📋 待辦總表 (Backlog)

> **工單來源目錄**：`docs/features/*/tasks/`
> **工單總數**：16 張

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

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | PEV-DEV-AGENT-002 | README 補上 git 流程能力對照表，讓換 git server 的人一眼看懂 | process_evolution | devops-engineer | ⏳ Pending |

**小計**：1 張

---

## ✅ 近期結案 (Closed)

> 最近結案的 10 張工單（依完成時間排序）。更早的結案工單可透過 `scan_backlog.py --format json` 查詢。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) | 完成時間 |
|---|---------|------|------|-------------------|---------------|----------|
| 1 | PEV-DEV-AGENT-014 | 冰箱清帳：移除已落地與前提消失的項目 | process_evolution | scrum-master | ✅ Done | 2026-08-17T21:55+08:00 |
| 2 | PEV-DEV-AGENT-013 | 立規：納入版控的生成檔必須是輸入的純函數 | process_evolution | backend-engineer | ✅ Done | 2026-08-17T21:30+08:00 |
| 3 | PEV-DEV-AGENT-012 | scan_backlog 的 metadata 正則跨行誤配：欄位留空會抓到下一行 | process_evolution | backend-engineer | ✅ Done | 2026-08-17T20:40+08:00 |
| 4 | PEV-DEV-AGENT-009 | DOCS_MAP 的模組表抽成獨立檔，骨架恢復可升級 | process_evolution | devops-engineer | ✅ Done | 2026-08-17T19:00+08:00 |
| 5 | PEV-DEV-AGENT-008 | `scan_backlog.py` 生成 DN 索引，並檢查懸空依賴 | process_evolution | backend-developer | ✅ Done | 2026-08-17T18:20+08:00 |
| 6 | PEV-DEV-AGENT-006 | scrum-master 加上「開單前置關卡」 | process_evolution | devops-engineer | ✅ Done | 2026-08-17T17:40+08:00 |
| 7 | PEV-DEV-AGENT-005 | `team_protocol.md`：DN 的權威效力與模組「類型」欄位 | process_evolution | devops-engineer | ✅ Done | 2026-08-17T17:10+08:00 |
| 8 | PEV-DEV-AGENT-011 | commit 閘門的範圍：把關「進入主線」，不是每一顆 commit | process_evolution | devops-engineer | ✅ Done | 2026-08-17T16:40+08:00 |
| 9 | PEV-DEV-AGENT-004 | `documentation_conventions.md` 新增 Design Note 機制章節 | process_evolution | devops-engineer | ✅ Done | 2026-08-17T15:45+08:00 |
| 10 | PEV-DEV-AGENT-007 | 出貨 `kit/docs/design_notes/`：DN 範本與目錄說明 | process_evolution | devops-engineer | ✅ Done | 2026-08-17T15:10+08:00 |

**小計**：10 張（Done: 10 / Canceled: 0）

> 📦 另有 4 張已歸檔工單未顯示。

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
| ⏳ Pending | 1 | 7.1% |
| ✅ Done | 13 | 92.9% |
| **總計** | **14** | **100%** |

### worktree_guard

| 狀態 | 數量 | 佔比 |
|------|------|------|
| 🚫 Canceled | 1 | 100.0% |
| **總計** | **1** | **100%** |

---

## 🧪 設計筆記 (Design Notes)

> 開單前置關卡：AC 寫不出來時先開 DN，寫得出來就直接開工單。
> **本節由 `scan_backlog.py` 生成，不要手動編輯。**

| DN | 狀態 | 標題 | 依賴 |
|---|---|---|---|
| [DN-001](../design_notes/DN-001_design_note_mechanism.md) | 🎓 Graduated | Design Note 機制本身的設計 | — |
| [DN-002](../design_notes/DN-002_discord_notification_layer.md) | 🌱 Seed | Discord 作為通知與批准層 | DN-001（本檔的格式）；DN-007（CI 閘門，2026-08-17 開出，解除本欄長期懸空） |
| [DN-003](../design_notes/DN-003_git_workflow_and_pr_gate.md) | 🎓 Graduated | Git 流程與 PR 閘門 | DN-001（格式） |
| [DN-004](../design_notes/DN-004_skill_system_realignment.md) | 🌱 Seed | Skill 體系與現行流程的重新對齊 | DN-001（本檔的格式）；DN-003（git 流程，其落地會先改動 6 份 skill）； |
| [DN-005](../design_notes/DN-005_parallel_task_decomposition.md) | 🌱 Seed | 並行開發的任務拆解與變更傳播 | DN-001（本檔的格式）；DN-003（git 流程，本 DN 視其為「基本層」並在其上擴充） |
| [DN-006](../design_notes/DN-006_branch_topology_and_isolation.md) | 🌱 Seed | 分支拓撲與並行隔離 | DN-001（本檔的格式）；DN-003（已畢業的單線 git 流程，本 DN 在其上擴充） |
| [DN-007](../design_notes/DN-007_ci_gate.md) | 🔍 Exploring | CI 閘門：kit 要不要出貨自動檢查，以及檢查什麼 | DN-001（本檔的格式）；DN-003（已畢業，`git_workflow.md` 是本檔要補的那份規範） |

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

| 負向對照自動化 | 待開工單 | 要跑在 CI 上，等 [DN-007](../design_notes/DN-007_ci_gate.md) 定出檢查落點 |
| 工單瘦身 | 待開 DN | 審查輪次與 HITL 問答移出工單檔案，落點未定。design_note §3.5 |
| 展示層生成 | 待開 DN | 100% 從 source of truth 生成，Mermaid + 靜態站台。排最後。design_note §3.8 |
| 審查與開發拆 context | 待判定 | 若只有一種做法就直接開工單；若有 subagent／獨立 session／換模型之分則需 DN。design_note §3.3 |
| precheck 腳本 | 可直接開工單 | 審查清單三分法，做法單一。design_note §3.4 |
| headroom 壓縮工具輸出 | 待調查 | code-reviewer 讀 diff 可能讀到壓縮版；2026-08-17 該輪對話三度遇到，隔輪的 PEV-DEV-AGENT-012/013 開發中又遇到兩次（讀 DN-007、讀 Icebox 表格時被壓成 JSON）。開 spike 工單 |
