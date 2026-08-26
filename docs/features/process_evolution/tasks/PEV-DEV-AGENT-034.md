# [Task ID: PEV-DEV-AGENT-034] 建立跨代理執行標準與任務輪廓 registry

**🔗 依附母任務 (Parent Task ID):** DN-009
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** system-architect
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-26T20:02+08:00
**🔀 審查載體編號 (PR/MR):** 分支 `PEV-DEV-AGENT-034`（見 `../reviews/PEV-DEV-AGENT-034.md`）

## 1. 任務描述 (Description)

把 DN-009 的路由模型寫進第 1 層規範，建立版本化、可擴充的任務輪廓與能力詞彙。
這張只定資料契約與規則，不實作探針或路由命令。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：DN-009 全文、`team_protocol.md` 的 Role／Task Type 語意。
- **Outputs**：
  - `kit/docs/standards/agent_runtime.md`
  - `kit/.agent/resources/agent_runtime/task_profiles.json`
  - `kit/docs/DOCS_MAP.md` 與 `kit/docs/standards/README.md` 登記
  - registry 結構與文件登記測試

標準必須分開 Role、Task Profile、Execution Profile、Availability；Task Type 與 Assignee
不得改成供應商欄位。registry 初版含 DN-009 §3.4 的八個輪廓，且有 schema version。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`agent_runtime.md` 完整定義四個維度、六階段路由順序與四種可用性。
- [x] AC-02：task profile registry 含八個初始輪廓、schema version、必備／選配能力與資料分級。
- [x] AC-03：新增輪廓只需改 registry，不需修改既有 Python enum 或供應商清單。
- [x] AC-04：測試證明未知欄位／重複 ID／未知能力會給出可定位的失敗訊息。
- [x] AC-05：規範明文禁止把 Claude／Codex 寫進 `Task Type` 或 `Assignee`。
- [x] AC-06：Codex CLI 是可攜基線；Codex App／Cloud 是額外 execution profile，不是另一套流程。
- [x] AC-07：文件登記、pytest、precheck 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無，DN-009 已於 2026-08-26 簽核畢業。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不實作 `agent_runtime.py`；不探測本機登入；不修改工單模板。
