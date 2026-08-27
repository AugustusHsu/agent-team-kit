# [Task ID: PEV-DEV-AGENT-039] 實作 route／explain 與失效重路由

**🔗 依附母任務 (Parent Task ID):** DN-009／DN-011（硬依賴 `PEV-DEV-AGENT-038`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-27T00:01+08:00
**🔀 審查載體編號 (PR/MR):** 分支 `PEV-DEV-AGENT-039`（見 `../reviews/PEV-DEV-AGENT-039.md`）

## 1. 任務描述 (Description)

把任務輪廓、資料政策、最新可用性與使用者覆寫組成可解釋的決策；中途失效時保留同一張
工單與角色，只替換 execution profile，不偷偷降級成不符合硬性能力的候選。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：034 registry、037 state、038 probes。
- **Outputs**：`route`／`explain` 子命令、排序器、override 與 reroute 資料格式、測試。

排序固定為硬性能力 → 資料政策 → 可用性 → 專案偏好 → 簡單分數 → 使用者覆寫。
輸出同時提供 machine-readable JSON 與人類可讀理由。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：缺硬性能力或違反資料政策的 profile 永遠不進排序。
- [x] AC-02：只有一個供應商時仍跑路由並驗能力；不可把「已登入」當成全部能力成立。
- [x] AC-03：層內簡單評分完全可解釋，輸出每個候選的得分與排除理由。
- [x] AC-04：override 預設單次；整輪／永久必須明示 scope 與到期條件。
- [x] AC-05：零候選時列出缺少能力，不靜默選擇 `unknown` 或 cloud 違規候選。
- [x] AC-06：中途失效產生 handoff 候選，包含 Task ID、branch、HEAD、AC、驗證與失效類型。
- [x] AC-07：有外部副作用的任務只提出建議並等待；純讀子任務才可由政策允許自動接手。
- [x] AC-08：相同輸入必得相同決策；測試覆蓋單供應商、雙供應商、過期 cache、禁止 cloud。
- [x] AC-09：pytest、precheck 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不自動操作 Codex App UI，不代替使用者購買或切換訂閱。
