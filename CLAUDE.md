# agent-team-kit

把「AI 虛擬團隊 + 工單驅動開發」的角色、流程與腳本打包成可安裝到任何專案的套件。

## 指令

```bash
uv run pytest                                    # 全套件測試，離線執行
./install.sh <目標專案路徑>                       # 首次安裝
./install.sh <目標專案路徑> --upgrade --dry-run   # 升級既有安裝，先看會動到什麼
```

## 架構

`kit/` 底下的結構**就是**安裝後在使用者專案裡的樣子——`install.sh` 是原封不動複製，
不做任何改名或改寫。改 `kit/` 內任何檔案 = 改出貨內容。

`tests/` 不會被安裝，是這個套件自己的測試。

根目錄的 `docs/features/` 是**這個 repo 自己的工單**（套用 kit 的慣例，但不會被安裝），
別跟出貨樣板 `kit/docs/features/` 搞混；模組前綴登記在 `docs/features/README.md`。

## 陷阱

- **`install.sh` 複製的是工作區內容，不是 git 追蹤的內容。** 在 `kit/` 底下跑出來的本機
  產生物（`__pycache__`、`.pyc`）會被裝進使用者專案。排除清單同時寫在 `install.sh` 與
  `tests/test_install.py` 的 `_是本機產生物()`，**兩邊必須同步改**，否則
  `test_安裝後檔案與_kit_完全一致` 會失敗。
- 在 `kit/docs/` 新增文件要同步到 `kit/docs/DOCS_MAP.md` 登記，否則連結測試會抓到孤兒文件。
- **安裝會多產生一個 `kit/` 裡沒有的檔案：`.agent/.kit-manifest`**（升級用的 sha256 基準線）。
  `test_安裝後檔案與_kit_完全一致` 的預期清單因此是「kit 檔案 + manifest」，不是純 kit 檔案。
- **`install.sh` 的種子檔清單**（`is_seed_file()`：`CLAUDE.md`、`.gitignore`、`BACKLOG.md`）
  決定升級時哪些檔案永不覆蓋。改這份清單要同步改 `tests/test_install.py::test_升級保留種子檔`。
- `kit/.agent/resources/team_protocol.md` 改章節結構時，要同步 `kit/docs/standards/team_protocol.md`
  指路檔的章節索引，否則 `test_指路檔章節索引與正版同步` 會失敗。

## Commit

commit 前必須把訊息原文給我複查，取得當次同意才執行；上一次的同意不算。
訊息只描述這個專案的變更，**不得加入 AI 署名 trailer**
（`Co-Authored-By:`、`🤖 Generated with ...`）。完整格式見
`kit/.agent/workflows/git-commit.md`。

## Worktree

背景執行或多 Agent 並行時，動程式碼前先開 worktree，分支名 = Task ID。
預設同時只允許一個；規則見 `kit/docs/standards/worktree_workflow.md`。
