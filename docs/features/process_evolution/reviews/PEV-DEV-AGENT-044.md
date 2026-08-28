# [Review: PEV-DEV-AGENT-044] 實作工單 DAG、欄位與 wave 驗證

## 2026-08-28 第五輪 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-044`
**Round：** `ROUND-001`
**Base：** `983cada7d8c01e0dc249063ed651758edc33e866`
**Head：** `f077f49aab170b8687084765e5030f96ae4f5fab`
**Fresh-context reviewer：** `gpt-5.6-sol`／`xhigh`；五行 fidelity probe 原樣通過。

前四輪 findings 除 R4-F-03 的相鄰邊界外都已關閉；第五輪只剩混合破折號路徑仍可能
fail open，因此本 target 不得合併進 round。

### 第五輪 AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | 六欄模板、舊工單與只缺 External Effects 的過渡格式通過 |
| AC-02 | ✅ | DAG 錯誤與確定性 topo／wave／blocks 通過 |
| AC-03 | ✅ | Round 欄位、真實 commit、集合、結構與重複歸屬驗證通過 |
| AC-04 | ❌ | `—/src` 與 `—/docs/api.md` 仍被當成合法 Write Scope／Contract |
| AC-05 | ✅ | Parallel Change 與 Change Set schema 通過 |
| AC-06 | ❌ | 既有測試未咬住混合破折號路徑 |
| AC-07 | ✅ 開發分支證據 | 91 passed、precheck 8/8 與 9/9、BACKLOG 一致、diff check 通過；正式安裝入口仍留待 047 |

### 第五輪阻擋 finding

#### R5-F-01 — P1／混合破折號路徑仍可通過來源驗證

- **File／line：** `kit/.agent/scripts/scan_backlog.py:161-174,267-287`
- **Claim：** path validator 只拒絕整個 token 恰為破折號；`—/src`、`—/docs/api.md`
  仍能 exit 0、`errors=[]`，違反破折號空值必須是整欄唯一內容的規則。
- **Recommended fix：** Write Scope／Contract 都拒絕空值 sentinel 出現在非整欄空值路徑中，
  並各補真實 Markdown 與 precheck 回歸。

### 第五輪客觀證據

| 驗證 | 結果 |
|---|---|
| Head 目標兩檔／完整套件 | 91 passed／232 passed、4 baseline failed |
| Base 完整套件 | 196 passed、4 baseline failed |
| 401＋Head tests | 83 passed、8 failed |
| root／kit precheck | 8/8、9/9 |
| graph／BACKLOG／diff | 兩次逐字一致且 errors=[]／原位一致／通過 |
| R5-F-01 最小重現 | exit 0、errors=[] |

四個全套失敗在 Base／Head 完全同形，均為未變更的 `test_check_versions.py` archive 路徑問題。
審查前後工作 repo 均乾淨且 HEAD 未漂移；所有取證產物只在 `/tmp`。

### 第五輪修正紀錄（Developer）

- **R5-F-01：已修正。** path validator 拒絕 Unicode 破折號出現在路徑任何位置，也拒絕
  `-/src` 這類獨立 ASCII 空值路徑段；一般含連字號檔名仍合法。
- **回歸：** Write Scope 覆蓋 `—/src`、`–src`、`-/src`，Contract 覆蓋
  `—/docs/api.md`；precheck 以兩張真實 Markdown 工單同時驗證 `TBD` 與混合破折號。
- **規範同步：** `parallel_development.md` 與 ADR-001 已明定破折號空值不得成為路徑的一部分。
- **修正後證據：** 目標兩檔 91 passed；完整套件 232 passed、4 個相同 baseline failures；
  root／kit precheck 8/8、9/9；graph 兩次一致、`errors=[]`、拓撲與候選不變；BACKLOG 原位
  重建一致；`git diff --check` 通過。新測試套用第五輪 Head 為 89 passed、2 failed。

修正後正式結論待第六輪 fresh-context review 固定新 head 後獨立重跑。

