# [Round ID: ROUND-001] 並行開發流程落地

**🚥 輪次狀態 (Status):** In Review
**🎯 輪次目標 (Goal):** 將 DN-005、DN-006、DN-008 的已簽核設計落成可安裝、可驗證並能自我 dogfood 的並行開發流程。
**🌿 輪次分支 (Branch):** `feature/parallel-development`
**📍 開輪基準 (Opening Base):** `247de42b9b09026cdbdad33eb6564b5fe86db085`
**📅 建立時間 (Created):** 2026-08-27T10:18+08:00
**🔎 整合審查對象 (Integration Review Target):** `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=98dfad7e64375edd2c1ee769ae3d06dffc4a3ac3; id=ROUND-001`

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
- **條件式第 3 位風險專家**：已觸發並完成獨立取證。整合語意 lane 判定 `migration`，
  風險專家判定 `migration` 與公開 API；對抗驗證 lane 判定未觸發。原始分類衝突保留至
  reconciliation，且依 fail-safe 原則保留使用者最終人工閘門。

## 4. 整合 QA

| 欄位 | 證據 |
|---|---|
| QA Candidate Target | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=98dfad7e64375edd2c1ee769ae3d06dffc4a3ac3; id=ROUND-001` |
| 當下主線 SHA | `feature/kit-dev-process@247de42b9b09026cdbdad33eb6564b5fe86db085` |
| 輪次 head SHA | `feature/parallel-development@98dfad7e64375edd2c1ee769ae3d06dffc4a3ac3` |
| 執行者／Task Profile | `qa-automation-engineer`／`test_verification` |
| 指令與原始結果 | 2026-08-28T12:03+08:00：`uv run pytest` 259 passed；root／kit `precheck.py` 各 9/9；installer `--upgrade --dry-run` 為新增 0、更新 0、最新 82、保留 seed 6、待合併 0；graph exit 0、`errors=[]`、waves `1:{043}, 2:{044,045}, 3:{046}, 4:{047}`；`git diff --check` 通過；worktree 僅主工作目錄 |
| 失敗歸因／退回紀錄 | 無；本次 QA 未觸發原 Task ID 退回、integration-fix 或超過五張停止擴張 |

## 5. Panel Raw Findings

所有 lane 使用同一個候選 target，並在讀取其他 lane 前獨立完成。Raw findings 必須先落入本節，
才可開始 §6 reconciliation；沒有 finding 的 lane 也要留下「無」及其實跑證據。

**Panel Candidate Target:** `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001`

| ID | Lane | Severity | Claim | File／Line | Reproducible Evidence | Recommended Verdict | Reviewed Target |
|---|---|---|---|---|---|---|---|
| `INT-F-001` | integration-semantics | blocking | 只有 043 在固定樹內具可重建的最終 APPROVED；044 artifact 停在第五輪 CHANGES REQUESTED，045～047 缺正式 review artifact／審查結論，無法證明 Task→Round merge 前完成 pinned fresh-context 窄審。 | `docs/features/process_evolution/reviews/PEV-DEV-AGENT-044.md:3,61`；045～047 對應 review 檔不存在；`team_protocol.md:333-376` | 固定 Head 的 `git cat-file -e`：044 exit 0，045～047 exit 128；044 artifact 僅第一至第五輪 CHANGES REQUESTED；歷史卻已有 044～047 merge `2e02787`、`06c6848`、`7ed4512`、`98dfad7`。 | CHANGES REQUESTED | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001` |
| `INT-F-002` | integration-semantics | blocking | 043～045 已標 Done，但各自保留給後續正式入口複驗的最後一條 AC 仍未核取；固定 Head 已包含 047 同步與 QA，狀態與驗收紀錄矛盾。 | `PEV-DEV-AGENT-043.md:15,46-47`；`044.md:16,46-49`；`045.md:15,45-48` | 三張工單均為 Done，但 AC-06／AC-07／AC-07 仍是未勾選；本 lane 重跑 259 passed、root／kit precheck 各 9/9、installer 零待合併、diff check 通過。047 AC-09 是 panel 尚未完成的刻意保留，不納入本 finding。 | CHANGES REQUESTED | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001` |
| `INT-F-003` | integration-semantics | blocking | 固定 target 修改 installer upgrade／migrate 行為，Manifest 卻仍標風險專家未觸發；命中 migration 即須增加第三 lane 並保留使用者最終閘門。 | `install.sh:75-80`；`tests/test_install.py:193-230`；本檔原 `:47-48,82-85` | installer 對舊專案缺少新版 seed 提示執行 migrate；測試 `test_升級不直接補缺少的種子檔而是提示_migrate` 實際覆核該行為。 | CHANGES REQUESTED | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001` |
| `QA-E-001` | adversarial-qa-evidence | none | 無 blocking 或 non-blocking finding；DAG、外部副作用 fail-closed、兩層拓撲、head 漂移、installer／upgrade 與結案前證據均可重跑。 | — | 259 passed；root／kit precheck 各 9/9；graph `errors=[]`、waves 1／2／3／4；installer dry-run 0／0／82／6／0；head 漂移、安全刪 branch、外部副作用與輪外前置等六項負向測試通過。 | APPROVED | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001` |
| `RISK-F-001` | conditional-risk | blocking | 舊版專案升級後無法取得新增的 `overlap_zones.md`：installer 要求 migrate，但 migrate 只處理 AGENTS／CLAUDE，既不建立檔案也不產生 `.new`，後續升級無限重複告警。 | `install.sh:80,140-145`；`kit/.agent/scripts/agent_runtime.py:626-647,661-670` | Base 首次安裝後以 Head upgrade，再跑 `agent_runtime.py migrate --dry-run --json`；targets 只有 AGENTS／CLAUDE，`overlap_zones.md` 仍不存在，第二次 upgrade 再次告警。現有 install test 只驗提示，未證明 migration 可用。 | CHANGES REQUESTED | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001` |
| `RISK-F-002` | conditional-risk | blocking | `Integration Review Target` 只驗欄位存在，不驗 `base/head/id` schema、SHA 或 Round ID；In Review manifest 填 `banana` 仍可由 graph 發布且 precheck 全綠。 | `kit/.agent/scripts/scan_backlog.py:545-552,960-966,1133-1139` | 兩張合法工單搭配 `Status: In Review`、`Integration Review Target: banana`：graph、BACKLOG、precheck 均 exit 0，graph 原樣輸出 `banana`；現有測試只覆蓋欄位缺失。 | CHANGES REQUESTED | `base=247de42b9b09026cdbdad33eb6564b5fe86db085; head=83ed5cc7c74580050056e698e98189b6b2977c06; id=ROUND-001` |

