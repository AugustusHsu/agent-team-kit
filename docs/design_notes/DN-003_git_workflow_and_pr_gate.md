# [DN-003] Git 流程與 PR 閘門

**🚥 狀態 (Status):** 🎓 Graduated
**📅 建立 (Created):** 2026-08-16
**🔗 依賴 (Depends on):** DN-001（格式）
**🎓 畢業去向 (Landing):** D（改流程／基礎建設）→ `kit/docs/standards/git_workflow.md`，見 §8

> ⚠️ DN 不得寫實作步驟。本檔只處理「該長什麼樣」與「哪些還沒答」。
> **worktree 不在本 DN 範圍內**——kit 的 worktree 內容已整份移除，日後另開 DN 重新設計。

## 1. 問題陳述

kit 有「worktree 流程」，**沒有「git 流程」**。分支、合併、commit 時點這些
與 worktree 無關的通用概念，原本全部寄生在一份 421 行、講 worktree 的文件裡。

**量化證據**（移除前的盤點）：kit 內 git 概念（branch/merge/push/rebase）
命中 57 處在 `worktree_workflow.md`，第二名 `team_protocol.md` 只有 12 處；
而管 commit 的那份 workflow 命中 **0** 處——它只管訊息格式。
**「git 流程」在 kit 裡從未作為獨立主題存在過。**

該檔已隨本次變更移除，通用分支規則就地保留在 `team_protocol.md` §1.9
（改寫為平台中立版本），避免出現「完全沒有分支規範」的空窗。
但 §1.9 只是最小保底，**完整的 git 流程仍待本 DN 定案**。

現況缺口：

| 主題 | 現在寫在哪 | 狀態 |
|---|---|---|
| commit 訊息格式／禁止內容 | `.agent/workflows/commit-message.md` | ✅ 乾淨的單一職責 |
| commit 前 HITL 閘門 | `team_protocol.md` §1.10 | ✅ 獨立 |
| 分支命名 = Task ID、分支生命週期 | `team_protocol.md` §1.9 | ⚠️ 保底版，待搬進正式文件 |
| 合併策略 | **隨 worktree 文件一起移除，目前無規範** | ❌ |
| PR／平台上的 code review | **完全沒有** | ❌ |
| push／remote／遠端同步 | **完全沒有** | ❌ |
| CI 與工單狀態的關係 | **完全沒有** | ❌ |

## 2. 為什麼與 PR 閘門合併成一份 DN

PR 建立在分支上、合併產生 merge commit。分支規範與 PR 閘門是同一個設計的兩面，
拆成兩份 DN 會產出互相引用、必然漂移的兩份文件。**合併是為了避免那個結果**。

## 3. 需要使用者裁定的核心決策

### 3.1 commit 時點 vs PR 的前提

現行規範（`team_protocol.md` §1.9／§1.10）明定：

> **commit 發生在 APPROVED 之後，不是交付時。** 一張工單產出一個 commit，
> 用的是通過審查的那則訊息原文。

PR 流程的前提**恰好相反**：要先有 commit 並 push，才有東西可開 PR、
才有 diff 可審、CI 才跑得起來。兩者不可能同時成立。
這不是細節，是**流程的根本假設相衝突**。

現行設計的副作用：`In Review` 期間變更**沒有任何 ref 指著它**，
只存在工作目錄與暫存區。任何 `git checkout`／`git reset`／清理動作都會使它永久消失。
PR 流程天然免疫於此，因為東西已經在遠端。

> ✅ **已裁定（2026-08-16）：改成「先 commit 再審」。**
> 決定性理由不是 PR 相容性，而是**現行設計會弄丟工作**——`In Review` 期間
> 沒有 ref 指著變更，一次誤操作就永久消失，本 repo 已有實證（見 `WTG-DEV-BE-001`
> 記錄的孤兒 worktree 帶著未合併 commit）。
>
> **連帶影響**：`team_protocol.md` §1.9 生命週期表與 §1.10 commit 閘門要改寫，
> 五份 skill 的「此時不要 commit」提示要改。commit message 的**複查閘門依然保留**，
> 只是複查對象從「即將寫下的訊息」變成「已經寫下、可用 `--amend` 修的訊息」。

### 3.2 push 授權 vs PR 的前提

