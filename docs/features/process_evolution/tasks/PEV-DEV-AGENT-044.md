# [Task ID: PEV-DEV-AGENT-044] 實作工單 DAG、欄位與 wave 驗證

**🔗 依附母任務 (Parent Task ID):** DN-005
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** backend-developer
**🧭 任務輪廓 (Task Profile):** —
**🧩 必備能力覆寫 (Required Capabilities):** —
**🔐 資料分級 (Data Class):** —
**↪️ Execution 覆寫 (Execution Override):** —
**⛓️ 前置工單 (Blocked By):** PEV-DEV-AGENT-043
**✍️ 寫入範圍 (Write Scope):** `kit/.agent/resources/task_template.md`、`kit/docs/features/_TEMPLATE/tasks/_EXAMPLE-DEV-BE-001.md`、`kit/.agent/scripts/scan_backlog.py`、`kit/.agent/scripts/precheck.py`、`kit/.agent/skills/scrum-master/SKILL.md`、`tests/test_scan_backlog.py`、`tests/test_precheck.py`
**📜 共用契約 (Contract):** `kit/docs/standards/parallel_development.md`
**🔁 變更集合 (Change Set):** —
**🪜 變更階段 (Phase):** —
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

讓工單與 Round Manifest 成為可機械驗證的依賴圖：模板承載最小來源欄位，掃描器／precheck
拒絕無效 DAG 與輪次，並穩定推導 wave、可並行集合及反向 blocks。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - `kit/docs/standards/parallel_development.md`
  - `kit/.agent/resources/task_template.md`
  - `kit/.agent/scripts/scan_backlog.py`
  - `kit/.agent/scripts/precheck.py`
- **Outputs (輸出/預期變更)**：
  - 工單模板新增 `Blocked By`、`Write Scope`、`Contract`、`Change Set`、`Phase`，舊工單仍可讀。
  - 掃描器與 precheck 解析工單／Round Manifest、驗證依賴與輪次不變式並產生推導視圖。
  - Scrum Master 指引改用來源欄位拆單，不手寫 `[P]`、wave 或反向 blocks。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：新版模板包含五個來源欄位；未含新欄位的歷史工單仍能被掃描，不因遷移前資料中斷 BACKLOG。
- [ ] AC-02：未知 Task ID、自我依賴、重複依賴與有向循環都有明確錯誤；合法 DAG 產出確定性的拓撲順序、wave 與反向 blocks。
- [ ] AC-03：Round Manifest 必須有全域 Round ID、目標、branch、40 字元 opening base SHA 與封閉的 2～5 張既有 Task ID；重複歸屬、超額、缺漏皆失敗。
- [ ] AC-04：並行候選只在 DAG 無邊、Write Scope 不重疊、Contract 已位於 round base、外部副作用可隔離時成立；不可判定時不得誤標可並行。
- [ ] AC-05：Parallel Change 驗證 expand 建立時已有同 Change Set 的 contract，phase 只接受 `expand|migrate|contract`，且 contract 的 `Blocked By` 涵蓋所有 migrate 工單。
- [ ] AC-06：測試以 `tmp_path` 建真實 Markdown／manifest，涵蓋合法圖、負向案例與舊格式相容；不使用 mock，測試名稱與 assert 訊息使用繁體中文。
- [ ] AC-07：`test_scan_backlog.py`、`test_precheck.py`、BACKLOG 重建與 `git diff --check` 通過。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無；欄位與推導邊界已由 DN-005 簽核。
- **✍️ User 補充回覆 (User Input)**：同意建立 `ROUND-001` 與工單 043～047。

## 5. 範圍外 (Out of Scope)

- 不操作 Git branch／worktree，不執行 panel，不自動改寫工單依賴。
- 不要求一次性補齊所有歷史工單的新欄位。
