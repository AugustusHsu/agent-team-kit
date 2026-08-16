# 開發團隊協作守則 (Team Protocol)

本文件定義了所有開發階段 Agent（Scrum Master、Frontend Developer、Backend Developer、DevOps Engineer、Code Reviewer）之間的協作規約。每位 Agent 在執行任務前，都應先閱讀本守則，以確保流程銜接無縫。

---

## 1. 工單生命週期 (Task Lifecycle)

每張 Task Ticket 在系統中會經歷以下五種狀態。只有符合轉換條件的角色才能推進狀態：

```
Pending → Ready → In Progress → In Review → Done
```

| 狀態 | 含義 | 誰負責推進到下一狀態 |
|---|---|---|
| **Pending** | 工單被**未完成的前置工單（硬依賴）**擋住，尚不可開工。 | 前置工單全數 `Done`/`In Review`、依賴解除後，由 Scrum Master 或執行者標記為 Ready。 |
| **Ready** | 工單**無未完成的前置依賴**，可交由 Developer 開始執行。工單內「❓ 需要確認的事項」（即使附建議值）**不阻擋 Ready**，改於**執行前**強制詢問（見 §1.7）。 | Developer (Frontend/Backend/DevOps) 領取後標記為 In Progress。 |
| **In Progress** | Developer 正在開發中。 | Developer 完成開發並提交交付回報後，標記為 In Review。 |
| **In Review** | Code Reviewer 正在審查程式碼。 | Code Reviewer 產出審查報告後，決定結果；APPROVED 後由 Developer 收尾合併。 |
| **Done** | 變更**已合併進主線**，工單正式完結。`[ ✅ APPROVED ]` 只是**放行訊號**，不等於 `Done`——合併還可能失敗（衝突、CI 紅燈）。 | — |

### 1.1 退回機制 (Rejection Flow)
- 若 Code Reviewer 標記 `[ ❌ CHANGES REQUESTED ]`，工單狀態**退回至 `In Progress`**。
- Developer 根據審查報告中的「重大瑕疵清單」進行修正後，再次提交並將狀態推進回 `In Review`。
- 此循環可重複直到 Reviewer 放行。
- **新發現的缺陷若成因落在尚未結案的工單範圍內，一律優先退回該工單而非新開工單**，退回時必須同步修正錯誤的 AC／規格、取消失效的勾選並補上新的待辦項目——詳見 §1.8。

### 1.2 矛盾暫停 (Contradiction Halt)
- 若 Developer 在開發過程中偵測到工單要求與系統現狀存在**矛盾**，工單狀態保持 `In Progress`，但 Developer 必須**立即暫停開發**並向使用者報告。
- 使用者裁定後，Developer 可繼續或 Scrum Master 可修改工單內容。

### 1.3 Epic 關閉條件 (Epic Closure)
- Epic (`DOC-EPIC-*`) 工單的關閉條件為：其所有子工單皆達到 `Done` 或 `Canceled` 狀態。
- 當最後一張子工單**合併完成**（即該子工單的 Status 已成為 `Done`）後，審查者或 Scrum Master 應同步將 Epic 的 Status 推進至 `Done`，並勾選「所有 N 張子工單皆完成並通過 Code Review」AC。
- 若部分子工單為 `Canceled`，N 的計算應排除已取消的工單。

### 1.4 母子工單狀態連動 (Parent-Child Status Linkage)
- 當母工單被 Scrum Master 拆分為子工單後，母工單的 Status 必須**立即**推進至 `In Progress`（代表其工作已透過子工單展開）。
- 母工單的 Status **禁止**在所有子工單完成前被推進至 `In Review` 或 `Done`。唯有當所有子工單的 Status 皆為 `Done` 或 `Canceled`，且母工單的驗收標準已全數勾選時，母工單才可結束 `In Progress`。
- 此規則適用於所有具備 Parent-Child 關係的工單（不僅限於 Epic）。

