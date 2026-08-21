# [Task ID: PEV-DEV-AGENT-032-FIX-001] 更正 git_workflow.md §7.3 的反查對照表

**🔗 依附母任務 (Parent Task ID):** —（回歸來源工單：`PEV-DEV-AGENT-032`）
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Ready
**📅 建立時間 (Created):** 2026-08-22T01:12+08:00
**✅ 完成時間 (Closed):** —
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

**回歸來源工單：`PEV-DEV-AGENT-032`**（Status `Done`，由 `b4dbd47` 合併）。
依 `team_protocol.md` §1.8「成因工單已 `Done` 不得復活」，本張以 `*-FIX-*` 收容。

`032` 寫進 `kit/docs/standards/git_workflow.md` §7.3 的反查對照表（`:293-302`）
有兩處與實測不符。缺陷在 `026`／`027`／`031` 那一輪——**§7 形狀 E 的第一次實戰**——
照著規範走完之後，拿規範自己列的查法去驗收時暴露。

### 1.1 §7.3 現在說什麼

| 查法 | §7.3 宣稱 |
|---|---|
| `git log --grep=ABC-DEV-BE-002` | ✅ 找得到那顆 merge commit |
| `git log --oneline \| grep ABC-DEV-BE-002` | ❌ **找不到**——`--oneline` 只給第一行 |

並在 `:300-302` 推論：

> `--oneline` 截掉 Body，所以慣用的 `--oneline | grep <TaskID>` 在本形狀下會**查無此工單**。
> Body 若也沒寫完整 ID，`--grep` 這條路一併斷掉，那張工單就再也反查不到。

### 1.2 隔離沙盒實測

沙盒重建 §7.3 描述的完全相同拓撲（形狀 E：三張工單堆疊、只 `--no-ff` 合併最上層、
三條 `branch -d` 全部成功），並沿用 §7.3 自己的 ID 格式：

```
*   acb6d3d merge: [ABC-DEV-BE-003／002／001] 本輪三張工單
|\
| * 401b8fd fix: [ABC-DEV-BE-003] 第三張
| * ba4d7e8 fix: [ABC-DEV-BE-002] 第二張
| * 007e766 fix: [ABC-DEV-BE-001] 第一張
|/
* 7fc6b22 base

$ git log --grep=ABC-DEV-BE-002 --oneline
acb6d3d merge: [ABC-DEV-BE-003／002／001] 本輪三張工單
ba4d7e8 fix: [ABC-DEV-BE-002] 第二張

$ git log --oneline | grep ABC-DEV-BE-002
ba4d7e8 fix: [ABC-DEV-BE-002] 第二張          ← §7.3 說這裡應該「找不到」

$ git log --oneline --first-parent | grep ABC-DEV-BE-002
（無輸出）                                     ← 只有加上 --first-parent 才成立
```

第二個推論另建一份沙盒對照（把 merge 訊息的 Body 拿掉完整 ID）：

```
$ git log --grep=ABC-DEV-BE-002 --oneline
ba4d7e8 fix: [ABC-DEV-BE-002] 第二張          ← §7.3 說「--grep 這條路一併斷掉」，並沒有
```

本 repo 的真實歷史同樣重現：`git log --oneline | grep PEV-DEV-AGENT-027`
找得到 `cb62caf`；`git log --oneline | grep PEV-DEV-AGENT-032` 找得到 `1d011b2`。

### 1.3 成因

`--no-ff` **保留工單自己那顆 commit**，它的第一行帶著完整 Task ID，
所以裸 `--oneline` 與 `--grep` 都掃得到。§7.3 誤把
「`--first-parent` 主線視角下看不到」寫成「整個 repo 裡找不到」。

證據其實一直在 `032` 自己的審查紀錄裡：
`docs/features/process_evolution/reviews/PEV-DEV-AGENT-032.md` §5.2 的 **D 段
「側支逐張可見」列出的三顆 commit，正是 C 段宣稱找不到的東西**——
同一份沙盒輸出裡 C 與 D 自相矛盾，當時沒被發現。
推測 C 段實跑的指令帶了 `--first-parent` 而記錄時漏寫。

### 1.4 結論不受影響，錯的是理由

