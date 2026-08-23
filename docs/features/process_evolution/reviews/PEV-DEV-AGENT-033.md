# 審查紀錄：PEV-DEV-AGENT-033

**工單**：[PEV-DEV-AGENT-033](../tasks/PEV-DEV-AGENT-033.md) 依 `skill_conventions.md` 補齊 13 份 skill 的落差
**審查載體**：分支 `PEV-DEV-AGENT-033`（無遠端 PR，依 `docs/standards/git_workflow.md` §8.3 降級）
**審查者**：code-reviewer
**結論**：**APPROVED**，無退回

---

## 1. 驗收標準逐條

| AC | 判定 | 證據 |
|---|---|---|
| AC-01 §1.10 補進缺的 8 份，每份針對該角色 | ✅ | 本篇 §2.1 逐份摘要；行號見 §2.3 |
| AC-02 §1.11 補進 13 份，同上 | ✅ | 本篇 §2.2；覆蓋率實測見 §2.3 |
| AC-03 引用格式一律用標準第 1 節 | ✅ | `uv run pytest` 全綠，含 `test_skill_引用守則的編號與標題都要對得上`（§5） |
| AC-04 `frontend-developer:37` 改寫為技術棧中立 | ✅ | 本篇 §3；`description` 未動 |
| AC-05 補齊後才標「適用全角色」，前後各跑一次 pytest | ✅ | 本篇 §4，兩次輸出俱在 |
| AC-06 超過 150 行者檔頭有超限理由 | ✅ | 3 份，本篇 §6 |
| AC-07 新增段落不得逐字重複，附最長共同子字串實測 | ✅ | 本篇 §7，兩輪量測 |
| AC-08 pytest／precheck／upgrade 三閘門 | ✅ | 本篇 §5 |
| AC-09 BACKLOG 重生含本工單 | ✅ | 本篇 §5 |

---

## 2. 補齊了什麼

### 2.1 §1.10 Commit 閘門 — 補 8 份（5/13 → 13/13）

原本只有施工側 5 份寫了 §1.10，因為它們有 `## 交付與回報格式` 這個容器。
上游 8 份沒有交付段落，**新章節是為它們各自寫的，不是把開發者那段搬過去**。
每份的切入點都是「這個角色的產出被 commit 時，會出什麼它專屬的錯」：

| Skill | 這條規範對它的具體意義 |
|---|---|
| `business-analyst` | BA 經常沒有工單分支、直接在整合分支上動 `brd.md`——**那種情況豁免不適用，事前同意照要**。 |
| `product-manager` | 改一條規格，Dev／QA／UIUX 三方基準同時變；訊息不能只寫「更新 PRD」，要指出哪一份下游產出會失效。 |
| `qa-test-planner` | `test_plan.md` 與追溯矩陣一起漂移；覆蓋率升降的原因只存在於訊息裡，diff 只看得到表格行數。 |
| `scrum-master` | 全團隊最常「順手改一格 Status 就提交」，而那些改動往往不在任何工單分支上。 |
| `security-engineer` | 查核表新增一條 = 所有既有設計的評審基準都變了；沒有訊息就無從判斷某設計是在哪一版下通過的。 |
| `system-architect` | 訊息只寫「更新 HLD」，等於把「哪天、基於哪條 NFR 否決了另一案」從歷史抹掉——那是日後推翻決策時唯一的依據。 |
| `tech-lead` | 規格與實作不符時要修哪一邊，取決於誰先變；訊息要寫明是**規格先行**還是**回填實作**，兩者處置相反。 |
| `uiux` | ASCII-art 的 diff 是大片空白位移，讀不出改的是資訊層級還是補了狀態；訊息必須指名畫面與狀態。 |

### 2.2 §1.11 文檔權威階序 — 補 13 份（0/13 → 13/13）

**這一章原本 0 覆蓋，等於對所有角色都不存在。** 補寫時的共同判準是：
每個角色最容易錯認的「那一層」並不相同，寫出它自己的那一層。

