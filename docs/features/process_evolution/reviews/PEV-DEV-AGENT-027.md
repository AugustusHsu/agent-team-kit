# 審查紀錄：PEV-DEV-AGENT-027

**👤 審查者 (Reviewer):** code-reviewer
**📅 審查時間 (Reviewed):** 2026-08-21T21:30+08:00
**🚥 結論:** 通過

---

## 1. AC 逐條核對

| AC | 結論 | 佐證 |
|---|---|---|
| AC-01 移除「不可自行引入其他框架」 | ✅ | `grep -rc '不可自行引入其他框架' kit/` → 0 檔命中；原第 43 行整段連同 §2 一起改寫 |
| AC-02 107 行程式碼範例移出本體 | ✅ | 386 → 255 行，**移出 131 行**；§4 |
| AC-03 skill 內留明確的第 2 層落點說明 | ✅ | 新 §2（`SKILL.md:41-64`），§3 |
| AC-04 殘留 pytest／cypress 逐筆判定 | ✅ | §5 |
| AC-05 「假設專案用 Jest」情境實跑 | ✅ | §6（含**一項實跑後才發現的修正**） |
| AC-06 本 repo 自己的第 2 層填上 | ✅ | `CLAUDE.md` 新增「測試技術棧」一節，§7 |
| AC-07 pytest 全綠、precheck 6 項全綠 | ✅ | §8 |
| AC-08 BACKLOG 重生 | ✅ | §8 |

---

## 2. 落點決定：專案 `CLAUDE.md`（工單 §2 要求寫進審查紀錄）

工單把落點留給執行時決定，候選是「skill 內留一個小節」或「指向專案 `CLAUDE.md`」。
**選 `CLAUDE.md`，而且這不是偏好問題——安裝機制已經把答案決定了。**

`install.sh` 的 `is_seed_file()` 只認四個檔：`CLAUDE.md`、`.gitignore`、
`docs/development/BACKLOG.md`、`docs/features/README.md`。這四個檔升級時永不覆蓋。
**skill 檔不在清單內**，所以：

> 落點若寫在 shipped `SKILL.md` 裡，每個專案填進去的框架與路徑
> **都會在下一次 `./install.sh --upgrade` 被 kit 的版本蓋掉**。

若堅持用獨立檔案當落點，就得擴充 `is_seed_file()` 並同步
`tests/test_install.py::test_升級保留種子檔`——為了一個小節新增一套種子檔機制，
成本明顯大於寫進 `CLAUDE.md`。

**而且 `CLAUDE.md` 本來就是這套規範既有的第 2 層落點**：`team_protocol.md` §1.12
的第 2 層原文就是「每個專案要在自己的 `CLAUDE.md` 記下三件事，缺了本節在該專案就是空的」。
選同一個落點是延續慣例，不是新增機制。理由已寫進 skill 本體（`SKILL.md:63-64`），
下一個讀到的人不必重推一次。

---

## 3. AC-03：第 2 層落點說明的寫法

比照 §1.12 的「缺了本節在該專案就是空的」句式，並把**不填的後果寫成具體行為**
而不是抽象警告（`SKILL.md:47-61`）：

- 要填的四件事逐條列出：框架與工具鏈／執行指令／存放路徑與命名／語言專屬風格；
- 後果：「你會照著自己的訓練資料猜一套框架與路徑，產出跑不起來的測試檔，
  或在專案既有的測試基礎設施旁邊另建一套」；
- 行為指令：「動手前先讀專案的 `CLAUDE.md`；那一節是空的就先問使用者，不要猜」；
- 優先序：「若第 2 層與你的預設習慣衝突，**以第 2 層為準**」。

最後一條是 AC-01 的正面版本。光刪掉「不可自行引入其他框架」只是移除禁令，
不會讓 agent 主動去讀專案的選型；補上優先序才把預設值換掉。

---

## 4. AC-02：移出了什麼、留下了什麼

386 → 255 行（−131）。移出的內容：