## 2026-08-28 第四輪 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-044`
**Round：** `ROUND-001`
**Base：** `983cada7d8c01e0dc249063ed651758edc33e866`
**Head：** `4010b54262ffd9324dc070caa8fbd0645b1a14d2`
**Fresh-context reviewer：** `gpt-5.6-sol`／`xhigh`；五行 fidelity probe 原樣通過。

第三輪 R3-F-01、F-03、F-04 的原始案例已關閉，但 Round validity 只做到 pair-local，另有
literal Contract、路徑 placeholder 與 Change Set 單值格式三個新缺口，因此本 target
仍不得合併進 round。

### 第四輪 AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | 六欄模板、舊工單與只缺 External Effects 的過渡工單相容行為正確 |
| AC-02 | ✅ | unknown／self／duplicate／cycle 與確定性 topo、wave、reverse blocks 均通過 |
| AC-03 | ✅ | Round 必備欄位、真實 commit、集合大小、非法列與表格結構均會報錯 |
| AC-04 | ❌ | 無效成員未污染整輪、literal 子路徑與 placeholder Write Scope 仍可能產生 candidate |
| AC-05 | ❌ | 完整三階段可共用非法的混合破折號 Change Set 而零錯誤通過 |
| AC-06 | ❌ | 既有 85 tests 使用真實檔案／Git、零 mock，但未覆蓋本輪四個邊界 |
| AC-07 | ✅ 開發分支證據 | 85 passed、precheck 8/8 與 9/9、BACKLOG 一致、diff check 通過；正式安裝入口仍留待 047 |

### 第四輪阻擋 findings

#### R4-F-01 — P1／Round validity gate 仍是 pair-local

- **File／line：** `kit/.agent/scripts/scan_backlog.py:988-998,1043-1048`
- **Claim：** 同 Round 的 A 工單來源非法時，合法 B／C 仍能成為 candidate；工單重複歸屬時
  也只污染後讀到的 Round。
- **Recommended fix：** 所有 manifest 讀完後做全域 validity／membership pass；任一 member
  或 Parallel Change 無效就阻擋整輪全部配對，重複歸屬污染所有涉入 Round。

#### R4-F-02 — P1／literal 子路徑錯認為涵蓋父層 Contract

- **File／line：** `kit/.agent/scripts/scan_backlog.py:666-670`
- **Claim：** `docs/contracts/api.md/child` 被視為提供 `docs/contracts/api.md`，即使 Contract
  不在 base 且 provider 沒有寫該完整路徑。
- **Recommended fix：** 非 glob scope 只接受 exact；目錄涵蓋必須有明確表示，禁止 child→parent。

#### R4-F-03 — P1／placeholder 可被當成合法 Write Scope

- **File／line：** `kit/.agent/scripts/scan_backlog.py:154-167,244-257`
- **Claim：** `TBD`、`N/A`、`None` 及未引用的混合破折號能通過 repo path 驗證，可能放行候選；
  Contract 使用相同 parser，也有相同來源風險。
- **Recommended fix：** 路徑 token 明確拒絕 placeholder 與混合空值；只有整欄精準破折號代表無值。

#### R4-F-04 — P2／混合破折號 Change Set 可成為合法群組

- **File／line：** `kit/.agent/scripts/scan_backlog.py:291-296,799-807`
- **Claim：** 三階段全部使用 `—、auth-v2` 時仍 `errors=[]`，沒有單值 identifier schema。
- **Recommended fix：** Change Set 只接受單一識別碼，拒絕 placeholder、分隔清單與引用殘留。

### 第四輪客觀證據

| 驗證 | 結果 |
|---|---|
| Head 目標兩檔／完整套件 | 85 passed／226 passed、4 baseline failed |
| Base 完整套件 | 196 passed、4 baseline failed |
| 舊 Head＋Head tests | c70：81 passed、4 failed；98bb：78／7；8be：67／18 |
| root／kit precheck | 8/8、9/9 |
| graph／BACKLOG／diff | 兩次逐字一致且 errors=[]／原位一致／通過 |

