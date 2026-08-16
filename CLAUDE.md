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

⚠️ `scan_backlog.py` **預設是 `--format json` 且只印到 stdout**。不加
`--format backlog --output` 就不會寫入 `BACKLOG.md`——直接跑它看起來成功，
BACKLOG 卻完全沒更新。

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
- 在 `kit/docs/standards/` 新增文件要同步登記到 `kit/docs/DOCS_MAP.md`，否則
  `test_standards_文件都登記在_DOCS_MAP` 會失敗（登記檢查只涵蓋 `standards/`）。
- **推翻既有流程規範時**，要把被廢除的舊說法加進 `tests/test_kit_integrity.py` 的
  `已廢除的流程規則` 表。規則散在十三份 SKILL.md 與 evals.json 裡，只靠人工 grep
  漏改不會有任何執行期錯誤——`test_kit_不得殘留已廢除的流程規則` 就是為此而存在。
- **安裝會多產生一個 `kit/` 裡沒有的檔案：`.agent/.kit-manifest`**（升級用的 sha256 基準線）。
  `test_安裝後檔案與_kit_完全一致` 的預期清單因此是「kit 檔案 + manifest」，不是純 kit 檔案。
- **`install.sh` 的種子檔清單**（`is_seed_file()`：`CLAUDE.md`、`.gitignore`、`BACKLOG.md`）
  決定升級時哪些檔案永不覆蓋。改這份清單要同步改 `tests/test_install.py::test_升級保留種子檔`。
- `kit/.agent/resources/team_protocol.md` 改章節結構時，要同步 `kit/docs/standards/team_protocol.md`
  指路檔的章節索引，否則 `test_指路檔章節索引與正版同步` 會失敗。

## Commit

工單分支（含 worktree）上的 commit 直接做，不用先問。**合併回整合分支或主線前**，
必須把合併訊息原文給我複查、取得當次同意；上一次的同意不算。
直接在主線／整合分支上 commit 不適用這項豁免，仍須事前同意。
訊息只描述這個專案的變更，**不得加入 AI 署名 trailer**
（`Co-Authored-By:`、`🤖 Generated with ...`）。完整格式見
`kit/.agent/workflows/commit-message.md`。

## 本專案自己的開發流程（dogfooding）

本 repo **用自己出貨的那套流程開發自己**。根目錄的 `.agent/`、`docs/DOCS_MAP.md`、
`docs/development/`、`docs/standards/`、`docs/features/_TEMPLATE/` 是 `./install.sh .`
裝出來的**安裝實例，視為唯讀**——要改流程規範請改 `kit/` 再重跑安裝，
直接改根目錄那份會在下次升級被 `.new` 衝突淹掉。

例外一（`is_seed_file()` 認定的種子檔，升級不覆蓋）：
`CLAUDE.md`、`.gitignore`、`docs/development/BACKLOG.md`。
`docs/features/README.md` 不在 kit 內，是本 repo 自有檔案，安裝從不碰它。

例外二（**已知缺陷**）：`docs/DOCS_MAP.md` 的「功能模組」表 kit 出貨時就要求專案自行填寫，
但它**不是**種子檔，升級時會被判定為「使用者改過」而產生 `.new` 衝突。
本 repo 已經填了 `PEV`/`KIT`/`WTG` 三列，等於明知故犯。是否列為種子檔見 BACKLOG Icebox。

**worktree 可以用**（2026-08-17 裁定，解除原本的禁用），但有三條硬性要求：
**用完一定要 `git worktree remove`**、**worktree 內的 commit 必須合併回分支**、
收尾後 `git worktree list` 只剩主工作目錄。

kit 出貨的 worktree 規範仍是空的——已於 2026-08-16 整份移除
（見 [DN-003](docs/design_notes/DN-003_git_workflow_and_pr_gate.md)）。
要不要寫回出貨規範由 [DN-006](docs/design_notes/DN-006_branch_topology_and_isolation.md) §4.1 決定：
worktree 只提供工作區隔離、**不解決檔案所有權**，回來時必須連所有權規則一起設計。
