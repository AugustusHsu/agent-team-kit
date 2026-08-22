# 審查紀錄：PEV-DEV-AGENT-032-FIX-001

**👤 審查者 (Reviewer):** code-reviewer
**📅 審查時間 (Reviewed):** 2026-08-22T01:48+08:00
**🚥 結論:** 通過

---

## 1. AC 逐條核對

| AC | 結論 | 佐證 |
|---|---|---|
| AC-01 對照表改為三列 | ✅ | `kit/docs/standards/git_workflow.md:295-299`（§3.1） |
| AC-02 推論段改寫，刪掉兩個錯敘述 | ✅ | `:301-309`；diff 裡「查無此工單」「一併斷掉」皆為 `-`（§3.2） |
| AC-03 兩條規定維持不變 | ✅ | `:290-291` 未進 diff（§3.3） |
| AC-04 沙盒重跑並留輸出 | ✅ | §2 全文，含對照組與一項新證據 |
| AC-05 032 審查紀錄 C／D 矛盾的處置 | ✅ | §4，不改該檔、在此記明 |
| AC-06 `[平台相關]` 仍為 9 | ✅ | §5 |
| AC-07 install／pytest／precheck | ✅ | §5，待合併 0、141 passed、七項全綠 |
| AC-08 BACKLOG 重生含本工單 | ✅ | §5 |

## 2. AC-04：沙盒重跑

AC-04 明文「只引用本張 §1.2 不算通過」，所以重建了兩份全新的隔離 repo，
腳本留在 `$CLAUDE_JOB_DIR/tmp/ac04_build.sh`／`ac04_probe.sh`，可重跑。
拓撲與 §7.1 形狀 E 一致：三張工單各自開分支、堆疊、只 `--no-ff` 合併最上層。

```
===== A. 形狀 E 拓撲（merge Body 有完整 ID）=====
*   3182e19 merge: [ABC-DEV-BE-003／002／001] 本輪三張工單
|\
| * 69bb957 fix: [ABC-DEV-BE-003] 第三張
| * b5d0e7e fix: [ABC-DEV-BE-002] 第二張
| * ccd20cb fix: [ABC-DEV-BE-001] 第一張
|/
* 42df83c base

--- A1. git log --grep=ABC-DEV-BE-002 --oneline ---
3182e19 merge: [ABC-DEV-BE-003／002／001] 本輪三張工單
b5d0e7e fix: [ABC-DEV-BE-002] 第二張
--- A2. git log --oneline | grep ABC-DEV-BE-002 ---
b5d0e7e fix: [ABC-DEV-BE-002] 第二張
--- A3. git log --oneline --first-parent | grep ABC-DEV-BE-002 ---
(無輸出)
--- A4. git log --oneline --first-parent（完整主線視角）---
3182e19 merge: [ABC-DEV-BE-003／002／001] 本輪三張工單
42df83c base
--- A5. git branch -d 三條 ---
已刪除分支 ABC-DEV-BE-001（曾為 ccd20cb）。
已刪除分支 ABC-DEV-BE-002（曾為 b5d0e7e）。
已刪除分支 ABC-DEV-BE-003（曾為 69bb957）。
```

對照 §7.3 改前的宣稱：

| 查法 | §7.3 改前 | 實測 |
|---|---|---|
| `--grep` | ✅ 找得到 merge | ✅ 找得到 merge **兩顆都找得到**（A1 少列了工單自己那顆） |
| `--oneline \| grep` | ❌ 找不到 | ✅ **找得到**（A2） |
| `--oneline --first-parent \| grep` | 未列 | ❌ 找不到（A3）——真正失效的是這個視角 |

### 2.1 對照組：Body 不列完整 ID

第二份沙盒把 merge 訊息的 Body 換成不帶 ID 的敘述，其餘完全相同：

```
===== B. 對照組（merge Body 不列完整 ID）=====
    merge: [ABC-DEV-BE-003／002／001] 本輪三張工單

    - 第一張做了什麼
    - 第二張做了什麼
    - 第三張做了什麼

--- B1. git log --grep=ABC-DEV-BE-002 --oneline ---
b5d0e7e fix: [ABC-DEV-BE-002] 第二張
--- B2. git log --oneline --first-parent | grep ABC-DEV-BE-002 ---
(無輸出)
--- B3. 合併後刪掉側支分支，再跑 B1（模擬工單分支已回收）---
b5d0e7e fix: [ABC-DEV-BE-002] 第二張
```

B1 直接否掉「Body 若也沒寫完整 ID，`--grep` 這條路一併斷掉」：`--grep` 掃的是
所有可達 commit 的訊息全文，工單自己那顆的第一行就帶著完整 ID，Body 有沒有列
不影響它。

### 2.2 一項工單裡沒有的新證據：分支回收後仍查得到

