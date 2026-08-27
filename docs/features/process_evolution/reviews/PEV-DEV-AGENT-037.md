# [Review: PEV-DEV-AGENT-037] agent runtime state、registry 與 init

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | `init` 有互動選擇、重複 flags 與 `--config` 三種入口 |
| AC-02 | ✅ | 非互動且沒有 fresh verified 本機 profile 時 exit 2；能力不足也拒絕成功 |
| AC-03 | ✅ | 既有政策不覆寫；差異寫 `.new`，既有候選不同時遞增 `.new.2` |
| AC-04 | ✅ | 三層設定合併測試通過；portable `project_id` 在真實臨時 worktree 相同 |
| AC-05 | ✅ | state schema 只允許狀態、時間、短摘要與錯誤分類；摘要另擋 credential 形狀 |
| AC-06 | ✅ | 損壞 JSON 回報行列；不支援版本、未知欄位／profile 回報檔案與 JSON path |
| AC-07 | ✅ | 測試只用 stdlib、`tmp_path`、假 HOME／XDG 與臨時 git repo |
| AC-08 | ✅ | 完整 pytest 162 passed；precheck 7/7；installer dry-run 待合併 0 |

## 2. 三層資料沒有混在一起

| 層 | 路徑 | 這一層唯一能回答的問題 |
|---|---|---|
| 共享政策 | `.agent/agent-runtime.json` | 專案允許／偏好哪些 profiles、資料與外連政策 |
| 使用者狀態 | `${XDG_STATE_HOME}/agent-team-kit/agent-runtime.json` | 這台機器上哪些 profile 此刻有可信證據 |
| repo-local override | `.agent/agent-runtime.local.json` | 這台機器在此專案要停用或改偏好哪些 profile |

`project_id` 在共享政策中，是 portable 32 位 hex ID。測試把初始化後的專案真的 `git init`、
commit，再 `git worktree add`，兩邊 `project_identity()` 完全相同。初始化前才以 git common dir
的 hash 當暫時 identity，避免 worktree 各自生出不同專案。

override 不得改 `project_id`；未知 profile 也不會被當成「目前停用所以無所謂」而略過。
這能提早抓出供應商改名或使用者拼字錯誤。

## 3. init 的三種外形

```text
互動：python3 .agent/scripts/agent_runtime.py init
旗標：python3 .agent/scripts/agent_runtime.py init --non-interactive \
        --verified-profile codex-cli --prefer-profile codex-cli
設定檔：python3 .agent/scripts/agent_runtime.py init --non-interactive --config <path>
```

非互動模式沒有 verified profile 的實測訊息：

```text
❌ init：至少要有一個本機開發 profile verified；請加 --verified-profile 或在設定檔提供 verified_profiles
```

`verified` 不只看 profile 名稱：它還必須是 `local`，具備 `implementation_local` 的全部硬性能力，
而且 functional TTL 尚未到期。其餘已啟用 profiles 可以沒有 state，留給 038 探測成 `unknown`。

## 4. 重跑與候選安全

- 已有政策且新設定不同：保留原檔，寫 `.agent/agent-runtime.json.new`；
- `.new` 已被使用者修改：不覆寫，改寫 `.new.2`；
- 缺 `AGENTS.md`／`CLAUDE.md`：從 `.agent/templates/` 產生候選，不直接啟用新入口；
- 全部相同：只更新本機短狀態，政策不產生無意義 diff。

這與 036 的 installer 邊界一致：upgrade 只提示 migrate，init 也不趁機把缺少的種子檔正式補入。

## 5. 狀態安全與錯誤可定位

runtime state 的 schema 沒有任意 metadata／stdout／environment 欄位；evidence 只容許
`kind` 與 160 字內的單行 `summary`。工具自行產生的 init 證據是固定摘要，不讀 shell output。
若日後 probe 嘗試把 `token=`、`cookie=`、`private key=` 等形狀塞進摘要，寫入前會拒絕。

負向測試同時證明：

- JSON 截斷會指出檔案、行、列；
- `schema_version: 99` 指到 `$.schema_version`；
- `capabilites` 拼錯指到 `$.capabilites：未知欄位`；
- local override 的 `typo-agent` 指到 `$.disabled_profiles`。

## 6. 驗證

- runtime registry／adapter／init 目標測試：**20 passed**；
- 完整 `uv run pytest --basetemp=/dev/shm/agent-team-kit-037-full-2`：**162 passed**；
- `python3 .agent/scripts/precheck.py`：**7/7 全綠**；
- `./install.sh . --upgrade --dry-run`：新增 0、更新 0、待合併 0；
- `git diff --check`：通過。

完整測試第一次抓到 README 內容物樹漏列 `agent_runtime.py`，已補成雙入口與新初始化流程；
這是出貨門面真的跟著實作走，而不是只讓新測試自己全綠。

## 7. 留給後續工單

- 038 在同一支腳本加入 `doctor`／`refresh` 與真實 probe，不另造 state schema；
- 039 使用 `effective_policy()`、registry 與 state 實作 route／explain；
- 041 實作 migrate，處理本 repo 現存的 Claude／Codex 本機設定，不在本張碰真實帳號。
