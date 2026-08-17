# [Task ID: PEV-DEV-AGENT-020] 清帳：冰箱卡點更新，舊 design_note 轉為歷史索引

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** scrum-master
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T19:03+08:00
**✅ 完成時間 (Closed):** 2026-08-18T05:31+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`docs/features/process_evolution/design_note.md` 是 **DN 機制出現之前**的舊檔，
§3 列了九個候選改進項當作待辦清單。它現在已經半數過期——

| 舊 design_note | 現況 |
|---|---|
| §3.1 Draft PR + CI 閘門 ⬅ 最優先 | 由 [DN-007](../../../design_notes/DN-007_ci_gate.md) 接手並畢業 |
| §3.3 審查與開發拆成不同 context | 由 `PEV-DEV-AGENT-015` 落地（取證義務），機制選項併入 DN-004 §5 |
| §3.4 審查清單三分法（precheck 腳本） | 由 `PEV-DEV-AGENT-018` 落地 |
| §3.5 工單瘦身：審查紀錄與 HITL 移出 | 由 `PEV-DEV-AGENT-016` 落地（`reviews/<TaskID>.md`） |
| §3.9 design_note 本身的落點 ⬅ 元問題 | 由 [DN-001](../../../design_notes/DN-001_design_note_mechanism.md) 接手並畢業 |

留著不標註的後果是**下一輪規劃會把已落地的項目當成還沒做**——這正是 DN-001 §7.3
記載的失效模式（DN-002 的依賴欄位懸空六份 DN 沒人發現）。

同時處理 BACKLOG 冰箱的卡點描述：「負向對照自動化」原本卡在「等 DN-007 定出檢查落點」，
而 DN-007 已畢業，這個卡點已經消失。落點的結論是**確定不在** precheck 第 1 層——
`precheck.py` 是 stdlib-only、只讀檔案、不執行任何測試，而負向對照的定義就是
「還原實作後重跑專案測試套件」，依 DN-007 §3.2 屬**第 2 層**（技術棧綁定，kit 只能留 hook）。
真正的卡點是**做法有三條路互斥、尚未收斂**，現在的卡點描述沒反映這件事。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - **前置**：`PEV-DEV-AGENT-018`、`019`——它們落地後這裡標註的去向才是既成事實
  - `docs/features/process_evolution/design_note.md`（§3.1～§3.9）
  - `docs/development/BACKLOG.md` 冰箱（本 repo 種子檔）
- **Outputs (輸出/預期變更)**：
  - `design_note.md` §3 各項加上落點標註
  - `docs/development/BACKLOG.md` 冰箱「負向對照自動化」卡點改寫
  - **不動** kit——本工單全部是本 repo 自己的文件

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`design_note.md` §3 的**每一項**都標明現況——已落地的標出工單 ID 或 DN 編號，
      未落地的標明卡在哪。九項一個都不漏。
- [x] AC-02：檔頭加一句說明本檔已轉為**歷史索引**、不再是待辦清單，並指向
      `docs/design_notes/` 作為現行機制。
- [x] AC-03：冰箱「負向對照自動化」的卡點改為「落點**確定不在** precheck 第 1 層
      （負向對照要跑專案測試套件，依 DN-007 §3.2 屬第 2 層），卡在三條做法互斥
      待收斂 → 待開 DN」，並列出那三條是什麼。
      ⚠️ 本條在開工前依 `team_protocol.md` §1.8 改寫過，原文的前提已被 `018`／`019` 推翻，
      詳見 §5。
- [x] AC-04：冰箱「precheck 腳本」該列已由 `PEV-DEV-AGENT-018` 移除，此處確認不重複出現。
- [x] AC-05：「展示層生成」**不碰**——依它自己在冰箱的註記排最後。
- [x] AC-06：`uv run pytest` 全綠；BACKLOG 重生後無 diff（冪等）。
- [x] AC-07（清帳時追加）：`KIT-DEV-AGENT-001` 結案——14 條 AC 全打勾、交付物實查全部
      進了主線，Status 卻卡在 `In Review` 兩天。`Closed` 取最後一次實質變更的 commit
      時間 `2026-08-16T15:05+08:00`，不是清帳當天。
- [x] AC-08（清帳時追加）：`018`／`019` 審查檔 §5 記下的落差開成工單——
      `PEV-DEV-AGENT-021`（commit 規範送達）、`PEV-DEV-AGENT-022`（precheck 與測試收斂）。
      不開單的兩項要寫明理由。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：
  - 無。
- **✍️ User 補充回覆 (User Input)**：
  -

## 5. 開工前的改單紀錄

工單當時是 `Pending`，依 `team_protocol.md` §1.8 的對照表，`Ready`／`Pending` 的工單
由 **Scrum Master 直接修正規格**（尚未開工，改單成本最低），且**要改寫導致缺陷的那條
敘述本身，不可只在後面追加新條**。本工單的 §1 與 AC-03 因此是被改寫的，不是被補充的。

**被推翻的前提**：原文寫「負向對照自動化的落點其實已經由 DN-007 §3.2 釐清
（屬第 1 層流程檢查、要落在 precheck）」。`018`／`019` 落地後這句話不成立：

- `precheck.py` 是 stdlib-only、只讀 repo 內的檔案，**不執行任何測試**。
- 負向對照／mutation testing 的定義就是「改壞實作或還原 commit，**重跑專案測試套件**」，
  而 DN-007 §3.2 明確把那件事歸為**第 2 層**：「跟技術棧綁定，kit 只能留一個 hook 讓專案填」。

所以落點**不是**已定，而是**確定不在 precheck 出貨的那一層**。這個更正比原說法有用：
它把「等 DN-007」這個已消失的卡點，換成一個真正的卡點（三條做法互斥）。

本工單自己的 Inputs 就寫了「前置：`018`、`019`——**它們落地後這裡標註的去向才是既成事實**」，
改單正是它預期的動作。

**追加 AC-07／AC-08 的理由**：清帳的定義是「讓帳面與現實一致」。開工後盤點發現，
帳面落後現實的載體不只 `design_note.md` 一個——還有卡在 `In Review` 的 `KIT-DEV-AGENT-001`
（AC-07），以及只記在審查檔、沒進 BACKLOG 的兩個落差（AC-08）。
三者是同一種失效模式的三個載體，分開處理只會清一半。
