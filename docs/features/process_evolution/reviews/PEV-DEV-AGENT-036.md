# [Review: PEV-DEV-AGENT-036] installer 雙入口種子檔與模板升級

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | 首次安裝同時產生 `AGENTS.md`／`CLAUDE.md`，manifest 涵蓋 kit 全檔 |
| AC-02 | ✅ | 雙入口都列種子，使用者修改後 upgrade 原文保留、不產生 `.new` |
| AC-03 | ✅ | upgrade 缺少新種子時不補檔，輸出 `請執行 migrate`；dry-run 零寫入 |
| AC-04 | ✅ | `install.sh::is_seed_file()` 與 `test_升級保留種子檔` 同步加入 `AGENTS.md` |
| AC-05 | ✅ | `.gitignore` 排除 repo-local runtime state，`.codex/` 採 portable allowlist |
| AC-06 | ✅ | 安裝完成訊息改成執行 `agent_runtime.py init`，不再只叫使用者填 CLAUDE |
| AC-07 | ✅ | 四種實跑輸出見 §2；installer 測試 18 passed |
| AC-08 | ✅ | 完整閘門見 §3 |

## 2. 四種情境實跑

```text
A 首次安裝： AGENTS.md + CLAUDE.md
B 種子保留： # 使用者 AGENTS / # 使用者 CLAUDE / 待合併 0 = True
C 舊專案 dry-run： migrate 提示 = True / 零寫入 = True
D 無 manifest： 原文保留 = True / 另存 .new = True / 待合併 = True
```

情境 C 是本張最重要的邊界。一般新增出貨檔 upgrade 會自動補上，但新 `AGENTS.md` 是種子入口；
在舊專案尚未拆分共同／Claude 專屬規則前直接補入，會立即改變 agent 行為。因此 upgrade
只保留最新版 `.agent/templates/AGENTS.md` 並提示 migrate，不把種子檔當一般新增檔。

## 3. 驗證

- `uv run pytest tests/test_install.py` → **18 passed**；
- `uv run pytest --basetemp=/dev/shm/agent-team-kit-036-full` → **153 passed**；
- `python3 .agent/scripts/precheck.py` → **7/7 全綠**；
- `./install.sh . --upgrade --dry-run` → 新增 0、更新 0、待合併 0。
- `git diff --check` 通過。

## 4. 版控邊界

新專案 `.gitignore`：

- 忽略 `.agent/agent-runtime.local.json`；
- 先忽略 `.codex/*`；
- 只放行 `.codex/config.toml` 與 `.codex/actions/**`。

這是檔案層 allowlist，不代表其中內容自動安全；`035` 的 adapter／秘密掃描與 `040` 的 precheck
仍會檢查內容。現有專案的 seed `.gitignore` 不由 upgrade 覆蓋，`041` 再安全遷移。

## 5. 未處理

- `agent_runtime.py init` 由 `037` 實作；本張先把 installer 的提示與生命週期邊界接好。
