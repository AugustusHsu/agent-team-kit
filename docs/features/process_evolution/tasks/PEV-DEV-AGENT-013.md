# [Task ID: PEV-DEV-AGENT-013] 立規：納入版控的生成檔必須是輸入的純函數

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** backend-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T20:50+08:00
**✅ 完成時間 (Closed):** 2026-08-17T21:30+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

規則本身在 [DN-001](../../../design_notes/DN-001_design_note_mechanism.md) §5 已經定稿，
是那份 DN 的「順帶產出」，當場寫得出 AC，依 §3.2 不需要另開 DN：

> **納入版控的生成檔，內容必須是輸入的純函數**——不得含時間相依值。
> 一旦嵌入「停滯 N 天」，輸入沒變輸出卻天天變，同一份 repo 在不同日期跑會產生不同檔案，
> 並連帶弄壞「重跑看有沒有 diff ＝ 判斷 BACKLOG 是否過期」這個現行檢查。

**問題是規則寫下來的當下，我們自己就在違反它。** `scan_backlog.py` 的 `--format backlog`
有兩處時間相依：

| 位置 | 內容 | 後果 |
|---|---|---|
| 標頭 | `> **最後更新時間**：{今天}` | 輸入完全沒變，換一天重跑就產生 diff |
| 「近期結案」區塊 | `now - timedelta(days=recent_days)` 切出時間窗 | 已結案工單會**自己從報表裡消失**，不需要任何人改工單 |

第二點的代價已經浮現在測試基礎設施上：fixture 工單的結案日期不能寫死，得由
`conftest.py` 把 `{{CLOSED_RECENT}}`／`{{CLOSED_OLD}}` 換算成「相對現在」，
而 `test_recent_days_可調整分界` 得傳 `--recent-days 500` 才拉得回 fixture 裡的舊工單——
**那個 500 是定時炸彈**，等 repo 的「現在」離 fixture 日期超過 500 天，測試會自己壞掉。

停滯偵測本身不在本工單（DN-001 §5 已移交 [DN-002](../../../design_notes/DN-002_discord_notification_layer.md)）；
本工單只負責把**時間相依的視圖趕到 stdout**，並給它一個正式落點 `--stale`。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**（a）立規**——`kit/docs/standards/documentation_conventions.md` 新增一節「生成檔」，
定義：哪些算生成檔、純函數要求、時間相依視圖該走哪裡、以及「重跑有無 diff」這個檢查為何依賴它。

**（b）`--format backlog` 去時間相依**

| | 修正前 | 修正後 |
|---|---|---|
| 標頭 | `最後更新時間：{今天}` | **移除**（要知道何時重生看 git log） |
| 近期結案 | 「最近 `--recent-days` 天內結案」 | 「最近 `--recent-limit` 張已結案工單」，依 Closed 由新到舊 |
| `--recent-days` | 存在，預設 7 | **移除**（時間窗語意已消失） |

**（c）新增 `--stale DAYS`**——列出非終態（`Done`／`Canceled` 以外）且 `Created` 早於
`DAYS` 天前的工單，**只印 stdout**。與 `--output` 併用時以非零狀態碼結束並說明原因：
規則的執行面，不是靠人記得。

## 3. 驗收標準 (Acceptance Criteria)

- [x] `documentation_conventions.md` 有「生成檔」一節，寫明純函數要求與時間相依視圖的去處
- [x] `--format backlog` 的輸出不含「最後更新時間」；`backlog_template.md` 與 kit 出貨的
      `docs/development/BACKLOG.md` 骨架同步移除該行
- [x] 「近期結案」改為取最近 N 張（依 Closed 排序），`--recent-days` 移除
- [x] 新增 `--stale DAYS`，只輸出 stdout；`--stale` 併 `--output` 以非零狀態碼結束
- [x] 新增測試：結案日期遠在過去的 fixture 工單，不加任何旗標也會出現在「近期結案」
      （證明時間窗確實消失）
- [x] 新增測試：`--stale` 併 `--output` 失敗且不產生檔案；`--stale` 能列出停滯工單
- [x] `conftest.py` 不再需要為了時間窗改寫 fixture 日期，或其註解已更新為現況
- [x] 全套測試綠燈且數量增加；`./install.sh . --upgrade` 待合併 0
- [x] 本 repo 的 `BACKLOG.md` 重生後，連續兩次重生無 diff

## 4. 人為補充與確認 (Human-in-the-loop)

- 2026-08-17：使用者要求先做不依賴 CI 的項目，本工單屬其一。
- 規則出處 DN-001 §5，非本工單新創；本工單負責落地與自我遵守。

## 📝 Code Review 備註

**審查人**：code-reviewer（2026-08-17）

### 客觀指標

| 指標 | 修正前 | 修正後 |
|---|---|---|
| 全套測試 | 105 passed | **110 passed** |
| `BACKLOG.md` 連續兩次重生 | 不同日期必有 diff | **無 diff**（實測 `diff -q` 相同） |
| `--format backlog` 內的 `datetime.now()` 依賴 | 2 處（標頭、時間窗） | **0 處** |
| `./install.sh . --upgrade` 待合併 | — | **0**（更新 3） |
| `conftest.py` 為了時間窗改寫 fixture 的機制 | 20 行 | **移除** |

### 三處改動與各自的理由

1. **移除標頭的「最後更新時間」**——它是純粹的時間戳，沒有任何輸入對應。
   要知道何時重生看 `git log -1 docs/development/BACKLOG.md`，git 記得比檔案裡的字串準。
2. **「近期結案」從時間窗改成取最近 N 張**——時間窗的真正代價不是 diff，是
   **已結案工單會自己從報表裡消失**。改成依 Closed 排序取前 N 張後，
   進出報表只由工單內容與 `--recent-limit` 決定。
3. **`--recent-days` 整條移除**——時間窗語意消失後這個旗標無法解釋。
   留著會讓人以為還能調分界，因此下架並補測試釘住「傳了會失敗」。

### 順帶的簡化（規則帶來的直接收益）

原本 `conftest.py` 得把 fixture 工單的 `{{CLOSED_RECENT}}`／`{{CLOSED_OLD}}` 換算成
「相對現在」，且 `test_recent_days_可調整分界` 要傳 `--recent-days 500` 才拉得回舊工單。
**那個 500 是定時炸彈**：等 repo 的「現在」離 fixture 日期超過 500 天，測試會自己壞掉。
時間窗移除後，fixture 日期直接寫死，佔位符機制整段刪除——
規則不只是規範，它讓測試基礎設施少了一層。

### `--stale` 的守衛是執行面而非文件面

`--stale` 併 `--output` 走 `parser.error()` 以非零狀態碼結束，錯誤訊息直接指向
`documentation_conventions.md` §5。測試 `test_stale_不得寫入檔案` 同時斷言
**檔案沒有被建立**，而不只是回傳碼——避免「先寫檔再報錯」這種假守衛。

### 未處理

- `--format json` 的輸出仍含 `classified` 分類結果，本身不含時間相依值，未動。
- 停滯的**通知**（誰該被提醒、多久一次）不在本工單，DN-001 §5 已移交 DN-002。

**結論**：通過。
