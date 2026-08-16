# [Task ID: PEV-DEV-AGENT-006] scrum-master 加上「開單前置關卡」

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-17T10:20+08:00
**✅ 完成時間 (Closed):**
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

DN 機制的進場點在 scrum-master 身上——**它是唯一會開工單的角色**。
規範寫在 `documentation_conventions.md`（PEV-DEV-AGENT-004）不代表它會被執行：
skill 不讀規範就不會照做。

DN-001 §3.2 的判準只有一條，簡單到可以直接寫進 SKILL.md：

| 情境 | 動作 |
|---|---|
| **當場寫得出可驗收的 AC** | 直接開工單，**不要開 DN** |
| 寫不出來——方案沒定、邊界不清、影響範圍未知 | **先開 DN** |

必須同時寫進 evals，否則這條規則沒有任何執行期驗證
（PEV-DEV-AGENT-001 的教訓：改了四份 SKILL.md 卻漏掉 evals，測試全綠照樣放行）。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.2（進場規則）、§3.3（狀態）、§3.4（畢業條件，scrum-master 不得自行簽核）
  - `kit/.agent/skills/scrum-master/SKILL.md` 與 `evals/evals.json`
- **Outputs (產出物)**:
  - `kit/.agent/skills/scrum-master/SKILL.md`
  - `kit/.agent/skills/scrum-master/evals/evals.json`
  - 安裝同步

## 3. 驗收標準 (Acceptance Criteria)

- [ ] SKILL.md 新增「開單前置關卡」段落，含上表兩列的判準
- [ ] 明寫 **DN 不是工單**：不進 `scan_backlog.py` 的五狀態，
      也不得由 scrum-master 自行標 `Graduated`（§3.4 條件 3 只有使用者能簽）
- [ ] 明寫 DN 的落點與取號方式（`docs/design_notes/`，全域扁平流水號）
- [ ] `evals.json` 新增至少一筆：給一個「方案未定、寫不出 AC」的需求，
      expected_output 是**開 DN 而非開工單**
- [ ] `evals.json` 通過 `test_evals_符合_skill_creator_schema`（id 連號、欄位齊全）
- [ ] `evals.json` 不含來源專案識別資訊（`test_evals_不得殘留來源專案的識別資訊`）
- [ ] `uv run pytest` 全綠
- [ ] `./install.sh . --upgrade` 同步後 `git diff --stat` 只動到預期檔案

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。
- **✍️ User 補充回覆 (User Input)**:
  -