使用者全域規則：**「絕不主動 push，除非我在那個當下說了 push」**。
而 PR 本質上要求 push——不 push 就沒有 PR。

若每次都要當下同意，PR 的自動化收益會被閘門吃掉大半；
若放寬，就動到使用者明確立過的規則。

可能的中間路線（待評估，非結論）：

- 只有 `{TaskID}` 分支可自由 push，`main` 永遠需要當次同意
- Draft PR 階段可自由 push，轉 Ready for Review 才需要同意
- 維持原規則，接受 PR 流程多一道確認

> ✅ **已裁定（2026-08-16）：採第一條——按分支分層。**
> `{TaskID}` 分支自由 push；`main`（與任何受保護分支）一律需要當次同意。
>
> 理由：原規則「絕不主動 push」保護的其實是**共享歷史**，不是 push 這個動作本身。
> 一條只有自己在用的 `{TaskID}` 分支被推上去，沒有任何人的工作會被影響，
> 而且推上去反而讓變更多一份遠端備份——正好補上 §3.1 指出的遺失風險。
>
> **前提條件**：`main` 必須在 GitHub 上設為受保護分支，否則這條規則只是口頭約定。
> 見 §6。

### 3.3 工單、分支、PR、commit 的粒度對映

前兩節解決「什麼時候 commit／push」，但沒有回答**「一個 PR 裝什麼」**。
沒有這個答案，PR 閘門就設計不出來——所以它跟前兩節同屬本 DN，不另開 DN。

**先拆掉一個常見誤解：PR 對應的是工單，不是 commit。**
「每個 commit 就 PR 一次」不會發生，因為 PR 的審查單位是**一個完整的可驗收變更**。

| 物件 | 是什麼 | 對工單的數量關係 |
|---|---|---|
| **工單 Task** | 一個可獨立驗收的變更單位 | — |
| **分支 Branch** | 工單的實體位置（§1.9 已定：分支名 = Task ID） | **1 : 1** |
| **PR** | 工單的審查容器 | **1 : 1**（但反向不成立，見下） |
| **commit** | 開發過程的存檔點 | **1 : N** |

一張工單開發過程可以有 5 顆 commit，最後合成**一個** PR 送審。

**工單要切多細——三條判準，全部滿足才算切對：**

1. **AC 可獨立驗收**——不需要等另一張工單完成才驗得了。
   驗不了就是切太細，該合併。
2. **合併後系統仍可運作**——不能出現「這張合進去會壞，要等下一張才修好」。
   這條擋掉「為了讓 PR 變小而硬拆」。
3. **一次審查看得完**——diff 規模讓審查者在一個 session 內讀完。
   超過就是切太粗，該拆。

判準 1 與 3 會互相拉扯（1 要求夠大、3 要求夠小），**判準 2 是仲裁者**：
拆到不能再拆而仍滿足 2 的那個大小，就是正確粒度。

**特例：DN 本身的工作不開工單。**
這不是例外處理，是 [DN-001](DN-001_design_note_mechanism.md) §3.2 進場規則的直接推論——
工單的存在前提是「寫得出 AC」，而 DN 的存在前提正是「寫不出 AC」，兩者互斥。
因此：

| 階段 | 開工單？ | 分支 | PR |
|---|---|---|---|
| **探索期**（撰寫、修改 DN） | ❌ 不開 | 直接在 `main` | 不走 |
| **落地期**（DN 畢業後的實作） | ✅ 開 | `{TaskID}` | 走完整流程 |

> 📌 本 DN 自己就在探索期。在 `main` 設為受保護分支之前，DN 變更直接 commit
> 到 `main` 是符合上表的；設為受保護分支之後改走 PR（見下）。

**修正：PR 與工單不是雙向一對一。**
上表說「每張工單一個 PR」是對的，但**反過來不成立**——`main` 設為受保護分支後，
探索期的 DN 變更也必須走 PR（否則推不上去），而 DN 依上表不開工單。因此正確的
關係是：

> **每張工單一個 PR，但不是每個 PR 都有工單。**

**為什麼不給 `main` 保護開後門（admin bypass）**：PR 的功能不只是審查，還有
CI 閘門與遠端備份。DN 走 PR 幾乎零成本（自己開、自己合），但後門一旦存在
就會被習慣性使用，保護等於形同虛設。

