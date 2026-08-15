# 文檔地圖 (DOCS MAP)

> 全專案文件導覽。新增模組或規範文件時，回來這裡補一列——這是 AI 與新成員找文件的唯一入口。

## 開場必讀

| 文件 | 用途 |
|---|---|
| [development/BACKLOG.md](development/BACKLOG.md) | **專案現況唯一來源**：進行中／審查中工單、統計、Icebox。由 `scan_backlog.py` 產生，不要手改。 |
| `../CLAUDE.md` | 每個 AI session 的入口摘要 |
| `../.agent/resources/team_protocol.md` | 工單生命週期、角色交接、命名約定（**流程正版**） |
| `../.agent/workflows/git-commit.md` | Commit message 格式、禁止寫入的內容、交付前複查閘門（**commit 正版**） |

## 跨功能規範 (standards/)

| 文件 | 內容 |
|---|---|
| [standards/team_protocol.md](standards/team_protocol.md) | **指路檔**（不含內容）→ 正版在 `../.agent/resources/team_protocol.md`；含章節索引 |
| [standards/documentation_conventions.md](standards/documentation_conventions.md) | 文件撰寫慣例 |
| [standards/qa_testing_spec.md](standards/qa_testing_spec.md) | 測試規範與分層策略 |
| [standards/security_audit.md](standards/security_audit.md) | 資安查核表（後端 OWASP Checklist + 前端客戶端查核） |
| [standards/worktree_workflow.md](standards/worktree_workflow.md) | **Git Worktree 工作流程**（出貨內容；⚠️ **本 repo 自己不採用**，見 `../CLAUDE.md`） |
| [standards/adr/](standards/adr/) | 架構決策紀錄 (ADR) |

<!-- 依專案補上：design_system.md（設計系統）、devenv_spec.md（開發環境）、third_party_versions.yaml -->

## 功能模組 (features/)

複製 [features/_TEMPLATE/](features/_TEMPLATE/) 建立新模組後，在下表登記：

> ⚠️ **本 repo 特例**：這裡登記的是 agent-team-kit **自己**的模組。出貨樣板在
> `kit/docs/features/`，前綴權威表在 [features/README.md](features/README.md)。

| 前綴 | 模組 | 文件 | 工單 |
|---|---|---|---|
| `PEV` | 開發流程演進 | [features/process_evolution/design_note.md](features/process_evolution/design_note.md) | `features/process_evolution/tasks/` |
| `KIT` | 出貨內容同步與安裝／升級 | *（無 PRD，規格在工單內）* | `features/kit_sync/tasks/` |
| `WTG` | worktree 防孤兒機制（已取消） | *（無）* | `features/worktree_guard/tasks/` |

## 流程指引 (development/)

| 文件 | 用途 |
|---|---|
| [development/PLAN_FROM_HANDOFF.md](development/PLAN_FROM_HANDOFF.md) | 從交接／需求文件規劃工單的三階段閘門式流程 |

## 讀文件的注意事項

- 大檔（>20KB）先 `grep -n` 定位段落再局部讀，不要整份載入。
- 工單狀態以工單 `.md` 的 `**🚥 任務狀態 (Status):**` 為準；`test_plan.md` 追溯矩陣的狀態欄常滯後。
- 「目前進度」只信 BACKLOG.md 與 `git log`。
