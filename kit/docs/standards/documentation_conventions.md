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

## Sources

- [architecture-decision-record/architecture-decision-record (GitHub)](https://github.com/architecture-decision-record/architecture-decision-record)
- [Architecture Decision Records: the complete guide (2026) | Align Docs](http://docs.align.tech/blog/architecture-decision-records-complete-guide/)
- [Architecture Decision Records (ADRs): The 2026 Guide | Catio](https://www.catio.tech/blog/architecture-decision-record)
- [From decentralized Docs-as-Code to a centralized repository: Evolving Grab's documentation strategy](https://engineering.grab.com/evolving-documentation-strategy)
- [Document as Code: A Practical Guide for Modern Teams — GitDoc](https://gitdoc.ai/resources/document-as-code)
- [mkdocs monorepo plugin (GitHub, Spotify 案例參考)](https://github.com/Bonial-International-GmbH/mkdocs-monorepo-plugin)
