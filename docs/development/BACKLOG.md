# 📋 待辦總表 (Backlog)

> **工單來源目錄**：`docs/features/*/tasks/`
> **工單總數**：34 張

---

## 🏃‍♂️ 當前衝刺 (Current Sprint)

> 包含狀態為 `In Progress` 或 `Ready` 的工單。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | PEV-DEV-AGENT-026 | skill 與規範一致性的自動檢查：覆蓋率 ＋ 引用標題比對 | process_evolution | backend-developer | 🟢 Ready |
| 2 | PEV-DEV-AGENT-027 | qa-automation-engineer 的技術棧內容拆成第 2 層 | process_evolution | system-architect | 🟢 Ready |
| 3 | PEV-DEV-AGENT-031 | precheck 新增 Assignee 合法性檢查 | process_evolution | devops-engineer | 🟢 Ready |

**小計**：3 張（In Progress: 0 / Ready: 3）

---

## ⏳ 審查中 (In Review)

> 開發已完成，等待 Code Review 或驗收確認的工單。

*(無)*

---

## 🧊 產品待辦 (Product Backlog)

> 包含狀態為 `Pending` 的工單，等待前置條件完成或人為確認後方可開始。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) |
|---|---------|------|------|-------------------|---------------|
| 1 | PEV-DEV-AGENT-028 | 立 skill 撰寫標準：skill_conventions.md | process_evolution | system-architect | ⏳ Pending |

**小計**：1 張

---

## ✅ 近期結案 (Closed)

> 最近結案的 10 張工單（依完成時間排序）。更早的結案工單可透過 `scan_backlog.py --format json` 查詢。

| # | Task ID | 標題 | 專案 | 負責人 (Assignee) | 狀態 (Status) | 完成時間 |
|---|---------|------|------|-------------------|---------------|----------|
| 1 | PEV-DEV-AGENT-032 | 一輪多張工單的合併拓撲寫進 git_workflow.md §7 | process_evolution | devops-engineer | ✅ Done | 2026-08-19T14:53+08:00 |
| 2 | PEV-DEV-AGENT-025 | 13 份 skill 全面盤點與對齊 | process_evolution | tech-lead | ✅ Done | 2026-08-18T23:55+08:00 |
| 3 | PEV-DEV-AGENT-029 | 移除 kit 出貨內容裡硬編碼的 uv run | process_evolution | devops-engineer | ✅ Done | 2026-08-18T23:40+08:00 |
| 4 | PEV-DEV-AGENT-030 | 修正 DN 取號指令：改從檔名取號 | process_evolution | scrum-master | ✅ Done | 2026-08-18T23:35+08:00 |
| 5 | PEV-DEV-AGENT-024 | 填上 §1.12 第 2 層：把本 repo 的取證通道設定寫進 CLAUDE.md | process_evolution | devops-engineer | ✅ Done | 2026-08-18T08:20+08:00 |
| 6 | PEV-DEV-AGENT-023 | 取證通道保真：從「審查者換讀法」升級成全角色的開工自檢 | process_evolution | backend-developer | ✅ Done | 2026-08-18T07:27+08:00 |
| 7 | PEV-DEV-AGENT-022 | precheck 與 kit 自身測試收斂：同一個盲點兩份實作，再補兩項漏掉的檢查 | process_evolution | backend-developer | ✅ Done | 2026-08-18T06:35+08:00 |
| 8 | PEV-DEV-AGENT-021 | commit 規範送不到 Agent 手上：CLAUDE.md 只指路，沒帶格式 | process_evolution | devops-engineer | ✅ Done | 2026-08-18T06:05+08:00 |
| 9 | PEV-DEV-AGENT-002 | README 補上 git 流程能力對照表，讓換 git server 的人一眼看懂 | process_evolution | devops-engineer | ✅ Done | 2026-08-18T05:45+08:00 |
| 10 | PEV-DEV-AGENT-020 | 清帳：冰箱卡點更新，舊 design_note 轉為歷史索引 | process_evolution | scrum-master | ✅ Done | 2026-08-18T05:31+08:00 |

**小計**：10 張（Done: 10 / Canceled: 0）

> 📦 另有 20 張已歸檔工單未顯示。

---

## 📊 統計摘要

### kit_sync

| 狀態 | 數量 | 佔比 |
|------|------|------|
| ✅ Done | 1 | 100.0% |
| **總計** | **1** | **100%** |

### process_evolution

