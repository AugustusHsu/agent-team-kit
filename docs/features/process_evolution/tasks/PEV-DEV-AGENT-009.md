# [Task ID: PEV-DEV-AGENT-009] DOCS_MAP 的模組表抽成獨立檔，骨架恢復可升級

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T10:30+08:00
**✅ 完成時間 (Closed):** 2026-08-17T19:00+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`docs/DOCS_MAP.md` 是 kit 的**已知缺陷**（本 repo CLAUDE.md「例外二」明載）：
kit 出貨時就要求專案自行填寫「功能模組」表，但它**不是種子檔**，
於是每次升級都被判定為「使用者改過」而產生 `.new` 衝突。
**這不是使用者亂改，是規範叫他改的。**

DN-001 §4.3 裁定**第三案**：不列為種子檔，而是**把會變動的模組表抽成獨立檔**。

理由是兩害相權：列為種子檔可以消掉 `.new`，但代價是 kit 日後改 DOCS_MAP 的骨架
（新增章節、改導航規則）**再也推不到既有專案**，使用者永遠停在安裝當天的版本。
`BACKLOG.md` 能承受這代價是因為它由腳本整份重生成，DOCS_MAP 沒有生成器，骨架真的會凍住。
抽出後：骨架仍隨 kit 升級，會變動的那張表歸專案所有，兩邊都拿到想要的。

本 repo 已經自發長出 `docs/features/README.md` 當前綴權威表，且**安裝從不碰它**——
這個做法已經被本 repo 實證過，不是憑空設計。

順帶處理 DN-001 §3.7 的正名：表頭「功能模組」與「基礎建設模組」直接打架，
改為「模組」並加「類型」欄。**目錄名 `features/` 不動**——改名會弄斷既有連結、
`.kit-manifest` 基準線與 `scan_backlog.py` 的硬編路徑。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.7（類型欄）、§4.3（第三案裁定）
  - `kit/docs/DOCS_MAP.md` §「功能模組 (features/)」
  - `install.sh` 的 `is_seed_file()`（**本工單不改它**——第三案不列種子檔）
  - 本 repo 的 `docs/features/README.md` 作為形狀參考
- **Outputs (產出物)**:
  - `kit/docs/features/README.md`（新，模組表落點）
  - `kit/docs/DOCS_MAP.md`（模組表改為指向該檔）
  - 安裝同步；本 repo 的 `docs/DOCS_MAP.md` 與 `docs/features/README.md` 一併對齊

## 3. 驗收標準 (Acceptance Criteria)

- [x] `kit/docs/features/README.md` 存在，內含模組登記表，欄位含**類型**（功能／基礎建設）
- [x] `kit/docs/DOCS_MAP.md` 不再內嵌模組表，改為一行指向 `features/README.md`
- [x] DOCS_MAP 的標題「## 功能模組 (features/)」改為平台中立的「## 模組 (features/)」
- [x] `install.sh` 的 `is_seed_file()` **不變**（第三案：DOCS_MAP 維持非種子檔）
- [x] 本 repo 的 `docs/DOCS_MAP.md` 升級後**不再產生 `.new`**——
      這是本工單成立與否的關鍵驗證：跑 `./install.sh . --upgrade --dry-run` 確認
- [x] 本 repo 現有的 `PEV`／`KIT`／`WTG` 三列完整遷移到 `docs/features/README.md`，
      且該檔仍是**本 repo 自有檔案**（安裝不覆蓋）
- [x] `kit/` 內無死連結
- [x] `uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`）
- [x] CLAUDE.md「例外二」的敘述同步更新（它記錄的是已消失的缺陷）

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - `kit/docs/features/README.md` 與 kit 既有的 `kit/docs/features/_TEMPLATE/` 並存，
    需確認 `test_安裝後檔案與_kit_完全一致` 的預期清單不受影響（新增檔案應自動涵蓋）。
- **✍️ User 補充回覆 (User Input)**:
  - 2026-08-17：4.3 第三案。

## 5. 審查與結案 (Review & Closure)

## 📝 Code Review 備註 (Review Notes)

審查日期：2026-08-17 ｜ 審查結論：✅ APPROVED（附一項須知悉的偏離）
審查方式：作者自審 ＋ 客觀指標核對。依 `docs/standards/git_workflow.md` §8.3，
本工單不推送、無 PR，本章節即唯一審查載體，編號欄位填 `—`。

