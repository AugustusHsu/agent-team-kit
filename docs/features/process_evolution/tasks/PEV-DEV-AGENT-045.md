# [Task ID: PEV-DEV-AGENT-045] 實作輪次分支、worktree 與所有權流程

**🔗 依附母任務 (Parent Task ID):** DN-006
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🧭 任務輪廓 (Task Profile):** parallel_long_running
**🧩 必備能力覆寫 (Required Capabilities):** —
**🔐 資料分級 (Data Class):** —
**↪️ Execution 覆寫 (Execution Override):** —
**⛓️ 前置工單 (Blocked By):** PEV-DEV-AGENT-043
**✍️ 寫入範圍 (Write Scope):** `kit/docs/development/overlap_zones.md`、`kit/.agent/skills/devops-engineer/SKILL.md`、`install.sh`、`tests/test_install.py`、`tests/test_git_workflow.py`
**📜 共用契約 (Contract):** `kit/docs/standards/parallel_development.md`
**🔁 變更集合 (Change Set):** —
**🪜 變更階段 (Phase):** —
**🚥 任務狀態 (Status):** In Review
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

把短命工作輪次、條件式 worktree、動態 Write Scope 與專案級 overlap zones 變成可操作流程，
並用真實暫存 Git repo 證明兩層 merge 拓撲、first-parent 視圖與安全清理。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - `kit/docs/standards/parallel_development.md`
  - `kit/docs/standards/git_workflow.md`
  - `install.sh`
  - `kit/.agent/skills/devops-engineer/SKILL.md`
- **Outputs (輸出/預期變更)**：
  - 可由專案維護且升級保留的 `overlap_zones.md` 種子檔。
  - DevOps 操作指引：開輪前所有權檢查、2+ 同時活躍工單才建 worktree、合併後清理與退回重建。
  - 真實 Git repo 測試：工單→輪次→主線的 merge commit 拓撲、同期主線變更與安全刪支。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`overlap_zones.md` 是專案版控種子，記錄長期高風險範圍而不複製輪次內 Write Scope；upgrade 保留使用者內容。
- [x] AC-02：兩張以上工單「同時活躍」才要求一 branch 一 worktree；建立前檢查 Write Scope／Contract／overlap zone，重疊預設改為排序而非並行。
- [x] AC-03：工單分支以 merge commit 進輪次、輪次以 merge commit 進主線；分支名稱刪除後仍由 merge 訊息中的 Task／Round ID 保留可追溯性。
- [x] AC-04：真實暫存 repo 同時涵蓋兩張平行工單、main 同期前進、最終整合、main／round 的 first-parent 視圖與 `git branch -d` 安全回收。
- [x] AC-05：工單併入輪次後移除其 worktree但保留 branch；輪次完成後只剩主工作目錄，退回時可由原 Task ID／branch 重建。
- [x] AC-06：`git rerere` 只列 repo-local 選用項，不改 kit 預設、不版控 rr-cache；重用後仍要求檢查 diff 與重跑測試。
- [ ] AC-07：`is_seed_file()` 與 `tests/test_install.py::test_升級保留種子檔` 同步；安裝、升級與 Git 拓撲測試通過。

> AC-07 的開發分支證據已通過；核取留待 047 將新版流程與種子檔同步至根目錄安裝實例後，
> 由 fresh-context reviewer 以正式安裝入口複驗。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：只有命中安全政策、公開 API、migration 或核准的關鍵 overlap zone 時，於輪次整合點請使用者作最終裁定。
- **✍️ User 補充回覆 (User Input)**：已同意保留兩層拓撲與 Round Manifest。

## 5. 範圍外 (Out of Scope)

- 不建立永久模組分支，不設定固定日曆 rebase，不讓 worktree 取代檔案所有權。
- 不修改遠端 branch protection、不 push。
