# 審查紀錄：PEV-DEV-AGENT-031

**👤 審查者 (Reviewer):** code-reviewer
**📅 審查時間 (Reviewed):** 2026-08-21T21:26+08:00
**🚥 結論:** 通過

---

## 1. AC 逐條核對

| AC | 結論 | 佐證 |
|---|---|---|
| AC-01 `check_assignee_valid` 實作並註冊 | ✅ | `kit/.agent/scripts/precheck.py:274` 定義、檔尾 `CHECKS` 第 7 筆；`--list` 印出七行（§4） |
| AC-02 合法值讀自 `.agent/skills/`，不寫死 | ✅ | `available_roles()`（`:252`）掃目錄；`test_合法角色讀自_skills_目錄而不是寫死清單` 是它的可執行證明（§3.2） |
| AC-03 只檢查未結案工單、不動 012／013 | ✅ | 沿用 `AC_EXEMPT_STATUSES`；`git status` 全程未出現 012／013（§5） |
| AC-04 負向對照實跑、輸出留檔 | ✅ | §2 全文輸出，四項資訊逐一對照 |
| AC-05 三處「六項」同步為七項 | ✅ | §4 |
| AC-06 正負向測試各至少一個、pytest 全綠 | ✅ | §3；141 passed（§5） |
| AC-07 `./install.sh . --upgrade` 已跑 | ✅ | §5，待合併 0 |
| AC-08 precheck 七項全綠 | ✅ | §2 還原後的輸出 |
| AC-09 BACKLOG 重生含本工單 | ✅ | §5 |

## 2. AC-04：負向對照實跑

工單 AC-04 明文「只寫『不合法』不算通過」，所以這裡要證明的不是「會紅」，
而是**紅燈訊息足以讓人不必翻檔案就修好**。

**造違規**：把 `PEV-DEV-AGENT-028`（Status `Pending`，未結案）第 5 行的
Assignee 由 `system-architect` 改成 `systems-architect`——刻意只差一個 `s`，
因為真實的這類缺陷（012／013 的 `backend-engineer`）就是這個量級的錯字。

```
$ sed -i '5s/system-architect/systems-architect/' docs/features/process_evolution/tasks/PEV-DEV-AGENT-028.md
$ python3 .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md
$ python3 .agent/scripts/precheck.py
✅ BACKLOG 是否為最新
✅ 工單 Status 值是否合法
✅ 工單時間戳是否正確
✅ 文件是否有死連結
✅ 結案工單是否填了 Closed
✅ AC 全打勾的工單是否已結案
❌ 未結案工單的 Assignee 是否合法
   docs/features/process_evolution/tasks/PEV-DEV-AGENT-028.md:5：Assignee 不是實際存在的角色：'systems-architect'；合法值為 ['backend-developer', 'business-analyst', 'code-reviewer', 'devops-engineer', 'frontend-developer', 'manual_user', 'product-manager', 'qa-automation-engineer', 'qa-test-planner', 'scrum-master', 'security-engineer', 'system-architect', 'tech-lead', 'uiux']，或留空填 —

1/7 項檢查未通過。   ← 走 stderr
$ echo $?
1
```

AC-04 要求的四件事逐一對照：

| 要求 | 訊息裡的哪一段 | 沒有它會怎樣 |
|---|---|---|
| 哪張工單 | `docs/features/process_evolution/tasks/PEV-DEV-AGENT-028.md` | 得自己 grep 全部工單 |
| 哪一行 | `:5` | 檔案裡有八個 metadata 欄位，要逐行找 |
| 填了什麼 | `'systems-architect'`（帶引號，看得出前後有無空白） | 只說「不合法」等於沒說 |
| 合法值有哪些 | 14 個值的完整列表，含 `manual_user` 與「留空填 —」 | 得自己去 `ls .agent/skills/`，還猜不到 `manual_user` 也放行 |

**還原**：

