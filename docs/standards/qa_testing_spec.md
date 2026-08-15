# 軟體品質保證與測試規範 (QA & Testing Specification)

> **版本**：v1.1.0
> **更新日期**：2026-07-20（系統審查對齊：修正 §2 前後端測試目錄結構與實際路徑一致）
> **適用對象**：QA Automation Engineer, Backend Developer, Frontend Developer, Product Manager

本文件定義了專案的軟體測試策略、分層架構、目錄結構與測試案例的撰寫規範，以確保系統具備高可維護性並符合業務需求。所有模組的測試實作皆應遵循本標準。

---

## 1. 測試分層策略 (Test Pyramid)

我們採用經典的測試金字塔策略，將測試分為三個核心層級，每一層級有其特定的目標與邊界：

### 1.1 Unit Test（單元測試）
- **目標**：驗證單一函式、方法或 Class 的純內部邏輯，確保核心演算法與資料轉換正確無誤。
- **特徵**：
  - **不**依賴真實資料庫、網路請求或外部服務。
  - 執行速度極快（毫秒級），作為 CI 流程中最基礎的防線。
- **適用情境**：
  - 密碼強度驗證、Email 格式檢查。
  - JWT Token 加解密純邏輯 (使用 mock 的 key)。
  - 複雜業務規則的推導邏輯（例如權限層級換算）。

### 1.2 Integration Test（整合測試）
- **目標**：驗證多個元件或子系統之間的互動是否正確，重點在於 API 端點的輸入與輸出驗證。
- **特徵**：
  - **需要**啟動測試用資料庫 (如 Testcontainers 或本機獨立 DB) 或 Redis 快取。
  - 若有不可控的外部第三方服務（如 Google OAuth），則進行 Mock。
- **適用情境**：
  - API 端點的 Request → Middleware → Service → DB → Response 完整流程。
  - 資料庫 Transaction 的原子性驗證與並行防鎖死測試。
  - RBAC 或 Membership-Based 權限攔截防護（HTTP 403 / 401 驗證）。

### 1.3 E2E Test（端對端測試）
- **目標**：從終端使用者的視角，模擬真實瀏覽器操作，驗證前端 UI 與後端 API 的完整鏈路。
- **特徵**：
  - 啟動完整的 Frontend 與 Backend 服務。
  - 執行成本與維護成本最高，因此僅針對「關鍵使用者旅程 (Critical User Journeys)」進行覆蓋。
- **適用情境**：
  - 使用者從登入、瀏覽儀表板、建立任務到登出的完整生命週期。
  - 跨頁面的路由防護 (Route Guards) 與頁面重新導向邏輯。

---

## 2. 測試專案與目錄結構

為避免測試檔案散落，前後端測試目錄應嚴格區分層級與模組。

### 2.1 後端測試目錄 (`backend/tests/`)

```text
backend/tests/
├── conftest.py               # 全域共用 Fixtures (Database, Redis, Test Client, Helpers)
├── unit/                     # 單元測試目錄 (純邏輯，不依賴 DB/Redis)
│   └── test_{模組名}.py
├── integration/              # 整合測試目錄 (需 DB/Redis，涵蓋 API 端點與跨模組流程)
│   └── test_{功能流程}.py
└── api/                      # 針對特定子系統（如 DMS 分支/合併）的 API 路由測試
    └── test_{子功能}.py
```

### 2.2 前端測試目錄

```text
frontend/
├── cypress/
│   ├── e2e/                  # 端對端測試 (Cypress)
│   │   └── {功能名}.cy.ts
│   ├── fixtures/              # 測試資料
│   └── support/                # 共用指令 (commands.ts)
└── src/
    └── **/__tests__/           # 前端單元測試 (Jest + React Testing Library)
        └── {元件或工具名}.test.tsx
```

> 註：前端單元測試與 E2E 測試分別使用 Jest（`npm run test`）與 Cypress（`make test-e2e`），並非集中於獨立的 `frontend/tests/` 目錄。

---

## 3. 測試計畫與文件產出 (Test Planning)

在實作任何測試程式碼前，必須先透過 `qa-test-planner` 產出對應模組的 `test_plan.md`。

