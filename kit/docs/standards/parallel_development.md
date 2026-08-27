# 並行開發與工作輪次標準

> 本檔是多工單排程、所有權、工作輪次與兩層審查的**流程正版**。
> Git 指令與平台適配見 [git_workflow.md](git_workflow.md)；工單狀態與角色交接見
> [team_protocol 指路檔](team_protocol.md)。三者分工，不互相建立第二份規則。

## 1. 適用範圍與核心不變式

多人開發包含單人開發，因此只有一套流程：單張工單使用基本層；同一目標有 2～5 張相關工單時，
才增加短命工作輪次。供應商、模型、PR 平台與 worktree 工具都不是流程語意的一部分。

以下不變式不可由平台或執行者自行降級：

1. 一張工單只寫正向硬依賴與自己的寫入範圍；wave、反向 blocks 與並行候選均由來源資料推導。
2. 共用契約未進入本輪 base、Write Scope 重疊或外部副作用不可隔離時，不得並行。
3. 一張工單一條 Task ID 分支；多工單輪次另有一條 `feature/{topic}` 整合分支。
4. 所有進入共享分支的合併都保留 merge commit；PR／MR 只承載審查、CI 與權限。
5. 工單與輪次正式審查都固定在不可變 Review Target；head 改變即失效。
6. 語法合併不是驗收。多工單輪次必須驗證「當下主線＋輪次」後才能進 panel 與最終合併。

## 2. 來源資料模型

### 2.1 工單欄位

| 欄位 | 唯一語意 | 不得拿來做什麼 |
|---|---|---|
| `Blocked By` | 正向硬依賴的 Task ID；無則 `—` | 不手寫反向 `blocks`、wave 或 `[P]` |
| `Write Scope` | 本工單可寫的檔案／目錄／glob | 不取代專案級長期風險登記 |
| `External Effects` | 外部寫入作用域的 `category:resource`；明確無外部寫入填 `—` | 不從標題、Task Type 或未列出關鍵詞推測安全 |
| `Contract` | 已位於本輪 base 的第 1 層共用契約路徑；無則 `—` | 不指向未合併分支或 DN |
| `Change Set` | Parallel Change 三階段共用識別；不用則 `—` | 不當 Epic 或 Round ID |
| `Phase` | `expand`、`migrate`、`contract`；不用則 `—` | 不新增同名 Task Type |

舊工單沒有原五欄仍合法；已採原五欄但沒有 `External Effects` 的過渡工單也可讀，
但外部副作用視為未知，不能取得並行資格。新建或重新規劃的工單必須填齊六欄；
`External Effects: —` 是「明確沒有外部寫入」，與缺欄的 unknown 不同。`Assignee` 仍是專業角色，
執行者由 [agent_runtime.md](agent_runtime.md) 的能力路由決定。

六欄的破折號空值必須是**整個欄位的唯一內容**；`—、TBD`、`—、實際值` 等混合表示一律無效。
清單只要使用 backtick，所有 token 都必須放在 backtick 內，外部只能有分隔符與空白；任何殘留
文字都視為來源資料不完整，precheck 必須 fail closed，不能靜默丟棄後繼續推導。

### 2.2 Round Manifest

多工單輪次以 `docs/development/rounds/{RoundID}[_slug].md` 為唯一載體；Round ID 全域遞增，
從 `ROUND-001` 起。manifest 至少保存：

- 一個清楚目標、`feature/{topic}` branch 與 40 字元 opening base SHA；
- 封閉的 2～5 張既有 Task ID；工單不重複保存 Round ID；
- Integration Review Target；
- 當下主線＋輪次的 QA 證據、panel raw findings、reconciliation 與必要的人為裁定。

manifest **不手寫** wave、反向 blocks 或彙總狀態。介面可顯示由工單 DAG 重算的快照，
但必須標明是衍生視圖，衝突時回到工單與 manifest 的來源欄位。
封閉集合表格中除 header／separator 外，每個資料列的第一欄都必須完整匹配 Task ID；非法或
非空未知列不得略過，否則 manifest 不再是可驗證的封閉集合。header 與 separator 都只能
各出現一次、依序位於第一筆資料列之前；重複、錯位或缺漏都使整份 manifest 無效。

## 3. 排程與拆解

### 3.1 DAG 與並行放行

開輪前先驗證 Task ID 存在、無自我依賴、無重複邊且整圖無循環。兩張工單只有在以下四項
**全部成立**時才可同時活躍：

