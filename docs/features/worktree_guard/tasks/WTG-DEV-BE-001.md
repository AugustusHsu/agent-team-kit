# [Task ID: WTG-DEV-BE-001] 補齊 worktree 防孤兒機制的登記欄位與對帳邏輯

**🔗 依附母任務 (Parent Task ID):** Independent
**🏷️ 任務類型 (Task Type):** queue_backend
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-13T02:39+08:00
**✅ 完成時間 (Closed):** —

## 1. 任務描述 (Description)

`kit/docs/standards/worktree_workflow.md` §6 定義了四層防孤兒機制，其中兩層目前
**只有文字、沒有實作**：

- **§6.1 入口登記**（號稱最重要的一層）要求「建立 worktree 的同時，在工單 `.md` 內
  記錄分支名與建立時間」。但 `task_template.md` 的 metadata 欄位只有 Parent Task ID /
  Task Type / Assignee / Status / Created / Closed，**沒有分支欄位**；
  `scrum-master/SKILL.md` 全篇不提 worktree，開單時也不會產生該欄位。
  結果是登記沒有固定形狀，只能靠 Agent 自由發揮往工單裡塞一行。
- **§6.2 對帳**要求 `scan_backlog.py` 讀取 `git worktree list` 與工單狀態對帳，
  輸出三類異常。但該腳本 579 行內 `grep worktree` 零命中，這層防護等於不存在。

**兩者必須一起做**：§6.2 要對帳的另一半就是 §6.1 登記的欄位，只做其中一邊沒有意義。

**急迫性來自 commit 時點的改變（cb4d0f4）**：新流程下 `In Review` 期間的變更
**沒有任何 ref 指著它**，只存在 worktree 的工作目錄與私有暫存區，
`git worktree remove` 一執行即永久消失。而 §6.2 是四層裡**唯一**能在 session
中途崩潰後事後對帳的一層（§6.4 的 session 結束回報在崩潰時完全無效）。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `kit/docs/standards/worktree_workflow.md` §6 —— 正版規格，三類異常的定義在 §6.2
  - `kit/.agent/resources/task_template.md` —— 要新增欄位的檔案
  - `kit/.agent/resources/team_protocol.md` §1.9（worktree 生命週期）、§3.2（檔案存放慣例）
  - `kit/.agent/scripts/scan_backlog.py` —— 重點看 `PATTERNS`、`find_project_root()`、
    `parse_task_file()`、`format_backlog_markdown()`
  - `kit/.agent/skills/scrum-master/SKILL.md` —— 開單時要產出新欄位
  - `tests/` —— 本套件自己的測試，`tests/fixture_project/` 可用來建構對帳情境
- **Outputs (輸出/預期變更)**:
  - `kit/.agent/resources/task_template.md`：新增 worktree 登記欄位
  - `kit/.agent/scripts/scan_backlog.py`：新增 worktree 對帳與異常輸出
  - `kit/.agent/skills/scrum-master/SKILL.md`：說明新欄位的填寫規則
  - `kit/docs/standards/worktree_workflow.md` §6.2：移除「⚠️ 尚未實作」警告
  - `tests/`：三類異常各一個測試

## 3. 驗收標準 (Acceptance Criteria)

- [ ] `task_template.md` 具備 worktree 登記欄位，且**未使用 worktree 時有明確預設值**
      （例如 `—`），不是留空——留空無法區分「沒開」與「忘了填」
- [ ] `parse_task_file()` 能解析該欄位，`PATTERNS` 有對應正則，欄位缺漏時回傳 `None`
      而非拋錯（既有工單沒有這個欄位，必須向後相容）
- [ ] `scan_backlog.py` 讀取 `git worktree list --porcelain`，並輸出 §6.2 表列的三類異常：
      疑似孤兒（有 worktree 但工單不在 `In Progress`/`In Review`）、
      可能繞過 worktree（工單 `In Progress` 但沒有對應 worktree）、
      純孤兒（worktree 對不到任何工單）
- [ ] **不在 git repo 內、或 `git` 指令不存在時不得 crash**，退化為略過對帳並提示
      （`scan_backlog.py` 是每次改工單都要跑的高頻腳本，不能因此變得脆弱）
- [ ] 三類異常各有一個測試，且「無異常」與「非 git 環境」各有一個測試
- [ ] `scrum-master/SKILL.md` 說明開單時如何填該欄位
- [ ] `worktree_workflow.md` §6.2 的「⚠️ 尚未實作」警告已移除
- [ ] `uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致` 與死連結檢查）

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  1. **欄位形狀**：§6.1 要記「分支名 + 建立時間」。要合成一欄
     （例：`**🔀 Worktree (分支 @ 建立時間):** —`）還是拆兩欄？
     建議合成一欄，避免 metadata 區塊膨脹。另外 emoji 用哪個？
     （先前已要求 worktree 相關標題不用 🌲）
  2. **異常輸出到哪**：只印 stderr，跑完就消失；還是也寫進
     `docs/development/BACKLOG.md` 頂端的「⚠️ Worktree 異常」區塊？
     建議兩者都做——寫進 BACKLOG 才能被看見。
  3. **偵測到異常時 exit code 要不要非零**？非零會擋住 CI 與自動化流程。
     建議維持 `0`，只警告不阻斷。
  4. **對帳範圍**：只看 `.claude/worktrees/` 底下的 worktree，還是 `git worktree list`
     回報的全部？主 checkout 那一行必須排除。使用者手動在別處開的 worktree
     算「純孤兒」還是忽略？
- **✍️ User 補充回覆 (User Input)**:
  - [留空，由 User 閱讀後於此處親手填寫]
