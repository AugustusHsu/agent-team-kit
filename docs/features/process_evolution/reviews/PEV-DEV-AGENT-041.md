# [Review: PEV-DEV-AGENT-041] 安全遷移本 repo 的 Claude／Codex／GitHub 設定

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | `migrate --dry-run` 顯示 AGENTS／CLAUDE 兩份候選與 unified diff；前後 `git status` 完全一致，沒有 `.new` |
| AC-02 | ✅ | `AGENTS.md` 成為共同真相；`CLAUDE.md` 只剩 `@AGENTS.md`、Claude scope、MCP 與功能探針 |
| AC-03 | ✅ | `tests/test_agent_runtime_migrate.py::test_本_repo_雙入口保留必要規則且不含個人設定` 鎖住十項必要規則 |
| AC-04 | ✅ | 本 repo 不版控 `.codex/`；原有 proxy URL 與絕對 hook 已從專案本機設定移除 |
| AC-05 | ✅ | 使用者 2026-08-27 裁定不再使用 headroom；專案 hook、marker、proxy URL、現行入口與全域啟動設定均移除 |
| AC-06 | ✅ | doctor 實跑兩套 CLI、Git remote URL/read、GitHub SSH／API；Connector 與寫入能力維持 unknown |
| AC-07 | ✅ | `.agent/agent-runtime.json` 同時啟用 Claude Code、Codex CLI／App；三個本機 profile 最終皆 verified |
| AC-08 | ✅ | 現行入口與政策測試拒絕 token、cookie、private key、家目錄絕對路徑與供應商 proxy URL |
| AC-09 | ✅ | 完整 pytest 194 passed；precheck 8/8；installer dry-run 新增 0、更新 0、待合併 0 |

## 2. `migrate` 的安全邊界

`kit/.agent/scripts/agent_runtime.py:661` 新增 `migrate`：

- `--dry-run` 只回報來源、候選路徑與 unified diff，不寫工作區；
- 正式模式只寫 `<入口>.new`，永不覆寫 `AGENTS.md`／`CLAUDE.md`；
- 候選已存在且內容不同時遞增 `.new.2`；
- `--common-source` 可指定真正的共同規則來源；未指定時依序採 AGENTS、CLAUDE、模板；
- 舊專案只有 CLAUDE 時，先把全文保留成 AGENTS 候選，再產生精簡 Claude adapter。

本 repo 預覽實測：AGENTS diff 224 行、CLAUDE diff 160 行；兩份 candidate 都是 null，
預覽前後工作區清單相同。正式模式產生候選後才由人工接受、刪除不再需要的內容。

## 3. 雙入口遷移結果

共同規則集中在 `AGENTS.md`：指令、kit／安裝實例邊界、同步陷阱、跨代理政策、取證、
測試、commit 與 worktree。`CLAUDE.md` 只保留 Claude Code 會使用的 adapter，沒有重複
`uv run pytest`、push 閘門或 worktree 規則。

必要規則測試不是只比行數，而是逐項要求以下高風險句型仍存在：BACKLOG 正確指令、
工作區複製、安裝排除同步、已廢除規則表、runtime policy、秘密邊界、merge approval、
禁止自動 push 與 worktree cleanup。

## 4. headroom 移除裁定

041 原規格要求保留 headroom；使用者於執行中明確改為「不再需要」。成因工單尚未結案，
依 §1.8 直接修正本工單 AC-05，不另開 FIX。

已移除的**現行設定**：

- 主工作目錄 `.claude/settings.local.json` 的 SessionStart hook 與 `ANTHROPIC_BASE_URL`；
- 主工作目錄 `.codex/config.toml`、`.codex/hooks.json` 與 marker；
- 全域 Codex config 的 headroom MCP；
- shell 啟動時載入 proxy 與 `HEADROOM_PROTECT_TOOL_RESULTS` 的四行；
- 本 repo 共同入口內的產品、port、proxy 與回滾說明。

修改前的全域 Codex 與 shell 設定備份在 `/tmp/codex-config.toml.before-pev-041`、
`/tmp/bashrc.before-pev-041`。已結案工單、舊 review、已畢業 DN 仍依 §1.11 保留歷史證據；
它們不是現行設定，刪除反而會破壞稽核鏈。

## 5. Codex CLI 模型設定的真實故障

第一次 online doctor：Claude Code verified、Codex App verified，但 Codex CLI functional probe
回 `command_failed`。單獨重跑顯示全域預設仍是 `gpt-5-codex`，ChatGPT 帳號回 400：

```text
The 'gpt-5-codex' model is not supported when using Codex with a ChatGPT account.
```

用 `-m gpt-5.6-terra` 重跑立即得到 `AGENT_RUNTIME_PROBE_OK`，因此不是登入失效。
全域預設改為已實測可用的 `gpt-5.6-terra`、reasoning 保持 high；再以**無 model override**
重跑也通過。這份個人設定不進版控。

## 6. Doctor 與 GitHub 實測

`run_probe` 支援特定 probe 的成功 exit code；GitHub SSH 的成功握手依官方行為回 1，
因此仍須同時看到 `successfully authenticated` marker 才算 verified。最終結果：

| 類別 | 結果 |
|---|---|
| Claude Code CLI | verified |
| Codex CLI | verified |
| Codex App worktree | verified（本 session 人工確認） |
| Git remote URL／read | verified／verified |
| GitHub SSH／API read | verified／verified |
| Git／GitHub write | unknown（不以外部寫入當健康檢查） |
| Codex Cloud Connector | unknown（目前不可觀察） |

Connector 的 unknown 不被美化成 verified，也不阻擋已確認的本機流程。

## 7. 版控政策與秘密邊界

`.agent/agent-runtime.json` 啟用五個 execution profiles，偏好順序為 Codex App worktree、
Codex CLI、Claude Code CLI；cloud／connector 仍是 conditional。登入與探針結果只寫 XDG
state，不進 repo；`.agent/agent-runtime.local.json` 與整個 `.codex/` 由專案 `.gitignore`
排除。本 repo 目前沒有需要分享的 portable Codex project config，因此不為了「有檔案」而
提交空設定。

## 8. 驗證

- `tests/test_agent_runtime_migrate.py` + health：**13 passed**；
- 完整 `uv run pytest --basetemp=/dev/shm/agent-team-kit-041-full`：**194 passed**；
- `python3 .agent/scripts/precheck.py`：結案並重生 BACKLOG 後 **8/8**；
- `./install.sh . --upgrade --dry-run`：新增 0、更新 0、待合併 0；
- `git diff --check`：通過；
- `[平台相關]` 標記：9，未改變。

## 9. 留給後續工單

042 以這份 verified 狀態與新 review 格式，實跑 Claude → Codex 與 Codex → Claude 的雙向交接，
並驗證換代理不改 Assignee、工單或分支。
