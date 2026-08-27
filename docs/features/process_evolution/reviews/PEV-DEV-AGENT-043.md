# [Review: PEV-DEV-AGENT-043] 落地並行開發標準與架構決策

## 2026-08-27 ❌ CHANGES REQUESTED

**Review Target：** `PEV-DEV-AGENT-043`
**Base：** `5708adbe8e547bad171d8ced639a4351322f89c1`
**Head：** `c113b82312d1375f47c1037477829895a819b616`
**Fresh-context reviewer：** `gpt-5.6-terra`／`xhigh`；五行 fidelity probe 原樣通過。

## 1. AC 核對

| AC | 結果 | 證據／理由 |
|---|---|---|
| AC-01 | ✅ | `parallel_development.md` §2～§7 覆蓋三份 DN 裁定；未把供應商當角色或流程前提 |
| AC-02 | ✅ | `parallel_development.md:121-161`、`git_workflow.md:83-180` 定義一／兩層拓撲與事件制同步 |
| AC-03 | ✅ | `parallel_development.md:22-51` 定義五欄、Round Manifest 與來源／衍生邊界 |
| AC-04 | ✅ | ADR-001～003 均含 Context、Decision、Rejected alternatives、Consequences |
| AC-05 | ❌ | 活躍 skills 仍保留「APPROVED 後才做結案 commit」，新增 guard 未咬住 |
| AC-06 | ❌ | 固定 target 的 `git diff --check` 回報 6 處行尾空白 |

## 2. Raw findings

### F-01 — P1／驗收阻擋

- **Claim：** 三則 ADR 共 6 處 trailing whitespace，違反 AC-06。
- **File／line：** `ADR-001_task_dag_and_ownership.md:3-4`、
  `ADR-002_round_branch_topology.md:3-4`、`ADR-003_fresh_context_review_target.md:3-4`。
- **Reproducible evidence：**

  ```bash
  git diff --check 5708adbe8e547bad171d8ced639a4351322f89c1..c113b82312d1375f47c1037477829895a819b616
  ```

  固定 diff 回報上述 6 處 `trailing whitespace.`。
- **Recommended verdict：** CHANGES REQUESTED；移除空白並重跑 AC-06。

### F-02 — P1／流程死循環與回歸防線失效

- **Claim：** 第 1 層已要求結案資料納入正式 Review Target，但五份活躍 skill 與
  `code-reviewer` eval 仍要求 APPROVED 後才寫結案 commit，會使 pinned head 與核可失效。
- **File／line：** 第一輪 target 的 `code-reviewer/SKILL.md:78-83,121-132`、
  `frontend-developer/SKILL.md:66`、`backend-developer/SKILL.md:37`、
  `devops-engineer/SKILL.md:45`、`qa-automation-engineer/SKILL.md:261`、
  `code-reviewer/evals/evals.json:17`。
- **Reproducible evidence：**

  ```bash
  rg -n 'APPROVED 後才做結案 commit|APPROVED 後的收尾提醒|由 Developer 做結案 commit' kit/.agent/skills
  uv run pytest tests/test_kit_integrity.py -k '死連結 or 已廢除'
  ```

  前者命中活躍指引，後者仍為 `3 passed`，證明 guard 漏抓。
- **Recommended verdict：** CHANGES REQUESTED；更新相關 skills／eval 與精確舊句型 guard。

## 3. 客觀驗證

| 指令／檢查 | 第一輪結果 |
|---|---|
| `git merge-base --is-ancestor <base> <head>` | exit 0 |
| `git diff --check <base>..<head>` | 失敗：6 處 trailing whitespace |
| 固定 head archive 執行 `uv run pytest -p no:cacheprovider` | 200 passed |
| 固定 head 執行 `.agent/scripts/precheck.py` | 8/8 |
| `pytest tests/test_kit_integrity.py -k '死連結 or 已廢除'` | 3 passed，未捕捉 F-02 |
| `[平台相關]` 標記數 | 9 |

## 4. 修正紀錄（Developer）

- F-01：移除 ADR-001～003 的 6 處行尾空白。
- F-02：使用者同意擴大 043 Write Scope；更新 backend／frontend／devops／QA／code-reviewer／
  scrum-master skills、code-reviewer eval、team protocol 與精確回歸 guard。
- 修正後證據待第二輪 fresh-context review 固定新 head 後獨立重跑。

## 5. 僅人工判讀

- 三份 DN 到第 1 層標準／ADR 的語意映射。
- GitHub／GitLab branch protection 未實際設定；本工單明列不修改託管平台。
- Task → round → main 的真實 merge 與安全回收屬後續輪次證據。
