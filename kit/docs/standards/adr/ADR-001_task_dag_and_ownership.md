# ADR-001：任務排程採 DAG 與雙層所有權

**狀態：** Accepted
**定案日期：** 2026-08-27
**影響範圍：** 工單拆解、並行排程、檔案所有權

## Context

Epic／模組只能表達分類，不能證明兩張工單之間沒有內容依賴、檔案衝突或外部副作用。
直接手寫 wave、`[P]` 與正反向依賴，又會讓同一事實存在多份、在新增依賴後漂移。

## Decision

工單只保存 `Blocked By`、`Write Scope`、`External Effects`、`Contract`、`Change Set`、`Phase`
六個來源欄位；wave、反向 blocks 與可並行集合由 DAG 推導。輪次內以 Write Scope 表達動態
排他所有權，專案另以 `overlap_zones.md` 保存長期熱點；Epic 不擁有檔案。

並行必須同時滿足 DAG 無邊、Write Scope 不重疊、Contract 已進 base 且沒有 peer 同時修改，
以及雙方都有可證互不重疊的 External Effects 來源。缺欄與不可判定都預設排序。
六欄的破折號空值只接受精準整欄值；清單使用 backtick 時不得留下未引用 token。Round 封閉
集合的每個資料列也必須完整匹配 Task ID，任何非法來源列都直接阻擋規劃圖。

## Rejected alternatives

- **依 Epic／模組直接並行**：無法捕捉設定、schema、路由等跨模組熱點。
- **只比檔案路徑**：不同檔案仍可能透過同一契約產生語意衝突。
- **手寫 `[P]`／wave／blocks**：正反向與衍生資料會在變更後不一致。
- **Epic 保存所有權**：永久分類無法表達每輪不同的實際寫入範圍。

## Consequences

開輪成本增加一次結構化檢查，但 wave 可重算、執行期新依賴有明確落點，且重疊預設會在
開工前轉為排序。舊工單沒有原五欄仍合法；只有原五欄、缺 External Effects 的過渡工單
也可讀但不取得並行資格，避免一次性遷移造成 BACKLOG 中斷。

完整規則見 [並行開發與工作輪次標準](../parallel_development.md) §2～§4。
