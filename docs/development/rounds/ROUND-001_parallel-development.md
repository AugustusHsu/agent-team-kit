# [Round ID: ROUND-001] 並行開發流程落地

**🚥 輪次狀態 (Status):** Open
**🎯 輪次目標 (Goal):** 將 DN-005、DN-006、DN-008 的已簽核設計落成可安裝、可驗證並能自我 dogfood 的並行開發流程。
**🌿 輪次分支 (Branch):** `feature/parallel-development`
**📍 開輪基準 (Opening Base):** `247de42b9b09026cdbdad33eb6564b5fe86db085`
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**🔎 整合審查對象 (Integration Review Target):** —（047 合併進輪次並完成審查前結案 commit 後固定）

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

- **Write Scope／Contract／External Effects 結果**：根目錄正式入口執行
  `.venv/bin/python .agent/scripts/scan_backlog.py --format graph`，exit 0、`errors=[]`；拓撲為
  `043 → {044,045} → 046 → 047`，waves 為 `1／2／3／4`。保守候選為空；既有 wave 2
  已依開輪人工所有權裁定分流，沒有在掃描器落地後反向改寫歷史。
- **Overlap zones**：`docs/development/overlap_zones.md` 尚未登記長期 `critical`／`high` 熱區，
  本輪未取得任何例外豁免。
- **條件式第 3 位風險專家**：目前未觸發；若正式 integration target 顯示安全政策、migration、
  公開 API 或 `critical` overlap zone，panel 前改為觸發並保留使用者最終閘門。

## 4. 整合 QA

| 欄位 | 證據 |
|---|---|
| QA Candidate Target | —（047 Task merge 與審查前結案 commit 後固定） |
| 當下主線 SHA | —（整合 QA 執行當下讀取完整 SHA） |
| 輪次 head SHA | —（整合 QA 執行當下讀取完整 SHA） |
| 執行者／Task Profile | `qa-automation-engineer`／`test_verification` |
| 指令與原始結果 | 047 分支前置證據：`tests/test_parallel_development_e2e.py` 3 passed；installer 正式同步後再次 `--upgrade --dry-run` 為新增 0、更新 0、待合併 0；正式 target 結果待回填 |
| 失敗歸因／退回紀錄 | 前置證據無失敗；正式 target 若失敗，依原 Task ID／integration-fix／超過五張停止擴張三分法處置 |

## 5. Panel Raw Findings

所有 lane 使用同一個候選 target，並在讀取其他 lane 前獨立完成。Raw findings 必須先落入本節，
才可開始 §6 reconciliation；沒有 finding 的 lane 也要留下「無」及其實跑證據。

**Panel Candidate Target:** —（整合 QA 與審查前結案 commit 後固定）

| ID | Lane | Severity | Claim | File／Line | Reproducible Evidence | Recommended Verdict | Reviewed Target |
|---|---|---|---|---|---|---|---|
| — | — | — | 待雙 lane 獨立取證 | — | — | — | — |

### 5.1 整合語意 lane

- **Fresh-context 聲明**：待 047 合併進輪次後由與開發隔離的 reviewer 填寫。
- **Raw output**：待正式 target。

### 5.2 對抗驗證 lane

- **Fresh-context 聲明**：待 047 合併進輪次後由與開發及整合語意 lane 隔離的 reviewer 填寫。
- **Raw output**：待正式 target。

### 5.3 條件式風險專家 lane

目前未觸發；正式 target 若命中安全政策、migration、公開 API 或 `critical` overlap zone 才新增，
不以空白第三人增加固定成本。

## 6. Reconciliation 與人為閘門

| Finding ID | Disposition | 理由 | Blocking 回查／重跑證據 |
|---|---|---|---|
| — | — | 待 raw findings 全數落盤後逐項處理 | — |

- **Code Reviewer 自己的 lane 完成時間**：—
- **Raw findings 落盤 commit**：—
- **未解證據衝突**：—
- **條件式風險最終人工裁定**：—（四類均未觸發才可填不適用；否則記錄觸發類型、
  使用者裁定原文與時間）
- **修正與重跑範圍**：—

## 7. 最終 Review Target 與 Verdict

- **Final Review Target**：—（raw findings、reconciliation、blocking 回查與必要人工裁定落盤後固定）
- **候選到最終 head 的差異**：—
- **Blocking findings 結果**：—
- **正式 Verdict**：—
