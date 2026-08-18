# [Task ID: PEV-DEV-AGENT-028] 立 skill 撰寫標準：skill_conventions.md

**🔗 依附母任務 (Parent Task ID):** —（硬依賴 `PEV-DEV-AGENT-025`／`026`／`027`）
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** system-architect
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-18T21:40+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

[DN-004](../../../design_notes/DN-004_skill_system_realignment.md) §4 待決 4.1
（使用者裁定「分兩張工單」）的**第二張**，內容為 4.3 的骨架規範。

**為什麼分兩張**：對齊有明確的完成定義（§1.3 三筆修完），撰寫標準沒有；
綁在一起會讓止血等設計。`025`／`026`／`027` 是止血，本張是防復發。

**為什麼排在最後**：撰寫標準應該從**已經對齊過的 13 份 skill** 歸納出來，
而不是先憑空定規則再回頭套。`025`～`027` 跑完才知道哪些慣例真的有用。

**為什麼新開一份而不併入既有文件**（4.3 提案）：
`documentation_conventions.md` 管的是產出文件（BRD／PRD／ADR），
skill 是給 agent 讀的執行指引，兩者讀者與生命週期都不同。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**輸入：** `025`～`027` 完成後的 13 份 skill，以及那三張工單的審查紀錄
（尤其 `025` 的盤點報告——它會列出實際遇到的骨架問題）。

**輸出：** `kit/docs/standards/skill_conventions.md`，並登記進 `kit/docs/DOCS_MAP.md`。

**至少要涵蓋**：

| 項目 | 來源 |
|---|---|
| 引用格式 | A+ 慣例：`team_protocol.md §X.Y 章節標題`，單一寫法（`026`） |
| 必備章節 | 由 `025` 的盤點報告歸納 |
| 技術棧中立原則 | `027` 立下的第 2 層界線——出貨規範不得寫死特定框架 |
| 「適用全角色」章節的處理 | 規範標了就要 13 份全引用（`026` 的檢查 B） |
| 篇幅 | 是否設軟上限，由 `027` 抽完後的實際行數決定 |

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：`kit/docs/standards/skill_conventions.md` 建立，涵蓋 §2 表列五項。
- [ ] AC-02：**同步登記進 `kit/docs/DOCS_MAP.md`**，否則
      `test_standards_文件都登記在_DOCS_MAP` 會失敗（登記檢查只涵蓋 `standards/`）。
- [ ] AC-03：每一條規則都要能回答「不寫這條會出什麼錯」，並引用
      `025`～`027` 的實際案例；寫不出案例的規則不收。
- [ ] AC-04：**不與 `team_protocol.md` 重複表述**——同一條規則不得有兩份表述
      （§1.11 文檔權威階序）。重疊處只指路。
- [ ] AC-05：13 份 skill 逐份對照新標準，落差列進審查紀錄；
      **本張不修**（修的話 `025` 就白做了），落差另開工單或收進標準的「已知例外」。
- [ ] AC-06：`uv run pytest` 全綠；`python3 .agent/scripts/precheck.py` 6 項全綠。
- [ ] AC-07：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- 4.1「分兩張工單」由使用者於 2026-08-18 裁定；4.3 為 AI 提案、同日一併簽核。

## 5. 範圍外 (Out of Scope)

- **不改 13 份 skill 的內容**（AC-05）。
- **不寫成自動檢查**——`026` 已涵蓋可機械驗證的部分；
  其餘（例如「必備章節」）要不要上檢查另議。