| 原章節 | 內容 | 行數 |
|---|---|---|
| §2.1 | 後端技術選型表、分層 Makefile 指令表、`backend/` 目錄樹、`conftest.py` fixture 清單 | ~55 |
| §2.2 | 前端技術選型表（Cypress／Next.js 16／shadcn／Zustand）＋「尚未安裝 Cypress」註記 | ~12 |
| §3.1 | Pytest AAA 範例（`TestCreateUser`） | 28 |
| §3.2 | Cypress AAA 範例（`describe('使用者登入')`） | 17 |
| §4.3 | Mock 範例（`@patch("app.services.oauth...")`） | 32 |
| §5.1 | Makefile 環境變數區塊、`user_management_test` 等具體資源名 | ~14 |
| §7.1／7.2 | `backend/tests/unit/`、`frontend/cypress/e2e/` 等具體路徑表 | ~14 |
| §8.2／8.3 | `asyncio_mode`、`client: AsyncClient`、`data-testid` 等專屬條款 | ~11 |

留下並改寫為技術棧中立的：AAA 三階段職責表與比例指引、Mock 判準
（改成「這個依賴會不會讓測試變得不可預測或不可重複」）、環境隔離的三項必要條件、
重構五步流程、命名原則、通用風格、交付格式。

**順帶修掉一處失效指路**：舊 §2.2 的「首次使用時需先執行環境設定（見 §6）」指向 §6，
但 §6 是「測試重構」，不是環境設定——那句連同整節一起移除了。

> **已知代價**（使用者裁定時已明示接受）：抽走範例後 skill 變抽象，
> 新專案沒有可抄的樣板。本輪不補樣板；第 2 層要求專案自己登記框架，
> 樣板應由專案自己的既有測試充當。

---

## 5. AC-04：殘留 pytest／cypress 逐筆判定

```
$ grep -rniE 'pytest|cypress' kit/.agent/skills/qa-automation-engineer/SKILL.md
3:description: ...或提到任何測試框架名稱（Pytest、Jest、Vitest、Playwright、Cypress、JUnit、go test 等）...
```

**只剩 1 筆，且是舉例性質。** 判定理由：

- 它在 `description` 裡，語意是「**使用者說了這個詞就啟動我**」，
  對產出沒有任何規定力；
- 它與 Jest／Vitest／Playwright／JUnit／go test **並列**，本身就是「任何框架」的例示——
  單獨列 Pytest／Cypress 才會構成偏好，並列六個不會；
- 這次順帶把 Jest 等四個補進去，正是為了讓非 Python 專案的使用者也觸發得到本 Skill。
  原本的關鍵字表只有 pytest／Cypress，**Jest 專案的使用者說「幫我寫測試」以外的話都叫不動它**。

另做一次機械掃描，確認沒有漏網的規定句（腳本 `jest_sweep.py`）：

```
=== 帶規定性語氣、且出現技術棧綁定符號的句子 ===
  L255 [Python 專屬: .py] - **🔄 刷新 BACKLOG**: ...`python3 .agent/scripts/scan_backlog.py ...`
  → 命中 1 句

=== 全文出現特定框架元件名的位置 ===   無
=== 全文出現建置工具指令的位置 ===     無
```

唯一命中的 `scan_backlog.py` 是 **kit 自己出貨的流程腳本**（純標準函式庫，
任何語言的專案裝了 kit 都跑得動），13 份 skill 都有同一行，與測試技術棧無關。

---

## 6. AC-05：「假設專案用 Jest」情境實跑

> ⚠️ **先講清楚範圍**：本環境沒有 node（`which node` → 指令找不到），
> 因此**沒有真的執行 Jest**。實跑的是「照這份 skill 在 Jest 專案走一遍」的情境，
> 加上 §5 的機械掃描。這一點不掩飾。

### 6.1 §9.1 八個步驟逐步走

假想專案：Next.js + Jest + Testing Library（unit/integration）+ Playwright（E2E）。

