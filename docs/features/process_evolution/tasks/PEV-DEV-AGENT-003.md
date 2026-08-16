# [Task ID: PEV-DEV-AGENT-003] 無遠端專案的合併方式降級為 `--no-ff`，補上 squash 前提不成立時的缺口

**🔗 依附母任務 (Parent Task ID):** PEV-DEV-AGENT-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-16T15:20+08:00
**✅ 完成時間 (Closed):** 2026-08-17T00:15+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`git_workflow.md` §2 裁定 5 給 squash 的理由寫得很明白：

> squash 讓兩者**同時成立**——過程 commit **留在 PR 內可追溯**，主線上仍是一張工單一顆。

**squash 的代價是用「PR 會保存過程 commit」付掉的。** 但 §8.3 的無遠端降級只換掉了
審查載體、自動檢查、Done 訊號與載體編號欄位，**獨漏合併方式**。無遠端專案照字面走
= squash + `git branch -D` = 過程 commit 成為 dangling object，gc 一跑就永久消失，
沒有任何東西接住——這正是 §2 裁定 5 認為「不可接受」而特地用 PR 換掉的那個代價。

本工單把合併方式納入 §8.3 的降級範圍：無遠端改用 `--no-ff`，
「一張工單一顆 commit」改由讀取時的 `--first-parent` 達成。
核心取捨是：**細節在讀的時候略過，而不是在寫的時候銷毀。**

本 repo 自身就是受害者——PEV-DEV-AGENT-001 原本以 squash 合併，四顆過程 commit
已成 dangling（Phase 0 已重做為 `--no-ff` 救回，樹雜湊不變）。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `kit/docs/standards/git_workflow.md` §2 裁定 5、§6.1、§6.4、§8.1、§8.3、§9
  - `kit/.agent/skills/code-reviewer/SKILL.md`（回填欄位的理由句）
  - `tests/test_kit_integrity.py` 的 `已廢除的流程規則` 表
  - `docs/development/BACKLOG.md` Icebox
  - 已查證**不需改**：`kit/.agent/resources/team_protocol.md` L174-176 本來就同時涵蓋
    squash 與非 fast-forward 兩種合併訊息，平台中立
- **Outputs (輸出/預期變更)**:
  - `git_workflow.md` 六個章節共八處修改
  - `code-reviewer/SKILL.md` 一處理由一般化
  - 禁語表新增一列 ＋ 修正一列過期理由字串
  - 新增本工單檔案、BACKLOG 同步
  - 根目錄安裝實例經 `./install.sh . --upgrade` 同步

## 3. 驗收標準 (Acceptance Criteria)

- [x] §2 裁定 5 之後有 blockquote 明說「留在 PR 內可追溯」是**前提**而非附帶效果，並指向 §6.1／§8.3
- [x] §6.1 不再無條件 squash：拆成「有 PR／MR → squash」與「無遠端 → `--no-ff`」兩路
- [x] §6.4 驗證方式拆兩路：squash 比對樹（維持原規則）；`--no-ff` 用 `git branch -d` 成功作為證明，且明說不必比對樹、永遠不動用 `-D`
- [x] §8.1 能力對照表新增「合併方式（§6.1）」一列，無遠端欄為 `--no-ff`
- [x] §8.1 的「已合併」訊號無遠端欄由「主線的樹含該分支內容」改為「`git branch -d` 成功」
- [x] §8.1 表格說明由「這六列」改為「這七列」
- [x] §8.3 有獨立段落說明合併方式降級的理由，並附可直接照抄的四行指令範例
- [x] §9 檢查清單第 7 列措辭涵蓋兩種合併方式（不新增列）
- [x] `grep -o '\[平台相關\]' kit/docs/standards/git_workflow.md | wc -l` 仍為 **9**
- [x] `sed -n '/## 9\./,$p' kit/docs/standards/git_workflow.md | grep -c '^| .*|'` 仍為 **10**
- [x] `grep -rn '一律 squash' kit/ | wc -l` 為 **0**（改動前為 1）
- [x] `code-reviewer/SKILL.md` 的「不填 commit SHA」理由改為「回填當下合併還沒發生、commit 不存在」，對兩種合併方式皆成立
- [x] `已廢除的流程規則` 新增 `一律[^\n]{0,6}squash` 一列，且**經反證**：對改動前的 `git_workflow.md` 會命中、改動後為 0
- [x] `已廢除的流程規則` 中 `--is-ancestor` 那列的理由字串不再宣稱「§6.1 一律 squash」
- [x] BACKLOG Icebox「worktree 重新設計」由「待開 DN」改為指向已開出的 DN-006
- [x] `./install.sh . --upgrade` 後 `uv run pytest` 全綠，且 BACKLOG Icebox 未被 `scan_backlog.py` 清空
- [x] 本工單的實作直接落在整合分支 `feature/kit-dev-process`——使用者 2026-08-17 裁定
      不另開工單分支、本輪不併回 main。新立的 `--no-ff` 規則改由後續工單實跑（見 DN-006 §2 兩層拓撲）

## 📝 Code Review 備註 (Review Notes)

> 審查日期：2026-08-17 ｜ 審查結論：✅ APPROVED
> 審查方式：**作者自審 ＋ 客觀指標核對**（本輪未派獨立審查員，與 PEV-DEV-AGENT-001 不同，
> 據實記錄）。最終放行由使用者裁定（2026-08-17 核准計畫時一併認可本工單收尾方式）。
> 依 `docs/standards/git_workflow.md` §8.3，本工單不推送、無 PR，
> 本章節即唯一的審查載體，編號欄位填 `—`。

### 客觀指標核對（全部可重跑）

| 指標 | 期望 | 實得 |
|---|---|---|
| `grep -rn '一律 squash' kit/ \| wc -l` | 0（改動前 1） | **0** ✅ |
| `grep -o '\[平台相關\]' kit/docs/standards/git_workflow.md \| wc -l` | 9 | **9** ✅ |
| `sed -n '/## 9\./,$p' … \| grep -c '^\| .*\|'` | 10 | **10** ✅ |
| `grep -c '能填滿這七列' …` | 1 | **1** ✅ |
| 根目錄安裝實例與 `kit/` 一致 | 無 diff | **無 diff** ✅ |
| BACKLOG Icebox 資料列 | 13 | **13** ✅ |
| `uv run pytest` | 全綠 | **98 passed** ✅ |

### 新測試的反證（避免永遠綠的假測試）

禁語 `一律[^\n]{0,6}squash` 對**改動前**的 `git_workflow.md:124` 會命中，
改動後為 0——這條有真實鑑別力。

### 一項與原計畫的偏離

原計畫寫「§6.1 改為『有 PR 時**一律 squash**』」，實作時發現該措辭會被本工單
新增的禁語**自己命中**。已改為「合併方式取決於有沒有審查載體平台」的兩路寫法。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。裁定依據為 §2 裁定 5 的原文，AC 當場可驗收，依 DN-001 §3.2 直接開工單不另開 DN。
- **✍️ User 補充回覆 (User Input)**:
  -
