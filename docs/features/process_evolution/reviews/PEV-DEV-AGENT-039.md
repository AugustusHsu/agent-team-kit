# [Review: PEV-DEV-AGENT-039] route／explain 與失效重路由

## 1. 驗收結果

| AC | 結果 | 證據 |
|---|---|---|
| AC-01 | ✅ | cloud forbid 候選在評分前 `score=null`；硬能力缺漏同樣不進排序 |
| AC-02 | ✅ | 只啟用 codex-cli 仍因缺 visual capability 得到零候選 |
| AC-03 | ✅ | 每個候選輸出 availability、逐項 delta、排除理由與 metadata unknown |
| AC-04 | ✅ | 單次覆寫免到期；round／project 沒 `--override-expires-at` 直接失敗 |
| AC-05 | ✅ | 零候選 CLI exit 3，JSON 仍保留每個 profile 的缺漏原因 |
| AC-06 | ✅ | quota 失效後 handoff 保留 Task ID、branch、HEAD、AC、驗證與 failure type |
| AC-07 | ✅ | implementation 即使開 auto flag 仍要求人；純讀設計工作才允許自動接手 |
| AC-08 | ✅ | 相同輸入 decision 完全相等；覆蓋單／雙供應商、過期 cache、禁止 cloud |
| AC-09 | ✅ | 完整 pytest 180 passed；precheck 7/7；installer 待合併 0 |

## 2. 六階段順序真的不可交換

`route_decision()` 先建立全候選表，再依下列順序處理：

1. enabled 與 hard capabilities；
2. cloud／Connector／data class；
3. fresh Availability；
4. project preference；
5. 可解釋層內分數；
6. 使用者 override。

負向對照只啟用 verified 的 `codex-cloud`，同時把 project cloud policy 設 `forbid`。
結果不是「高分但被註記」，而是：

```text
eligible = false
score = null
excluded_reasons = ["project cloud policy=forbid 不允許 internal"]
```

同理，使用者 override 選缺 `visual_interaction` 的 `codex-cli` 會直接拒絕，不會把最後決定權
誤寫成可以繞過安全與硬能力。

## 3. 單一供應商也必須跑路由

測試只啟用 `codex-cli`，狀態是 fresh verified，再替 `implementation_local` 加上
`visual_interaction`。結果仍是零候選，原因明列缺該能力。這證明「登入成功」與「目前只有它」
都不是全能力通行證。

CLI 零候選輸出 machine-readable JSON 並回 exit 3；呼叫端能自動停止，又保留人可讀原因。

## 4. 分數可解釋，也誠實承認未知

初始分數 100，再加：

- Availability：verified +30、degraded +10、容許的 pure-read unknown -20；
- project preference：依偏好順序 +20 起遞減；
- task profile optional capabilities：每命中一項 +1；
- cost／latency／context：registry 尚無可比較證據，各 0 並標 `metadata_unknown`。

不以「Claude 應該比較貴」或「Codex 應該比較快」這類印象偷排。雙供應商同為 verified 時，
偏好 `codex-cli` 的加分逐項可見；相同 policy／state／registry／時間輸入跑兩次，整份 decision 相等。

## 5. 過期 cache 的唯一例外

同一份過期 `codex-cli` state：

| task profile | 結果 |
|---|---|
| `design_research` | 保留為 unknown 本機唯讀候選並扣分 |
| `implementation_local` | 排除，零候選 |

只要 required capabilities 含 repo write、shell、test、Connector、視覺互動、長時間工作或批次副作用，
unknown 就不能進排序。

## 6. 覆寫與中途失效

`--override-profile` 預設 `single`。使用者可在兩個合格候選間把 Claude 改成 Codex 或反向；
若 scope 是 `round`／`project`，必須同時給時間或明確事件，例如「本輪 merge 完成」。

模擬 `codex-cli` 因 quota 中途失效後，路由排除它並選 fresh verified 的 Claude。handoff 保存：

```text
Task ID / branch / HEAD
completed_ac / pending_ac
validations / failure_type
failed_profile / suggested_profile
```

`implementation_local` 即使帶 `--allow-auto-read-handoff` 仍是
`requires_user_confirmation=true`；只有 `design_research` 這類純讀、無外部副作用工作，且使用者
明示允許時，才是 `auto_handoff_allowed=true`。換 profile 不換工單與 Assignee。

## 7. CLI 與驗證

- routing／health／init 目標測試：**27 passed**；
- 完整 `uv run pytest --basetemp=/dev/shm/agent-team-kit-039-full`：**180 passed**；
- `python3 .agent/scripts/precheck.py`：**7/7 全綠**；
- `./install.sh . --upgrade --dry-run`：新增 0、更新 0、待合併 0；
- `git diff --check`：通過。

CLI 端到端先 init 假 XDG state，再 route：一般實作選到 `codex-cli` 且 exit 0；同時要求
`visual_interaction` 與 `noninteractive` 時無 profile 能同時滿足，exit 3。

## 8. 留給後續工單

- 040 把 route JSON 接入工單 override 與 review 證據，不把本機狀態放進 CI；
- 041 對本 repo 實跑，使用者偏好與真實 GitHub 能力由 migration／doctor 產生；
- 042 驗證 Claude→Codex 與 Codex→Claude 的完整交接。
