# [Task ID: PEV-DEV-AGENT-009] DOCS_MAP 的模組表抽成獨立檔，骨架恢復可升級

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-17T10:30+08:00
**✅ 完成時間 (Closed):**
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`docs/DOCS_MAP.md` 是 kit 的**已知缺陷**（本 repo CLAUDE.md「例外二」明載）：
kit 出貨時就要求專案自行填寫「功能模組」表，但它**不是種子檔**，
於是每次升級都被判定為「使用者改過」而產生 `.new` 衝突。
**這不是使用者亂改，是規範叫他改的。**

DN-001 §4.3 裁定**第三案**：不列為種子檔，而是**把會變動的模組表抽成獨立檔**。

理由是兩害相權：列為種子檔可以消掉 `.new`，但代價是 kit 日後改 DOCS_MAP 的骨架
（新增章節、改導航規則）**再也推不到既有專案**，使用者永遠停在安裝當天的版本。
`BACKLOG.md` 能承受這代價是因為它由腳本整份重生成，DOCS_MAP 沒有生成器，骨架真的會凍住。
抽出後：骨架仍隨 kit 升級，會變動的那張表歸專案所有，兩邊都拿到想要的。

本 repo 已經自發長出 `docs/features/README.md` 當前綴權威表，且**安裝從不碰它**——
這個做法已經被本 repo 實證過，不是憑空設計。

順帶處理 DN-001 §3.7 的正名：表頭「功能模組」與「基礎建設模組」直接打架，
改為「模組」並加「類型」欄。**目錄名 `features/` 不動**——改名會弄斷既有連結、
`.kit-manifest` 基準線與 `scan_backlog.py` 的硬編路徑。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.7（類型欄）、§4.3（第三案裁定）
  - `kit/docs/DOCS_MAP.md` §「功能模組 (features/)」
  - `install.sh` 的 `is_seed_file()`（**本工單不改它**——第三案不列種子檔）
  - 本 repo 的 `docs/features/README.md` 作為形狀參考
- **Outputs (產出物)**:
  - `kit/docs/features/README.md`（新，模組表落點）
  - `kit/docs/DOCS_MAP.md`（模組表改為指向該檔）
  - 安裝同步；本 repo 的 `docs/DOCS_MAP.md` 與 `docs/features/README.md` 一併對齊

## 3. 驗收標準 (Acceptance Criteria)

- [ ] `kit/docs/features/README.md` 存在，內含模組登記表，欄位含**類型**（功能／基礎建設）
- [ ] `kit/docs/DOCS_MAP.md` 不再內嵌模組表，改為一行指向 `features/README.md`
- [ ] DOCS_MAP 的標題「## 功能模組 (features/)」改為平台中立的「## 模組 (features/)」
- [ ] `install.sh` 的 `is_seed_file()` **不變**（第三案：DOCS_MAP 維持非種子檔）
- [ ] 本 repo 的 `docs/DOCS_MAP.md` 升級後**不再產生 `.new`**——
      這是本工單成立與否的關鍵驗證：跑 `./install.sh . --upgrade --dry-run` 確認
- [ ] 本 repo 現有的 `PEV`／`KIT`／`WTG` 三列完整遷移到 `docs/features/README.md`，
      且該檔仍是**本 repo 自有檔案**（安裝不覆蓋）
- [ ] `kit/` 內無死連結
- [ ] `uv run pytest` 全綠（含 `test_安裝後檔案與_kit_完全一致`）
- [ ] CLAUDE.md「例外二」的敘述同步更新（它記錄的是已消失的缺陷）

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - `kit/docs/features/README.md` 與 kit 既有的 `kit/docs/features/_TEMPLATE/` 並存，
    需確認 `test_安裝後檔案與_kit_完全一致` 的預期清單不受影響（新增檔案應自動涵蓋）。
- **✍️ User 補充回覆 (User Input)**:
  - 2026-08-17：4.3 第三案。
