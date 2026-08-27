# [Review: PEV-DEV-AGENT-035] 雙入口模板與供應商 adapter manifests

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | 共同規則在 `kit/AGENTS.md`；`kit/CLAUDE.md:3` 以 `@AGENTS.md` 匯入且沒有複製 commit 範例 |
| AC-02 | ✅ | 隔離目錄真實執行 Claude Code，回傳共同入口 marker，見 §2 |
| AC-03 | ✅ | 五個 manifests 均含 provider、surface、capabilities、三種 probe 與 TTL |
| AC-04 | ✅ | 測試以 `future-vendor` manifest 實跑，核心 schema／registry 不需修改 |
| AC-05 | ✅ | 自動掃描秘密值、家目錄絕對路徑與跨供應商環境變數 |
| AC-06 | ✅ | `AGENTS.md` 與 `CLAUDE.md` 分別寫明 `.codex/` allowlist、`.claude/` 原生 scope |
| AC-07 | ✅ | 必備規則集合只驗共同入口；Claude adapter 可保留 MCP／context 專屬段落 |
| AC-08 | ✅ | pytest 152 passed；precheck／BACKLOG 見 §5 |

## 2. Claude `@AGENTS.md` 真實載入

隔離目錄只有：

```text
AGENTS.md  → 要求輸出 AGENTS_IMPORT_OK_20260826
CLAUDE.md  → @AGENTS.md
```

執行：

```text
claude -p "Return only the project import marker from the shared project instructions."
AGENTS_IMPORT_OK_20260826
```

這不是只查文件語法；Claude Code 確實把共同入口送進該次請求。

## 3. Execution profiles

| Profile | Provider／Surface | 特別邊界 |
|---|---|---|
| `claude-code-cli` | Anthropic／CLI | 本機基線、Claude MCP 設定留 adapter |
| `codex-cli` | OpenAI／CLI | 本機可攜基線，不假設 App 能力 |
| `codex-app-local` | OpenAI／App Local | 視覺與 Connector 需人工確認 |
| `codex-app-worktree` | OpenAI／App Worktree | managed worktree／handoff 需人工確認 |
| `codex-cloud` | OpenAI／Cloud | GitHub Connector 與 cloud 權限另驗 |

App 能力列在 `manual_capabilities`，避免「manifest 有寫」被誤當成「這台機器已驗證」。

## 4. 設定分層

- `AGENTS.md`：供應商中立的共同真相；
- `CLAUDE.md`：Claude context、settings scope 與 MCP；
- execution profile manifest：能力宣告與 probe 名稱；
- 使用者登入、訂閱、hook、token、絕對路徑：不在上述任何可提交檔案。

`kit/AGENTS.md` 與 `.agent/templates/AGENTS.md` 都是出貨來源：前者是新安裝的種子初稿，
後者是未來 migrate 可比較的最新版模板。使用者只編輯根目錄種子檔，不改模板。

## 5. 驗證

```text
針對性測試：78 passed
完整測試：152 passed in 9.42s
install --upgrade --dry-run：待合併 0
```

precheck 在工單結案與 BACKLOG 重生後為 7/7。

## 6. 本 repo 的過渡狀態

升級在 worktree 根目錄產生通用的 `AGENTS.md` 種子初稿，本張將它與 manifest 一起保存，
使安裝實例自洽；但它**還不是本 repo 的最終入口**。主工作目錄另有使用者未追蹤草稿，
`PEV-DEV-AGENT-041` 必須用 migrate 比較並保留客製內容，再處理最終合併前的未追蹤檔衝突。
在 `041` 完成前不得把這份通用初稿當成遷移完成。

## 7. 未處理

- installer 的雙種子語意由 `036`；probe 真正執行由 `038`；本 repo 遷移由 `041`。
