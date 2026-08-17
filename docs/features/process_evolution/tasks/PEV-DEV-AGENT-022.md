# [Task ID: PEV-DEV-AGENT-022] precheck 與 kit 自身測試收斂：同一個盲點兩份實作，再補兩項漏掉的檢查

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_backend
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-18T05:26+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`PEV-DEV-AGENT-018`／`019` 的審查檔 §5 記了幾個落差，但**審查檔不會有人主動回頭讀**——
不開單就等於沒發現。本工單處理其中兩件機械可判定的：

**① 死連結檢查有兩份實作，其中一份有盲點。**
`precheck.py` 的 `check_dead_links()` 會先 `strip_code()` 剝掉 code fence 與行內 code
再找連結；`tests/test_kit_integrity.py::test_kit_內沒有死連結` 卻是逐行
`LINK.finditer(line)`，**完全沒剝**。同一件事兩份實作、其中一份落後——
這正是 `design_note.md` §3.8 說的「任何需要手動維護的第二份表述，必然漂移」。
`019` 已經留下 `_載入_precheck(kit_root)` helper，收斂的工具已經在手上。

**② precheck 看不到工單狀態漂移。**
`KIT-DEV-AGENT-001` 的 14 條 AC 全部打勾、交付物全部進主線，Status 卻在 `In Review`
躺了兩天沒人發現，直到 `PEV-DEV-AGENT-020` 人工清帳才處理。現行四項檢查沒有一項看得到它。
同類的還有「Status 是 `Done` 但 `Closed` 留空」——`scan_backlog.py` 會照樣把它列進結案區，
完成時間欄空白。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - **前置**：`PEV-DEV-AGENT-020`——KIT-001 必須先結案，否則新檢查一上線就紅燈
  - `kit/.agent/scripts/precheck.py`（`strip_code()`、`CHECKS`、`iter_tasks()`）
  - `tests/test_kit_integrity.py`（`test_kit_內沒有死連結`、`_載入_precheck()` helper）
  - `kit/docs/standards/git_workflow.md` §8.1 能力對照表的「檢查內容」欄
- **Outputs (輸出/預期變更)**：
  - `kit/.agent/scripts/precheck.py`：新增兩項檢查，接進 `CHECKS`
  - `tests/test_kit_integrity.py`：死連結測試改用 `precheck.strip_code`
  - `kit/docs/standards/git_workflow.md`：§8.1「檢查內容」欄同步（**不同步會讓測試轉紅**）
  - 安裝實例同步：合併後跑 `./install.sh . --upgrade`

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：`test_kit_內沒有死連結` 改用 `precheck.strip_code()`（經既有的
      `_載入_precheck(kit_root)` helper 取得），**不另寫一份剝除邏輯**。
- [ ] AC-02：兩邊的 placeholder／略過規則（`LINK_PLACEHOLDERS`、`http(s)`、`mailto`）
      對齊；若有差異，在測試或腳本裡註明差異存在的理由。
- [ ] AC-03：precheck 新增檢查「Status 為 `Done` 但 `Closed` 留空」。
- [ ] AC-04：precheck 新增檢查「AC 全數打勾但 Status 不是 `Done` 也不是 `Canceled`」。
      `Canceled` 必須排除——取消的工單允許帶著打勾的 AC。
- [ ] AC-05：兩項新檢查沿用 `iter_tasks()`，確認 `_TEMPLATE/_EXAMPLE-DEV-BE-001`
      不會誤觸（**要實測，不是推論**）。
- [ ] AC-06：`git_workflow.md` §8.1 的「檢查內容」欄同步成六項，
      `test_能力對照表的檢查內容與_precheck_實際項目一致` 保持綠燈。
- [ ] AC-07：**負向對照，兩個方向都要做**——(a) 造一張假工單觸發每一項新檢查，
      確認 precheck 轉紅；(b) 把新檢查的判斷式改反，確認現有工單集合會轉紅，
      證明它不是恆綠。兩者都要記進審查檔。
- [ ] AC-08：`uv run pytest` 全綠；`./install.sh . --upgrade --dry-run` 的
      「待合併」數與實際改動的 kit 檔案數相符。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：
  - 無。
- **✍️ User 補充回覆 (User Input)**：
  -

## 5. 範圍外 (Out of Scope)

- **不做**冰箱區的偵測。`extract_existing_icebox()` 原樣保留手寫內容，
  沒有真值來源可比對——這是結構必然，不是缺陷（見 `reviews/PEV-DEV-AGENT-019.md` §5）。
- **不做**負向對照自動化本身（第 2 層，待開 DN，見 BACKLOG 冰箱）。
