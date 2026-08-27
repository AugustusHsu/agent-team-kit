# [Review: PEV-DEV-AGENT-044] 實作工單 DAG、欄位與 wave 驗證

## 2026-08-27 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-044`
**Round：** `ROUND-001`
**Base：** `983cada7d8c01e0dc249063ed651758edc33e866`
**Head：** `8be71ed21b2bd61cbfed4768dcbe8ebd7be95bb2`
**Fresh-context reviewer：** `gpt-5.6-sol`／`xhigh`；五行 fidelity probe 原樣通過。

## 1. AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | 兩份模板均含五欄；五欄全無的舊工單可相容讀取，partial-field 會明確拒絕 |
| AC-02 | ❌ | 一般 unknown／self／duplicate／cycle 與穩定推導正確，但非空非法 `Blocked By` token 會被靜默丟棄或截成另一個 ID |
| AC-03 | ❌ | 唯一 ID、2～5 張、未知、重複歸屬與 direct closed-set 已驗證；缺 Integration Review Target 或不存在的 40 位 opening base 仍通過 |
| AC-04 | ❌ | 根目錄 glob 與實際檔案可能重疊卻被判 disjoint；外部副作用只靠標題／Task Type heuristic，無來源證據仍可能放行 |
| AC-05 | ❌ | phase、階段數量與 contract 涵蓋 migrate 已驗證，但 migrate 不依賴 expand 仍通過 |
| AC-06 | ✅ | 測試使用 `tmp_path` 真實 Markdown 與 Git、零 mock；隔離負向對照證實新增 13 項測試會讓舊實作轉紅 |
| AC-07 | ✅ | 兩個目標測試檔 68/0、BACKLOG 原位重建一致、`git diff --check` 通過；隔離全套的 4 項 baseline 環境失敗非本 diff 引入 |

## 2. 重大瑕疵清單

### F-01 — P1／依賴 token 可被靜默改寫

- **File／line：** `kit/.agent/scripts/scan_backlog.py:137`
- **Claim：** `parse_task_ids()` 只搜尋 regex 子字串，`nonsense` 變成空依賴，
  `MOD-DEV-BE-099x` 被截成 `MOD-DEV-BE`，會錯算 wave、blocks、closed-set 與並行候選。
- **Evidence：** `parse_task_ids("nonsense") == []`；
  `parse_task_ids("MOD-DEV-BE-099x") == ["MOD-DEV-BE"]`。
- **Recommended fix：** 先拆 token，再以正式 Task ID regex 完整匹配；任何非法 token 產生 planning error。

### F-02 — P1／並行候選可產生 false positive

- **File／line：** `kit/.agent/scripts/scan_backlog.py:437-471,541-552`
- **Claim：** `*.md` 與 `README.md` 被誤判不相交；未知第三方帳號／網路寫入工作只因未命中
  標題關鍵詞就被視為可隔離。
- **Evidence：** `scopes_are_definitely_disjoint(["*.md"], ["README.md"]) == True`；
  `queue_backend`＋repo-local scope 的「更新第三方帳號設定」回傳可隔離。
- **Recommended fix：** glob 無非空可證靜態前綴或路徑表示模糊時 fail closed；外部副作用必須有
  權威來源證據，不能由未命中 heuristic 推導安全。

### F-03 — P1／Parallel Change 可錯序

- **File／line：** `kit/.agent/scripts/scan_backlog.py:584-623`
- **Claim：** migrate 沒有依賴 expand 時仍無錯誤，expand 與 migrate 可落在同一 wave，違反
  `expand → migrate → contract`。
- **Recommended fix：** 每張 migrate 的 transitive dependencies 必須包含唯一 expand；補錯序負向測試。

### F-04 — P1／Round Manifest schema 與 opening base 驗證不足

- **File／line：** `kit/.agent/scripts/scan_backlog.py:657-669`
- **Claim：** 刪除必備 Integration Review Target 後仍 `errors=[]`；不存在的 40 位 hex 也被接受。
- **Recommended fix：** 要求 Integration Review Target 欄位存在；opening base 必須以 argv-list
  `git cat-file -e <sha>^{commit}` 驗證為 repo 內 commit object。

## 3. 客觀驗證

| 指令／檢查 | 變更前／負向對照 | 變更後 |
|---|---:|---:|
| 全套測試 | base：196 passed、4 failed | head：209 passed、4 failed |
| 目標兩檔 | base implementation＋head tests：55 passed、13 failed | 68 passed、0 failed |
| `python3 kit/.agent/scripts/precheck.py` | — | 9/9，exit 0 |
| process_evolution graph | — | exit 0，`errors: []` |
| BACKLOG 重建 | — | `/tmp` 原位重建後 `cmp` exit 0 |
| `git diff --check <base>..<head>` | — | exit 0 |
| git_workflow／CHECKS integrity | — | 1 passed |
| Scrum Master `quick_validate` | — | `Skill is valid!` |

隔離全套的四個失敗在 base 與 head 完全相同，皆為未變更的 `test_check_versions.py` 在 archive
環境解析 `/tmp/docs/standards/...`；不歸因於本 diff，但該環境下不宣稱全套完全綠燈。

## 4. 架構優化與建議

- Round branch 建議完整驗證 `feature/{topic}`，不可接受空 topic。
- Write Scope 應先正規化 POSIX 路徑，拒絕 `..`、空 segment 與模糊表示。
- `different_wave` 是四項條件外的額外保守限制；應明示候選為同 wave 配對。
- precheck 可在單次執行快取 planning view，避免重建兩次。
- 四個既有 `check_versions` archive 環境失敗應另案處理。

審查者全程未修改檔案、ref 或工作樹。本 target 不得合併進 round；修正後須固定新 head 重審。

## 5. 修正紀錄（Developer）

- **F-01：已修正。** `Blocked By` 改為 token 完整匹配；backtick 清單外的殘留文字也會失敗。
- **F-02：已修正。** root glob、`..`、空 segment 與模糊路徑全部 fail closed；經使用者同意新增
  `External Effects` 第六來源欄位，缺欄、非法、重疊／父子作用域不得並行，並移除標題／Task Type
  heuristic。同 wave peer 修改另一工單引用的 Contract 也會阻擋候選。
- **F-03：已修正。** 每張 migrate 的 transitive dependencies 必須包含唯一 expand。
- **F-04：已修正。** Round 必須保存 Integration Review Target，branch 必須有非空 topic，
  opening base 必須是 repo 中存在的 commit object。
- **規範同步：** 六欄語意已同步 `parallel_development.md`、ADR-001、Git workflow、兩份模板與
  Scrum Master skill；skill quick validation 通過。
- **修正後證據：** 目標兩檔 78 passed；完整套件 223 passed；precheck 9/9；
  `git diff --check` 通過。隔離舊 head `8be71ed…` 套用新測試為 67 passed、11 failed。

修正後正式結論待第二輪 fresh-context review 固定新 head 後獨立重跑。