**「Body 必須列完整 ID」這條規則本身仍然成立，不要因為本張而放寬。**
理由要換成正確的那個：`--first-parent` 正是 §8.3 明文建議的主線讀法
（`git log --oneline --first-parent`），在那個視角下側支 commit 全部隱形，
**Body 的完整 ID 是「這張工單屬於哪一輪」的唯一記載**。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs**：
  - `kit/docs/standards/git_workflow.md` §7.3（`:293-302`）
  - 本張 §1.2 的沙盒輸出（可重跑，指令已完整列出）
  - `docs/features/process_evolution/reviews/PEV-DEV-AGENT-032.md` §5.2（矛盾的 C／D 段）
- **Outputs**：
  - `kit/docs/standards/git_workflow.md` §7.3 的對照表與推論段改寫
  - `docs/standards/git_workflow.md`（根目錄安裝實例，經 `./install.sh . --upgrade` 同步）
  - `docs/features/process_evolution/reviews/PEV-DEV-AGENT-032-FIX-001.md`

### 2.1 對照表要改成三列

| 查法 | 結果 |
|---|---|
| `git log --grep=<TaskID>` | ✅ 找得到 merge commit **與工單自己那顆 commit** |
| `git log --oneline \| grep <TaskID>` | ✅ 找得到工單自己那顆——`--no-ff` 保留了它 |
| `git log --oneline --first-parent \| grep <TaskID>` | ❌ 找不到——側支隱形，這才是 Body 完整 ID 要救的視角 |

### 2.2 ⚠️ 不得順手放寬規則

改的是**理由**不是**規則**。§7.3 的兩條規定（第一行縮寫、Body 逐張列完整 ID）
維持不變。實作時若發現「那既然查得到，Body 好像不必列了」——
那正是本張要防的誤讀，§1.4 的理由段就是為此而寫。

### 2.3 連動點

| 檔案 | 要改什麼 |
|---|---|
| `kit/docs/standards/git_workflow.md` §7.3 | 對照表三列、`:300-302` 的推論段 |
| `grep -c '\[平台相關\]'` | 改完仍須為 **9**（§9 換平台清單的對照數，§7.3 不帶此標記） |
| `tests/test_kit_integrity.py` 的 `已廢除的流程規則` | **不加列**——見 §5 |
| 根目錄安裝實例 | `./install.sh . --upgrade`，待合併須為 0 |

## 3. 驗收標準 (Acceptance Criteria)

- [ ] AC-01：§7.3 對照表改為 §2.1 的三列，`--first-parent` 那列明列出來。
- [ ] AC-02：`:300-302` 的推論段改寫——刪掉「查無此工單」與「`--grep` 一併斷掉」
      兩個與實測不符的敘述，換成 §1.4 的正確理由（`--first-parent` 是 §8.3 的主線讀法）。
- [ ] AC-03：§7.3 的**兩條規定維持不變**（第一行縮寫、Body 逐張列完整 ID），
      diff 裡不得出現放寬。
- [ ] AC-04：**沙盒實測重跑一次並把輸出留進審查紀錄**——三種查法各自的結果，
      外加「Body 不列完整 ID」的對照組。只引用本張 §1.2 不算通過。
- [ ] AC-05：`PEV-DEV-AGENT-032.md` 審查紀錄 §5.2 的 C／D 矛盾要處理。
      **不得改寫該檔的既有內容**（`team_protocol.md` §1.11 已結案工單是歷史紀錄），
      處置方式（例如在本張的審查紀錄裡記明）由執行時裁定並寫出理由。
- [ ] AC-06：`grep -c '\[平台相關\]' kit/docs/standards/git_workflow.md` 仍為 9。
- [ ] AC-07：`./install.sh . --upgrade` 已跑，待合併 0；`uv run pytest` 全綠；
      `python3 .agent/scripts/precheck.py` 七項全綠。
- [ ] AC-08：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**:
  - 無。缺陷已於 2026-08-22 在隔離沙盒實測確認，使用者當日裁定開本張 FIX 工單。
- **✍️ User 補充回覆 (User Input)**:
  -

## 5. 範圍外 (Out of Scope)

- **不改 `PEV-DEV-AGENT-032` 工單與其審查紀錄的既有內容**——§1.11 已結案工單不改。
- **不加進 `tests/test_kit_integrity.py` 的「已廢除的流程規則」表**——
  該表收容的是**被推翻的流程規範**，本張推翻的是一段**事實敘述**，
  規則本身（Body 列完整 ID）原封不動。誤收會讓那張表擋掉正確的說法。
- **不改 §7.1／§7.2**——形狀 E 與主線讀法都經實測，本張只動 §7.3。
- **不重寫歷史、不 push**。
