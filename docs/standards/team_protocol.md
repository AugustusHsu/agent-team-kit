# 開發團隊協作守則 (Team Protocol) — 指路檔

> ⚠️ **本檔不含內容。正版在 [`.agent/resources/team_protocol.md`](../../.agent/resources/team_protocol.md)。**

## 為什麼分兩處

協作守則的讀者是 AI 虛擬團隊的各個 SKILL（`.agent/skills/*/SKILL.md` 全部在開頭「前置閱讀」指向 `.agent/resources/team_protocol.md`），因此正版住在 `.agent/`。但 `docs/standards/` 是人類讀者的規範入口，需要一個進入點——本檔即為該進入點。

**同步策略：不複製、不做 symlink，只留指路。**

- **不複製**：兩份一定會分岔。實際發生過的樣態是——`docs/standards/` 的拷貝停在舊版本，缺了正版後來新增的章節，而全專案工單引用章節編號時指的都是正版；拷貝於是變成一份沒人維護、卻長得像正版的假貨。
- **不用 symlink**：`grep -rn`（查證流程的主力指令）**不跟隨** symlink，只有 `grep -R` 才跟隨。改成 symlink 會讓 `docs/standards/` 在日常搜尋中變成黑洞——搜得到路徑、搜不到內容。

## 章節索引（內容請至正版閱讀）

| 章節 | 主題 |
|---|---|
| §1 | 工單生命週期 (Task Lifecycle) |
| §1.1 | 退回機制 (Rejection Flow) |
| §1.2 | 矛盾暫停 (Contradiction Halt) |
| §1.3 | Epic 關閉條件 |
| §1.4 | 母子工單狀態連動 |
| §1.5 | 狀態更新操作方式 |
| §1.6 | 日期欄位更新規則 |
| §1.7 | 執行前的 Human-in-the-loop 確認 (🔒 HITL Gate at Execution) |
| §1.8 | 新發現缺陷的收容優先序 (🔁 Defect Routing Priority) |
| §1.9 | 程式碼隔離與分支 (🔀 Code Isolation) |
| §1.10 | Commit 閘門 (🔒 HITL Gate before Commit) |
| §1.11 | 文檔權威階序 (📚 Source of Truth Hierarchy) |
| §1.12 | 取證通道保真 (🔬 Evidence Channel Fidelity) |
| §2 | 角色交接規範 (Handoff Rules) |
| §2.1 | Scrum Master → Developer |
| §2.2 | Developer → Code Reviewer |
| §2.3 | Code Reviewer → Done / 退回 |
| §2.4 | 多工單輪次 Panel 與 Reconciliation |
| §3 | 共用命名約定 (Naming Conventions) |
| §3.1 | Task ID 編碼規則 |
| §3.2 | 檔案存放慣例 |

> 改動正版的章節結構時，記得回來同步這張表——它是本檔唯一會過期的部分。

## 相關

- Git 流程正版（§1.9／§1.10 的操作手冊面）：[git_workflow.md](git_workflow.md)
- 並行流程正版（DAG、所有權、工作輪次與 panel）：[parallel_development.md](parallel_development.md)
- 工單模板：[`.agent/resources/task_template.md`](../../.agent/resources/task_template.md)
- 文件分檔與交叉引用守則：[documentation_conventions.md](documentation_conventions.md)
- Commit message 正版：[`.agent/workflows/commit-message.md`](../../.agent/workflows/commit-message.md)
