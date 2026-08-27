# [DN-008] 審查的執行形態：panel 模式與 context 隔離

**🚥 狀態 (Status):** 🎓 Graduated
**📅 建立 (Created):** 2026-08-18
**🔗 依賴 (Depends on):** DN-001（本檔的格式）；[DN-005](DN-005_parallel_task_decomposition.md)（§2.1 的 panel 是它 §4「放大審查粒度」訴求的落點）；[DN-006](DN-006_branch_topology_and_isolation.md)（§4.2 的重疊區強制人工審查與 panel 方向相反，判準要一起定；隔離載體的選擇與它的合併點耦合）；[DN-009](DN-009_multi_agent_capability_routing.md)（panel 成員可來自不同供應商／執行面，需先有共同能力與可用性判準）
**📌 來源 (Origin):** 從 [DN-004](DN-004_skill_system_realignment.md) §3／§5 拆出（2026-08-18）。
原始來源：panel 為使用者對並行開發的訴求「需要人來判斷的部份可以放大審查粒度，減少人工審查的負擔」（2026-08-16）；
context 隔離原為 `BACKLOG.md` 冰箱「審查與開發拆 context」，2026-08-17 裁定拆兩半後併入 DN-004
**🤝 姊妹篇 (Sibling):** 無
**🎓 畢業去向 (Landing):** D（改流程／基礎建設）→ `PEV-DEV-AGENT-043`、`046`、`047`，見 §5

> 🎓 **已畢業（2026-08-27）→ `PEV-DEV-AGENT-043`、`046`、`047`。**
> 使用者簽核兩層審查、基線雙面向 panel、fresh context、不可變 Review Target 與 reconciliation；
> 本檔自此凍結，不再更新。
>
> **歷程**：2026-08-27 由 Seed 推進 Exploring，依 DN-001 §3.3 由 system-architect 推進、
> 不需簽核）。DN-005 已裁定工單窄審＋輪次 panel，DN-006 已裁定 overlap zone 的分級人工閘門，
> 原本阻塞本檔的兩項前置已解除；§4 開始比較 panel 切面、統整與隔離方案。
> 2026-08-27 使用者裁定 §4.1～4.8，待決事項歸零並完成畢業簽核。

> 📌 **為什麼從 DN-004 拆出來。** DN-004 處理的是「skill 內容與規範脫節」——
> 那是一個**當下就能修、不等任何人**的問題。本檔的兩節不同：panel 的成本模型
> 取決於並行度（DN-005），隔離的審查載體取決於分支拓撲與合併點（DN-006），
> 兩者都要等那對姊妹篇定案才比得出取捨。留在 DN-004 裡會讓一份修得動的 DN
> 被兩個修不動的問題卡住畢業。

## 1. 問題陳述

兩個問題共用同一個主詞：**審查該由誰、在什麼視野下做。**

- **執行形態**：現行是一份 skill、一個 agent、掃過全部面向。要不要改成多個窄面向 agent 並行。
- **視野**：審查者現在看得到開發者的完整推理鏈。要不要隔離、隔離到什麼程度。

兩者互相牽制——panel 若成立，「每個面向各自隔離還是共用一個審查 context」
就變成一個新問題，而它在單一審查者的形態下根本不存在。所以合在同一份 DN 裡比。

## 2. 既有事實

### 2.1 審查的執行形態（原 DN-004 §3）

現行 `code-reviewer` 是**一份 skill、一個 agent、掃過全部面向**——
正確性、安全性、風格、測試覆蓋、規範遵循全塞在同一次審查裡，
142 行的 skill 要同時扛這些關注點（2026-08-18 實測 `wc -l`）。

**panel 模式**是另一種形態：同一份程式碼，派出多個**關注面向不同、範圍更窄**的
審查 agent 並行跑，各自只看自己那一面，最後由父 agent 統整成一份報告。
Claude Code 原生支援並行 subagent；Codex App 也支援平行 chat、受管理 worktree 與 Handoff。
機制端不是單一障礙，真正待決的是：要哪些能力、是否允許異質 panel，以及當下哪個執行面可用。
前兩項由本檔裁定，最後一項交給 DN-009。

為什麼值得考慮：使用者對並行開發的訴求之一是
**「需要人來判斷的部份可以放大審查粒度，減少人工審查的負擔」**（DN-005 §4）。
panel 正是達成它的手段——人看的是統整後的單一報告，而不是 N 個面向的原始意見。

已知的取捨：

- **成本是 N 倍。** 一次審查變成 N 個 agent 各跑一次，token 與時間都乘上去。
  面向切幾刀是成本／品質的直接槓桿。
