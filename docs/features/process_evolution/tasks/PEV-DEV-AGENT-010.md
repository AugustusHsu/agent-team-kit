# [Task ID: PEV-DEV-AGENT-010] 合併方式的殘留寫死清乾淨，並要求合併訊息帶 Task ID

**🔗 依附母任務 (Parent Task ID):** PEV-DEV-AGENT-003
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-17T10:00+08:00
**✅ 完成時間 (Closed):**
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

PEV-DEV-AGENT-003 把 §6.1 的合併方式改成「有 PR → squash／無遠端 → `--no-ff`」，
但**有兩處寫死的 squash 沒跟著改**，兩處都在描述「一般流程」而非平台專屬設定：

- §6.2 收尾流程表第 3 步：`| 3 | Developer | squash 合併 |`
- §4 的一句：「主線上仍是一顆（§6.1 的 squash）」

（§8.2 那句「允許的合併方式：只留 squash」不在此列——它在 GitHub 設定清單裡，
本來就是平台專屬，正確。）

第二個缺口更根本：**`--no-ff` 只保住拓撲，保不住分支名。**
本 repo 的實證——`52209c5` 是 `PEV-DEV-AGENT-001` 的合併 commit，
但預設訊息 `Merge branch 'PEV-DEV-AGENT-001'` 被工單層級訊息取代，
`git log --graph` 看到的是一條**無名側支**。分支名目前只活在本機 reflog：
不推送、預設 90 天過期。使用者 2026-08-17 明確要求「開出去的分支都要能在
git history 中呈現」，只有拓撲不夠，名字必須進 commit 物件。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `kit/docs/standards/git_workflow.md` §4、§6.1、§6.2
  - 實證：`git log -1 --format=%B 52209c5 | grep -c "Merge branch"` → `0`
- **Outputs (產出物)**:
  - `kit/docs/standards/git_workflow.md`（§4、§6.1、§6.2 三處）
  - `docs/standards/git_workflow.md`（`./install.sh . --upgrade` 同步）
  - `tests/test_kit_integrity.py`：`已廢除的流程規則` 新增一列擋「無條件 squash」的殘留

## 3. 驗收標準 (Acceptance Criteria)

- [ ] §6.2 收尾表第 3 步不再寫死 squash，改為指向 §6.1 的平台分流
- [ ] §4 那句「§6.1 的 squash」改為平台中立的措辭
- [ ] §6.1 新增規則：**合併 commit 的訊息第一行必須含 Task ID**，
      因為分支名 = Task ID（§3），這是分支名進入 commit 物件的唯一途徑
- [ ] 該規則同時說明**為什麼不能只靠 reflog**：reflog 不推送、預設 90 天過期
- [ ] `--no-ff` 的實際指令示例（§6.4／§8.3）更新為帶 Task ID 的訊息形式
- [ ] `tests/test_kit_integrity.py` 的 `已廢除的流程規則` 新增一列，
      且該列對**改動前**的檔案會命中、對改動後為 0（反證，避免加出永遠綠的假測試）
- [ ] `grep -c '\[平台相關\]' kit/docs/standards/git_workflow.md` 維持 **9**
- [ ] §9 檢查清單維持 **9 列**（`sed -n '/## 9\./,$p' | grep -c '^| .*|'` 為 10，含表頭）
- [ ] `uv run pytest` 全綠
- [ ] `./install.sh . --upgrade` 後 `git diff --stat` 只動到預期檔案

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - **不含**「有 PR 平台時是否也改用 `--no-ff`」——那會推翻 DN-003 裁定 5，
    屬於另開 DN 的範圍（DN-001 §3.9：推翻已畢業的 DN 要開新 DN）。
    本工單只做「殘留清理」與「合併訊息帶 Task ID」，兩者與該裁定無關、先做不會白做。
- **✍️ User 補充回覆 (User Input)**:
  - 2026-08-17：「我是希望開出去的分支都能在 git history 中呈現」
