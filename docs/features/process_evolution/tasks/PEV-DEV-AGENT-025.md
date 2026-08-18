# [Task ID: PEV-DEV-AGENT-025] 13 份 skill 全面盤點與對齊

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** tech-lead
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-18T21:40+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

[DN-004](../../../design_notes/DN-004_skill_system_realignment.md)（🎓 Graduated）的
第一張工單，承接 4.1（分兩張工單，本張是「對齊」那一張）、4.2（全面盤點）、
4.6（只盤點使用紀錄、不裁撤），以及 4.5 裁定的 A+ 慣例所需的補標題工作。

**問題**：前 24 張工單改的全是 `team_protocol.md` 與 `docs/standards/`，
但 agent 執行時實際讀的是 `kit/.agent/skills/*/SKILL.md`。規範改了而 skill 沒改
＝**規範上生效、執行上沒生效**。DN-004 §1.3 查證出三筆具體脫節，
§1.2 的兩天後重測證明落差不會自癒——那 7 份從未複檢的 skill 一個字都沒動。

**為什麼是全面盤點而非逐份按需**（4.2 裁定）：逐份按需的前提是「知道哪一份有問題」，
而 DN-004 §2 已證實目前無法規模化地知道——`tests/test_kit_integrity.py` 對 skill 的
四項檢查全部關於 frontmatter 與 evals，**沒有一項讀 skill 內文**。
這是一次性成本，之後由 `PEV-DEV-AGENT-026` 的自動檢查接手。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**輸入：** `kit/.agent/resources/team_protocol.md`（17 個章節）與
`kit/.agent/skills/*/SKILL.md`（13 份）。

**輸出：** 13 份 skill 的對齊修改，以及一份盤點報告（寫在審查紀錄
`docs/features/process_evolution/reviews/PEV-DEV-AGENT-025.md`）。

**三筆已知脫節**（DN-004 §1.3，本工單建立時實測）：

| # | 脫節 | 現況 |
|---|---|---|
| a | §1.12 覆蓋不全 | §1.12 明文「適用全角色」，13 份只有 5 份引用；缺 business-analyst、product-manager、qa-test-planner、scrum-master、security-engineer、system-architect、tech-lead、uiux |
| b | 章節引用錯置 | `backend-developer:37`、`devops-engineer:45`、`frontend-developer:66`、`qa-automation-engineer:385` 的「Status 更新」寫「詳見 `team_protocol.md` §1.3」，但 §1.3 是「Epic 關閉條件」，狀態更新操作方式是 **§1.5** |
| c | 7 份從未複檢 | business-analyst／product-manager／qa-test-planner／system-architect／tech-lead／uiux 各變更 1 次、security-engineer 2 次，期間 `team_protocol.md` 長出 §1.9～§1.12 |

**A+ 慣例**（DN-004 §4 附錄，4.5 裁定）：引用寫成 `§1.12 取證通道保真` 而非只寫 `§1.12`。
現有 25 筆引用有三種寫法（`` `team_protocol.md` §1.12 ``、`team_protocol §1.10`、
`§1.9 / §1.10` 一次寫兩個），要一併正規化成單一寫法，否則 `026` 的檢查寫不乾淨。

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：§1.12 補進缺的 8 份 skill。
- [ ] AC-02：**8 份各寫各的，不得複製貼上。** §1.12 適用全角色，但非開發角色
      （business-analyst、product-manager、uiux）的取證形式與開發角色不同——
      現有 5 份各自寫了貼合自身的一句（devops 講 build／部署 log、
      qa-automation 講測試輸出、frontend／backend 講查閱檔案）。
      複製貼上就是製造「宣稱 ≠ 實際」。審查時逐份比對這 8 句彼此不相同。
- [ ] AC-03：b 那 4 筆 `§1.3` 改為 `§1.5`。
- [ ] AC-04：13 份 skill 內所有 `team_protocol.md` 章節引用**補上章節標題**
      並正規化成單一寫法；`grep -rnE '§[0-9]+\.[0-9]+' kit/.agent/skills/`
      的每一筆後面都跟著標題。
- [ ] AC-05：那 7 份從未複檢的 skill **逐份開檔比對** §1.9～§1.12，
      盤點報告逐份寫出「有無脫節、處置為何」，不得只寫「已檢查」。
- [ ] AC-06：盤點報告列出 13 個角色的使用紀錄（在 26 張工單中各被指派幾次）。
      **只盤點不裁撤**——裁撤會連帶動到 `evals.json` 與 `test_每個角色都有_evals`，
      且「沒派用過」在一個只跑了 26 張工單的 repo 裡樣本太小、不構成證據。
- [ ] AC-07：**不動 `qa-automation-engineer` 的技術棧內容**——那是
      `PEV-DEV-AGENT-027` 的範圍，兩張同時改同一檔會衝突。
- [ ] AC-08：`uv run pytest` 全綠；`python3 .agent/scripts/precheck.py` 6 項全綠。
- [ ] AC-09：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- DN-004 的畢業與 4.1／4.2／4.6 的裁定由使用者於 2026-08-18 簽核。

## 5. 範圍外 (Out of Scope)

- **不寫自動檢查**——`PEV-DEV-AGENT-026`。先對齊後上鎖，反過來會讓 CI 立刻紅在
  半數 skill 不合規上，擋住自己的合併。
- **不拆 `qa-automation-engineer` 的技術棧內容**——`PEV-DEV-AGENT-027`。
- **不定 skill 撰寫標準**——`PEV-DEV-AGENT-028`。
- **不裁撤任何角色**（AC-06）。