1. DAG 之間沒有先後邊；
2. `Write Scope` 不重疊；
3. 共用 `Contract` 已存在於 opening base 或已由前置工單合併進輪次，且沒有同 wave peer 正在修改；
   前置工單以 glob 宣告 Write Scope 時，必須由錨定完整路徑的 glob 實際匹配 Contract，只有
   靜態前綴、路徑深度不符或含無法明確解讀的表示都不算已提供；
4. 兩張工單都有 `External Effects` 來源證據，且網路寫入、部署、migration、帳號或其他
   外部寫入作用域可證明互不重疊；`—` 代表明確沒有外部寫入。

外部作用域使用不含 glob 的 `category:resource` opaque key，例如 `deploy:staging`、
`account:vendor/project`；相同作用域或父子作用域視為重疊。不同 Epic／模組只能當低耦合提示，
不是放行條件。工單、Parallel Change 或所屬 Round 只要有任何來源驗證錯誤，該 Round 的
相關配對都不得列入並行候選；缺欄、格式不合法或任何一項無法判定時，預設排序執行。

### 3.2 執行中發現新依賴

原工單維持 `In Progress`，只停止受影響範圍，branch／worktree 原地保留：

- 仍屬原目標、Write Scope 與 owner：修正原工單 AC／Outputs 後繼續；
- 超出 Write Scope、需要新角色或顯著擴張：開前置工單並回填 `Blocked By`；
- AC 仍寫不出：開 DN，不開內容模糊的工單；
- 會讓本輪超過五張或改變目標：停止擴張，交由使用者重新規劃。

引用同一 Contract 或命中受影響 Write Scope 的活躍工單同步暫停；其餘工單可繼續。

### 3.3 Parallel Change

破壞性介面變更拆成三張普通工單，共用 `Change Set`，依序為：

1. `expand`：新舊介面並存；
2. `migrate`：消費者逐一遷移，可有多張；
3. `contract`：移除舊介面，其 `Blocked By` 必須涵蓋全部 migrate 工單。

開 expand 的同時就建立 contract；contract 初始為 `Pending`。不可把三階段塞進同一張工單，
也不可為它們新增 Task Type。

### 3.4 競爭式開發

只在方案互斥、優劣事前不確定且客觀評判方式能在開工前凍結時使用。候選共用同一組
test／benchmark／eval，且不得含不可逆副作用、安全政策、migration、合規或純主觀評判。

預設最多兩個候選；第三個需使用者明示同意。候選只做到可比較的 spike，共同機械驗證後，
只有暫定贏家進完整審查。落選 branch 與評估紀錄保留到使用者同意取消／回收。

## 4. 所有權與隔離

### 4.1 兩層所有權

- 工單 `Write Scope`：本輪動態、排他的寫入所有權。
- `docs/development/overlap_zones.md`：專案長期熱點與風險級別，由專案維護、kit 升級保留。

Epic 不擁有檔案。Write Scope 重疊預設不並行，改由單一 owner 排序，或先開契約工單。
確實無法避免時，panel 先縮小風險，使用者只在輪次整合點裁定一次；安全政策、公開 API、
migration 等關鍵區即使是單一 owner，仍保留最終人工閘門。

### 4.2 Worktree 與 rerere

同一輪有兩張以上工單**同時活躍**時，每條活躍 Task ID branch 使用獨立 worktree；只有一張
活躍工單時不為形式建立。建立 worktree 前必須先通過 §3.1 與所有權檢查。

工單合併進輪次後立即移除其 worktree，但 Task ID branch 保留到整輪驗證與主線合併完成；
退回時由同一 branch 重建。輪次收尾後 `git worktree list` 只能剩主工作目錄。

`git rerere` 只能由專案 repo-local 選用，不是 kit 預設；重用後仍須檢查 diff、重跑測試，
且不得版控 `.git/rr-cache`。

## 5. Git 拓撲與生命週期

### 5.1 啟用條件

- 單張工單：Task ID branch → 主線／既有整合線。
- 2～5 張相關工單：`feature/{topic}` 輪次 branch；每張 Task ID branch 從當時的輪次 head 建立。

輪次是一個目標與封閉工單集合，全部工單達 terminal 狀態即收尾，不是永久模組分支。
若工單有內容依賴，後一張只能在前置合併進輪次後才建立／更新 base；無依賴工單可從相同
opening base 平行開出。不得用「永遠堆疊後只合併最上層」取代明確 DAG。

### 5.2 合併與可讀歷史

所有進入共享分支的方向都使用 merge commit，不因 PR／MR 平台改用 squash 或 rebase merge：

