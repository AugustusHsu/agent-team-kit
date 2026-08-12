# 這個 repo 自己的工單

這裡是 **agent-team-kit 本身的開發工單**，套用 `kit/` 出貨的那套慣例
（`docs/features/{模組}/tasks/{TaskID}.md`），但**不會被 `install.sh` 安裝**。

不要跟 `kit/docs/features/` 搞混——那是要複製到使用者專案的樣板。

## 模組前綴對照表

`kit/.agent/resources/team_protocol.md` §3.1 的對照表屬於出貨內容，
只放範例前綴，不能拿來登記本 repo 的模組。本 repo 的前綴登記在這裡。

| 前綴 | 模組名稱 | 對應目錄 |
|------|---------|---------|
| `WTG` | worktree 防孤兒機制 | `docs/features/worktree_guard/` |

新增模組時先在上表登記前綴，再開工單。
