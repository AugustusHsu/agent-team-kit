# User Management System — 資安防禦與查核表 (Security Audit)

> **更新日期**：2026-04-08（2026-07-20 系統審查對齊：於各查核項目後標註現況，未標註者本輪未覆核）
> **負責角色**：Security Engineer (資安工程師)

本文件作為 LLD (低階設計) 之必要擴充，負責防禦所有端點與底層基礎設施（AuthN/AuthZ）的惡意攻擊可能性。後續進入開發階段時，全體工程師與 QA 均須依循此清單進行驗收。

---

## 1. 核心安全策略與防禦架構

### 1.1 Token 安全儲存 (打擊 XSS)
為了防禦跨站腳本攻擊 (XSS)，我們已推翻傳統的 JSON 回傳機制，強制規定 **Access Token 與 Refresh Token 必須採用 `HttpOnly` Cookie 儲存**。
前端 Vue/React/SPA 完全不可接觸 Token，僅由作業系統與瀏覽器接管網路傳輸時的自動夾帶。

### 1.2 跨站請求偽造 (打擊 CSRF)
因改用 Cookie 夾帶身分，系統必定會遭受 CSRF 攻擊風險。
- **解決方案**：前端所有更改狀態的請求 (`POST`, `PUT`, `DELETE`)，除了挾帶 Cookie 以外，必須在 Request Header 附加前端自己生成的自定義防護頭 (例如：`X-CSRF-Token: 1`)，或者限制 API Gateway 端的 `SameSite=Strict` 以及強制校驗 `Origin` 或 `Referer`。

### 1.3 密碼雜湊強度 (Cryptography)
為防止資料庫外洩導致帳密被「彩虹表 (Rainbow Table)」秒解：
- 使用 **`bcrypt`** 演算法。
- 強制規範 `Work Factor` (Cost) 至少設定為 **12** (依據機器算力，處理一次應消耗約 200~300ms)。
  > ✅ **現況**：`backend/app/core/security.py` 使用 `bcrypt.gensalt()` 預設值（12），數值合規；但 `.env.example` 中的 `BCRYPT_ROUNDS` 變數並未被實際讀取接線，屬於死設定，見 UMS-DEV-BE-FIX-007。

---

## 2. 開發前最終查核表 (OWASP Checklist)

開發團隊在提交程式碼前，必須逐項打勾確認以下實作：

### 🛡️ 輸入驗證與基礎防護 (Input Validation & Injection)
- [ ] 所有 API 的 Request Body 與 Query 參數是否均經過嚴格的型別與長度校驗 (Validation) 及消毒 (Sanitization)？
- [ ] 資料庫操作是否全面強制依賴 ORM 或 Prepared Statement，嚴禁以字串拼接形式執行 Raw SQL 以防範 SQL Injection 攻擊？

### 🔑 身分驗證 (Authentication)
- [ ] `/api/v1/auth/login` 等高風險端點是否實作了嚴格的 **Rate Limiting**? (例如：同一 IP 每分鐘最多失敗 5 次，超過封鎖 15 分鐘)。
  > ✅ **現況（2026-07-28 經 UMS-DEV-BE-061 & UMS-DEV-BE-FIX-008 覆核校正）**：
  > 1. `/api/v1/auth/login` 與 `/api/v1/auth/oauth/*/callback` 已由 `check_general_rate_limit` 進行 IP 頻率限制，對匿名流量正常生效。
  > 2. `POST /api/v1/admin/users` 為管理員建立帳號的後台 API（非公開註冊入口），其匿名流量於 `AuthMiddleware` 認證層即被 401 阻擋，刻意未納入路由層限流。
  > 3. 針對 bootstrap 空窗期（Redis 未標記 `bootstrap_completed`），`_is_bootstrap_bypass()` 於 DB 查詢前加入 IP 頻率限制 (10 次 / 60 秒)，超量時不執行 `select(func.count(User.id))` 並落回 401 阻擋，封堵匿名 DB 成本放大路徑。此結論以 `/admin/users` 非公開註冊入口為前提。
- [ ] 針對註冊 (`POST /api/v1/users`) 與忘記密碼等 API，是否加入了 Rate Limiting 以防範「可用信箱列舉攻擊 (Email Enumeration)」？
  > ✅ **現況（2026-07-28）**：已由 `check_general_rate_limit` (10 次 / 60 秒) 實作限流。
- [ ] 系統是否實施嚴格的密碼強度政策 (Password Policy)？(例如：最少 8~12 碼、包含英數大小寫，並阻擋常見弱密碼)。
- [ ] API 註冊建立使用者 (`POST /api/v1/users`) 的密碼儲存前是否確實調用 bcrypt 並套用 Salt？
- [ ] 是否規範 Refresh Token 在資料庫端會以雜湊或加密儲存，且是否實作 Token Rotation 機制 (每次使用 Refresh Token 換發時，舊 Token 立即失效)？
- [ ] 所有回傳 JWT Token 的端點是否都確實使用了 `Set-Cookie` 並包含 `HttpOnly; Secure; SameSite=Strict`？
- [ ] 執行登出 (`POST /api/v1/auth/logout`) 時，是否除了將 Session 寫入 Redis 黑名單，也同時清除了 Client 端的 Cookie (`Max-Age=0`)？

### 🛡️ 權限控管 (Authorization / IDOR)
- [ ] 修改/刪除使用者的端點 (例如 `PATCH /api/v1/users/{id}`)，在執行 DB 操作前，是否確實校驗了「操作者是 Admin」或「操作者本身的 `Token.id` 和 `{id}` 一模一樣」？
- [ ] JWT 內的預設 Payload 是否只包含無害資訊（例如 UUID、Role），絕無包含密碼 Hash、信用卡號或敏感個資？

### 🔌 傳輸與防護層 (Infrastructure)
- [ ] 正式環境與測試環境的 API Gateway 外部介接，是否強制限制為 `HTTPS`/`TLS 1.2+`（阻擋中間人攻擊 MITM）？
- [ ] CORS 配置是否明確拒絕 `Access-Control-Allow-Origin: *`？（若使用了 Cookie/Credentials，瀏覽器本就會報錯，但 Gateway 應主動配置白名單如 `https://web.workstation.internal`）。
- [ ] 針對系統初始化的自舉放行例外 (`GET /api/v1/system/status`)，是否已使用 Redis `SETNX` 機制防堵高併發搶佔建立 `Super Admin`？
  > ✅ **現況**：`backend/app/api/endpoints/users.py` 已使用 `redis.set("bootstrap_lock", "locked", nx=True, ex=30)` 實作。
- [ ] 是否針對敏感操作（如：賦予/修改權限、刪除使用者、異常大量登入失敗）實作了不可竄改的獨立稽核日誌 (Audit Logging)，以利後續 SIEM/SOC 工具的對接追蹤？
