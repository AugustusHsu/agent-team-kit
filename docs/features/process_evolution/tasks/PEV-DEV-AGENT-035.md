# [Task ID: PEV-DEV-AGENT-035] 建立雙入口模板與供應商 adapter manifests

**🔗 依附母任務 (Parent Task ID):** DN-010（硬依賴 `PEV-DEV-AGENT-034`）
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** system-architect
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-26T19:53+08:00
**✅ 完成時間 (Closed):** 2026-08-26T20:10+08:00
**🔀 審查載體編號 (PR/MR):** 分支 `PEV-DEV-AGENT-035`（見 `../reviews/PEV-DEV-AGENT-035.md`）

## 1. 任務描述 (Description)

建立共同 `AGENTS.md`、Claude adapter `CLAUDE.md` 與可擴充 provider manifest。
共同規則只能有一份可編輯真相，供應商專屬設定不得滲入共同層。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：DN-010、`PEV-DEV-AGENT-034` 的 runtime schema、現有 `kit/CLAUDE.md`。
- **Outputs**：
  - `kit/AGENTS.md` 與精簡的 `kit/CLAUDE.md`
  - `kit/.agent/templates/AGENTS.md`、`CLAUDE.md`
  - `kit/.agent/resources/agent_runtime/adapters/*.json`
  - Claude Code CLI、Codex CLI、Codex App Local／Worktree、Codex Cloud 初始 manifests

`CLAUDE.md` 必須以 `@AGENTS.md` 匯入共同內容，只保留 Claude 專屬補充。
adapter manifest 描述能力、surface、probe 名稱與預設 TTL，不含 token、絕對路徑或個人 hook。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：共同規則只在 `AGENTS.md` 維護；`CLAUDE.md` 不複製共同段落。
- [x] AC-02：以隔離沙盒驗證 Claude Code 能實際載入 `@AGENTS.md`，輸出留進審查紀錄。
- [x] AC-03：五個初始 execution profiles 都有 provider、surface、capabilities、probe 與 TTL。
- [x] AC-04：加入第三個假 provider 只需新增 manifest，核心 registry 不修改。
- [x] AC-05：掃描 adapters 與模板，確認無 token、cookie、家目錄絕對路徑及跨供應商環境變數。
- [x] AC-06：`.codex/` 採 allowlist 的版控邊界與 `.claude/` 原生 scope 都寫進標準。
- [x] AC-07：必備規則集合一致性測試能抓到入口遺漏，但允許合理的供應商專屬段落。
- [x] AC-08：pytest、precheck 全綠；BACKLOG 已重生。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：無，DN-010 已簽核。
- **✍️ User 補充回覆 (User Input)**：—

## 5. 範圍外 (Out of Scope)

- 不修改 installer 種子檔邏輯；不搬動本 repo 未追蹤的 `.codex/`。
