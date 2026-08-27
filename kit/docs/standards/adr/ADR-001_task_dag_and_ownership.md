# ADR-001：任務排程採 DAG 與雙層所有權

**狀態：** Accepted
**定案日期：** 2026-08-27
**影響範圍：** 工單拆解、並行排程、檔案所有權

## Context

Epic／模組只能表達分類，不能證明兩張工單之間沒有內容依賴、檔案衝突或外部副作用。
直接手寫 wave、`[P]` 與正反向依賴，又會讓同一事實存在多份、在新增依賴後漂移。

## Decision

工單只保存 `Blocked By`、`Write Scope`、`Contract`、`Change Set`、`Phase` 五個來源欄位；
wave、反向 blocks 與可並行集合由 DAG 推導。輪次內以 Write Scope 表達動態排他所有權，
專案另以 `overlap_zones.md` 保存長期熱點；Epic 不擁有檔案。

並行必須同時滿足 DAG 無邊、Write Scope 不重疊、Contract 已進 base、外部副作用可隔離。

## Rejected alternatives

- **依 Epic／模組直接並行**：無法捕捉設定、schema、路由等跨模組熱點。
- **只比檔案路徑**：不同檔案仍可能透過同一契約產生語意衝突。
- **手寫 `[P]`／wave／blocks**：正反向與衍生資料會在變更後不一致。
- **Epic 保存所有權**：永久分類無法表達每輪不同的實際寫入範圍。

## Consequences

開輪成本增加一次結構化檢查，但 wave 可重算、執行期新依賴有明確落點，且重疊預設會在
開工前轉為排序。舊工單沒有新欄位仍合法，避免一次性遷移。

完整規則見 [並行開發與工作輪次標準](../parallel_development.md) §2～§4。