### 1.5 狀態更新操作方式 (How to Update Status)
每次推進或退回狀態時，負責的角色**必須**直接修改對應工單 `.md` 檔案中的 `**🚥 任務狀態 (Status):**` 欄位。操作時機如下：

| 動作觸發時機 | 執行者 | 將 Status 改為 |
|---|---|---|
| 工單新建，有未完成的前置工單依賴 | Scrum Master | `Pending` |
| 工單新建，無前置依賴（即使仍有「❓ 需要確認的事項」建議值） | Scrum Master | `Ready` |
| 前置工單全數完成，依賴解除 | Scrum Master / 執行者 | `Ready` |
| 母工單完成子工單拆分 | Scrum Master | `In Progress` |
| Developer 開始執行工單 | Developer | `In Progress` |
| Developer 完成開發並提交交付回報 | Developer | `In Review` |
| Code Reviewer 判定 `[ ✅ APPROVED ]` | Code Reviewer | **維持 `In Review`**（放行訊號，不是結案；見 §1.9） |
| 結案 commit 已合併進主線 | Developer | `Done` |
| Code Reviewer 判定 `[ ❌ CHANGES REQUESTED ]` | Code Reviewer | `In Progress` |
| Scrum Master 取消工單 | Scrum Master | `Canceled` |

### 1.6 日期欄位更新規則 (Date Tracking)
工單包含兩個日期追蹤欄位，格式為 ISO 8601（精確到分鐘 + 時區，例如 `2026-04-22T16:04+08:00`）：

| 欄位 | 填寫時機 | 執行者 |
|---|---|---|
| `**📅 建立時間 (Created):**` | 工單首次建立時 | Scrum Master |
| `**✅ 完成時間 (Closed):**` | Status 改為 `Done` 時——隨**結案 commit** 一併寫入（§1.9） | Developer |
| `**✅ 完成時間 (Closed):**` | Status 改為 `Canceled` 時 | Scrum Master |

- 未完成的工單，`Closed` 欄位保持 `—`（em dash）。
- 若工單曾被重新開啟（由 `Done` 退回 `In Progress` 後再次完成），`Closed` 欄位以**最新**的完成時間為準。

> ⚠️ **此步驟為強制規範**：若角色在交付或審查時忘記更新 Status 或日期欄位，等同於流程斷裂，後續角色將無法正確識別工單的可執行狀態，且 BACKLOG 的近期結案篩選將無法正確運作。

### 1.7 執行前的 Human-in-the-loop 確認 (🔒 HITL Gate at Execution)

任何工單在真正動工（撰寫／修改程式碼、實作）**之前**，執行者（Developer / DevOps 等）**必須**檢查工單「4. 人為補充與確認 (Human-in-the-loop)」區塊：

- 若「❓ 需要確認的事項 (Agent 提問)」內有**未解答**的項目（對應「✍️ User 補充回覆 (User Input)」為空、且工單正文亦無使用者裁定），**即使該項附有建議值 / 預設值，也必須先向使用者逐條提問並取得回覆後，才可繼續實作**。**嚴禁**逕自採用建議值當作已確認。
- **唯一例外**：該項的「✍️ User 補充回覆」已由**使用者本人**填寫，或工單正文（Description／決議註記）已明載使用者裁定——此時視為已確認，依該回覆執行。
- **建議值 = 提案，不是授權**。使用者未回覆前，建議值不具開工授權效力。

> 此為 `Ready` 解耦後的配套機制：開放問題不再把工單卡在 `Pending`，改由本閘門在**執行當下**把關，確保每個需要決策的點都經過使用者。取得回覆後，應把使用者的裁定補寫回工單「✍️ User 補充回覆」欄位以留痕。

### 1.8 新發現缺陷的收容優先序 (🔁 Defect Routing Priority)

當實測或審查中發現新缺陷時，**先判定成因落在哪張工單的範圍內**，再決定收容方式。判定順序如下：

