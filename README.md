# agent-team-kit

以「**AI 虛擬團隊 + 工單驅動開發**」為核心的專案流程套件，可安裝到任何新專案。

一句話：把 13 個角色（BA / PM / 架構師 / Tech Lead / 前後端 / DevOps / QA / Code Reviewer …）的職責、工單生命週期、文檔規範與 BACKLOG 掃描腳本打包成一套可複用資產，讓 AI 協作有固定的接力規則，而不是每次重新交代。

> 本套件抽取自實際運作一年的單人 + AI 團隊 monorepo，語言為**繁體中文**。

## 這套件解決什麼問題

| 痛點 | 本套件的解法 |
|---|---|
| AI 每次的產出格式、深度都不一樣 | 13 個角色 SKILL，各自定義職責、產出物與回報格式 |
| 不知道現在做到哪、哪張單卡住 | 工單即檔案（`docs/features/{模組}/tasks/{ID}.md`），`scan_backlog.py` 自動彙整成 BACKLOG |
| AI 自作主張、跳過確認就開幹 | 工單生命週期 + §1.7 執行前 HITL 閘門 |
| 發現 bug 就無腦開新單，舊單留著錯誤 AC | §1.8 缺陷收容優先序：成因工單未結案一律退回改單 |
| 需求文件散落、沒人知道正版在哪 | `docs/features/{模組}/{brd,prd,hld,lld,api_spec,test_plan}.md` 固定骨架 |

## 內容物

`kit/` 底下的結構**就是**安裝後在你專案裡的樣子——安裝＝原封不動複製，不做任何改名。

```
kit/
├── .agent/
│   ├── resources/
│   │   ├── team_protocol.md    # ⭐ 核心：工單生命週期、角色交接、命名約定
│   │   ├── task_template.md    # 工單模板
│   │   └── backlog_template.md
│   ├── skills/                 # 13 個角色 SKILL.md（各含 evals/）
│   │   ├── business-analyst/ product-manager/                      # 需求
│   │   ├── system-architect/ tech-lead/ uiux/ security-engineer/   # 設計
│   │   ├── scrum-master/                                           # 排程開單
│   │   ├── frontend-developer/ backend-developer/ devops-engineer/ # 開發
│   │   └── qa-test-planner/ qa-automation-engineer/ code-reviewer/ # 品質
│   ├── workflows/              # git-commit / product-analysis / validate-wireframes
│   └── scripts/
│       ├── scan_backlog.py     # 掃工單 → 產生 BACKLOG.md（狀態儀表板）
│       ├── migrate_dates.py    # 工單日期格式遷移
│       └── check_versions.py   # 第三方版本檢查
├── docs/
│   ├── DOCS_MAP.md             # 文件導覽入口
│   ├── development/            # BACKLOG.md、PLAN_FROM_HANDOFF.md
│   ├── standards/              # 文檔慣例、QA 規範、資安查核、ADR
│   └── features/_TEMPLATE/     # 單一功能模組的文件骨架
└── CLAUDE.md                   # 專案接手指南模板

install.sh                      # 安裝到目標專案
tests/                          # 本套件自身的 smoke test（不會被安裝）
```

## 安裝到新專案

```bash
git clone git@github.com:AugustusHsu/agent-team-kit.git
./agent-team-kit/install.sh /path/to/your-project
```

既有檔案預設不覆蓋，`--force` 可強制覆蓋。

### 安裝後必做

1. 編輯 `.agent/resources/team_protocol.md` §3.1 的**模組前綴對照表**，換成你的模組（前綴取 3 個大寫字母，全專案唯一）。
2. 依 `docs/features/_TEMPLATE/` 複製出第一個功能模組目錄，並到 `docs/DOCS_MAP.md` 登記。
3. 依安裝到專案根目錄的 `CLAUDE.md` 模板，寫成你專案的入口摘要。
4. 跑一次 `python .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md` 確認腳本正常。

## 日常運作

```
scrum-master 開單 → (HITL 閘門：問使用者未決事項)
    → developer 領單開發 → 三段式交付回報
    → code-reviewer 四維審查 → APPROVED / CHANGES REQUESTED
    → 回寫工單 + 重跑 scan_backlog.py
```

狀態流：`Pending → Ready → In Progress → In Review → Done`（另有 `Canceled`）。
完整規則見 `kit/.agent/resources/team_protocol.md`（安裝後為 `.agent/resources/team_protocol.md`）。

## 相容性

SKILL 檔為 Claude Code 的 Skill 格式（frontmatter `name` / `description`）。放在 `.agent/skills/` 時可由使用者指名觸發；若要用 `/{name}` 斜線指令直接叫，請改放 `.claude/skills/`。內容本身是純 Markdown 指令，其他 Agent 工具也能沿用。

每個角色附一份 `evals/evals.json`，格式對齊 Anthropic 官方 `skill-creator` 的 eval schema：

```json
{ "skill_name": "...", "evals": [ { "id": 1, "prompt": "...", "expected_output": "...", "files": [], "expectations": ["..."] } ] }
```

`expectations` 是可被評分者逐條判定的敘述句；`files` 一律留空——本套件的 eval 皆為自足式 prompt，不依賴外部輸入檔。你把 `skill-creator` 裝進來後即可直接跑這些 eval，也可以照同一格式往下加。

## 沒有包進來的東西

刻意排除、需要你自己補的專案專屬資產：

- `docs/standards/design_system.md`、`devenv_spec.md`、`third_party_versions.yaml`（綁技術棧）
- 具體的 ADR（只留 `adr/README.md` 慣例）
- Anthropic 官方 `skill-creator` skill——本套件的 evals 對齊它的格式，但不內含它；需要時自行從 [anthropics/skills](https://github.com/anthropics/skills) 取用，避免授權混淆

## 授權

MIT，見 [LICENSE](LICENSE)。
