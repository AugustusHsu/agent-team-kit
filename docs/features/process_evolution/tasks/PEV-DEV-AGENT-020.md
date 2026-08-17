# [Task ID: PEV-DEV-AGENT-020] 清帳：冰箱卡點更新，舊 design_note 轉為歷史索引

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** scrum-master
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-17T19:03+08:00
**✅ 完成時間 (Closed):** —
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

同時處理 BACKLOG 冰箱的卡點描述：「負向對照自動化」的落點其實已經由 DN-007 §3.2
釐清（屬第 1 層流程檢查、要落在 precheck），但**做法有三條路互斥、尚未收斂**，
現在的卡點描述沒反映這件事。

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

- [ ] AC-01：`design_note.md` §3 的**每一項**都標明現況——已落地的標出工單 ID 或 DN 編號，
      未落地的標明卡在哪。九項一個都不漏。
- [ ] AC-02：檔頭加一句說明本檔已轉為**歷史索引**、不再是待辦清單，並指向
      `docs/design_notes/` 作為現行機制。
- [ ] AC-03：冰箱「負向對照自動化」的卡點改為「落點已定（precheck 第 1 層），
      卡在三條做法互斥待收斂 → 待開 DN」，並列出那三條是什麼。
- [ ] AC-04：冰箱「precheck 腳本」該列已由 `PEV-DEV-AGENT-018` 移除，此處確認不重複出現。
- [ ] AC-05：「展示層生成」**不碰**——依它自己在冰箱的註記排最後。
- [ ] AC-06：`uv run pytest` 全綠；BACKLOG 重生後無 diff（冪等）。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：
  - 無。
- **✍️ User 補充回覆 (User Input)**：
  -
