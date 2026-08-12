# 測試

驗證的是**這個套件本身**：`install.sh` 複製對不對、三支腳本在安裝後的環境跑不跑得動、
`kit/` 內的 SKILL 與 evals 有沒有壞掉。不是驗證「AI 角色表現得好不好」——那是各角色
`evals/evals.json` 的事，需要真的跑模型。

```bash
uv run pytest              # 全部
uv run pytest -k install   # 只跑 install.sh 相關
```

全部離線執行，約 1.5 秒。

## 測法

不在本 repo 內就地跑腳本，而是先 `install.sh` 到暫存目錄、把假專案疊上去，再在那裡執行。
一次驗證兩件事：安裝行為，以及腳本在「安裝後的真實環境」裡能不能運作。
組裝邏輯在 `conftest.py` 的 `project` fixture。

| 檔案 | 測什麼 |
|---|---|
| `test_install.py` | 1:1 複製、不覆寫既有檔案、`--force`、目標不存在時拒絕安裝 |
| `test_scan_backlog.py` | metadata 解析、狀態正規化、四大區塊分類、近期結案切分、三種 `--format` |
| `test_check_versions.py` | 階段一自我驗證與一致性驗證、無 PyYAML 時的備用解析器 |
| `test_migrate_dates.py` | 預設預覽模式不改檔案、模組篩選 |
| `test_kit_integrity.py` | SKILL frontmatter、evals schema、死連結、`team_protocol.md` 只有一份 |

## `fixture_project/`

一個刻意「有點亂」的假專案，每個檔案都對應一條要釘住的行為：

| 檔案 | 為什麼存在 |
|---|---|
| `tasks/_INDEX.md` | 底線開頭的檔案必須被當成索引跳過，不算工單 |
| `ABC-DEV-BE-003.md` | H1 標題故意不合格式，釘住「回退為以檔名當 Task ID」 |
| `ABC-TEST-QA-001.md` | Status 寫成 `Canceled (改由 ... 統一涵蓋)`，釘住狀態正規化 |
| `ABC-DOC-EPIC-001.md` | 400 天前結案 → 應落到「已封存」 |
| `XYZ-DEV-MANUAL-001.md` | 1 天前結案 → 應落到「近期結案」；另涵蓋 `manual_user` 類型 |
| `third_party_versions*.yaml` | 三種情境：通過、宣告與實體檔案不符、關聯項目版本不一致 |

底線開頭的**目錄**（kit 自己帶的 `_TEMPLATE/`）不該被當成功能模組，這條是直接對安裝結果驗證的，
不放在 fixture 裡：全新安裝掃不到任何模組應以非零狀態碼結束，從骨架複製出模組後則應立刻被掃到。

工單裡的 `{{CLOSED_RECENT}}` / `{{CLOSED_OLD}}` 由 `conftest.py` 在複製時換成相對於
「現在」的時間。寫死日期的話，`--recent-days` 的測試會隨時間流逝自己壞掉。

版本宣告 fixture 的 `source_type` 一律是 `local`——它不屬於任何已知上游來源，
`check_versions.py` 的階段二會直接回 `UNSUPPORTED SOURCE`，因此不發任何網路請求。
階段二的真實上游查詢沒有納入測試（會連 DockerHub / PyPI / npm / GitHub，CI 裡不可靠）。
