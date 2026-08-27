# [Task ID: PEV-DEV-AGENT-038] 實作 doctor／refresh 與 Claude、Codex、GitHub probes

**🔗 依附母任務 (Parent Task ID):** DN-011（硬依賴 `PEV-DEV-AGENT-037`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-26T23:55+08:00
**🔀 審查載體編號 (PR/MR):** 分支 `PEV-DEV-AGENT-038`（見 `../reviews/PEV-DEV-AGENT-038.md`）

## 1. 任務描述 (Description)

以功能探針而非單一狀態命令判斷 execution profile 可用性，並把 Claude Code、Codex CLI/App
與 GitHub 的不同連線拆開記錄。任何 probe 都不得產生外部寫入副作用。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：adapter manifests、037 的 state engine、2026-08-26 本機探測反例。
- **Outputs**：`doctor`／`refresh` 子命令、probe runner、錯誤分類與測試。

GitHub 至少分 git remote read/write、GitHub API read/write、Codex Cloud Connector、automated review。
Codex App Connector 無可靠 API 時記 `unknown + manual_confirmation`，不得自動開 cloud task。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：零網路檢查與可選 online read probe 分開，`--offline` 不嘗試連線。
- [x] AC-02：Claude Code CLI、Codex CLI 的安裝／版本／auth metadata 都有 adapter probe。
- [x] AC-03：功能 probe 與 metadata 矛盾時保留兩份證據並標 `degraded`，不任選其一。
- [x] AC-04：GitHub 四類能力分開回報；SSH 成功不能推出 Codex Cloud Connector 成功。
- [x] AC-05：App Connector 不可觀察時回 `unknown`，可由使用者人工確認且有到期時間。
- [x] AC-06：TTL 由 adapter 決定；`refresh` 只重跑過期或指定 probe。
- [x] AC-07：探針不得 push、開 PR、傳訊息、修改 Connector、購買或續訂。
- [x] AC-08：用假 executable／fixture 覆蓋成功、未安裝、auth 失效、quota、permission、timeout。
- [x] AC-09：pytest、precheck 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：Codex App Connector 的目前狀態若仍不可觀察，保留 unknown。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不自動登入、不重設 token、不 push、不啟動付費 cloud task。