| Skill | 它最容易錯認的一層 |
|---|---|
| `backend-developer` | 舊工單（第 4 層）的欄位定義，當成現行 API 規格。 |
| `frontend-developer` | 既有元件庫（第 2 層事實）當成設計規範，繼承上一次的臨時處理。 |
| `devops-engineer` | 「線上正在跑的配置」當準則——它證明的是目前如此，不是應該如此。 |
| `code-reviewer` | 從已 `Done` 工單反推「本專案的規格」，把一次性決定當通則——**§1.11 本來就是為這個情境立的**。 |
| `qa-automation-engineer` | 從實作反推期望值，於是缺陷被抄進斷言並受測試保護。 |
| `qa-test-planner` | 從既有工單反推需求母體，分母縮成「有人開過單的部分」，矩陣反而顯示接近 100%。 |
| `scrum-master` | 把上一張相似工單整段複製當 `Inputs`；DN 也不得作 Inputs。 |
| `business-analyst` | 把 `Seed`／`Exploring` 的 DN 當定案寫進 BRD 的 To-Be。 |
| `product-manager` | 引用第 4 層工單來定義規格，讓下游執行紀錄反過來決定上游藍圖。 |
| `system-architect` | 把還在比較中的 DN 選項寫進 ADR，讓架構去實作沒被選中的方案。 |
| `tech-lead` | 從已合併的程式碼回填 `api_spec.md`，把漂移固化成規格。 |
| `security-engineer` | 拿「上次通過的設計」當基準，於是同一個未防禦面被連續判成通過。 |
| `uiux` | 沿用舊 mockup，把當時的臨時妥協當規範繼承。 |

### 2.3 覆蓋率與行號實測

```
backend-developer        §1.10:  36  §1.11:  18  總行數:39
business-analyst         §1.10:  63  §1.11:  62  總行數:63
code-reviewer            §1.10:  83  §1.11:  15  總行數:143
devops-engineer          §1.10:  44  §1.11:  20  總行數:46
frontend-developer       §1.10:  65  §1.11:  24  總行數:72
product-manager          §1.10:  60  §1.11:  59  總行數:60
qa-automation-engineer   §1.10: 260  §1.11:  43  總行數:263
qa-test-planner          §1.10: 199  §1.11: 198  總行數:199
scrum-master             §1.10: 172  §1.11: 171  總行數:172
security-engineer        §1.10:  44  §1.11:  43  總行數:47
system-architect         §1.10:  53  §1.11:  52  總行數:56
tech-lead                §1.10:  48  §1.11:  47  總行數:51
uiux                     §1.10:  59  §1.11:  58  總行數:65
```

§1.12 維持 13/13；§1.5／§1.9 維持在施工側 6 份（`backend-developer`、`code-reviewer`、
`devops-engineer`、`frontend-developer`、`qa-automation-engineer`、`scrum-master`），
與 `skill_conventions.md` 第 3 節的分層一致，**本張未擴大該分層**。

---

## 3. AC-04：`frontend-developer` 的技術棧中立改寫

改寫前（`:37`）：

```markdown
- **核心技術**：優先使用 HTML / React 結構搭配 **Vanilla CSS** 來達到靈活控制。切勿寫出無聊、死板、毫無互動感的介面。
```

改寫後（`:38`，行號因 §1.11 插入而後移一行）：

```markdown
- **樣式的控制權**：優先讓樣式層維持可直接調整的狀態，間距、動態與細節都要能精準改動，不要因為整套沿用現成主題而失去微調餘地。切勿寫出無聊、死板、毫無互動感的介面。**框架與樣式方案依專案既有技術棧，此處不指定**——本節管的是成品質感，不是選型。
```

**為什麼改寫後對非 React 專案不再是錯誤指令**（AC-04 明文要求回答這一題）：

原句是**指令性**的（「優先使用 X」）。裝在一個用 Vue、Svelte 或 server-side
template 的專案裡，agent 讀到的是一條要它偏離專案既有技術棧的指示——
而 SKILL.md 屬 `skill_conventions.md` 第 4 節所稱的第 1 層（跨專案通用），
第 1 層講的話在**每一個**安裝它的專案裡都成立才行。原句在多數專案裡不成立。

改寫後保住了原句真正想要的東西：**樣式層要保有微調餘地**。這個意圖在任何技術棧
下都成立——Vue 的 scoped style、Svelte 的 component style、甚至純 CSS 都能滿足它。
「不要因為整套沿用現成主題而失去微調餘地」把原本用「Vanilla CSS」這個具體選型
表達的顧慮，還原成它背後的判準，於是判準可以跨技術棧套用，而選型交還給第 2 層。

**未動的部分**：

- **frontmatter `description` 原封不動**——依 `skill_conventions.md` 第 4 節的界線，
  那一欄是 skill 的觸發關鍵字，框架名列得越全召回越準，與「規定專案該用什麼」無關。
