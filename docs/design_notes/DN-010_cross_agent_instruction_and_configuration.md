# [DN-010] 跨代理入口與設定分層

**🚥 狀態 (Status):** 🎓 Graduated
**📅 建立 (Created):** 2026-08-26
**🔗 依賴 (Depends on):** DN-001（本檔的格式與畢業條件）；DN-009（供應商／執行面／可用性的名詞與邊界）
**📌 來源 (Origin):** 使用者指令（2026-08-26）——確定混用 Claude Code 與 Codex，要求預設開發流程同時支援兩者，且未來可加入其他廠商
**🤝 姊妹篇 (Sibling):** DN-009（多代理能力路由）；DN-011（初始化、健康檢查與生命週期）

> 🎓 **已畢業（2026-08-26）→ `PEV-DEV-AGENT-035`、`036`、`041`。**
> 使用者同意依 §4 建議裁定；本檔凍結，不再更新。

## 1. 問題陳述

目前 kit 的專案入口、種子檔與維護義務全部以 Claude Code 為前提：

- `kit/CLAUDE.md` 是唯一入口模板；
- `install.sh::is_seed_file()` 只保留 `CLAUDE.md`；
- 安裝完成訊息只要求填 `CLAUDE.md`；
- `team_protocol.md` 的專案第 2 層也直接指向 `CLAUDE.md`。

切換到 Codex 後，根目錄已出現一份未追蹤的 `AGENTS.md`，但它不是受控遷移：內容幾乎是
`CLAUDE.md` 的複本，只把兩處種子檔名稱改成 `AGENTS.md`；實際安裝器仍認 `CLAUDE.md`。
若直接 commit，兩份文件會從第一天就對同一件事給出互斥答案。

同時出現的未追蹤 `.codex/` 也混了三種不同性質：Codex shell policy、Claude 的
`ANTHROPIC_BASE_URL`，以及寫死個人家目錄的 headroom hook。把整個目錄一律版控或一律忽略，
都會把「可共享的專案設定」與「只能留在本機的個人狀態」綁在一起。

## 2. 已查證的事實

### 2.1 兩邊的入口載入機制不同

| 執行者 | 原生專案入口 | 已知能力 |
|---|---|---|
| Codex | `AGENTS.md`／`AGENTS.override.md` | 由 repo root 往目前目錄逐層載入，可設定 fallback 檔名 |
| Claude Code | `CLAUDE.md`／`.claude/CLAUDE.md` | 會自動載入，並支援 `@path` 匯入其他文件 |

因此「只留 `CLAUDE.md`，期待 Codex 自己找」不是預設可攜方案；「兩份全文各自維護」則會產生漂移。

### 2.2 現行 repo 的實際落差

| 檔案／機制 | 現況 | 風險 |
|---|---|---|
| `install.sh:79` | 種子檔只有 `CLAUDE.md` | 新專案沒有受管理的 Codex 入口 |
| `tests/test_install.py` | 只驗證 `CLAUDE.md` 保留 | 就算 `AGENTS.md` 被升級覆蓋也不會轉紅 |
| `kit/CLAUDE.md` | 全文以 Claude 的 context 成本與命令描述 | 不能直接改名當通用模板 |
| 根目錄 `AGENTS.md` | 未追蹤、與安裝器說法衝突 | 目前不應 commit |
| `.claude/settings.local.json` | 個人專案設定，已忽略 | 分層正確，但沒有跨代理總覽 |
| `.codex/config.toml` | 未追蹤，設定 Claude proxy 變數 | 供應商設定跨層污染 |
| `.codex/hooks.json` | 未追蹤，含個人絕對路徑 | 換機器即失效，不可直接出貨 |

### 2.3 `.codex/` 不是天然的「全部本機」或「全部共享」

Codex App 的 Local Environment 設定可以放在專案根目錄 `.codex` 並納入版控，讓團隊共享
setup 與 actions。另一方面，CLI 的使用者設定、登入狀態、絕對路徑與個人 hook 不應跟 repo 走。
所以判準必須看**內容與用途**，不能只看目錄名。

### 2.4 GitHub 也有多個彼此獨立的連線

至少要分開記錄：

- git remote 使用的 SSH／HTTPS 能力；
- GitHub CLI 的 API 身分與權限；
- Codex Cloud／Code Review 的 GitHub Connector；
- 未來可能加入的 Claude GitHub Action／Connector。

本機 SSH 正常不代表 cloud Connector 正常；公開 repo 可讀也不代表 API 已登入。

## 3. 已定調的設計

### 3.1 設定分三層

| 層 | 是否版控 | 放什麼 | 不放什麼 |
|---|---|---|---|
| **共同專案層** | ✅ | 跨代理都必須遵守的專案規則、能力需求、路由政策 | token、訂閱狀態、個人路徑 |
| **供應商轉接層** | 視內容 | 入口檔、可攜的 project settings、供應商專屬指路 | 另一家供應商的環境變數 |
| **使用者執行層** | ❌ | 登入、訂閱／額度觀察、個人 hook、絕對路徑、暫時停用 | 團隊共同規格 |

「專案偏好 Codex」屬共同專案層；「我今天的 Claude Max 到期」屬使用者執行層。

