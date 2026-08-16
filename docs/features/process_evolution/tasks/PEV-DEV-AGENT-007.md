# [Task ID: PEV-DEV-AGENT-007] 出貨 `kit/docs/design_notes/`：DN 範本與目錄說明

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T10:05+08:00
**✅ 完成時間 (Closed):** 2026-08-17T15:10+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

kit 的規範要教 scrum-master「AC 寫不出來時先開 DN」，但 **`kit/docs/design_notes/` 不存在**——
裝了 kit 的專案沒有目錄、沒有範本、沒有狀態機。規範指向一個不存在的東西。

DN-001 §4.4 裁定**完整出貨**：目錄、範本、規範三者都給。本工單負責前兩者。

範本的 header 欄位依 DN-001 §4.1 的定案（實跑六份後的盤點結果）：

| 欄位 | 決定 | 理由 |
|---|---|---|
| 🚥 狀態 | 保留 | 6/6 有值且會變動 |
| 📅 建立 | 保留 | 6/6 有值 |
| 🔗 依賴 | 保留 | 6/6 有值，DN-001 §7 已實際拿它算過順序 |
| 📌 來源 | 保留，**改必填** | 5/6——DN-003 漏填，證明可選就是會漏 |
| 🎓 畢業去向 | **刪除** | 6/6 有欄位但 5/6 是「待填」；畢業當下 §6 與頂端標記本來就要寫 |
| 🤝 姊妹篇 | **新增** | 雙向關係塞進「依賴」會讓拓撲排序看到環，分不出「要等」與「必須同時設計」 |

**不出貨本 repo 的六份 DN 實例**——它們是本 repo 的歷史，對別的專案是噪音。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.1（落點與命名）、§3.3（狀態）、§4.1（欄位定案）
  - 既有實例 `docs/design_notes/DN-001` ～ `DN-007` 作為形狀參考
- **Outputs (產出物)**:
  - `kit/docs/design_notes/_TEMPLATE.md`
  - `kit/docs/design_notes/README.md`
  - `kit/docs/DOCS_MAP.md`（登記 `design_notes/`）
  - 安裝實例同步（`./install.sh . --upgrade`）

## 3. 驗收標準 (Acceptance Criteria)

- [x] `kit/docs/design_notes/_TEMPLATE.md` 存在，header 有 **5 個欄位**：
      狀態／建立／依賴／來源／姊妹篇；**沒有**「畢業去向」欄位
- [x] `_TEMPLATE.md` 含 DN-001 §3.3 的四狀態說明與 §3.4 的三條畢業條件
- [x] `_TEMPLATE.md` 含「⚠️ DN 不得寫實作步驟」的警語（DN-001 §3.9）
- [x] `kit/docs/design_notes/README.md` 說明取號方式（DN-001 §3.1 的 grep 指令）
      與「全域扁平、不放模組底下」的理由
- [x] `kit/docs/DOCS_MAP.md` 有 `design_notes/` 一列
      （⚠️ `test_standards_文件都登記在_DOCS_MAP` **只涵蓋 `standards/`**，這裡要人工確認）
- [x] `./install.sh` 裝到全新空目錄後，`docs/design_notes/_TEMPLATE.md` 存在
- [x] `uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`）
- [x] `kit/` 內無死連結（`test_kit_內沒有死連結`）

## 📝 Code Review 備註 (Review Notes)

> 審查日期：2026-08-17 ｜ 審查結論：✅ APPROVED
> 審查方式：作者自審 ＋ 客觀指標核對（含**裝到全新空目錄**的端對端驗證）。
> 依 `docs/standards/git_workflow.md` §8.3，本工單不推送、無 PR，
> 本章節即唯一審查載體，編號欄位填 `—`。

### 客觀指標核對（在 `/tmp` 全新安裝的目標專案上量測）

| 指標 | 期望 | 實得 |
|---|---|---|
| `ls <新專案>/docs/design_notes/` | `README.md`、`_TEMPLATE.md` | **兩者都在** ✅ |
| 範本 header 欄位數 | 5（狀態／建立／依賴／來源／姊妹篇） | **5** ✅ |
| 範本含 `**🎓` header 欄位 | 0 | **0** ✅ |
| 範本含四狀態列 | 4 | **4** ✅ |
| 範本含畢業三條件 | 1 | **1** ✅ |
| 範本含「DN 不得寫實作步驟」 | 1 | **1** ✅ |
| README 含取號指令 | 1 | **1** ✅ |
| DOCS_MAP 提及 `design_notes/` | ≥1 | **3** ✅ |
| `uv run pytest`（含死連結與安裝一致性） | 全綠 | **98 tests / 0 failures** ✅ |

### 兩項超出 AC、但有明確理由的決定

1. **狀態機與畢業條件放在範本的「📎 填寫指引（寫完可以整段刪掉）」段落。**
   AC 要求範本必須含這兩者，但若當成正文留著，每一份 DN 都會揹一份重複的規範副本。
   標成可刪的指引段落，既滿足「開檔當下看得到」，又不會製造 N 份會 drift 的副本。
2. **README 不放 DN 一覽表。** DN-001 §3.9 已定「索引用腳本生成」，
   手抄索引必然出現孤兒；此處明文寫下這條禁令，避免日後有人好意補一張表。

### 一個測試涵蓋不到、已人工確認的點

`test_standards_文件都登記在_DOCS_MAP` **只掃 `docs/standards/`**，
`design_notes/` 的登記沒有自動防線。已人工確認 DOCS_MAP 新增「設計筆記」一節，
且兩條連結都通過 `test_kit_內沒有死連結`。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。欄位、落點、出貨範圍全部由 DN-001 §4.1／§4.4 裁定，AC 當場可驗收。
- **✍️ User 補充回覆 (User Input)**:
  - 2026-08-17：4.4 完整出貨。
