# [Task ID: PEV-DEV-AGENT-047] 並行流程端到端驗證與安裝同步

**🔗 依附母任務 (Parent Task ID):** DN-005／DN-006／DN-008
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** qa-automation-engineer
**🧭 任務輪廓 (Task Profile):** test_verification
**🧩 必備能力覆寫 (Required Capabilities):** —
**🔐 資料分級 (Data Class):** —
**↪️ Execution 覆寫 (Execution Override):** —
**⛓️ 前置工單 (Blocked By):** PEV-DEV-AGENT-046
**✍️ 寫入範圍 (Write Scope):** `tests/test_parallel_development_e2e.py`、`tests/fixture_project/**`、`.agent/**`、`.github/**`、`docs/**`
**📜 共用契約 (Contract):** `kit/docs/standards/parallel_development.md`
**🔁 變更集合 (Change Set):** —
**🪜 變更階段 (Phase):** —
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**✅ 完成時間 (Closed):** 2026-08-28T12:03+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

以隔離假專案與本 repo 的 `ROUND-001` dogfooding 驗證完整鏈路：安裝、規劃 DAG、條件式
worktree、兩層 merge、整合 QA、fresh-context panel、head 失效、退回與安全清理。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - `PEV-DEV-AGENT-043`～`046` 的出貨內容。
  - `install.sh`、`kit/` 與 `tests/fixture_project/`。
  - `docs/development/rounds/ROUND-001_parallel-development.md`。
- **Outputs (輸出/預期變更)**：
  - 真實檔案／subprocess／暫存 Git repo 的端到端測試與負向對照。
  - `./install.sh . --upgrade` 同步後的根目錄安裝實例及最新 BACKLOG。
  - Round Manifest 中的整合驗證、panel、reconciliation 與最終人為閘門證據。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：隔離專案可完成 install → 建輪次 → 解析五張工單 → 推導 wave → 驗證 Write Scope／Contract → 建立與清理 worktree。
- [x] AC-02：暫存 Git repo 實跑工單→輪次→當下主線候選的兩層 merge，驗證 first-parent、同期主線變更、保留拓撲與安全刪支。
- [x] AC-03：工單與輪次 Review Target 都固定 SHA；審查後改變 head 的負向案例會使 verdict 失效並要求只重跑受影響層。
- [x] AC-04：整合失敗可歸因時退回原 Task ID，不可歸因時要求 integration-fix；不得靜默超過一輪五張上限。
- [x] AC-05：單一可用 provider、沒有 Codex App／PR 平台的本機環境仍能完成流程；不依賴網路、付費額度或特定供應商。
- [x] AC-06：測試不使用 mock，以 `tmp_path`、真實檔案及 `subprocess` 執行；中文測試名、assert 訊息與負向案例符合專案測試慣例。
- [x] AC-07：先跑 `./install.sh . --upgrade --dry-run` 再正式同步；同步後無 `.new`、manifest 一致，根目錄安裝實例只來自 `kit/`。
- [x] AC-08：`uv run pytest`、`precheck.py`、安裝／升級／dry-run、BACKLOG 重建與 `git diff --check` 全部通過。
- [ ] AC-09：`ROUND-001` 記錄 pinned integration target、可重跑 QA 證據、所有 raw findings、reconciliation、阻塞項處置與必要的人為裁定。

> AC-09 的 manifest schema、pinned integration target 與整合 QA 證據已在本工單通過窄審並以
> merge commit 進入 `feature/parallel-development` 後落盤；尚待雙 lane raw findings、
> reconciliation 與最終 verdict 依序完成，不能在 panel 前提前核取。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：整合 panel 若命中關鍵 overlap zone 或存在未解證據衝突，提交一份統整報告請使用者裁定。
- **✍️ User 補充回覆 (User Input)**：已同意 `ROUND-001` 與工單 043～047。

## 5. 範圍外 (Out of Scope)

- 不消耗真實 provider 額度、不建立 cloud task、不變更遠端平台設定、不 push。
- 不在此工單新增 043～046 未定義的新功能；發現跨工單缺口時依 round 規則退回或開 integration-fix。
