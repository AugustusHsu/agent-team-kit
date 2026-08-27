# [Review: PEV-DEV-AGENT-038] doctor／refresh 與無副作用 probes

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | `doctor --offline` 的 subprocess log 沒有 exec／prompt／ls-remote／gh api |
| AC-02 | ✅ | Claude／Codex 都有 version、auth metadata、functional 三段 probe ID |
| AC-03 | ✅ | 假 Codex auth exit 1、functional marker 成功 → `degraded`，兩筆 probe 都保留 |
| AC-04 | ✅ | Git remote、GitHub API、Cloud Connector、automated review 分成六個 state keys |
| AC-05 | ✅ | App／Connector 預設 unknown；manual confirmation 寫明來源並依 manifest TTL 到期 |
| AC-06 | ✅ | doctor 強制重跑；refresh 在五分鐘內零新增呼叫，指定 probe 才多一筆 |
| AC-07 | ✅ | probe registry 沒有 push／PR create／issue create／購買；online 只有 read 命令 |
| AC-08 | ✅ | 假 executable 覆蓋成功、not_installed、auth、quota、permission、timeout |
| AC-09 | ✅ | 完整 pytest 170 passed；precheck 7/7；installer 待合併 0 |

## 2. Offline 是預設，也是明確旗標

以下兩個寫法都不跑網路：

```text
agent_runtime.py doctor
agent_runtime.py doctor --offline
```

只有 `--online` 才允許 functional prompt、`git ls-remote` 與 `gh api user`。CLI 整合測試把
四個假執行檔的每次呼叫寫入 log；offline 輸出只有：

```text
claude --version
claude auth status --json
codex --version
codex login status
```

沒有 `claude -p`、`codex exec`、`git ls-remote` 或 `gh api user`。本機命令形狀另以實際
`claude 2.1.243`、`codex-cli 0.149.1` 的 `--help` 校準；沒有為驗證而發出付費 prompt。

## 3. 矛盾證據不再被壓成單一布林值

負向對照讓假 `codex login status` 回 `not logged in`／exit 1，同一次的假 `codex exec`
回 `AGENT_RUNTIME_PROBE_OK`。結果：

```text
profile status                 degraded
profile error_class            evidence_conflict
probes.auth.status             unavailable
probes.auth.error_class        auth
probes.functional.status       verified
```

所以使用者看得到「metadata 失敗但功能真的能跑」，不會因為只信其中一邊而被誤導。
state 仍然只保存固定摘要，不保存假命令輸出的原文。

## 4. GitHub 不是一個 connected 布林值

online read 對照讓 `git ls-remote` 與 `gh api user` 都成功，結果只有
`git_remote_read`／`github_api_read` 變 verified；下列四項仍是 unknown：

- `git_remote_write`；
- `github_api_write`；
- `codex_cloud_connector`；
- `automated_review`。

這直接封住「SSH／remote read 成功，所以 Codex Cloud Connector 一定能用」的錯誤推論。
寫入能力不以 push、開 PR 或傳訊息探測，只能人工確認並帶到期時間。

## 5. TTL 與人工確認

doctor 用於重新診斷，會跑選定範圍；refresh 預設只跑缺資料或過期項目。實測第一次 doctor
留下呼叫數，五分鐘後 refresh 完全不增加；再指定 `--probe codex_login_status` 才精確增加一筆。

不可觀察的 App 能力可寫：

```text
--manual-profile codex-app-local=verified
--manual-integration codex_cloud_connector=verified
```

證據種類是 `manual_confirmation`，不是偽裝成 command probe；本例 1800 秒後到期。

## 6. 錯誤分類與無副作用保證

| 假情境 | error_class |
|---|---|
| executable 不存在 | `not_installed` |
| `not logged in` | `auth` |
| `quota exceeded` | `quota` |
| `permission denied` | `permission` |
| 超過測試 timeout | `timeout` |

出貨的 online probe 只有唯讀 prompt、`git ls-remote`、`gh api user`；沒有 push、開 PR、
傳訊息、改 Connector 或購買。App 沒有可靠 API 時維持 unknown，不用 cloud task 製造證據。

## 7. 驗證

- health／init 目標測試：**17 passed**；
- 完整 `uv run pytest --basetemp=/dev/shm/agent-team-kit-038-full`：**170 passed**；
- `python3 .agent/scripts/precheck.py`：**7/7 全綠**；
- `./install.sh . --upgrade --dry-run`：新增 0、更新 0、待合併 0；
- `[平台相關]` 標記未新增；`git diff --check` 通過。

## 8. 留給後續工單

- 039 只消費這份 state，不自行重跑或重解釋 probe；
- 041 才對本 repo 的真實 Claude／Codex／GitHub 狀態執行 doctor、處理現有本機設定；
- App Connector 若仍不可觀察，dogfooding 結果必須保留 unknown，不得補造「已連線」。
