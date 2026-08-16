# [Task ID: PEV-DEV-AGENT-011] commit 閘門的範圍：把關「進入主線」，不是每一顆 commit

**🔗 依附母任務 (Parent Task ID):** PEV-DEV-AGENT-003
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T16:00+08:00
**✅ 完成時間 (Closed):** 2026-08-17T16:40+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

使用者 2026-08-17 裁定：

> 「我認為在 worktree 上的 commit 不用詢問，等要 merge 回來再詢問即可，記得保留拓樸在 git 上」
> 「我認為這條規則也需要加到 kit 的通用開發流程內」

**這條規則目前是「半寫、且自相矛盾」。** `team_protocol.md` §1.10 同一節內部打架：

| 行 | 內容 | 判讀 |
|---|---|---|
| L158 | 「**任何 commit 之前**，都必須把 commit message 原文交付使用者複查」 | 每顆都要問 |
| L161 | 「複查對象是**已經寫下**、可用 `git commit --amend` 修改的訊息」 | 那顆顯然沒事前問過 |
| L164 | 「**閘門把關的是「進入主線的那則訊息」**」 | 這就是使用者的裁定 |

`commit-message.md` 同樣分裂：L94「未經複查的訊息不得進入**主線**」（範圍正確）
vs 步驟 6 標題「執行 Commit（**待使用者確認後**）」（每顆都要）。

**本工單不是推翻 DN-003，是補上它沒落地的那一半**——DN-003 已裁定閘門改為把關
「最終進入主線的那則訊息」（L164 就是它），只是 L158 那句舊的沒跟著改掉。
依 DN-001 §3.2，使用者已裁定、無待決事項、AC 當場寫得出來，因此直接開工單、不開 DN。

**最高槓桿處是 `kit/CLAUDE.md` 模板**：它叫每個專案把嚴格版（「commit 前必須把訊息
原文給我複查」）抄進自己的 CLAUDE.md，而 CLAUDE.md 是唯一每次請求都在 context 的檔案。
模板不改 ＝ 規則實際上以**錯的版本**在每個裝了 kit 的專案生效。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - 使用者裁定（2026-08-17，見上）
  - `kit/.agent/resources/team_protocol.md` §1.10（L158 vs L161／L164 的矛盾）
  - `kit/docs/standards/git_workflow.md` §3.1（「可自由推送」的論證，本工單沿用同一條理由）
  - PEV-DEV-AGENT-010 已立的規則：合併訊息第一行帶 Task ID（§6.1）
- **Outputs (產出物)**:
  - `kit/.agent/resources/team_protocol.md` §1.10（改寫，**不新增 `§x.y` 章節**）
  - `kit/.agent/workflows/commit-message.md`（步驟 5、6）
  - `kit/docs/standards/git_workflow.md` §4、§6.1
  - `kit/CLAUDE.md`（專案模板的 Commit 範例）
  - `CLAUDE.md`（本 repo 種子檔，安裝不覆蓋，須手改）
  - `tests/test_kit_integrity.py`：`已廢除的流程規則` 新增一列
  - `docs/design_notes/DN-006_...md` §7：只補一條論據，**不下判斷**

## 3. 驗收標準 (Acceptance Criteria)