```
$ sed -i '5s/systems-architect/system-architect/' docs/features/process_evolution/tasks/PEV-DEV-AGENT-028.md
$ python3 .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md
$ python3 .agent/scripts/precheck.py
✅ BACKLOG 是否為最新
✅ 工單 Status 值是否合法
✅ 工單時間戳是否正確
✅ 文件是否有死連結
✅ 結案工單是否填了 Closed
✅ AC 全打勾的工單是否已結案
✅ 未結案工單的 Assignee 是否合法

7 項檢查全部通過。
$ echo $?
0
```

還原是否乾淨不靠肉眼比對：`git status --short` 回到動工前的六個檔案，
`028` 與 `BACKLOG.md` 都不在清單裡。

### 2.1 取證時踩到的一個假象（記錄下來免得下次誤判）

第一次把輸出導進檔案取證時，`1/7 項檢查未通過。` 出現在**所有 ✅ 之前**，
看起來像輸出順序壞了。實際是 stream 差異：失敗摘要走 `sys.stderr`
（`precheck.py:377`），通過摘要走 stdout（`:379`），`2>&1` 重導時
stderr 無緩衝先落地、stdout 到行程結束才 flush。

**這不是 bug，也不需要改**——終端機上兩者交錯輸出、順序正常。
記在這裡是因為它與 `team_protocol.md` §1.12 要防的「通道改寫了證據」長得很像，
但成因完全不同：§1.12 是中間層改內容，這是本地 buffering 改順序。
**判準：§1.12 的失真在同一個 stream 內也會發生，buffering 假象只在合併兩個 stream 時出現**——
分開導向（`1>a 2>b`）就會消失。

## 3. AC-06：新增的測試

`tests/test_precheck.py` 新增四個（工單只要求正負向各一個）。

### 3.1 負向：`test_assignee_不是實際存在的角色會紅`（`:167`）

不只斷言「returncode != 0」——那樣任何一項紅都會讓它綠。它把 AC-04 的四件事
全部寫成 assertion：訊息含填錯的值、含工單路徑、含合法值 `backend-developer`，
且**回報的行號真的指得回 Assignee 那一行**：

```python
行號 = int(訊息.split(TASK + ":")[1].split("：")[0].split()[0])
原文 = (乾淨專案 / TASK).read_text(encoding="utf-8").splitlines()
assert "負責人 (Assignee)" in 原文[行號 - 1], f"回報行號 {行號} 指到 {原文[行號 - 1]!r}"
```

這條沿用 `test_死連結行號指得回原始檔案` 已有的做法：行號寫得出來不代表寫得對，
而寫錯的行號比不寫更浪費時間。

### 3.2 正向三個

| 測試 | 守的是什麼 | 不寫會怎樣 |
|---|---|---|
| `test_合法角色讀自_skills_目錄而不是寫死清單`（`:283`） | 在測試專案裡 `mkdir .agent/skills/data-engineer` 後，該角色立刻算合法 | AC-02 只是一句宣告。寫死清單的實作照樣讓其他測試全綠——而且是最糟的那種紅：專案愈認真擴充團隊，紅得愈厲害 |
| `test_留空與_manual_user_的_assignee_不算違規`（`:299`） | `—` 與 `manual_user` 兩個值都放行 | 判紅只會逼人隨便填一個角色進去閃避，檢查於是製造出它本來要防的錯誤 |
| `test_已結案工單的錯誤_assignee_不算違規`（`:312`） | `Done` 工單填 `backend-engineer` 仍綠 | 這正是 012／013 的形狀。少了它，日後有人「順手把檢查改成涵蓋全部工單」不會有任何測試擋下來，而那個改動會製造一個**只能靠違反 §1.11 才解得掉的紅燈** |

### 3.3 順帶修正的 fixture

`_工單()` 原本寫死 `**👤 負責人 (Assignee):** backend-engineer`——**跟 012／013 是同一個錯字**。
新檢查上線後它會讓 17 個既有測試全部轉紅。

