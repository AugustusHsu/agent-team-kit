# 多代理執行標準 (Agent Runtime)

> 本標準回答「同一張工單此刻由哪個代理、在哪個執行面完成」。
> 角色職責仍以 `.agent/skills/` 為準，工單生命週期仍以
> `.agent/resources/team_protocol.md` 為準；本檔不取代兩者。

## 1. 先分清四個維度

| 維度 | 問題 | 例子 |
|---|---|---|
| **Role** | 需要哪種專業判斷 | `tech-lead`、`backend-developer` |
| **Task Profile** | 這次工作需要哪些能力與風險限制 | `implementation_local` |
| **Execution Profile** | 哪個產品、執行面與工具集合 | `claude-code-cli`、`codex-app-worktree` |
| **Availability** | 這個 execution profile 此刻能不能用 | `verified`、`degraded`、`unavailable`、`unknown` |

**不得把供應商名稱寫進 `Task Type` 或 `Assignee`。** `Assignee` 永遠是角色；Task Type
是既有佇列分類。Claude、Codex 或未來供應商只出現在 execution profile。
使用者換訂閱或換產品時，工單的角色與業務語意不應跟著改名。

## 2. Task Profile 宣告能力，不宣告廠商

Task profile 的唯一正版是
`.agent/resources/agent_runtime/task_profiles.json`。它包含：

- `schema_version`：格式版本；不支援的版本必須明確失敗；
- `capabilities`：高階能力詞彙與說明；
- `data_classes`：資料敏感度由低到高的順序；
- `profiles`：任務輪廓、必備／選配能力與預設風險政策。

能力使用**高階語意**，例如 `repo_write`、`isolated_workspace`、`visual_interaction`。
「有 Bash 3.2」或「有某個 plugin」只是 execution profile 證明高階能力的證據，
不應成為每張工單都要知道的詞彙。工具版本改動時，只更新 adapter 的證據，不改任務語意。

### 2.1 初始八種輪廓

| ID | 典型工作 | 主要硬性能力 |
|---|---|---|
| `design_research` | DN、架構比較、外部證據 | repo 讀取、來源查證、長 context |
| `implementation_local` | 程式與文件實作 | repo 讀寫、shell、測試 |
| `parallel_long_running` | 多工單、背景任務 | 隔離工作區、長時間執行、交接 |
| `review_security` | code review、安全審查 | 唯讀 diff、新鮮 context、證據紀錄 |
| `test_verification` | 測試、負向對照 | shell、原始輸出保真、可重跑 |
| `visual_interactive` | UI、瀏覽器、桌面應用 | 視覺互動、使用者在場 |
| `automation_batch` | CI、批次、固定流程 | 非互動模式、結構化輸出、timeout |
| `external_integration` | GitHub、MCP、Connector | 外部連線、權限與資料政策 |

新增輪廓只新增 registry 資料；**不得為每個輪廓新增 Python enum 或供應商 if/else**。
新增高階能力時必須同時補詞彙說明與至少一個可證明它的 adapter，但不需修改既有輪廓。

## 3. 資料與外部連線分開判斷

資料分成四級：`public`、`internal`、`sensitive`、`restricted`。registry 的順序就是
風險順序，不由程式碼另寫第二份。

每個 task profile 分別宣告：

- `cloud_policy`：`allow`／`conditional`／`forbid`；
- `connector_policy`：`allow`／`conditional`／`forbid`；
- `default_data_class`：未被工單覆寫時採用的資料級別。

「可上 cloud」不等於「可把資料送給外部 Connector」。兩個政策必須獨立檢查；
任一為 `forbid`，路由器都不得以「目前只剩這個候選」為由偷偷放寬。

## 4. 路由順序不可交換

候選依下列順序處理：

1. **硬性能力**：缺一項立即排除；
2. **安全與資料政策**：cloud、Connector、資料級別不符即排除；
3. **當下可用性**：依仍在有效期內的 probe 判斷；
4. **專案偏好**：只能在合格候選之間作用；
5. **成本、速度與 context**：採簡單、可解釋的層內評分；
6. **使用者覆寫**：最後決定權屬使用者，但不得偽裝成自動決策。

候選為零時回報「缺少哪些能力或政策衝突」，不得靜默選 `unknown`、禁止的 cloud，
或只有登入 metadata 卻未證明功能的 profile。

## 5. Availability 是有時效的證據

