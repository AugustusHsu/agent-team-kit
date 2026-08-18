# [Task ID: PEV-DEV-AGENT-027] qa-automation-engineer 的技術棧內容拆成第 2 層

**🔗 依附母任務 (Parent Task ID):** —（硬依賴 `PEV-DEV-AGENT-025`，同檔）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** system-architect
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-18T21:40+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

[DN-004](../../../design_notes/DN-004_skill_system_realignment.md) §1.4a 查出的
**第二類脫節：skill 與 kit 的定位脫節**，§4 待決 4.4 由使用者裁定
「拆成第 2 層由專案填」。

**問題**：kit 的定位是「可安裝到**任何**專案」，但
`kit/.agent/skills/qa-automation-engineer/SKILL.md` 硬綁 Pytest／Cypress——
386 行中有 107 行（28%）是程式碼範例，且 §2 有一句明文
**「不可自行引入其他框架」**。這對非 Python／非 Cypress 的專案不只是無用，
是**有害**：agent 會照著禁止使用該專案實際採用的測試框架。

這同時是篇幅失衡的成因（386 行 vs `backend-developer` 38 行，10 倍差距）。

**做法**：形狀同 [DN-007](../../../design_notes/DN-007_ci_gate.md) 選 C（adapter）——
skill 留與技術棧無關的部分，技術棧專屬內容移到專案自己填的落點。

**已知代價（使用者裁定時已知並接受）**：抽走範例後 skill 會變抽象，
新專案沒有可抄的樣板。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**輸入：** `kit/.agent/skills/qa-automation-engineer/SKILL.md`（386 行）。

**留在 skill 的**（技術棧無關）：AAA 結構原則、Mock 判準、環境隔離原則、交付格式、
與 `team_protocol.md` 的流程銜接。

**移出的**：107 行 Pytest／Cypress 程式碼範例，以及 §2「不可自行引入其他框架」那句。

**落點**：專案自己填的第 2 層。沿用 `team_protocol.md` §1.12 第 2 層的形狀——
kit 定義到「這裡要填什麼」，實際內容由每個專案在自己的落點寫。
落點的具體位置在執行時決定並寫進審查紀錄（候選：skill 內留一個
「本專案的測試框架」小節，或指向專案 `CLAUDE.md`）。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：§2「不可自行引入其他框架」那句移除。
- [ ] AC-02：107 行 Pytest／Cypress 程式碼範例移出 skill 本體。
- [ ] AC-03：skill 內留下**明確的第 2 層落點說明**——寫清楚專案要填什麼、
      不填的後果是什麼。比照 §1.12 第 2 層的寫法（「缺了本節在該專案就是空的」）。
- [ ] AC-04：`grep -rniE 'pytest|cypress' kit/.agent/skills/qa-automation-engineer/SKILL.md`
      剩下的每一筆都是「舉例性質」而非「規定性質」，逐筆列進審查紀錄佐證。
- [ ] AC-05：抽完後 skill 仍能獨立指導一次完整交付——審查時實跑一次
      「假設專案用 Jest」的情境，確認 skill 沒有任何一句擋住它。
      這是 AC-01 的正向驗證，不是形式檢查。
- [ ] AC-06：本 repo 自己的第 2 層一併填上（dogfooding：本 repo 用 Pytest），
      否則本 repo 的 `qa-automation-engineer` 會變成空的。
- [ ] AC-07：`uv run pytest` 全綠；`python3 .agent/scripts/precheck.py` 6 項全綠。
- [ ] AC-08：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- 4.4 由使用者於 2026-08-18 裁定「拆成第 2 層由專案填」，並明示已接受
  「新專案沒有可抄的樣板」這項代價。

## 5. 範圍外 (Out of Scope)

- **不動其他 12 份 skill**——`PEV-DEV-AGENT-025`。
- **不處理該檔的引用對齊**（§1.12、章節標題）——同樣屬 `025`，
  本工單必須等 `025` 合併後才開始，否則同檔衝突。
- **不定 skill 撰寫標準**——`PEV-DEV-AGENT-028`。
