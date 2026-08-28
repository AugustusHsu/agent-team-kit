# [Round ID: {RoundID}] [輪次標題]

**🚥 輪次狀態 (Status):** Open
**🎯 輪次目標 (Goal):** [單一、可驗收的共同目標]
**🌿 輪次分支 (Branch):** `feature/{topic}`
**📍 開輪基準 (Opening Base):** `[完整 40 字元 SHA]`
**📅 建立時間 (Created):** [ISO 8601]
**🔎 整合審查對象 (Integration Review Target):** —

> Round Manifest 是 QA、panel 與 reconciliation 的唯一載體，不另建 round review 檔。
> 正式 target 使用完整 `base SHA + head SHA + Round ID`；PR／MR 或 branch 只供定位。

## 1. 封閉工單集合（唯一來源）

| Task ID | 目標 | 初始狀態 |
|---|---|---|
| `{TaskID}` | [本輪內的明確輸出] | Ready／Pending |

本輪只接受 2～5 張既有工單。新增前置或 integration-fix 若超過五張或改變目標，停止擴張並請
使用者重新規劃；wave、反向 blocks 與並行候選由工單來源欄位推導，不手寫第二份來源。

## 2. 依賴推導快照（非第二份來源）

| Wave | 工單 | 放行／阻擋理由 |
|---|---|---|
| [數字] | `{TaskID}` | [由 Blocked By、Write Scope、Contract、External Effects 推導] |

## 3. 所有權與關鍵風險

- **Write Scope／Contract／External Effects 結果**：[可重跑指令與摘要]
- **Overlap zones**：[未命中／列出 high 或 critical 範圍]
- **條件式第 3 位風險專家**：[未觸發／觸發原因與角色]

## 4. 整合 QA

| 欄位 | 證據 |
|---|---|
| QA Candidate Target | `base=[完整 40 字元 SHA]; head=[完整 40 字元 SHA]; id={RoundID}` |
| 當下主線 SHA | `[完整 40 字元 SHA]` |
| 輪次 head SHA | `[完整 40 字元 SHA]` |
| 執行者／Task Profile | `[角色]`／`[profile]` |
| 指令與原始結果 | [可重跑指令、通過／失敗數與輸出位置] |
| 失敗歸因／退回紀錄 | [無／原 Task ID／integration-fix；不得靜默擴張] |

## 5. Panel Raw Findings

所有 lane 使用同一個候選 target，並在讀取其他 lane 前獨立完成。Raw findings 必須先落入本節，
才可開始 §6 reconciliation；沒有 finding 的 lane 也要留下「無」及其實跑證據。

**Panel Candidate Target:** `base=[完整 40 字元 SHA]; head=[完整 40 字元 SHA]; id={RoundID}`

| ID | Lane | Severity | Claim | File／Line | Reproducible Evidence | Recommended Verdict | Reviewed Target |
|---|---|---|---|---|---|---|---|
| `[lane]-F-001` | integration-semantics／adversarial／risk | blocking／non-blocking | [可證偽主張] | [精確位置] | [指令與原始結果] | APPROVED／CHANGES REQUESTED | [完整 target] |

### 5.1 整合語意 lane

- **Fresh-context 聲明**：[與開發隔離；同 session 自查不得填正式結果]
- **Raw output**：[finding ID 清單／無 finding 與證據]

### 5.2 對抗驗證 lane

- **Fresh-context 聲明**：[與開發及整合語意 lane 隔離]
- **Raw output**：[finding ID 清單／無 finding 與證據]

### 5.3 條件式風險專家 lane

[未觸發；或記錄安全政策、migration、公開 API、critical overlap zone 的觸發理由與 raw output。]

## 6. Reconciliation 與人為閘門

| Finding ID | Disposition | 理由 | Blocking 回查／重跑證據 |
|---|---|---|---|
| `[lane]-F-001` | accept／reject／duplicate／defer | [不得只填結論] | [blocking 必填；其餘可填 —] |

- **Code Reviewer 自己的 lane 完成時間**：[必須早於讀取其他 lane]
- **Raw findings 落盤 commit**：`[SHA；必須早於 reconciliation]`
- **未解證據衝突**：[無／停止原因與使用者裁定]
- **條件式風險最終人工裁定**：[不適用（安全政策、migration、公開 API、critical overlap zone
  均未觸發）／觸發類型、使用者裁定原文與時間]
- **修正與重跑範圍**：[無／只重跑哪些受影響 lane 及理由]

## 7. 最終 Review Target 與 Verdict

- **Final Review Target**：`base=[完整 40 字元 SHA]; head=[完整 40 字元 SHA]; id={RoundID}`
- **候選到最終 head 的差異**：[只有 panel metadata／列出實作或測試變更及重跑 lane]
- **Blocking findings 結果**：[全部關閉／尚未關閉]
- **正式 Verdict**：APPROVED／CHANGES REQUESTED

正式 APPROVED 必須由與開發隔離的 fresh context 綁定上方 final target。APPROVED 後不得修改
reviewed round head；target、verdict 與尚待補記的審查 metadata 由目的端 merge commit 寫回本檔，
且相對核准 head 不得混入實作或測試變更。
