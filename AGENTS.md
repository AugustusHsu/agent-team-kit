# agent-team-kit

把「AI 虛擬團隊 + 工單驅動開發」的角色、流程與腳本打包成可安裝到任何專案的套件。

## 指令

```bash
uv run pytest                                    # 全套件測試，離線執行
./install.sh <目標專案路徑>                       # 首次安裝
./install.sh <目標專案路徑> --upgrade --dry-run   # 升級既有安裝，先看會動到什麼

# 重新生成 BACKLOG（改完工單狀態一定要跑）
uv run python .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md
```

⚠️ `scan_backlog.py` 預設是 `--format json` 且只印到 stdout；不加
`--format backlog --output` 不會寫入 `BACKLOG.md`。

## 架構

`kit/` 的結構就是安裝後的樣子；`install.sh` 原封不動複製，不改名也不改寫。
`tests/` 只測這個套件，不會被安裝。根目錄 `docs/features/` 是本 repo 自己的工單，
別跟出貨骨架 `kit/docs/features/` 混用；模組前綴登記在 `docs/features/README.md`。

## 陷阱

- `install.sh` 複製工作區而非 git 追蹤內容。`kit/` 的本機產生物排除清單同時在
  `install.sh` 與 `tests/test_install.py::_是本機產生物()`，兩邊必須同步。
- 在 `kit/docs/standards/` 新增文件要同步登記 `kit/docs/DOCS_MAP.md`。
- 推翻流程規範時，要把舊說法加進 `tests/test_kit_integrity.py` 的
  `已廢除的流程規則` 表。
- 安裝會額外產生 `.agent/.kit-manifest`；安裝一致性測試的預期是「kit + manifest」。
- `is_seed_file()` 的清單改動要同步 `tests/test_install.py::test_升級保留種子檔`。
- `kit/.agent/resources/team_protocol.md` 改章節結構時，要同步
  `kit/docs/standards/team_protocol.md` 的索引。

## 多代理執行

- `Assignee` 是專業角色，不是 Claude／Codex 供應商。
- 本專案同時支援 Claude Code CLI、Codex CLI 與 Codex App；選擇依
  `docs/standards/agent_runtime.md` 與 `.agent/agent-runtime.json`，不靠記憶猜測。
- 初始化或能力改變後執行 `.agent/scripts/agent_runtime.py init`、`doctor` 與 `route`；
  token、登入、訂閱、個人 hook、絕對路徑只留在本機層，不得版控。
- 中途換代理不重開工單；交接保留 Task ID、branch／worktree、HEAD、完成與待辦 AC、
  最後可信驗證及外部副作用。

## 取證通道（`team_protocol.md` §1.12 第 2 層）

本專案不配置 context 壓縮 proxy 或其他會改寫工具輸出的中間層。每個 session 第一次取證前
仍依 §1.12 跑五行探針；只有表格與前後散文逐字保留才算通過。若執行環境日後新增中間層，
必須先在本節補上保真方式、驗證與回滾成本。

## 測試技術棧（`qa-automation-engineer` 第 2 層）

- **框架與工具鏈**：Pytest；`uv` 管依賴。`kit/` 出貨的五支 Python 腳本只用標準函式庫，
  測試也不加額外 runtime 套件。全套件零 mock：用 `tmp_path` 造真實檔案、`subprocess`
  實跑腳本，避免把真正要驗的檔案系統行為 mock 掉。
- **執行**：`uv run pytest`；單檔 `uv run pytest tests/test_install.py`；單項 `-k <中文測試名>`。
  沒有分層指令與覆蓋率設定。
- **路徑與命名**：`tests/test_<被測腳本名>.py`；共用 fixture 在 `tests/conftest.py`，
  `tests/fixture_project/` 是安裝測試的假專案。
- **風格**：測試函式名與 assert 訊息用繁體中文；docstring 寫存在理由；參數化用
  `pytest_generate_tests`，不用 `@pytest.mark.parametrize`。

## Commit

工單分支（含 worktree）上的 commit 直接做，不用先問。合併回整合分支或主線前，
必須把合併訊息原文給使用者複查並取得當次同意；上一次同意不算。直接在整合分支上
commit 仍須事前同意。絕不主動 push，禁止 AI 署名 trailer。

格式：`<emoji> <type>(<scope>): <繁中標題>`，空行後 Body 用
`- **標題**：說明` 條列；其餘規則見 `kit/.agent/workflows/commit-message.md`。

## 本專案自己的開發流程

本 repo 用自己的出貨流程開發自己。根目錄 `.agent/`、`docs/DOCS_MAP.md`、
`docs/development/`、`docs/standards/`、`docs/features/_TEMPLATE/` 是安裝實例，視為唯讀；
要改流程規範先改 `kit/`，再跑 `./install.sh . --upgrade`。

種子檔 `AGENTS.md`、`CLAUDE.md`、`.gitignore`、`docs/development/BACKLOG.md`、
`docs/features/README.md` 由專案維護，升級不覆蓋。

worktree 可以用，但用完必須 `git worktree remove`，其中的 commit 必須合併回分支，
收尾後 `git worktree list` 只能剩主工作目錄。worktree 只隔離工作區，不解決檔案所有權。
