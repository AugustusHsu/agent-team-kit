# ADR-003：正式審查採 fresh context 與不可變 Review Target

**狀態：** Accepted  
**定案日期：** 2026-08-27  
**影響範圍：** Code review、輪次 panel、審查證據與人工閘門

## Context

同 session 換角色會讓開發者的假設與交付摘要成為審查者的既有前提；只以 branch／PR 名稱
指認 diff，則 head 改變後仍可能沿用舊核可。多面向 panel 若只交摘要給統整者，也會讓
blocking 證據在統整階段遺失。

## Decision

所有能簽發正式 APPROVED 的工單審查與 round panel 都使用獨立 fresh context；同 session
只能自查。審查唯一對象是 `base SHA + head SHA + Task/Round ID`，head 改變即使相應 verdict 失效。

多工單 round panel 基線兩個獨立面向：整合語意與對抗驗證；只在關鍵風險加入第三位專家。
raw findings 先落 Round Manifest，`code-reviewer` 再逐項 reconciliation 並回查所有 blocking 證據。

## Rejected alternatives

- **同 session 換角色即可正式核可**：回報與證據同源，無法形成獨立反證。
- **強制更換模型**：模型多樣性可能有益，但供應商可用性不應成為流程硬依賴。
- **以 PR／branch 名稱當審查對象**：名稱可變，不能證明 verdict 對應哪一個 head。
- **統整者只讀摘要**：無法直接回查 blocking finding，也容易漏掉被折疊的證據。
- **固定三人以上 panel**：一般輪次成本不必要地倍增。

## Consequences

每次正式核可都有可重建對象；任何後續結案資料必須先納入 reviewed head。審查成本增加，
但使用者只需看一份 reconciliation；安全政策、公開 API、migration 等仍保留最終人工閘門。

完整規則見 [並行開發與工作輪次標準](../parallel_development.md) §6～§8。
