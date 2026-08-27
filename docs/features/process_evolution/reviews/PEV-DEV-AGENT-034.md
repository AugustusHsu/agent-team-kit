# [Review: PEV-DEV-AGENT-034] 跨代理執行標準與任務輪廓 registry

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | `kit/docs/standards/agent_runtime.md:7-89` 定義四維度、六階段路由與四種 availability |
| AC-02 | ✅ | `task_profiles.json` 有 schema version、20 個高階能力、4 級資料與 8 個輪廓 |
| AC-03 | ✅ | 標準第 2 節明定新增輪廓只改 registry；新增資料的測試通過 |
| AC-04 | ✅ | 4 個 registry 負向／擴充測試實跑，訊息含 JSON path |
| AC-05 | ✅ | `agent_runtime.md:16` 禁止供應商進 Task Type／Assignee；registry 掃描無供應商名稱 |
| AC-06 | ✅ | `agent_runtime.md:92` 定義 Codex CLI 基線、App／Cloud 額外 profiles |
| AC-07 | ✅ | DOCS_MAP／README 已登記；安裝 dry-run 待合併 0；完整閘門見 §4 |

## 2. 資料契約

registry 不使用寫死 enum，而是把可擴充部分留在 JSON：

- `capabilities` 是高階能力詞彙；
- `data_classes` 的陣列順序就是風險順序；
- `profiles` 只引用前兩者；
- `schema_version` 讓不相容格式明確失敗。

schema 將未知欄位設成不允許，避免 `capabilites` 這類拼字錯誤被靜默接受。
測試再補跨欄位的語意檢查：profile ID 不重複、能力與資料級別必須存在、必備與選配不可重疊。

## 3. 負向對照實跑

執行：

```text
uv run pytest tests/test_agent_runtime_registry.py tests/test_kit_integrity.py
........................................................................ [ 98%]
.                                                                        [100%]
73 passed in 0.10s
```

其中四個關鍵案例：

| 案例 | 預期訊息／判準 |
|---|---|
| profile 多出 `capabilites` | `$.profiles[0].capabilites：未知欄位` |
| 重複 `design_research` | 指出重複 profile ID |
| 引用 `telepathy` | 指出未知 capability |
| 新增 `documentation_only` | 不修改 Python enum 仍通過 |

## 4. 安裝同步

`./install.sh . --upgrade --dry-run` 與正式升級結果一致：新增 registry、schema、標準文件；
更新 DOCS_MAP／standards README；**待合併 0**。根目錄安裝實例不是手改產物。

結案閘門：`uv run pytest` → **147 passed**；`precheck.py` → **7/7**；
`git diff --check` 通過。

## 5. 設計邊界

- 這張只定 task profile，不建立 execution profile manifests；後者是 `035`。
- `reasoning_class` 只用 `fast／balanced／deep`，模型名稱留給 adapter 與使用者本機設定。
- CI 只驗版控契約；登入、訂閱與 Connector 狀態不在本張，也不應使 CI 因人而異。

## 6. 未處理

- `agent_runtime.py`、provider probes、route/explain 與工單欄位由 `037`～`040` 接手。