| 步驟 | skill 要求 | Jest 專案能不能做到 |
|---|---|---|
| 1 確認技術棧 | 讀專案 `CLAUDE.md` 第 2 層 | ✅ 專案填 Jest 即可，skill 沒有預設值要推翻 |
| 2 確認來源 | 讀 `test_plan.md` | ✅ 與語言無關 |
| 3 檢查既有測試 | `list_dir`／`grep_search` | ✅ 與語言無關 |
| 4 確認範圍 | 問使用者要寫哪些 Test ID | ✅ 與語言無關 |
| 5 撰寫測試 | 遵循 AAA、專案既有框架與慣例 | ✅ `describe`／`it` 完全容納得下 AAA |
| 6 執行驗證 | 用第 2 層登記的指令 | ✅ 專案登記 `npm test` 即可，skill 不再寫死 `make test-*` |
| 7 取證通道自檢 | `team_protocol.md` §1.12 | ✅ 與語言無關 |
| 8 回報 | 覆蓋率與通過率 | ✅ 不指定產生方式 |

### 6.2 照 skill 產出的 Jest 測試檔（第 2 層填 Jest 之後）

```javascript
// tests/unit/login.test.js
describe('使用者登入', () => {
  // 正確帳密應成功登入並取得 session (T-AUTH-001)
  it('正確帳密應成功登入並取得 session', async () => {
    // ── Arrange ──────────────────────────────────
    const payload = { email: 'admin@test.com', password: 'TestPass123!' }

    // ── Act ──────────────────────────────────────
    const res = await login(payload)

    // ── Assert ───────────────────────────────────
    expect(res.status).toBe(200)
    expect(res.body.session).toBeDefined()
  })
})
```

逐條對照 §8.1：函式名用「該語言的等價慣例」（`it('<行為>_<情境>')`）✅；
繁體中文說明與 Test ID ✅；AAA 三段以註解分隔 ✅；相關測試以 `describe` 分組 ✅。

### 6.3 實跑後發現並修正的一項

**§8.1 原本只示範 `# ── Arrange/Act/Assert ──`**，`#` 是 Python／shell 的註解語法。
雖然 §3 有一句「分隔符依專案語法而定」，但 §8.1 是規範條列、§3 是說明，
**條列贏過說明**——Jest 專案照著寫會產出語法錯誤的檔案。

修正兩處：

- `SKILL.md:220` §8.1 改為「用註解把 Arrange／Act／Assert 三段明確分隔
  （形式見本篇第 3 節，註解語法依語言而定）」，不再自帶示例；
- `SKILL.md:80` §3.1 同時列出 `#`、`//`、`/* */` 三種，並補一句
  「分隔本身是必要的，用哪種符號不是」。

**這正是 AC-05 要求「實跑而非形式檢查」的價值**——這一句過不了機械掃描
（`#` 不在任何框架名清單裡），只有真的把 Jest 檔案寫出來才會撞到。

---

## 7. AC-06：本 repo 自己的第 2 層

`CLAUDE.md` 新增「測試技術棧（`qa-automation-engineer` 第 2 層）」一節，
四件事逐條填齊：Pytest／`uv run pytest`／`tests/test_<被測腳本名>.py` 不分層／
中文測試名與 `pytest_generate_tests`。

**每條敘述都實測過才寫**，不是照印象寫：

| 敘述 | 查核 | 結果 |
|---|---|---|
| dev 依賴只有 pytest | `pyproject.toml` | `dev = ["pytest>=8"]` ✅ |
| 測試只用標準函式庫 | `grep -rhoP '^(import\|from) \S+' tests/*.py` | 只有 `pytest`＋stdlib＋`conftest` ✅ |
| 不分 unit／integration | `ls tests/` | 平鋪，一支腳本對一支測試檔 ✅ |
| 測試名一律中文 | 89 個 `def test_` | 89 個含中文，比例 100% ✅ |
| 用 `pytest_generate_tests` 不用 `parametrize` | grep | `parametrize` 0 檔、`pytest_generate_tests` 1 檔 ✅ |

**一處初稿寫錯、查核後改掉**：初稿寫「要 mock 就用 `unittest.mock` 與 `tmp_path`」，
但 `grep -rn 'mock\|Mock\|monkeypatch' tests/*.py` → **0 處**。
真實慣例是完全不 mock：用 `tmp_path` 造真實檔案、`subprocess` 實跑腳本再驗輸出。
改寫為那一條，並補上為什麼（要測的正是「腳本在真實檔案系統上做對了沒」，
mock 掉就什麼都沒驗到）。

