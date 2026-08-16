# [Task ID: PEV-DEV-AGENT-008] `scan_backlog.py` 生成 DN 索引，並檢查懸空依賴

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** backend-developer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-17T10:25+08:00
**✅ 完成時間 (Closed):**
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

DN-001 §3.9 立了「**索引用腳本生成，不手動維護**」，理由是生成的索引不可能有孤兒、
不需要強制登記儀式，且避開 `DOCS_MAP.md` 那個「出貨一份要專案自填的索引檔」的坑。

**但這條規則現在正被本 repo 自己違反**：`BACKLOG.md` 的 🧊 冰箱裡有七列手抄的 DN
（項目／狀態／卡在哪），那就是一份手動維護的 DN 索引。

DN-001 §4.2 裁定：**併進 `scan_backlog.py`**，在 `--format backlog` 的輸出中新增一節，
不另開索引檔、不加新的 `--format`。理由是 DN 是開單前置關卡，讀者跟 BACKLOG
是同一批人、同一個時機；另開 `DESIGN_NOTES.md` 等於多一個沒人記得看的檔案。

第二個功能來自 DN-001 §7.3 的實跑發現：**依賴可以指向不存在的 DN**——
DN-002 的「CI 閘門（尚未開 DN）」懸空了六份 DN 的時間都沒人發現。
腳本應該把這種懸空依賴列出來，讓缺口自己浮出來。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - `docs/design_notes/DN-*.md` 的 header 欄位（狀態／建立／依賴／來源／姊妹篇）
  - DN-001 §4.2（裁定）、§5（生成檔內容必須是輸入的純函數）
  - 現有 `format_backlog_markdown()`、`extract_existing_icebox()`
- **Outputs (產出物)**:
  - `kit/.agent/scripts/scan_backlog.py`
  - `tests/`：新增對應測試
  - `docs/development/BACKLOG.md`（重生後含新章節、冰箱移除手抄 DN 列）
  - 安裝同步

## 3. 驗收標準 (Acceptance Criteria)

- [ ] `--format backlog` 的輸出新增一節「🧪 設計筆記 (Design Notes)」，**排在 🧊 冰箱之前**
- [ ] 該節列出每份 DN 的：狀態、標題、連結、依賴
- [ ] **不印任何時間相依值**（天數、距今多久）——DN-001 §5：
      納入版控的生成檔內容必須是輸入的純函數
- [ ] **懸空依賴檢查**：依賴欄位提到 `DN-0NN` 但該檔不存在時，明確標出
- [ ] `docs/design_notes/` 不存在時不報錯，該節整段省略（裝了 kit 但沒開 DN 的專案）
- [ ] 冰箱中手抄的 DN 列全部移除，改由新章節生成
- [ ] **冪等**：連跑兩次 `--format backlog --output docs/development/BACKLOG.md`
      後 `git diff` 為空
- [ ] 就地重跑仍保留手動維護的冰箱內容（既有 `extract_existing_icebox()` 行為不得破壞）
- [ ] 腳本**只依賴標準函式庫**（CI 的 `stdlib-only` job 會擋）
- [ ] 新增測試涵蓋：懸空依賴被標出、無 `design_notes/` 時不報錯
- [ ] `uv run pytest` 全綠
- [ ] `./install.sh . --upgrade` 同步後 `git diff --stat` 只動到預期檔案

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 建議與 PEV-DEV-AGENT-007 的範本欄位一起確認：header 少了「畢業去向」欄位後，
    已畢業 DN 的去向改從頂端的 `> 🎓 已畢業（…）→ {工單號}` 那行抓。
- **✍️ User 補充回覆 (User Input)**:
  - 2026-08-17：4.2 併進 `scan_backlog.py`。
