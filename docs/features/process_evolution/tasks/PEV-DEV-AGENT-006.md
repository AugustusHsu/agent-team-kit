# [Task ID: PEV-DEV-AGENT-006] scrum-master 加上「開單前置關卡」

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T10:20+08:00
**✅ 完成時間 (Closed):** 2026-08-17T17:40+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

DN 機制的進場點在 scrum-master 身上——**它是唯一會開工單的角色**。
規範寫在 `documentation_conventions.md`（PEV-DEV-AGENT-004）不代表它會被執行：
skill 不讀規範就不會照做。

DN-001 §3.2 的判準只有一條，簡單到可以直接寫進 SKILL.md：

| 情境 | 動作 |
|---|---|
| **當場寫得出可驗收的 AC** | 直接開工單，**不要開 DN** |
| 寫不出來——方案沒定、邊界不清、影響範圍未知 | **先開 DN** |

必須同時寫進 evals，否則這條規則沒有任何執行期驗證
（PEV-DEV-AGENT-001 的教訓：改了四份 SKILL.md 卻漏掉 evals，測試全綠照樣放行）。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.2（進場規則）、§3.3（狀態）、§3.4（畢業條件，scrum-master 不得自行簽核）
  - `kit/.agent/skills/scrum-master/SKILL.md` 與 `evals/evals.json`
- **Outputs (產出物)**:
  - `kit/.agent/skills/scrum-master/SKILL.md`
  - `kit/.agent/skills/scrum-master/evals/evals.json`
  - 安裝同步

## 3. 驗收標準 (Acceptance Criteria)

- [x] SKILL.md 新增「開單前置關卡」段落，含上表兩列的判準
- [x] 明寫 **DN 不是工單**：不進 `scan_backlog.py` 的五狀態，
      也不得由 scrum-master 自行標 `Graduated`（§3.4 條件 3 只有使用者能簽）
- [x] 明寫 DN 的落點與取號方式（`docs/design_notes/`，全域扁平流水號）
- [x] `evals.json` 新增至少一筆：給一個「方案未定、寫不出 AC」的需求，
      expected_output 是**開 DN 而非開工單**
- [x] `evals.json` 通過 `test_evals_符合_skill_creator_schema`（id 連號、欄位齊全）
- [x] `evals.json` 不含來源專案識別資訊（`test_evals_不得殘留來源專案的識別資訊`）
- [x] `uv run pytest` 全綠
- [x] `./install.sh . --upgrade` 同步後 `git diff --stat` 只動到預期檔案

## 📝 Code Review 備註 (Review Notes)

> 審查日期：2026-08-17 ｜ 審查結論：✅ APPROVED
> 審查方式：作者自審 ＋ 客觀指標核對。依 `docs/standards/git_workflow.md` §8.3，
> 本工單不推送、無 PR，本章節即唯一審查載體，編號欄位填 `—`。

### 客觀指標核對（全部可重跑）

| 指標 | 期望 | 實得 |
|---|---|---|
| SKILL.md 新增「開單前置關卡」段落 | 1 | **1** ✅ |
| 判準表資料列 | 2 | **2** ✅ |
| 明寫「不進 `scan_backlog.py`／不套五狀態」 | 有 | **有** ✅ |
| 明寫 scrum-master 不得自行標 `Graduated` | 有 | **有** ✅ |
| 明寫落點與取號指令 | 各 1 | **各 1** ✅ |
| `evals.json` 筆數 | 4（id 1–4 連號） | **4** ✅ |
| `evals.json` diff | 只新增，不重排既有內容 | **+15 行、0 刪除** ✅ |
| `./install.sh . --upgrade` 更新檔數 | 2（SKILL.md、evals.json） | **2** ✅ |
| `uv run pytest` | 全綠 | **98 tests / 0 failures** ✅ |

### 為什麼 evals 這一筆不可省

PEV-DEV-AGENT-001 的教訓寫在工單描述裡：改了四份 SKILL.md 卻漏掉 evals，
測試照樣全綠。SKILL.md 是給 Agent 讀的散文，**沒有任何執行期驗證**；
evals 是唯一會把「這條規則有沒有被遵守」變成可判定輸出的地方。
新增的第 4 筆刻意用一個**方案未定的模糊需求**（「流程好像哪裡怪怪的」），
正確答案是**不開工單**——這是規則生效與否的分水嶺。

### 段落位置的取捨

「開單前置關卡」放在 `## 核心職責與執行邏輯` **之前**，不是塞進第 7 點
「嚴格把關完工定義」。理由是它要擋的是**動手寫工單之前**那一刻的決定；
放在核心邏輯裡面，讀到它時工單早就開下去了。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。
- **✍️ User 補充回覆 (User Input)**:
  -
