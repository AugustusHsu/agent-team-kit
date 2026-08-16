# [DN-004] Skill 體系與現行流程的重新對齊

**🚥 狀態 (Status):** 🌱 Seed
**📅 建立 (Created):** 2026-08-16
**🔗 依賴 (Depends on):** DN-001（本檔的格式）；DN-003（git 流程，其落地會先改動 6 份 skill）
**📌 來源 (Origin):** 使用者指令（2026-08-16）——「目前 skill 已經很久沒更新了，
對於目前流程跟狀況套用 skill 的狀況也需要重新設計」
**🎓 畢業去向 (Landing):** 待填

> 🌱 **Seed 狀態：只有問題陳述，尚未開始比方案。** 依 DN-001 §3.3，
> 要推進到 `Exploring` 再填「選項與取捨」。

## 1. 問題陳述

流程規範（`team_protocol.md`、`docs/standards/`）這幾天持續演進，
但 skill 只有被流程**直接點名**的那幾份跟著改，其餘原地不動。
skill 是 agent 實際執行時讀的東西，規範改了而 skill 沒改，
等於**規範上生效、執行上沒生效**。

實測（2026-08-16，`git log` 統計 `kit/.agent/skills/*/SKILL.md`）：

| skill | 最後變更 | 變更次數 | 行數 |
|---|---|---|---|
| qa-automation-engineer | 08-16 | 4 | 384 |
| code-reviewer | 08-16 | 4 | 103 |
| frontend-developer | 08-16 | 4 | 69 |
| backend-developer | 08-16 | 3 | 36 |
| devops-engineer | 08-16 | 3 | 43 |
| scrum-master | 08-12 | 2 | 135 |
| security-engineer | 08-12 | 2 | 37 |
| business-analyst | 08-12 | **1** | 56 |
| product-manager | 08-12 | **1** | 47 |
| qa-test-planner | 08-12 | **1** | 189 |
| system-architect | 08-12 | **1** | 44 |
| tech-lead | 08-12 | **1** | 39 |
| uiux | 08-12 | **1** | 52 |

兩個訊號：

- **13 份中有 6 份「變更次數 = 1」**，也就是建立當天寫完後再也沒被檢視過。
  它們是否仍與現行流程一致，目前**無人驗證過**。
- **篇幅從 36 行到 384 行，差 10 倍**。`qa-automation-engineer` 一份就超過
  最短的六份加起來。這不太可能是職責複雜度的真實差距，比較像是
  **沒有統一的撰寫標準**，各寫各的。

## 2. 已知的邊界條件

- **DN-003 的落地（PEV-DEV-AGENT-001）會先動到 6 份 skill**
  （4 份 dev ＋ `code-reviewer` ＋ `scrum-master`）。本 DN 不阻擋它，
  也不該把那 6 份的 git 流程修正吸收進來——那是 DN-003 的產出，
  已有工單、已有 AC。本 DN 處理的是**它蓋不到的另外 7 份，以及體系層的問題**。
- **skill 沒有像 `team_protocol.md` 那樣的正版／指路檔關係**，
  也沒有 `documentation_conventions.md` 等級的撰寫慣例。
  「該寫多長、該寫什麼、哪些是每份都要有的骨架」目前沒有規範。
- **沒有自動檢查能發現 skill 與規範脫節**。`tests/` 檢查的是安裝一致性、
  連結有效性、章節索引同步，沒有一項會在「規範改了但 skill 沒改」時亮紅燈。
  DN-003 落地時就是靠人工 `grep` 才找出矛盾敘述——這個做法無法規模化。

## 3. 待決事項

- [ ] 範圍：只做「與現行流程對齊」的修補，還是連 skill 的**撰寫標準**一起定？
- [ ] 那 6 份「從未複檢」的 skill，先做一次全面盤點還是逐份按需處理？
- [ ] 是否需要 skill 的骨架規範（必備章節、篇幅上限、與 `team_protocol.md`
      的引用方式）？若要，落在 `docs/standards/` 哪一份
- [ ] 篇幅失衡怎麼處理？`qa-automation-engineer` 384 行是拆分、瘦身，還是本來就該這麼長
- [ ] **能不能自動偵測脫節？** 例如規範章節有版本號／雜湊，skill 引用時記下，
      不一致就測試失敗。這條若成立，本 DN 的價值遠大於一次性修補
- [ ] 13 個角色是否都還需要？有沒有從未被實際派用過的
