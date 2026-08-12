# Git Worktree 工作流程 (Worktree Workflow)

> 本文是 worktree 使用規則的**正版**。工單狀態機本身見
> [`.agent/resources/team_protocol.md`](../../.agent/resources/team_protocol.md) §1，
> 本文只定義「程式碼實體放在哪」以及對應的建立／凍結／收尾規則。

## 0. 這份規則要解決的問題

工單系統定義了工作的**狀態**，但沒有定義工作的**實體位置**。多個 Agent（或 Agent 與人）
同時動同一個 checkout 會互相覆蓋；而隨手開的 worktree 又會變成沒人記得的孤兒。

貫穿全文的一條原則：

> **孤兒 = 本機狀態沒有版控裡的對應物。**

worktree 是純本機的東西，永遠不進版控、不跨機器。因此每一個 worktree 都必須在版控裡
（工單 `.md`）留下對應紀錄——否則沒有任何機制記得它存在。

---

## 1. 什麼時候該開 worktree

**判準：並行度 > 1 才開。**

| 情境 | 做法 |
|---|---|
| 單線工作，使用者就在旁邊看 | **不開**，直接在主 checkout 開分支即可 |
| Agent 在背景執行，使用者同時可能編輯 | 開 |
| 多個 Agent 平行處理不同工單 | 開，且受 §7 限制 |

**預設 WIP = 1：同一時間只允許一個活躍的 worktree。** 要開第二個必須由使用者明確授權。

> 這條上限的價值不只是控制負擔——它讓「有沒有孤兒」變成一眼可判的布林值：
> `git worktree list` 平時 1 行（主 checkout），開工時 2 行。**出現第 3 行就是異常**，
> 不需要任何比對邏輯。上限放寬到 3 的話，你得先記得哪幾個是合法的才能判斷。

**重依賴專案的例外**：若專案的開發環境動輒數 GB（`node_modules`、含 CUDA 的
虛擬環境），每開一個 worktree 就複製一份。此類專案應優先採用 §4 的共用環境做法，
或直接放棄 worktree、改用單一 checkout 加分支。

---

## 2. 命名：分支名 = Task ID

```
分支名     DAT-DEV-BE-001
worktree   .claude/worktrees/DAT-DEV-BE-001/
```

如此 `git worktree list` 的每一行都對得回
`docs/features/{模組}/tasks/DAT-DEV-BE-001.md`，無需額外對照表。

**沒有工單的臨時工作，一律先開一張最小工單再開 worktree。** 這是孤兒的最大來源：
有工單的，BACKLOG 會記得；沒工單的，只有本機的 `git worktree list` 記得，
而那個檔案不會有人每天去看。

worktree 目錄一律放在 `.claude/worktrees/` 底下，**且該路徑必須被 `.gitignore` 忽略**
（kit 出貨的 `.gitignore` 已含此條）。worktree 目錄內有一個 `.git` **檔案**，
若被 `git add` 會變成一個詭異的 gitlink——這不是衛生問題，是正確性問題。

---

## 3. 生命週期：對映工單狀態機

**worktree 的存活期橫跨 `In Progress` 與 `In Review` 兩個狀態**，
從 `Ready → In Progress` 建立，到 `In Review → Done` 銷毀。

| 工單狀態轉換 | worktree 動作 |
|---|---|
| `Ready` → `In Progress` | **建立** worktree，分支名 = Task ID，並在工單登記（§6.1） |
| `In Progress` | 自由 commit |
| `In Progress` → `In Review` | 草擬 commit 訊息 → 取得使用者同意 → commit → **凍結** |
| `In Review` | worktree **保留但凍結**：developer 不得再寫入，reviewer 只讀 |
| `In Review` → `In Progress`（CHANGES REQUESTED） | **解凍**，同一個 worktree 繼續改 |
| `In Review` → `Done`（APPROVED） | 合併 → 收尾（§5）→ **收尾完成才可標 `Done`** |
| 任何狀態 → `Canceled` | 見 §5.4 |

### 3.1 沒有 `In Progress` → `Done` 的捷徑

狀態機不存在這條路徑，`Done` 只能由 Code Reviewer 從 `In Review` 推進。
因此**每個 worktree 必然經歷 `In Review`**，不會有「做完直接收掉」的情況。

### 3.2 交付時必須 commit，不得只停在 staged

**每個 worktree 有自己私有的暫存區**（`.git/worktrees/<name>/index`，與主 checkout 的
`.git/index` 是不同檔案）。staged 但未 commit 的內容只存在該私有 index 與工作目錄裡，
**worktree 一移除就永久消失**。已 commit 的則進入共用物件庫、由分支 ref 指著，
目錄刪掉照樣還在。

另外兩個理由：

- Code Review 需要穩定引用。審 working tree 沒有 SHA 可指、無法回填工單，
  且 developer 可能還在改，reviewer 看到的內容會浮動。
