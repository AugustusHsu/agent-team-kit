# 🔀 Git 流程與 PR 閘門 (Git Workflow)

> 本檔是 Git 操作的**正版**：分支怎麼開、commit 何時寫、審查在哪裡發生、怎麼合併與收尾。
> 工單狀態與角色交接見 [team_protocol](team_protocol.md)；多工單的 DAG、所有權、整合驗證與
> panel 見 [parallel_development.md](parallel_development.md)。

平台預設為 GitHub，但規則描述的是能力，不把 PR／MR 當成歷史的唯一載體。凡是換 git server
就要重新對應的規則，都標了「平台相關」；§8 與 §9 提供對照。

## 1. 核心原則

| # | 原則 | 為什麼不可協商 |
|---|---|---|
| 1 | **一張工單 = 一條 Task ID 分支** | branch 必須能直接追溯到工作來源 |
| 2 | **合併前必須通過固定對象的審查與自動檢查** | 合併後才查，錯誤已進共享事實；只看浮動 head 則核可無法重建 |
| 3 | **所有進入共享分支的合併都保留 merge commit** | branch ref 刪除、平台更換後，拓撲與過程 commits 仍留在 Git 物件中 |
| 4 | **主線是唯一生效事實；round 是尚未生效的整合候選** | branch 上的 Done 預告或 panel 資料只有合併成功才會進主線 |

沒有工單的臨時工作，一律先開最小工單再開 branch。多工單輪次額外使用短命
`feature/{topic}` round branch，但不取代每張工單的 Task ID branch。

## 2. 工單 × Git 狀態對映

工單狀態是唯一來源，branch 與審查載體是鏡像：

| 工單狀態 | Task ID branch | 審查／合併 |
|---|---|---|
| `Ready` | — | — |
| `In Progress` | 建立／恢復寫入 | 首次 push 後開草稿載體 |
| `In Review` | 停止寫入；head 固定 | 正式窄審；通過後才能進 round／main |
| 多工單窄審通過 | branch 保留、worktree 移除 | merge commit 進 round；工單仍 `In Review` |
| `Done` | 合併成功後安全刪除 | 單張已進 main，或所屬 round 已進 main |

`APPROVED` 是對 pinned Review Target 的放行，不是 `Done`。單張工單的結案資料必須先寫入
reviewed head；多工單輪次則在 round 最終候選一次寫入全部結案資料，再做 round panel。
正式核可後不得追加會改 head 的結案 commit。

## 3. 分支

- **Task branch 名 = Task ID**，不加描述。
- **Round branch 名 = `feature/{topic}`**，一輪一個清楚目標與 2～5 張封閉工單，輪次完即刪。
- 單張工單從最新主線／既有整合線建立；多工單依 Round Manifest 的 opening base 與 DAG 建立。
- 無依賴且通過 Write Scope／Contract／副作用檢查者可從相同 base 平行開出；有依賴者等前置
  merge 進 round 再開工，不以隱性堆疊取代 DAG。
- 工單取消且 branch 已有 commit 時，必須詢問使用者保留或丟棄，不得逕自刪除。

### 3.1 推送授權

| 對象 | 授權 |
|---|---|
| Task ID branch | 可依專案政策推送；本 repo 未經使用者當下說「push」不得主動推送 |
| round、main 與任何受保護共享分支 `[平台相關]` | 一律需要當次明確同意 |

推送與合併分開授權；commit 完成不代表可以 push，Task branch 可推也不代表可以進共享分支。

## 4. Commit

開發過程中可隨時在 Task branch commit，不必等審查通過。一張工單可有多顆過程 commit；
它們會透過 merge topology 保留，`--first-parent` 則提供乾淨的人讀視角。

- Task branch 的中間 commit 不需逐顆取得訊息同意。
- 直接在 round／main 做 commit，以及任何 Task → round、Task → main、round → main 的 merge 訊息，
  都適用 `team_protocol.md` §1.10 的當次使用者複查。
- 多工單 round 的審查前結案 commit 直接寫在共享 round，必須先呈現訊息並取得當次同意。
- 訊息格式與禁止內容一律以
  [`.agent/workflows/commit-message.md`](../../.agent/workflows/commit-message.md) 為正版。

## 5. 審查載體

PR／MR 或本地 review artifact 是操作介面；審查正版一律是
`base SHA + head SHA + Task/Round ID`。

- **合併前審查載體 `[平台相關]`**：必須同時可取得 pinned diff、工單與第 1 層文件。
- **草稿 ↔ 正式請求 `[平台相關]`**：`In Progress` 首次推送開草稿，交付才轉正式；退回轉草稿。
- **自動檢查 `[平台相關]`**：載體上必須看得到對同一 head 執行的檢查結果。
- **意見落點 `[平台相關]`**：平台討論仍須回寫 repo 內 review artifact；平台資料不是唯一來源。

