# [Task ID: {模組前綴}-{階段}-{佇列}-{流水號}] [在此填寫工單標題]

**🔗 依附母任務 (Parent Task ID):** [在此填寫追溯來源，例如: ABC-DOC-HLD-001 或 Independent]
**🏷️ 任務類型 (Task Type):** [在此填寫類型，例如: queue_frontend, queue_backend, queue_agent, queue_data, docs_generation, manual_user]
**👤 負責人 (Assignee):** [指定 Skill 名稱，例如: backend-developer, frontend-developer, devops-engineer；若需使用者親自處理填 manual_user]
**🚥 任務狀態 (Status):** Pending / Ready / In Progress / In Review / Done
**📅 建立時間 (Created):** {YYYY-MM-DDTHH:MM+08:00}
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** — [開 PR／MR 的當下回填編號（例如 #42）；未使用 PR 平台的專案保持 —。留空無法區分「沒有 PR」與「忘了填」]

## 1. 任務描述 (Description)
[簡潔明瞭地描述這張工單要達成什麼目的、為何要做這件事]

## 2. 規格：輸入與輸出 (Inputs & Outputs)
- **Inputs (輸入/依賴項目)**:
  - [在此列出前置依賴：對應的 PRD/HLD 文件連結、Figma 設計稿、需要讀取的現有 DB Schema、或現有的程式碼路徑]
- **Outputs (輸出/預期變更)**:
  - [在此列出預期產出：產生的程式碼檔案(src/...)、更新的資料庫表、建立的元件、或寫入的文件]

## 3. 驗收標準 (Acceptance Criteria)
*(工單被認定「已完成」必須達成的客觀條件)*
<!--
  📌 Epic 工單專用規則：
  若本工單為 Epic (DOC-EPIC-*) 且會產出子工單，
  **第一條 AC 必須為**：
  - [ ] 所有 N 張子工單皆完成並通過 Code Review
  其中 N 為預計產出的子工單數量。此條 AC 由 Code Reviewer 或 Scrum Master
  在最後一張子工單**合併完成**（Status 成為 Done）時勾選。
-->
- [ ] [條件 A：例如 API 成功回傳 200 並包含特定的 JSON 結構]
- [ ] [條件 B：例如出現特定的錯誤時，前端跳出 Toast 警告]
- [ ] [條件 C：...]

## 4. 人為補充與確認 (Human-in-the-loop)
*(針對本工單尚未定義清楚，或在拆解時發現需要利害關係人/User 介入決策與手動補充的項目)*
- **❓ 需要確認的事項 (Agent 提問)**:
  - [若資訊充足，填寫：無。若有疑慮，列出精確的問題要求 User 解答]
- **✍️ User 補充回覆 (User Input)**:
  - [留空，由 User 閱讀後於此處親手填寫]
