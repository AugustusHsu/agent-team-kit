# [Task ID: PEV-DEV-AGENT-021] commit 規範送不到 Agent 手上：CLAUDE.md 只指路，沒帶格式

**🔗 依附母任務 (Parent Task ID):** —
**🏷️ 任務類型 (Task Type):** docs_generation
**👤 負責人 (Assignee):** devops-engineer
**🚥 任務狀態 (Status):** Done
**📅 建立時間 (Created):** 2026-08-18T05:26+08:00
**✅ 完成時間 (Closed):** 2026-08-18T06:05+08:00
**🔀 審查載體編號 (PR/MR):** —

## 1. 任務描述 (Description)

`kit/CLAUDE.md` 模板自己診斷得很準：

> **這是不寫就等於沒有的一條。** `.agent/workflows/commit-message.md` 只有在被明確呼叫
> （`/commit-message`）時才載入；Agent 順手 commit 的路徑完全不經過它。

診斷對，藥開錯。模板給的三行範例最後一句是「格式見 `.agent/workflows/commit-message.md`」——
**它把「規則」換成了「規則的地址」**，而問題正是那個地址不會被走到。
指路成功、規則沒送達。

實證就在本 repo：`CLAUDE.md` 忠實照抄了模板那段，結果整批歷史 commit 的 Body
寫成散文，而 `commit-message.md`（`:10`／`:78`）要求的是 `- **標題**：說明` 條列式。
**沒有任何一次 commit 讀到那條規則**，直到 2026-08-18 人工發現才逐一改寫。

修法不是把 `commit-message.md` 整份搬進 CLAUDE.md（那違反模板自己的成本判準），
而是：**範例本身就要帶上「不寫就會做錯」的那幾條最小規則**，其餘才指路。
判準用模板既有的那條——「不寫這條，Claude 會不會做錯事？」——Body 格式的答案是「會」。

## 2. 規格：輸入與輸出 (Inputs & Outputs)

- **Inputs (輸入/依賴項目)**：
  - `kit/CLAUDE.md`「Commit 規則這裡必須寫」節（診斷與現行範例）
  - `kit/.agent/workflows/commit-message.md`（正版格式，判斷哪幾條屬於「不寫就會錯」）
  - 證據：`reviews/PEV-DEV-AGENT-019.md`、本 repo `git log` 的 Body 形式
- **Outputs (輸出/預期變更)**：
  - `kit/CLAUDE.md`：範例改寫，帶上 Body 條列式格式
  - `CLAUDE.md`（本 repo）：同步。⚠️ 它是 `is_seed_file()` 種子檔，
    升級**不會**覆蓋，必須手改
  - `tests/`：一條測試，鎖住「模板範例必須帶 Body 格式」

## 3. 驗收標準 (Acceptance Criteria)

- [x] AC-01：`kit/CLAUDE.md` 的 Commit 範例區塊**內含 Body 條列式格式**
      （`- **標題**：說明`），不是只寫「格式見 …」。
- [x] AC-02：範例仍維持模板自訂的長度紀律——**五行以內**（原訂三行，
      因新增格式而放寬，並在模板內寫明放寬的理由）。
- [x] AC-03：模板要說明**取捨判準**：哪些規則必須內嵌（不寫就會做錯的：Body 格式、
      禁止 AI 署名 trailer、閘門範圍），哪些指路即可（gitmoji 對照表、範疇命名、
      互動模式操作細節）。
- [x] AC-04：本 repo 的 `CLAUDE.md` 同步帶上 Body 格式；改動說明種子檔不受升級覆蓋。
- [x] AC-05：新增測試，斷言 `kit/CLAUDE.md` 的 Commit 範例區塊裡出現 Body 條列式格式；
      **負向對照**：把該行從模板拿掉要能讓測試轉紅。
- [x] AC-06：`uv run pytest` 全綠、`python3 .agent/scripts/precheck.py` 全綠。

## 4. 人為補充與確認 (Human-in-the-loop)

- **❓ 需要確認的事項 (Agent 提問)**：
  1. 範例放寬到五行可以接受嗎？若堅持三行，就得從現有三行裡砍掉一項才能塞進 Body 格式。
- **✍️ User 補充回覆 (User Input)**：**（由 Agent 於 2026-08-18 代填，使用者可否決）**
  1. **可以放寬到五行。** 三行的紀律要保護的是 context 成本，而 Body 格式那一行約
     40 個字——把它砍掉省下的 token 遠少於「每次 commit 都寫錯格式」的代價。
     模板自己的判準（「不寫這條，Claude 會不會做錯事？」）對這一行的答案是「會」，
     所以它屬於必須內嵌那一類，紀律該讓路的是行數上限而不是這一行。
     放寬的理由已寫進模板本文，不是只留在工單裡。

## 5. 範圍外 (Out of Scope)

- **不搬** `commit-message.md` 的完整內容進 CLAUDE.md——那正是模板成本判準要避免的事。
- **不改**已推送的歷史 commit 訊息（需要 force-push）。
