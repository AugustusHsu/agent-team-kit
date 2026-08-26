# 文檔地圖 (DOCS MAP)

> 全專案文件導覽。新增模組或規範文件時，回來這裡補一列——這是 AI 與新成員找文件的唯一入口。

## 開場必讀

| 文件 | 用途 |
|---|---|
| [development/BACKLOG.md](development/BACKLOG.md) | **專案現況唯一來源**：進行中／審查中工單、統計、Icebox。由 `scan_backlog.py` 產生，不要手改。 |
| `../CLAUDE.md` | 每個 AI session 的入口摘要 |
| `../.agent/resources/team_protocol.md` | 工單生命週期、角色交接、命名約定（**流程正版**） |
| `../.agent/workflows/commit-message.md` | Commit message 格式、禁止寫入的內容、交付前複查閘門（**commit 正版**） |

## 跨功能規範 (standards/)

| 文件 | 內容 |
|---|---|
| [standards/team_protocol.md](standards/team_protocol.md) | **指路檔**（不含內容）→ 正版在 `../.agent/resources/team_protocol.md`；含章節索引 |
| [standards/git_workflow.md](standards/git_workflow.md) | **Git 流程正版**：分支、commit 時點、PR 閘門、合併與收尾、平台適配與換平台檢查清單 |
| [standards/documentation_conventions.md](standards/documentation_conventions.md) | 文件撰寫慣例 |
| [standards/skill_conventions.md](standards/skill_conventions.md) | **Skill 撰寫標準**：引用格式、必備章節分層、技術棧中立、篇幅上限 |
| [standards/agent_runtime.md](standards/agent_runtime.md) | **多代理執行標準**：任務輪廓、能力路由、執行設定檔、可用性與失效交接 |
| [standards/qa_testing_spec.md](standards/qa_testing_spec.md) | 測試規範與分層策略 |
| [standards/security_audit.md](standards/security_audit.md) | 資安查核表（後端 OWASP Checklist + 前端客戶端查核） |
| [standards/adr/](standards/adr/) | 架構決策紀錄 (ADR) |

<!-- 依專案補上：design_system.md（設計系統）、devenv_spec.md（開發環境）、third_party_versions.yaml -->

## 設計筆記 (design_notes/)

**開單前置關卡**：AC 寫不出來時先開一份 DN，寫得出來就直接開工單。

| 文件 | 用途 |
|---|---|
| [design_notes/README.md](design_notes/README.md) | 什麼時候該開 DN、取號方式、目錄約定 |
| [design_notes/_TEMPLATE.md](design_notes/_TEMPLATE.md) | 新 DN 的範本（含狀態機與畢業條件） |

個別 DN 以全域流水號直接放在該目錄下，**不在這裡逐份登記**——索引由 `scan_backlog.py`
生成在 [development/BACKLOG.md](development/BACKLOG.md) 的「🧪 設計筆記」區塊。

## 模組 (features/)

模組登記表在 [features/README.md](features/README.md)——**由專案自己維護**，
刻意不內嵌在這裡：這份地圖的骨架要能隨 kit 升級推送，會變動的那張表歸專案所有。

## 流程指引 (development/)

| 文件 | 用途 |
|---|---|
| [development/PLAN_FROM_HANDOFF.md](development/PLAN_FROM_HANDOFF.md) | 從交接／需求文件規劃工單的三階段閘門式流程 |

## 讀文件的注意事項

- 大檔（>20KB）先 `grep -n` 定位段落再局部讀，不要整份載入。
- 工單狀態以工單 `.md` 的 `**🚥 任務狀態 (Status):**` 為準；`test_plan.md` 追溯矩陣的狀態欄常滯後。
- 「目前進度」只信 BACKLOG.md 與 `git log`。