`CLAUDE.md` 130 行，仍在 kit 模板規定的 200 行預算內。

---

## 8. AC-07／AC-08：閘門輸出

```
$ uv run pytest -q --no-header
137 passed

$ python3 .agent/scripts/precheck.py
6 項檢查全部通過。   exit=0

$ ./install.sh . --upgrade
  ⬆️  更新：.agent/skills/qa-automation-engineer/SKILL.md
  🌱 保留種子檔（由專案自行維護）：CLAUDE.md
  ── 升級摘要 ── 新增 0、更新 1、已是最新 59、保留 4、待合併 0

$ diff -q .agent/skills/qa-automation-engineer/SKILL.md kit/.agent/skills/qa-automation-engineer/SKILL.md
（無輸出＝一致）
```

**「保留種子檔：CLAUDE.md」這一行就是 §2 落點判斷的執行期證據**——
同一次升級把 skill 更新掉、卻原封不動保留了填著本 repo 測試技術棧的 `CLAUDE.md`。

---

## 9. 本工單在 026 的新檢查下觸發的紅燈（值得記錄）

027 是 026 上線後**第一筆真實的 skill 編輯**，第一次跑就被擋下來，抓到 3 筆：

```
qa-automation-engineer/SKILL.md:54 引用了不存在的 §8.1
qa-automation-engineer/SKILL.md:63 §1.12 的標題對不上：期望「取證通道保真」，實際「第 2 層一致，」
qa-automation-engineer/SKILL.md:225 引用了不存在的 §8.1
```

- **`:63` 是真錯**——我寫成「`team_protocol.md` §1.12 第 2 層一致」，漏了章節標題。
  已補為「§1.12 取證通道保真 的第 2 層一致」。**這正是 A+ 設計要抓的東西。**
- **`:54`／`:225` 是我引入的新構造**：用裸 `§8.1` 指**本篇自己**的章節。
  A+ 以「往前找最近的檔名」歸屬，而 `team_protocol.md` 在第 8 行就出現過，
  於是自我引用被判成跨文件引用。

### 9.1 為什麼不改 A+ 的判準

實測比較過兩種歸屬方式（腳本 `attr_test.py`）：

```
往前找最近檔名：45 筆
限同一行內    ：42 筆
改判準後不再檢查的：3 筆
  code-reviewer:17 §1.12 ✅正版有  |  §1.12 取證通道保真 跑一次開工自檢。...
  qa-automation-engineer:54 §8.1 ❌正版無
  qa-automation-engineer:225 §8.1 ❌正版無
```

改成「限同一行」雖然消掉兩筆誤判，**卻同時漏掉 `code-reviewer:17` 這筆真實的跨行引用**
（路徑在第 16 行、`§1.12` 在第 17 行）。用少一筆真實覆蓋去換兩筆對「語料中原本不存在的構造」
的誤判，不划算。

### 9.2 改的是寫法，不是判準

現行 13 份 skill **全部沒有自我引用**（普查 45 筆引用全指向 `team_protocol.md`／
`git_workflow.md`），也就是說「skill 不用裸 `§X.Y` 指自己」本來就是既有慣例，
只是從沒寫下來過，被我這次無意打破。9 處自我引用全部改為「本篇第 N 節」。

### 9.3 缺陷收容（§1.8）

依 §1.8 第一步「先判定成因落在哪張工單的範圍內」：**成因在 027**——
A+ 對它成文時的語料判定完全正確，是 027 引入了語料中不存在的構造。
因此**不退回 026、不新開 FIX 工單**，修正落在 027 自己的檔案內。

那條未成文的慣例則補進 `PEV-DEV-AGENT-028`（立 skill 撰寫標準）§2 的涵蓋表，
新增「自我引用格式」一列。028 目前是 `Pending`，依 §1.8 狀態表
「`Ready`／`Pending` → Status 維持不變，直接修正規格」，不需改動其狀態。

---

## 10. 退回項目

無。
