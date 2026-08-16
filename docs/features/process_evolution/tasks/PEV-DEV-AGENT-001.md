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
    是 `git_workflow.md` 的內容來源（但**不是章節結構**，見 §4 裁定一）
  - `kit/.agent/resources/team_protocol.md` —— 要改寫的對象，**共四處**：
    §1 狀態表（`Done` 的定義）、§1 狀態轉換表、§1.9、§1.10、§2.2
  - `kit/.agent/resources/task_template.md` —— 回填欄位要改
  - `kit/.agent/skills/{backend,frontend,devops,qa-automation}-developer/SKILL.md`、
    `code-reviewer/SKILL.md`、`scrum-master/SKILL.md` —— **六份**，非五份
  - `kit/.agent/workflows/commit-message.md` —— 第 105 行「要等審查 APPROVED
    之後才執行第 6 步」與新流程矛盾
  - `kit/docs/standards/documentation_conventions.md` —— 新文件要遵守的撰寫慣例
- **Outputs (輸出/預期變更)**:
  - **`kit/docs/standards/git_workflow.md`（新建，主要產出）**
  - `kit/.agent/resources/team_protocol.md` 四處改寫（含 `Done` 定義）
  - `kit/.agent/resources/task_template.md` 回填欄位
  - 六份 SKILL.md ＋ `commit-message.md`
  - `kit/docs/DOCS_MAP.md`、`kit/docs/standards/README.md` 登記
  - `kit/docs/standards/team_protocol.md`（指路檔）章節索引
  - 根目錄安裝實例（`./install.sh . --upgrade`）

**範圍修正紀錄（2026-08-16）**：開單時只列了 §1.9／§1.10 與五份 skill。
實際 `grep` 後發現與新流程矛盾的敘述**至少 13 處**，其中三處開單時完全沒看到：
`team_protocol.md` §1 狀態表把 `Done` 定義為 APPROVED（DN-003 裁定為 merged）、
`scrum-master/SKILL.md` 的 Epic 完成條件、`commit-message.md` 第 105 行。
**`Done` 的定義是狀態機的根，漏掉它會讓整套裁定落地失敗。**

## 3. 驗收標準 (Acceptance Criteria)

### 3.1 新文件 `kit/docs/standards/git_workflow.md`

- [ ] 章節依**主題**切，順序為：核心原則 → 工單 × git 狀態對映 → 分支 →
      commit → PR → 合併與收尾 → 平台適配 → 換平台檢查清單（§4 裁定一）
- [ ] **只有平台相關的規則帶 `[平台相關]` 標記**，L1／L2 不標
- [ ] 末章「換平台檢查清單」列出全部 `[平台相關]` 標記處，
      且**與正文的標記數量一致**（可 `grep -c` 驗證）
- [ ] 含 DN-003 §5 能力對照表六列，並保留
      「只要一個平台能填滿這六列，就能套用本流程」的結論
- [ ] 寫出五條裁定：`Done` = merged、工單 `In Review` 保留、
      Draft PR 於首次 push 時開、CI 紅燈硬擋 merge、合併用 squash
- [ ] 寫出回填 **PR 編號**（非 commit SHA）及其理由（squash 後 SHA 必變）
- [ ] 寫出「寫入時點 ≠ 生效時點」的推導（DN-003 §3.4.1）
- [ ] 寫出 GitHub 設定要求，含**必須關閉** "Dismiss stale pull request approvals"，
      並說明不關會造成結案 commit 讓 approve 失效的死循環
- [ ] 收錄 `git branch -d` 誤報「未合併」的陷阱與
      `git merge-base --is-ancestor` 的客觀驗證法（自 §1.9 搬入）

### 3.2 `team_protocol.md` 改寫（依 §4 裁定二的判準）

判準：**`team_protocol.md` 回答「工單走到這一步該做什麼」（狀態機）；
`git_workflow.md` 回答「git 這件事該怎麼做」（操作手冊）。**

- [ ] §1 狀態表的 `Done` 定義由「Code Reviewer 標記 APPROVED，工單正式完結」
      改為 **merged**，並明確 APPROVED 只是放行訊號
- [ ] §1 狀態轉換表「Code Reviewer 判定 APPROVED → `Done`」同步修正
- [ ] §1.9 **保留**：一張工單 = 一個分支、分支名 = Task ID、
      工單狀態 ↔ 分支／PR 動作對映表、`Done` 的前置條件
- [ ] §1.9 **搬出**：squash 理由、PR 編號 vs SHA、`git branch -d` 陷阱、
      平台設定、三層結構、「寫入 ≠ 生效」的推導過程（只留結論）
- [ ] §1.9 移除「本節是最小保底規範……待專案自行約定」的免責語
      （流程已定案，保底定位消失），改為指向 `git_workflow.md`
- [ ] §1.10 **保留**且改寫為「先 commit 再審，複查對象是已寫下、
      可 `--amend` 修改的訊息」；HITL 性質不變
- [ ] §2.2 交付回報「此時尚未 commit」改為新流程
- [ ] **§1.9／§1.10 的章節編號未變**——各有 7 處交叉引用（跨 7 個檔）不得斷

### 3.3 交付回報與回填時點（§4 裁定三）

