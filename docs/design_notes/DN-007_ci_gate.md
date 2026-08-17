# [DN-007] CI 閘門：kit 要不要出貨自動檢查，以及檢查什麼

**🚥 狀態 (Status):** 🎓 Graduated
**📅 建立 (Created):** 2026-08-17
**🔗 依賴 (Depends on):** DN-001（本檔的格式）；DN-003（已畢業，`git_workflow.md` 是本檔要補的那份規範）
**📌 來源 (Origin):** 使用者指令（2026-08-17，本輪範圍裁定為「DN-001 ＋ 新開 CI 閘門 DN」）；
另一個來源是 DN-002 的依賴欄位——它從 2026-08-16 起就指向「CI 閘門（尚未開 DN）」
**🎓 畢業去向 (Landing):** D（改流程／基礎建設）→ `kit/.agent/scripts/precheck.py`、`kit/.github/workflows/`、`kit/docs/standards/git_workflow.md` §8，見 §5

⚠️ **DN 不得寫實作步驟。** 本檔只比方案、列待決，不寫「第一步做什麼」。

## 1. 問題陳述

**kit 出貨的規範要求 CI 當閘門，但 kit 一份 CI 都沒出貨。**

- `git_workflow.md` §6.1 裁定 4：「**CI 紅燈硬擋合併。** 不擋的話，PR 只是個好看的
  diff 檢視器，不是閘門。」
- §8.1 能力對照表把「自動檢查」列為 **kit 要求的能力**（GitHub Actions／GitLab CI／
  無遠端時「合併前手動跑測試」）。
- §8.2 GitHub 設定清單：「合併前必須通過 CI ✅ 開」。
- 但 **`kit/.github/` 不存在**。裝了 kit 的專案讀到這三條時，手上沒有任何 CI，
  也沒有任何樣板可抄。

這跟本輪處理的另一個落差同型：**規範指向一個 kit 不提供的東西。**
（另一個是 scrum-master 被教「AC 難產先開 DN」，但 `kit/docs/design_notes/` 不存在。）

附帶的證據：DN-002 的依賴欄位寫「CI 閘門（尚未開 DN，見 Icebox）」，
從 DN-002 建立到 DN-007 出現為止懸空了六份 DN 的時間都沒人發現——
見 [DN-001](DN-001_design_note_mechanism.md) §7.3。

## 2. 既有事實（現況，不是設計）

本 repo 自己有 `.github/workflows/ci.yml`，44 行，兩個 job：

| Job | 內容 | 它實際在防什麼 |
|---|---|---|
| `test` | matrix 三版 Python（3.10／3.12／3.13）跑 `uv run pytest` | 套件本身的迴歸 |
| `stdlib-only` | **不裝 uv**，`./install.sh /tmp/demo` 後直接用系統 python 跑 `scan_backlog.py`、`migrate_dates.py` | 出貨腳本偷用第三方套件——裝了 kit 的專案不一定有 uv |

觸發條件：`push` 到 `main` ＋ 所有 `pull_request`。

第二個 job 值得注意：**它檢查的不是「程式對不對」，而是「出貨物在使用者環境跑不跑得動」。**
這類檢查跟專案技術棧無關，是 kit 可以替所有人定義的那一層（見 §3.2）。

## 3. 選項與取捨

### 3.1 出貨形式（三選一）

| | 做法 | 優點 | 代價 |
|---|---|---|---|
| **A** | 直接出貨 `kit/.github/workflows/ci.yml` | 裝完就有，零設定 | 綁死 GitHub；且 `install.sh` 是原封不動複製，樣板裡的 `uv run pytest` 對非 Python 專案是**死的** |
| **B** | 只出貨檢查清單與廠商中立規範，不出 YAML | 不綁平台 | **等於現狀**——§8.2 本來就是清單，落差原封不動 |
| **C** | 出貨 adapter：repo 內一支 kit 自己的檢查腳本 ＋ 一份薄的 workflow 只負責呼叫它 | 「要跑什麼」定義在 repo 內，換平台只換那份薄 YAML；本機也能跑同一支 | 多一層間接；薄 YAML 仍要一個平台版本 |