四個全套失敗在 Base／Head 完全同形，均為未變更的 `test_check_versions.py` archive 路徑問題。
審查前後工作 repo 均乾淨且 HEAD 未漂移；所有取證產物只在 `/tmp`。

### 第四輪修正紀錄（Developer）

- **R4-F-01：已修正。** 全部 manifest 驗證完成後，再將 invalid task／Parallel Change 傳播至
  所屬 Round；重複歸屬同步標記先後所有 Round，invalid round 的全部 pair 都有
  `invalid_planning_source` blocker。
- **R4-F-02：已修正。** literal Write Scope 只接受與 Contract 完整相等；目錄統一明示為
  `path/**`，沿用錨定完整路徑的 glob matching。
- **R4-F-03：已修正。** Write Scope／Contract path validator 明確拒絕 `TBD`、`N/A`、`None`
  與混合破折號 token，並由 graph／precheck fail closed。
- **R4-F-04：已修正。** Change Set 新增單值 identifier schema；非法值會標記 task 與整輪無效，
  不再建立 Parallel Change 群組。
- **規範同步：** 兩份模板、`parallel_development.md` 與 ADR-001 已同步 `path/**`、單值
  Change Set、placeholder 與整輪污染規則。
- **修正後證據：** 目標兩檔 91 passed；完整套件 232 passed、4 個相同 baseline failures；
  root／kit precheck 8/8、9/9；graph 兩次一致、`errors=[]`、拓撲與候選不變；BACKLOG 原位
  重建一致；`git diff --check` 通過。新測試套用第四輪 Head 為 83 passed、8 failed，第三輪
  80／11，第二輪 77／14，第一輪 67／24。

修正後正式結論待第五輪 fresh-context review 固定新 head 後獨立重跑。

## 2026-08-27 第三輪 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-044`
**Round：** `ROUND-001`
**Base：** `983cada7d8c01e0dc249063ed651758edc33e866`
**Head：** `c70c515cd6c9b026a3ef490ea6b2c2394625749d`
**Fresh-context reviewer：** `gpt-5.6-sol`／`xhigh`；五行 fidelity probe 原樣通過。

前兩輪 parser、Round schema、External Effects 與 Parallel Change 修正均可重現；第三輪仍找到
三個會誤放行並行候選的 fail-open，另有一項工單審查備註不合第 1 層協議，因此本 target
不得合併進 round。

### 第三輪 AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | 六欄模板、舊工單與只缺 External Effects 的過渡工單相容行為正確 |
| AC-02 | ✅／下游有 finding | DAG 來源錯誤會回報，但錯誤工單仍可能進候選，併入 AC-04 的 R3-F-02 |
| AC-03 | ❌ | 一般非法資料列會失敗，但重複 header／separator 被略過 |
| AC-04 | ❌ | invalid source 與不匹配的 ancestor glob Contract provider 仍可能產生 candidate |
| AC-05 | ✅ | phase、expand→migrate、contract direct dependencies 與混合破折號正負向案例通過 |
| AC-06 | ❌ | 真實 Markdown／Git、零 mock，但缺本輪三個 fail-open 的回歸 |
| AC-07 | ✅ 開發分支證據 | 目標兩檔 83 passed、BACKLOG 重建一致、diff check 通過；正式安裝入口仍留待 047 |

### 第三輪阻擋 findings

#### R3-F-01 — P1／Round 重複 header／separator 被當成合法結構

- **File／line：** `kit/.agent/scripts/scan_backlog.py:542-557`
- **Claim：** parser 在封閉集合任何位置看到 header 或 separator 都直接略過，沒有驗證唯一性與順序；
  插入第二組表格結構後 graph 仍 `errors=[]`、kit precheck 仍 9/9。
- **Recommended fix：** 使用狀態式 parser 驗證唯一 header 與其後唯一 separator，並補 graph／precheck 回歸。

