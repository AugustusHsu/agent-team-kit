---
description: 根據 git diff 產生符合專案風格的 Git Commit Message
---

## 目標格式（gitmoji + Conventional Commits）

```
<emoji> <type>(<scope>): <繁體中文 Subject>
<空行>
<繁體中文 Body — 條列式說明>
```

### Emoji 對照表

| Emoji | Type              | 使用時機                       |
| ----- | ----------------- | ------------------------------ |
| ✨     | feat              | 新增功能                       |
| 🐛     | fix               | 修正 Bug                       |
| ♻️     | refactor          | 重構（不影響行為）             |
| 📝     | docs              | 文件新增或修改                 |
| ⚡     | perf              | 效能優化                       |
| 🛠️ / 🔧 | chore             | 建構工具、Docker、設定檔等雜項 |
| 🧪     | test              | 新增或修改測試                 |
| 💥     | feat! / refactor! | Breaking Change                |

### 禁止寫進 commit message 的內容

commit message **只描述這個專案本身的變更**。以下一律不寫：

- **AI 署名 trailer**——`Co-Authored-By: Claude ...`、`🤖 Generated with ...` 之類。
  工具來源不是專案歷史的一部分，還會汙染 `git shortlog` 的作者統計。
- **對話脈絡**——「依你的要求」「上一輪討論到的」。未來讀 log 的人沒有那段對話。
- **工具或 session 的內部狀態**——worktree 路徑、job ID、暫存目錄。

---

## 執行步驟

1. **確認暫存區狀態**

   執行以下指令查看目前的暫存狀態，確認有哪些檔案已 `git add`（Staged）：

   ```bash
   git status
   git diff --staged --stat
   ```

   > ⚠️ **嚴格限制**：**絕對不可**自作主張幫使用者執行 `git add` 或把 untracked / modified 檔案加入暫存區。只能針對「目前已經在 Staged 階段」的內容進行後續分析。

2. **讀取完整 diff 內容**

   ```bash
   git diff --staged
   ```

   仔細閱讀所有變更，理解：
   - 變更涉及哪些模組（用於決定 `scope`）
   - 變更的主要意圖（新功能 / 修正 / 重構 / 文件？）
   - 是否有 Breaking Change（API 簽章或 DB Schema 改動）

3. **參考近期 log 風格（選用）**

   ```bash
   git log --oneline -10
   ```

   確保新訊息的語氣、用詞與現有 log 一致。

4. **產生 Commit Message**

   依照以下規則撰寫，**只輸出 commit message 內容，不執行 commit**：

   - **第一行（Subject）**：`<emoji> <type>(<scope>): <一句話說明做了什麼>`
     - 使用**繁體中文**，動詞開頭（例如：實作、修正、重構、新增、優化）
     - 長度不超過 72 個字
   - **空行**
   - **Body（可選，但建議加入）**：
     - 使用 `- **標題**：說明` 或純條列式描述
     - 說明「為什麼」與「怎麼做」，而非逐行解釋程式碼
     - 若有多個子系統，可用 Markdown 小標題分組（如 `- **API 端點 (routers)**:`）

   **格式範例：**

   ```
   ✨ feat(upload): 導入不可變/去重流程並調整 manifest 唯一索引為 (path, sha256)

   - DB 索引：`manifest_items` 唯一索引改為 `(path, sha256)`，符合不可變 + 去重策略。
   - 去重判斷：批量查詢改以 `(path, sha256)` 作為 key，命中則重用既有 `_id/object_key`。
   - 上傳寫入：以 `_ensure_manifest_item`（Find-or-Create）取代舊的 upsert 方法，確保冪等。
   ```

5. **交付使用者複查（強制閘門）**

   > ⚠️ **嚴禁未經複查即 commit。** 必須先把**完整 commit message 原文**呈現給使用者，
   > 取得**當次**明確同意後才可執行。**前一次的同意不延用到下一個 commit。**

   呈現後詢問：

   > 「以上 commit message 是否符合預期？確認後我可以幫您執行 `git commit`，或提供指令讓您自行執行。」

   使用者要求修改時，改完必須**重新呈現完整訊息**再取得一次同意，
   不可只回覆「已修正」就逕自提交。

   > **工單／worktree 流程下的時點**：訊息隨交付回報一併呈交（`In Progress` → `In Review`），
   > 但**要等審查 APPROVED 之後才執行第 6 步**。詳見 `.agent/resources/team_protocol.md` §1.10。

6. **執行 Commit（待使用者確認後）**

   ```bash
   git commit -m "<subject>" -m "<body>"
   ```

   > ⚠️ **注意**：若 Body 含有換行或特殊符號，建議改用互動模式或 `COMMIT_EDITMSG` 檔案方式處理：
   >
   > ```bash
   > git commit  # 開啟編輯器，貼入完整 message
   > ```