- Task ID branch → round branch：round 的 `--first-parent` 一張工單一行；
- round branch → main：main 的 `--first-parent` 一輪一行；
- 單張 Task ID branch → main：main 的 `--first-parent` 一張工單一行。

每顆 task merge 訊息寫完整 Task ID；round merge 訊息寫 Round ID，Body 逐張列完整 Task ID。
branch ref 可在安全驗證後刪除，名稱與目的仍留在 merge commit。詳細指令見
[git_workflow.md](git_workflow.md) §6～§7。

### 5.3 主線同步事件

不設定「每 N 天 rebase」：

1. 開輪前同步最新主線並固定 opening base；
2. 主線出現必要且命中本輪 Write Scope／Contract 的變更時，停止受影響工單、評估後再適應；
3. 最終合併前，以當下主線建立 integration candidate 並完整驗證。

不必要的主線變更不打斷本輪；必要變更也不得由各工單任意各自 rebase，應在輪次層統一處理。

## 6. 驗證、退回與完成

所有工單通過窄審並合併進輪次後，由 `qa-automation-engineer`、`test_verification` profile
驗證「當下主線＋輪次」的整合候選。主線在驗證與 panel 通過以前保持不動。

- 可歸因到單張工單：該工單 `In Review` → `In Progress`，重建原 branch／worktree 修正；
- 跨工單互動：開 integration-fix，列出 Contract 與 Blocked By；超過五張就重新規劃；
- 未受影響的已審工單不重做，但任何 head 變更都依 §7.2 使相符層級的審查失效。

Task ID branches 在整輪通過前保留。多工單輪次中，工單窄審通過並合併進 round 後仍維持
`In Review`；整合候選通過 QA 後，由 round 上的一顆**審查前結案 commit**一次寫入各工單
`Done`／`Closed` 與 manifest 放行資料，然後固定 round Review Target。正式 APPROVED 後不得再改 head；
round merge 成功時，這些狀態才進入主線並生效。單張工單同理：結案 commit 必須包含在正式
Review Target 裡，不得在 APPROVED 後追加而使核可失效。

## 7. 兩層審查與 Review Target

### 7.1 審查層級

- 工單窄審：每張工單各自查 AC、Write Scope 與測試；沒通過不得合併進 round。
- 輪次 panel：只適用多工單輪次；整合後一次檢查契約、依賴、重疊區、語意衝突與 QA 結果。

使用者接收一份 round 統整報告。單張工單不為形式啟動 panel。

### 7.2 Fresh context 與不可變對象

任何能產生正式 `APPROVED` 的審查都必須與開發 context 隔離；同 session 換角色只能自查。
模型多樣性是可選加分，不是硬條件。

唯一正版為 `Review Target = base SHA + head SHA + Task/Round ID`。PR／MR 或 branch diff 只是介面。
head 改變時，對不上該 SHA 的核可失效：task head 改變重跑該工單窄審；round head 改變重跑
受影響 panel 面向。不得沿用「內容看起來差不多」但 target 不符的 verdict。

### 7.3 Panel 與 reconciliation

基線兩個獨立 fresh context：

1. `code-reviewer`：整合語意、Contract、依賴、Write Scope 與架構一致性；
2. 對抗驗證者：可重跑證據、錯誤路徑、回歸與負向對照。

命中安全、migration、公開 API 或關鍵 overlap zone 才加第三位風險專家。各成員取得相同 pinned
target 與必要第 1 層文件，先獨立完成；`code-reviewer` 在讀取其他 finding 前完成自己的 lane。

每筆 raw finding 至少包含 ID、severity、claim、file／line、可重跑 evidence、recommended verdict，
先寫入 Round Manifest。`code-reviewer` 再逐項 reconciliation：`accept|reject|duplicate|defer` 加理由；
所有 blocking finding 直接回查。證據衝突仍無法排解時適用矛盾暫停，交由使用者裁定。

## 8. 收尾檢查清單

輪次只有在以下全部成立時才可合併主線並關閉：

- 封閉工單集合全部 terminal，且沒有未記錄的新依賴；
- 當下主線＋輪次 QA 通過；
- pinned round panel 通過，blocking finding 全數 reconciliation；
- 關鍵 overlap zone 已取得最終人工裁定；
- round merge 訊息已取得當次使用者同意；
- merge 成功後 Task ID／round branches 都可用 `git branch -d` 安全回收；
- 所有 task worktree 已移除，BACKLOG 與 Round Manifest 已更新。
