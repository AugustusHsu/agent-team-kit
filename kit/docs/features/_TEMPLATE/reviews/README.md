# 審查檔 (Code Review Records)

一張工單一個檔，與工單同名：`tasks/<TaskID>.md` ↔ `reviews/<TaskID>.md`。

- 放的是 `code-reviewer` SKILL.md §4 的**完整審查報告**：AC 逐條核對表、
  重大瑕疵與建議改法、Nitpicks、僅人工判讀的部分。
- 多輪審查**追加在同一檔內，新的放最前面**，每輪以
  `## {YYYY-MM-DD} ✅ APPROVED` 或 `## {YYYY-MM-DD} ❌ CHANGES REQUESTED` 起頭。
- 工單那邊只留結論行、📊 客觀指標表，以及退回時的待修正項目單行清單。
  正版規則見 `.agent/resources/team_protocol.md` §2.3。
- 本目錄**不會**被 `.agent/scripts/scan_backlog.py` 掃描（它只讀 `tasks/*.md`）。

沒有遠端 PR／MR 的專案，這個檔案就是唯一的審查載體，
因此 **APPROVED 也必須寫**（見 `docs/standards/git_workflow.md` §8.3）。
