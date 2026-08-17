# [Task ID: PEV-DEV-AGENT-016] 審查紀錄搬出工單：完整報告落在 reviews/，工單只留結論與指標

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** scrum-master
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T09:25+08:00
**✅ 完成時間 (Closed):** 2026-08-17T09:29+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

現行規範要求 Code Reviewer 把**完整審查報告寫進工單 `.md`**
（`team_protocol.md` §2.3 回寫機制、`code-reviewer/SKILL.md` §4 第 3 條）。
後果是工單隨審查輪次單調膨脹：工單本來是「要做什麼」的規格、會被反覆讀取，
審查報告是「這一輪做得如何」的過程紀錄、只在該輪有用，兩者混在同一個檔案裡，
每次讀規格都要付整份審查歷程的成本。

**實查本 repo（2026-08-17）**：工單總量 122 KB／30 張，其中 14 張含
「📝 Code Review 備註」；最大的 `PEV-DEV-AGENT-001.md` 單檔 31 KB，
是第二名（7.7 KB）的四倍——膨脹來源正是多輪審查與 HITL 問答的堆疊。

冰箱的「工單瘦身」列卡在「落點未定」。2026-08-17 裁定落點為
**repo 內獨立檔 `docs/features/<模組>/reviews/<TaskID>.md`**：
不綁平台（無遠端專案一樣成立）、跟著 commit 走、`grep` 得到，
且 `scan_backlog.py` 只掃 `tasks/*.md`，不會把審查檔誤認成工單。
落點既定、AC 當場寫得出來，依 DN-001 §3.2 直接開工單，不開 DN。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**（a）正版規則**——`team_protocol.md` §2.3 的「回寫機制」改寫為「審查紀錄的落點」：
完整報告進 `docs/features/<模組>/reviews/<TaskID>.md`（一張工單一個檔，
多輪審查在同檔內由新到舊追加）；工單的「📝 Code Review 備註」章節**只放三樣東西**
——結論行（日期＋Verdict＋審查檔連結）、📊 客觀指標表、
CHANGES REQUESTED 時的待修正項目單行清單。§1.8 退回條款（第 100 行）同步改指向。

**（b）skill 落地**——`code-reviewer/SKILL.md` §4 的報告產出與回寫條款依上述改寫，
含「無遠端專案」路徑：審查載體從「工單的備註章節」改為審查檔本身。
`evals/evals.json` 的對應 expectation 一併更新。

**（c）目錄慣例**——`kit/docs/features/README.md` 的目錄慣例補上 `reviews/<TaskID>.md`；
`kit/docs/features/_TEMPLATE/` 新增 `reviews/README.md` 佔位說明，
讓新專案 clone 出來就有這個目錄。根目錄的 `docs/features/README.md` 是種子檔
（升級不覆蓋），手動同步同一段。

**（d）git_workflow**——§8.3「無遠端專案的降級」與 §8 平台對照表的
「合併前審查的載體」欄位改為審查檔。

**（e）回歸防線**——`tests/test_kit_integrity.py` 的 `已廢除的流程規則` 加一列，
擋住「審查結果直接寫入對應工單」這類殘留；`tests/test_scan_backlog.py` 加一測，
釘住 `reviews/*.md` 不會被當工單掃描。

**（f）冰箱**——「工單瘦身」列移除（落點已定、已開工單）。

**不做**：**既有 14 張工單不追溯遷移**。依 `team_protocol.md` §1.11，
已結案工單「不改它，也不引用它」——新規則只對新的審查輪次生效。

## 3. 驗收標準 (Acceptance Criteria)

- [x] `team_protocol.md` §2.3 有「審查紀錄的落點」條款，明確寫出審查檔路徑格式與工單只留的三樣東西
- [x] `team_protocol.md` §1.8 的退回回寫改指向審查檔
- [x] `code-reviewer/SKILL.md` §4 的回寫條款與「無遠端專案」路徑均以審查檔為載體
- [x] `code-reviewer/evals/evals.json` 不再要求「編輯工單 .md 回寫審查結果」
- [x] `kit/docs/features/README.md` 與根目錄種子檔的目錄慣例都含 `reviews/<TaskID>.md`
- [x] `kit/docs/features/_TEMPLATE/reviews/README.md` 存在
- [x] `git_workflow.md` §8 對照表與 §8.3 的審查載體改為審查檔
- [x] `test_kit_不得殘留已廢除的流程規則` 新增一列且全 kit 掃描通過
- [x] 新增測試證明 `docs/features/<模組>/reviews/*.md` 不會被 `scan_backlog.py` 掃成工單
- [x] 本工單自己的完整審查報告寫在 `docs/features/process_evolution/reviews/PEV-DEV-AGENT-016.md`（規則的第一個適用對象是它自己）
- [x] 冰箱移除「工單瘦身」列
- [x] `uv run pytest` 全綠；`./install.sh . --upgrade` 待合併 0

## 4. 人為補充與確認 (Human-in-the-loop)

- 2026-08-17：落點由使用者裁定為「repo 內獨立檔」，理由見 §1。

## 📝 Code Review 備註

> 2026-08-17 ✅ APPROVED — 完整報告見 [../reviews/PEV-DEV-AGENT-016.md](../reviews/PEV-DEV-AGENT-016.md)

### 📊 客觀指標

| 指標 | 變更前 | 變更後 |
|---|---|---|
| 全套測試／失敗數 | 110 / 0 | **111 / 0** |
| 本次新增測試的負向對照 | — | **確認會紅**（`glob` → `rglob` 後轉紅，還原回綠） |
| kit 內「完整報告寫進工單」的殘留 | 3 檔各 1 處 | **0** |
| kit 內「最近 7 天」時間窗殘留 | 2 檔各 1 處 | **0** |
| `已廢除的流程規則` 列數 | 9 | **11** |
| 冰箱資料列 | 5 | **4** |
| `./install.sh . --upgrade` 待合併 | — | **0** |