1. **成因工單尚未結案（Status ≠ `Done` / `Canceled`）→ 一律優先退回該工單，不新開工單。**
2. 僅在符合下列**例外**時才新開工單（見下方「何時才新開工單」）。

#### 退回時的必辦事項

退回**不是只把狀態改回去**，必須同時處理三件事，否則下一輪會照著同一份錯誤規格再做錯一次：

| # | 動作 | 說明 |
|---|---|---|
| 1 | **修正受影響項目** | 找出**導致缺陷的那條 AC／規格敘述並直接改寫正確**。錯的規格必須改掉，不可只在後面追加新條——原條文留著，下一輪仍會依它實作。 |
| 2 | **取消失效的勾選** | 原本已 `- [x]` 但實際上未達成（或因缺陷而不成立）的 AC，改回 `- [ ]`，並在該條後方註明退回原因。 |
| 3 | **新增待處理項目** | 缺陷所暴露、原工單未涵蓋的面向補為新的 AC（含對應的回歸測試要求）。 |

另須依 §2.3 回寫機制，於工單新增「📝 Code Review 備註」或「🔁 退回紀錄」章節，載明**退回日期、缺陷成因、對應到哪幾條 AC**，使開發者重新開工時不需回頭翻對話。

狀態轉換依成因工單當下的狀態決定：

| 成因工單當下狀態 | 執行者 | 動作 |
|---|---|---|
| `In Review` | Code Reviewer | 判定 `[ ❌ CHANGES REQUESTED ]`，Status 退回 `In Progress`（§1.1） |
| `In Progress` | Scrum Master / Developer | Status 維持不變，直接補寫 AC 與退回紀錄 |
| `Ready` / `Pending` | Scrum Master | Status 維持不變，直接修正規格（尚未開工，改單成本最低） |

#### 何時才新開工單（例外）

- **成因工單已 `Done` / `Canceled`**：已結案的工單不得復活，改開 `*-FIX-*` 工單並於 §1 載明「回歸來源工單」。
- **修復位置落在該工單範圍之外**：缺陷成因跨模組、或修復要動的檔案不屬該工單的 Outputs 時，依**修復位置所在模組**開單（模組歸屬原則同 §3.2）。
- **修復內容會使原工單顯著膨脹**：新增範圍已超出原工單標題所能涵蓋的目的時，開新單並以**前置依賴**與原工單串接，避免同檔並行修改互相覆蓋。

#### Epic 同步

- **退回不改變子工單張數**：Epic 第一條 AC 的 N 值**不動**，僅需在 Epic §4 補一行退回紀錄（載明退回哪張、原因）。
- **新開才需調整 N**：同步更新 Epic 的 N 值、§5 子工單清單與依賴鏈。

> 📌 立規背景：某張工單在 `In Review` 期間被發現引入功能全阻斷的回歸，最初以新開 FIX 工單處理，後改為**退回原工單**——成因工單既未結案，新開單只會讓同一份錯誤 AC 留在已「完成」的工單裡，並在同一個檔案上製造兩張工單的並行修改風險。

### 1.9 程式碼隔離與分支 (🔀 Code Isolation)

工單定義工作的**狀態**，本節定義工作的**實體位置**。

**一張工單 = 一個分支，分支名 = Task ID。** 使 `git branch` 的每一行都對得回
`docs/features/{模組}/tasks/{TaskID}.md`。
**沒有工單的臨時工作，一律先開一張最小工單再開分支。**

**分支與審查載體的生命週期對映工單狀態：**

| 工單狀態 | 分支 | 審查載體（PR／MR／工單審查報告） |
|---|---|---|
| `Ready` | — | — |
| `In Progress` | **建立分支**，分支名 = Task ID | 首次推送後開**草稿**，並把編號回填工單 |
| `In Progress` → `In Review` | **停止寫入**——任何寫入都會讓審查對象漂移 | 草稿 → **正式請求審查** |
| `In Review` → `In Progress` | **恢復寫入**，同一分支繼續修正 | 轉回草稿 |
| `In Review` → `Done` | 結案 commit → 合併 → 刪除分支 | **已合併** |
| → `Canceled` | 分支內有 commit 時**必須詢問使用者**保留或丟棄，不可逕自刪除 | 關閉 |

