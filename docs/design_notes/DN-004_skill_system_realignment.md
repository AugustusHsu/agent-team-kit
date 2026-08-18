# [DN-004] Skill 體系與現行流程的重新對齊

**🚥 狀態 (Status):** 🔍 Exploring
**📅 建立 (Created):** 2026-08-16
**🔗 依賴 (Depends on):** DN-001（本檔的格式）；DN-003（git 流程，其落地會先改動 6 份 skill）
**📌 來源 (Origin):** 使用者指令（2026-08-16）——「目前 skill 已經很久沒更新了，
對於目前流程跟狀況套用 skill 的狀況也需要重新設計」
**🎓 畢業去向 (Landing):** 待填

> 📌 **2026-08-18 拆分。** 原 §3（審查 panel 模式）與 §5（審查與開發的 context 隔離）
> 已拆出至 [DN-008](DN-008_review_panel_and_context_isolation.md)。
> 那兩節的取捨取決於 DN-005／DN-006 的並行拓撲，本檔則處理**當下就修得動**的
> skill 與規範脫節，不該被它們卡住畢業。依 DN-001 §3.4 第 1 條，
> 移出的待決事項在 §4 標「延後至 DN-008」——延後有去處。

## 1. 問題陳述

流程規範（`team_protocol.md`、`docs/standards/`）持續演進，
但 skill 只有被流程**直接點名**的那幾份跟著改，其餘原地不動。
skill 是 agent 實際執行時讀的東西，規範改了而 skill 沒改，
等於**規範上生效、執行上沒生效**。

### 1.1 建檔當時的實測（2026-08-16）

`git log` 統計 `kit/.agent/skills/*/SKILL.md`：

| skill | 最後變更 | 變更次數 | 行數 |
|---|---|---|---|
| qa-automation-engineer | 08-16 | 4 | 384 |
| code-reviewer | 08-16 | 4 | 103 |
| frontend-developer | 08-16 | 4 | 69 |
| backend-developer | 08-16 | 3 | 36 |
| devops-engineer | 08-16 | 3 | 43 |
| scrum-master | 08-12 | 2 | 135 |
| security-engineer | 08-12 | 2 | 37 |
| business-analyst | 08-12 | **1** | 56 |
| product-manager | 08-12 | **1** | 47 |
| qa-test-planner | 08-12 | **1** | 189 |
| system-architect | 08-12 | **1** | 44 |
| tech-lead | 08-12 | **1** | 39 |
| uiux | 08-12 | **1** | 52 |

兩個訊號：

- **13 份中有 6 份「變更次數 = 1」**，也就是建立當天寫完後再也沒被檢視過。
  它們是否仍與現行流程一致，目前**無人驗證過**。
- **篇幅從 36 行到 384 行，差 10 倍**。`qa-automation-engineer` 一份就超過
  最短的六份加起來。這不太可能是職責複雜度的真實差距，比較像是
  **沒有統一的撰寫標準**，各寫各的。

### 1.2 兩天後的重測（2026-08-18）：問題沒有自癒

同一支統計指令重跑：

| skill | 最後變更 | 變更次數 | 行數 |
|---|---|---|---|
| qa-automation-engineer | 08-18 | 6 | 386 |
| code-reviewer | 08-18 | 12 | 142 |
| frontend-developer | 08-18 | 6 | 71 |
| backend-developer | 08-18 | 5 | 38 |
| devops-engineer | 08-18 | 5 | 45 |
| scrum-master | 08-17 | 5 | 162 |
| security-engineer | 08-12 | 2 | 37 |
| business-analyst | 08-12 | **1** | 56 |
| product-manager | 08-12 | **1** | 47 |
| qa-test-planner | 08-12 | **1** | 189 |
| system-architect | 08-12 | **1** | 44 |
| tech-lead | 08-12 | **1** | 39 |
| uiux | 08-12 | **1** | 52 |

**動的還是同一批。** 兩天內 `code-reviewer` 又被改了 8 次、`scrum-master` 3 次，
而那 7 份（含 `security-engineer`）**一個字都沒動**。篇幅差距維持在同一個量級
（384/36 = 10.7 倍 → 386/38 = 10.2 倍，兩端一起長，比值沒改善）。
這證明落差不是「還沒輪到」，是**沒有任何機制會輪到它們**。

### 1.3 三筆具體脫節（2026-08-18 查證）