PR 描述至少寫 Task／Round ID、做了什麼、驗證指令與 Review Target；已有工單內容只附路徑，
不複製成第二份規格。

## 6. 合併與收尾

### 6.1 合併方式：所有共享方向保留 merge commit

平台有無 PR 都不改變歷史語意：

```bash
git merge --no-ff <來源分支> -F <經當次複查的訊息檔>
```

| 方向 | merge 訊息第一行 | first-parent 視角 |
|---|---|---|
| Task → main | 完整 Task ID | main 一張工單一行 |
| Task → round | 完整 Task ID | round 一張工單一行 |
| round → main | Round ID；Body 逐張列完整 Task ID | main 一輪一行 |

禁止 squash merge 與 rebase merge：它們會抹平已核准保留的側支拓撲。PR／MR 繼續負責 review、
CI 與權限；Git merge commit 負責可攜歷史。

- **阻擋未通過合併 `[平台相關]`**：Review Target 不符、正式審查未通過或檢查紅燈時，
  機制上必須擋住，不能只靠自律。
- **執行合併 `[平台相關]`**：平台必須選「Create a merge commit」或等價操作，並使用經當次
  複查的訊息原文；無平台則使用上方 `--no-ff` 指令。

### 6.2 結案資料必須在正式審查 head 內

版控工單描述的是主線事實，但 `Done` 要記錄的事件正是「即將合併」。解法是讓 branch 上先寫
結案資料，只有 merge 成功時才進主線；merge 失敗，主線工單仍維持原狀。

**單張工單：**

1. Developer 完成內容與測試，Status → `In Review`，完成自查。
2. 在 Task branch 寫入結案資料（Status → `Done`、Closed），固定 base／head／Task ID。
3. fresh-context reviewer 對該最終 head 正式審查；退回則同 branch 修正並重新固定 target。
4. APPROVED 後不再改 head，merge commit 進 main；成功後安全刪 branch。

**多工單輪次：**

1. 各 Task branch 固定 target、窄審通過後逐張 merge commit 進 round，Task 仍 `In Review`。
2. 對「當下 main＋round」做整合 QA；失敗依 `parallel_development.md` §6 退回。
3. round 上以一顆經同意的結案 commit 寫入全部 Task `Done`／Closed 與 manifest 放行資料。
4. 固定 round target 並跑 fresh-context panel；APPROVED 後不再改 head。
5. round merge commit 進 main；成功後安全刪除全部 Task／round branches。

這個順序讓「head 改變就失效」能成立，也避免 APPROVED 後追加結案 commit 的死循環。

### 6.3 回填審查載體編號

**回填識別碼 `[平台相關]`**：使用 PR／MR 時在開啟當下填編號；無平台填 `—`。
Review Target 的 SHA 與正式結果寫在 review artifact／Round Manifest，不塞進這個欄位。

### 6.4 刪除 branch 前的驗證

**已合併訊號 `[平台相關]`**：平台回報 merge commit 已建立，且本地確認來源 head 是目標祖先；
無平台直接以安全刪除作最後防線：

```bash
git merge-base --is-ancestor <來源分支> <目標分支>
git branch -d <來源分支>
```

禁止把失敗改成 `git branch -D`。多工單 round 中，Task branch merge 進 round 後先保留 ref；
round merge main 後，內層 Task commits 經巢狀 merge 仍是 main 祖先，所有 branch 都應能 `-d`。

## 7. 多工單工作輪次

### 7.1 開輪

1. 以最新 main 建立 `feature/{topic}`，把完整 SHA 寫入 Round Manifest。
2. 驗證 2～5 張封閉 Task ID、DAG、Write Scope、Contract 與外部副作用。
3. 由來源資料推導 wave；同 wave 只有符合全部放行條件者才可同時活躍。
4. 兩張以上同時活躍時，每條 Task branch 一個 worktree；否則使用主工作目錄即可。

### 7.2 Task 合併進 round

每張工單各自完成 pinned 窄審，再用 merge commit 進 round。合併前呈現完整訊息並取得當次同意。
合併後立即移除該 Task worktree，但 branch 與 `In Review` 狀態保留到整輪進 main。

前置 Task 已進 round 後，依賴它的下一 wave 才能從目前 round head 開工。若 main 期間出現必要且
命中本輪 Contract／Write Scope 的變更，停止受影響工單，在 round 層統一適應，不讓各 branch
自行按日曆 rebase。

### 7.3 整合、panel 與 round merge

所有 Task 進 round 後，以當下 main 建立整合候選並執行 QA。通過後依 §6.2 寫審查前結案 commit、
固定 Round Review Target、執行 panel 與 reconciliation；關鍵 overlap zone 保留最終人為閘門。

round merge 訊息第一行寫 Round ID，Body 每張 Task ID 一行，取得當次同意後才進 main。
main 成功後重建 BACKLOG、完成 Round Manifest、移除 worktrees，最後安全刪除 Task／round branches。