#### R3-F-02 — P1／來源已報錯仍輸出 parallel candidate

- **File／line：** `kit/.agent/scripts/scan_backlog.py:830-836,975-1010,1042-1048`
- **Claim：** errors 與候選推導沒有共用 validity gate；非法 Blocked By 或 Parallel Change
  雖讓 graph exit 1，同一對工單仍可能出現在 `parallel_candidates`。
- **Recommended fix：** 傳遞 per-task／per-round validity；任何相關來源無效時只列
  `invalid_planning_source` blocker。

#### R3-F-03 — P1／glob 靜態前綴錯誤證明 Contract 已由 ancestor 提供

- **File／line：** `kit/.agent/scripts/scan_backlog.py:626-638,693-711`
- **Claim：** `docs/r3-contracts/*.md` 只因與 `docs/r3-contracts/api.json` 共用靜態前綴，
  就被錯認為已提供 opening base 中不存在的 Contract。
- **Recommended fix：** Contract provider 必須以錨定完整路徑的 glob 實際匹配；副檔名、深度或
  brace 表示無法證明匹配時 fail closed。

#### R3-F-04 — P2／工單 Code Review 備註超出允許結構

- **File／line：** `docs/features/process_evolution/tasks/PEV-DEV-AGENT-044.md:64-79`
- **Claim：** CHANGES REQUESTED 的工單備註另含 Developer 修正論述，超出 `team_protocol.md`
  §2.3 允許的結論、客觀指標與單行 findings。
- **Recommended fix：** 工單只保留三段摘要，完整判讀與修正紀錄移至本 review artifact。

### 第三輪客觀證據

| 指令／檢查 | 98bb／舊負向對照 | Head |
|---|---:|---:|
| 全套 archive | 219 passed、4 baseline failed | 224 passed、4 baseline failed |
| 目標兩檔 | 78 passed | 83 passed |
| rejected implementation＋Head tests | 8be：67 passed、16 failed | 83 passed、0 failed |
| precheck／graph／BACKLOG／diff／skill | — | 8/8、9/9／確定且 errors=[]／一致／通過／有效 |

完整套件四項失敗與第二輪相同，均為未變更的 `test_check_versions.py` archive 路徑問題。
審查者全程未修改檔案、ref 或工作樹。

### 第三輪修正紀錄（Developer）

- **R3-F-01：已修正。** Round parser 改為狀態式驗證；header、separator 必須各唯一且依序
  位於資料列前，重複、錯位與缺漏都使整份 manifest 無效。
- **R3-F-02：已修正。** DAG、Parallel Change 與 Round 驗證會累積 per-task／per-round
  validity；相關 pair 一律加入 `invalid_planning_source` blocker，不得成為候選。
- **R3-F-03：已修正。** ancestor Write Scope glob 改為錨定完整 repo-relative 路徑實際匹配；
  副檔名、深度或 brace 表示不匹配時都維持 Contract 未就緒。
- **R3-F-04：已修正。** 工單 Code Review 備註只保留結論、客觀指標與四條單行 finding；
  開發判讀與修正結果集中於本檔。
- **規範同步：** `parallel_development.md` 與 ADR-001 已同步 Round 結構唯一性、來源 validity
  gate 及 Contract glob 完整匹配規則。
- **修正後證據：** 目標兩檔 85 passed；完整套件 226 passed、4 個與 reviewed head 相同的
  baseline failures；root／kit precheck 8/8、9/9；`git diff --check` 通過。新測試套用第三輪
  reviewed head 為 81 passed、4 failed，第二輪為 78 passed、7 failed，第一輪為
  67 passed、18 failed。

修正後正式結論待第四輪 fresh-context review 固定新 head 後獨立重跑。

