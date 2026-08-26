# [Task ID: PEV-DEV-AGENT-040] 工單與審查流程接入能力路由證據

**🔗 依附母任務 (Parent Task ID):** DN-009／DN-011（硬依賴 `PEV-DEV-AGENT-039`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** scrum-master
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-27T00:09+08:00
**🔀 審查載體編號 (PR/MR):** 分支 `PEV-DEV-AGENT-040`（見 `../reviews/PEV-DEV-AGENT-040.md`）

## 1. 任務描述 (Description)

把路由接進既有工單驅動流程，但不讓每張工單綁死供應商。工單只保存穩定的 task profile
與必要 override；本次實際選擇、排除理由與交接寫進審查載體。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：039 的 route/explain 輸出、現有 task/review templates、precheck。
- **Outputs**：出貨工單與審查模板、team protocol／runtime standard、precheck 與測試。

新增欄位必須向後相容：舊工單沒填時由 Task Type 映射預設 profile；只有例外才要求 override。
CI 只驗 versioned policy 的 schema、引用與機密未入版控，不讀使用者本機訂閱狀態。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：工單模板可表達 task profile、能力 override、資料分級與 override scope。
- [x] AC-02：舊工單無新欄位仍合法，映射結果可由 `route --explain` 顯示。
- [x] AC-03：審查模板記錄選中 profile、候選排除理由、probe 時間與是否交接。
- [x] AC-04：precheck 驗 shared policy schema、profile 引用與 secret-like 值未進版控。
- [x] AC-05：precheck 不因某使用者 Claude／Codex 未登入而在 CI 轉紅。
- [x] AC-06：負向測試涵蓋未知 profile、非法 override scope、cloud 禁止卻強制 cloud、疑似 token。
- [x] AC-07：team_protocol 的 Role／Assignee 定義維持不變，不加入供應商角色。
- [x] AC-08：所有安裝實例由 `./install.sh . --upgrade` 同步，待合併 0。
- [x] AC-09：pytest、precheck 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不更名既有 Task Type；不把 provider 設成必填欄位。
