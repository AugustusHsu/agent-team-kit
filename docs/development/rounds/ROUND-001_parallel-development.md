# [Round ID: ROUND-001] 並行開發流程落地

**🚥 輪次狀態 (Status):** Open
**🎯 輪次目標 (Goal):** 將 DN-005、DN-006、DN-008 的已簽核設計落成可安裝、可驗證並能自我 dogfood 的並行開發流程。
**🌿 輪次分支 (Branch):** `feature/parallel-development`
**📍 開輪基準 (Opening Base):** `247de42b9b09026cdbdad33eb6564b5fe86db085`
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**🔎 整合審查對象 (Integration Review Target):** —（所有工單通過窄審並併入本輪後回填完整 base SHA、head SHA 與 `ROUND-001`）

> 📌 **Bootstrap 說明：** 本 manifest 是 Round Manifest schema 與掃描器實作前的第一份 dogfood 資料，
> 依 DN-005 §5.8 人工建立。正式 schema 由 `PEV-DEV-AGENT-043` 落地、機械驗證由 `044` 落地；
> 後續若 schema 有相容性調整，由對應工單在不改變本輪目標與封閉集合的前提下更新本檔。

## 1. 封閉工單集合（唯一來源）

| Task ID | 目標 | 初始狀態 |
|---|---|---|
| `PEV-DEV-AGENT-043` | 落地並行開發標準與架構決策 | Ready |
| `PEV-DEV-AGENT-044` | 實作工單 DAG、欄位與 wave 驗證 | Pending |
| `PEV-DEV-AGENT-045` | 實作輪次分支、worktree 與所有權流程 | Pending |
| `PEV-DEV-AGENT-046` | 實作 fresh-context panel 與不可變 Review Target | Pending |
| `PEV-DEV-AGENT-047` | 並行流程端到端驗證與安裝同步 | Pending |

本輪工單集合在開輪時封閉。新增前置或 integration-fix 若使總數超過五張、或改變上述目標，
必須停止擴張並請使用者重新規劃；工單不另存 Round ID，避免雙重來源。

## 2. 依賴推導快照（非第二份來源）

此表僅記錄開輪時從各工單 `Blocked By` 推導出的可重算結果；若與工單衝突，以工單欄位為準，
待 `PEV-DEV-AGENT-044` 落地後由掃描器重建。

| Wave | 工單 | 放行條件 |
|---|---|---|
| 1 | `043` | 無前置 |
| 2 | `044`、`045` | `043` 完成；兩者 Write Scope 不重疊，可分 branch／worktree 並行 |
| 3 | `046` | `044`、`045` 完成 |
| 4 | `047` | `046` 完成 |

## 3. 所有權與關鍵風險

- `043`：第 1 層並行標準、Git／team protocol 對齊、ADR 與文件完整性回歸。
- `044`：工單模板、BACKLOG／precheck 的 DAG 邏輯、Scrum Master 指引與其測試。
- `045`：overlap zones 種子、DevOps worktree 指引、installer seed 行為與真實 Git 拓撲測試。
- `046`：code review／QA skills、review／round 範本、team protocol 審查生命週期與完整性回歸。
- `047`：端到端測試、安裝實例同步、本 manifest 的放行證據與 BACKLOG。

開輪檢查結果：`044` 與 `045` 沒有重疊 Write Scope；共用契約由前置 `043` 建立後才放行。
目前不預先核准任何關鍵 overlap zone 例外；若執行中命中安全政策、公開 API 或 migration，
必須在本輪整合點保留最終人工閘門。

## 4. 整合驗證（由 047 回填）

- **驗證對象**：—
- **當下主線 SHA**：—
- **輪次 head SHA**：—
- **執行者／Task Profile**：`qa-automation-engineer`／`test_verification`
- **指令與原始結果**：—
- **失敗歸因／退回紀錄**：—

## 5. Panel 原始 findings（由 046／047 回填）

### 5.1 整合語意 lane

—

### 5.2 對抗驗證 lane

—

### 5.3 條件式風險專家 lane

未觸發；若命中關鍵風險再新增，不以空白第三人增加固定成本。

## 6. Reconciliation 與人為閘門（由 046／047 回填）

| Finding ID | 處置 | 理由／重跑證據 |
|---|---|---|
| — | — | — |

- **Blocking findings 回查結果**：—
- **未解證據衝突**：—
- **關鍵 overlap zone 最終人工裁定**：—
- **輪次最終 verdict**：—
