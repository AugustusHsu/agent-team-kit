# [Task ID: PEV-DEV-AGENT-036] installer 支援雙入口種子檔與模板升級

**🔗 依附母任務 (Parent Task ID):** DN-010（硬依賴 `PEV-DEV-AGENT-035`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

讓新安裝同時產生 `AGENTS.md` 與 `CLAUDE.md`，升級時兩份都視為專案接手的種子檔；
新版模板則由 `.agent/templates/` 正常升級，避免種子檔永遠收不到結構更新。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：`PEV-DEV-AGENT-035` 的模板與入口、現行 manifest 升級機制。
- **Outputs**：`install.sh`、`tests/test_install.py`、安裝完成訊息、`.gitignore` 最小邊界。

舊專案只有 `CLAUDE.md` 時不得直接覆蓋或假裝遷移成功；installer 只提示後續 `migrate`。
本機 runtime state、個人 Codex hook 與 local settings 必須被排除，portable project config 可版控。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：首次安裝產生雙入口，內容逐位元組等於 kit，manifest 涵蓋兩者。
- [ ] AC-02：升級保留使用者改過的 `AGENTS.md` 與 `CLAUDE.md`，模板本身仍可更新。
- [ ] AC-03：舊安裝只有 `CLAUDE.md` 時 dry-run 不寫入，正式升級不覆蓋且提示 `migrate`。
- [ ] AC-04：`is_seed_file()` 與 `test_升級保留種子檔` 同步更新。
- [ ] AC-05：本機狀態與個人 hook 不會被 installer 出貨或意外納入版控。
- [ ] AC-06：安裝完成訊息改成執行多代理初始化，不再只要求填 `CLAUDE.md`。
- [ ] AC-07：首次安裝、升級、dry-run、無 manifest 舊版四種負向／正向情境實跑留證。
- [ ] AC-08：pytest、precheck 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不實作登入探針；不自動修改既有使用者入口內容。