| 狀態 | 意義 |
|---|---|
| `verified` | 功能探針成功且尚未過期 |
| `degraded` | 部分能力失效，仍能執行受限任務 |
| `unavailable` | 已確認登入、權限、額度或工具失效 |
| `unknown` | 未驗證、已過期或目前不可觀察 |

訂閱名稱、使用者填的到期日與 `auth status` 都只能當提示。最小功能探針才是主要證據；
兩者矛盾時保留兩份證據並標 `degraded`，不得任選較順眼的一邊。

即使只啟用一個供應商也要跑路由：候選數量變成一，不代表它自動具備任務所需能力。

## 6. Codex CLI 是基線，App 是增強層

預設流程以 **Claude Code CLI 與 Codex CLI** 都能承載的本機能力作可攜基線。
Codex App Local／Worktree、Codex Cloud、瀏覽器、Apps／Plugins 等能力建成額外
execution profiles；有就加入候選，沒有也不使基本開發流程失效。

因此文件不得寫成「使用 Codex 就一定有 managed worktree」或「沒有 App 就不能路由」。
同一供應商的 CLI、App Local、App Worktree 與 Cloud 是不同 profiles，分別驗證。

模型與 reasoning 名稱同樣留在 provider adapter／使用者設定。Task profile 只描述
`fast`、`balanced`、`deep` 等需求級別，避免模型改名或訂閱變動迫使所有工單改寫。

## 7. 覆寫與證據

工單由 Task Type 取得預設 task profile，只在例外時寫 capability／data override。
使用者覆寫預設只對**單次路由**有效；整輪或專案永久覆寫必須明示 scope 與到期條件。

實際路由證據寫進審查載體，至少包含：

- task profile 與所有 override；
- 硬性能力與資料政策；
- 選中的 execution profile；
- 其他候選的排除理由；
- probe 的時間與是否使用過期 cache；
- 是否發生中途交接。

不得只寫「這次用 Codex」；那無法重建決策，也無法判斷換成 Claude 是否等價。

## 8. 中途失效

執行中失效採「保存 → 重探 → 重新路由」：保留 Task ID、branch／worktree、HEAD、
工作區狀態、已完成 AC 與最後可信驗證，再停用失效 profile 並重新排序。

換 execution profile **不重開工單、不更換 Assignee**。有外部副作用的工作預設停下等待
使用者；只有純讀、無外部副作用的子任務可由專案政策允許自動接手。

## 9. Registry 相容性

- `schema_version` 不支援：明確失敗，不猜測；
- 未知欄位：失敗並指出 JSON 路徑，避免拼字錯誤被靜默忽略；
- 重複 profile ID：失敗；
- 引用未知 capability／data class／policy：失敗；
- 新增 profile：向後相容；
- 刪除或重新命名既有 profile：屬破壞性變更，必須提供 migrate 對映。

CI 驗證版控中的 schema 與引用；**不驗使用者是否登入、訂閱是否有效或 Connector 是否連上**。
後者是本機生命週期狀態，不得讓同一個 commit 在不同人的 CI 得到不同結果。

## 10. 設定分層與初始化

三層資料各自只回答一種問題，不得把本機登入狀態寫回共同政策：

| 層 | 路徑 | 是否版控 | 內容 |
|---|---|---|---|
| 共享政策 | `.agent/agent-runtime.json` | ✅ | portable project ID、啟用／偏好 profiles、資料與外連政策 |
| 使用者狀態 | `${XDG_STATE_HOME:-~/.local/state}/agent-team-kit/agent-runtime.json` | ❌ | profile 可用性、短證據摘要、驗證與到期時間 |
| 專案本機覆寫 | `.agent/agent-runtime.local.json` | ❌ | 此機器停用／偏好的 profiles 與較嚴格的本機政策 |

共享政策裡的 `project_id` 跟著 repo，所有 worktree 因而使用同一 identity；使用者狀態則可在
同一台機器跨 worktree 共用。override **不能**改 `project_id`，也不能加入 registry 不存在的
profile。三層任一 JSON 損壞、schema 版本不支援或欄位拼錯，工具都應指出檔案與 JSON path，
不得以預設值靜默帶過。

首次設定：

```bash
# 互動模式
python3 .agent/scripts/agent_runtime.py init

# 可重跑的非互動模式
python3 .agent/scripts/agent_runtime.py init --non-interactive \
  --verified-profile codex-cli --prefer-profile codex-cli

# 大量專案可改用版控外的 JSON 設定檔
python3 .agent/scripts/agent_runtime.py init --non-interactive --config <path>
```

