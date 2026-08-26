# Claude Code 專案 adapter

@AGENTS.md

> 共同專案規則只維護在 `AGENTS.md`。本檔只放 Claude Code 專屬載入、MCP 與本機設定；
> 不得複製 commit、測試、架構或文件權威規則。

## Claude context 成本

Claude Code 會在 session 開頭載入專案入口，內容之後持續佔用 context。
Claude 專屬補充同樣採「不寫會不會做錯」判準，避免把一次性資訊留成常駐成本。

全域 Claude 慣例放 `~/.claude/CLAUDE.md`；專案共同規則放 `AGENTS.md`；
只有本專案的 Claude 差異才留在這裡。

## Claude 設定 scope

- 可共享的專案設定：`.claude/settings.json`，可納入版控；
- 個人專案設定：`.claude/settings.local.json`，不得納入版控；
- 登入、訂閱、個人 hook、絕對路徑與暫時停用屬使用者執行層。

不要把 Codex 的 sandbox、App environment、plugin 或 model 設定寫進 `.claude/`。

## MCP scope

初始化或更新本檔時，回報 `claude mcp list` 的伺服器與 scope：

1. 專案專屬 MCP 預設 `--scope project`，寫進 repo 的 `.mcp.json`；
2. `local` 存在使用者設定，換機器會消失；
3. `user` 會在所有專案載入，只有真正跨專案必要的工具才使用；
4. 密鑰以 `${VAR}` 引用，值留在使用者 secrets 檔，不進 repo；
5. 新增 MCP 前評估工具 schema 的固定 context 成本，避免重複內建 filesystem／git 能力。

MCP 是否存在是 Claude execution profile 的能力證據，不得反過來污染 `AGENTS.md` 的共同規則。

## Claude Code 功能探針

`auth status`、訂閱名稱與版本只算 metadata。是否能完成某項任務，以
`docs/standards/agent_runtime.md` 定義的最小功能 probe 為準；兩者矛盾時保留證據並標 degraded。

Claude Code 中途不可用時，依共同入口保存 Task ID、branch／worktree、HEAD、AC 與驗證輸出，
再交由其他合格 execution profile 接手；不得因換供應商而更換 Assignee。
