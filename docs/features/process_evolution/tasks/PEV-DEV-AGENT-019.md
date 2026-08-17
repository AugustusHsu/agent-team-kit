# [Task ID: PEV-DEV-AGENT-019] CI adapter：出貨薄 workflow，並讓本 repo 的 commit 第一次真的跑到 CI

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Pending
**📅 建立時間 (Created):** 2026-08-17T19:03+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

[DN-007](../../../design_notes/DN-007_ci_gate.md) §1 的落差：**kit 出貨的規範要求 CI 當閘門，
但 kit 一份 CI 都沒出貨。** `git_workflow.md` 三處指向它——§6.1 裁定 4「CI 紅燈硬擋合併」、
§8.1 能力對照表把「自動檢查」列為 kit 要求的能力、§8.2 設定清單「合併前必須通過 CI ✅ 開」
——但 `kit/.github/` 不存在，裝了 kit 的專案手上沒有任何東西可抄。

本工單接上 `PEV-DEV-AGENT-018` 產出的 `precheck.py`，補完 adapter 的另一半。

**還有一個本 repo 自己的問題要一併解決**：`.github/workflows/ci.yml` 只在
`push` 到 `main` 與 `pull_request` 觸發，而開發全程在整合分支上、又不開 PR——
到 `2026-08-17` 為止 `feature/kit-dev-process` 領先 `main` **37 顆**，
**這批 commit 從來沒跑過 CI**。DN-007 §4 #4 把這個中間態命名為
「**有遠端但不推送**」：`git_workflow.md` §8.3 只降級了「無遠端」，這第三種模式沒有規範接。
使用者裁定的解法是**改觸發條件**，不是改用 PR。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - **前置**：[PEV-DEV-AGENT-018](PEV-DEV-AGENT-018.md) 的 `precheck.py`
    ——DN-007 §5 訂了不可調換的順序，先接 CI 會讓薄 YAML 指向不存在的腳本
  - [DN-007](../../../design_notes/DN-007_ci_gate.md) §4.1 #4／#6、§4.2（連帶改寫清單）
  - `kit/docs/standards/git_workflow.md` §8.1 能力對照表、§8.2、§8.3
  - `.github/workflows/ci.yml`（本 repo 現況，兩個 job）
- **Outputs (輸出/預期變更)**：
  - **新增 `kit/.github/workflows/`** 薄 workflow
  - `kit/docs/standards/git_workflow.md` §8.1 補「檢查內容」欄、§8.3 補第三種模式
  - `.github/workflows/ci.yml`：`on.push.branches` 擴及開發分支；`stdlib-only` job 加跑 `precheck.py`
  - `install.sh` 與 `tests/test_install.py` 的排除清單**若需調整必須兩邊同步**（見 CLAUDE.md 陷阱）

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：`kit/.github/workflows/` 下的 workflow **只做 checkout ＋ 呼叫 `precheck.py`**，
      不含任何專案測試指令、不含 `uv`。第 2 層留給專案自己填，且該處要有註解說明怎麼填。
- [ ] AC-02：`git_workflow.md` §8.1 能力對照表新增「檢查內容」欄，內容與 `precheck.py`
      實際跑的四項一致——**表格寫五項而腳本跑四項就是不通過**。
- [ ] AC-03：§8.3 新增「有遠端但不推送」這第三種模式的處置，明說它跟「無遠端」的差別。
- [ ] AC-04：`test_安裝後檔案與_kit_完全一致` 通過——新增 `kit/.github/` 後，
      預期清單要涵蓋它（既有規則：kit 檔案 ＋ `.agent/.kit-manifest`）。
- [ ] AC-05：本 repo `.github/workflows/ci.yml` 的 `on.push.branches` 涵蓋 `feature/**`
      與 `PEV-*` 這類開發分支；`stdlib-only` job 新增 `precheck.py` 的執行。
- [ ] AC-06：**推送後到 GitHub Actions 確認 workflow 實際被觸發且通過**。
      ⚠️ YAML 語法正確不等於有跑——DN-007 §4 #4 記的正是「以為有 CI，其實從沒跑過」。
      此 AC 的證據必須是 run 的 URL 或 `gh run list` 的輸出，不接受「應該會跑」。
- [ ] AC-07：`uv run pytest` 全綠，`./install.sh . --upgrade --dry-run` 顯示「待合併 0」。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：
  - 無。出貨形式（C）、觸發方式（改觸發條件而非開 PR）、兩份 YAML 不收斂但共用腳本，
    皆由 DN-007 §4.1 裁定。
- **✍️ User 補充回覆 (User Input)**：
  - （2026-08-17）「CI 要怎麼第一次真的跑起來」選「改觸發條件」，不開 PR。