- commit message 本身就是交付說明的一部分。

**但不得自動 commit。** 依全域慣例，commit 前必須草擬訊息並取得使用者當下同意。
HITL 閘門就掛在 `In Progress → In Review` 這個轉換點上（性質同
team_protocol §1.7，只是那道閘門在「執行前」，這道在「交付時」）。

### 3.3 `In Review` 為什麼是凍結而不是另開 worktree

一旦交付時已 commit，**審查的對象就是一個 SHA，根本不需要工作目錄**——
`git diff main...DAT-DEV-BE-001` 從主 checkout 就能執行。這正是 §3.2 那條規則換來的好處。

另開 review 專用 worktree 的代價則是實在的：

- 多一份開發環境（見 §4）
- `CHANGES REQUESTED` 會退回 `In Progress`，若已銷毀就得重建環境，而退回可能發生多次
- 違反 §1 的 WIP = 1

因此規則是**凍結而非分裂**：`In Review` 期間 developer 不得再寫入，
reviewer 需要實際執行測試時就在該 worktree 內執行——因為已凍結，共用是安全的。

> **真正需要第二個 worktree 的情境不是「審查」，是「審查期間要平行開下一張工單」。**
> 那個 worktree 屬於下一張工單，不屬於 review。兩者不要混為一談。

### 3.4 「卡在 `In Review`」

指 developer 已 commit 並推進到 `In Review`，但 reviewer 遲未審完。

**這不是孤兒**——工單存在、狀態明確、版控裡查得到。它是 WIP 積壓，
但會佔住 §1 的唯一 worktree 名額。處理方式是催審或明確授權開第二個 worktree，
而不是把 worktree 收掉（收掉會讓 CHANGES REQUESTED 無處可退）。

---

## 4. 建立時的 bootstrap

新 worktree 是一個**乾淨的 checkout**，只有版控裡的檔案。以下東西**不會**跟過去，
必須逐項處理：

| 類型 | 例子 | 處理方式 |
|---|---|---|
| 本機設定 | `.env`、本機憑證 | 複製（每個 worktree 各一份） |
| 唯讀共用資產 | 模型權重、大型測試素材 | **symlink**，不要複製 |
| 可寫獨佔資產 | 本機 DB、向量庫、快取 | 見 §7.2——多 worktree 時會互相踩 |
| 開發環境 | `.venv`、`node_modules` | 見下 |

**共用開發環境**（重依賴專案必做）：把虛擬環境指到 repo 之外的固定路徑
（例如 `UV_PROJECT_ENVIRONMENT`），或使用有全域 store 的套件管理器（pnpm），
避免每個 worktree 複製一份。

專案應把自己的 bootstrap 步驟寫進 `docs/standards/devenv_spec.md`；
本文只規定「必須有這一步」，不規定內容。

---

## 5. 收尾程序

### 5.1 標準流程

```bash
# 1. 合併（在主 checkout 執行；worktree 內絕不 merge）
git merge <Task-ID>

# 2. 移除目錄
git worktree remove .claude/worktrees/<Task-ID>

# 3. 刪除分支
git branch -d <Task-ID>

# 4. 確認無殘留
git worktree list      # 應只剩主 checkout
git worktree prune     # 清掉目錄已消失但登記還在的紀錄
```

**順序不可顛倒**：分支仍被 worktree 佔用時，git 會拒絕刪除該分支。

### 5.2 ⚠️ `git branch -d` 的誤報陷阱

`git branch -d` 的「是否已合併」只檢查**當前 HEAD**。
若把工單分支合併進的是**非當前分支**（例如合併到 `develop`，而 HEAD 在 `main`），
`-d` 會回報：

```
error: the branch '<name>' is not fully merged.
If you are sure you want to delete it, run 'git branch -D <name>'
```

**這則訊息在「已安全合併到別的分支」與「真的沒合併」兩種情況下完全相同。**

> **禁止**看到 `-d` 失敗就改用 `-D`。必須先客觀驗證：
>
> ```bash
> git merge-base --is-ancestor <分支> <合併目標分支> && echo 安全
> ```
>
> 驗證通過才可 `-D`。養成 force 習慣的 Agent 遲早會無聲丟掉一批 commit。

### 5.3 收不掉的狀況，依「force 的代價可否逆」分類

**必須回報使用者、禁止自行 force：**

| 阻擋原因 | 風險 |
|---|---|
| worktree 內有未提交變更（`remove` 會拒絕） | force 會永久遺失 |
| 分支有未合併的 commit | 刪分支即遺失 |
| 有程序仍在該目錄執行（測試、dev server、shell） | 刪除失敗，或刪後被寫回 |

**可自行判斷處理、無須詢問：**

| 狀況 | 依據 |
|---|---|
| `-d` 誤報未合併 | 以 §5.2 的 `merge-base` 驗證 |
| 存在 gitignored 產生物（`.venv`、`node_modules`） | 不影響 `worktree remove`，不算「不乾淨」 |

