# [Task ID: PEV-DEV-AGENT-044] 實作工單 DAG、欄位與 wave 驗證

**🔗 依附母任務 (Parent Task ID):** DN-005
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** backend-developer
**🧭 任務輪廓 (Task Profile):** —
**🧩 必備能力覆寫 (Required Capabilities):** —
**🔐 資料分級 (Data Class):** —
**↪️ Execution 覆寫 (Execution Override):** —
**⛓️ 前置工單 (Blocked By):** PEV-DEV-AGENT-043
**✍️ 寫入範圍 (Write Scope):** `kit/.agent/resources/task_template.md`、`kit/docs/features/_TEMPLATE/tasks/_EXAMPLE-DEV-BE-001.md`、`kit/.agent/scripts/scan_backlog.py`、`kit/.agent/scripts/precheck.py`、`kit/.agent/skills/scrum-master/SKILL.md`、`kit/docs/standards/git_workflow.md`、`kit/docs/standards/parallel_development.md`、`kit/docs/standards/adr/ADR-001_task_dag_and_ownership.md`、`tests/test_scan_backlog.py`、`tests/test_precheck.py`、`docs/features/process_evolution/tasks/PEV-DEV-AGENT-043.md`、`docs/features/process_evolution/tasks/PEV-DEV-AGENT-047.md`
**🌐 外部副作用 (External Effects):** —
**📜 共用契約 (Contract):** `kit/docs/standards/parallel_development.md`
**🔁 變更集合 (Change Set):** —
**🪜 變更階段 (Phase):** —
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**✅ 完成時間 (Closed):** 2026-08-28T12:03+08:00
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
  - 工單模板新增 `Blocked By`、`Write Scope`、`External Effects`、`Contract`、`Change Set`、`Phase`，舊工單仍可讀。
  - 掃描器與 precheck 解析工單／Round Manifest、驗證依賴與輪次不變式並產生推導視圖。
  - Scrum Master 指引改用來源欄位拆單，不手寫 `[P]`、wave 或反向 blocks。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：新版模板包含六個來源欄位；未含原五欄或只缺 `External Effects` 的歷史工單仍能被掃描，不因遷移前資料中斷 BACKLOG；缺外部副作用來源時不得取得並行資格。
- [x] AC-02：`Blocked By` 的每個非空 token 都必須是完整 Task ID；未知 Task ID、自我依賴、重複依賴與有向循環都有明確錯誤；合法 DAG 產出確定性的拓撲順序、wave 與反向 blocks。
- [x] AC-03：Round Manifest 必須有全域 Round ID、目標、完整 `feature/{topic}` branch、Integration Review Target、存在於 repo 的 40 字元 opening base commit 與封閉的 2～5 張既有 Task ID；重複歸屬、超額、缺漏皆失敗。
- [x] AC-04：並行候選只在 DAG 無邊、Write Scope 可證不重疊、Contract 已位於 round base 且無 peer 同時修改、外部副作用有來源證據可隔離時成立；glob 或副作用不可判定時不得誤標可並行。
- [x] AC-05：Parallel Change 驗證 expand 建立時已有同 Change Set 的 contract，phase 只接受 `expand|migrate|contract`，每張 migrate 都在 expand 之後，且 contract 的 `Blocked By` 涵蓋所有 migrate 工單。
- [x] AC-06：測試以 `tmp_path` 建真實 Markdown／manifest，涵蓋合法圖、負向案例與舊格式相容；不使用 mock，測試名稱與 assert 訊息使用繁體中文。
- [ ] AC-07：`test_scan_backlog.py`、`test_precheck.py`、BACKLOG 重建與 `git diff --check` 通過。

> AC-07 的開發分支證據已通過；核取留待 047 將 `kit/` 同步至根目錄安裝實例後，
> 由 fresh-context reviewer 以正式安裝入口複驗。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無；欄位與推導邊界已由 DN-005 簽核。
- **✍️ User 補充回覆 (User Input)**：同意建立 `ROUND-001` 與工單 043～047；2026-08-27
  同意擴大 044 Write Scope，納入 `kit/docs/standards/git_workflow.md` 以同步 precheck 第 9 項；
  同意新增 `External Effects` 來源欄位並納入 `kit/docs/standards/parallel_development.md`；
  同意擴大 044 Write Scope，等義正規化 043／047 的規劃來源欄位；同意修正第三輪 findings。
  2026-08-28 同意修正第四輪 findings。
  2026-08-28 同意修正第五輪 finding。

## 5. 範圍外 (Out of Scope)

- 不操作 Git branch／worktree，不執行 panel，不自動改寫工單依賴。
- 不要求一次性補齊所有歷史工單的新欄位。

## 📝 Code Review 備註
> 2026-08-28 第五輪 ❌ CHANGES REQUESTED — 完整報告見 [../reviews/PEV-DEV-AGENT-044.md](../reviews/PEV-DEV-AGENT-044.md)

### 📊 客觀指標
| 指標 | 變更前／負向對照 | 變更後 |
|---|---:|---:|
| 目標兩檔 | reviewed head：91 passed | 修正後：91 passed、0 failed |
| rejected head＋新 tests | 89 passed、2 failed | 91 passed、0 failed |
| 全套驗證 | reviewed head：232 passed、4 baseline failed | 232 passed、4 baseline failed |
| precheck／diff | — | 8/8、9/9／通過 |

### 待修正項目
- `kit/.agent/scripts/scan_backlog.py:161`：Write Scope／Contract 必須拒絕破折號空值混入實際路徑。