- **`:40` 的「採用現代感字體 (如 Inter 或 Roboto)」保留**——句型是「如」而非「應使用」，
  屬第 4 節認定的舉例句，不會擋掉選型。

**殘留掃描**：對 13 份的正文（排除 frontmatter）掃「框架名 ＋ 指令性動詞」的組合，
結果為空。掃描腳本的框架清單涵蓋 React／Vue／Angular／Svelte／Next.js／Django／
Flask／FastAPI／Express／Pytest／Jest／Vitest／Playwright／Cypress／Tailwind／Vanilla CSS，
指令性動詞涵蓋「優先使用／必須使用／應使用／一律使用／不可自行引入／請使用」。

⚠️ **這是輔助掃描，不是閘門。** 它抓不到沒用上述動詞的硬指令，
也抓不到清單外的框架名——第 4 節本來就是人工判準（判斷句子搬到別的技術棧會不會出錯），
沒有機器判準，這點與第 6 節同理。

---

## 4. AC-05：順序與兩次 pytest

`028` 刻意把「標記」留給本張，理由是 `tests/test_kit_integrity.py` 的
`test_適用全角色的章節被十三份_skill_全部引用` 直接讀 `team_protocol.md` 的標記，
**標了就要求 13 份全數引用**。當時 §1.11 是 0/13，先標就會當場產生 13 筆紅。

本張的執行順序因此是：**先補齊 13 份 → 跑 pytest → 才加標記 → 再跑 pytest**。

**第一次（補齊完成、尚未標記）**：

```
141 passed in 16.31s
```

**加標記**（`kit/.agent/resources/team_protocol.md`）：

- §1.10 開頭加 `**適用全角色。**「有產出就會 commit」對十三份 skill 都成立——上游側的
  BRD／PRD／HLD／wireframe 同樣是檔案，同樣要進版控；差別只在改的是什麼，不在要不要過閘門。`
- §1.11 開頭加 `**適用全角色。** 每個角色都得回答「現在的規格是什麼」，而各自最容易錯認的
  那一層並不相同——施工側常把程式碼現況當準則，上游側常把已結案工單或未收斂的 Design Note 當定案。`

標記的措辭把 `028` 寫進標準第 3 節的理由**搬進了正版**：
「有產出就會 commit」對 13 份都成立，所以「上游不需要 §1.10」不成立。

**第二次（標記完成）**：

```
141 passed in 8.08s
```

兩次都是 141 passed。若順序顛倒，第一次就會是 13 筆 fail——**兩次都綠本身就是順序正確的證據**。

**未動指路檔**：`kit/docs/standards/team_protocol.md` 的章節索引只列編號與標題
（`:28`、`:29`），本次沒有改章節標題或結構，因此 `test_指路檔章節索引與正版同步` 不受影響。

---

## 5. 閘門

| 閘門 | 結果 |
|---|---|
| `uv run pytest` | **141 passed**（標記前後各一次，皆綠；起點亦為 141，本張不新增測試） |
| `python3 .agent/scripts/precheck.py` | **7 項全部通過**，exit 0 |
| `./install.sh . --upgrade --dry-run` | 新增 0、更新 14、已是最新 47、保留 4、**待合併 0** |
| `./install.sh . --upgrade` | 同上，實跑完成 |
| BACKLOG 重生 | `scan_backlog.py --format backlog --output docs/development/BACKLOG.md`，本工單以 `Done` 列入 |

`test_適用全角色的章節被十三份_skill_全部引用` 現在覆蓋 §1.10、§1.11、§1.12 三章——
本張把它的守備範圍從 1 章擴到 3 章，而**測試碼一行未改**：檢查是從規範標記推導的，
規範改了檢查自動跟上。這正是 `026` 設計它時要的性質。

---

## 6. AC-06：篇幅例外

補寫後有 3 份超過 `skill_conventions.md` 第 7 節的 150 行軟上限，各自在檔頭
（`> **📏 篇幅例外**`，位於 frontmatter 之後、前置閱讀之前）寫明理由：

