# [Task ID: ABC-DEV-BE-001] 實作角色與權限資料表

**🔗 依附母任務 (Parent Task ID):** ABC-DOC-EPIC-001
**🏷️ 任務類型 (Task Type):** queue_backend
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** In Progress
**📅 建立時間 (Created):** 2026-01-06T10:00+08:00
**✅ 完成時間 (Closed):** —

## 1. 任務描述 (Description)
依 LLD 建立 roles / permissions / role_permissions 三張資料表與對應 migration。

## 2. 規格：輸入與輸出 (Inputs & Outputs)
- **Inputs (輸入/依賴項目)**:
  - `docs/features/example_module/lld.md`
- **Outputs (輸出/預期變更)**:
  - `backend/models/role.py`、對應的 migration 檔

## 3. 驗收標準 (Acceptance Criteria)
- [ ] migration 可正向與反向執行且不遺失資料
- [ ] 三張表的外鍵與唯一鍵約束符合 LLD

## 4. 人為補充與確認 (Human-in-the-loop)
- **❓ 需要確認的事項 (Agent 提問)**:
  - 無
- **✍️ User 補充回覆 (User Input)**:
  - —