B3 是本次加測的。原本的疑慮是「`branch -d` 之後那顆 commit 會不會變成不可達」——
不會。`--no-ff` 已把側支接進 merge 的第二父，commit 在 merge 之後仍然可達，
`--grep` 照樣掃得到。這條把「規則的理由」收得更緊：**側支 commit 不是暫時查得到、
之後會消失**，它一直都在，只是 `--first-parent` 看不到。所以 Body 完整 ID 要救的
確實只有那一個視角，不多不少。

## 3. 改了什麼

### 3.1 對照表：兩列 → 三列（`:295-299`）

新增 `--first-parent` 那列，並把前兩列的結果從 ❌ 改回 ✅、補上
`--grep` 其實會回兩顆 commit（A1）。

### 3.2 推論段（`:301-309`）

刪掉的兩句：

- 「`--oneline` 截掉 Body，所以慣用的 `--oneline | grep <TaskID>` 在本形狀下會**查無此工單**」
- 「Body 若也沒寫完整 ID，`--grep` 這條路一併斷掉，那張工單就再也反查不到」

換成的理由：`--no-ff` 保留側支、工單那顆自帶完整 ID（§4），所以前兩列查得到，
且分支回收後仍然可達；真正失效的是 `--first-parent`——它同時是 §7.2 的一輪一行
與 §8.3 在沒有 PR 時建議的主線讀法，該視角下 Body 是唯一還記得住工單粒度的地方。
保留了原本「§6.1 不能只靠 reflog 補救」的呼應，那句與新理由並不衝突。

### 3.3 AC-03：規則沒有被放寬

`:290-291` 的兩條規定（第一行縮寫、Body 逐張列完整 ID）逐字未動，
`git diff` 裡不含這兩行。這是本張最容易走歪的地方——實測結論是「查得到」，
順著寫下去很容易變成「那 Body 好像不必列了」。工單 §2.2 事先寫明了這個誤讀，
執行時據此把改動限縮在理由段。

## 4. AC-05：032 審查紀錄的 C／D 矛盾，不改該檔

`docs/features/process_evolution/reviews/PEV-DEV-AGENT-032.md` §5.2 的沙盒輸出裡：

- **C 段**（`:122-123`）：「第一行縮寫時 `--oneline | grep` 完整 ID 找不找得到 → 找不到」
- **D 段**（`:125-128`）：「側支逐張可見」，列出 `e35d649 fix: [PEV-DEV-AGENT-029] 移除硬編碼`

D 段列出的正是 C 段宣稱找不到的那顆 commit，而且它的第一行就帶著完整 ID——
裸 `--oneline | grep PEV-DEV-AGENT-029` 不可能漏掉它。兩段在同一個 code block 裡
互相否證，當時沒被察覺。合理推測是 C 段實跑的指令帶了 `--first-parent`，
記錄時漏寫，於是結論被寫成了更強的版本。

**處置：不改該檔。** 依 `team_protocol.md` §1.11，已結案工單與其審查紀錄是歷史紀錄，
改它等於竄改「當時是怎麼判斷的」這項事實——而本張要留下的恰恰是「當時判斷錯了、
錯在哪」。真正需要正確的是**規範**（`git_workflow.md` §7.3），那份已經改了；
審查紀錄的角色是佐證，佐證留著原樣才有對照價值。

這也是選擇開 `*-FIX-*` 而不是復活 `032` 的同一個道理（§1.8）：
用一張新工單記載更正，比回頭改舊紀錄更能保住可追溯性。

## 5. 閘門輸出

| 閘門 | 結果 |
|---|---|
| `./install.sh . --upgrade` | 新增 0、更新 1（`docs/standards/git_workflow.md`）、已是最新 59、保留 4、**待合併 0** |
| `uv run pytest` | **141 passed** in 8.19s（與本輪起點相同，本張不新增測試） |
| `python3 .agent/scripts/precheck.py` | **7 項檢查全部通過**，exit 0 |
| `grep -c '\[平台相關\]' kit/docs/standards/git_workflow.md` | **9**（AC-06，未變動） |
| BACKLOG | 已重生，本工單列於結案區 |

`git diff --stat` 只有一個檔：`kit/docs/standards/git_workflow.md | 19 +++++---`
（13 增 6 刪），加上安裝同步的 `docs/standards/git_workflow.md` 與 `.kit-manifest`。

## 6. 為什麼不進「已廢除的流程規則」表

`tests/test_kit_integrity.py` 的 `已廢除的流程規則` 收容的是**被推翻的流程規範**，
用來擋住散落在十三份 SKILL.md 裡的舊說法。本張推翻的是一段**事實敘述**
（某個指令查不查得到），規則本身原封不動。把它收進去會讓那張表開始擋
「`--oneline | grep` 找得到」這種正確的句子，方向剛好相反。工單 §5 已預先寫明，
執行時照辦。

## 7. 退回項目

無。