- **不存在 `In Progress` → `Done` 的捷徑**，故每張工單必然經歷 `In Review`。
- **開發過程中隨時可以 commit，不必等審查通過。** 反過來做會讓 `In Review` 期間
  沒有任何 ref 指著變更，一次 `git checkout`／`git reset` 就永久消失。
- **`Done` = 已合併，不是 APPROVED。** APPROVED 只是放行訊號；合併還可能失敗。
- **`Done` 的前置條件**：結案 commit 已合併進主線，且分支已刪除。
- **結案 commit 在合併前寫入、於合併後生效。** 合併失敗它就不在主線，
  工單自動維持 `In Review`，不需要任何回滾動作。
- **回填的是審查載體的編號，不是 commit SHA**（合併會產生全新的 SHA），
  且在**開 PR 當下**就回填，不等結案。

> 📌 **本節只定義「工單走到這一步該做什麼」。** 分支怎麼開、commit 怎麼打、
> 推送授權、合併與刪分支怎麼做、換平台要對應哪些能力，一律見
> [`docs/standards/git_workflow.md`](../../docs/standards/git_workflow.md)。

### 1.10 Commit 閘門 (🔒 HITL Gate before Commit)

**閘門在「離開工單分支」的那一刻，不在每一顆 commit。**
性質同 §1.7，差別在 §1.7 把關「開工前」，本節把關「進入主線前」。

**`{TaskID}` 分支上的中間 commit 不需事前取得同意，直接 commit 即可。**
它們進不了主線，而且隨時可以改寫——因此複查對象是**已經寫下、可用
`git commit --amend`（單顆）或合併訊息（多顆）修改的訊息**，不是一份「即將寫下」
的草稿。開發過程中即可 commit（§1.9），交付審查時訊息已經存在於分支上。

**要取得當次同意的是「進入主線的那則訊息」**：沒有任何一則未經使用者當次同意的訊息
可以留在主線上。**豁免到分支邊界為止**——直接在主線或整合分支上做的 commit
不適用本豁免，仍須事前取得同意。

**配套：未經逐顆複查的中間 commit 必須留下拓撲。** 正因為它們沒被逐顆把關，
事後追溯的需求反而更高，合併時不可把側支抹平，見
[`docs/standards/git_workflow.md`](../../docs/standards/git_workflow.md) §6.1。

- **交付時（`In Progress` → `In Review`）呈交分支上實際的 commit 訊息原文**，
  隨交付回報一併表態（§2.2）。多顆時呈交的是**合併後會留在主線的那一則**。
- **執行時必須使用經確認的那則訊息原文**，不得在同意後再自行增刪；
  需要改就用 `git commit --amend`（單顆）或合併時的訊息（多顆）改寫。
- **上一次的同意不延用到下一次。** 每次交付各自取得一次同意。
- 使用者要求修改訊息時，改完須**重新呈現完整訊息**再確認，不可只回覆「已修正」。
- 審查退回（CHANGES REQUESTED）後重新交付時，**訊息須重新呈現、重新取得同意**。
- **合併時產生的訊息同樣適用，而且它才是最終進入主線的那一則。** 無論是 squash
  合併的訊息，還是非 fast-forward 合併自動寫的 `Merge branch '...'`，都從未經過
  使用者過目——這是本閘門最容易漏掉的路徑，合併前必須先呈現。

commit message 的格式、Emoji 對照與**禁止寫入的內容**（AI 署名 trailer、對話脈絡、
工具／session 內部狀態），一律以
[`.agent/workflows/commit-message.md`](../workflows/commit-message.md) 為**正版**，本節不重述。