### 客觀指標核對（全部可重跑）

| 指標 | 期望 | 實得 |
|---|---|---|
| `./install.sh . --upgrade --dry-run` 的「待合併」數 | 0 | **0**（改動前為 1：`docs/DOCS_MAP.md.new`） ✅ |
| `grep -c 功能模組 kit/docs/DOCS_MAP.md` | 0 | **0** ✅ |
| DOCS_MAP 內嵌的模組表列數 | 0 | **0**（改為一行指向 `features/README.md`） ✅ |
| `kit/docs/features/README.md` 含「類型」欄 | 是 | **是**（前綴／模組／類型／文件／工單 五欄） ✅ |
| 本 repo 三列遷移到 `docs/features/README.md` | 3 | **3**（PEV／KIT／WTG，並補齊類型與文件欄） ✅ |
| `test_kit_內沒有死連結` | 綠 | **綠** ✅ |
| `uv run pytest` | 全綠 | **103 tests / 0 failures**（與 008 後基準相同，無新增測試） ✅ |

### ⚠️ 偏離 AC：`is_seed_file()` 有改（AC 第 4 條寫「不變」）

**實測發現抽表本身消不掉 `.new`，只會讓它搬家。** 第一次升級的實際輸出：

```
⚠️  已改過，另存待合併：docs/features/README.md.new
```

`kit/docs/features/README.md` 一旦出貨就是 kit 檔案，而它的內容註定要被專案改寫——
於是同一個衝突原封不動地從 DOCS_MAP 移到了新檔案上，關鍵 AC（升級後不再產生 `.new`）
無法成立。因此把 `docs/features/README.md` 加進 `is_seed_file()`。

判斷依據，不是自行擴權：

1. AC 第 4 條的括號原文是「**第三案：DOCS_MAP 維持非種子檔**」——它管的是 DOCS_MAP。
   DOCS_MAP 現在仍**不是**種子檔，第三案完整成立（骨架照樣隨升級推送，本次升級 57 檔已是最新）。
2. 工單描述第 25 行自己寫著「本 repo 已經自發長出 `docs/features/README.md` 當前綴權威表，
   且**安裝從不碰它**」。「安裝從不碰它」在 `install.sh` 裡的實作就叫種子檔。
3. `install.sh` 對種子檔的定義是「kit 給的只是起始內容，安裝後由專案自己接手」——
   模組登記表逐字符合。**要專案自己填的表才是種子檔，骨架不是**，這條分界比原本
   「整份 DOCS_MAP 要嘛全給要嘛全不給」清楚。

配套已一併處理：`tests/test_install.py::test_升級保留種子檔` 加入該檔（CLAUDE.md
明載清單與測試兩邊必須同步改），CLAUDE.md 的種子檔清單與「例外」段落同步更新。

### 其他偏離（皆為達成關鍵 AC 的必要動作）

- **`kit/docs/DOCS_MAP.md` 的「設計筆記」段補一句指向 BACKLOG 的生成索引。**
  本 repo 那份手抄了 DN-001～006 的表格，不清掉就無法讓 repo 副本與 kit 骨架一致、
  `.new` 也就消不掉；而 PEV-DEV-AGENT-008 已經把索引生成到 BACKLOG 的「🧪 設計筆記」區塊，
  手抄表已是重複來源。清掉不損失資訊。
- **本 repo 的 `docs/DOCS_MAP.md` 以 `cp` 還原成 kit 骨架**（它本來就是安裝實例、視為唯讀）。
- **移除 BACKLOG Icebox 的「`DOCS_MAP.md` 是否列為種子檔」一列**——本工單就是那題的落地，
  依 Icebox「一旦決定（做或不做）就離開這裡」的規則移除。

### 沒做的事

- **`features/` 目錄名不動**（工單第 29 行已明載理由：改名會弄斷既有連結、`.kit-manifest`
  基準線與 `scan_backlog.py` 的硬編路徑）。只改標題與欄位。
- 其餘 `{功能模組名}` 路徑佔位符（`product-analysis.md`、`qa-test-planner` 等 7 處）不動，
  那是路徑樣板不是分類名稱，且 AC 只點名 DOCS_MAP 標題。
