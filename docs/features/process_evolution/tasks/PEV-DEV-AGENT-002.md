# [Task ID: PEV-DEV-AGENT-002] README 補上 git 流程能力對照表，讓換 git server 的人一眼看懂

**🔗 依附母任務 (Parent Task ID):** PEV-DEV-AGENT-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-16T14:06+08:00
**✅ 完成時間 (Closed):**

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

- [ ] `README.md` 有一節說明 git 流程，內含**表格形式**的能力對照表，
      至少涵蓋 GitHub／GitLab／無遠端三欄
- [ ] 表格的列是**能力**而非指令（例如「合併前的審查場所」而非「開 PR」），
      讓讀者能自行對映到自家 git server
- [ ] 明確寫出「預設實作是 GitHub」以及 kit 對平台的**最低要求**
- [ ] 連結到 `docs/standards/git_workflow.md` 正版，且不重複正版內容
      （依 `documentation_conventions.md` 的單一事實來源原則）
- [ ] 該節長度控制在**一頁內看得完**——README 是評估用文件，不是規範全文
- [ ] `uv run pytest` 全綠（死連結檢查會驗證新增的連結）

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  1. 這節放在 README 哪個位置？建議放在「日常運作」之後、「相容性」之前。
  2. 要不要順帶列出「不支援的情況」（例如沒有 CI 的環境，CI 紅燈硬擋 merge
     這條就無從實施）？
- **✍️ User 補充回覆 (User Input)**:
  - [留空，由 User 閱讀後於此處親手填寫]
