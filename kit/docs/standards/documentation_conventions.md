# 📐 文件分檔與交叉引用守則 (Documentation Conventions)

> 本檔存放不隸屬於特定功能模組、長期有效的**文件組織規範**。目的：避免「補充檔案孤兒化」（存在但沒有任何地方連結到它）與「ADR 編號衝突」這兩類問題——兩者都是本套件來源專案實際踩過的坑。
> **研究依據**：業界 docs-as-code / ADR 實務慣例（見文末 Sources），已依「小團隊或單人 + AI 協作、工單驅動、Markdown + Git 版控」的工作方式取捨簡化。

## 1. 核心原則

依 Grab 工程團隊「集中索引 + 分散撰寫」的混合模式（見 Sources）：**`DOCS_MAP.md` 是唯一的集中式導覽索引，但實際文件內容分散撰寫在各模組目錄下、就近其所屬的 `docs/features/{module}/`**。本專案規模不需要更複雜的多 `docs/` 站台合併機制（如 Spotify 的 mkdocs-monorepo-plugin），維持現行單一 `docs/` 樹狀結構即可。

真正要解決的是 GitDoc 提出的判準：**「一個變更能不能在文件沒跟著更新的情況下被合併？如果可以，你的流程本來就註定會產生過時文件。」** 本專案是工單驅動、單人 + AI 協作，沒有 PR review 這道關卡替你把關文件同步，所以**建立補充檔的當下就必須完成登記**，不能指望「之後有空再補」。

## 2. 補充檔案（Supplement File）規則

### 2.1 何時該拉出獨立檔案，而非寫成主文件的一個章節

| 情境 | 建議 |
|---|---|
| 內容篇幅小（幾段文字、一個表格即可講完） | 直接寫進主文件（`lld.md`/`hld.md`）對應章節 |
| 內容是一個**完整子課題**（有自己的時序圖、狀態機、多個子章節），且不會讓主文件失焦 | 拉出獨立補充檔 |
| 內容綁定某張規劃中的工單、**尚未定案**（工單未 `Done`，如 AC 尚未打勾／使用者尚未簽核） | **一律拉出獨立補充檔**，不論篇幅——避免未定案的假說/草案污染已確認的主文件（`lld.md`/`hld.md` 應只承載目前已生效的架構事實） |

工單定案、實作完成、工單轉 `Done` 後，補充檔內容應**折併回主文件**對應章節（或至少在主文件加上「已定案，內容併入 §X」的註記），補充檔可保留作為歷史記錄或刪除，依當下判斷。

### 2.2 命名慣例

`lld_0XX_{主題}.md` / `hld_0XX_{主題}.md`，數字為**該模組內**的流水號（非全域）。
例：`docs/features/{模組}/lld_003_oauth_registration.md`。

### 2.3 強制登記（建立補充檔的當下必須同時完成，缺一不可）

1. **正向連結**：在 `DOCS_MAP.md` 對應模組區塊新增一行，指向該補充檔。
2. **反向連結**：在其「母文件」（通常是 `lld.md`/`hld.md` 被補充的那個章節）加一行指回補充檔，註明「詳見 `lld_0XX_xxx.md`」。

只做其中一項＝孤兒文件：檔案存在、卻沒有任何人找得到它。

## 3. ADR 編號慣例

> 📌 立規背景：來源專案曾同時在多份文件裡各自遞增 ADR 編號（模組 HLD 一套、開發環境規格另一套），造成五組編號重複，事後校正成本很高。以下規則就是為了避免重演。

- **新 ADR 一律使用「全專案目前已用過的最大編號 + 1」**，不分模組。撰寫前執行：
  ```bash
  grep -rEn "^#{2,4} ADR-[0-9]+" docs --include=*.md | grep -oE "ADR-[0-9]+" | sort -t- -k2 -n | tail -1
  ```
- **ADR 只在決策已定案／已生效時撰寫**，不對規劃中／尚待驗證的方案預先寫 ADR（即不使用 `Proposed` 狀態）。規劃階段的假說與待驗證設計，依 §2 規則寫進補充檔，不寫 ADR。
- 若該 ADR **同時影響多個模組**，寫入 `standards/` 下的跨模組文件或另立 `standards/adr/ADR-0XX_xxx.md`；若僅影響單一模組，寫入該模組 `hld.md`。無論寫在哪，**都必須同步在 `standards/adr/README.md` 補登一行索引**（僅登記用途，不影響上述全域流水號）。這一步最容易被跳過，跳過就等於沒有索引。

