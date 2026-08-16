# [Task ID: PEV-DEV-AGENT-004] `documentation_conventions.md` 新增 Design Note 機制章節

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-17T10:10+08:00
**✅ 完成時間 (Closed):**
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

DN-001 的結論屬於「跨模組的文件慣例」，依 §3.5 去向 D 必須落到 `docs/standards/`——
**結論落不到第 1 層文件，對 Agent 而言等於不存在**（`team_protocol.md` §1.11）。

本工單把 DN 機制寫進 `kit/docs/standards/documentation_conventions.md`：
它是 DN 機制在 kit 的**規範正版**，PEV-DEV-AGENT-007 出貨的範本是它的執行物。

要寫進去的是 DN-001 §3 已定調的五塊，**不含**探索過程與被否決的方案
（§3.6：不折併全文，只落結論）。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.2（進場規則）、§3.3（狀態機）、§3.4（畢業三條件）、
    §3.5（畢業去向 A–G 與 A/B 四條判準）、§3.6（不折併但結論必落地）
  - `kit/docs/standards/documentation_conventions.md` §2.1（本節刻意偏離它，理由要寫進去）
- **Outputs (產出物)**:
  - `kit/docs/standards/documentation_conventions.md`（新增一節）
  - `docs/standards/documentation_conventions.md`（安裝同步）

## 3. 驗收標準 (Acceptance Criteria)

- [ ] 新章節含**進場規則**：AC 當場寫得出 → 直接開工單、不要開 DN；寫不出 → 先開 DN
- [ ] 新章節含**四狀態**（🌱 Seed／🔍 Exploring／🎓 Graduated／🚫 Dropped）與各自誰推進
- [ ] 新章節含**畢業三條件**，且明寫第 2 條（寫得出至少一張工單的 AC）是主力、
      第 3 條（使用者本人簽核）不外包給 AI
- [ ] 新章節含**畢業去向 A–G 表**與 A/B 四條判準
- [ ] 新章節明寫「**不折併全文，但結論中屬於架構事實的部分必須寫進第 1 層**」，
      並說明這是對 §2.1 的刻意偏離與理由
- [ ] 新章節明寫畢業後頂端加 `> 🎓 已畢業（YYYY-MM-DD）→ {工單號}。本檔凍結，不再更新。`
- [ ] `kit/docs/DOCS_MAP.md` 已登記（`documentation_conventions.md` 本來就在，確認未失聯）
- [ ] `uv run pytest` 全綠
- [ ] `./install.sh . --upgrade` 同步後 `git diff --stat` 只動到預期檔案

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。內容全部來自 DN-001 §3 已定調的部分。
- **✍️ User 補充回覆 (User Input)**:
  -