> 此閘門的成立前提是**工單狀態機不允許自動併入主線**：什麼訊息能代表這張工單
> 留在歷史裡，屬於使用者的決定。Agent 代為執行 `git commit` 或合併只是省下貼指令的工，
> 不改變決定權歸屬。commit 時點與推送授權見
> [`docs/standards/git_workflow.md`](../../docs/standards/git_workflow.md) §3.1／§4。

### 1.11 文檔權威階序 (📚 Source of Truth Hierarchy)

查證「現在的規格是什麼」時，權威由高至低：

| 層級 | 內容 | 效力 |
|---|---|---|
| **1. 非工單文檔** | `docs/features/{module}/{brd,prd,hld,lld,api_spec,test_plan}.md`、`docs/standards/` | **唯一的開發準則**。規格衝突以此為準 |
| **2. 程式碼現況** | 已合併的程式碼 | **事實**（與實作它的工單狀態無關）。與第 1 層不符即為缺陷，依 §1.8 收容 |
| **3. 開放工單** | Status 非 `Done`／非 `Canceled` | 待辦意圖，可引用；**尚未生效** |
| **4. 已結案工單** | Status 為 `Done` / `Canceled` | **歷史紀錄，不得作為規格依據** |

**為什麼已結案工單不算規格**：文檔會演進，演進後往往另開新工單，舊工單可能永遠不會被執行、也不會被回頭修正。以已結案工單推導「現在該怎麼做」，等於拿一份已被取代的快照當準則。此規則與 §1.8「已結案工單不得復活」互為表裡——**不改它，也不引用它**。

**實務守則**：

- 工單 `Inputs` 必須指向第 1 層文檔；引用其他工單時**只能引用開放工單**，且須註明其 Status。
- 第 1 層文檔之間互相矛盾（跨模組尤其常見）→ 適用 §1.2 矛盾暫停，回報使用者裁定，**不可自行選一邊**。
- 已結案工單若記載了第 1 層文檔沒有的規格 → 代表**文檔漏了**：應開文檔修訂單把它補進主文件（見 `docs/standards/documentation_conventions.md` §2.1「工單轉 Done 後折併回主文件」），而不是繼續引用該工單。
- 「目前進度」不適用本階序，一律以 `docs/development/BACKLOG.md` + `git log` 為準。

> 📌 立規背景：某次審查後的討論中，Code Reviewer 以一張已 `Done` 的工單推導「現行規格允許某項操作」，經使用者指正——工單只是當時的快照，`prd.md`／`lld.md`／`api_spec.md` 才是準則。本節將該裁定明文化。

---

## 2. 角色交接規範 (Handoff Rules)

### 2.1 Scrum Master → Developer
- Scrum Master 產出的每張工單必須遵循 `.agent/resources/task_template.md` 格式。
- 工單中的 `Inputs` 區塊必須包含可存取的檔案路徑或資源連結（非抽象描述）。
- 工單的 `Ready`/`Pending` 以**前置工單依賴**是否解除為準，**不**以 Human-in-the-loop 是否回覆為準。工單內「❓ 需要確認的事項」即使附建議值，仍須於**執行前**由執行者強制向使用者確認（見 §1.7），不得逕自採用建議值。

### 2.2 Developer → Code Reviewer
- **交付回報的第一行必須指出審查載體的位置**——使用 PR 的專案填 PR 連結、
  使用 MR 的填 MR 連結、無遠端的填分支名。審查者要能只憑這一行就找到要審的東西。
- Developer 完成開發後，必須提交一份統一的**三段式交付回報**：
  - **✅ 執行項目追蹤**: 逐條對應工單的 Acceptance Criteria，標示通過或未通過。
  - **🚨 矛盾與風險警告**: 列出開發過程中發現的任何風險或架構衝突（無則填「無」）。
  - **🧪 驗證/測試建議**: 提供具體的驗證方法（`curl` 指令、`pytest` 指令、或瀏覽器頁面路徑）。