C 呼應 §8.1 已經確立的形狀：能力對照表把「平台」與「能力」分開，
`[平台相關]` 標記本來就是為了讓執行方式可替換。

> ✅ **裁定（2026-08-17，使用者）：選 C。**

### 3.2 要跑哪些檢查——分兩層

**這一層分法是本 DN 的核心主張**：
kit 出貨的 CI 應該檢查**流程有沒有被遵守**，而不是替使用者跑他的單元測試。

| 層 | 內容 | kit 能不能定義 |
|---|---|---|
| **第 1 層：流程檢查** | BACKLOG 是否過期（重跑 `scan_backlog.py` 後有 diff ＝ 過期）、工單 Status 值合法、`Closed` 是 ISO 8601、文件死連結、已廢除的流程規則殘留 | ✅ **可以**——跟技術棧無關，且輸入全在 repo 內 |
| **第 2 層：專案測試** | 跑專案自己的測試指令 | ❌ 只能留一個 hook 讓專案填 |

第 1 層正是舊 `design_note.md` §3.1 標「⬅ 最優先」的理由：
它消滅**第 1 類人工介入**——機械性失敗在人看到之前就已經紅了，不必等審查者用眼睛抓。

「BACKLOG 是否過期」這條特別值得做：它是純函數檢查（重跑比 diff），
而且 CLAUDE.md 已經記載這個坑——`scan_backlog.py` 預設只印到 stdout，
不加 `--format backlog --output` 看起來成功、BACKLOG 卻沒更新。這是人反覆踩的，機器一次就抓到。

> ✅ **裁定（2026-08-17）：第 1 層出貨四項檢查**——BACKLOG 是否過期、工單 Status
> 值合法、`Created`／`Closed` 是 ISO 8601 且 `Closed` 不早於 `Created`、文件死連結。
>
> **「已廢除的流程規則殘留」不出貨。** 它跟其他四項不同類：其他四項檢查的是
> **使用者自己寫的工單與文件**，這一項檢查的是 **kit 出貨內容有沒有被改壞**。
> 使用者專案不編輯 `.agent/`，帶著一張空規則表沒有意義，它留在
> `tests/test_kit_integrity.py` 當 kit 的開發期守衛。
>
> 「`Closed` 不早於 `Created`」這項的來源是實際事故：`PEV-DEV-AGENT-012`～`015`
> 的 Closed 時間戳比真實時鐘早了一天，使 `016` 結案後在 BACKLOG 裡被擠出「近期結案」。
> 使用者裁定**不回頭修**（依 team_protocol §1.11「已結案工單不改它」），改用檢查防未來。

### 3.3 CI 紅燈與工單狀態的關係

`git_workflow.md` §6.1 裁定 4 只說「硬擋合併」，**沒說要不要動工單 Status**。
兩種可能：紅燈只擋合併、狀態不動（審查者仍是 `In Review`）；
或紅燈視同 CHANGES REQUESTED，Status 退回 `In Progress`。
後者的風險是把機械性失敗（跑一次 CI 就好）跟設計性退回混為一談。

> ✅ **裁定（2026-08-17）：不改 Status，紅燈只擋合併。**
> `PEV-DEV-AGENT-016` 剛把退回程序訂得更重（要寫審查檔、記退回日期與缺陷成因），
> 把它套在「忘了重生 BACKLOG」上是儀式化浪費——那類失敗重跑一次腳本就綠了，
> 沒有任何設計資訊值得留存。審查者維持 `In Review`，等 CI 轉綠再合併。

## 4. 待決事項

### 4.1 已裁定（2026-08-17）

六項全數結清，無延後項。⭐ 三項由使用者本人裁定，其餘三項由 AI 提案、使用者於畢業時一併簽核。