## 4. Design Note (DN) 機制

> 📌 立規背景：工單要求「當場寫得出可驗收的 AC」，但有些工作在開單當下方案還沒定、
> 邊界還不清。硬開工單會得到一張 AC 寫著「設計得合理」的假工單；不開又會讓事情
> 消失在 Icebox 裡。DN 就是這兩者之間的緩衝區。

DN 是**開單前置關卡**，不是待辦清單，也不是「Icebox 項目的展開」。
檔案放 `docs/design_notes/`，全域扁平、全域流水號，範本見
[`../design_notes/_TEMPLATE.md`](../design_notes/_TEMPLATE.md)。

### 4.1 進場規則：AC 難產時才開 DN

| 情境 | 動作 |
|---|---|
| scrum-master **當場寫得出可驗收的 AC** | 直接開工單，**不要開 DN** |
| 寫不出來——方案沒定、邊界不清、影響範圍未知 | **先開 DN** |

進場與畢業共用同一個測試（見 §4.3），所以這道關卡不會變成單向閘門：
寫得出 AC 就進不來，也就出得去。

### 4.2 狀態

```
🌱 Seed ──→ 🔍 Exploring ──→ 🎓 Graduated（工單已開出）
                         └─→ 🚫 Dropped（決定不做）
```

| 狀態 | 含義 | 誰推進 |
|---|---|---|
| 🌱 Seed | 檔案剛建，只有問題陳述，沒人在推 | scrum-master |
| 🔍 Exploring | 正在比方案，「待決事項」清單成形中 | system-architect / tech-lead |
| 🎓 Graduated | 工單已開出，DN 凍結唯讀 | **使用者簽核** |
| 🚫 Dropped | 決定不做，理由必填，DN 凍結唯讀 | **使用者簽核** |

**刻意不重用工單的五狀態**：工單狀態回答「事情做完了沒」，DN 回答「問題想清楚了沒」。
共用詞彙會讓索引腳本與 Agent 混淆，也會誘使人把 DN 當工單推進。

### 4.3 畢業條件（三條全中）

1. **「待決事項」每項都有答案**，或明確標記「延後至 DN-0YY」。延後也要有去處。
2. ⭐ **寫得出至少一張工單的驗收標準。** 寫不出可驗收的 AC ＝ 設計沒收斂完，不准畢業。
3. **使用者本人簽核。** DN 畢業屬於「只有你能決定」那一類，**不外包給 AI**。

第 2 條是主力：它把「想清楚了沒」這種主觀感覺換成一個當場可驗證的動作，
也防止 `🔍 Exploring` 變成無限期停車場。

### 4.4 畢業去向（必填，畢業時才算數）

**結論落不到第 1 層文件，對 Agent 而言等於不存在。**
`team_protocol.md` §1.11 定義第 1 層＝各模組的 `brd`／`prd`／`hld`／`lld`／`api_spec`／`test_plan`
與 `docs/standards/`；`docs/design_notes/` **不在表上**。

| 去向 | 落在哪個第 1 層文件 | 附帶動作 |
|---|---|---|
| **A. 新開模組** | 新 `docs/features/{模組}/` 底下文件 | 登記前綴、展開 `_TEMPLATE/`、DOCS_MAP 補列 |
| **B. 掛現有模組** | 該模組 `prd`／`hld`／`lld` 對應章節 | 篇幅大時依 §2.1 拉補充檔 |
| **C. 改跨模組規範** | `docs/standards/*.md` | 通常同時要一則 ADR |
| **D. 改流程／基礎建設** | `docs/standards/` | 工單掛在基礎建設模組 |
| **E. 純決策，無文件變更** | 只有 ADR | Icebox 移除 |
| **F. 拆成多份 DN** | 無 | 舊 DN 標 `Split`，子 DN 繼承脈絡 |
| **G. 放棄** | 無 | 標 `🚫 Dropped`，**理由必填** |

**A 還是 B——四條全中才開新模組：**

1. 能一句話講清職責，且不需要說「就是 X 的一部分」
2. 需要自己的 PRD，不是現有 PRD 的一節
3. 預期 **≥ 3 張工單**（一兩張不值得付目錄＋前綴＋DOCS_MAP 的開辦成本）
4. 主要改動的檔案跟現有模組不重疊