### 5.1 整合語意 lane

- **Fresh-context 聲明**：reviewer 與開發 context 隔離，未沿用舊 Task verdict，未讀其他 lane；
  固定提交與輸出僅在 `/tmp`，repo／refs／worktree 全程唯讀。
- **取證保真**：§1.12 五行探針逐字通過，表格與前後散文完整。
- **Raw output**：`INT-F-001`～`INT-F-003`；建議 `CHANGES REQUESTED`。功能整合、安裝同步、
  DAG 與 Git 拓撲本身無新增實作缺陷，阻擋點在窄審證據、結案 AC 與風險閘門。

### 5.2 對抗驗證 lane

- **Fresh-context 聲明**：reviewer 與開發 context 隔離，未沿用舊 Task verdict，未讀其他 lane；
  暫存測試僅在 `/tmp`，未修改 repo／ref／worktree。
- **取證保真**：§1.12 五行探針逐字通過，表格與前後散文完整。
- **Raw output**：`QA-E-001`，無 findings；建議 `APPROVED`。本 lane 將四類風險 trigger
  人工分類為未觸發，此判定與另外兩條 lane 衝突，尚未 reconciliation。

### 5.3 條件式風險專家 lane

- **Fresh-context 聲明**：由無歷史 fork 的獨立 reviewer 取證，與開發及雙路 panel 隔離，
  未讀其他 lane、未做 reconciliation；所有暫存位於 `/tmp`。
- **取證保真**：§1.12 五行探針逐字通過。
- **Trigger 原始判定**：`migration` 與公開 API 成立；安全政策未另行觸發，未命中已登記的
  `critical` overlap zone。此判定要求保留使用者最終人工裁定。
- **Raw output**：`RISK-F-001`、`RISK-F-002`；建議 `CHANGES REQUESTED`。

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
