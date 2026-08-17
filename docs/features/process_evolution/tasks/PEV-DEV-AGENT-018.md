# [Task ID: PEV-DEV-AGENT-018] precheck.py：出貨第 1 層流程檢查，機械性失敗不再靠人眼抓

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-17T19:03+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

[DN-007](../../../design_notes/DN-007_ci_gate.md) §3.2 的核心主張是**把檢查分兩層**：
第 1 層「流程有沒有被遵守」跟技術棧無關、輸入全在 repo 內，**kit 可以替所有人定義**；
第 2 層「專案自己的測試」只能留 hook。§4.1 #1 已裁定出貨形式為 **C（adapter）**——
檢查邏輯放 repo 內一支腳本，CI 只負責呼叫它。本工單做那支腳本。

它消滅的是**第 1 類人工介入**：機械性失敗在人看到之前就已經紅了，不必等審查者用眼睛抓。
四項檢查每一項都對應到本 repo 真實踩過的坑：

| 檢查 | 踩過的實例 |
|---|---|
| BACKLOG 過期 | CLAUDE.md 已載明——`scan_backlog.py` 預設只印到 stdout，不加 `--format backlog --output` 看起來成功、BACKLOG 卻沒更新 |
| 工單 Status 值合法 | 打錯字的 Status 會讓工單從所有視圖裡靜默消失，`scan_backlog.py` 不會報錯 |
| `Closed` 不早於 `Created` | `PEV-DEV-AGENT-012`～`015` 的時間戳早了一天，害 `016` 結案後被擠出「近期結案」。使用者裁定不回頭修（team_protocol §1.11），**改用檢查防未來** |
| 文件死連結 | `PEV-DEV-AGENT-016` 開發途中就被死連結測試擋下過一次 |

**🔴 「已廢除的流程規則殘留」明確不出貨。** 它跟上面四項不同類：那四項檢查的是
**使用者自己寫的工單與文件**，這一項檢查的是 **kit 出貨內容有沒有被改壞**。
使用者專案不編輯 `.agent/`，帶著一張空規則表沒有意義。它留在
`tests/test_kit_integrity.py` 當 kit 的開發期守衛。**這是取捨不是遺漏**，寫在這裡
是為了讓下一輪的人不要以為漏做了。

本工單同時吃掉 BACKLOG 冰箱的「precheck 腳本」那一列——落點已定、AC 當場寫得出來，
依 [DN-001](../../../design_notes/DN-001_design_note_mechanism.md) §3.2 直接開工單、不另開 DN。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - [DN-007](../../../design_notes/DN-007_ci_gate.md) §3.2（兩層分法）、§4.1（六項裁定）、§5（落點與執行順序）
  - `kit/.agent/scripts/scan_backlog.py`——`find_project_root()`（:69-83）與
    `parse_task_file()`（:86-）是要沿用的既有實作，**不要重寫一份 metadata 解析**
  - **Status 合法值的權威是 `scan_backlog.py` 的 `STATUS_ICONS`**（:47-54）——`documentation_conventions.md` 並未定義 Status 值，別去那裡找。
    時間格式的範本在 `kit/.agent/resources/task_template.md`
  - `tests/test_kit_integrity.py`——現有死連結檢查的判定邏輯，可參照但不搬走
- **Outputs (輸出/預期變更)**：
  - **新增 `kit/.agent/scripts/precheck.py`**——只用標準函式庫
  - 新增 `tests/test_precheck.py`
  - `docs/development/BACKLOG.md` 冰箱移除「precheck 腳本」該列（本 repo 種子檔）
  - **不動** `.github/`（那是 `PEV-DEV-AGENT-019` 的範圍，DN-007 §5 訂了執行順序：
    先有腳本再接 CI）

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：`kit/.agent/scripts/precheck.py` 存在，**只 import 標準函式庫**。
      驗證方式為現有 `stdlib-only` CI job 的同一條線——用系統 python（無 uv、無第三方套件）
      在 `install.sh` 裝出來的專案裡執行成功。
- [ ] AC-02：四項檢查全部實作——① BACKLOG 過期（重跑 `scan_backlog.py` 的產出與現檔比對）、
      ② 工單 Status 值合法、③ `Created`／`Closed` 是 ISO 8601 且 `Closed` 不早於 `Created`、
      ④ 文件相對連結指向的檔案存在。
- [ ] AC-03：全綠時 exit code 0；**任一項紅燈時 exit code 非 0**，且輸出指明是哪個檔案、
      哪一項檢查、期望什麼。只印「失敗」而不說哪裡失敗不算通過。
- [ ] AC-03a：**時間戳精度不同時降到日期粒度比較。** `PEV-DEV-AGENT-001` 的
      `Closed` 是 `2026-08-16`（只有日期）、`Created` 是 `2026-08-16T14:06+08:00`；
      把日期當成午夜 00:00 去比會判成「Closed 早於 Created」，那是**假紅燈**。
      純日期本身就是合法 ISO 8601，精度較粗時推不出先後違規。
- [ ] AC-03b：**死連結檢查必須先剝掉 fenced code block 與行內 code span。**
      `PEV-DEV-AGENT-008.md:89` 的 `[DN-007](DN-007_ci_gate.md)` 包在反引號裡，
      是拿來說明「DN 檔的依賴欄位長什麼樣」的引用，不是真連結。
      （同一個盲點也是 `PEV-DEV-AGENT-016` 當初被迫把範例路徑寫成非連結語法的原因。）
- [ ] AC-04：檢查之間**互不短路**——第一項紅燈時後三項仍然要跑完並一起回報。
      跑一次只修一個問題會讓修復迴圈變成四趟。
- [ ] AC-05：`tests/test_precheck.py` **每一項檢查都有負向對照**：造出過期的 BACKLOG、
      非法 Status、`Closed` 早於 `Created`、指向不存在檔案的連結，各自確認腳本回非零；
      再確認乾淨專案回 0。**另加兩支防假紅燈的迴歸**：日期粒度混用（AC-03a 的形狀）
      要綠、行內程式碼裡的連結（AC-03b 的形狀）要綠。只證明「壞的會紅」不夠，
      還要證明「對的不會被誤判成壞的」。
- [ ] AC-06：在本 repo 自己跑 `python3 .agent/scripts/precheck.py` 為綠。
      ⚠️ 若因 `PEV-DEV-AGENT-012`～`015` 的時間戳而紅，**不得修改那些工單**（§1.11），
      應改為在工單描述裡記錄該紅燈的成因與處置，並在此 AC 註明實際結果。
- [ ] AC-07：`uv run pytest` 全綠（基準 111），`./install.sh . --upgrade` 後
      `--dry-run` 顯示「待合併 0」。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：
  - 無。四項清單、stdlib-only、落點皆由 DN-007 §4.1 #2 裁定。
- **✍️ User 補充回覆 (User Input)**：
  - （2026-08-17）012–015 的 Closed 時間戳處置選「不修，改用檢查防未來」→ 成為本工單檢查 ③。