- [x] §1.10 明寫**閘門在「離開工單分支」那一刻**，工單分支上的中間 commit 不需事前同意
- [x] §1.10 明寫**豁免的邊界**：直接在主線／整合分支上的 commit 不適用
- [x] §1.10 明寫**配套**：未經逐顆複查的中間 commit 更需要保留拓撲
- [x] §1.10 **沒有新增 `### x.y` 章節**（新增就得同步指路檔索引，見 `test_指路檔章節索引與正版同步`）
- [x] `commit-message.md` 步驟 5／6 的標題與內文不再暗示「每顆 commit 都要先問」
- [x] `git_workflow.md` §4 補上豁免明文，且理由與 §3.1「可自由推送」同源（保護的是共享歷史）
- [x] `git_workflow.md` §6.1 補上「合併訊息必須先經複查」，與 010 的 Task ID 規則並列
- [x] `kit/CLAUDE.md` 模板的 Commit 範例改為主線範圍措辭，且維持**三行以內**
- [x] 本 repo `CLAUDE.md` 同步（種子檔，`install.sh` 不會覆蓋）
- [x] `grep -rn '任何 commit 之前' kit/` → **0**（改動前為 1）
- [x] `tests/test_kit_integrity.py` 新增一列禁語，且對**改動前**檔案命中、改動後為 0（反證）
- [x] `grep -c '\[平台相關\]' kit/docs/standards/git_workflow.md` 維持 **9**
- [x] `uv run pytest` 全綠
- [x] `./install.sh . --upgrade` 後 `git diff --stat` 只動到預期檔案

## 📝 Code Review 備註 (Review Notes)

> 審查日期：2026-08-17 ｜ 審查結論：✅ APPROVED
> 審查方式：作者自審 ＋ 客觀指標核對。依 `docs/standards/git_workflow.md` §8.3，
> 本工單不推送、無 PR，本章節即唯一審查載體，編號欄位填 `—`。

### 客觀指標核對（全部可重跑）

| 指標 | 期望 | 實得 |
|---|---|---|
| `grep -rn '任何 commit 之前' kit/` | 0（改動前 1） | **0** ✅ |
| `grep -rn 'commit 前必須把訊息原文' kit/` | 0（改動前 1） | **0** ✅ |
| §1.10 內新增的 `###` 章節 | 0 | **0** ✅ |
| `grep -o '\[平台相關\]' … \| wc -l` | 9 | **9** ✅ |
| §9 檢查清單列數（含表頭） | 10 | **10** ✅ |
| `kit/CLAUDE.md` Commit 範例行數 | ≤ 3 | **3** ✅ |
| `./install.sh . --upgrade` 同步檔數 | 4（team_protocol、commit-message、git_workflow、manifest） | **4** ✅ |
| `uv run pytest` | 全綠 | **98 tests / 0 failures** ✅ |

### 新測試的反證（避免永遠綠的假測試）

禁語 `任何 commit 之前|commit 前必須把訊息原文` 對**改動前**的 `kit/` 命中 **2 處**：

```
kit/.agent/resources/team_protocol.md:158
kit/CLAUDE.md:79
```

正是本工單點名的兩處——§1.10 那句自相矛盾的舊規則，以及模板叫每個專案抄進
自己 CLAUDE.md 的嚴格版。改動後 **0 處**。

### 一項刻意的克制

DN-006 §7 的 ⭐ 待決**只補論據、沒有下判斷**。新論據是：中間 commit 既然明文免除
逐顆複查，拓撲保留就從「方便」升格為**配套條件**，而這個理由與有沒有 PR 平台無關，
所以它同樣壓在「有 PR → squash」那一支上。是否據此改判仍屬 DN 的範圍
（DN-001 §3.9：推翻已畢業的 DN-003 裁定 5 要走 DN）。

### 一項與流程的偏離（已依新規則）

本工單的**開單 commit 落在工單分支上**，而非像 010／007／004 那樣先在整合分支開單。
理由正是本工單所立的規則：整合分支上的 commit 需要事前同意，工單分支不需要。
把開單也收進分支，這一輪就只需要在合併點取得一次同意。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - **不裁定「有 PR 平台時是否也改 `--no-ff`」**——那會推翻 DN-003 裁定 5，
    依 DN-001 §3.9 屬於另開 DN 的範圍，DN-006 §7 已登記該待決。本工單只補論據。
  - 全域 `~/.claude/CLAUDE.md` **不在本工單範圍**，改法由使用者自行決定。
- **✍️ User 補充回覆 (User Input)**:
  - 2026-08-17：「我認為在 worktree 上的 commit 不用詢問，等要 merge 回來再詢問即可，
    記得保留拓樸在 git 上」／「我認為這條規則也需要加到 kit 的通用開發流程內」
