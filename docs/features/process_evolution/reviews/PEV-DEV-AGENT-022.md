# 審查紀錄：PEV-DEV-AGENT-022

**工單**：[precheck 與 kit 自身測試收斂](../tasks/PEV-DEV-AGENT-022.md)
**審查者**：code-reviewer
**日期**：2026-08-18
**結論**：✅ **APPROVED**

## 1. AC 逐條核對

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 死連結測試改用 `precheck.strip_code()` | ✅ | 新增 `_死連結()` helper，`test_kit_內沒有死連結` 與 `test_README_沒有死連結` 都走它 |
| AC-02 placeholder／略過規則對齊 | ✅ | 測試檔的 `LINK`、`LINK_PLACEHOLDERS` 兩個常數**整個刪掉**，改用 `precheck.LINK_RE`／`PLACEHOLDER_WORDS`／`PLACEHOLDER_CHARS` |
| AC-03 新增「Done 但 Closed 留空」 | ✅ | `check_closed_filled()` |
| AC-04 新增「AC 全打勾但未結案」，排除 `Canceled` | ✅ | `check_ac_matches_status()`，`AC_EXEMPT_STATUSES = {"Done", "Canceled"}` |
| AC-05 `_EXAMPLE-DEV-BE-001` 不誤觸（**實測**） | ✅ | `test_底線開頭的範例工單不會誤觸新檢查`，先斷言檔案真的被複製過來才驗綠燈 |
| AC-06 §8.1「檢查內容」欄同步成六項 | ✅ | `test_能力對照表的檢查內容與_precheck_實際項目一致` 綠 |
| AC-07 兩個方向的負向對照 | ✅ | 見 §3、§4 |
| AC-08 pytest 全綠、`--upgrade --dry-run` 待合併數相符 | ✅ | `tests=135 failures=0 errors=0`；dry-run「更新 2」＝實際改動的 kit 檔案數（`precheck.py`、`git_workflow.md`），「待合併 0」 |

## 2. 開發過程抓到的真實 bug

`CHECKBOX_RE` 第一版寫成 `re.compile(r"^\s*[-*] \[([ xX])\]")`，**漏了 `re.MULTILINE`**。
`^` 於是只錨在整份檔案的開頭，`findall` 永遠回傳空 list，
`if boxes and …` 短路，**新檢查在任何輸入下都不會紅**。

precheck 對本 repo 照樣印綠燈、六項全過——**看起來完全正常**。
是 `test_ac_全打勾但未結案會紅` 把它擋下來的（`assert 0 != 0`）。

這正是這張工單存在的理由的縮影：一個恆綠的檢查器比沒有檢查器更糟，
因為它會讓人以為那個缺口已經被守住。

## 3. 負向對照（a）：造違規輸入

| 檢查 | 輸入 | 結果 |
|---|---|---|
| 結案工單是否填了 Closed | `Status: Done` ＋ `Closed: —` | 🔴 `test_done_沒填_closed_會紅` |
| AC 全打勾的工單是否已結案 | `Status: In Review` ＋ 兩條 AC 全打勾 | 🔴 `test_ac_全打勾但未結案會紅` |

配套的防假紅燈迴歸（**兩項新檢查最大的風險是誤判**）：

| 情境 | 期望 | 結果 |
|---|---|---|
| `Canceled` ＋ AC 全打勾 | 綠 | ✅ `test_canceled_工單允許_ac_全打勾` |
| `In Progress` ＋ AC 有沒打勾的 | 綠 | ✅ `test_ac_還有沒打勾的不算違規` |
| 未結案工單 `Closed: —` | 綠 | ✅ `test_未結案工單的空_closed_不算格式錯誤` |
| `_EXAMPLE-DEV-BE-001.md`（Status 是說明文字、AC 全空） | 綠且不出現在輸出裡 | ✅ `test_底線開頭的範例工單不會誤觸新檢查` |

## 4. 負向對照（b）：把實作改反

| # | 破壞 | 結果 |
|---|---|---|
| b1 | `check_closed_filled` 的判斷式反轉成「Closed **有**填就報」 | 🔴 `❌ 結案工單是否填了 Closed`（現有 24 張工單） |
| b2 | `check_ac_matches_status` 反轉成「**不是**全打勾就報」 | 🔴 `❌ AC 全打勾的工單是否已結案` |