| # | 待決 | 裁定 | 理由 |
|---|---|---|---|
| 1 | ⭐ 出貨形式 A／B／C | **C（adapter）** | 見 §3.1；B 等於現狀，A 綁死 GitHub 且樣板對非 Python 專案是死的 |
| 2 | ⭐ 第 1 層清單／落點／stdlib | **`kit/.agent/scripts/precheck.py`，只用標準函式庫，出貨四項** | 見 §3.2；與現有三支出貨腳本一致，且 `stdlib-only` job 立的線就是「沒有 uv 也要跑得動」 |
| 3 | 能不能在本機跑 | **能——腳本本身就是本機可跑的 CLI；但不出貨 pre-commit hook** | hook 要額外安裝步驟，又能被 `--no-verify` 靜默繞過。裝了卻被繞過的閘門比沒有更糟，因為它讓人以為已經檢查過了 |
| 4 | ⭐ 「有遠端但不推送」第三種模式 | **改 CI 觸發條件涵蓋開發分支的 push，不靠 PR** | 使用者裁定。本 repo 就是這個模式，`git_workflow.md` §8.3 只降級了「無遠端」，這個中間態要一併補進去 |
| 5 | CI 紅燈是否改工單 Status | **不改，只擋合併** | 見 §3.3 |
| 6 | kit 自己的 `ci.yml` 與出貨樣板要不要收斂 | **不收斂成同一份，但兩份呼叫同一支 `precheck.py`** | 本 repo 有 kit 專屬需求（三版 Python matrix、`stdlib-only` 出貨物驗證），使用者專案不需要。**共用的是檢查邏輯，不是 YAML**——這正是選 C 的意義 |

### 4.2 落地時必須連帶改寫（不是待決，是已知工作量）

- `kit/docs/standards/git_workflow.md` §8.1 能力對照表——補「檢查內容」欄
- 同檔 §8.3——現在只寫了「無遠端」的降級，要補「有遠端但不推送」
- 本 repo `.github/workflows/ci.yml`——`on.push.branches` 加開發分支；
  `stdlib-only` job 加跑 `precheck.py`

## 5. 畢業去向

**畢業條件檢核（依 [DN-001](DN-001_design_note_mechanism.md) §3.4）：**

1. ✅ 所有待決已答，無延後項——見 §4.1
2. ✅ **寫得出可驗收的 AC**——§3.2 的四項檢查每一項都能寫成「造出違規輸入 → 腳本回非零」
   的負向對照，落點與退出碼語意都已具體
3. ✅ **使用者本人簽核畢業**——2026-08-17 裁定 §3.1（選 C）、§4.1 #4（改觸發條件）、
   §3.2 的時間戳處置（不回頭修，改用檢查防未來），並確認本 DN 畢業

**軟上限診斷（DN-001 §5）**：本 DN 約 155 行，**未觸發** 250 行軟上限，不需要拆分。

**類型**：**D（改流程／基礎建設）**——依 DN-001 §3.5，第 1 層權威在 `docs/standards/`，不需 PRD

**落點**：

- **`kit/.agent/scripts/precheck.py`（新建，本 DN 的主要產出）**——§3.2 的四項第 1 層檢查
- **`kit/.github/workflows/`（新建）**——薄 YAML，只負責呼叫 `precheck.py`，
  不含任何專案測試指令（第 2 層留 hook 給專案自己填）
- `kit/docs/standards/git_workflow.md` §8——見 §4.2
- 本 repo `.github/workflows/ci.yml`——見 §4.2

**執行順序（不可調換）**：先有 `precheck.py`，再接 CI。
反過來的話薄 YAML 會指向一支不存在的腳本，第一次跑就紅，而且是紅在「檔案不存在」
這種跟閘門本身無關的理由上。

**工單**（2026-08-17 開立，模組前綴 `PEV`）：

| 工單 | 內容 |
|---|---|
| [PEV-DEV-AGENT-018](../features/process_evolution/tasks/PEV-DEV-AGENT-018.md) | `precheck.py` 與四項第 1 層檢查（含冰箱「precheck 腳本」該列） |
| [PEV-DEV-AGENT-019](../features/process_evolution/tasks/PEV-DEV-AGENT-019.md) | CI adapter：出貨薄 YAML、`git_workflow.md` §8、本 repo 觸發條件 |