## 2026-08-27 第二輪 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-044`
**Round：** `ROUND-001`
**Base：** `983cada7d8c01e0dc249063ed651758edc33e866`
**Head：** `98bb488fa28e307451d8db0ffc4519ba1c3db3bf`
**Fresh-context reviewer：** `gpt-5.6-sol`／`xhigh`；五行 fidelity probe 原樣通過。

第一輪 F-03 已關閉，F-01、F-02、F-04 的主要路徑已修正；但對抗測試仍找出三個
fail-open 邊界，因此本 target 不得合併進 round。

### 第二輪 AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | 六欄已同步模板與主要規範；舊格式與過渡五欄可讀，缺 External Effects 不取得並行資格 |
| AC-02 | ❌ | 一般非法依賴會失敗，但 `—、TBD` 被空值短路成無依賴 |
| AC-03 | ❌ | schema、branch、真實 commit 與合法 closed-set 已驗證；非法非空成員列仍被略過 |
| AC-04 | ❌ | 一般 glob、非法路徑、External Effects 與 peer Contract 會阻擋；backtick 外路徑及混合空值仍可能 false positive |
| AC-05 | ✅ | migrate transitive ordering 與 contract direct dependency 已有正負向測試 |
| AC-06 | ❌ | 現有測試形狀合規，但缺少本輪三個 fail-open 邊界的回歸 |
| AC-07 | ✅ | 目標測試、BACKLOG 暫存重建與 diff check 通過；根目錄正式安裝入口仍留待 047 |

### 第二輪阻擋 findings

#### R2-F-01 — P1／破折號前綴可藏掉依賴或外部作用域

- **File／line：** `kit/.agent/scripts/scan_backlog.py:129-171,249-267`
- **Claim：** `is_explicit_none()` 接受任何以破折號開頭的值，`—、TBD` 與
  `—、deploy:prod` 都被視為明確無值。
- **Recommended fix：** explicit none 只接受整欄精準破折號；與任何 token 混用都要報錯。

#### R2-F-02 — P1／Write Scope／Contract 靜默丟棄 backtick 外路徑

- **File／line：** `kit/.agent/scripts/scan_backlog.py:137-145,239-247,548-573`
- **Claim：** `` `src/a.py`、tests/shared.py `` 只保留 backtick 內項目，可能把實際重疊誤判為 disjoint；
  Contract 也會藏掉尚未進 base 或正在被 peer 修改的契約。
- **Recommended fix：** 兩欄改用 strict parser，保存 residual 並由 graph／precheck 報錯。

#### R2-F-03 — P1／Round 封閉集合忽略非法資料列

- **File／line：** `kit/.agent/scripts/scan_backlog.py:483-509,840-866`
- **Claim：** Round 表格加入 `| TBD | ... |` 後仍 `errors=[]`，非法非空資料列沒有進驗證模型。
- **Recommended fix：** 只略過 header／separator；每張資料列第一欄都要完整匹配 Task ID，
  否則留下 `invalid_round_member_token`。

### 第二輪客觀證據

| 指令／檢查 | Base／負向對照 | Head |
|---|---:|---:|
| 全套 archive | 196 passed、4 baseline failed | 219 passed、4 baseline failed |
| 目標兩檔 | 55 passed | 78 passed |
| rejected head＋新 tests | 67 passed、11 failed | 78 passed、0 failed |
| precheck／graph／diff／skill | — | 9/9／errors=[]／通過／有效 |

完整套件四項失敗在 Base 與 Head 相同，均為未變更的 `test_check_versions.py` archive 路徑問題。
審查者全程未修改檔案、ref 或工作樹。

### 第二輪修正紀錄（Developer）

- **R2-F-01：已修正。** `is_explicit_none()` 只接受整欄精準破折號；依賴、External Effects、
  Change Set 與 Phase 的混合空值都保留實際 token 並產生明確錯誤。
- **R2-F-02：已修正。** Write Scope／Contract 共用 strict parser；backtick 外殘留、非法
  repo-relative path 與 Contract glob 都保存為 invalid token，graph／precheck fail closed。