`init` 成功的最低門檻是至少一個能滿足 `implementation_local` 的本機 profile 尚在
`verified` 有效期內。重跑若會改變已存在的共享政策，只產生 `.new` 候選；既有候選也不
覆寫，而是遞增尾碼。缺少 `AGENTS.md`／`CLAUDE.md` 時同樣只從 `.agent/templates/` 產生
候選，避免在使用者確認前改變 agent 行為。

## 11. Doctor、refresh 與無副作用探針

`doctor` 重新檢查選定 profile；`refresh` 只重跑已過 TTL 或用 `--probe` 指定的項目。
兩者預設都是 offline，只有明示 `--online` 才能執行唯讀網路探針：

```bash
python3 .agent/scripts/agent_runtime.py doctor --offline
python3 .agent/scripts/agent_runtime.py doctor --online --profile codex-cli
python3 .agent/scripts/agent_runtime.py refresh --probe codex_login_status
```

每個 profile 的 `install`／`auth`／`functional` 證據分開保存，再彙總成 Availability。
若 auth metadata 說未登入，但最小功能探針成功，兩份證據都留下並標 `degraded`；不得刪掉
其中一份來製造整齊結論。state 只存固定摘要與錯誤分類，不存完整 stdout／stderr。

GitHub 也不是一個布林值：

| 能力 | 自動探針 | 為何分開 |
|---|---|---|
| Git remote read | `git ls-remote`（online read） | 只證明 remote 可讀 |
| Git remote write | 人工確認 | 健康檢查不得用 push 製造寫入 |
| GitHub API read | `gh api user` | 與 git transport 是不同憑證路徑 |
| GitHub API write | 人工確認 | 不以開 issue／PR 作探針 |
| Codex Cloud Connector | 人工確認＋TTL | App 目前未必有可觀察 API |
| automated review | 人工確認＋TTL | 屬 repo／平台設定，不能由 SSH 成功推出 |

人工確認使用 `--manual-profile ID=STATUS` 或 `--manual-integration ID=STATUS`，同樣有 adapter
定義的到期時間。所有探針禁止 push、開 PR、傳訊息、修改 Connector 或購買／續訂。

## 12. Route、explain 與失效重路由

基本路由與單一候選解釋：

```bash
python3 .agent/scripts/agent_runtime.py route --task-profile implementation_local
python3 .agent/scripts/agent_runtime.py explain \
  --task-profile implementation_local --execution-profile codex-cli
```

route 的資料流固定為 §4 的六階段。每個 execution profile 都保留：是否合格、Availability、
排除理由、分數與每個加減分因子。硬性能力或政策不合格時 `score` 必須是 `null`，不能讓偏好
或高分把它救回來。初始 registry 尚未提供可比較的實際價格／latency／context 數值，因此三者
明列 `metadata_unknown: 0`；**誠實的零分比憑供應商印象偷排更可解釋**。

Availability 的例外只有一個：fresh cache 到期後，純本機唯讀任務可把 `unknown` 留在候選中，
但扣分；有 repo write、shell、測試、外部連線或長時間副作用的任務一律排除 unknown。

使用者可用 `--override-profile` 在**合格候選**間改選；覆寫不能繞過硬能力或資料政策。預設
scope 是單次。`round`／`project` 必須同時寫 `--override-expires-at`（時間或明確事件），
避免永久偏好在訂閱失效後仍靜默作用。

中途失效時 route 接受原 Task ID、branch、HEAD、AC、驗證與 failure type，排除失效 profile
後產生 handoff record。工單與 Assignee 不變。即使使用者開啟自動接手，也只有**純讀且無外部
副作用**的任務可以自動；其餘輸出 `requires_user_confirmation: true`。

人類輸出適合當下判讀；`--json` 是工單與審查載體保存決策證據的介面。零候選回傳非零狀態，
並逐一列出缺少能力／政策／可用性原因，不選 unknown 或違規 cloud 填空。

## 相關文件

- `.agent/resources/agent_runtime/task_profiles.json`——任務輪廓唯一正版
- `.agent/resources/agent_runtime/adapters/*.json`——execution profile manifests
- `.agent/resources/agent_runtime/*schema.json`——政策、狀態與 registry 的格式契約
- `.agent/scripts/agent_runtime.py`——初始化與 runtime 管理介面
- `.agent/resources/team_protocol.md`——角色、工單狀態與 commit 閘門
- [git_workflow.md](git_workflow.md)——分支、隔離與合併拓撲
- [skill_conventions.md](skill_conventions.md)——角色 skill 的撰寫邊界