兩項都在真實工單集合上轉紅，證明它們不是恆綠。

### 死連結收斂的驗證：先做的那個對照沒有結論

一開始想用「把 `strip_code` 改成恆等，看 `test_kit_內沒有死連結` 會不會紅」來證明委派是真的。
**結果是綠的**——`kit/` 現有的 markdown 剛好沒有任何「被 code 包住的死連結」，
兩種實作在這份語料上答案一致。**那個對照證明不了任何事。**

改成注入輸入的對照組，才問得出來：

| # | 輸入（加在 `kit/docs/DOCS_MAP.md` 尾端） | 期望 | 結果 |
|---|---|---|---|
| c1 | 死連結放在 ` ``` ` fence 內 | 綠（舊版測試會誤判成紅） | ✅ 綠 |
| c2 | 同一個死連結放在正文 | 紅 | 🔴 紅 |
| c3 | 維持 c1 的輸入，同時把 `strip_code` 改成恆等 | 紅 | 🔴 紅 |
| c4 | 死連結放在行內 `` ` `` 內 | 綠 | ✅ 綠 |
| c5 | 佔位路徑 `reviews/{TaskID}.md` | 綠（舊版測試會誤判成紅） | ✅ 綠 |

**c1 + c3 是決定性的那一對**：c1 說「它被跳過了」，c3 說「跳過來自 `strip_code`」。
少了 c3，c1 也可能只是測試根本沒掃到那個檔案。

c1／c5 同時量化了收斂前的盲點：**舊版測試在這兩種合法寫法上都會出假紅燈**，
而假紅燈會逼作者改成不自然的寫法來閃避（`PEV-DEV-AGENT-016` 被逼過一次）。

## 5. 設計判斷

**「四項」這個數字散在四個地方。** 加檢查時同時要改：`precheck.py` 的 docstring、
`git_workflow.md` §8.1、`test_precheck.py` 的模組 docstring，以及兩個寫死 `== 4` 的斷言。
處置分兩種：

- 能推導的就推導——新增 `檢查項數(專案)` 從 `precheck.py --list` 取得，
  `test_乾淨專案每項全綠` 不再寫死數字。
- 推導不了的留紅燈——`git_workflow.md` §8.1 由既有的
  `test_能力對照表的檢查內容與_precheck_實際項目一致` 盯著。

`test_各項互不短路` 仍寫死 `== 4`，但那是**這張輸入實際違反的項數**，不是總項數；
額外加一條 `✅ + ❌ == 檢查項數` 綁住總數。後兩項與 `Status` 合法值互斥
（`Closed` 留空要 `Status == Done`，AC 檢查要 `Status` 不是 `Done`），湊不進同一張單。

**`check_ac_matches_status` 讀檔而不靠 `parse_task_file`。** 工單 dict 沒有 AC 欄位，
擴充 `scan_backlog.py` 會為了一個檢查污染產生器的資料模型。檢查自己讀檔比較便宜。

**只數核取方塊，不限定在「## 3. 驗收標準」章節內。** 章節標題各專案會改，
而多數的其他核取方塊反而讓判準更寬鬆（多一個沒打勾的就不報）——
往「少報」的方向失效，可以接受；往「誤報」失效則不行。

## 6. 已知邊界

- **只看形狀，看不出勾是不是誠實打的。** 那要跑專案測試＝第 2 層，本單不碰。
- **冰箱區偵測不到**（工單 §5 已排除）：`extract_existing_icebox()` 原樣保留手寫內容，
  沒有真值來源可比對，是結構必然。
- **`Closed` 檢查只認 `Status == "Done"`。** `Canceled` 沒填 `Closed` 不報——
  取消的工單是否該有結案時間沒有定論，維持現狀比猜一個好。
- **既有安裝要跑 `--upgrade` 才會拿到這兩項檢查。** 本 repo 已在本單內跑過
  （`.agent/scripts/precheck.py`、`docs/standards/git_workflow.md`、`.kit-manifest` 同步進 commit）。

## 7. 結論

✅ **APPROVED**。八條 AC 全數達成；(a)(b) 兩個方向的負向對照都做了，
其中一個對照沒有結論並已替換成決定性的 c1／c3 組合；開發中被測試擋下一個
會讓新檢查恆綠的 `re.MULTILINE` 缺漏。
