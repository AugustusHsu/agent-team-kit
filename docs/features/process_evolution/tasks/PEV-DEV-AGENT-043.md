# [Task ID: PEV-DEV-AGENT-043] 落地並行開發標準與架構決策

**🔗 依附母任務 (Parent Task ID):** DN-005／DN-006／DN-008
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** system-architect
**🧭 任務輪廓 (Task Profile):** —
**🧩 必備能力覆寫 (Required Capabilities):** —
**🔐 資料分級 (Data Class):** —
**↪️ Execution 覆寫 (Execution Override):** —
**⛓️ 前置工單 (Blocked By):** —
**✍️ 寫入範圍 (Write Scope):** `kit/docs/standards/parallel_development.md`、`kit/docs/standards/git_workflow.md`、`kit/docs/standards/ADR-001_*.md`～`ADR-003_*.md`、`kit/docs/standards/adr/README.md`、`kit/docs/DOCS_MAP.md`、`kit/.agent/resources/team_protocol.md`、`kit/docs/standards/team_protocol.md`、`tests/test_kit_integrity.py`
**📜 共用契約 (Contract):** —（本工單建立 `kit/docs/standards/parallel_development.md`）
**🔁 變更集合 (Change Set):** —
**🪜 變更階段 (Phase):** —
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

把 DN-005、DN-006、DN-008 已簽核的設計轉成可被後續工單引用的第 1 層流程標準，
並以三則 ADR 保存任務 DAG／所有權、輪次分支拓撲與 fresh-context 審查的取捨理由。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - `docs/design_notes/DN-005_parallel_task_decomposition.md`
  - `docs/design_notes/DN-006_branch_topology_and_isolation.md`
  - `docs/design_notes/DN-008_review_panel_and_context_isolation.md`
  - `kit/docs/standards/git_workflow.md`
  - `kit/.agent/resources/team_protocol.md`
  - `kit/docs/standards/documentation_conventions.md`
- **Outputs (輸出/預期變更)**：
  - 新增 `kit/docs/standards/parallel_development.md`，定義 Round Manifest、DAG、Write Scope、Contract、輪次與審查的正版語意。
  - 新增 ADR-001～003 並登記索引；更新 DOCS_MAP 與 team protocol 指路索引。
  - 改寫既有單線／squash-only 敘述，讓 `git_workflow.md` 與 `team_protocol.md` 不和新標準矛盾。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：第 1 層標準完整覆蓋 DN-005 §5.1～5.8、DN-006 §2.1～4.3、DN-008 §4.1～4.8 的已簽核規則，且不把供應商名稱寫成角色或流程前提。
- [ ] AC-02：標準明確定義單張工單一層、多工單輪次兩層、2～5 張封閉集合、開輪 base、事件制同步、merge commit 與 first-parent 視圖。
- [ ] AC-03：標準明確定義 `Blocked By`、`Write Scope`、`Contract`、`Change Set`、`Phase`、Round Manifest 與其唯一來源／推導資料邊界。
- [ ] AC-04：三則 ADR 分別保存「任務 DAG 與所有權」、「短命輪次分支與拓撲保留」、「fresh-context panel 與不可變 Review Target」的採用理由及被否決方案。
- [ ] AC-05：`git_workflow.md`、team protocol 正版與索引、DOCS_MAP、ADR 索引互相連結且無 dead link；DN-003 被推翻的舊說法加入 `已廢除的流程規則` 回歸表。
- [ ] AC-06：`git diff --check`、文件連結／完整性測試與 `precheck.py` 通過。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無；三份 DN 已於 2026-08-27 簽核畢業。
- **✍️ User 補充回覆 (User Input)**：同意建立 `ROUND-001` 與工單 043～047。

## 5. 範圍外 (Out of Scope)

- 本工單只落地規範與 ADR，不實作 DAG 掃描、worktree 操作或 panel 執行器。
- 不建立遠端 PR、不修改託管平台設定、不 push。