**待決（見 §7）**：判準 3 要不要給數字參考值、PR 內多顆 commit 要不要 squash。

### 3.4 工單狀態 × PR 狀態的對映

> ✅ **已裁定（2026-08-16）。** 原先 §7 分散在「狀態機類／合併策略類／生效點類」
> 的七條待決，其實是同一張表的不同欄位，故一次裁定。

| 工單狀態 | 分支 | PR |
|---|---|---|
| `Ready` | — | — |
| `In Progress` | 建立 `{TaskID}` | 首次 push 後開 **Draft PR** |
| `In Review` | 停止寫入 | Draft → **Ready for Review** |
| 退回 → `In Progress` | 恢復寫入 | Ready → Draft |
| `Done` | 合併後刪除 | **Merged** |

**隨表的五條裁定：**

1. **`Done` = merged，不是 APPROVED。** APPROVED 之後還有 merge 這一步會失敗
   （衝突、CI 紅燈），標早了 BACKLOG 就在說謊。
2. **工單 `In Review` 保留**，不被 PR review 取代。BACKLOG 是從工單生成的，
   PR 狀態進不了 BACKLOG——工單是唯一來源，PR 是它的鏡像。
3. **Draft PR 在 `In Progress` 首次 push 時就開。** 早開的收益是 CI 早跑，
   問題在寫的當下發現，而不是交付後才發現。
4. **CI 紅燈硬擋 merge。** 不擋的話，PR 只是個好看的 diff 檢視器，不是閘門。
5. **合併用 squash。** 這條順帶解掉一個看似矛盾之處：§3.1 裁定「先 commit 再審」
   後，PR 內會有多顆過程 commit，與原規則「一張工單一個 commit」衝突。
   squash 讓兩者**同時成立**——過程 commit 留在 PR 內可追溯，`main` 上仍是
   一張工單一顆。

#### 3.4.1 `In Review` → `Done` 怎麼寫入（寫入時點 ≠ 生效時點）

**問題**：把 Status 改成 `Done` 本身是一次檔案修改，需要 commit。但此時 PR 正要
merge——改在分支上等於「還沒 merge 就宣告 Done」，改在 `main` 上則需要再開一個
PR 才推得上去，會無限遞迴。

**根本原因**：工單狀態是**版控裡的資料**，而它要記錄的事件（merged）發生在
**版控之外**（PR 平台）。這是阻抗不匹配，不是流程沒設計好。

**解法：把寫入時點與生效時點分開。**

| # | 誰 | 動作 |
|---|---|---|
| 1 | Reviewer | PR approve——**工單此時仍是 `In Review`** |
| 2 | Developer | 在 `{TaskID}` 分支做**結案 commit**：Status → `Done`、填 Closed、填 PR 編號 |
| 3 | Developer | squash merge |
| 4 | — | `main` 上工單即為 `Done`，刪除分支 |

第 2 步看似「預告」，但**它不會說謊**：結案 commit 只有在 merge 成功時才會出現在
`main` 上。merge 失敗，那顆 commit 就不在 `main`，工單在 `main` 上仍是 `In Review`
——**狀態自動正確，不需要任何回滾動作**。

> 📌 「工單是唯一來源」指的是 **`main` 上的工單**，不是分支上的。
> 分支上的預告不影響唯一來源。

**連帶：回填 PR 編號取代回填 commit SHA。**
squash merge 會產生**全新的 SHA**，與分支上任何一顆都不同，因此原規則
（`team_protocol.md` §1.9「commit 產生的 SHA 於此時回填工單」）在 merge 前
物理上做不到。改填 PR 編號——開 PR 當下就確定、永不改變，且能反查全部
commit 與審查紀錄。

**連帶：GitHub 設定的硬性要求。**
**不得開啟 "Dismiss stale pull request approvals when new commits are pushed"**，
否則第 2 步的結案 commit 會讓第 1 步的 approve 失效，形成死循環。

## 4. 提議的結構：三層分離

只有最外層跟平台綁定。這是「保留彈性」的機制本身。