- **統整層是新的單點。** 父 agent 若在統整時漏掉某個 panel 成員的意見，
  那個面向等於沒審。原本單一 agent 沒有這個失效模式。
- **與重疊區的強制人工審查方向相反。** DN-006 §4.2 要求碰到高風險檔案時
  **強制人工介入**，panel 則是**減少人工介入**。兩者要能共存，
  判準必須寫清楚——大概是「panel 放大的是一般情況的粒度，重疊區是它的例外」。

### 2.2 審查與開發的 context 隔離（原 DN-004 §5）

2026-08-17 裁定把冰箱的「審查與開發拆 context」拆兩半：
**取證義務**（不得採信交付回報、一律回查程式碼）做法單一，已由
[PEV-DEV-AGENT-015](../features/process_evolution/tasks/PEV-DEV-AGENT-015.md) 落地；
**隔離機制**選項多、成本差距大，留在設計階段繼續比。

| 機制 | 隔離強度 | 成本 | 已知問題 |
|---|---|---|---|
| 同 session 換角色（**現況**） | 最低——開發者的推理鏈完整留在 context 裡 | 0 | 「自己審自己」，回報與證據同源 |
| subagent | 中——獨立 context window | 一次 agent 呼叫 | 提示由父 agent 給，能被無意間帶偏；回報只是摘要，父 agent 難以查核 |
| 獨立 session／從 diff 起手 | 高——只看得到 diff 與工單 | 需要人或腳本轉場 | 需要一個穩定的「審查載體」；本 repo 目前無 PR 流程 |
| 換模型 | 高——連推理偏好都不同 | 額外成本、可能不可得 | 與上一項正交，可疊加 |

## 3. 已定調的設計

**本節只放已經拍板、不會再翻的既有約束**，它們限制 §4 的選項，不是待決事項。

- **取證義務已落地，不重比。** 審查者不得採信交付回報，一律回查程式碼
  （PEV-DEV-AGENT-015，`team_protocol.md` §2.3）。任何隔離方案都必須讓審查者
  **拿得到可回查的原始碼**，只給摘要的方案一律不合格。
- ⚠️ **隔離之後，審查者讀到的 diff 可能是被壓縮過的版本——會。**
  [PEV-DEV-AGENT-017](../features/process_evolution/tasks/PEV-DEV-AGENT-017.md) 實測：
  表格與高度重複的結構會被中間層改寫，**表格周圍的散文可能整段消失且不留任何提示**，
  這一類損失連原文都沒被留存、救不回來。處置已於 2026-08-18 升格為
  `team_protocol.md` **§1.12（適用全角色的開工自檢）**，不再只是審查者的讀法紀律。

  **這對 §4 的選擇有直接影響**：隔離得越徹底（獨立 session、只看 diff），
  審查者手上的旁證越少，越沒機會察覺自己讀到的是殘缺版本——
  **隔離強度要跟「怎麼確認讀到的是原文」一起設計，不能只挑強度。**

- **審查採兩層，不重比要不要 panel。** DN-005 於 2026-08-27 經使用者裁定：
  每張工單先做窄範圍 AC／Write Scope／測試審查；全部併入工作輪次後，
  再做一次跨工單 panel。單張工單不為了形式硬開 round panel。
- **panel 不取代關鍵風險的人工裁定。** DN-006 於 2026-08-27 經使用者裁定：
  Write Scope 重疊預設不並行；例外由 panel 先縮小風險，人工判斷集中在輪次整合點；
  安全政策、公開 API、migration 等關鍵 overlap zone 即使只有單一 owner，仍保留最終人工閘門。

## 4. 選項與待決事項

| # | 待決 | 選項 | 建議 |
|---|---|---|---|
| 4.1 | 審查要不要改成 panel 模式 | 維持單一審查者／panel | **已裁定**：工單窄審＋輪次 panel；單張不硬開 panel |
| 4.2 | panel 面向怎麼切、切幾個 | 固定 N 人／依風險動態擴充 | **已裁定**：基線 2 面向，關鍵風險才加第 3 位專家 |
| 4.3 | panel 的統整層由誰擔任 | 父 agent／既有 `code-reviewer`／`tech-lead`／新角色 | **已裁定**：既有 `code-reviewer`，不新增角色 |
| 4.4 | 隔離強度要求多高？是否分級 | 同 session 換角色／所有正式審查 fresh context／依風險分級 | **已裁定**：所有能產生 APPROVED 的審查都與開發 context 隔離 |
| 4.5 | subagent 的回報要怎麼查核 | 摘要／原始 finding＋逐項 reconciliation | **已裁定**：原始 finding 落盤，blocking finding 全數回查並逐項處置 |
| 4.6 | 若採「從 diff 起手」，審查載體是 PR 還是分支 diff | 平台載體二選一／共同的不可變 Review Target | **已裁定**：base SHA＋head SHA＋Task/Round ID 為正版，PR／branch 只是介面 |
| 4.7 | panel 與隔離怎麼組合 | 每個面向各自隔離／共用一個審查 context | **已裁定**：各自 fresh context，先獨立審查、報告落盤後才統整 |
| 4.8 | panel（減少人工）與 DN-006 §4.2 重疊區（強制人工）怎麼共存 | — | **已裁定**：panel 先縮小風險，關鍵區在輪次整合點保留一次人工閘門 |