| 狀態 | 數量 | 佔比 |
|------|------|------|
| 🟢 Ready | 3 | 9.4% |
| ⏳ Pending | 1 | 3.1% |
| ✅ Done | 28 | 87.5% |
| **總計** | **32** | **100%** |

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
| [DN-004](../design_notes/DN-004_skill_system_realignment.md) | 🎓 Graduated | Skill 體系與現行流程的重新對齊 | DN-001（本檔的格式）；DN-003（git 流程，其落地會先改動 6 份 skill） |
| [DN-005](../design_notes/DN-005_parallel_task_decomposition.md) | 🌱 Seed | 並行開發的任務拆解與變更傳播 | DN-001（本檔的格式）；DN-003（git 流程，本 DN 視其為「基本層」並在其上擴充） |
| [DN-006](../design_notes/DN-006_branch_topology_and_isolation.md) | 🔍 Exploring | 分支拓撲與並行隔離 | DN-001（本檔的格式）；DN-003（已畢業的單線 git 流程，本 DN 在其上擴充） |
| [DN-007](../design_notes/DN-007_ci_gate.md) | 🎓 Graduated | CI 閘門：kit 要不要出貨自動檢查，以及檢查什麼 | DN-001（本檔的格式）；DN-003（已畢業，`git_workflow.md` 是本檔要補的那份規範） |
| [DN-008](../design_notes/DN-008_review_panel_and_context_isolation.md) | 🌱 Seed | 審查的執行形態：panel 模式與 context 隔離 | DN-001（本檔的格式）；DN-005（§2.1 的 panel 是它 §4「放大審查粒度」訴求的落點）；DN-006（§4.2 的重疊區強制人工審查與 panel 方向相反，判準要一起定；隔離載體的選擇與它的合併點耦合） |

---

## 🧊 冰箱 (Icebox)

> 暫時擱置、待未來進一步討論或需要先行更新架構文件 (PRD/API Specs) 的想法與功能點。
>
> 📌 **Icebox 只放「還沒決定」的事**——一旦決定（做或不做）就離開這裡：
> 做 → 變成工單；不做 → 只剩 design note 裡的 `Dropped` 紀錄。這條規則讓本區永遠短。
>
> 📌 **不是每一項都要有 design note。** 依 [DN-001](../design_notes/DN-001_design_note_mechanism.md) §3.2：
> **當場寫得出可驗收的 AC → 直接開工單；寫不出來 → 才開 DN。**
> 沒有 DN 的項目，脈絡就寫在下表的「卡在哪」欄，或其後的小節。
> 舊的 [`process_evolution/design_note.md`](../features/process_evolution/design_note.md)
> 已於 2026-08-18（`PEV-DEV-AGENT-020`）轉為**歷史索引**，不再是待辦來源。

| 項目 | 狀態 | 卡在哪 |
|---|---|---|
| 負向對照自動化 | 待開 DN | 落點**不在** precheck 第 1 層（要跑專案測試套件＝第 2 層），三條做法互斥未收斂 → 見下方小節 |
| 展示層生成 | 待開 DN | 100% 從 source of truth 生成，Mermaid + 靜態站台。排最後。design_note §3.8 |

### 負向對照自動化：三條互斥的做法

**先更正一個過期的前提。** 本項原本寫「等 [DN-007](../design_notes/DN-007_ci_gate.md)
定出檢查落點」——DN-007 已畢業、`PEV-DEV-AGENT-018`／`019` 也已落地，結論是落點
**確定不在** precheck 出貨的那一層：`precheck.py` 是 stdlib-only、只讀 repo 內的檔案、
**不執行任何測試**，而負向對照的定義就是「還原實作後**重跑專案測試套件**」，
依 DN-007 §3.2 屬**第 2 層**（跟技術棧綁定，kit 只能留一個 hook 讓專案填）。

所以卡點不是「落點未定」，而是**做法有三條、互斥、還沒擇一**：

| # | 做法 | 落層 | 卡在哪 |
|---|---|---|---|
| a | 全量 mutation testing | 第 2 層 | 慢；且 kit 給不出跑法（測試指令跟技術棧綁定） |
| b | 只對本次變更做負向對照——還原實作 diff，確認新增的測試轉紅 | 第 2 層 | 「還原到哪個 commit」沒有通用答案 |
| c | 只檢查「審查檔有沒有記錄負向對照」（純文字檢查） | 第 1 層，precheck 做得到 | **驗證的是有沒有「寫」，不是有沒有「做」** |

**c 的問題是自我指涉的**：一個只檢查「有沒有寫」的閘門，本身就會製造
`design_note.md` §2 第 2 類人工介入（宣稱 ≠ 實際）——而那正是負向對照要抓的東西。

依 `PEV-DEV-AGENT-015` 立下的判準（只有一種做法就直接開工單，有多種就開 DN）→ **待開 DN**。
