# 模組登記表 (features/)

**這份檔案由專案自己維護。** `DOCS_MAP.md` 只留骨架、不再內嵌這張表——
骨架跟著 kit 升級走，這張表歸專案所有，升級不會互相覆蓋。

## 登記表

複製 [_TEMPLATE/](_TEMPLATE/) 建立新模組後，在下表補一列：

| 前綴 | 模組 | 類型 | 文件 | 工單 |
|---|---|---|---|---|
| `XXX` | *（範例列，建立第一個模組後刪除）* | 功能 | `example_module/` | `example_module/tasks/` |

- **前綴**：三碼大寫、全專案唯一，決定工單 ID 的第一段。
  正版規則見 `../../.agent/resources/team_protocol.md` §3.1。
- **類型**：`功能` 或 `基礎建設`。**基礎建設模組不需要 PRD**——CI、安裝腳本、
  開發流程本身沒有使用者故事可寫，規格直接寫在工單的「規格：輸入與輸出」。
- **文件**：模組主文件的入口；沒有 PRD 就寫「*（無 PRD，規格在工單內）*」。

## 目錄慣例

```
features/<模組>/
├── prd.md / hld.md / lld.md ...   # 功能模組才有；基礎建設模組可整組省略
└── tasks/<TaskID>.md              # 工單，一律要有
```

工單狀態以工單自己的 `**🚥 任務狀態 (Status):**` 為準，
彙整報表由 `.agent/scripts/scan_backlog.py` 生成到 `docs/development/BACKLOG.md`。