### 5.4 工單 `Canceled` 時

- worktree 內**沒有** commit → 直接移除目錄與分支
- worktree 內**已有** commit → **必須詢問使用者**要保留分支還是丟棄。
  不可逕自 `-D`

### 5.5 工單重新開啟

工單由 `Done` 退回 `In Progress` 時，原分支通常已刪除。
依 §3 重新建立 worktree，分支名沿用同一個 Task ID。

---

## 6. 防孤兒機制

由強到弱四層，重點在前兩層。

### 6.1 入口登記（最重要）

建立 worktree 的**同時**，在工單 `.md` 內記錄分支名與建立時間。
把「我開過一個 worktree」寫進版控，孤兒就不可能無聲存在。

沒有工單的臨時工作，強制先開一張最小工單（見 §2）。

### 6.2 對帳掛在既有的高頻動作上

`scan_backlog.py` 應讀取 `git worktree list` 與工單狀態對帳，輸出三類異常：

| 異常 | 含義 |
|---|---|
| 有 worktree，但工單不在 `In Progress` / `In Review` | 疑似孤兒 |
| 工單為 `In Progress`，但沒有對應 worktree | 可能有人直接在主 checkout 修改 |
| worktree 對不到任何工單 | 純孤兒 |

**關鍵在於掛在既有動作上**：本套件本來就要求每次異動工單後重跑 `scan_backlog.py`，
因此偵測是免費的，不需要任何人「記得去檢查」。

> **這也是唯一能救「session 中途崩潰」的機制**——它是事後對帳，
> 不依賴 session 正常結束。§6.4 在崩潰時完全無效。

> ⚠️ **尚未實作**：目前 `scan_backlog.py` 還沒有這段對帳邏輯，需另行開單實作。
> 在實作完成前，本層防護不存在，請以 §6.1 與 §6.3 為主。

### 6.3 `Done` 的前置條件

**工單不得標記為 `Done`，除非其 worktree 已完成收尾。** 由 Code Reviewer 在
APPROVED 時一併檢查。這讓清理有強制觸發點，而不是仰賴自覺。

### 6.4 Session 結束的回報義務

Agent 結束工作前必須回報 worktree 狀態（已清理／刻意保留及原因），
不得默默留下。最弱的一層——session 崩潰時無效，故需 §6.2 兜底。

---

## 7. 多 worktree 的額外限制

僅在使用者明確授權開第二個以上 worktree 時適用。

### 7.1 只有 `Ready` 的工單能開 worktree

`Pending` 代表有未完成的前置依賴。下游工單需要上游的程式碼，
但上游尚未合併進主線——在 worktree 裡開工等於**基於一個不存在的基底**。

### 7.2 同時存在的 worktree，工單必須屬於不同模組前綴

模組前綴（team_protocol §3.1）本就對應互不重疊的目錄。
靠邊界避免衝突，而不是靠運氣。

**可寫獨佔資產是這裡最容易爆的點**：本機 DB、向量庫、固定 port、GPU
無法被多個 worktree 同時安全使用（例如兩個 worktree 同時跑 GPU 推論會直接 OOM）。
這類資產必須 per-worktree 各一份，或以約定／鎖確保同時只有一個使用者。
**單 worktree 時此問題不存在，因此極容易被忽略。**

### 7.3 合併一次一個

第二個 APPROVED 的分支若基底已過期，先在其 worktree 內 `git rebase <主線>`，
再回主 checkout 合併。嚴守 §7.2 的模組邊界時，幾乎不會產生衝突。

---

## 8. 收尾回報格式

Agent 每次收尾都必須回報，格式固定。

**成功：**

```
Worktree 收尾
工單：DAT-DEV-BE-001
分支：已合併至 main (7dd838c)
目錄：已移除    分支：已刪除
殘留：無（worktree list 僅剩主 checkout）
```

**未完成——必須寫出「需要使用者決定什麼」，不可只說失敗：**

```
Worktree 收尾 ⚠️ 未完成
工單：DAT-DEV-BE-001
阻擋：worktree 內有 3 個未提交檔案
風險：強制移除會永久遺失這些變更
需要你決定：(a) 先提交再收　(b) 確認可丟棄，我用 --force
建議指令：git -C .claude/worktrees/DAT-DEV-BE-001 status
```

---

## 9. 跨機器注意事項

- **worktree 永遠不跨機器。** 會旅行的只有本文的約定，以及推送出去的分支。
  每台機器各自建立、各自收尾。
- **建立分支的基底**：部分工具預設從 `origin/<default-branch>` 開分支。
  剛初始化、尚未設定 remote 的專案會因此失敗或行為不如預期，
  此類專案應改以本機 HEAD 為基底。
- `.claude/worktrees/` 是慣例路徑，非強制。改用其他路徑時，
  **唯一不可妥協的要求是該路徑必須被 `.gitignore` 忽略**。