| 層 | 內容 | 可否因專案而異 |
|---|---|---|
| **L1 核心** | 一張工單 = 一個分支，分支名 = Task ID；合併前必須通過審查；已合併的 `main` 是唯一事實 | ❌ 不可協商 |
| **L2 狀態對映** | 工單狀態 ↔ 分支／PR 狀態的對應表 | ⚠️ 可調，但要整套一致 |
| **L3 平台適配** | GitHub／GitLab／無遠端各一份 | ✅ 各專案自選 |

**關鍵設計：規範描述「能力」，不描述「指令」。**
kit 不說「必須開 GitHub PR」，而說「必須有一個地方讓審查在合併前發生」。
使用者再把自己的 git server 對上去。

## 5. 能力對照表（L3 的核心）

| kit 要求的能力 | GitHub（預設） | GitLab | 無遠端／純本地 |
|---|---|---|---|
| 隔離變更 | branch | branch | branch |
| 合併前審查的載體 | **Pull Request** | Merge Request | 工單內的審查報告 |
| 自動檢查 | **Actions** | GitLab CI | 合併前手動跑測試 |
| 阻擋未通過的合併 | Branch protection ＋ required checks | Protected branch ＋ pipeline | 人工紀律 |
| 審查意見的落點 | PR review comment | MR discussion | 工單「審查報告」章節 |
| 「已合併」的訊號 | PR merged | MR merged | `main` 含該 commit |

只要一個平台能填滿這六列，就能套用本流程。填不滿的列要在專案 `CLAUDE.md` 註明降級方式。

## 6. 預設實作：GitHub（本 repo 現況）

- `.github/workflows/ci.yml` **已存在**（2026-08-12 建立），已設 `on: pull_request`，
  跑 Python 3.10/3.12/3.13 的 pytest ＋ 一個 `stdlib-only` job
  （實際 `./install.sh` 到暫存專案再跑腳本）。
- **CI 不需要新建**，缺的是工單狀態與 PR 狀態的對映。本 DN 範圍因此比原先預估小。
- ⚠️ 本地 `main` 領先 `origin/main` **11 顆** commit（2026-08-16 實測）。
  PR 對著 `origin/main` 開，不先同步的話第一個 PR 會夾帶大量不相干的 commit。
  **這是落地前必須先解決的前置**，且解法只有一個：把 11 顆推上去。
- ✅ **本地 `main` 已於 2026-08-16 推送至 `origin/main`，兩者同步**，
  CI 四個 job（`stdlib-only` ＋ Python 3.10／3.12／3.13）全綠。PR 前置已解除。
- **`main` 必須設為受保護分支**（§3.2 裁定的前提，也是 §7.1 定的 cutover 生效點）。
  查核於 2026-08-16：目前 `protected: false`，**尚未設定**。設定內容：

  | 設定 | 值 | 依據 |
  |---|---|---|
  | 禁止直接 push | ✅ 開 | §3.2 |
  | 合併前必須通過 CI | ✅ 開 | §3.4 第 4 條 |
  | 合併前必須經過 PR | ✅ 開 | §3.3 |
  | 允許的合併方式 | **只留 squash** | §3.4 第 5 條 |
  | Dismiss stale approvals | ❌ **必須關** | §3.4.1——開了會讓結案 commit 作廢 approve，形成死循環 |

  ⚠️ **設定時機在最後**：見 §8「執行順序」。

## 7. 待決事項

### 7.1 已裁定（2026-08-16）

- [x] §3.1 commit 時點 → **先 commit 再審**
- [x] §3.2 push 授權 → **按分支分層**，`{TaskID}` 自由、`main` 需當次同意
- [x] §3.3 粒度 → **工單 : 分支 : PR = 1 : 1 : 1，commit 為 1 : N**；
      反向不成立（DN 有 PR 無工單）
- [x] `Done` = **merged**，不是 APPROVED（§3.4）
- [x] 工單 `In Review` **保留**，不被 PR review 取代（§3.4）
- [x] Draft PR 在 **`In Progress` 首次 push** 時開（§3.4）
- [x] CI 紅燈 **硬擋 merge**（§3.4）
- [x] 合併策略 → **squash**；一併解決「一張工單一個 commit」與
      「PR 內允許多顆 commit」的表面衝突（§3.4）
