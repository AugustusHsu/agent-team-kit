# ADR-002：多工單採短命輪次分支並保留兩層拓撲

**狀態：** Accepted  
**定案日期：** 2026-08-27  
**影響範圍：** Git 分支、worktree、合併與歷史追溯

## Context

所有 Task branch 直接對 main，會讓跨工單語意衝突只在最後才出現；永久模組分支又會累積
漂移與不清楚的生命週期。PR 平台保存的過程 commits 不屬於可攜 Git 歷史，squash 後刪除
branch 會讓本地 repo 無法重建支線拓撲。

## Decision

單張工單維持一層。2～5 張同目標工單建立短命 `feature/{topic}` round branch 與 Round Manifest；
每張工單仍使用 Task ID branch。Task → round、round → main、單 Task → main 全部使用 merge commit。
main first-parent 一輪一行，round first-parent 一張工單一行；merge 訊息保存 Round／Task ID。

兩張以上工單同時活躍才強制各自 worktree，Task 合併 round 後移除 worktree但保留 branch，
整輪通過並合併 main 後才安全回收所有 refs。

## Rejected alternatives

- **永久模組分支**：目標與結束條件模糊，持續吸收 main 的成本無上限。
- **永遠堆疊、只合併最上層**：把依賴與無依賴工單都強行線性化，round 看不到逐張 merge 點。
- **PR 時 squash、無 PR 才 no-ff**：同一流程產生兩種歷史語意，且可攜性依賴平台資料。
- **每 N 天 rebase**：日曆不是風險訊號，會製造不必要的衝突工作。

## Consequences

歷史會多出 merge commits，但 first-parent 提供穩定的人讀粒度；平台更換、branch ref 刪除後，
完整拓撲與 ID 仍在 Git 物件中。輪次同步改為開輪、必要重疊事件、最終整合三個時點。

完整規則見 [並行開發與工作輪次標準](../parallel_development.md) §4～§6 與
[Git 流程](../git_workflow.md) §6～§7。