| Skill | 行數 | 理由摘要 |
|---|---|---|
| `scrum-master` | 172 | 唯一貫穿工單生命週期全程的角色；拆檔會讓「開單當下該查什麼」與「收尾該做什麼」分離，而兩者必須同時在場。 |
| `qa-test-planner` | 199 | Test Plan 與追溯矩陣是**可直接套用的樣板**；刪掉範例會把它從樣板降級成說明，而說明無法被複製貼上。 |
| `qa-automation-engineer` | 263 | 同時承接「Test Plan 轉譯」與「實際撰碼」；且第 2 層（框架、路徑）由專案 CLAUDE.md 補，**第 2 層缺席時本篇仍須可用**。 |

`code-reviewer` 補寫後為 143 行，仍在上限內，未加註記。

行數是腳本實算後填入的（含本次插入的 2 行），不是估計值。

---

## 7. AC-07：逐字重複的實測

判準是人工的（`skill_conventions.md` 第 6 節刻意不設機器門檻），
所以這裡提供的是**事實**：13 份新增段落兩兩之間最長共同子字串的長度與內容。
78 組配對全數計算。

**第一輪（未遮蔽）**：最大 59 字。

```
   59 字  qa-automation-engineer × tech-lead  →  '。依.agent/resources/team_protocol.md§1.11文檔權威階序，程式碼現況是第2層的事實'
   55 字  business-analyst × security-engineer  →  '依.agent/resources/team_protocol.md§1.11文檔權威階序，已結案工單是第4層'
   54 字  qa-test-planner × scrum-master  →  '行，超過docs/standards/skill_conventions.md第7節的150行軟上限。理由：'
   52 字  product-manager × security-engineer  →  '要進版控（.agent/resources/team_protocol.md§1.10Commit閘門）'
```

**這些長串幾乎全是規範自己要求逐字一致的東西**，不是抄襲：

- `.agent/resources/team_protocol.md §1.X 章節標題` 是 `skill_conventions.md` 第 1 節
  規定的**唯一**引用格式，改寫它反而會讓 `test_skill_引用守則的編號與標題都要對得上` 轉紅；
- 篇幅例外句型是本張 AC-06 自訂的模板，理由文字在冒號之後立刻分岔。

**第二輪（遮蔽上述兩類固定字串）**：最大 16 字，而那 16 字是路徑片段 `docs/standards/s`，
最長的**散文**重疊為 15 字。

```
   16 字  qa-automation-engineer × security-engineer  →  'docs/standards/s'
   15 字  code-reviewer × scrum-master  →  '已結案工單不改、也不引用；需要'
   13 字  qa-automation-engineer × tech-lead  →  '，程式碼現況是第2層的事實'
   12 字  scrum-master × system-architect  →  'DesignNote不在'
   11 字  devops-engineer × security-engineer  →  '是缺陷，不是可以援引的'
   10 字  business-analyst × system-architect  →  'DesignNote'
```

對照 `PEV-DEV-AGENT-025` 抓到的 `backend` × `frontend` §1.12 逐字重複為 **75 字**。

**中途做過一次收斂**：第二輪初測時最大為 29 字
（`product-manager` × `scrum-master`：「需要引用進行中的工作時，只引開放工單並註明其Status。」），
與 23 字（`business-analyst` × `system-architect` 的 DN 句型）。兩處都是**同一條規範的同句型複述**，
於是各自改寫成角色專屬的說法（PM 版強調「讀 PRD 的人才知道那段是暫定的」；
BA 版強調「BRD 的說服力建立在既成事實上」），最大值因此從 29 降到 16。

⚠️ **殘留的 15 字仍是 §1.11 條文原文的轉述**（「已結案工單不改、也不引用」）。
判定為可接受：那是規範條文本身的用語，兩個角色都必須引用同一條規則，
而**引用同一條規則不等於用同一段話解釋它**——兩份的前後文完全不同
（`code-reviewer` 講的是退回誤判，`scrum-master` 講的是 `Inputs` 取材）。

---

## 8. 沒做什麼

- **未動 `skill_conventions.md` 的規則本身**——本張是套用標準，不是修訂標準（工單 §5）。
- **未動任何 frontmatter `description`**——第 4 節的界線明文排除它。
- **未把第 6 節硬化成自動檢查**——`025` 已經誠實記錄過 12 字門檻是判斷不是事實。
- **未擴大 §1.5／§1.9 的施工側分層**——那 6 份的認定沿用 `028`，本張沒有重新裁定。
- **未改任何已結案工單與其審查紀錄**（§1.11 第 4 層：不改、也不引用）。
- **未 push、未重寫歷史。**

---

## 9. 退回項目

**無。** 9 條 AC 全數通過，三道閘門全綠。