> 📌 4.1～4.3 屬 panel，4.4～4.6 屬隔離，4.7～4.8 是兩者的交界。
> **4.1 與 4.4 是入口**：它們沒答案之前，其餘各項都問不出所以然。

### 4.1～4.4 與 4.8 的裁定（2026-08-27）

- 輪次 panel 基線切成兩個面向：`code-reviewer` 負責跨工單契約、依賴、Write Scope 與
  架構一致性的**整合語意**，另一位審查者負責測試證據、錯誤路徑、回歸與負向對照的
  **對抗驗證**。碰到安全政策、migration、公開 API 或其他關鍵 overlap zone 時，
  才依任務風險加入第 3 位專家；不固定讓每輪成本升到三人以上。
- 統整責任留在既有 `code-reviewer`。不新增 panel coordinator 角色，也不交給負責設計的
  `tech-lead`；panel 成員需要什麼角色與 execution profile，仍由工單能力與 DN-009 runtime 路由。
- 所有能產生正式 `APPROVED` 的審查都必須使用與開發隔離的 fresh context。
  同 session 換角色只能算開發者自查，不能簽發正式 verdict。工單窄審與輪次 panel
  各自重新建立審查 context；不強制換模型，模型多樣性只在合格候選間作加分。
- panel 先把關鍵 overlap zone 的風險縮成一份統整結果；使用者只在輪次整合點判斷一次。
  這不取消 DN-006 為安全政策、公開 API、migration 保留的最終人工閘門。

### 4.5～4.7 的裁定（2026-08-27）

每位 panel 成員輸出結構化 finding，至少包含 ID、嚴重度、主張、檔案／行號、可重跑證據
與建議 verdict。原始 finding 必須先寫入版控內的 round review artifact，統整者不能只收到摘要。
`code-reviewer` 隨後產出 reconciliation matrix，逐項標示採納、否決、重複或延後及其理由；
所有 blocking finding 都要回查原始 diff 或重跑證據。成員意見衝突且證據無法排解時，
適用矛盾暫停，不得由統整者任選一邊。

審查對象的唯一正版是不可變的 `Review Target = base SHA + head SHA + Task/Round ID`。
有 PR／MR 時平台是操作介面，無平台時用同一組 SHA 產生 branch diff；兩者不得形成兩套證據語意。
head 一旦變動，對不上該 SHA 的 APPROVED 失效：工單 head 變動重跑該工單窄審，
round head 在 panel 後變動則重跑受影響的 panel 面向。可依 Write Scope 判定受影響面向，
但不得沿用一份對不上 target 的 verdict。

panel 成員各自使用獨立 fresh context，取得同一份 pinned Review Target 與必要第 1 層文件。
`code-reviewer` 先完成自己的整合語意判讀，其他成員同步完成各自面向；各份原始報告落盤後，
才開始 reconciliation，避免先看到別人的結論而產生錨定。round review artifact 一律版控；
依 DN-005 §5.8 的 2026-08-27 使用者裁定，raw findings、reconciliation 與整合驗證
追加在同一份 `docs/development/rounds/{RoundID}.md` Round Manifest，不另建第二份 round review 檔。

## 5. 畢業去向（畢業時才填）

屬 **D（改流程／基礎建設）**：

| 工單 | 落點 |
|---|---|
| `PEV-DEV-AGENT-043` | 並行開發標準中的兩層審查、Review Target 與 Round Manifest 證據 schema |
| `PEV-DEV-AGENT-046` | `code-reviewer` 協調、fresh-context APPROVED、raw findings 與 reconciliation 流程 |
| `PEV-DEV-AGENT-047` | head 失效、矛盾暫停、整合驗證與 panel 證據的端到端驗證 |

**AC 可寫性驗證：** 以 `046` 為例，可驗證同 session 自查不能產生正式 APPROVED；
base／head／ID 固定後才能建立審查結果，head 變動會使不相符 verdict 失效，且 blocking finding
都有 raw evidence 與 reconciliation 處置。
**使用者簽核：** ✅ 2026-08-27。
