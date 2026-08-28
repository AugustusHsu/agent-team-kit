# [Task ID: PEV-DEV-AGENT-046] 實作 fresh-context panel 與不可變 Review Target

**🔗 依附母任務 (Parent Task ID):** DN-008
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** tech-lead
**🧭 任務輪廓 (Task Profile):** implementation_local
**🧩 必備能力覆寫 (Required Capabilities):** —
**🔐 資料分級 (Data Class):** —
**↪️ Execution 覆寫 (Execution Override):** —
**⛓️ 前置工單 (Blocked By):** PEV-DEV-AGENT-044, PEV-DEV-AGENT-045
**✍️ 寫入範圍 (Write Scope):** `kit/.agent/skills/code-reviewer/SKILL.md`、`kit/.agent/skills/qa-automation-engineer/SKILL.md`、`kit/.agent/resources/team_protocol.md`、`kit/docs/standards/team_protocol.md`、`kit/docs/standards/parallel_development.md`、`kit/docs/features/_TEMPLATE/reviews/_REVIEW_TEMPLATE.md`、`kit/docs/features/_TEMPLATE/reviews/README.md`、`kit/docs/development/rounds/_TEMPLATE.md`、`tests/test_kit_integrity.py`
**📜 共用契約 (Contract):** `kit/docs/standards/parallel_development.md`
**🔁 變更集合 (Change Set):** —
**🪜 變更階段 (Phase):** —
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**✅ 完成時間 (Closed):** 2026-08-28T12:03+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

建立兩層正式審查：每張工單先做 fresh-context 窄審，多工單輪次整合後再由兩個基線面向
獨立檢查並由 `code-reviewer` reconciliation；所有 verdict 固定在不可變 Review Target。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - `kit/docs/standards/parallel_development.md`
  - `kit/.agent/resources/team_protocol.md`
  - `kit/.agent/skills/code-reviewer/SKILL.md`
  - `kit/docs/features/_TEMPLATE/reviews/_REVIEW_TEMPLATE.md`
- **Outputs (輸出/預期變更)**：
  - 工單窄審與輪次 panel 的 fresh-context／取證／回退規範。
  - Round Manifest 範本，承載 Integration Review Target、QA 結果、raw findings 與 reconciliation。
  - 更新 code reviewer、QA reviewer、review template 與 team protocol 指引。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：任何能產生正式 APPROVED 的審查都要求與開發隔離的 fresh context；同 session 換角色只能標自查，不得正式核可。
- [x] AC-02：Review Target 固定為完整 base SHA、head SHA 與 Task／Round ID；PR/MR 或 branch diff 只是介面，head 改變會使不相符 verdict 失效。
- [x] AC-03：工單窄審只查該工單 AC、Write Scope 與測試；多工單輪次才啟動 panel，單張工單不為形式增加 panel。
- [x] AC-04：panel 基線兩面向為整合語意與對抗驗證；安全政策、migration、公開 API 或關鍵 overlap zone 才增加第 3 位風險專家並保留最終人工閘門。
- [x] AC-05：每份 raw finding 至少含 ID、severity、claim、file／line、可重跑 evidence 與 recommended verdict，且先落盤後才允許 reconciliation。
- [x] AC-06：`code-reviewer` 先獨立完成自己的 lane，再逐項標示 accept／reject／duplicate／defer 與理由；所有 blocking finding 直接回查，證據衝突未解時停止並詢問使用者。
- [x] AC-07：Round Manifest 的 QA、raw findings、reconciliation 與人工閘門欄位齊全；不另建重複的 round review 檔。
- [x] AC-08：完整性／precheck 測試通過，且不把特定模型或供應商設為正式審查的必要條件。

> AC-08 已由 047 將新版流程與範本同步至根目錄安裝實例，並由 fresh-context reviewer 以
> 正式安裝入口複驗；全套 259 passed、root／kit precheck 各 9/9。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：只在 blocking 證據衝突無法消解，或安全政策、migration、公開 API、`critical` overlap zone 任一觸發條件式風險最終人工閘門時詢問。
- **✍️ User 補充回覆 (User Input)**：已同意 DN-008 第一、第二批裁定。

## 5. 範圍外 (Out of Scope)

- 不要求模型多樣性，不新增 panel coordinator 角色，不由 panel 取代關鍵風險的人為決策。
- 不為單張工單強制建立 Round Manifest 或 round panel。
