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
- **`install.sh` 的種子檔清單**（`is_seed_file()`：`CLAUDE.md`、`.gitignore`、`BACKLOG.md`、
  `docs/features/README.md`）決定升級時哪些檔案永不覆蓋。改這份清單要同步改
  `tests/test_install.py::test_升級保留種子檔`。
- `kit/.agent/resources/team_protocol.md` 改章節結構時，要同步 `kit/docs/standards/team_protocol.md`
  指路檔的章節索引，否則 `test_指路檔章節索引與正版同步` 會失敗。

## 取證通道（`team_protocol.md` §1.12 第 2 層）

§1.12 規定每個專案要記下自己的通道狀況，本節就是本 repo 的那一份。
判準與探針在 §1.12，**這裡不重複**。

**中間層是哪一套**：本機開發環境跑 **headroom**（本地 context 壓縮 proxy，
`~/.local/bin/headroom`，以 `uv tool` 安裝的 `headroom-ai`）。它預設保護
Read／Glob／Grep／Write／Edit／WebSearch／WebFetch，**刻意不保護 Bash**——
原始碼註解直言 shell 輸出（build log、測試輸出）是理想的壓縮目標。
未保真時實測：五行含 Markdown 表格的文字送出去，回來只剩 `[{"a":"1","b":"2"}]`，
前後兩句散文整段消失且**不留任何提示**。若你的環境沒跑 headroom，本節不適用，
但 §1.12 的開工探針照跑——沒有中間層這件事也要由探針證實。

**保真怎麼開**：`~/.bashrc` 一行 `export HEADROOM_PROTECT_TOOL_RESULTS=Bash`。
生效條件有兩個，**缺一都不會生效**：

- **proxy 必須重啟**——設定是 proxy 進程啟動時從環境變數繼承的，改 rc 不影響已在跑的 proxy；
- **必須從新開的終端啟動**——舊終端沒有這個變數，`headroom wrap` 也就傳不下去。

**驗證看 proxy 端，不是看自己的 shell**：
`tr '\0' '\n' < /proc/$(pgrep -f 'headroom.cli proxy')/environ | grep PROTECT`。
在既有終端 `echo $HEADROOM_PROTECT_TOOL_RESULTS` 是空的**不代表沒生效**，
反之亦然——最終仍以 §1.12 的探針輸出為準。

⚠️ **重啟的坑**：舊 proxy 還被 session 連著時，新 wrap 不會殺它（defer-until-idle），
而是**靜默 fallback 到 8788／8789**——於是你以為換新版了，其實還連在舊 proxy 上。
重開前先 `pgrep -af 'headroom.cli proxy'` 確認乾淨。

**成本與回滾**：關掉有損壓縮不影響 headroom 的主要價值——實測帳單裡有損壓縮只佔
省下金額的 1.2%，其餘來自無損的 tool schema 去重與 prefix cache。
回滾就是移除 `~/.bashrc` 那行（備份 `~/.bashrc.bak-headroom-20260818`）再重啟 proxy。

## 測試技術棧（`qa-automation-engineer` 第 2 層）

該 Skill 只定義測試工程的原則，框架與路徑由本節補。缺這節它在本 repo 就是空的。

- **框架與工具鏈**：Pytest（`uv` 管依賴，dev group 只有 `pytest>=8`）。
  **不裝任何外部套件**——`kit/` 出貨的三支腳本只用標準函式庫，測試也跟著只用標準函式庫，
  這樣才驗得到「使用者專案不必安裝任何東西」。
  **全套件 0 處 mock**：一律用 `tmp_path` 造真實檔案、`subprocess` 實跑腳本再驗輸出，
  因為要測的正是「腳本在真實檔案系統上做對了沒」，mock 掉就什麼都沒驗到。
- **執行指令**：`uv run pytest`（`testpaths=["tests"]`、`addopts="-q"` 已寫在 `pyproject.toml`）。
  單檔用 `uv run pytest tests/test_install.py`，單項用 `-k <中文測試名>`。
  **沒有分層指令，也沒有覆蓋率設定**——套件小，全跑不到一秒。
- **存放路徑與命名**：`tests/test_<被測腳本名>.py`，一支腳本對一支測試檔，**不分 unit／integration**。
  共用 fixture 在 `tests/conftest.py`；`tests/fixture_project/` 是安裝測試用的假專案骨架。
- **風格專屬**：測試函式名與 assert 訊息一律用**繁體中文**（`test_安裝後檔案與_kit_完全一致`），
  docstring 寫「為什麼這條要存在」而不是複述程式碼。
  參數化用 `pytest_generate_tests`，不用 `@pytest.mark.parametrize`。

## Commit

工單分支（含 worktree）上的 commit 直接做，不用先問。**合併回整合分支或主線前**，
必須把合併訊息原文給我複查、取得當次同意；上一次的同意不算。
直接在主線／整合分支上 commit 不適用這項豁免，仍須事前同意。
訊息只描述這個專案的變更，**不得加入 AI 署名 trailer**
（`Co-Authored-By:`、`🤖 Generated with ...`）。
格式：`<emoji> <type>(<scope>): <繁中標題>`，空行後 Body 用 `- **標題**：說明` 條列。
對照表與其餘規則見 `kit/.agent/workflows/commit-message.md`。

## 本專案自己的開發流程（dogfooding）

本 repo **用自己出貨的那套流程開發自己**。根目錄的 `.agent/`、`docs/DOCS_MAP.md`、
`docs/development/`、`docs/standards/`、`docs/features/_TEMPLATE/` 是 `./install.sh .`
裝出來的**安裝實例，視為唯讀**——要改流程規範請改 `kit/` 再重跑安裝，
直接改根目錄那份會在下次升級被 `.new` 衝突淹掉。

例外（`is_seed_file()` 認定的種子檔，升級不覆蓋）：`CLAUDE.md`、`.gitignore`、
`docs/development/BACKLOG.md`、`docs/features/README.md`。

模組登記表 2026-08-17 依 PEV-DEV-AGENT-009 從 `docs/DOCS_MAP.md` 抽到
`docs/features/README.md` 並列為種子檔：**要專案自己填的表才是種子檔，骨架不是**。
DOCS_MAP 因此重新變回純骨架，升級推得動，也不再產生 `.new`。

**worktree 可以用**（2026-08-17 裁定，解除原本的禁用），但有三條硬性要求：
**用完一定要 `git worktree remove`**、**worktree 內的 commit 必須合併回分支**、
收尾後 `git worktree list` 只剩主工作目錄。

kit 出貨的 worktree 規範仍是空的——已於 2026-08-16 整份移除
（見 [DN-003](docs/design_notes/DN-003_git_workflow_and_pr_gate.md)）。
要不要寫回出貨規範由 [DN-006](docs/design_notes/DN-006_branch_topology_and_isolation.md) §4.1 決定：
worktree 只提供工作區隔離、**不解決檔案所有權**，回來時必須連所有權規則一起設計。