| 脫節 | 證據 | 影響 |
|---|---|---|
| **§1.12 覆蓋不全** | `team_protocol.md` §1.12 開頭明文「**適用全角色**」，但 13 份 skill 只有 5 份帶（backend／frontend／devops／qa-automation／code-reviewer）。缺的 8 份：scrum-master、qa-test-planner、security-engineer、system-architect、tech-lead、business-analyst、product-manager、uiux | 這條規範 **2026-08-18 才落地**（PEV-DEV-AGENT-023），**當天就已經漏了 8 份**。落差不是歷史包袱，是持續產生中 |
| **章節引用錯置** | `backend-developer:37`、`devops-engineer:45`、`frontend-developer:66`、`qa-automation-engineer:385` 的「Status 更新」都寫「詳見 `team_protocol.md` §1.3」，但 §1.3 是「Epic 關閉條件」，狀態更新操作方式是 **§1.5**。`scrum-master:115` 與 `code-reviewer:134` 寫的是 §1.5（正確） | agent 依指示去讀 §1.3，讀到的是無關內容。**這種錯不會有任何執行期訊號** |
| **7 份從未複檢** | 見 §1.2。期間 `team_protocol.md` 長出 §1.9（分支）、§1.10（commit 閘門）、§1.11（文檔權威階序）、§1.12（取證通道） | 這 7 份是否仍與現行流程一致，至今無人驗證 |

### 1.4 第二類脫節：skill 與 **kit 的定位**脫節（2026-08-18 查證）

§1.3 那三筆是「skill 沒跟上規範」。這一類不同——是 skill 沒跟上 **kit 自己的定位**。
CLAUDE.md 第一行寫 kit 是「可安裝到**任何專案**的套件」，但出貨的 skill 有兩處違反它：

| # | 脫節 | 證據 | 為什麼是缺陷 |
|---|---|---|---|
| a | **`qa-automation-engineer` 綁死技術棧** | §2 明文「本專案的測試工具鏈**已確立，不可自行引入其他框架**」，指定 Pytest + pytest-asyncio + httpx + Cypress。全檔 386 行中 **107 行在程式碼區塊內**（28%），27 行直接提到 Python／FastAPI／Next.js／Cypress | 一個 Go 或 Rails 專案裝了 kit，會拿到一份**禁止它使用自己測試框架**的 QA skill。這正是 DN-007 §3.1 否決選項 A 的同一個理由：「樣板裡的 `uv run pytest` 對非 Python 專案是**死的**」 |
| b | **5 處硬編碼 `uv run`** | `frontend-developer:67`、`backend-developer:38`、`qa-automation-engineer:386`、`code-reviewer:141`、`kit/docs/development/PLAN_FROM_HANDOFF.md:99`，全部教 agent 跑 `uv run python .agent/scripts/scan_backlog.py …` | **kit 特地把出貨腳本寫成 stdlib-only**，`ci.yml` 還有一個 `stdlib-only` job（不裝 uv，用系統 python 跑）專門守這件事（DN-007 §2）。守住了腳本，卻在 skill 裡叫 agent 用 `uv` 去跑它——**閘門守的那條線，被出貨內容自己跨過去了** |

**這一類同樣機檢得到**，而且比 §4.1 的兩條更便宜：
b 只要 `grep -rn "uv run" kit/` 回空即可；a 需要一份技術棧關鍵字表。

**其他三份只是順帶提及，不是綁定**（`backend-developer:33` 舉 pytest 當「例如」、
`frontend-developer:3`／`:37` 的 React 在 description 與風格建議裡、
`qa-test-planner:70` 的 Playwright／Cypress 是「例如」）。**只有 `qa-automation-engineer` 是硬性禁令。**

## 2. 既有事實

- **DN-003 的落地（PEV-DEV-AGENT-001）會先動到 6 份 skill**
  （4 份 dev ＋ `code-reviewer` ＋ `scrum-master`）。本 DN 不阻擋它，
  也不該把那 6 份的 git 流程修正吸收進來——那是 DN-003 的產出，
  已有工單、已有 AC。本 DN 處理的是**它蓋不到的另外 7 份，以及體系層的問題**。
- **skill 沒有像 `team_protocol.md` 那樣的正版／指路檔關係**，
  也沒有 `documentation_conventions.md` 等級的撰寫慣例。
  「該寫多長、該寫什麼、哪些是每份都要有的骨架」目前沒有規範。
- ⭐ **沒有自動檢查能發現 skill 與規範脫節——已查證，不是推測。**
  `tests/test_kit_integrity.py` 對 skill 只有四項檢查：
  `test_frontmatter_的_name_與目錄名相符`、`test_每個角色都有_evals`、
  `test_evals_符合_skill_creator_schema`、`test_evals_不得殘留來源專案的識別資訊`。
  **四項全部關於 frontmatter 與 evals，沒有一項讀 skill 正文。**
  `precheck.py` 的六項檢查也不碰 skill。
  DN-003 落地時就是靠人工 `grep` 才找出矛盾敘述——§1.2 已證明這個做法無法規模化。

