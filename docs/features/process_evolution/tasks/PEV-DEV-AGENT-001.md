# [Task ID: PEV-DEV-AGENT-001] 建立 git_workflow.md 並把 DN-003 的裁定落到出貨規範

**🔗 依附母任務 (Parent Task ID):** Independent
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-16T14:06+08:00
**✅ 完成時間 (Closed):**

## 1. 任務描述 (Description)

[DN-003](../../../design_notes/DN-003_git_workflow_and_pr_gate.md) 已畢業，
其裁定目前**只存在 DN 裡**。依 `team_protocol.md` §1.11 文檔權威階序，
DN 不在第 1 層，agent 讀規範時看不到它——**裁定必須落到出貨內容才會生效**。

本工單把 DN-003 的全部裁定寫成 kit 的正式規範，並改掉所有與新流程矛盾的舊敘述。

**為什麼範圍這麼大、不再往下拆**：依 DN-003 §3.3 判準 2「合併後系統仍可運作」，
若把「新建 `git_workflow.md`」與「改寫 §1.9／§1.10」拆成兩張，第一張合併後
會出現「新文件說先 commit 再審、§1.9 說 APPROVED 後才 commit」的**規範互相矛盾**
狀態。對照規範辦事的 agent 而言，那等同系統壞掉。

**本工單同時是 cutover 的前置**：DN-003 §7.1 定的規則生效點是「`main` 設為受保護
分支的那一刻」，而依 §8 執行順序，必須**先完成本工單再設保護**——否則本工單
自己就得遵守它正要產出的規則。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `docs/design_notes/DN-003_git_workflow_and_pr_gate.md` —— 唯一規格來源，
    §3.1／§3.2／§3.3／§3.4／§3.4.1 是必須落地的裁定，§4 三層結構與 §5 能力對照表
    是 `git_workflow.md` 的骨架
  - `kit/.agent/resources/team_protocol.md` §1.9（程式碼隔離與分支）、
    §1.10（Commit 閘門）—— 要改寫的對象
  - `kit/.agent/resources/task_template.md` —— 回填欄位要改
  - `kit/.agent/skills/{backend,frontend,devops,qa-automation}-developer/SKILL.md`
    與 `code-reviewer/SKILL.md` —— 五份交付／收尾提示
  - `kit/docs/standards/documentation_conventions.md` —— 新文件要遵守的撰寫慣例
- **Outputs (輸出/預期變更)**:
  - **`kit/docs/standards/git_workflow.md`（新建，主要產出）**
  - `kit/.agent/resources/team_protocol.md` §1.9／§1.10 改寫
  - `kit/.agent/resources/task_template.md` 回填欄位
  - 五份 SKILL.md
  - `kit/docs/DOCS_MAP.md`、`kit/docs/standards/README.md` 登記
  - `kit/docs/standards/team_protocol.md`（指路檔）章節索引
  - 根目錄安裝實例（`./install.sh . --upgrade`）

## 3. 驗收標準 (Acceptance Criteria)

- [ ] `kit/docs/standards/git_workflow.md` 建立，且含以下全部：
      L1 核心／L2 狀態對映／L3 平台適配的三層分離（DN-003 §4）、
      能力對照表（§5）、工單 × PR 狀態對映表（§3.4）、
      結案 commit 流程與「寫入時點 ≠ 生效時點」的說明（§3.4.1）
- [ ] 文件明確寫出五條裁定：`Done` = merged、工單 `In Review` 保留、
      Draft PR 於首次 push 時開、CI 紅燈硬擋 merge、合併用 squash
- [ ] 文件寫出回填 **PR 編號**（非 commit SHA）及其理由（squash 後 SHA 必變）
- [ ] 文件寫出 GitHub 設定要求，包含**必須關閉** "Dismiss stale pull request
      approvals"，並說明不關會造成結案 commit 讓 approve 失效的死循環
- [ ] `team_protocol.md` §1.9 生命週期表改為新流程；§1.10 commit 閘門改寫為
      「先 commit 再審，複查對象是已寫下、可 `--amend` 修改的訊息」
- [ ] **§1.9／§1.10 的章節編號未變**（既有交叉引用不得斷）
- [ ] 五份 SKILL.md 的「此時不要 commit」提示已改為新流程
- [ ] `task_template.md` 的回填欄位為 PR 編號，且**未使用 PR 時有明確預設值**
      （例如 `—`），不是留空——留空無法區分「沒有 PR」與「忘了填」
- [ ] `grep -rn "APPROVED 後才 commit\|此時不要 commit" kit/` **零命中**
- [ ] `kit/docs/DOCS_MAP.md` 與 `kit/docs/standards/README.md` 已登記
      `git_workflow.md`
- [ ] 指路檔 `kit/docs/standards/team_protocol.md` 的章節索引與正版一致
- [ ] `uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`、
      `test_指路檔章節索引與正版同步`、死連結檢查）
- [ ] `./install.sh . --upgrade` 後根目錄安裝實例同步，**除已知的
      `docs/DOCS_MAP.md.new` 外無其他 `.new` 衝突**

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  1. `git_workflow.md` 的章節切法：依 L1／L2／L3 三層各一章，還是依主題
     （分支／commit／PR／合併）切？DN-003 §7.2 把這條 defer 到本工單決定。
  2. `team_protocol.md` §1.9 有哪些內容該搬進 `git_workflow.md`、哪些留下？
     §1.9 目前是「git 流程定案前的最小保底規範」，定案後保底的定位消失。
     建議 §1.9 只留「一張工單 = 一個分支，分支名 = Task ID」與生命週期表，
     其餘全部指向 `git_workflow.md`。
  3. 五份 skill 改寫時，交付回報要不要附上 PR 連結？附了對 agent 是額外負擔，
     不附則審查者要自己找。
- **✍️ User 補充回覆 (User Input)**:
  - [留空，由 User 閱讀後於此處親手填寫]
