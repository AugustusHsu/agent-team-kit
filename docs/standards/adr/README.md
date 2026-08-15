# 🏛️ 架構決策紀錄索引 (ADR Index)

> 本檔是全專案 ADR 的**唯一索引**。每新增一則 ADR，都必須回來這裡補一行——編號規則與撰寫時機見
> [../documentation_conventions.md §3](../documentation_conventions.md)。

## 什麼算 ADR

一則 ADR 記錄「**為什麼**選這個方案」，而不是「這個方案**是什麼**」。後者屬於 HLD/LLD。
典型的 ADR 標題長這樣：「Session 驗證機制採用 Hybrid JWT」「Python 套件管理工具選型」。

只有**已定案、已生效**的決策才寫 ADR。規劃中、待驗證的方案寫成補充檔（見
[../documentation_conventions.md §2](../documentation_conventions.md)）。

## ADR 寫在哪裡

| 決策影響範圍 | 決策本文寫在 | 索引 |
|---|---|---|
| 單一功能模組 | 該模組的 `docs/features/{模組}/hld.md` 內文 | 一律回本檔登記 |
| 跨模組／全專案（技術棧、開發環境、CI） | `docs/standards/` 下的對應文件，或獨立的 `ADR-0XX_{主題}.md` | 一律回本檔登記 |

獨立檔案時的命名：`ADR-0XX_{主題}.md`，例如 `ADR-012_image_storage_proxy.md`。

## 編號規則（最重要的一條）

**全域唯一，不分模組。** 新增前先查出目前最大號，`+1`：

```bash
grep -rEn "^#{2,4} ADR-[0-9]+" docs --include=*.md | grep -oE "ADR-[0-9]+" | sort -t- -k2 -n | tail -1
```

> ⚠️ 各模組各自遞增編號是最常見的錯誤——一旦兩份文件同時用掉同一個號碼，之後所有引用都會產生歧義，而且很難回頭校正。

## 索引

<!--
  依模組分組。每則 ADR 一行，格式：
  | ADR-0XX | <決策標題> | <決策本文位置> | <定案日期 YYYY-MM-DD> |
  建立第一個模組後，把下面這列範例刪掉。
-->

| ADR | 標題 | 決策本文位置 | 定案日期 |
|---|---|---|---|
| — | *（尚無 ADR。新增後刪除本列）* | — | — |
