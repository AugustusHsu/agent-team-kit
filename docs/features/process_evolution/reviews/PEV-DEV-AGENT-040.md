# [Review: PEV-DEV-AGENT-040] 工單與審查流程接入能力路由證據

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | 工單模板新增四個 optional 欄位，Execution Override 明列 scope／expires 語法 |
| AC-02 | ✅ | 舊 queue_backend 工單無欄位仍映射 implementation_local，route 顯示來源 |
| AC-03 | ✅ | 新 review template 有選中 profile、候選表、probe、cache、handoff |
| AC-04 | ✅ | precheck 第八項驗 schema、task／execution profile 引用與秘密形狀 |
| AC-05 | ✅ | 刻意放損壞且含 local token 的 ignored override，precheck 仍全綠 |
| AC-06 | ✅ | 未知 profile、非法 scope、forbid cloud 強制 cloud、疑似 token 都實跑轉紅 |
| AC-07 | ✅ | team protocol 明文 Assignee 只填角色，禁止 Claude／Codex 供應商角色 |
| AC-08 | ✅ | installer 實際同步 10 項後，dry-run 新增 0、更新 0、待合併 0 |
| AC-09 | ✅ | 完整 pytest 189 passed；precheck 8/8；BACKLOG 重生 |

## 2. 工單只記穩定需求

新模板有四欄：

```text
Task Profile
Required Capabilities
Data Class
Execution Override
```

全部留 `—` 是正常情況。`task_profiles.json::task_type_defaults` 把現有 Task Type 映射到
task profile；沒有在 Python 寫供應商分支。實測一張只有 `Task Type: queue_backend` 的舊工單，
`route --task-file ... --explain` 顯示：

```text
task_profile = implementation_local
task_profile_source = Task Type mapping：queue_backend
selected_profile = codex-cli
```

`manual_user` 映射為 null，明確表示使用者工單不進 agent route。Task Type、Assignee 與既有工單
都不需改名；Claude／Codex 只存在 execution profile。

## 3. 審查檔保存本次決策

新增 `_REVIEW_TEMPLATE.md`，路由區要求保存：

- task profile 與來源；
- capability／data／execution overrides；
- 選中的 execution profile；
- 每個候選的 Availability、score 與排除理由；
- probe 時間、過期 cache、handoff。

模板只留必要欄位，不要求貼 credential 或完整敏感 probe stdout。team protocol §2.3 同步規定：
實際路由證據進 review，**不寫回 Assignee**。

## 4. Precheck 第八項的邊界

新增 `Agent runtime 版控政策與秘密邊界是否合法`，只讀：

- `.agent/agent-runtime.json`；
- 版控中的 adapter manifests；
- portable `.codex/config.toml` 與 project `.mcp.json`；
- 未結案工單的 runtime 欄位。

它**不讀** XDG state、HOME、登入、訂閱或 `.agent/agent-runtime.local.json`。負向對照把 local
override 寫成損壞非 JSON，甚至含 `access_token=local_only`，八項仍全綠；這證明 CI 不會因
某個人的本機狀態不同而變色。`${GITHUB_TOKEN}`／`${API_KEY}` 佔位也不誤判。

## 5. 四組負向對照

| 違規 | 實測訊息重點 |
|---|---|
| `Task Profile: typo_profile` | 未知 task profile，指出工單路徑 |
| `scope=forever` | scope 必須是 single／round／project |
| policy `cloud_policy=forbid` + `profile=codex-cloud` | 共享政策禁止 cloud，工單卻強制 cloud |
| policy `access_token=ghp_not_a_real_token` | 疑似把 access_token 值寫進版控，改用 `${VAR}` |

另有 `profile=codex-clii`，精確回報 Execution Override 引用未知 profile。舊工單完全沒有新欄位
仍合法，避免為了新流程追改歷史紀錄。

## 6. Role／Assignee 沒有被供應商污染

模板測試與 team protocol 共同保證：Assignee 的值仍是 `backend-developer` 等 skill 角色；
Claude、Codex、App、CLI、Cloud 只在 route／review 證據裡。換訂閱或中途換 agent 不必改工單
負責角色，也不會讓 BACKLOG 多出供應商佇列。

## 7. 驗證

- precheck／routing／registry 目標測試：**45 passed**；
- 收緊 local-state 邊界後目標測試：**40 passed**；
- 完整 `uv run pytest --basetemp=/dev/shm/agent-team-kit-040-full-2`：**189 passed**；
- `python3 .agent/scripts/precheck.py`：**8/8 全綠**；
- `./install.sh . --upgrade --dry-run`：新增 0、更新 0、待合併 0；
- `git diff --check`：通過。

## 8. 留給後續工單

- 041 用新 init／doctor／route 安全遷移本 repo 的真實 Claude、Codex 與 GitHub 設定；
- 042 用新 review template 驗證雙向交接，並確認路由證據足以重建決策。
