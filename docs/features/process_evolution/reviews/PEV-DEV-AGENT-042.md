# [Review: PEV-DEV-AGENT-042] 混合代理路由與交接端到端驗證

## 2026-08-27 ✅ APPROVED

## 1. AC 核對

| AC | 結果 | 客觀證據 |
|---|---|---|
| AC-01 | ✅ | `test_agent_runtime_e2e.py:108` 從 bare install 連跑兩次 init，policy bytes 不變且 local profile verified |
| AC-02 | ✅ | `:138` Claude＋Codex 同時 verified，偏好選 Codex；兩個候選都有完整 score 與排除理由 |
| AC-03 | ✅ | 同測試覆蓋 only Claude、only Codex 與 Codex TTL 過期後降級 Claude |
| AC-04 | ✅ | `:162` 雙向失效完整保留 Task ID、branch、HEAD、完成／待辦 AC 與 validation |
| AC-05 | ✅ | `:191` project cloud_policy=forbid 時 cloud 即使 verified／偏好第一仍被排除 |
| AC-06 | ✅ | Connector unknown、GitHub SSH／API verified 的真實狀態下，本 repo route 選本機 App，不選 cloud |
| AC-07 | ✅ | `:207` state 只留 Codex CLI 仍滿足 implementation_local |
| AC-08 | ✅ | `:217` 只新增 `acme-cli.json` manifest 就可路由，核心 script bytes 不變 |
| AC-09 | ✅ | 本檔保存 task profile、候選、probe／TTL、雙向 handoff 與人工確認點 |
| AC-10 | ✅ | 完整 pytest 200 passed；precheck 8/8；installer upgrade/dry-run 零待合併；BACKLOG 重生 |

## 2. 路由證據

| 欄位 | 本次值 |
|---|---|
| Task Profile | `implementation_local`；由 `Task Type: queue_agent` 映射 |
| Capability／Data Override | —；`internal` |
| Execution Override | 主路由無；Codex → Claude 的反向驗證明示單次 override |
| 選中 Execution Profile | 主路由 `codex-app-worktree` |
| Probe 證據時間 | 2026-08-27T00:10:09Z；先 refresh 再 route |
| 使用過期 cache | 否；第一次 route 發現 TTL 真正過期並正確零候選，沒有偷用 |
| 中途交接 | Claude → Codex App；Codex CLI → Claude Code，兩次都要求使用者確認 |

### 候選與排除理由

| Execution Profile | Availability | Score | 結果／排除理由 |
|---|---|---:|---|
| `codex-app-worktree` | verified | 152 | 主路由選中；偏好第 1 |
| `codex-cli` | verified | 151 | 合格；偏好第 2 |
| `claude-code-cli` | verified | 150 | 合格；偏好第 3 |
| `codex-app-local` | unknown | — | 無 fresh verified／degraded 證據 |
| `codex-cloud` | unknown | — | 無 fresh 證據；本輪也不允許用 cloud 補位 |

## 3. 六組離線端到端矩陣

| 情境 | 期望 | 實測 |
|---|---|---|
| bare install → init → init | 可重跑、policy 不漂移 | ✅ |
| Claude＋Codex verified | 偏好只在合格候選作用 | ✅ 選 codex-cli |
| Codex TTL 過期 | write 任務不得用 unknown | ✅ 降級 Claude |
| only Claude／only Codex | 單一供應商仍跑路由 | ✅ 各自通過 |
| cloud forbid＋Connector unknown | 不偷選 cloud、不阻擋 local | ✅ 選 codex-cli |
| 第三家 provider | 只加 manifest | ✅ 選 acme-cli，核心未改 |

六組測試全部用假 HOME、假 XDG state 與複製出的 kit，沒有讀真實帳號或網路。

## 4. 真實雙向交接

### Claude → Codex

以 `failed_profile=claude-code-cli` 重路由，選中 `codex-app-worktree`。handoff 保存：

```text
task_id=PEV-DEV-AGENT-042
branch=PEV-DEV-AGENT-042
head=80516d9
completed_ac=AC-01,AC-02,AC-03
pending_ac=AC-04
validation=e2e 6 passed
failure_type=auth
requires_user_confirmation=true
```

### Codex → Claude

以 `failed_profile=codex-cli` 並明示單次 `override_profile=claude-code-cli`，Claude 是 verified
合格候選，因此覆寫通過。相同 Task ID、branch、HEAD、AC 與 validation 全部保留；
`requires_user_confirmation=true`，因為 `implementation_local` 包含 repo write／shell／test。

兩個方向都沒有重開工單、改 Assignee 或換分支。

## 5. TTL 是有效防線，不是裝飾

第一次真實 route 得到零候選。檢查 state 後發現不是程式錯誤：041 的 probe 到期時間為
2026-08-26T17:25Z，而系統時鐘已到 2026-08-27T00:09Z。route 把三個舊 verified 都降成
unknown，對 write 任務全部排除。

依標準先 `refresh --online`，Claude Code、Codex CLI 與 Codex App worktree 再次 verified，
才重跑 route。這次意外正好證明「訂閱／登入可能中途過期」不會被舊 cache 掩蓋。

## 6. GitHub 與 Connector 邊界

041 的真實 doctor 狀態延續到本輪：Git remote URL/read、GitHub SSH、GitHub API read verified；
Git／API write 與 Codex Cloud Connector unknown。本機 `implementation_local` 不需要 Connector，
所以 unknown 不阻擋；cloud 也沒有因 Connector unknown 或 local 失效而被偷選。

`agent_runtime.md:199-203` 補上先前遺漏的 remote URL 與 SSH 探針說明；這是文件同步，
沒有增加路由功能。

## 7. 操作指南

`agent_runtime.md:240` 新增最短流程：

1. 既有專案先 `migrate --dry-run`；
2. `init` 至少確認一個本機 profile；
3. `doctor --online` 取得 fresh 證據；
4. `route --task-file ... --json` 保存候選與排除理由；
5. 中途失效帶 Task ID、branch、HEAD、AC、validation 與 failure type 重路由。

只有純本機唯讀工作可在專案明示後自動 handoff；其餘都停下等待使用者。

## 8. 驗證

- 端到端矩陣：**6 passed**；
- 完整 `uv run pytest --basetemp=/dev/shm/agent-team-kit-042-full`：**200 passed**；
- `python3 .agent/scripts/precheck.py`：結案重生 BACKLOG 後 **8/8**；
- `./install.sh . --upgrade --dry-run`：新增 0、更新 0、待合併 0；
- `git diff --check`：通過；
- `[平台相關]` 標記：9，未改變。

## 9. 重大瑕疵與風險

- 無阻擋問題。
- Codex App／Cloud Connector 仍沒有自動可觀察 API，因此 App 本身與 Connector 分別採人工
  confirmation／unknown；這是已知產品邊界，不被測試偽造。

## 10. 僅人工判讀

- 本 session 確實在 Codex App worktree 執行，因此 `codex-app-worktree=verified` 由人工確認；
- 沒有開 cloud task、沒有寫 GitHub、沒有 push。