### 3.2 共同規則只能有一份可編輯真相

commit 閘門、文件權威、測試指令與安裝實例等跨代理規則，不得在 `AGENTS.md` 與
`CLAUDE.md` 各自手改一份。可以有多個入口，但只能有一個共同內容來源；其餘入口是 adapter。

### 3.3 供應商專屬內容不得滲入共同層

下列內容應留在各自 adapter 或使用者執行層：

- Claude 的 `ANTHROPIC_BASE_URL`、Claude 專屬 hook 與全域記憶路徑；
- Codex App Local Environment、Codex hook／plugin 與 App-only actions；
- 只有某個執行面能理解的權限、sandbox、model／reasoning 設定。

共同層只能描述需求，例如「shell 輸出必須保真」，不能假設所有執行者都用 headroom。

### 3.4 憑證永不由 kit 管理

kit 只記環境變數名稱、所需 scope、功能探針與設定位置；token／OAuth refresh token／SSH 私鑰
留在供應商原生憑證庫或使用者的 secrets 檔。任何可提交的設定只能引用變數，不含值。

### 3.5 GitHub 能力按用途拆開

路由不得只判斷 `github=true`。至少要分成：

- `git_remote_read`／`git_remote_write`；
- `github_api_read`／`github_api_write`；
- `github_codex_cloud`；
- `github_automated_review`。

每一項有自己的 probe、scope 與資料外送邊界。

### 3.6 現有未追蹤檔案先凍結

在本 DN 畢業前：

- 不 commit 目前的 `AGENTS.md`；它對種子檔的描述已與程式碼矛盾；
- 不 commit 目前的 `.codex/`；其中含供應商跨層與個人絕對路徑；
- 不用「先複製、以後再整理」製造第二份共同真相。

## 4. 待決事項

| # | 待決 | 選項 | 建議 |
|---|---|---|---|
| 4.1 | 共同內容的唯一真相放哪 | `AGENTS.md`／中立檔再生成雙入口／雙份＋一致性測試 | **`AGENTS.md` 為共同入口，`CLAUDE.md` 以 `@AGENTS.md` 匯入並補 Claude 專屬內容**。反方：把通用概念放在 Codex 命名檔，需以沙盒驗證 Claude 的實際載入結果 |
| 4.2 | `AGENTS.md`／`CLAUDE.md` 是否都列種子檔 | 都是／只保留共同入口／改由初始化器管理 | 兩份都是專案接手的輸出，但模板更新另放可升級來源，由 DN-011 的 migrate 處理 |
| 4.3 | 模板放哪 | `kit/` 根目錄／`.agent/templates/`／生成器內嵌 | 建議可升級的 `.agent/templates/`，避免種子檔凍結後永遠收不到新版結構 |
| 4.4 | `.codex/` 的版控邊界 | 全忽略／全版控／allowlist | **allowlist**；只提交可攜的 project environment／actions，個人 config 與 hook 留本機 |
| 4.5 | `.claude/` 的版控邊界 | 沿現況／與 Codex 統一目錄 | 沿供應商原生 scope；共享用 `.claude/settings.json`，個人用 `.claude/settings.local.json` |
| 4.6 | 跨入口一致性怎麼驗 | byte-identical／必備規則集合／不驗 | 驗「必備規則集合」；adapter 必然有差異，逐字相同會阻止合理的供應商專屬內容 |
| 4.7 | 未來第三家供應商怎麼加入 | 修改核心 schema／新增 adapter manifest | 新增 adapter manifest；共同層不應知道所有廠商名稱 |
| 4.8 | secrets 路徑是否統一 | 一個 kit secrets 檔／各供應商原生／混合 | 憑證維持原生；只有 kit 自己新增的跨供應商秘密才進共同 secrets 檔 |
| 4.9 | GitHub Connector 是否初始化必選 | 必選／依執行面選配 | 選配；本機開發不該因 cloud Connector 缺席而失敗，只有選到 cloud profile 才是硬前提 |

> ✅ **裁定（2026-08-26，使用者）：** 4.1～4.9 全數採建議欄：`AGENTS.md` 是共同入口，
> `CLAUDE.md` 匯入它並只補 Claude 專屬內容；兩者都是種子檔；可升級模板放
> `.agent/templates/`；`.codex/` 採 allowlist；`.claude/` 沿原生 scope；一致性驗必備規則集合；
> 第三家以 adapter manifest 擴充；憑證維持供應商原生；GitHub Connector 依執行面選配。

## 5. 畢業去向（畢業時才填）

屬 **D（改流程／基礎建設）**：

| 工單 | 落點 |
|---|---|
| `PEV-DEV-AGENT-035` | 雙入口模板與 Claude／Codex adapter manifests |
| `PEV-DEV-AGENT-036` | installer 種子檔、模板升級與安裝測試 |
| `PEV-DEV-AGENT-041` | 本 repo 的安全遷移與 GitHub／Codex 專案設定 |

**AC 可寫性驗證：** 以 `035` 為例，可驗證共同規則只存在 `AGENTS.md`、`CLAUDE.md`
使用 `@AGENTS.md`、adapter 不含 token／絕對路徑、第三個 adapter 不需修改核心 schema。
**使用者簽核：** ✅ 2026-08-26。
