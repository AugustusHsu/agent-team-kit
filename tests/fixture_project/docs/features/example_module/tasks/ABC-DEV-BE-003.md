# 這個標題故意不符合 Task ID 格式

**🔗 依附母任務 (Parent Task ID):** ABC-DOC-EPIC-001
**🏷️ 任務類型 (Task Type):** queue_backend
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-01-06T10:10+08:00
**✅ 完成時間 (Closed):** —

## 1. 任務描述 (Description)
本工單的 H1 標題刻意不符合 `# [Task ID: xxx] 標題` 格式，用來釘住 `parse_task_file()` 回退為「以檔名當 Task ID」的行為。

## 2. 規格：輸入與輸出 (Inputs & Outputs)
- **Inputs (輸入/依賴項目)**:
  - 無
- **Outputs (輸出/預期變更)**:
  - 無

## 3. 驗收標準 (Acceptance Criteria)
- [ ] 解析結果的 task_id 等於檔名 `ABC-DEV-BE-003`

## 4. 人為補充與確認 (Human-in-the-loop)
- **❓ 需要確認的事項 (Agent 提問)**:
  - 無
- **✍️ User 補充回覆 (User Input)**:
  - —
