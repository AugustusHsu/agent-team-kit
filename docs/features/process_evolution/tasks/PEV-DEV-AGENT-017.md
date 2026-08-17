# [Task ID: PEV-DEV-AGENT-017] Spike：context 壓縮會不會讓審查者讀到非原文

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** code-reviewer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-17T09:33+08:00
**✅ 完成時間 (Closed):** 2026-08-17T09:36+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

PEV-DEV-AGENT-015 立下「交付回報是線索，不是證據，一律回查程式碼與實際輸出」。
但這條規則有個沒被檢查過的前提：**審查者讀到的「實際輸出」就是原文**。

冰箱的「headroom 壓縮工具輸出」列記錄了反例：本 repo 的開發環境把 Claude Code 的
API 流量導過一個本機壓縮 proxy，工具輸出在進入 context 前會被改寫。
2026-08-17 該輪對話三度遇到，隔輪的 PEV-DEV-AGENT-012／013 開發中又遇到兩次
（讀 DN-007、讀 Icebox 表格時被壓成 JSON）。

若審查者讀到的 diff 或工單是被改寫過的版本，§015 那條規則會**看起來成立、實際失效**——
審查者仍然「回查了程式碼」，只是查到的不是程式碼。

這是 spike：**先量出什麼情況會被改寫、損失多大、救不救得回來**，再決定規範怎麼寫。
它同時是 DN-004 §5 最後一條待決的前置。

## 2. 調查結果 (Findings)

環境：`.claude/settings.local.json` 把 `ANTHROPIC_BASE_URL` 指到 `http://127.0.0.1:8787`，
`headroom ... proxy --port 8787` 在跑。**它不是 MCP 工具，是攔在 Claude Code 與 API
之間的 proxy**——所以它能改寫任何工具的輸出，而且無法從 Claude Code 這一側逐工具關閉。

### 2.1 觸發條件：不是「輸出很長」，是「輸出很規律」

| 探針（Bash 輸出） | 結果 | 有無提示 |
|---|---|---|
| 40 行**內容各異**的程式碼樣式文字 | **原封不動** | — |
| 12 行**高度重複**的同構文字 | **原封不動** | — |
| 16 行同構文字 | 第 13 行起**只剩序號，內容消失** | 有 `[N items compressed …hash=]` |
| 20 行同構文字 | 第 13 行起**只剩序號，內容消失** | 有 hash |
| 與稍早訊息**完全相同**的 13 行 | 換成 `[↑12L same as msg 194: '…']` | 有提示 |
| **1 列的 Markdown 表格 ＋ 前後各一句散文** | 表格轉成 JSON，**前後兩句散文整段消失** | **完全沒有提示、沒有 hash** |

最後一列是最嚴重的：**最小重現只要一張一列的表格**。

```
輸入： AAA 這句話在表格之前。 / | a | b | / |---|---| / | 1 | 2 | / BBB 這句話在表格之後。
得到： [{"a":"1","b":"2"}]
```

散文沒了，沒有任何標記說「這裡刪過東西」。**讀的人不會知道自己少看了什麼。**

### 2.2 救不救得回：分兩種，一種救得回、一種永久遺失

- 有 hash 的（`kompress` 策略）：原文確實存在 `~/.headroom/ccr_store.db` 的
  `ccr_entries.original_content`，實查取得完整原文。**救得回**。
- **表格轉 JSON 的那類：store 裡根本沒有對應紀錄。永久遺失。**

### 2.3 官方的救援機制本身是壞的

`mcp__headroom__headroom_retrieve` 的用途是「用 hash 取回原文」。實測兩個 hash，
兩次都回傳佔位符而不是原文：

```
{"hash":"dc476370824a…","original_content":"<<ccr:dc476370824a,string,1.6KB>>", …}
```

原因在 store 裡看得到：那兩次 retrieve **自己被 proxy 再壓一次**，
留下 `compression_strategy: string_ccr:string`、`tokens 0→0` 的紀錄——
回應裡的原文被換成了指向它自己的引用。**這條救援路徑在本環境等於不可用**，
要拿原文只能直接讀 `~/.headroom/ccr_store.db`。

### 2.4 哪條讀法是乾淨的

| 讀法 | 表格＋散文的結果 |
|---|---|
| `Read` 工具 | **完整保留**（每行帶行號前綴，壓縮器不當它是表格） |
| Bash `cat -n` | 內容保留，換行被壓掉 |
| Bash `cat` / `sed -n` | **表格轉 JSON，散文消失** |

### 2.5 規模

`headroom_stats`：`cache` 模式，18383 次請求中 5160 次被壓縮，
平均 1.9%、最佳 28.6%，宣稱省下 $73.18／$1758.68（4.2%）。
**換算：為了 4.2% 的成本，換來的是審查證據可能靜默殘缺。**

## 3. 驗收標準 (Acceptance Criteria)

- [x] 量出觸發條件並附可重現的探針（§2.1），區分「重複結構」與「長度」
- [x] 判定救援可行性，並實查 store 佐證（§2.2）
- [x] 實測 `headroom_retrieve` 是否真能取回原文（§2.3）
- [x] 找出至少一條乾淨的讀法（§2.4）
- [x] `code-reviewer/SKILL.md` §0 增加一條**與工具無關**的規則：讀到的輸出也可能不是原文，
      指定讀法與自檢標記（出貨規範不得寫死 headroom 這個特定工具）
- [x] DN-004 §5 最後一條待決依本結果勾掉並填入結論
- [x] 冰箱移除「headroom 壓縮工具輸出」列
- [x] `uv run pytest` 全綠；`./install.sh . --upgrade` 待合併 0

## 4. 人為補充與確認 (Human-in-the-loop)

- 2026-08-17：使用者裁定「開 spike 工單」。
- **本工單不動使用者的機器設定。** 要整個關掉，改
  `.claude/settings.local.json` 的 `env.ANTHROPIC_BASE_URL`（連同 `ANTHROPIC_CUSTOM_HEADERS`）；
  要換模式，看 `headroom_stats` 提到的 `HEADROOM_MODE`。裁量權在使用者。

## 📝 Code Review 備註

> 2026-08-17 ✅ APPROVED — 完整報告見 [../reviews/PEV-DEV-AGENT-017.md](../reviews/PEV-DEV-AGENT-017.md)

### 📊 客觀指標

| 指標 | 變更前 | 變更後 |
|---|---|---|
| 全套測試／失敗數 | 111 / 0 | **111 / 0** |
| 可重現探針數 | 0 | **7** |
| `headroom_retrieve` 取回原文成功率 | 未知 | **0 / 2** |
| kit 內寫死 `headroom` 的檔案數 | 0 | **0** |
| 冰箱資料列 | 4 | **3** |
| `./install.sh . --upgrade` 待合併 | — | **0** |
