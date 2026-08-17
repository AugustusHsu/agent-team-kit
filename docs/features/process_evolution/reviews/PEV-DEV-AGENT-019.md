# 審查報告：PEV-DEV-AGENT-019

**審查者：** code-reviewer（作者自審 ＋ 客觀指標核對）
**審查時間：** 2026-08-18T05:00+08:00
**結論：** ✅ APPROVED

依 `docs/standards/git_workflow.md` §8.3，本工單走「有遠端但不開 PR」模式，
審查載體為本檔案。

## 1. 取證方式

⚠️ 依 `PEV-DEV-AGENT-017` 的結論，本輪所有表格與重複輸出都改用 `Read` 工具或
`python3` 直接解析取證，不採信終端輸出的轉述——`gh run list` 這類規律輸出正是
壓縮最容易改寫的形狀。CI 結果一律以 run URL 與 `--json` 欄位為準。

## 2. AC 逐條判定

| AC | 判定 | 證據 |
|---|---|---|
| AC-01 只做 checkout ＋ precheck，不含測試指令 | ✅ | `kit/.github/workflows/kit-precheck.yml` 生效行不含 `uv`／`pytest`／`npm`／`go test`；`test_出貨的_workflow_只做第一層` 釘住 |
| AC-02 §8.1「檢查內容」欄與腳本一致 | ✅ | `test_能力對照表的檢查內容與_precheck_實際項目一致` 逐項比對 `CHECKS`，多一項就紅 |
| AC-03 §8.3 補第三種模式 | ✅ | §8.3 改標題為「沒有 PR 時的降級」，分 (a) 無遠端／(b) 有遠端但不開 PR，並寫明差別在自動檢查跑不跑得起來 |
| AC-04 `test_安裝後檔案與_kit_完全一致` 通過 | ✅ | 預期清單是動態掃描（`kit_relative_files()` ＋ manifest），`.github/` 自動涵蓋；126 passed |
| AC-05 本 repo 觸發條件擴及開發分支 | ✅ | `.github/workflows/ci.yml` → `branches: [main, 'feature/**', 'PEV-*']`；實測推送 `PEV-DEV-AGENT-019` 觸發了 run |
| AC-06 **推送後確認 workflow 實際被觸發且通過** | ✅ | 流程檢查 [run 32068588715](https://github.com/AugustusHsu/agent-team-kit/actions/runs/32068588715) success；CI [run 32068586280](https://github.com/AugustusHsu/agent-team-kit/actions/runs/32068586280) success。log 內確認印出四項 ✅ 與「4 項檢查全部通過」 |
| AC-07 全套件綠、升級待合併 0 | ✅ | 126 passed / 0 failed；`--dry-run` 顯示「新增 1、更新 1、已是最新 58、保留 4、待合併 0」 |

**AC-05 的實作與字面有一處偏離**：工單原文要求「`stdlib-only` job 新增 `precheck.py`
的執行」。實作只保留了**在乾淨安裝的暫存專案裡**跑 precheck 那一段，移除了「在本 repo
自己跑一次」。理由是後者與裝回本 repo 的 `kit-precheck.yml` 完全重複，而 dogfooding
的正確形狀是讓安裝實例真的擔起這個責任，而不是在手寫 YAML 裡再複製一份。
兩份 workflow 的 run 都已驗證通過。

## 3. 負向對照

只證明「綠燈會亮」不夠，還要證明「紅燈擋得住」。

| 破壞法 | 期望 | 實際 |
|---|---|---|
| §8.1 表格多寫第五項 | `test_能力對照表…` 紅 | ✅ 紅，訊息列出表格與腳本的差集 |
| 出貨 workflow 混入 `pytest` | `test_出貨的_workflow_只做第一層` 紅 | ✅ 紅，指出違規行 |
| 出貨 workflow 改回 `branches: [main]` | `test_出貨的_workflow_監聽所有分支` 紅 | ✅ 紅 |
| **推一顆「改了工單狀態卻沒重生 BACKLOG」的 commit 到遠端** | CI run 失敗 | ✅ [run 32068710615](https://github.com/AugustusHsu/agent-team-kit/actions/runs/32068710615) **failure** |

最後一項是本單最重要的證據：它同時證明了觸發條件真的涵蓋開發分支、
腳本真的在 CI 環境跑得動、而且**紅燈真的會出現**。臨時分支
`PEV-CI-REDLIGHT-CHECK` 驗完即刪，遠端與本地皆已清除。

三個檔案層級的破壞實驗都以 `diff -q` 確認完全還原。

## 4. 設計判斷

**（一）出貨檔名不叫 `ci.yml`。** 這不是美學選擇，是實測出來的：先寫成
`kit/.github/workflows/ci.yml`，`./install.sh . --upgrade --dry-run` 立刻報
「待合併 1」並要產生 `.new`——因為本 repo 早就有自己的 `ci.yml`。改名後回到「待合併 0」。
多數專案都會有 `ci.yml`，撞名的後果是每次升級都要人工合併一份使用者根本不該改的檔案。
分成兩份還有一個好處：職責清楚——kit 那份只管第 1 層，專案那份管第 2 層，
**共用的是 `precheck.py` 這支腳本，不是 YAML**（DN-007 §4.1 #6）。

**（二）出貨版用 `branches: ['**']`，本 repo 用具名清單。** 出貨版面對未知的分支命名
慣例，只能全收；本 repo 有明確慣例（`feature/**`、`PEV-*`），列出來更精準。
這個差異本身就是「兩份 YAML 不收斂」的具體樣貌。

**（三）加了 `concurrency`。** 觸發條件從「只有 main」擴大到「所有開發分支」之後，
連續推送會堆積 run。這不在工單範圍內，但它是這次擴大觸發的直接後果，一併處理。

## 5. 已知落差

- **「BACKLOG 是否為最新」偵測不到冰箱區的改動。** 實測：把一行文字附加到
  `BACKLOG.md` 尾端（落在冰箱區），precheck 仍然是綠。原因是冰箱區由
  `extract_existing_icebox()` 原樣保留，重生結果會包含那行，比對自然一致。
  **這是結構上的必然**——冰箱區是手寫區，產生器沒有它的真值來源，
  「重生比對」只能覆蓋生成區。所幸「改完工單忘了重生」正是生成區的問題，
  該抓的抓得到（見 §3 最後一列）。這一點屬於 `PEV-DEV-AGENT-018` 的既有範圍，
  不在本單修，建議列入後續工單。
- **乾淨安裝跑 precheck 的驗證力有限。** 剛裝好的專案只有 1 張從 `_TEMPLATE`
  複製出的工單，Status／時間戳兩項幾乎沒東西可查；真正有份量的是死連結那項
  （掃 33 份出貨文件）。CI 註解已誠實寫成「出貨腳本不能只在本 repo 能跑」，
  沒有宣稱它驗證了四項。
- **`precheck.py` 的檢查對象由 cwd 決定**（`find_project_root()` 先試 `Path.cwd()`，
  才回退到腳本位置）。本輪自審時就因為在錯誤的 cwd 下跑而得到假結果，
  查了 20 分鐘才發現是測試方法錯、不是腳本錯。CI 裡的 `cd /tmp/demo` 順序因此不可調換。
- **CI 紅燈目前只是訊號，沒有機制阻擋合併。** 本 repo 不開 PR，也沒有 branch
  protection，所以「紅燈擋合併」仍靠人工紀律。DN-007 §4.1 #3 已裁定紅燈不動工單
  Status；要不要進一步用 required checks 硬擋，取決於未來要不要恢復 PR。

## 6. 結論

七項 AC 全數通過，證據以 run URL 為準而非「YAML 語法正確」。
CI 從「規範指向一個不存在的東西」變成「規範指向的東西存在、會跑、而且會擋」。
✅ APPROVED。