處置：把 Assignee 提成參數（預設 `backend-developer`），負向測試才有辦法傳入違規值。
這不是為了讓測試通過而遷就檢查——`backend-engineer` 在任何專案裡都不對應任何角色，
fixture 造的是一張**不合法的工單**，本來就該修。

> 📌 這筆意外收穫本身就是 AC-02 的旁證：新檢查在自己的測試套件裡抓到了第三筆
> `backend-engineer`。工單只知道 012／013 兩筆。

## 4. AC-05：三處「六項」同步

| 位置 | 現況 |
|---|---|
| `precheck.py` 開頭 docstring | 「七項檢查（見 `docs/standards/git_workflow.md` §8）」，並補上第 7 條說明（`:8`） |
| `--list` 輸出 | 印出七行——**不是另一份表述**，它直接遍歷 `CHECKS`，加一筆就自動多一行 |
| `git_workflow.md` §8.1 能力對照表 | `:317` 「自動檢查」列尾端加上「、未結案工單的 Assignee 是否合法」 |

```
$ python3 .agent/scripts/precheck.py --list
- BACKLOG 是否為最新
- 工單 Status 值是否合法
- 工單時間戳是否正確
- 文件是否有死連結
- 結案工單是否填了 Closed
- AC 全打勾的工單是否已結案
- 未結案工單的 Assignee 是否合法
```

`tests/test_precheck.py` 的 `檢查項數()` 也讀 `--list` 而非寫死數字，
所以「加檢查忘了改測試」這條路本來就不通。§8.1 那列則由既有的
`test_能力對照表的檢查內容與_precheck_實際項目一致` 盯著。

**全文掃過殘留的「六項」**：`grep -rn 六項 kit/ docs/ tests/` 剩下的都不必改——
不是已結案工單／審查紀錄的歷史敘述，就是「其餘六項照樣全綠」這種正確語意
（`precheck.py:278` 的 docstring 與 `test_precheck.py:170` 都是在描述缺陷本身：
Assignee 打錯時**其他**六項確實全綠）。

`grep -c '\[平台相關\]' kit/docs/standards/git_workflow.md` 仍為 **9**，
§8.1 的改動沒有動到 §9 換平台清單的對照數。

## 5. 閘門輸出

| 項目 | 結果 |
|---|---|
| `uv run pytest` | **141 passed**，exit 0 |
| `python3 .agent/scripts/precheck.py` | 七項全綠，exit 0 |
| `./install.sh . --upgrade` | 新增 0、更新 2（`.agent/scripts/precheck.py`、`docs/standards/git_workflow.md`）、已是最新 58、保留 4、**待合併 0** |
| `git status --short` | 6 個 `M`，全部在本工單的連動表內；`012`／`013` 不在其中 |

**本輪測試數推進**（工單 AC-06 寫的「135 + 新增數」在本輪會過期，改記實測）：

| 時點 | 通過數 |
|---|---|
| 本輪起點 | 135 |
| `026` 落地後 | 137（＋2：檢查 B、檢查 A+） |
| `027` 落地後 | 137（027 改的是 skill 內容，不新增測試） |
| `031` 落地後 | **141**（＋4：負向 1、正向 3） |

`docs/development/BACKLOG.md` 已用 `scan_backlog.py --format backlog --output` 重生
（本輪最後一次是在負向對照還原後），本工單以 Done 列入。

## 6. 實作上的兩個取捨

**`available_roles()` 找不到 `.agent/skills/` 時回 `None` 而非空集合。**
空集合會讓每一張工單都紅——kit 還沒裝完的專案於是開場就是一整排紅燈，
把真正的問題蓋掉。回 `None` 則整項跳過：沒有判準時不判，比亂判好。

**只驗「這個角色存在嗎」，不驗「這個角色適合這張工單嗎」。**
後者是判斷不是事實（工單 §5 明文排除）。這與 `026` 兩項檢查的邊界是同一條：
**閘門只驗證得了事實，語意判斷留給人。**

## 7. 退回項目

無。
