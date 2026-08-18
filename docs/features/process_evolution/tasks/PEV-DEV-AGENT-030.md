# [Task ID: PEV-DEV-AGENT-030] 修正 DN 取號指令：改從檔名取號

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** scrum-master
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-18T21:40+08:00
**✅ 完成時間 (Closed):** 2026-08-18T23:35+08:00
**🔀 審查載體編號 (PR/MR):** `reviews/PEV-DEV-AGENT-030.md`（無遠端 PR，見 git_workflow.md §8.3b）

## 1. 任務描述 (Description)

`docs/design_notes/README.md:24` 與出貨的 `kit/docs/design_notes/README.md:24`
教人用這條指令取下一個 DN 號：

```bash
grep -rhoE "DN-[0-9]+" docs --include=*.md | sort -t- -k2 -n | tail -1
```

**它會回錯答案。** 2026-08-18 實測回 `DN-099`，而當時真正的最大號是 `DN-007`——
因為它掃的是**檔案內容**，撈到了 `docs/features/process_evolution/tasks/PEV-DEV-AGENT-008.md:100`
內文提到的測試 fixture 名稱 `DN-099`。照著做的人會開出 `DN-100`。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

⚠️ **DN-004 §6 建議的做法（把掃描範圍縮到 `docs/design_notes/`）經實測不足**，
本工單建立時已驗證：DN-004 自己的 §6 表格就寫著 `DN-099`，
縮範圍後指令仍然回 `DN-099`。**只要指令掃的是內容，就會被內容裡的號碼污染。**

**正確做法：從檔名取號**，因為 DN 的編號本來就編碼在檔名裡
（`DN-004_skill_system_realignment.md`），而檔名不會被行文提及的號碼污染。
候選寫法（實測回 `008`，即當前真正的最大號）：

```bash
ls docs/design_notes/DN-*.md 2>/dev/null | sed 's/.*DN-\([0-9]\+\)_.*/\1/' | sort -n | tail -1
```

⚠️ **要處理「一份 DN 都還沒有」的情況**：kit 出貨的 `kit/docs/design_notes/`
只有 `README.md` 與 `_TEMPLATE.md`，新安裝的專案跑這條指令會是空輸出。
README 要寫明此時從 `DN-001` 開始。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`docs/design_notes/README.md` 與 `kit/docs/design_notes/README.md`
      兩份的指令都改掉（出貨內容與本 repo 的安裝實例是同一份文字，兩邊都要對）。
- [x] AC-02：新指令在本 repo 實測回**當前真正的最大號**，輸出留進審查紀錄。
- [x] AC-03：**負向對照**——在某份 DN 內文寫一行 `DN-099`，重跑新指令，
      確認**不受影響**（舊指令在同一情境下會回 `DN-099`）。兩次輸出都留進審查紀錄。
- [x] AC-04：README 寫明空輸出時從 `DN-001` 開始。
- [x] AC-05：**不回頭改 `PEV-DEV-AGENT-008` 的內文**——依 `team_protocol.md` §1.11
      已結案工單不改它，那份 fixture 名稱留著。它現在還是這條指令的天然測試案例。
- [x] AC-06：`uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`——
      兩份 README 若不同步會被抓到）；`python3 .agent/scripts/precheck.py` 6 項全綠。
- [x] AC-07：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- 本項為 DN-004 盤點時附帶查到，隨 DN-004 於 2026-08-18 畢業一併開出。
- DN-004 §6 對本工單的做法建議已被實測推翻，正確做法記在本工單 §2；
  **DN-004 已畢業凍結，不回頭改**。

## 5. 範圍外 (Out of Scope)

- **不改任何既有 DN 的編號。**
- **不寫成自動檢查**——取號是人在開檔前跑一次的動作，不是 CI 能守的東西。
