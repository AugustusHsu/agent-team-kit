# [Task ID: ABC-DEV-BE-002] 實作使用者列表分頁 API

**🔗 依附母任務 (Parent Task ID):** ABC-DOC-EPIC-001
**🏷️ 任務類型 (Task Type):** queue_backend
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-01-06T10:05+08:00
**✅ 完成時間 (Closed):** —

## 1. 任務描述 (Description)
提供帶分頁、排序與關鍵字搜尋的使用者列表端點。

## 2. 規格：輸入與輸出 (Inputs & Outputs)
- **Inputs (輸入/依賴項目)**:
  - `docs/features/example_module/api_spec.md`
  - ABC-DEV-BE-001（資料表需先就緒）
- **Outputs (輸出/預期變更)**:
  - `GET /api/v1/users` 端點與對應整合測試

## 3. 驗收標準 (Acceptance Criteria)
- [ ] 回傳 200 且 body 含 `items` 與 `total` 兩個欄位
- [ ] 超出範圍的頁碼回傳空陣列而非 500

## 4. 人為補充與確認 (Human-in-the-loop)
- **❓ 需要確認的事項 (Agent 提問)**:
  - 分頁筆數上限要設多少？（建議值：100）
- **✍️ User 補充回覆 (User Input)**:
  - [留空，由 User 閱讀後於此處親手填寫]