### 3.1 測試追溯性矩陣 (Traceability)
Test Plan 必須對應至 PRD 中的「業務規則 (Business Rules, BR-*)」或「驗收標準 (Acceptance Criteria, AC-*)」。
每個 Test Case 必須有一個唯一識別碼（如 `T-AUTH-001`），且在 Test Plan 尾端建立追溯性矩陣以供核對。

### 3.2 邊界與極端情境設計 (Edge Cases)
撰寫 Happy Path 測試後，必須針對以下面向進行 Edge Case 挖掘：
1. **權限越權 (Privilege Escalation)**：低權限使用者嘗試呼叫高權限 API。
2. **狀態轉換防護 (State Transition)**：嘗試對已批准的申請再次批准，或對已完成的任務進行狀態退回。
3. **並發操作 (Concurrency)**：驗證 Race Condition 防護（例如唯一資源的搶佔）。
4. **防呆與自我保護 (Self-Operation)**：例如 Super Admin 嘗試停用自己的帳號。

---

## 4. 程式碼撰寫規範

### 4.1 命名約定 (Naming Conventions)
- **檔案命名**：統一以 `test_` 開頭。
- **Class 命名**：以 `Test` 開頭的 CamelCase，通常用於將相同前置條件的測試分組（例如 `TestWorkspaceCreation`）。
- **函式命名**：應具備高度可讀性，採用 `test_{測試目標}_{預期結果}` 的格式。
  - ✅ `test_create_project_with_invalid_manager_returns_400`
  - ❌ `test_create_project_fail`

### 4.2 AAA 結構 (Arrange, Act, Assert)
每一個測試函式都應該清晰地分為三個區塊（建議用空行隔開）：
1. **Arrange (準備)**：初始化測試資料、設定 Mock 與 Fixtures。
2. **Act (執行)**：呼叫 API 或執行目標函式。
3. **Assert (驗證)**：斷言結果是否符合預期（HTTP Status Code、DB 狀態變更、JSON 欄位）。

### 4.3 避免巨型測試 (Avoid Giant Tests)
- **單一職責原則**：一個測試函式（`def test_...`）應該只測試一個特定的情境或業務邏輯。
- 若測試情境存在前後依賴（例如 A 必須先成功才能測 B），**禁止將它們寫在同一個長達百行的函式中**。應使用適當的 Fixtures 準備資料，讓 A 和 B 成為可獨立執行的測試，確保隔離性。

### 4.4 Fixtures 與共用邏輯
- 重複的資料庫建置邏輯（如建立測試帳號、登入並取得 Cookie）應統一移至 `conftest.py` 或特定的 `helpers.py` 模組中。
- 測試完成後必須清理資料或狀態，優先依賴框架提供的 Database Transaction Rollback 機制，避免手動撰寫 `DELETE` SQL 指令。

### 4.5 測試資料庫初始化與清理 (Database Initialization & Teardown)
為了確保測試的隔離性與穩定性，禁止測試案例之間產生「隱性耦合 (Implicit Coupling)」或依賴先前的測試結果：
1. **DB Transaction 隔離**：每一個 Integration Test 都應該運行在一個獨立的資料庫 Transaction 中。透過 Pytest Fixture（如 `db_session`），在測試開始時開啟 Transaction，並在測試結束後（`yield` 之後）執行 `rollback()`。這樣可以確保資料庫隨時回到初始乾淨的狀態。
2. **禁止手動清理**：嚴禁在測試函式中使用 `DELETE FROM ...` 或 `.delete()` 的方式手動清空資料表（例如先前的巨型測試寫法），這不僅容易遺漏且會導致平行測試時的 Race Condition。
3. **資料庫自舉 (Bootstrapping)**：若特定測試需要基礎資料（如預設的 Workspace 或 Super Admin），應使用專用的工廠函式 (Factory Functions) 或 Fixtures（如 `_setup_admin(client)`）即時在該次 Transaction 內產生，而非依賴整個測試套件共用的全域狀態。
4. **Redis 快取清理**：由於 Redis 不支援 Transaction Rollback，對於影響全域狀態的 Redis 操作，應依賴 `conftest.py` 中的 `autouse=True` Fixture 在每個測試前後執行 `flushdb`，以保證狀態完全隔離。