### 2.1 為什麼不照 DN-001 §7.2 的順序

[DN-001](DN-001_design_note_mechanism.md) §7.2 把本 DN 排在 **4️⃣**，理由兩條：
「依賴 DN-005 §3 的 panel 裁定」、「要修的 7 份 skill 會被 1️⃣～3️⃣ 的產出再改一次——
**先做等於白做**」。2026-08-18 決定先推本 DN，必須交代這兩條為什麼不再成立。

**先確認性質**：DN-001 §7 開頭自陳「**這一節是那條規則的證據，不是新的設計**」——
它是依賴欄位機制的一次實跑示範，不是裁定。因此本節是補充論證，
不是 DN-001 §3.9 意義下的「推翻已畢業 DN」，不需要另開 DN 標 `Superseded`。

| DN-001 的理由 | 拆分後的狀態 |
|---|---|
| 依賴 DN-005 §3 的 panel 裁定 | **消失。** 那個依賴整個活在原 §3 裡，已於 2026-08-18 移到 [DN-008](DN-008_review_panel_and_context_isolation.md)。本檔剩下的部分對 DN-005／DN-006 **零依賴** |
| 7 份 skill 會被再改一次，先做等於白做 | **反轉。** 見下 |

「先做等於白做」的隱含前提是**本 DN 的產出是 skill 內容**。拆分後不是了——
主產出是 §4.1 的**兩條自動檢查**，那是機制不是內容：

- **機制不會被後續產出作廢。** DN-005／006 落地時再怎麼改 skill，
  「引用的章節必須存在」「標為全角色的章節必須被 13 份全部引用」都繼續有效。
- **順序其實是反的。** DN-005／006 是最重的一組（15 項待決），它們落地時**又會改一批 skill**——
  §1.2 已證明每次規範演進都只有被點名的幾份跟著改。檢查先上，那一輪才不會再漏一次；
  檢查後上，就是再累積一批脫節等著清。**本 DN 的機制部分是 DN-005／006 的前置，不是後續。**
- **對齊的部分確實會被再改一次，但那不是白做。** §1.3 的 §1.12 缺口是**現在就在漏的**：
  §1.12 已經生效，那 8 個角色現在就在沒有開工自檢的情況下取證。
  等最重的一組畢業再修，中間整段時間規範是空轉的；
  而「已對齊的檔案之後再改一次」的成本，遠低於「規範長期不生效」。

## 3. 審查角色的並行化：panel 模式

> 📤 **本節已於 2026-08-18 拆出至
> [DN-008 §2.1](DN-008_review_panel_and_context_isolation.md)，此處不再維護。**
> 拆分理由見本檔頂端：panel 的成本模型取決於 DN-005 定出的並行度。

## 4. 待決事項

