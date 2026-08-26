# [Review: {TaskID}] [工單標題]

## {YYYY-MM-DD} ✅ APPROVED / ❌ CHANGES REQUESTED

## 1. AC 核對

| AC | 結果 | 客觀證據 |
|---|---|---|
| AC-01 | ✅／❌ | [可重跑指令、輸出或檔案位置] |

## 2. 路由證據

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

## 3. 重大瑕疵與風險

- [無，或列出 `檔案:行號` ＋具體影響]

## 4. 僅人工判讀

- [無，或明說哪些 AC 無法客觀自動驗證]
