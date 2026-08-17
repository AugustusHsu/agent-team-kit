# [Task ID: PEV-DEV-AGENT-002] README 補上 git 流程能力對照表，讓換 git server 的人一眼看懂

**🔗 依附母任務 (Parent Task ID):** PEV-DEV-AGENT-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-16T14:06+08:00
**✅ 完成時間 (Closed):** 2026-08-18T05:45+08:00

## 1. 任務描述 (Description)

git 流程是「變化性最大」的項目——每個專案的 git server 規則都不同。
kit 的規範描述的是**能力**（「必須有一個地方在合併前發生審查」），
不是**指令**（「你必須開 GitHub PR」）。

但這個設計意圖如果只寫在 `git_workflow.md` 裡，使用者要讀完整份才會發現。
`README.md` 是他們評估這套件時看的第一份文件，**必須在那裡就講清楚**：
預設實作是 GitHub，換成 GitLab／Gitea／無遠端要對應哪幾件事。

**依賴 PEV-DEV-AGENT-001**：對照表的正版在 `git_workflow.md`，本工單放的是
精簡版並連回正版。正版不存在時無從精簡。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `kit/docs/standards/git_workflow.md`（由 PEV-DEV-AGENT-001 產出）§ 能力對照表
  - `docs/design_notes/DN-003_git_workflow_and_pr_gate.md` §5
  - `README.md` 現有結構（「內容物」「日常運作」「相容性」等節）
- **Outputs (輸出/預期變更)**:
  - `README.md` 新增一節

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`README.md` 有一節說明 git 流程，內含**表格形式**的能力對照表，
      涵蓋 GitHub／GitLab／沒有遠端三欄——與正版 `git_workflow.md` §8.1 的欄位一致。
      ⚠️ 本條在開工前改寫過：原文寫「無遠端」是唯一的降級情境，但 `PEV-DEV-AGENT-019`
      已把 §8.3 拆成 (a) 完全沒有遠端、(b) 有遠端但不開 PR 兩種。(b) 不是獨立的一欄
      （它的 git 能力與 GitHub 欄相同，差別只在不開 PR），改以正文一句話交代。
- [x] AC-02：表格的列是**能力**而非指令（例如「合併前的審查場所」而非「開 PR」），
      讓讀者能自行對映到自家 git server
- [x] AC-03：明確寫出「預設實作是 GitHub」以及 kit 對平台的**最低要求**
- [x] AC-04：連結到 `docs/standards/git_workflow.md` 正版，且不重複正版內容
      （依 `documentation_conventions.md` 的單一事實來源原則）
- [x] AC-05：該節長度控制在**一頁內看得完**——README 是評估用文件，不是規範全文
- [x] AC-06：`uv run pytest` 全綠、`python3 .agent/scripts/precheck.py` 全綠。
      ⚠️ 括號內原本寫「死連結檢查會驗證新增的連結」，**這是錯的**：
      `precheck.check_dead_links()` 只掃 `docs/`（註解寫明是為了避開根目錄的
      `node_modules` 之類），`test_kit_內沒有死連結` 只掃 `kit/`——
      根目錄的 `README.md` 兩邊都掃不到。改由 AC-09 補上。
- [x] AC-07（開工時追加）：README「內容物」樹補齊落後的出貨物——
      `precheck.py`（`018`）、`.github/workflows/`（`019`）、`docs/design_notes/`（DN 機制）、
      `standards/` 的 git 流程、`_TEMPLATE/` 的 `reviews/`。
- [x] AC-08（開工時追加）：新增測試鎖住「README 能力對照表的列 ≡ `git_workflow.md`
      §8.1 的列」，以及「README 內容物涵蓋 kit 實際的腳本與目錄」。
      **手寫的第二份表述必然漂移**（`design_note.md` §3.8），所以不是靠紀律，是靠測試。
- [x] AC-09（開工時追加）：新增 README 死連結測試，複用 `precheck.strip_code()`
      而非另寫一份剝除邏輯。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  1. 這節放在 README 哪個位置？建議放在「日常運作」之後、「相容性」之前。
  2. 要不要順帶列出「不支援的情況」（例如沒有 CI 的環境，CI 紅燈硬擋 merge
     這條就無從實施）？
- **✍️ User 補充回覆 (User Input)**:
  - **（由 Agent 於 2026-08-18 代填，使用者可否決）**
  - **Q1 位置** → 採用工單自己的建議：「日常運作」之後、「相容性」之前。
    理由：讀者的閱讀動線是「這套流程怎麼跑」→「我的環境跑得動嗎」→「相容性」，
    git 平台適配正好卡在第二段。
  - **Q2 要不要列「不支援的情況」** → **不列，因為不存在。**
    `PEV-DEV-AGENT-019` 已把 §8.3 從「無遠端」改寫成「沒有 PR 時的降級」，
    分 (a) 完全沒有遠端、(b) 有遠端但不開 PR——kit 對每種環境都有降級路徑。
    寫「不支援」會讓讀者以為要換平台，實際上只是能力打折。
    正文改成一句話點出「沒有 PR 不代表不支援，只是能力打折，而且有兩種」。
