# [Task ID: PEV-DEV-AGENT-037] 實作 agent runtime state、provider registry 與 init

**🔗 依附母任務 (Parent Task ID):** DN-011（硬依賴 `PEV-DEV-AGENT-036`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

新增 stdlib-only `.agent/scripts/agent_runtime.py`，先完成設定載入、狀態分層與 `init`；
後續 `doctor`／`route` 共用同一套 schema，不各自發明格式。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：034～036 的標準、registry、adapter manifests 與雙入口模板。
- **Outputs**：`agent_runtime.py` 的 `init`、共用 parser／validator、本機狀態格式與測試。

共享政策放 repo；帳號能力放 XDG 使用者目錄；project override 放 repo-local ignored 檔。
狀態只記摘要、時間與錯誤分類，絕不保存 credential 或完整敏感輸出。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：`init` 同時支援互動模式與可重跑 flags／設定檔模式。
- [ ] AC-02：至少一個本機開發 profile verified 才回傳成功，其餘可 `unknown`。
- [ ] AC-03：重跑 `init` 不破壞使用者客製內容，差異以候選或 `.new` 呈現。
- [ ] AC-04：global state 與 repo-local override 正確合併，worktree 使用同一 project identity。
- [ ] AC-05：狀態輸出不含 token、cookie、SSH key、完整環境變數或命令 stdout。
- [ ] AC-06：缺 manifest、schema 版本不支援、JSON 損壞時訊息能指出檔案與欄位。
- [ ] AC-07：所有測試只用標準函式庫、tmp_path 與假 HOME／XDG，不碰真實帳號。
- [ ] AC-08：pytest、precheck 全綠；installer 待合併 0；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不實作網路 probe、route 或自動切換代理。
