# 功能模組文件骨架 (_TEMPLATE)

新增功能模組時，複製整個 `_TEMPLATE/` 目錄並改名為模組名（snake_case，例如 `user_management_system`），
然後到 `.agent/resources/team_protocol.md` §3.1 登記該模組的三字母前綴。

## 檔案與負責角色

| 檔案 | 內容 | 產出角色 |
|---|---|---|
| `brd.md` | 商業需求：為什麼要做、ROI、利害關係人 | `business-analyst` |
| `prd.md` | 產品需求：功能清單、使用者動線、MVP 範圍 | `product-manager` |
| `hld.md` | 高階架構：系統邊界、元件、資料流 | `system-architect` |
| `lld.md` | 低階設計：ERD、Sequence Diagram、模組細節 | `tech-lead` |
| `api_spec.md` | API 契約（路由、Request/Response、錯誤碼） | `tech-lead` |
| `test_plan.md` | 測試策略與追溯矩陣 | `qa-test-planner` |
| `wireframes/` | 線框圖與互動說明 | `uiux` |
| `tasks/` | 工單，一張一個 `.md`，檔名即 Task ID | `scrum-master` |

> 不是每個模組都需要全套。純後端模組可略過 `wireframes/`；小型模組可把 `hld.md` 併入 `lld.md`。
> 但 `prd.md` 與 `tasks/` 是最低配備——沒有 PRD 就沒有 AC 的來源，沒有 tasks 就進不了 BACKLOG。

## 擴充檔命名

單一檔案過大時拆分，命名為 `{類型}_{三位流水號}_{主題}.md`，例如：
`lld_001_optimistic_update.md`、`lld_003_oauth_registration.md`。原檔保留為索引並指向擴充檔。