- [x] `In Review` → `Done` 的寫入方式 → **結案 commit 在 merge 前、生效於 merge 後**（§3.4.1）
- [x] 回填內容 → **PR 編號取代 commit SHA**（squash 後 SHA 必變）（§3.4.1）
- [x] 探索期 vs 受保護分支的衝突 → **DN 也走 PR，但不開工單**，不開 admin 後門（§3.3）
- [x] cutover 生效點 → **`main` 設為受保護分支的那一刻**，因為那是物理上
      擋得住的第一刻，不是文件寫完的那一刻（§6）

### 7.2 明確 defer（不擋畢業）

- [ ] §3.3 判準 3「一次審查看得完」的數字參考值 → **defer**。
      現在給等於憑空捏造；累積十來個 PR 後再看實際分佈，需要時另開 DN。
- [ ] `git_workflow.md` 的章節切法、`team_protocol.md` §1.9 哪些內容搬走 →
      **defer 到落地工單**，屬實作細節。
      **§1.9／§1.10 各被 7 處交叉引用（跨 7 個檔），不得改編號**——只能改內容與標題。

### 7.3 落地時必須連帶改寫（不是待決，是已知工作量）

- `team_protocol.md` §1.9 生命週期表、§1.10 commit 閘門——「APPROVED 後才 commit」
  全數失效
- 五份 skill 的「此時不要 commit」提示
- `task_template.md`：commit SHA 欄位改為 PR 編號欄位

## 8. 畢業去向

**畢業條件檢核（依 [DN-001](DN-001_design_note_mechanism.md) §3.4）：**

1. ✅ 所有待決已答或明確 defer——見 §7.1／§7.2
2. ✅ 寫得出可驗收的 AC——§3.4 的狀態對映表與 §3.4.1 的結案 commit 流程
   已具體到可以逐條寫成驗收標準
3. ✅ **使用者本人簽核畢業**——2026-08-16 逐項裁定 §3.1／§3.2／§3.3／§3.4
   的設計內容，並於同日明確確認本 DN 畢業。

**軟上限診斷（DN-001 §5）**：本 DN 約 300 行，已觸發 250 行軟上限。
依規定的兩個診斷問題檢查：

- **是不是多個問題混在一起？** 否。commit 時點、push 授權、粒度、狀態對映
  是同一個問題（git 流程）的不同面向，拆開會產生互相引用、容易漂移的設計。
- **內容夠寫出 AC 了嗎？** 夠——見上。

因此**結論是畢業，不是拆分**。畢業後 DN 轉為歷史紀錄，長度不再是成本。

**類型**：**D（改流程／基礎建設）**

**落點**：

- **`kit/docs/standards/git_workflow.md`（新建，本 DN 的主要產出）**——
  含 §4 三層結構、§5 能力對照表、§3.4 狀態對映表、§3.4.1 結案 commit 流程
- `kit/.agent/resources/team_protocol.md` §1.9／§1.10 改寫（見 §7.3）
- `kit/.agent/resources/task_template.md` 的回填欄位
- 五份 skill 的交付提示
- `kit/docs/DOCS_MAP.md`、`kit/docs/standards/README.md` 登記
- **`README.md`**——放 §5 能力對照表的精簡版，讓使用者一眼看懂
  「預設是 GitHub，換成別的 git server 要對應哪幾件事」

**執行順序（不可調換）**：文件落地 → 再設 `main` 保護。
設早了，落地工單自己就得走新流程，而新流程的文件正是它要產出的。

**工單**（2026-08-16 開立，模組前綴 `PEV`）：

| 工單 | 範圍 |
|---|---|
| `PEV-DEV-AGENT-001` | `git_workflow.md` 新建 ＋ `team_protocol` §1.9／§1.10 改寫 ＋ 五份 skill ＋ `task_template` ＋ 登記 |
| `PEV-DEV-AGENT-002` | `README.md` 能力對照表精簡版（依賴 001） |

**為什麼 001 這麼大、不再往下拆**：依 §3.3 判準 2「合併後系統仍可運作」——
若把 `git_workflow.md` 新建與 `team_protocol` §1.9 改寫拆成兩張，
第一張合併後會出現「新文件說先 commit 再審、§1.9 說 APPROVED 後才 commit」
的**規範互相矛盾**狀態。對讀規範辦事的 agent 而言，那等同系統壞掉。
判準 2 在此充當仲裁者，把判準 3「一次審查看得完」的拆分壓力擋下來。
