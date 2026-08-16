# 📋 跨功能規範區 (Standards)

> 本目錄存放不隸屬於特定功能模組、長期有效的規範文件與共用設計決策。

---

## 本套件提供

| 文件 | 說明 |
|---|---|
| [team_protocol.md](team_protocol.md) | **指路檔**（不含內容）→ 正版在 `.agent/resources/team_protocol.md`；含章節索引與不做 symlink 的理由 |
| [documentation_conventions.md](documentation_conventions.md) | 文件分檔與交叉引用守則、ADR 全域編號慣例 |
| [qa_testing_spec.md](qa_testing_spec.md) | 測試規範與分層策略 |
| [security_audit.md](security_audit.md) | 資安查核表（§1~§2 後端與基礎設施 OWASP Checklist、§3 前端客戶端） |
| [adr/](adr/) | 架構決策紀錄 (ADR) 專區 |

## 依專案自行建立

以下是成熟專案通常會有、但**因為綁定技術棧所以本套件不提供**的文件。建立後請回到 [../DOCS_MAP.md](../DOCS_MAP.md) 補一列。

| 建議檔名 | 內容 |
|---|---|
| `design_system.md` | UI/UX 視覺規範（色票、字級、元件庫慣例），所有前端模組的 UI 基礎 |
| `devenv_spec.md` | 開發環境規格（容器、套件管理、Lint/Format 工具鏈） |
| `third_party_versions.yaml` | 第三方套件版本基準，供 `.agent/scripts/check_versions.py` 比對 |
| `hld.drawio` | 系統整體架構圖原始檔 |

## 團隊協作守則只有指路檔

本目錄的 [team_protocol.md](team_protocol.md) 是**指路檔，不含內容**；唯一正版在 `../../.agent/resources/team_protocol.md`（角色 SKILL 讀的是那份）。

**不要**把正版內容複製進本目錄——兩份一定會 drift，而且拷貝會長得像正版、卻沒人維護。也**不要**改成 symlink：`grep -rn` 不跟隨 symlink，會讓本目錄在日常搜尋中變成黑洞。理由詳見指路檔本身。
