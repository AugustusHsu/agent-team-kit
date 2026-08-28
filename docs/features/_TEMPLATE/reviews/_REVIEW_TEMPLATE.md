# [Review: {TaskID}] [工單標題]

## {YYYY-MM-DD} ✅ APPROVED / ❌ CHANGES REQUESTED

> 本範本只用於工單窄審；Round panel 的 raw findings、reconciliation 與最終 verdict 一律寫入
> `docs/development/rounds/<RoundID>.md`，不另建 round review 檔。

## 0. Review Target 與 Context

| 欄位 | 固定值 |
|---|---|
| Task ID | `{TaskID}` |
| Base SHA | `[完整 40 字元 SHA]` |
| Head SHA | `[完整 40 字元 SHA]` |
| 審查層級 | 工單窄審（只查本工單 AC、Write Scope 與測試） |
| Context | fresh context／自查（擇一；自查不得簽 APPROVED） |
| 操作介面 | [PR／MR／branch；只供定位，不是 Review Target] |

Head 改變時，本輪 verdict 立即失效；重新審查必須建立新段落，不得沿用舊 APPROVED。

## 1. 客觀指標

| 指標 | Base／負向對照 | Head |
|---|---|---|
| 測試數／失敗數 | [指令與原始結果] | [指令與原始結果] |
| 新增測試的負向對照 | [還原實作後的轉紅結果] | [修正後結果] |
| 其他可量測值 | [值] | [值] |

## 2. AC 核對

| AC | 結果 | 客觀證據 |
|---|---|---|
| AC-01 | ✅／❌ | [可重跑指令、輸出或檔案位置] |

## 3. 路由證據

| 欄位 | 本次值 |
|---|---|
| Task Profile | [ID；註明由 Task Type 映射或工單明示] |
| Capability／Data Override | [無則填 —] |
| Execution Override | [無則填 —；有則含 scope 與 expires] |
| 選中 Execution Profile | [ID] |
| Probe 證據時間 | [ISO 8601] |
| 使用過期 cache | [否／是，若是說明為何符合純本機唯讀例外] |
| 中途交接 | [無／有；有則列 failed profile、接手 profile 與 handoff 位置] |

### 候選與排除理由

| Execution Profile | Availability | Score | 結果／排除理由 |
|---|---|---:|---|
| [profile ID] | verified / degraded / unavailable / unknown | [分數或 —] | [選中／缺少能力／政策衝突／狀態過期] |

> 路由 JSON 可由 `python3 .agent/scripts/agent_runtime.py route --task-file <path> --json`
> 產生。審查檔保存必要欄位與結論即可；**不得貼入 credential 或完整敏感 probe stdout**。

## 4. Findings

沒有 finding 時明確填「無」。每筆 finding 使用完整欄位，不能只寫結論：

| ID | Severity | Claim | File／Line | Reproducible Evidence | Recommended Verdict |
|---|---|---|---|---|---|
| `F-001` | blocking／non-blocking | [可證偽主張] | [精確位置] | [可重跑指令與原始結果] | APPROVED／CHANGES REQUESTED |

## 5. 重大瑕疵與風險

- [無，或列出 `檔案:行號` ＋具體影響]

## 6. 僅人工判讀

- [無，或明說哪些 AC 無法客觀自動驗證]
