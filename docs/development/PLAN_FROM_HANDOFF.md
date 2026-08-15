---
description: 將一份 handoff / 需求交接文件轉為「可開發的文檔變更 + EPIC 與子工單」的三階段閘門式規劃流程。每階段強制停下等使用者確認後才續行；全程只動文檔與工單，絕不撰寫或修改任何程式碼。
---

# 交接文件轉工單規劃流程 (Plan from Handoff)

此 Workflow 是把「一份 handoff / 需求描述」收斂成**文檔變更**與**可直接開發的 EPIC + 子工單**的統一規劃入口，銜接於 `scrum-master` 開單、Developer 執行之前。

## 🔒 全域鐵則（不可違反）

- **絕對約束**：全程**只撰寫或修改文檔（`.md`）與工單**，**絕不撰寫或修改任何 `.py` / `.tsx` / `.ts` 等專案程式碼檔案**。程式實作一律交由後續開發 Agent 依工單進行。
- **閘門式停點**：三個階段之間**強制停下**，明確回報該階段產出並等使用者確認/放行後，才進入下一階段。中斷後續行前，**先確認上一階段是否完整**再繼續。
- **忠實回報**：不得為了「一致性」把尚未實作的狀態提前改綠（如 PRD 頁面狀態表 🟠 Mock → 🟢），實況與文件矛盾時**回報使用者裁定**，不自行妥協。
- **文檔修改不列入工單**：所有文檔（BRD/PRD/HLD/LLD/api_spec/test_plan/wireframe）的新增、修改、刪除，一律在**階段二由對應文檔角色就地完成**，屬規劃階段產物。階段三**只開程式碼實作與測試碼工單**，絕不產生 `*-DOC-*` 文檔工單。

---

## 前置作業 (Pre-work)：讀取相關角色 SKILL

在動任何文檔前，先讀取本次規劃會用到的角色定義（一律以 `.agent/skills/{name}/SKILL.md` 為準；skill 名稱皆為 kebab-case，與目錄名一致，可用 `/{name}` 觸發）。

### 文檔作業的角色分工（依需求分派不同 skill）

**慣例**：處理文檔（新增／修改／刪除）時，預設**併用以下五個文檔角色**通盤檢視，再依「當前這份文檔的實際需求」由對應角色主責，其餘角色以協作/糾察身分把關一致性：

| 文檔需求 | 主責 skill | 產出檔 |
|---|---|---|
| 為什麼要做、商業價值、ROI、BRD | `business-analyst` | `docs/features/{module}/brd.md` |
| 要做成什麼、功能清單、User Flow、驗收標準、PRD | `product-manager` | `docs/features/{module}/prd.md` |
| 高階架構、技術選型、ADR、HLD | `system-architect` | `docs/features/{module}/hld.md` |
| 資料庫 Schema/ERD、API 契約、Sequence、LLD | `tech-lead` | `docs/features/{module}/lld.md`、`api_spec.md` |
| Wireframe、Mockup、UX 動線、多狀態設計 | `uiux` | `docs/features/{module}/wireframes/*.md` |

> 併用而非各自為政：例如改 `api_spec.md`（tech-lead 主責）時，需同步請 product-manager 覆核是否偏離 PRD 初衷、system-architect 確認是否牽動 HLD/ADR、uiux 確認畫面契約。哪份文檔該由誰改，以上表「文檔需求 → 主責」對應。

### 規劃流程本身另需的 skill

| 用途 | 角色 SKILL |
|---|---|
| 開單、EPIC / 子工單拆分、BACKLOG 管理 | `scrum-master` |
| 測試案例規劃（test_plan） | `qa-test-planner` |
| 資安檢核（認證/授權/加密） | `security-engineer` |

---

## 階段一：理解與盤點（讀，不寫）→ STOP

**目標**：完整讀懂 handoff 的核心目標與範圍，並盤點既有實作/文檔，找出矛盾。

1. 讀 **handoff 文件**本身，抽出：要做什麼、明確不做什麼（維持 Mock 的部分）、預期產出檔案。
2. 讀現況權威來源：`docs/development/BACKLOG.md`（唯一進度真相）、相關 `api_spec.md` / `prd.md` / `test_plan.md` / `hld.md`（大檔用 `grep -n` 定位段落後**局部讀**，禁止整份載入）。
3. 讀**既有相關程式碼**（endpoints / crud / schemas / 前端 api 層 / 相關 model enum），確認 handoff 描述與實況的落差（欄位不存在、路由已存在於他處、enum 值與 spec 漂移等）。
4. **矛盾盤點**：若 handoff 與現狀衝突（例如端點已實作在別的 router），列出矛盾點與建議方案。

**停點產出**：回報「核心目標 / 範圍界線 / 既有實作落點 / 矛盾與建議」，然後**停下**等使用者確認範圍與方向，**不進入階段二**。

---

## 階段二：文檔變更（tech-lead + uiux + scrum-master 規範）→ STOP

依階段一確認的方向，只改文檔：