- **R2-F-03：已修正。** Round 集合只略過 header／separator，其餘資料列第一欄必須完整匹配
  Task ID；非法非空列產生 `invalid_round_member_token`。
- **Dogfood：已修正。** 經使用者同意擴大 Write Scope，將 043 的 ADR 範圍／Contract 與 047
  的根目錄同步範圍等義正規化；DAG 仍為 `043 → {044,045} → 046 → 047`，候選仍為空。
- **規範同步：** 破折號與 backtick 清單規則已同步 `parallel_development.md`、ADR-001 與
  Scrum Master skill；skill quick validation 通過。
- **修正後證據：** 目標兩檔 83 passed；完整套件 224 passed、4 個與 reviewed head 相同的
  baseline failures；root／kit precheck 8/8、9/9；graph 兩次逐字一致且 `errors=[]`；BACKLOG
  暫存原位重建一致；`git diff --check` 通過。舊 rejected head 套用新測試為 67 passed、16 failed。

修正後正式結論待第三輪 fresh-context review 固定新 head 後獨立重跑。

## 2026-08-27 第一輪 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-044`
**Round：** `ROUND-001`
**Base：** `983cada7d8c01e0dc249063ed651758edc33e866`
**Head：** `8be71ed21b2bd61cbfed4768dcbe8ebd7be95bb2`
**Fresh-context reviewer：** `gpt-5.6-sol`／`xhigh`；五行 fidelity probe 原樣通過。

## 1. AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | 兩份模板均含五欄；五欄全無的舊工單可相容讀取，partial-field 會明確拒絕 |
| AC-02 | ❌ | 一般 unknown／self／duplicate／cycle 與穩定推導正確，但非空非法 `Blocked By` token 會被靜默丟棄或截成另一個 ID |
| AC-03 | ❌ | 唯一 ID、2～5 張、未知、重複歸屬與 direct closed-set 已驗證；缺 Integration Review Target 或不存在的 40 位 opening base 仍通過 |
| AC-04 | ❌ | 根目錄 glob 與實際檔案可能重疊卻被判 disjoint；外部副作用只靠標題／Task Type heuristic，無來源證據仍可能放行 |
| AC-05 | ❌ | phase、階段數量與 contract 涵蓋 migrate 已驗證，但 migrate 不依賴 expand 仍通過 |
| AC-06 | ✅ | 測試使用 `tmp_path` 真實 Markdown 與 Git、零 mock；隔離負向對照證實新增 13 項測試會讓舊實作轉紅 |
| AC-07 | ✅ | 兩個目標測試檔 68/0、BACKLOG 原位重建一致、`git diff --check` 通過；隔離全套的 4 項 baseline 環境失敗非本 diff 引入 |

## 2. 重大瑕疵清單

### F-01 — P1／依賴 token 可被靜默改寫

- **File／line：** `kit/.agent/scripts/scan_backlog.py:137`
- **Claim：** `parse_task_ids()` 只搜尋 regex 子字串，`nonsense` 變成空依賴，
  `MOD-DEV-BE-099x` 被截成 `MOD-DEV-BE`，會錯算 wave、blocks、closed-set 與並行候選。
- **Evidence：** `parse_task_ids("nonsense") == []`；
  `parse_task_ids("MOD-DEV-BE-099x") == ["MOD-DEV-BE"]`。
- **Recommended fix：** 先拆 token，再以正式 Task ID regex 完整匹配；任何非法 token 產生 planning error。

### F-02 — P1／並行候選可產生 false positive

- **File／line：** `kit/.agent/scripts/scan_backlog.py:437-471,541-552`
- **Claim：** `*.md` 與 `README.md` 被誤判不相交；未知第三方帳號／網路寫入工作只因未命中
  標題關鍵詞就被視為可隔離。
- **Evidence：** `scopes_are_definitely_disjoint(["*.md"], ["README.md"]) == True`；
  `queue_backend`＋repo-local scope 的「更新第三方帳號設定」回傳可隔離。
