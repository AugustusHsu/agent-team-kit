# [Task ID: PEV-DEV-AGENT-042] 混合代理路由與交接端到端驗證

**🔗 依附母任務 (Parent Task ID):** DN-009／DN-010／DN-011（硬依賴 `PEV-DEV-AGENT-041`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** qa-automation-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-27T08:11+08:00
**🔀 審查載體編號 (PR/MR):** `../reviews/PEV-DEV-AGENT-042.md`（無遠端 PR，見 git_workflow.md §8.3）

## 1. 任務描述 (Description)

以隔離假專案與本 repo dogfooding 驗證整條流程：安裝 → 初始化 → 健康檢查 → 路由 →
中途失效 → 交接 → 審查證據。這張不增加新功能，只負責證明前八張能一起工作。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：034～041 的出貨內容、runtime 工具與本 repo 設定。
- **Outputs**：端到端測試、情境矩陣、操作指南、審查紀錄與必要的回歸修正。

所有自動測試離線執行，以假 executable／假 HOME／假 Git repo 模擬；真實帳號只做唯讀 manual probe，
不可讓測試依賴使用者訂閱或網路。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：新專案從 install 到至少一個 verified local profile 全流程可重跑。
- [x] AC-02：Claude＋Codex 都可用時，依能力與偏好選出 profile 並說明排除理由。
- [x] AC-03：只有 Claude、只有 Codex、另一家訂閱失效三種情境都能正常降級。
- [x] AC-04：執行中 quota/auth 失效時保留 Task ID、branch、HEAD、AC 與驗證證據再重路由。
- [x] AC-05：禁止 cloud 的任務不會因本機候選失效而偷選 Codex Cloud。
- [x] AC-06：GitHub SSH／API 可用但 App Connector unknown 時，本機工作不被阻擋、cloud profile 不被選。
- [x] AC-07：App Worktree 是選配增強；只裝 Codex CLI 的環境仍符合最低門檻。
- [x] AC-08：第三個假 provider 透過 manifest 加入，不修改核心程式。
- [x] AC-09：審查紀錄包含完整路由證據、失效交接與人工確認點。
- [x] AC-10：全套 pytest、precheck、install/upgrade/dry-run 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無外部寫入；任何 Connector 狀態僅人工確認。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不測付費額度消耗、不開 cloud task、不 push、不新增第三家正式支援。
