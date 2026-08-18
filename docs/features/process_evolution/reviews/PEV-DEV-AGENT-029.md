# 審查紀錄：PEV-DEV-AGENT-029

**工單**：[移除 kit 出貨內容裡硬編碼的 uv run](../tasks/PEV-DEV-AGENT-029.md)
**審查者**：code-reviewer
**日期**：2026-08-18
**結論**：✅ **APPROVED**（AC-03 的字面條件不成立，理由見 §3，實質意圖已滿足）

> ⚠️ **本輪開發與審查發生在同一個 context**（§2.3 明列的情況），比照 023／024 的處理：
> §1 每一條附可重跑的指令或檔案:行數，§5 集中列出僅人工判讀的部分。
>
> ✅ **本輪取證通道已通過 §1.12 探針**（2026-08-18 開工時，五行含 Markdown 表格的
> 探針原樣返回、表格前後兩句散文都在），下列 shell 輸出可作為審查證據。

## 1. AC 逐條核對

| AC | 結果 | 證據（可重跑） |
|---|---|---|
| AC-01 `grep -rn "uv run" kit/` 回空 | ✅ | 實跑無任何輸出 |
| AC-02 改用 `python3` | ✅ | 5 處全改成 `python3 .agent/scripts/scan_backlog.py …`，見 §2 |
| AC-03 根目錄 `CLAUDE.md` 不動 | ✅ | `git status --porcelain CLAUDE.md` → **空**；`grep -n "uv run" CLAUDE.md` → `:8`、`:13` 兩行仍在。**但條文字面寫「改動只在 kit/」，這一句不成立**——見 §3 |
| AC-04 實跑被改到的指令 | ✅ | 見 §2 的三組實跑輸出 |
| AC-05 測試與 precheck | ✅ | `uv run pytest` → **135 passed in 6.82s**；`precheck.py` → 6 項全綠 |
| AC-06 BACKLOG 重生成 | ✅ | `BACKLOG.md` 含 PEV-DEV-AGENT-029 |

## 2. AC-04：實跑，不是字串替換

5 處命中其實是**同一條指令**重複出現：

| 檔案:行 | 原本 |
|---|---|
| `kit/.agent/skills/code-reviewer/SKILL.md:141` | `uv run python .agent/scripts/scan_backlog.py --format backlog --output …` |
| `kit/.agent/skills/backend-developer/SKILL.md:38` | 同上 |
| `kit/.agent/skills/frontend-developer/SKILL.md:67` | 同上 |
| `kit/.agent/skills/qa-automation-engineer/SKILL.md:386` | 同上 |
| `kit/docs/development/PLAN_FROM_HANDOFF.md:99` | 同上 |

**改成哪一種寫法不是我挑的**——kit 內既有的正規寫法就是 `python3 .agent/scripts/…`
（`scan_backlog.py:9-13` 自己的 usage、`backlog_template.md:16-18`、
`scrum-master/SKILL.md:155-159`、`precheck.py:114,130` 的錯誤訊息）。
改成 `python3` 是**收斂到既有的那一種**，不是引入第三種拼法。

實跑證據：

| 驗的事 | 指令 | 結果 |
|---|---|---|
| 用的不是專案 venv | `which python3` | `/usr/bin/python3`（`.venv/bin/python` 沒被用到） |
| 版本 | `python3 -V` | `Python 3.12.3` |
| 改後的指令真的能跑 | `python3 .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md` | `exit=0`，BACKLOG 正常寫出 |
| 絕對路徑再驗一次 | `/usr/bin/python3 .agent/scripts/scan_backlog.py --format summary` | 正常輸出統計（process_evolution 30 張、kit_sync 1 張、worktree_guard 1 張） |
| stdlib-only 的根據 | `grep -n "^import \|^from " .agent/scripts/scan_backlog.py` | `argparse` / `json` / `re` / `sys` / `datetime` / `pathlib`——**全部標準函式庫** |

最後一列才是這張工單的真正依據：腳本沒有任何第三方相依，`uv run` 從頭到尾
沒有提供任何東西，只增加了一個使用者專案不見得裝了的前提。

> ⚠️ 想用 `env -i` 剝光環境變數再跑一次當作更強的證據，**被 worktree 隔離擋掉**
> （`env` 包裹的指令無法驗證）。改用絕對路徑 `/usr/bin/python3` 取近似證據——
> 它證明了「不是 venv 裡的 python」，但沒證明「完全不依賴任何環境變數」。

## 3. AC-03 字面不成立：本 repo dogfooding 自己的 kit

AC-03 寫「`git diff --stat` 佐證改動只在 `kit/`」。**這個條件在本 repo 不可能成立**，
因為根目錄的 `.agent/` 是 `./install.sh .` 裝出來的安裝實例，改了 `kit/` 就必須
跑升級把它傳播下去，否則 `test_安裝後檔案與_kit_完全一致` 會紅。

實際的 `git diff --stat`（11 個檔）：

| 類別 | 檔案 |
|---|---|
| 出貨內容（本次真正的修改） | `kit/.agent/skills/{backend,code-reviewer,frontend,qa-automation}-…/SKILL.md`、`kit/docs/development/PLAN_FROM_HANDOFF.md` |
| 安裝實例（由 `install.sh --upgrade` 產生，非手改） | 根目錄同名的 5 個檔 |
| 升級基準線 | `.agent/.kit-manifest` |

`./install.sh . --upgrade` 摘要：`新增 0、更新 5、已是最新 55、保留 4、**待合併 0**`。

**AC-03 的意圖是「不要動到本 repo 自己選擇用 uv 這件事」，這一點完全滿足**：
`CLAUDE.md` 的 `git status` 是空的、兩行 `uv run` 原封不動、`pyproject.toml` 與 CI 未動。
字面條件與意圖的落差來自寫 AC 時沒把 dogfooding 的傳播算進去——記在這裡，
不回頭改已進 In Progress 的 AC 文字。

## 4. 順帶查到、但不在本工單處理

`kit/docs/development/PLAN_FROM_HANDOFF.md:95` 教人用 `$CLAUDE_JOB_DIR/tmp/` 存備份。
那是 **Claude Code 特定的環境變數**，和 `uv run` 屬於同一類問題——把特定執行環境
寫進了要裝到任何專案的出貨內容。本工單 §2 明確限定輸入為 `grep -rn "uv run" kit/`
的命中，不擴大範圍；**這一筆留給 `PEV-DEV-AGENT-025` 的全面盤點或另開工單**。

## 5. 僅人工判讀（無法客觀驗證）

- **「使用者專案不裝 uv 就會失敗」未在真的無 uv 環境驗證。** 本機裝了 uv，
  無法直接示範失敗。推論依據是 `uv run` 在沒有 uv 的機器上是 `command not found`，
  這一步沒有實測。
- **AC-02 後半句沒有適用對象。** 「若某處確實需要專案自己的執行器，改寫成
  『用你的專案執行器』」——5 處全部只是要跑一個 stdlib-only 腳本，
  沒有任何一處需要專案自己的執行器，所以這半句在本次沒有觸發。

## 6. 未處理（不在本工單）

- **不新增「禁止 `uv run` 進 kit」的自動檢查**（工單 §5 明列）。代價是這件事
  會不會復發完全靠人——kit 現在乾淨，但沒有守門員。若要補，屬
  `PEV-DEV-AGENT-026`（自動檢查）的範圍。
- `$CLAUDE_JOB_DIR` 那一筆（見 §4）。