| # | 待決 | 選項 | 建議 |
|---|---|---|---|
| 4.1 | ⭐ 範圍：只做「與現行流程對齊」的修補，還是連 skill 的**撰寫標準**一起定 | 只對齊／對齊＋標準 | **分兩張工單**：對齊先行止血，撰寫標準視 4.4 結論再決定。理由：對齊有明確的完成定義（§1.3 三筆修完），撰寫標準沒有；綁在一起會讓止血等設計 |
| 4.2 | 那 7 份「從未複檢」的 skill，先做一次全面盤點還是逐份按需處理 | 全面盤點／逐份按需 | **全面盤點。** 逐份按需的前提是「知道哪一份有問題」，而 §2 最後一條已證實目前無法規模化地知道。反方：一次盤點 13 份成本高——但這是**一次性**成本，之後由 4.5 的檢查接手 |
| 4.3 | 是否需要 skill 的骨架規範（必備章節、篇幅上限、與 `team_protocol.md` 的引用方式）？若要，落在 `docs/standards/` 哪一份 | 不做／新開 `skill_conventions.md`／併入 `documentation_conventions.md` | 若做則**新開 `kit/docs/standards/skill_conventions.md`**——`documentation_conventions.md` 管的是產出文件（BRD／PRD／ADR），skill 是給 agent 讀的執行指引，不同類。⚠️ 新增後**必須同步登記進 `kit/docs/DOCS_MAP.md`**，否則 `test_standards_文件都登記在_DOCS_MAP` 會失敗 |
| 4.4 | ⭐ **`qa-automation-engineer` 的技術棧綁定怎麼處理**（§1.4a）。這同時是篇幅失衡（386 行 vs 38 行）的成因 | 維持／拆成第 2 層由專案填／改寫成技術棧中立 | **拆成第 2 層**，形狀同 DN-007 選 C（adapter）：skill 只留與技術棧無關的部分（AAA 結構原則、Mock 判準、環境隔離原則、交付格式），把 Pytest／Cypress 那 107 行程式碼範例移到專案自己填的落點。理由：§2 那句「不可自行引入其他框架」對非 Python 專案是**有害**的，不只是無用。反方：抽走範例後 skill 會變得抽象，新專案沒有可抄的樣板——**這是真代價，需要使用者裁定值不值得** |
| 4.5 | ⭐ **能不能自動偵測脫節？** 例如規範章節有版本號／雜湊，skill 引用時記下，不一致就測試失敗 | 不做／章節引用檢查／覆蓋率檢查／雜湊比對 | ⭐ **能，而且兩條檢查現在就寫得出可驗收的 AC**——見本節末的附錄。**這是本 DN 價值最高的一項**：4.1～4.4 是一次性修補，只有這一項防未來 |
| 4.6 | 13 個角色是否都還需要？有沒有從未被實際派用過的 | 全留／裁撤未用 | 本輪**只盤點使用紀錄、不裁撤**。裁撤會連帶動到 `evals.json` 與 `test_每個角色都有_evals`，且「沒派用過」在一個只跑了 26 張工單的 repo 裡不構成證據——樣本太小 |
| 4.7 | 審查要不要改成 panel 模式？面向怎麼切、切幾個 | — | **延後至 [DN-008](DN-008_review_panel_and_context_isolation.md) §4.1／§4.2** |
| 4.8 | panel 的統整層由誰擔任 | — | **延後至 [DN-008](DN-008_review_panel_and_context_isolation.md) §4.3** |
| 4.9 | 審查與開發的 context 隔離強度、subagent 回報查核、審查載體 | — | **延後至 [DN-008](DN-008_review_panel_and_context_isolation.md) §4.4～§4.6** |

> 📌 **§1.4b 的 `uv run` 硬編碼不列為待決事項。** 依 DN-001 §3.2「當場寫得出可驗收的 AC
> 就直接開工單」——它的 AC 是 `grep -rn "uv run" kit/` 回空，做法只有一種（改成 `python3`），
> 沒有要比的選項。它在本 DN 出現只是因為盤點時順帶查到，**畢業時直接開成工單**。

### 附錄：自動偵測脫節的兩條檢查（4.5 的具體提案）

DN-001 §3.4 第 2 條要求「寫得出至少一張工單的驗收標準」。這兩條都寫得出：

| 檢查 | 內容 | 負向對照 | 抓得到 §1.3 的哪一筆 |
|---|---|---|---|
| **A：章節引用存在性** | skill 內所有 `team_protocol.md §X.Y` 引用，必須對得上該檔真實存在的 `### X.Y` 標題 | 把某份 skill 的引用改成 `§9.9` → 測試轉紅 | **章節引用錯置**（`§1.3` 應為 `§1.5`） |
| **B：適用角色覆蓋率** | 規範中標「**適用全角色**」的章節（§1.12 已經有這句），必須被 13 份 skill 全部引用 | 拿掉任一份 skill 的 §1.12 引用 → 測試轉紅 | **§1.12 覆蓋不全**（缺 8 份） |

**落點提案：`tests/test_kit_integrity.py`，不是 `precheck.py`。**
理由沿用 DN-007 §3.2 對「已廢除的流程規則殘留」那一項的裁定——
其他 precheck 項目檢查的是**使用者自己寫的工單與文件**，這兩條檢查的是
**kit 出貨內容有沒有被改壞**。使用者專案不編輯 `.agent/`，
帶著一份永遠綠的檢查沒有意義，那是假閘門。

**已知限制**：檢查 B 依賴規範作者記得寫「適用全角色」這四個字。
沒寫的章節它抓不到——它防的是「規範寫了但 skill 沒跟上」，
不是「規範作者忘了標記適用範圍」。後者要靠 4.3 的撰寫標準。

## 5. 審查與開發的 context 隔離

> 📤 **本節已於 2026-08-18 拆出至
> [DN-008 §2.2](DN-008_review_panel_and_context_isolation.md)，此處不再維護。**
> 拆分理由見本檔頂端：隔離的審查載體取決於 DN-006 的分支拓撲與合併點。
>
> 其中**已定案、不再是待決**的一項（context 壓縮會讓審查者讀到非原文，
> PEV-DEV-AGENT-017 實測）已升格為 `team_protocol.md` §1.12，
> 由 PEV-DEV-AGENT-023／024 落地，並成為 DN-008 §3 的既有約束。

## 6. 畢業去向（畢業時才填）

待填。
