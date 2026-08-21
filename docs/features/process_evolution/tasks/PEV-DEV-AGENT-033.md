# [Task ID: PEV-DEV-AGENT-033] 依 skill_conventions.md 補齊 13 份 skill 的落差

**🔗 依附母任務 (Parent Task ID):** —（硬依賴 `PEV-DEV-AGENT-028`）
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** tech-lead
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-22T02:10+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`PEV-DEV-AGENT-028` 立了 `kit/docs/standards/skill_conventions.md`，
但**該張明文不修 skill**（AC-05／§5：修了 `025` 的對齊工作就白做了）。
逐份對照出來的落差全部收容在本張。落差清單見該標準的第 8 節「已知落差」。

**為什麼要分兩張**：`028` 是立標準，本張是套用標準。合在一起的話，
標準會被寫成「剛好描述現況」的樣子——**規則要先能指出現況哪裡不對，才有價值**。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：
  - `kit/docs/standards/skill_conventions.md`（尤其第 3、4、5 節與第 8 節落差表）
  - `docs/features/process_evolution/reviews/PEV-DEV-AGENT-028.md` §3 的逐份對照表
- **Outputs**：
  - `kit/.agent/skills/*/SKILL.md`（至多 13 份）
  - `kit/.agent/resources/team_protocol.md`（**只在最後一步**加標記，見 §2.3）
  - 根目錄安裝實例（`./install.sh . --upgrade`）

### 2.1 章節缺口（第 3 節「必備章節」）

| 章節 | 現況 | 要補幾份 |
|---|---|---|
| §1.10 Commit 閘門 | 5/13 | **8 份**：business-analyst、product-manager、qa-test-planner、scrum-master、security-engineer、system-architect、tech-lead、uiux |
| §1.11 文檔權威階序 | 0/13 | **13 份全部** |
| §1.12 取證通道保真 | 13/13 | — |
| §1.5／§1.9（施工側 6 份） | 6/6 | — |

⚠️ **補寫不是貼同一段話。** `025` 已經因為複製貼上踩過一次（backend／frontend 的
§1.12 段落逐字相同 75 字）。每一份要寫出**這條規範對該角色的具體意義**——
例如 `uiux` 的 §1.10 要講 wireframe 進 commit 前的確認，不是照抄開發者的說法。

### 2.2 技術棧中立的違規（第 4 節）

`frontend-developer/SKILL.md:37` 正文寫死
「**核心技術**：優先使用 HTML / React 結構搭配 **Vanilla CSS**」。
這對非 React 專案是直接的錯誤指令，性質與 `027` 移除的
「不可自行引入其他框架」相同。改寫成技術棧中立的說法
（意圖是「介面要有互動感、不要死板」，那部分保留）。

**不要順手改 frontmatter 的 `description`**——標準第 4 節已明文界定
那一欄是觸發關鍵字，框架名列得越全召回越準，不在本條範圍。

### 2.3 最後一步才在守則標記「適用全角色」

13 份補齊、`uv run pytest` 全綠之後，才可在
`kit/.agent/resources/team_protocol.md` 的 §1.10、§1.11 標上「適用全角色」。

⚠️ **順序顛倒會當場產生 13 筆紅**：`test_適用全角色的章節被十三份_skill_全部引用`
直接讀守則的標記，標了就要求全數引用。標準第 5 節寫的就是這條。

### 2.4 篇幅（第 7 節）

補寫會讓行數上升。`scrum-master`（163）、`qa-test-planner`（190）、
`qa-automation-engineer`（255）已超過 150 行軟上限，補完要**在檔頭寫明為什麼超過**。
其餘 10 份補完若跨過 150 也一樣。**軟上限不是刪內容的理由**——
它要照出的是「有沒有混進不該在這一層的東西」。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：§1.10 補進缺的 8 份，每份的敘述**針對該角色**，不是共用段落。
- [ ] AC-02：§1.11 補進 13 份，同上。
- [ ] AC-03：引用一律用標準第 1 節的格式（檔名＋編號＋標題），
      `test_skill_引用守則的編號與標題都要對得上` 全綠。
- [ ] AC-04：`frontend-developer/SKILL.md:37` 改寫為技術棧中立，
      `description` 欄位不動；審查紀錄要寫出改寫後對非 React 專案為何不再是錯誤指令。
- [ ] AC-05：**補齊之後**才在守則 §1.10／§1.11 標「適用全角色」，
      且標記前後各跑一次 `uv run pytest`，兩次輸出都留進審查紀錄
      （標記前應已全綠——若標記前就紅，代表補寫沒做完）。
- [ ] AC-06：超過 150 行的 skill 檔頭都有超限理由。
- [ ] AC-07：任兩份 skill 的新增段落不得逐字重複；審查紀錄附最長共同子字串的實測。
      **這是人工判準**（標準第 6 節），數字只作參考、不設閘門。
- [ ] AC-08：`uv run pytest` 全綠；`python3 .agent/scripts/precheck.py` 七項全綠；
      `./install.sh . --upgrade` 待合併 0。
- [ ] AC-09：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。落差清單與分層判準已由 `028` 定案（必備章節分層、150 行軟上限
    兩項由使用者於 2026-08-22 裁定）。
- **✍️ User 補充回覆 (User Input)**:
  -

## 5. 範圍外 (Out of Scope)

- **不改 `skill_conventions.md` 的規則**——本張是套用，不是重新立規。
  若補寫過程發現規則有問題，依 `team_protocol.md` §1.8 判定成因後另行處置。
- **不動 frontmatter 的 `description`**（§2.2）。
- **不把第 6 節「§1.12 角色專屬」硬化成自動檢查**——`028` 已裁定該判準需要人讀。
- **不重寫歷史、不 push**。