1. **API 設計文檔**（`tech-lead` 規範）：修改/新增 `api_spec.md` 對應章節——版本號與版本歷史、端點契約（method/路徑/權限/JSON 欄位）、遷移影響表（列出所有受影響呼叫端）、分桶/邊界規則。改動路由後**務必同步 spec**，避免持續漂移。
2. **BACKLOG Icebox**（`scrum-master` 規範）：把「本次不做、日後再議」的項目手動補進 `BACKLOG.md` 的 Icebox；被 EPIC 取代的舊 Icebox 列以刪節線 + `[日期 更新]` 註記。
3. **Wireframe**（`uiux` 規範）：於 `docs/features/{module}/wireframes/` 新增 ASCII-art markdown，涵蓋各視角版面、互動（切換/Tooltip）、Loading/Empty/Error/403 多狀態、以及刻意保留 Mock 的標註。
4. **跨角色文檔一致性（一律就地完成，不開文檔工單）**：api_spec 的改動常牽動 `prd.md` / `test_plan.md` / `hld.md`。**不論是事實性路由對齊，或需角色判斷的新需求（新增需求、新測試案例、新 ADR），皆在本階段由對應文檔角色就地完成**，改法對應「文檔需求 → 主責 skill」表：
   - 新需求 → `product-manager` 改 `prd.md`（含頁面狀態表，實作未完成前狀態維持 🟠 並註記，不提前翻 🟢）
   - 新 ADR / 架構決策 → `system-architect` 改 `hld.md`（先確認 ADR 編號未被佔用再順延）
   - 新測試案例 → `qa-test-planner` 改 `test_plan.md`（含追溯矩陣，指向實作測試碼工單）
   - API 契約 → `tech-lead` 改 `api_spec.md`；畫面 → `uiux` 改 `wireframes/`
   - > **政策**：文檔修改**不列入工單**。文檔屬規劃階段產物，於此就地改完；階段三只開「程式碼實作 / 測試碼」類工單，不再開 `*-DOC-*` 文檔工單。
5. **文檔修改摘要報告**：於專案根目錄 `./` 產出/更新一份摘要報告（使用者後續會刪除），列出：改動檔案清單、每檔變更邏輯、跨文檔一致性修正。文檔再有變更時同步更新此報告。

**停點產出**：交出「文檔修改摘要報告」，**停下**等使用者確認文檔無誤，**不進入階段三**。

---

## 階段三：EPIC 與子工單產出（scrum-master 規範）→ 任務結束

依 `scrum-master` 規範與 `.agent/resources/task_template.md` 模板開單：

1. **建立 EPIC 母工單**：
   - 第一條 AC 固定為「所有 N 張子工單皆完成並通過 Code Review」。
   - 列出子工單清單，並依角色 / 前後端分類（🔧 後端、🎨 前端、🧪 測試）。**不含文檔類**——文檔已於階段二就地改完；於 EPIC 內以一句話註明「文檔已於規劃階段完成，不列子工單」並列出已改檔案。
   - 標出**開發順序與前置依賴**（通常後端骨架/遷移、前端 API 層為前置）。
   - 未決事項寫進 **Human-in-the-loop** 欄位等使用者裁定，不阻斷開單。
2. **拆分子工單（只開程式碼/測試碼，不開文檔工單）**：後端 endpoints/schemas/crud、前端 api 層/頁面接線/互動、測試整合套件。**不產生任何 `*-DOC-*` 文檔工單**（PRD/test_plan/HLD/api_spec/wireframe 皆已在階段二完成）。
3. **子工單自足度要求（核心品質門檻）**：每張子工單須內嵌**確切檔案路徑與行號、完整 API 契約、可複用的既有函式指引、分桶/邊界規則表、客觀可驗證的 AC**，讓開發 Agent「只須簡單查找文檔、甚至不查找」即可直接開發。
4. **母子連動**：子工單全部建立後，EPIC 由 `Ready` 轉 `In Progress`。
5. **工單格式陷阱**（避免 `scan_backlog.py` 靜默漏收）：Status 欄位需帶 `🚥` emoji；`Created`/`Closed` 為 ISO 8601 精確到分鐘 `+08:00` 並帶欄位標籤。Task ID 即檔名，格式 `{UMS|TMS|DMS|WMS|SYS}-{DOC|DEV|TEST|DEPLOY}-{FE|BE|AGENT|QA|DATA|EPIC|MANUAL|FIX}-{三位流水號}`。

### 收尾：同步 BACKLOG（🔒 強制）

Icebox 為手動維護。⚠️ **關鍵**：`scan_backlog.py` 的 Icebox 保留機制是**讀取「`--output` 目標檔」自身**的既有 Icebox 來延續（`extract_existing_icebox()`）——因此**不可**用「輸出到新暫存檔再比對」的方式驗證（新檔沒有 Icebox 可讀，會塌成預設佔位符，造成誤判）。正確流程：

1. **備份**目標檔：`cp docs/development/BACKLOG.md $CLAUDE_JOB_DIR/tmp/BACKLOG_backup.md`。
2. **直接對目標檔**執行官方指令覆寫（它會讀 BACKLOG.md 自己的 Icebox 保留）：
   ```bash
   uv run python .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md
   ```
3. **與備份 diff** 確認 Icebox 各列完整無損：`diff <(sed -n '/🧊 冰箱/,/^## [^🧊]/p' 備份) <(sed -n '/🧊 冰箱/,/^## [^🧊]/p' BACKLOG.md)`；若有異常即從備份還原。
4. 以 `--format summary` 覆核工單數與狀態分佈是否如預期。

**任務結束**：回報「EPIC + 子工單清單、開發順序、BACKLOG 同步結果、待裁定的 HITL 事項」。至此規劃完成，**不進入任何程式碼實作**，等使用者指定子工單、指派對應 Developer 角色啟動開發。
