# [Task ID: KIT-DEV-AGENT-001] 回收 my_workstation 的文檔權威階序與指路檔，並建立 install.sh 升級路徑

**🔗 依附母任務 (Parent Task ID):** Independent
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-15T16:45+08:00
**✅ 完成時間 (Closed):** 2026-08-16T15:05+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

比對 `../my_workstation`（本套件的第一個使用者專案）與本 repo 後，發現兩邊已**雙向漂移**：
kit 領先一整套 worktree／commit 閘門流程，而 my_workstation 領先一條 2026-08-15 才立的
「文檔權威階序」。本工單處理其中三件事：

1. **回收文檔權威階序**——把 my_workstation 的 §1.9「Source of Truth Hierarchy」納入 kit。
   規則本身與專案無關（已結案工單不得作為規格依據），屬於出貨內容。
2. **回收指路檔模式**——`docs/standards/` 是人類讀者的規範入口，需要一個 `team_protocol.md`
   進入點；但正版必須留在 `.agent/`（角色 SKILL 讀那份）。既不複製也不做 symlink。
3. **建立升級路徑**——這是最關鍵的一項。現行 `install.sh` 只有「檔案存在就略過」與
   `--force` 全覆蓋兩種行為，對既有專案等於**無法升級**：不加 `--force` 什麼都不動，
   加了會輾掉 §3.1 模組前綴表、`BACKLOG.md`、`DOCS_MAP.md` 等專案客製內容。
   kit 再怎麼演進都送不進已安裝的專案。

**編號決策**：kit 的 §1.9／§1.10 各被 7 處交叉引用（跨 7 個檔），my_workstation 端
只有 3 處引用 §1.9。因此文檔權威階序在 kit 落為 **§1.11**，不動既有編號。代價是它與
語意相近的 §1.8 缺陷收容被 worktree／commit 兩節隔開，但對 Agent 讀取無實質影響。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `../my_workstation/.agent/resources/team_protocol.md` §1.9（移植來源）
  - `../my_workstation/docs/standards/team_protocol.md`（指路檔模式來源）
  - `kit/docs/standards/worktree_workflow.md`（既有的 §1.9／§1.10 交叉引用）
- **Outputs (輸出/預期變更)**:
  - `kit/.agent/resources/team_protocol.md`：新增 §1.11
  - `kit/docs/standards/team_protocol.md`：新建指路檔
  - `kit/docs/standards/README.md`、`kit/docs/DOCS_MAP.md`：登記
  - `install.sh`：新增 `--upgrade` / `--dry-run`，寫入 `.agent/.kit-manifest`
  - `tests/test_install.py`、`tests/test_kit_integrity.py`：對應測試
  - `README.md`、`CLAUDE.md`、`docs/features/README.md`

## 3. 驗收標準 (Acceptance Criteria)

- [x] `kit/.agent/resources/team_protocol.md` 有 §1.11 文檔權威階序，且四層權威表與實務守則完整
- [x] 移植時修正原文指向 `documentation_conventions.md` §2.3 的失效引用（正確為 §2.1）
- [x] `kit/docs/standards/team_protocol.md` 為指路檔：不含正文、指向 `.agent/` 正版、附章節索引與不做 symlink 的理由
- [x] 指路檔已登記於 `kit/docs/DOCS_MAP.md` 與 `kit/docs/standards/README.md`
- [x] `test_團隊守則只有一份正版` 改為驗證「第二份必須是指路檔且不抄正文」而非禁止存在
- [x] 新增 `test_指路檔章節索引與正版同步`，正版加章節而索引沒補就會失敗
- [x] `install.sh --upgrade` 依 `.agent/.kit-manifest` 分辨使用者改過與否：沒改過的更新、改過的另存 `.new`
- [x] 種子檔（`CLAUDE.md`、`.gitignore`、`docs/development/BACKLOG.md`）升級時一律保留
- [x] 沒有 manifest 的舊安裝走保守路徑，一律不覆蓋
- [x] `--upgrade --dry-run` 零寫入（含不產生 manifest 與 `.new`）
- [x] `--dry-run` 單獨使用、未知選項皆報錯離開
- [x] 既有行為不變：首次安裝略過既有檔案、`--force` 全覆蓋、不複製本機產生物
- [x] `uv run pytest` 全綠
- [x] 以 my_workstation 的副本實跑 `--upgrade`，確認其 §3.1 模組前綴表與自有 §1.9 未被動到

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。編號方向（文檔權威階序落為 §1.11）依前次分析提出的建議執行，使用者未提出異議。
- **✍️ User 補充回覆 (User Input)**:
  -

## 5. 範圍外 (Out of Scope)

使用者明確指示本次不做：

- **方向 B 第 2 項：`skill-creator` 整套 skill**——kit 有 12 份 `evals.json` 卻沒有執行器，
  仍是缺口，但本次不處理。
- **方向 A 全部 8 項**（把 kit 領先的 worktree／commit 閘門推進 my_workstation）——
  升級路徑已備妥，實際推送另案處理。

## 6. 已知後續 (Follow-up)

- my_workstation 的 §1.9「文檔權威階序」與 kit 的 §1.11 目前編號不同。實際推送方向 A 時，
  my_workstation 端 3 處引用（`docs/standards/team_protocol.md` 索引、
  `docs/features/dataset_management_system/tasks/DMS-DEV-EPIC-021.md`、`CLAUDE.md`）需一併改號。
- my_workstation 的 §1.9 內文引用 `documentation_conventions.md` §2.3「Done 後折併回主文件」，
  該處實為 §2.1；kit 已修正，my_workstation 端仍待修。

## 7. 結案補記（`PEV-DEV-AGENT-020` 清帳，2026-08-18）

本工單的 14 條 AC 早在 2026-08-16 就全部打勾、交付物也全部進了主線，
但 Status 一直停在 `In Review` 沒有人收尾——**帳面落後現實兩天，而沒有任何機制會叫**。
`PEV-DEV-AGENT-020` 清帳時發現，於此結案。

- **`Closed` 填 `2026-08-16T15:05+08:00`**，取最後一次實質變更的 commit 時間（`cd0e1ff`），
  **不是清帳當天**——填當天等於偽造完成時點。
- **交付物實查**（不採信 AC 勾選，依 `PEV-DEV-AGENT-015` 的取證義務）：
  `kit/.agent/resources/team_protocol.md` 有 §1.11、`kit/docs/standards/team_protocol.md`
  指路檔存在、`install.sh` 具備 `--upgrade`／`--dry-run` 與 `.agent/.kit-manifest` 機制。
- **不補 `reviews/KIT-DEV-AGENT-001.md`**：審查檔是 `PEV-DEV-AGENT-016` 之後才有的機制，
  本工單建立於其前，不追溯適用。結案理由記在
  [`reviews/PEV-DEV-AGENT-020.md`](../../process_evolution/reviews/PEV-DEV-AGENT-020.md)。
- **§6 的 follow-up 不阻擋結案**：那兩條待修都在 `../my_workstation`，是另一個 repo 的事。

這次漏帳催生了 `PEV-DEV-AGENT-022` 的其中一項檢查：
**AC 全數打勾但 Status 不是 `Done`／`Canceled`**，讓同一種漏帳下次由 precheck 攔下。
