# 審查紀錄：PEV-DEV-AGENT-016

> 工單：[../tasks/PEV-DEV-AGENT-016.md](../tasks/PEV-DEV-AGENT-016.md)
> 本檔是 PEV-DEV-AGENT-016 新規則的**第一個適用對象**——規則要求完整審查報告落在
> `reviews/<TaskID>.md`，這份報告自己就這麼放。

## 2026-08-17 ✅ APPROVED

**審查人**：code-reviewer

### 📊 客觀指標

| 指標 | 變更前 | 變更後 |
|---|---|---|
| 全套測試／失敗數 | 110 / 0 | **111 / 0** |
| 本次新增測試的負向對照 | — | **確認會紅**（見下） |
| kit 內「完整報告寫進工單」的殘留（`git grep -c`） | **3 個檔各 1 處** | **0** |
| kit 內「最近 7 天」時間窗殘留（`git grep -c`） | **2 個檔各 1 處** | **0** |
| `已廢除的流程規則` 列數 | 9 | **11** |
| 冰箱資料列 | 5 | **4** |
| `./install.sh . --upgrade` 待合併 | — | **0**（新增 1、更新 7） |

**負向對照原文**：把 `scan_backlog.py` 的 `tasks_dir.glob("*.md")` 改成
`feature_dir.rglob("*.md")`，`test_reviews_目錄不會被當成工單掃描` 立刻轉紅：

```
AssertionError: 工單狀態被審查檔的 Done 蓋掉
- In Progress
+ Done
```

還原後回綠。這證明該測試咬的是「只掃 `tasks/`」這條前提本身，不是巧合通過。

### 1. 工單驗收標準核對表

- [x] `team_protocol.md` §2.3 有「審查紀錄的落點」條款——實查含審查檔路徑格式、
      工單只留的三樣東西、拆分理由、`scan_backlog` 不掃 `reviews/`、既有工單不追溯遷移
- [x] §1.8 退回回寫改指向審查檔（第 100 行）
- [x] `code-reviewer/SKILL.md` §4 回寫條款改為「兩份寫入」，無遠端路徑以審查檔為載體
- [x] `evals.json` 的舊 expectation 換成兩條新的（落點 + 工單只留三樣）
- [x] `kit/docs/features/README.md` 目錄慣例含 `reviews/<TaskID>.md`；
      根目錄種子檔 `docs/features/README.md` 手動同步（它的內容與樣板不同，
      沒有目錄慣例區塊，改的是開頭那句路徑說明）
- [x] `kit/docs/features/_TEMPLATE/reviews/README.md` 存在，且已隨升級裝進根目錄
- [x] `git_workflow.md` §8 對照表與 §8.3 均改為審查檔
- [x] `已廢除的流程規則` 新增 2 列，全 kit 掃描 0 命中
- [x] 新增 `test_reviews_目錄不會被當成工單掃描`，附負向對照
- [x] 本工單的完整審查報告即本檔
- [x] 冰箱移除「工單瘦身」列
- [x] `uv run pytest` 111 passed；`./install.sh . --upgrade` 待合併 0

### 2. 重大瑕疵清單

無。

### 3. 架構優化與建議

- 💡 **順手修掉的既有缺陷（不在原 AC 內，已納入本輪）**：
  - `code-reviewer/SKILL.md:128` 與 `scrum-master/SKILL.md:150` 仍寫著
    「近期結案僅顯示最近 7 天」。該時間窗已由 **PEV-DEV-AGENT-013** 移除，
    但 013 沒為自己加 `已廢除的流程規則` 列，殘留因此在 110 passed 底下隱形——
    這正是 `test_kit_不得殘留已廢除的流程規則` docstring 裡寫的「邊界一」失效案例，
    第二次發生。本輪一併改正並補上防線列。
  - `BACKLOG.md` 冰箱表格的表頭與資料列之間有一行空行（PEV-DEV-AGENT-014 刪列時留下），
    Markdown 會把它切成「空表格 + 四段文字」。一併補回。
- 💡 **建議**：`已廢除的流程規則` 漏加列已連續兩張工單發生。值得在 CI 工單
  （DN-007 下游）評估一個機械化提醒：偵測到 `kit/` 的規範文字被刪改時，
  要求同批 commit 必須動到那張表。

### 僅人工判讀的部分

- **「工單只留三樣東西」是否真能壓住膨脹**，要等下一張被退回過的工單才驗得到。
  本輪只有 APPROVED 路徑被實際走過。
- **既有 14 張工單不遷移**是依 `team_protocol.md` §1.11 的規範判斷，不是量測結果。
  代價是 repo 內同時存在兩種形態的審查紀錄，靠工單的 Closed 日期分辨。
- **備註章節的位置**：舊 SKILL 寫「放在『4. 人為補充與確認』之前」，但本 repo
  012–015 四張工單實際都放末尾。本輪把規範改成貼合實作（末尾），
  屬於消除規範與實作的既有矛盾，非新規則。

**結論**：通過。
