# [Task ID: PEV-DEV-AGENT-005] `team_protocol.md`：DN 的權威效力與模組「類型」欄位

**🔗 依附母任務 (Parent Task ID):** DN-001
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T10:15+08:00
**✅ 完成時間 (Closed):** 2026-08-17T17:10+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

兩件事都必須寫進 `team_protocol.md`，否則會出現具體的錯誤行為：

**(1) §1.11 要寫 DN 的效力。** 不寫的話，Agent 會讀到一份 `Exploring` 的 DN 然後照著實作。
DN-001 §3.8 的判準：Seed／Exploring **不在權威階序內**，連「待辦意圖」都不是；
Graduated／Dropped 是**歷史紀錄，不得作為規格依據**（比照第 4 層已結案工單）。

**(2) §3.1 模組前綴表加「類型」欄。** 這一欄必須改變行為才值得加，DN-001 §3.7 的兩條差異就是：
基礎建設模組**不需要 PRD**（沒有使用者故事可寫），且它的第 1 層權威在 `docs/standards/`
而非模組自己的 prd／hld／lld。少了這欄，Agent 會被迫為基礎建設模組硬生一份
填滿「作為一個使用者，我希望…」的空洞 PRD。

依 DN-001 §4.5，範例表列一列 `INF`／基礎建設，標明**建議值、可自訂**，不強制。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**:
  - DN-001 §3.7（模組類型與兩條行為差異）、§3.8（DN 的權威效力）、§4.5（`INF` 為建議值）
  - `kit/.agent/resources/team_protocol.md` §1.11、§3.1
- **Outputs (產出物)**:
  - `kit/.agent/resources/team_protocol.md`（正版）
  - `kit/docs/standards/team_protocol.md`（**指路檔的章節索引**）
  - 安裝同步

## 3. 驗收標準 (Acceptance Criteria)

- [x] §1.11 明列 DN 的兩段效力（Seed／Exploring 不在階序內；Graduated／Dropped 是歷史紀錄）
- [x] §3.1 前綴對照表新增「類型」欄，範例列含 `INF`／基礎建設，並標明「建議值，可自訂」
- [x] §3.1 附一段功能模組 vs 基礎建設模組的差異表，至少含
      「必備文件」（基礎建設**不需要 PRD**）與「第 1 層權威在哪」兩列
- [x] ⚠️ 若動到章節結構（新增／改名 `### x.y`），**必須同步更新指路檔
      `kit/docs/standards/team_protocol.md` 的章節索引**，
      否則 `test_指路檔章節索引與正版同步` 會紅
- [x] 指路檔仍**不含正版任何一段正文**（`test_團隊守則只有一份正版`）
- [x] `uv run pytest` 全綠
- [x] `./install.sh . --upgrade` 同步後 `git diff --stat` 只動到預期檔案

## 📝 Code Review 備註 (Review Notes)

> 審查日期：2026-08-17 ｜ 審查結論：✅ APPROVED
> 審查方式：作者自審 ＋ 客觀指標核對。依 `docs/standards/git_workflow.md` §8.3，
> 本工單不推送、無 PR，本章節即唯一審查載體，編號欄位填 `—`。

### 客觀指標核對（全部可重跑）

| 指標 | 期望 | 實得 |
|---|---|---|
| §1.11 DN 效力表資料列 | 2（Seed／Exploring、Graduated／Dropped） | **2** ✅ |
| §3.1 前綴表欄數 | 4（前綴／模組名稱／類型／對應目錄） | **4** ✅ |
| `INF` 範例列＋「建議值，可自訂」 | 1 | **1** ✅ |
| 功能 vs 基礎建設差異表（必備文件、第 1 層權威） | 2 列 | **2** ✅ |
| 新增／改名的 `### x.y` 章節 | 0（不必動指路檔索引） | **0** ✅ |
| `git status` 變更檔 | 3（kit 正版＋安裝實例＋manifest） | **3** ✅ |
| `uv run pytest` | 全綠 | **98 tests / 0 failures** ✅ |

### 為什麼不必同步指路檔

`git diff kit/.agent/resources/team_protocol.md | grep '^[+-]### '` → **0**。
本工單只在既有 §1.11／§3.1 內加內容，沒有新增或改名任何 `### x.y`，
因此 `test_指路檔章節索引與正版同步` 不受影響（該測試比對的是章節標題）。
`test_團隊守則只有一份正版` 也維持綠燈——指路檔一個字都沒動。

### 一項超出 AC 的補充（刻意）

§1.11 實務守則多加一條：「**工單 `Inputs` 不得只指向一份 DN**」。
理由是 AC 只要求寫出 DN 的「效力」，但真正會出錯的行為是**開單時把 DN 當規格來源**——
DN-001 §3.6 要求「結論必落地」，這條就是它在工單層的檢查點：
第 1 層找不到依據，代表結論還沒落地，那張工單就還不該開。

### 一項與 scan_backlog.py 的相容性確認

前綴表加欄位前先確認過 `scan_backlog.py` **不解析這張表**——它掃的是
`docs/features/*/tasks/` 目錄結構。加欄位不會動到 BACKLOG 生成。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。`INF` 的定位（建議非強制）由 DN-001 §4.5 定案。
- **✍️ User 補充回覆 (User Input)**:
  -
