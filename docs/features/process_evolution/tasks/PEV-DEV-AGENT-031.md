# [Task ID: PEV-DEV-AGENT-031] precheck 新增 Assignee 合法性檢查

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** queue_agent
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-19T00:40+08:00
**✅ 完成時間 (Closed):** 2026-08-21T21:32+08:00
**🔀 審查載體編號 (PR/MR):** —（見 `../reviews/PEV-DEV-AGENT-031.md`，git_workflow.md §8.3 降級）

## 1. 任務描述 (Description)

`PEV-DEV-AGENT-025` 盤點 13 個角色的使用紀錄時，順帶發現一個工單沒預期到的缺陷：

```
docs/features/process_evolution/tasks/PEV-DEV-AGENT-012.md:5:**👤 負責人 (Assignee):** backend-engineer
docs/features/process_evolution/tasks/PEV-DEV-AGENT-013.md:5:**👤 負責人 (Assignee):** backend-engineer
```

`backend-engineer` **不對應任何 skill**（正確名稱是 `backend-developer`）。
兩張工單都已 `Done`，錯誤存活至今從未被察覺。

**為什麼值得一張工單**：這是**最容易自動檢查、也最不容易人工發現**的一類缺陷。
Assignee 打錯不會有任何執行期錯誤——BACKLOG 照樣生成、precheck 六項照樣全綠，
只是那張工單永遠不會被正確的角色接手。而 `025` 之所以會發現，
純粹是因為它剛好在做全角色盤點；沒有那次盤點，這筆錯誤會一直留著。

**與 `PEV-DEV-AGENT-026` 的分工**：026 也在做一致性檢查，但**這一項不能併進去**。
026 §2 已裁定落點分界——

| 落點 | 檢查對象 |
|---|---|
| `precheck.py` | **使用者自己寫的**工單與文件 |
| `tests/test_kit_integrity.py` | **kit 出貨內容**有沒有被改壞 |

Assignee 是使用者填的工單欄位，屬前者；026 的 AC-06 更明文「不落在 `precheck.py`」。
兩張各自落在自己的層，互不依賴，**可並行**。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

**輸入：** `docs/features/*/tasks/*.md` 的 Assignee 欄位、`.agent/skills/` 的目錄清單。

**輸出：** `precheck.py` 的第 7 項檢查。

### 2.1 判定基準

Assignee 必須是下列之一，否則報錯：

| 合法值 | 說明 |
|---|---|
| `.agent/skills/` 底下實際存在的目錄名 | 例如 `backend-developer`。**讀目錄而非寫死清單**——使用者專案可以自己加 skill |
| `manual_user` | 工單範本明列的「使用者親自處理」值 |
| `—` | 未指派 |

`docs/features/_TEMPLATE/` 不掃（範本的 Assignee 是佔位說明文字，不是真值）。

### 2.2 ⚠️ 必須先解掉的設計衝突：檢查範圍只涵蓋未結案工單

012／013 已經是 `Done`，而 `team_protocol.md` §1.11 規定
**已結案工單是歷史紀錄，不改它、也不引用它**。
檢查若涵蓋全部工單，合入當天 precheck 就會紅在兩張不准修的工單上——
唯一的解法會是去違反 §1.11。

**裁定：只檢查未結案工單**（Status 不是 `Done` 也不是 `Canceled`）。

這與 `026` 的落點理由同型：**檢查要對得起它能改變的東西。**
026 說「使用者專案不編輯 `.agent/`，帶著一份永遠綠的檢查沒有意義，那是假閘門」；
這裡是反面同一件事——**對一份規定不准改的歷史紀錄上鎖，只會製造一個解不掉的紅燈**。

> 📌 沿用既有寫法：`precheck.py` 的 `check_ac_matches_status` 已有
> `AC_EXEMPT_STATUSES = {"Done", "Canceled"}`，本項比照，不另立一套。

### 2.3 連動點（漏一個就會不一致）

| 檔案 | 要改什麼 |
|---|---|
| `kit/.agent/scripts/precheck.py` | 新增 `check_assignee_valid(root)`，並註冊進檔尾的 `CHECKS`（現為 6 筆） |
| 同檔開頭 docstring | 「六項檢查」→ 七項，並補上第 7 條的說明 |
| `kit/docs/standards/git_workflow.md` §8.1 能力對照表 | 「自動檢查」那列的檢查清單目前列六項，要加第七項 |
| `tests/test_precheck.py` | 現有 17 個測試，本項至少補正向一個、負向一個 |

⚠️ **改完 `kit/` 要跑 `./install.sh . --upgrade`**，否則根目錄的安裝實例不會更新，
本 repo 自己跑 `precheck.py` 仍是舊的六項。

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`check_assignee_valid` 實作於 `kit/.agent/scripts/precheck.py` 並註冊進 `CHECKS`。
- [x] AC-02：合法值讀自 `.agent/skills/` 的實際目錄，**不得寫死角色清單**——
      寫死的話使用者專案新增自訂 skill 就會誤報。
- [x] AC-03：只檢查未結案工單，沿用 `AC_EXEMPT_STATUSES`（§2.2 的裁定）。
      **不修改 012／013**（§1.11 已結案工單不改）。
- [x] AC-04：**負向對照實跑，輸出留進審查紀錄**——把某張未結案工單的 Assignee
      改成不存在的角色 → 該項轉紅且訊息指名**哪張工單、哪一行、填了什麼、合法值有哪些**；
      還原 → 轉綠。只寫「不合法」不算通過。
- [x] AC-05：docstring、`--list` 輸出、`git_workflow.md` §8.1 三處的「六項」全部同步為七項
      （§2.3 的連動表）。
- [x] AC-06：`tests/test_precheck.py` 新增正向與負向測試各至少一個；
      `uv run pytest` 全綠，**通過數應為 135 + 新增數**，並在審查紀錄寫出新的數字。
- [x] AC-07：`./install.sh . --upgrade` 已跑，根目錄安裝實例同步。
- [x] AC-08：`python3 .agent/scripts/precheck.py` **七項**全綠。
- [x] AC-09：`BACKLOG.md` 重新生成，含本工單。

## 4. 人為補充與確認 (Human-in-the-loop)

- 缺陷由 `PEV-DEV-AGENT-025` 的盤點發現，處置（開新工單而非併進 026）
  由使用者於 2026-08-19 裁定。

## 5. 範圍外 (Out of Scope)

- **不修 `PEV-DEV-AGENT-012／013`**——§1.11 已結案工單是歷史紀錄，不改它。
- **不檢查 Assignee 是否「適合」該工單內容**——那是判斷不是事實，不該進閘門。
- **不動 `026` 的兩項 skill 檢查**——落點不同層，各做各的。
