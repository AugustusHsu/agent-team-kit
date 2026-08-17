# 這個 repo 自己的工單

這裡是 **agent-team-kit 本身的開發工單**，套用 `kit/` 出貨的那套慣例
（工單 `docs/features/{模組}/tasks/{TaskID}.md`、審查檔
`docs/features/{模組}/reviews/{TaskID}.md`），但**不會被 `install.sh` 安裝**。

不要跟 `kit/docs/features/` 搞混——那是要複製到使用者專案的樣板。

## 模組前綴對照表

`kit/.agent/resources/team_protocol.md` §3.1 的對照表屬於出貨內容，
只放範例前綴，不能拿來登記本 repo 的模組。本 repo 的前綴登記在這裡。

| 前綴 | 模組 | 類型 | 文件 | 工單 |
|---|---|---|---|---|
| `PEV` | 開發流程演進（PR 流程、審查自動化、展示層） | 基礎建設 | [process_evolution/design_note.md](process_evolution/design_note.md) | `process_evolution/tasks/` |
| `KIT` | 出貨內容同步與安裝／升級機制 | 基礎建設 | *（無 PRD，規格在工單內）* | `kit_sync/tasks/` |
| `WTG` | worktree 防孤兒機制（**已取消**，見 WTG-DEV-BE-001） | 基礎建設 | *（無）* | `worktree_guard/tasks/` |

三個模組**全是基礎建設**：本 repo 的產品就是流程本身，沒有使用者故事可寫，
規格一律直接落在工單的「規格：輸入與輸出」，因此都沒有 PRD。

新增模組時先在上表登記前綴，再開工單。

這張表原本內嵌在 `docs/DOCS_MAP.md`，2026-08-17 依 PEV-DEV-AGENT-009 抽到這裡——
DOCS_MAP 只留骨架才能隨 kit 升級推送，登記表歸 repo 自己所有。
出貨樣板的對應檔案是 `kit/docs/features/README.md`。
