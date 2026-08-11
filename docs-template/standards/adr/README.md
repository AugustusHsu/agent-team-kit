# 🏛️ 架構決策紀錄 (ADR) 索引

> 本頁彙整所有系統層級的架構決策紀錄 (Architecture Decision Records)。ADR 本文分散寫在各模組 `hld.md`（或跨模組的 `standards/devenv_spec.md`）內，此處只做**集中索引**，不重複貼文字內容。
> **2026-08-10 校正**：本索引先前的 ADR-01~06、ADR-07~11 兩張表格內容（標題如「後端框架選型」「全容器化開發環境」等）經查證與現行 [UMS HLD](../../features/user_management_system/hld.md)、[devenv_spec.md](../devenv_spec.md) 實際內容完全不符——比對 git 歷史，該索引自 2026-05-06 建立當下即未與任何檔案的真實內容同步過。已重寫為以下反映現況的完整索引；依 ADR 不可回頭編輯的慣例，**這裡的更動僅限索引本身（誰在哪裡、標題是什麼），不涉及任何一條 ADR 決策本文的內容變更**。

## ⚠️ 已知編號重複（不追溯重編，僅明文記錄）

專案並非自始就有「全域連續編號」的共識，以下重複是實際發生過的編號衝突，兩邊決策皆真實有效、皆保留原編號，僅在此標註以避免誤用：

| 重複編號 | A | B |
|---|---|---|
| ADR-07~11 | [devenv_spec.md](../devenv_spec.md)（2026-04-09 建立：uv/全容器化/Docker Image/Lint-Format/DinD） | [UMS HLD](../../features/user_management_system/hld.md)（2026-04-16～稍後陸續建立：大頭貼策略/前端模板/Admin路由/多租戶隔離/Capabilities） |
| ADR-13 | [DMS HLD](../../features/dataset_management_system/hld.md)（2026-07-15：DatasetBranch 分支層級） | [UMS HLD](../../features/user_management_system/hld.md)（2026-07-21：Dashboard 統計 API 群集分離） |

自 `labeling_viewing_system`（2026-07-22，ADR-14 起）之後，新增 ADR 已改為查證全專案最大編號 +1（見 [documentation_conventions.md](../documentation_conventions.md) §3.2），未再發生新的重複。**目前全域最大編號為 ADR-21**（`devenv_spec.md`）。

## ADR 總覽（依模組分組，模組內依編號排序）

### User Management System — [hld.md](../../features/user_management_system/hld.md)

| ADR | 標題 | 位置 |
|---|---|---|
| ADR-01 | Session 驗證機制採用 Hybrid JWT | HLD 內文 |
| ADR-02 | 避免 SPOF (單點故障) 架構設計 | HLD 內文 |
| ADR-03 | 防止初始化競態條件 (Race Condition) | HLD 內文 |
| ADR-04 | 核心資料庫選型 (Identity Database) | HLD 內文 |
| ADR-05 | 系統稽核與可觀測性 (Observability & Audit Logging) | HLD 內文 |
| ADR-06 | 應用層技術棧選型 (Frontend & Backend Framework) | HLD 內文 |
| ADR-07 | 大頭貼整合策略 (Hybrid Avatar Strategy) | HLD 內文（與 devenv ADR-07 編號重複，見上表） |
| ADR-08 | 前端核心模板遷移 (Frontend Template Migration) | [ADR-08_frontend_template_migration.md](ADR-08_frontend_template_migration.md) |
| ADR-09 | Admin Settings 路由分離策略 | HLD 內文（與 devenv ADR-09 編號重複） |
| ADR-10 | Membership-Based Isolation 架構 (多租戶隔離) | HLD 內文（與 devenv ADR-10 編號重複） |
| ADR-11 | 導入 Capabilities 能力陣列取代寫死角色 | HLD 內文（與 devenv ADR-11 編號重複） |
| ADR-12 | MinIO 圖片儲存與代理架構 | HLD 內文 |
| ADR-13 | Dashboard 統計 API 群集分離策略 | HLD 內文（與 DMS ADR-13 編號重複，見上表） |

### Dataset Management System — [hld.md](../../features/dataset_management_system/hld.md)

| ADR | 標題 | 位置 |
|---|---|---|
| ADR-13 | 引進分支 (DatasetBranch) 層級以解耦視圖與 Commit 歷史 | HLD 內文（與 UMS ADR-13 編號重複，見上表） |

### Labeling Viewing System — [hld.md](../../features/labeling_viewing_system/hld.md)

| ADR | 標題 | 位置 |
|---|---|---|
| ADR-14 | Shell + Labeler 策略模式（動態載入） | HLD 內文 |
| ADR-15 | 獨立 URL Path 路由 + 全畫面展間（取代輕量 Dialog） | HLD 內文 |
| ADR-16 | 以「DMS `dataset_type` 去 unlabeled 化」為硬前置依賴 | HLD 內文 |
| ADR-17 | 圖片以「後端代理串流」供應，不採 presigned URL | HLD 內文 |
| ADR-18 | 語義型別收歸 `dataset_type`，`data_format` 降為來源匯入格式 | HLD 內文 |

### 跨模組（開發環境）— [devenv_spec.md](../devenv_spec.md)

| ADR | 標題 | 位置 |
|---|---|---|
| ADR-07 | Python 套件管理工具 — uv (全專案一致) | devenv_spec.md 內文（與 UMS ADR-07 編號重複，見上表） |
| ADR-08 | Docker Compose 開發策略 — 全容器化 | devenv_spec.md 內文（與 UMS ADR-08 編號重複） |
| ADR-09 | Docker Image 基底選型與第三方釘版規範 | devenv_spec.md 內文（與 UMS ADR-09 編號重複） |
| ADR-10 | Linter 與 Formatter 選型與雙軌收斂 — Ruff + Prettier | devenv_spec.md 內文（與 UMS ADR-10 編號重複） |
| ADR-11 | Docker-in-Docker (DinD) 策略 | devenv_spec.md 內文（與 UMS ADR-11 編號重複） |
| ADR-19 | 自建映像檔的跨節點配送機制 — 本地私有 Registry | devenv_spec.md 內文 |
| ADR-20 | 前端品質門檻與 Cypress 型別隔離機制 | devenv_spec.md 內文 |
| ADR-21 | dev 與 e2e 環境之 Dockerfile/Base Image 自動重建機制與 bind mount 邊界澄清 | devenv_spec.md 內文 |

---

新增 ADR 時的編號與登記規則，見 [documentation_conventions.md](../documentation_conventions.md) §3。
