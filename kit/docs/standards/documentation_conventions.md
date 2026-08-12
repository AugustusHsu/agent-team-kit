# 📐 文件分檔與交叉引用守則 (Documentation Conventions)

> 本檔存放不隸屬於特定功能模組、長期有效的**文件組織規範**。目的：避免「補充檔案孤兒化」（存在但沒有任何地方連結到它）與「ADR 編號衝突」這兩類已在本專案發生過的問題再次出現。
> **建立日期**：2026-08-10（起因：`LVS-DEV-FE-FIX-033` 規劃階段整理 `lld_001_optimistic_update.md` 時發現 `lld_003_oauth_registration.md` 從未被 `user_management_system/lld.md` 反向連結）
> **研究依據**：業界 docs-as-code / ADR 實務慣例（見文末 Sources），已依本專案「單人 + AI 虛擬團隊、工單驅動、Markdown + Git 版控」的實際工作方式取捨簡化。

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

`lld_0XX_{主題}.md` / `hld_0XX_{主題}.md`，數字為**該模組內**的流水號（非全域），已有先例：`user_management_system/lld_003_oauth_registration.md`、`labeling_viewing_system/lld_001_optimistic_update.md`。

### 2.3 強制登記（建立補充檔的當下必須同時完成，缺一不可）

1. **正向連結**：在 `DOCS_MAP.md` 對應模組區塊新增一行，指向該補充檔。
2. **反向連結**：在其「母文件」（通常是 `lld.md`/`hld.md` 被補充的那個章節）加一行指回補充檔，註明「詳見 `lld_0XX_xxx.md`」。

只做其中一項＝孤兒文件（本專案已知案例：`lld_003_oauth_registration.md` 有登記在 `DOCS_MAP.md`，但直到 2026-08-10 才補上 `lld.md` 的反向連結）。

## 3. ADR 編號慣例

### 3.1 現況查證（2026-08-10，含 git log 逐項核對）

依 git 歷史逐一核對（而非只看檔案現況），本專案的 ADR 編號實際上經歷過**兩種不同時期的慣例**：

- **2026-04-09 之前**：只有 `user_management_system/hld.md` 一份文件在編號（ADR-01~06）。
- **2026-04-09**：`standards/devenv_spec.md` 建立時正確接續全域最大號，取用 ADR-07~11。
- **2026-04-16 起**：`user_management_system/hld.md` 陸續新增自己的 ADR-07~13，但依據的是「UMS 檔案內自己的最後編號 +1」，**沒有跨檔案查證 `devenv_spec.md` 已用掉 07~11**，於是造成 ADR-07~11（UMS ↔ devenv_spec）長期重複，且此慣例一路延續到 UMS 的 ADR-13（2026-07-21）——當時 `dataset_management_system/hld.md` 已於 6 天前（2026-07-15）用掉 ADR-13，形成 UMS ↔ DMS 的第二組重複。
- **2026-07-22 起**（`labeling_viewing_system/hld.md` 建立 ADR-14）：才真正開始「查證全域最大號 +1」，此後（LVS 14~18 → devenv_spec 19~21）未再出現新的重複。**目前全域最大編號為 ADR-21**（`standards/devenv_spec.md` 之「dev 與 e2e 環境之 Dockerfile/Base Image 自動重建機制」）。

**已知重複（不追溯重編，僅記錄以避免未來誤用，完整清單與雙方連結見 [adr/README.md](adr/README.md) 頂部表格）**：
1. `devenv_spec.md` ADR-07~11 ↔ `user_management_system/hld.md` ADR-07~11（五組重複，2026-04 期間發生）。
2. `dataset_management_system/hld.md` ADR-13 ↔ `user_management_system/hld.md` ADR-13（2026-07-15 vs 07-21）。
3. `standards/adr/README.md` 索引本身在重寫前長期記載一組與任何現行檔案內容都對不上的 ADR-01~06／ADR-07~11 標題——經查證這**不是**「另一套已凍結的歷史決策」，而是該索引自 2026-05-06 建立當下就未與任何檔案同步過的錯誤內容。此索引本身只是指向 ADR 本文的**目錄**，不是 ADR 決策本文，修正指目錄內容不違反「ADR 本文不可回頭編輯」原則，已於本次一併重寫為準確索引。

依 ADR 慣例「不可回頭編輯/重編已存在的 ADR **本文**」（見 Sources），上述第 1、2 項的重複**不追溯重編**，僅明文記錄；第 3 項（索引本身）已直接修正為準確內容。

### 3.2 明文化規則（自 2026-08-10 起適用）

- **新 ADR 一律使用「全專案目前已用過的最大編號 + 1」**，不分模組。撰寫前執行：
  ```bash
  grep -rEn "^#{2,4} ADR-[0-9]+" docs --include=*.md | grep -oE "ADR-[0-9]+" | sort -t- -k2 -n | tail -1
  ```