- 交付回報連同工單原文一併提交給 Code Reviewer。
- **交付回報須附上分支上實際的 commit message 原文**（依
  `.agent/workflows/commit-message.md` 產出），與報告**一併呈交、一次表態**。
  變更**此時已經 commit 並推送**，訊息可用 `--amend` 修改（§1.10）。
- 審查者可只針對報告表態退回；退回時訊息一併作廢，重新交付須重新呈現。
  通過後由 Developer 依 §1.9 做結案 commit、合併、刪除分支。

### 2.3 Code Reviewer → Done / 退回
- Code Reviewer 審查後產出標準化審查報告（含 Verdict: APPROVED 或 CHANGES REQUESTED）。
- 若 APPROVED，**工單狀態維持 `In Review`**——APPROVED 是放行訊號，不是結案。接著由 Developer 做**結案 commit**（Status → `Done`、填 Closed；審查載體編號早在開 PR／MR 當下就已回填）、合併、刪除分支；**合併完成之後工單才是 `Done`**——見 §1.9。
- 若 CHANGES REQUESTED，工單退回 `In Progress`，Developer 根據報告修正。
- **回寫機制 (Write-back)**：Code Reviewer 審查完成後，**必須**將審查結果直接寫入對應工單的 `.md` 檔案（可更新驗收標準、規格區塊，或新增「📝 Code Review 備註」章節），確保 Developer 重新開工時無需額外查找審查報告。詳細寫入格式請參照 `code-reviewer` SKILL.md 中的「回寫審查結果至工單」條款。

---

## 3. 共用命名約定 (Naming Conventions)

### 3.1 Task ID 編碼規則
格式：`{模組前綴}-{階段}-{佇列}-{流水號}`

**模組前綴對照表：**（👉 安裝到新專案後，請把下表換成你自己的模組）
| 前綴 | 模組名稱 | 對應目錄 |
|------|---------|---------|
| `XXX` | 範例模組（安裝後刪除本列） | `docs/features/example_module/` |

> ⚠️ 新增模組時，必須先在此對照表登記前綴後，Scrum Master 才可開始產出工單。
> 前綴建議取 3 個大寫字母，全專案唯一；`scan_backlog.py` 依此辨識工單歸屬。

**階段前綴：**
| 前綴 | 含義 | 範例 |
|---|---|---|
| `DOC` | 文件產出 (BRD/PRD/HLD/LLD 等) | `ABC-DOC-BRD-001` |
| `DEV` | 程式開發 | `ABC-DEV-FE-001` |
| `TEST` | 測試 | `ABC-TEST-E2E-001` |
| `DEPLOY` | 部署 | `ABC-DEPLOY-STAGING-001` |

**佇列前綴：**
| 前綴 | 對應 Task Type | 預設 Assignee (Skill) |
|---|---|---|
| `FE` | `queue_frontend` | `frontend-developer` |
| `BE` | `queue_backend` | `backend-developer` |
| `AGENT` | `queue_agent` | `devops-engineer` |
| `QA` | `queue_qa` | `qa-automation-engineer` |
| `DATA` | `queue_data` | *(未來擴充)* |
| `MANUAL` | `manual_user` | 使用者本人 |
| `BRD/PRD/HLD/LLD` | `docs_generation` | 對應的文件產出 Skill |

### 3.2 檔案存放慣例
| 產出類型 | 存放路徑 |
|---|---|
| 功能需求文件 (BRD/PRD/Wireframe) | `docs/features/{功能模組名}/` |
| 架構設計文件 (HLD/LLD/API) | `docs/features/{功能模組名}/` |
| 開發工單 (Task) | `docs/features/{功能模組名}/tasks/`，每張工單一個獨立 `.md` 檔，檔名即 Task ID（例如：`ABC-DEV-FE-001.md`） |
| 程式碼 | `src/` (依專案結構) |