### 7.4 歷史讀法

| 想看什麼 | 指令 |
|---|---|
| main 有哪些輪次／單張工單 | `git log --oneline --first-parent main` |
| round 依序合入哪些 Task | `git log --oneline --first-parent <round>` |
| 展開完整巢狀拓撲 | `git log --oneline --graph --decorate --all` |
| 反查某 Task／Round | `git log --all --grep=<ID>` |

first-parent 是讀取粒度，不在寫入時銷毀過程資料。

## 8. 平台適配

### 8.1 能力對照表

| kit 要求的能力 | GitHub（預設） | GitLab | 無遠端／純本地 | 檢查內容 |
|---|---|---|---|---|
| 隔離變更 | branch／選用 worktree | branch／選用 worktree | branch／選用 worktree | — |
| 合併前審查的載體 | Pull Request＋repo review artifact | Merge Request＋repo review artifact | `reviews/<TaskID>.md`／Round Manifest | — |
| 自動檢查 | Actions | GitLab CI | 合併前手動跑測試 | BACKLOG 是否為最新、工單 Status 值是否合法、工單時間戳是否正確、文件是否有死連結、結案工單是否填了 Closed、AC 全打勾的工單是否已結案、未結案工單的 Assignee 是否合法、Agent runtime 版控政策與秘密邊界是否合法 |
| 阻擋未通過的合併 | Branch protection＋required checks | Protected branch＋pipeline | 人工紀律＋pinned artifact | — |
| 審查意見的落點 | PR comment＋repo artifact | MR discussion＋repo artifact | repo artifact | — |
| 合併方式（§6.1） | Create a merge commit | Merge commit | `git merge --no-ff` | — |
| 「已合併」的訊號 | merge commit＋祖先檢查 | merge commit＋祖先檢查 | `git branch -d` 成功 | — |

只要平台能填滿七列就能套用。自動檢查列必須與 `.agent/scripts/precheck.py` 的 `CHECKS` 逐項一致；
專案技術棧測試屬第 2 層，由專案自己的 workflow 負責。

### 8.2 GitHub 設定要求

main 與實際使用的 `feature/**` 必須受保護：

| 設定 | 值 | 理由 |
|---|---|---|
| 禁止直接 push | 開 | 共享歷史要經當次同意與檢查 |
| 合併前必須經 PR／checks | 開 | §1 原則 2 |
| 允許的合併方式 | **只留 merge commit**；關閉 squash／rebase merge | §1 原則 3 |
| Dismiss stale approvals | 開（若平台 approval 是正式 verdict） | head 改變必須使舊核可失效 |
| Required approvals | 單一協作者預設 0；有獨立人類 reviewer 才提高 | PR 作者不能核可自己，避免永久死鎖 |

分支樣式必須是 `feature/**`，不是不跨 `/` 的 `feature/*`。本 repo 只有一名協作者時，
fresh-context AI review 證據寫入 repo artifact，不能把平台的 Required approvals 誤設為 1。

### 8.3 沒有 PR 時

沒有 PR 不降低 Review Target、fresh context、測試或 merge topology：工單用
`docs/features/<模組>/reviews/<TaskID>.md`，round 用 Round Manifest；APPROVED 也必須落盤。
合併使用 `git merge --no-ff`，訊息照樣先取得當次同意。

有遠端但不開 PR 時，自動檢查仍必須在合併前跑。workflow 需監聽所有工作分支：

```yaml
on:
  push:
    branches: ['**']
  pull_request:
```

kit 的 `.github/workflows/kit-precheck.yml` 已採此設定；驗收要查看實際 run，不只閱讀 YAML。

## 9. 換平台檢查清單

正文共有九處平台相關能力，換 git server 時逐條對應：

```bash
grep -c '\[平台相關\]' docs/standards/git_workflow.md   # 應為 9
```

| # | 出處 | 要對應的能力 |
|---|---|---|
| 1 | §3.1 | 受保護共享分支與 push 授權 |
| 2 | §5 | 合併前 pinned 審查載體 |
| 3 | §5 | 草稿與正式請求狀態 |
| 4 | §5 | 同一 head 的自動檢查 |
| 5 | §5 | 意見回寫 repo artifact |
| 6 | §6.1 | 阻擋未通過合併 |
| 7 | §6.1 | 執行 merge commit 與訊息來源 |
| 8 | §6.3 | 工單回填的載體識別碼 |
| 9 | §6.4 | 已合併訊號與祖先驗證 |

## 相關

- 多工單排程、所有權與審查：[parallel_development.md](parallel_development.md)
- 工單生命週期與狀態機：[team_protocol.md](team_protocol.md)（指向 `.agent/resources` 正版）
- Commit message 正版：[`.agent/workflows/commit-message.md`](../../.agent/workflows/commit-message.md)
- 文件分檔與交叉引用：[documentation_conventions.md](documentation_conventions.md)