紅旗（任一中就別開新的）：描述時反覆引用現有模組／主要改動落在現有模組的檔案／
只有 1–2 張工單的量。**由 AI 提建議＋理由＋反方，使用者拍板。**

### 4.5 DN 全文不折併，但結論必須落地

**這一條刻意偏離 §2.1「工單 `Done` 後折併回主文件」，理由如下：**

- **不折併全文**——探索過程、被否決的方案、錯掉的假設不該進 `lld.md`／`hld.md`；
  §2.1 自己就說那兩份「應只承載目前已生效的架構事實」。DN 的價值恰恰在於它保存了
  **不再生效**的東西。
- **但結論中屬於架構事實的部分必須寫進第 1 層**——這是畢業的必要條件，不是選項。
- **不刪、不搬、凍結唯讀。** DN 記的是被否決的選項與否決理由，刪掉就永遠回答不了
  「當初為什麼不用 X」；搬目錄會弄斷既有連結。

畢業後在 DN 標題底下加一行：

```
> 🎓 已畢業（YYYY-MM-DD）→ {工單號}。本檔凍結，不再更新。
```

### 4.6 其他規則

- **推翻一份已畢業的 DN，開新 DN**，舊的標 `Superseded by DN-0YY`，不改舊檔（沿用 §3 的 ADR 慣例）。
- **DN 不得寫實作步驟。** 開始寫步驟＝該畢業了。這是「DN 退化成第二套工單系統」的防線。
- **軟上限 250 行。** 超過不是違規，是觸發一次檢查：(1) 裝了不只一個待決問題？→ 拆（去向 F）。
  (2) 已經夠寫 AC 了？→ 畢業。兩題都否就註明「已檢查」繼續長。
- **索引用腳本生成，不手動維護。** 生成的索引不可能有孤兒，也不需要 §2.3 那種強制登記儀式。

## 5. 生成檔 (Generated Files)

**生成檔**＝由腳本從別的檔案產生、且納入版控的檔案。目前是
`docs/development/BACKLOG.md`（由 `scan_backlog.py` 從 `docs/features/*/tasks/*.md` 生成）。

### 5.1 內容必須是輸入的純函數

同一份輸入，不管哪一天、由誰、在哪台機器上重跑，都必須產生**位元相同**的輸出。
**不得含時間相依值**——生成時間戳、「N 天內」的時間窗、「停滯 N 天」都不行。

理由不是潔癖，是這條檢查會壞掉：

> **重跑生成腳本，看有沒有 diff ＝ 判斷生成檔是否過期。**

一旦輸出含時間相依值，每天重跑都有 diff，這條檢查就永遠回答「過期」，等於沒有。
時間窗還有第二個代價：**項目會自己從報表裡消失**，沒有任何一筆輸入改變過，
讀報表的人無從得知東西是被移走還是根本沒進來。

### 5.2 時間相依的視圖走 stdout

「哪些工單停滯超過 14 天」是有價值的問題，只是答案不屬於版控檔案。這類視圖：

- 一律只印到 **stdout**，由人或通知管道當場消費
- 腳本要**主動擋掉**寫入檔案的用法，不是靠人記得
  （`scan_backlog.py --stale` 併用 `--output` 會以非零狀態碼結束）

### 5.3 生成檔內不得有人工編輯區以外的手改

生成檔可以保留明確標示的人工維護區塊（例如 BACKLOG 的「冰箱」），腳本必須原樣保留它；
其餘部分手改一定會在下次重生時被蓋掉，等於沒改。

## Sources

- [architecture-decision-record/architecture-decision-record (GitHub)](https://github.com/architecture-decision-record/architecture-decision-record)
- [Architecture Decision Records: the complete guide (2026) | Align Docs](http://docs.align.tech/blog/architecture-decision-records-complete-guide/)
- [Architecture Decision Records (ADRs): The 2026 Guide | Catio](https://www.catio.tech/blog/architecture-decision-record)
- [From decentralized Docs-as-Code to a centralized repository: Evolving Grab's documentation strategy](https://engineering.grab.com/evolving-documentation-strategy)
- [Document as Code: A Practical Guide for Modern Teams — GitDoc](https://gitdoc.ai/resources/document-as-code)
- [mkdocs monorepo plugin (GitHub, Spotify 案例參考)](https://github.com/Bonial-International-GmbH/mkdocs-monorepo-plugin)
