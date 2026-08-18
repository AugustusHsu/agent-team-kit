# [Task ID: PEV-DEV-AGENT-029] 移除 kit 出貨內容裡硬編碼的 uv run

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-18T21:40+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

[DN-004](../../../design_notes/DN-004_skill_system_realignment.md) §1.4b 盤點時
順帶查到的一筆，依 DN-001 §3.2「當場寫得出可驗收的 AC 就直接開工單」，
**不列為 DN 的待決事項**——它只有一種做法，沒有要比的選項。

**問題**：kit 特地把 `.agent/scripts/` 的腳本寫成 **stdlib-only**
（CI 甚至有一個 `stdlib-only` job 在守這件事），為的是讓任何專案不裝 uv 也能跑；
但出貨內容裡有 5 處教 agent 用 `uv run` 執行它們。使用者專案若不用 uv，
照著做會直接失敗——**而失敗的是一個本來就不需要 uv 的腳本**。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**輸入：** `grep -rn "uv run" kit/` 的 5 處命中。

**輸出：** 改為 `python3`。

⚠️ **只改 `kit/`。** 本 repo 根目錄的 `CLAUDE.md` 用 `uv run` 是**正確的**——
本 repo 自己就用 uv，那是專案自己的選擇，不是出貨內容。
`kit/` 的定位是「裝到任何專案」，兩者判準不同。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：`grep -rn "uv run" kit/` 回空。
- [ ] AC-02：改用 `python3`；若某處確實需要專案自己的執行器，
      改寫成「用你的專案執行器」而非寫死另一個工具名。
- [ ] AC-03：**根目錄 `CLAUDE.md` 的 `uv run` 不動**（見 §2）。
      `git diff --stat` 佐證改動只在 `kit/`。
- [ ] AC-04：改完後**實跑一次**被改到的每一條指令，輸出留進審查紀錄——
      證明 `python3` 版本真的跑得起來，不是只做字串替換。
- [ ] AC-05：`uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`）；
      `python3 .agent/scripts/precheck.py` 6 項全綠。
- [ ] AC-06：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- 無。DN-004 §1.4b 已記錄此項不需裁定。

## 5. 範圍外 (Out of Scope)

- **不改本 repo 自己的 `uv` 使用**——根目錄 `CLAUDE.md`、`pyproject.toml`、CI 都不動。
- **不新增「禁止 uv run」的自動檢查**——若要，另議；本張只修現況。