- [ ] 規範以**平台中立**方式表述：交付回報**第一行須指出審查載體的位置**
      （GitHub = PR 連結／GitLab = MR／無遠端 = 分支名），不寫死 "PR 連結"
- [ ] **PR 編號的回填時點提前到「開 PR 當下」**（`In Progress` 階段），
      不再等結案 commit；結案 commit 只負責改 `Status` 與 `Closed`
- [ ] `task_template.md` 的回填欄位為 PR 編號，且**未使用 PR 時有明確預設值**
      （例如 `—`），不是留空——留空無法區分「沒有 PR」與「忘了填」

### 3.4 六份 skill ＋ workflow

- [ ] 四份 dev skill：「**此時不要 commit**」與「通過後才執行 commit
      並收尾分支」皆改為新流程
- [ ] `code-reviewer/SKILL.md`：「回填 commit SHA」改為 PR 編號；
      「APPROVED 只是放行訊號」段落與新的 `Done` = merged 定義一致；
      `Done` 的標記時點改為 merged 之後
- [ ] `scrum-master/SKILL.md`：Epic 推進至 `Done` 的條件由
      「最後一張子工單 APPROVED」改為「最後一張子工單 merged」（第 59、109 行）
- [ ] `commit-message.md` 第 105 行「要等審查 APPROVED 之後才執行第 6 步」改寫
- [ ] `task_template.md` 與 `_EXAMPLE-DEV-BE-001.md` 第 27 行
      「在最後一張子工單 APPROVED 時勾選」同步修正

### 3.5 一致性與驗證

- [ ] **矛盾敘述清零**，以下 grep 全部零命中（開單時的 pattern 只抓得到 4 處，
      已擴充）：
      `grep -rn "此時不要 commit\|通過後才執行 commit\|APPROVED 之後才執行\|commit 發生在 APPROVED 之後\|尚未 commit\|回填 commit SHA" kit/`
- [ ] `grep -rn "APPROVED" kit/` 的每一處都經人工確認語意仍成立
      （APPROVED 本身沒有被廢除，只是不再等於 `Done`）

> ⚠️ **grep 清零 ≠ 改完。** 上面那條 pattern 目前命中 13 處，但**抓不到**
> 最關鍵的三處——`team_protocol.md` §1 狀態表與狀態轉換表的 `Done` 定義、
> `scrum-master/SKILL.md` 的 Epic 完成條件——因為它們的措辭是
> 「判定 APPROVED → `Done`」「APPROVED 時勾選」，不含上列關鍵字。
> 那三處由 §3.2 與 §3.4 的逐條 AC 指名覆蓋，**不可只靠 grep 收工**。
- [ ] `kit/docs/DOCS_MAP.md` 與 `kit/docs/standards/README.md` 已登記 `git_workflow.md`
- [ ] 指路檔 `kit/docs/standards/team_protocol.md` 的章節索引與正版一致
- [ ] `uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`、
      `test_指路檔章節索引與正版同步`、死連結檢查）
- [ ] `./install.sh . --upgrade` 後根目錄安裝實例同步，**除已知的
      `docs/DOCS_MAP.md.new` 外無其他 `.new` 衝突**

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  1. ~~`git_workflow.md` 的章節切法~~ **已裁定**
  2. ~~`team_protocol.md` §1.9 哪些搬走、哪些留下~~ **已裁定**
  3. ~~交付回報要不要附 PR 連結~~ **已裁定**
- **✍️ User 補充回覆 (User Input)**（使用者於 2026-08-16 對話中裁定，
  由 agent 轉錄至此以符合 §1.11——裁定不落到工單，執行者就看不到）:

  **裁定一（章節切法）：依主題切，平台相關處加標記。**
  評估過三案：A 依 L1／L2／L3 三層、B 依主題、C 主題為主 ＋ L3 標記。
  A 的邊界清楚但把實務問題切散（光是「我要 commit」就得跨三章拼）；
  B 對 agent 友善但**可替換的邊界消失**，換 git server 時要逐章掃、容易漏。
  取 C：**主體依主題，只在平台相關的規則加 `[平台相關]`**（L1／L2 不標，
  標記量最小、漏標代價最小），末章附換平台檢查清單服務「換平台」這類讀者。

  **裁定二（§1.9 去留）：照「狀態機 vs 操作手冊」判準分配。**
  見 §3.2。§1.9 的定位從「保底規範」轉為「狀態機的 git 欄位」，
  留下的是工單走到某一步要做什麼，搬走的是 git 操作怎麼做。

  **裁定三（交付回報）：兩件都做。**
  (a) 規範寫成平台中立的能力要求「須指出審查載體的位置」，而非寫死 PR 連結；
  (b) **PR 編號回填提前到開 PR 當下**。原設計（DN-003 §3.4.1）等結案 commit
  才回填，但交付回報發生在 APPROVED 之前，那時工單裡還沒有 PR 編號，
  審查者無從找起。提前後工單自己就是唯一來源，交付回報不必重複貼。
  此細化**不回頭改 DN-003**——DN 畢業後轉為歷史紀錄，細化落在本工單。

  **另註（2026-08-16）**：skill 體系整體已久未更新，與現行流程的落差
  不只 git 這一項，另開 [DN-004](../../../design_notes/DN-004_skill_system_realignment.md)
  管理。本工單只處理 DN-003 裁定所涉的六份，不擴大範圍。
