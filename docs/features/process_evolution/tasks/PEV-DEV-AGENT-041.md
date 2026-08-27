# [Task ID: PEV-DEV-AGENT-041] 安全遷移本 repo 的 Claude／Codex／GitHub 設定

**🔗 依附母任務 (Parent Task ID):** DN-010／DN-011（硬依賴 `PEV-DEV-AGENT-040`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-27T00:27+08:00
**🔀 審查載體編號 (PR/MR):** `../reviews/PEV-DEV-AGENT-041.md`（無遠端 PR，見 git_workflow.md §8.3）

## 1. 任務描述 (Description)

用新 `migrate` 流程處理本 repo 已存在的 `CLAUDE.md`、未追蹤 `AGENTS.md` 與 `.codex/`，
保留專案規則與仍需使用的本機功能，同時移除跨供應商污染、絕對路徑與重複真相。

> ✅ **裁定（2026-08-27，使用者）：** 本專案不再使用 headroom；遷移時移除所有現行
> headroom hook、proxy URL 與入口說明，不保留或搬移該功能。已結案工單與已畢業 DN
> 仍依 §1.11 保持歷史原貌，不把刪除歷史證據誤當成移除現行設定。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：目前三份入口／設定、本輪 034～040 的標準與工具。
- **Outputs**：本 repo 的正式雙入口、portable Codex project config、local-only 邊界、路由政策與審查紀錄。

GitHub 狀態要分別記錄：remote URL、SSH 功能、`gh api user`、Codex Cloud Connector。
`gh auth status` 與功能 probe 矛盾時不得把可用 API 判死；Connector 不可觀察時保留 `unknown`。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`migrate --dry-run` 先產生候選與差異，沒有改動工作區。
- [x] AC-02：正式遷移後 `AGENTS.md` 為共同真相，`CLAUDE.md` 只保留匯入與 Claude 專屬內容。
- [x] AC-03：現有專案規則無遺漏；必備規則集合測試全綠。
- [x] AC-04：`.codex/` 只版控 portable allowlist；`ANTHROPIC_BASE_URL` 與個人絕對 hook 不進 commit。
- [x] AC-05：本機 headroom hook、proxy URL 與現行入口說明已移除；其他個人設定不受牽連。
- [x] AC-06：doctor 實跑 Claude Code、Codex CLI、Git remote、SSH、GitHub API；Connector 無法驗則 unknown。
- [x] AC-07：路由政策同時允許 Claude Code 與 Codex，本機至少一個 profile verified。
- [x] AC-08：repo 內無 token、cookie、SSH key 或家目錄絕對路徑被納入版控。
- [x] AC-09：pytest、precheck、installer dry-run 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：若 Codex App Connector 仍無法觀察，只記 unknown，不阻擋本機流程。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不自動修改全域供應商設定、不重設登入、不 push。