- **ADR 只在決策已定案／已生效時撰寫**，不對規劃中／尚待驗證的方案預先寫 ADR（本專案現行所有 ADR 皆反映已生效決策，不使用「Proposed」狀態，維持此慣例）。規劃階段的假說與待驗證設計，依 §2 規則寫進補充檔，不寫 ADR。
- 若該 ADR **同時影響多個模組**（如 `devenv_spec.md` 現況），寫入 `standards/devenv_spec.md` 或另立 `standards/adr/ADR-0XX_xxx.md`；若僅影響單一模組，寫入該模組 `hld.md`。無論寫在哪，皆須同步在 `standards/adr/README.md` 補登一行索引（僅登記用途，不影響上述全域流水號）——**這一步先前長期沒被落實**（該索引在 2026-08-10 校正前只收錄了 ADR-08 一條加上一組內容錯誤的 ADR-01~11，DMS/LVS/devenv-19~21 皆未登記），已於本次一併補齊，往後新增 ADR 務必同步更新。

## 4. 本次已修正之具體案例（供對照）

- `user_management_system/lld.md` §2.1：補上指向 `lld_003_oauth_registration.md` 的反向連結。
- `labeling_viewing_system/lld.md` §4.2、§5：補上指向 `lld_001_optimistic_update.md` 的反向連結。
- `DOCS_MAP.md`：`devenv_spec.md` 描述由「ADR-07~11、ADR-19」更新為「ADR-07~11、ADR-19~21」（原描述在 ADR-20/21 新增後未同步更新）；新增 `documentation_conventions.md` 登記列；並發現 **`DOCS_MAP.md` 從未列出 Labeling Viewing System、System Documentation 兩個模組**（兩者整組文件皆孤兒，非僅 `lld_001` 單一檔案），已補上完整模組區塊。
- `standards/README.md`：同步修正 `devenv_spec.md` 描述並新增 `documentation_conventions.md` 登記列。
- `standards/adr/README.md`：經 git log 逐項核對，發現其 ADR-01~06／ADR-07~11 索引內容自建立當下就未與任何檔案實際內容同步過，且完全未收錄 DMS/LVS/devenv-19~21 的 ADR；已重寫為依模組分組、內容與現行 `hld.md`/`devenv_spec.md` 一致的完整索引，並在頂部新增「已知編號重複」表格（UMS↔devenv 的 ADR-07~11、UMS↔DMS 的 ADR-13）。
- `LVS-DEV-FE-FIX-033.md`：修正本次新增的兩個相對路徑連結（指向 `documentation_conventions.md`/`adr/README.md`）算錯層數導致的壞連結（全文連結掃描抓出）。
- `user_management_system/hld.md`：全文連結掃描順帶抓出三處 2026-05-06 文件重構前遺留的壞連結／過時敘述（皆指向重構後未搬遷、已不存在的檔案），已修正：§1.3 ADR-08、§2 系統方塊圖 `drawio`、ADR-06 內文提及之 `workstation架構.drawio`。
- **全 `docs/` 樹壞連結稽核（2026-08-10，腳本掃描 `[text](relative/path)` 逐一驗證檔案是否存在）**：找到 25 個壞連結，全數確認來源後修正或標註，皆為已 `Done` 之歷史工單，未變更其結論性內容：
  - 7 個檔案（UMS `UMS-DEV-AGENT-001/002/003/004/005`、`UMS-DEV-BE-001/004/057`、`UMS-DOC-LLD-002`）誤把 repo-root-relative 路徑（如 `docs/standards/devenv_spec.md`）當作該工單檔案的相對路徑寫，已改為正確的 `../` 層數。
  - `UMS-DOC-EPIC-SYS-004.md`（`api_status_report.md`）、`UMS-DOC-LLD-002.md`（`workstation架構.drawio`／`開發流程.drawio`）：連結指向的檔案未進版控或未隨重構搬遷、現已不存在，改為純文字敘述並加註說明，不保留死連結。
  - `UMS-DEV-AGENT-003.md`（`../agents/.pre-commit-config.yaml`）：查證後確認引用的是撰寫當下另一個舊專案的本機路徑，本來就不是本 repo 內文件，改為純文字敘述並加註說明。
  - `task_management_system/prd.md`（`tasks/_index.md`）：查證全 repo 從未存在任何 `_index.md`（2026-05-06 重構 commit 訊息宣稱有建立但實際未落地），改連結至 `tasks/` 目錄本身。
  - `TMS-DEV-BE-071.md`（`../lld.md`）：連結文字寫「DMS LLD」但相對路徑卻指向不存在的 TMS 自己的 `lld.md`（TMS 模組本無 LLD 文件）——查證 DMS `lld.md` §3.2（非原引用之 §3.3）確有對應之 `dataset_upload_tasks` 表 Schema，改為正確指向 DMS `lld.md` 並校正章節號。

## Sources

- [architecture-decision-record/architecture-decision-record (GitHub)](https://github.com/architecture-decision-record/architecture-decision-record)
- [Architecture Decision Records: the complete guide (2026) | Align Docs](http://docs.align.tech/blog/architecture-decision-records-complete-guide/)
- [Architecture Decision Records (ADRs): The 2026 Guide | Catio](https://www.catio.tech/blog/architecture-decision-record)
- [From decentralized Docs-as-Code to a centralized repository: Evolving Grab's documentation strategy](https://engineering.grab.com/evolving-documentation-strategy)
- [Document as Code: A Practical Guide for Modern Teams — GitDoc](https://gitdoc.ai/resources/document-as-code)
- [mkdocs monorepo plugin (GitHub, Spotify 案例參考)](https://github.com/Bonial-International-GmbH/mkdocs-monorepo-plugin)