- **Recommended fix：** glob 無非空可證靜態前綴或路徑表示模糊時 fail closed；外部副作用必須有
  權威來源證據，不能由未命中 heuristic 推導安全。

### F-03 — P1／Parallel Change 可錯序

- **File／line：** `kit/.agent/scripts/scan_backlog.py:584-623`
- **Claim：** migrate 沒有依賴 expand 時仍無錯誤，expand 與 migrate 可落在同一 wave，違反
  `expand → migrate → contract`。
- **Recommended fix：** 每張 migrate 的 transitive dependencies 必須包含唯一 expand；補錯序負向測試。

### F-04 — P1／Round Manifest schema 與 opening base 驗證不足

- **File／line：** `kit/.agent/scripts/scan_backlog.py:657-669`
- **Claim：** 刪除必備 Integration Review Target 後仍 `errors=[]`；不存在的 40 位 hex 也被接受。
- **Recommended fix：** 要求 Integration Review Target 欄位存在；opening base 必須以 argv-list
  `git cat-file -e <sha>^{commit}` 驗證為 repo 內 commit object。

## 3. 客觀驗證

| 指令／檢查 | 變更前／負向對照 | 變更後 |
|---|---:|---:|
| 全套測試 | base：196 passed、4 failed | head：209 passed、4 failed |
| 目標兩檔 | base implementation＋head tests：55 passed、13 failed | 68 passed、0 failed |
| `python3 kit/.agent/scripts/precheck.py` | — | 9/9，exit 0 |
| process_evolution graph | — | exit 0，`errors: []` |
| BACKLOG 重建 | — | `/tmp` 原位重建後 `cmp` exit 0 |
| `git diff --check <base>..<head>` | — | exit 0 |
| git_workflow／CHECKS integrity | — | 1 passed |
| Scrum Master `quick_validate` | — | `Skill is valid!` |

隔離全套的四個失敗在 base 與 head 完全相同，皆為未變更的 `test_check_versions.py` 在 archive
環境解析 `/tmp/docs/standards/...`；不歸因於本 diff，但該環境下不宣稱全套完全綠燈。

## 4. 架構優化與建議

- Round branch 建議完整驗證 `feature/{topic}`，不可接受空 topic。
- Write Scope 應先正規化 POSIX 路徑，拒絕 `..`、空 segment 與模糊表示。
- `different_wave` 是四項條件外的額外保守限制；應明示候選為同 wave 配對。
- precheck 可在單次執行快取 planning view，避免重建兩次。
- 四個既有 `check_versions` archive 環境失敗應另案處理。

審查者全程未修改檔案、ref 或工作樹。本 target 不得合併進 round；修正後須固定新 head 重審。

## 5. 修正紀錄（Developer）

- **F-01：已修正。** `Blocked By` 改為 token 完整匹配；backtick 清單外的殘留文字也會失敗。
- **F-02：已修正。** root glob、`..`、空 segment 與模糊路徑全部 fail closed；經使用者同意新增
  `External Effects` 第六來源欄位，缺欄、非法、重疊／父子作用域不得並行，並移除標題／Task Type
  heuristic。同 wave peer 修改另一工單引用的 Contract 也會阻擋候選。
- **F-03：已修正。** 每張 migrate 的 transitive dependencies 必須包含唯一 expand。
- **F-04：已修正。** Round 必須保存 Integration Review Target，branch 必須有非空 topic，
  opening base 必須是 repo 中存在的 commit object。
- **規範同步：** 六欄語意已同步 `parallel_development.md`、ADR-001、Git workflow、兩份模板與
  Scrum Master skill；skill quick validation 通過。
- **修正後證據：** 目標兩檔 78 passed；完整套件 223 passed；precheck 9/9；
  `git diff --check` 通過。隔離舊 head `8be71ed…` 套用新測試為 67 passed、11 failed。

修正後正式結論待第二輪 fresh-context review 固定新 head 後獨立重跑。
