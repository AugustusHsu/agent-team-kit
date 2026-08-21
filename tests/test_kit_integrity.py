"""kit/ 內容本身的一致性：SKILL frontmatter、evals schema、文件連結。

這些是 clone 這份套件的人最先踩到的東西，壞掉不會有任何執行期錯誤提醒你。
"""

import json
import re
from pathlib import Path

import pytest

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
EVAL_KEYS = {"id", "prompt", "expected_output", "files", "expectations"}
# 連結的正則、placeholder 白名單與剝除規則一律取自出貨的 precheck（見 _死連結）——
# 這裡不留第二份常數，否則兩邊遲早分岔，而分岔的方向永遠是測試這邊放行得比較寬。
# 每次推翻一條流程規則，就把舊說法加進這張表。反轉規範時你清楚自己廢除了什麼，
# 不清楚的是它還躺在哪幾個角落。
已廢除的流程規則 = [
    (r"APPROVED[^\n]{0,8}改為\s*[`「]?Done", "Done 已改為「已合併進主線」，APPROVED 只是放行訊號"),
    (r"APPROVED\s*時[^\n]{0,10}填寫[^\n]{0,20}Closed", "Closed 改由 Developer 在結案 commit 填"),
    (r"審查通過後才[^\n]{0,6}commit", "commit 時點已改為開發期間即可 commit"),
    (r"此時不要\s*commit", "commit 時點已改為開發期間即可 commit"),
    # 抓的是形狀不是措辭：缺陷長成「填 Closed」後面用頓號直接並列編號。
    # 正確的三種寫法（編號移出結案 commit 的括號、或加「早在…已回填」）都不會命中。
    (
        r"填 Closed[、，][^\n]{0,8}編號",
        "審查載體編號在開 PR／MR 當下就回填，結案 commit 只改 Status 與 Closed",
    ),
    # squash 下 --is-ancestor 永遠回非 0，拿它當「已合併」判準等於分支永遠刪不掉。
    (
        r"merge-base --is-ancestor[^\n]*#[^\n]*已合併",
        "squash 路徑的已合併判準改為比對樹，--no-ff 路徑用 git branch -d（§6.4）",
    ),
    # squash 的理由建立在「PR 保存過程 commit」上，無遠端時前提不成立（§8.3）。
    (
        r"一律[^\n]{0,6}squash",
        "squash 只在有 PR／MR 平台時成立，無遠端改用 --no-ff（§6.1／§8.3）",
    ),
    (r"訊號.{0,6}主線含該 commit", "squash 後過程 commit 不在主線，判準是樹相同（§6.4）"),
    # §6.1 改成平台分流後，「一般流程」的敘述不能再把 squash 當成唯一選項。
    # §8.2 的 GitHub 設定清單（「只留 squash」）本來就是平台專屬，不在此列，
    # 所以只抓兩種殘留形狀：指著 §6.1 說它是 squash、以及流程表格裡的裸「squash 合併」儲存格。
    (
        r"§6\.1 的 squash|\| *squash 合併 *\|",
        "一般流程不得寫死 squash，合併方式依平台分流（§6.1）",
    ),
    # commit 閘門的範圍是「進入主線前」，不是「每一顆 commit 前」。抓兩種殘留形狀：
    # §1.10 那句「任何 commit 之前」，以及 kit/CLAUDE.md 模板叫每個專案抄進自己
    # CLAUDE.md 的嚴格版——後者槓桿最大，抄錯就會在每個裝了 kit 的專案每次請求生效。
    (
        r"任何 commit 之前|commit 前必須把訊息原文",
        "commit 閘門在進入主線那一刻；工單分支上的中間 commit 不需事前同意（§1.10）",
    ),
    # 模板的 Commit 範例原本只寫「格式見 …」，而那個地址在順手 commit 的路徑上
    # 不會被載入——PEV-DEV-AGENT-021 把 Body 格式改為內嵌，長度紀律隨之放寬到五行。
    (
        r"寫\*\*三行以內\*\*|^格式見 `\.agent/workflows/commit-message\.md`。$",
        "Commit 範例必須內嵌 Body 條列格式，長度紀律改為五行以內（PEV-DEV-AGENT-021）",
    ),
    # 審查紀錄的落點改成 reviews/<TaskID>.md（PEV-DEV-AGENT-016）。工單仍留
    # 「📝 Code Review 備註」章節，所以不能抓章節名，只能抓「完整報告塞進工單」的形狀。
    (
        r"審查結果直接寫入對應工單|審查載體改為工單的|記錄本次審查發現的具體問題",
        "完整審查報告改放 docs/features/<模組>/reviews/<TaskID>.md，工單只留結論與客觀指標（§2.3）",
    ),
    # 近期結案的時間窗已移除（PEV-DEV-AGENT-013）：生成檔不得含時間相依值，
    # 否則同一份輸入每天重跑會生出假 diff。
    (
        r"最近 7 天|7 天 \+ 上限|--recent-days",
        "近期結案只按完成時間倒序取最新 N 筆，不看今天是哪一天"
        "（documentation_conventions.md §5）",
    ),
    # PEV-DEV-AGENT-017 的結論是「這件事關不掉，只能靠讀法規避」，PEV-DEV-AGENT-023
    # 追到根因後推翻：中間層有工具保護名單，保真是可設定的，規避只是修不了時的退路。
    # 正版同時從 §2.3 移到 §1.12（適用全角色），但 §2.3 仍是合法章節、多處正當指向它，
    # 沒有能區分新舊的正則——那條靠這裡的措辭抓，抓不到的靠 §1.12 本身是唯一正版。
    (
        r"只能靠讀法規避|這件事關不掉",
        "保真優先修通道設定，規避是修不了時的退路（§1.12）",
    ),
]


def skill_dirs(kit_root: Path):
    return sorted((kit_root / ".agent" / "skills").iterdir())


def pytest_generate_tests(metafunc):
    if "skill_dir" in metafunc.fixturenames:
        kit = Path(__file__).resolve().parent.parent / "kit"
        dirs = skill_dirs(kit)
        metafunc.parametrize("skill_dir", dirs, ids=[d.name for d in dirs])


def test_角色數量為十三(kit_root: Path):
    assert len(skill_dirs(kit_root)) == 13


def test_frontmatter_的_name_與目錄名相符(skill_dir: Path):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    assert match, f"{skill_dir.name}/SKILL.md 缺少 frontmatter"
    fields = dict(
        line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
    )
    assert fields["name"].strip() == skill_dir.name
    assert fields["description"].strip(), "description 不可為空——它是自動觸發的唯一依據"


def test_每個角色都有_evals(skill_dir: Path):
    assert (skill_dir / "evals" / "evals.json").is_file()


def test_evals_符合_skill_creator_schema(skill_dir: Path):
    data = json.loads((skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"))
    assert set(data) == {"skill_name", "evals"}
    assert data["skill_name"] == skill_dir.name
    assert data["evals"], "至少要有一筆 eval"

    for index, item in enumerate(data["evals"], start=1):
        assert set(item) == EVAL_KEYS, f"#{index} 欄位不符：{sorted(item)}"
        assert item["id"] == index, "id 應為 1 起算的連號"
        assert item["prompt"].strip()
        assert item["expected_output"].strip()
        assert isinstance(item["files"], list)
        assert item["expectations"], f"#{index} 缺少 expectations"
        assert all(isinstance(x, str) and x.strip() for x in item["expectations"])


def test_evals_不得殘留來源專案的識別資訊(skill_dir: Path):
    """這是給人 clone 的模板，eval 內容不能帶著開發者原專案的模組名與工單編號。"""
    leak = re.compile(
        r"user_management_system|task_management_system|UMS-|TMS-|LVS-|DMS-", re.IGNORECASE
    )
    text = (skill_dir / "evals" / "evals.json").read_text(encoding="utf-8")
    assert not leak.search(text), f"{skill_dir.name} 的 evals 疑似殘留來源專案資訊"


def markdown_files(root: Path):
    return sorted(p for p in root.rglob("*.md"))


def _死連結(precheck, 檔案: Path, 基準: Path, 標籤: str) -> list[str]:
    """死連結的判定完全委派給出貨的 precheck，測試這邊一行判斷邏輯都不寫。

    原本這裡是逐行 `LINK.finditer`，**沒有剝 code fence 與行內 code**——
    跟 `precheck.check_dead_links()` 是同一件事的兩份實作，而落後的是這一份。
    文件把連結語法當例子引用時（`[DN-007](DN-007_ci_gate.md)`），
    precheck 會跳過、測試會誤判；反過來 `{TaskID}` 這類佔位路徑 precheck 跳過
    而測試沒有。收斂之後只剩一份規則，改一次兩邊同時生效。
    """
    壞的 = []
    內容 = precheck.strip_code(檔案.read_text(encoding="utf-8"))
    for lineno, line in enumerate(內容.splitlines(), start=1):
        for match in precheck.LINK_RE.finditer(line):
            target = match.group(1).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if target in precheck.PLACEHOLDER_WORDS:
                continue
            if any(char in target for char in precheck.PLACEHOLDER_CHARS):
                continue
            if not (基準 / target).exists():
                壞的.append(f"{標籤}:{lineno} → {target}")
    return 壞的


def test_kit_內沒有死連結(kit_root: Path):
    precheck = _載入_precheck(kit_root)
    broken = []
    for md in markdown_files(kit_root):
        broken += _死連結(precheck, md, md.parent, str(md.relative_to(kit_root)))
    assert not broken, "死連結：\n" + "\n".join(broken)


def test_團隊守則只有一份正版(kit_root: Path):
    """正版只能有一份；`docs/standards/` 那份必須是指路檔，複製過去一定會 drift。"""
    found = sorted(p.relative_to(kit_root).as_posix() for p in kit_root.rglob("team_protocol.md"))
    assert found == [".agent/resources/team_protocol.md", "docs/standards/team_protocol.md"]

    正版 = (kit_root / ".agent/resources/team_protocol.md").read_text(encoding="utf-8")
    指路檔 = (kit_root / "docs/standards/team_protocol.md").read_text(encoding="utf-8")

    assert "本檔不含內容" in 指路檔
    assert "../../.agent/resources/team_protocol.md" in 指路檔
    # 指路檔只列章節標題，不得抄任何一段正文
    正文 = [
        line.strip()
        for line in 正版.splitlines()
        if line.strip() and not line.startswith(("#", "|", ">", "-", "`"))
    ]
    抄襲 = [line for line in 正文 if line in 指路檔]
    assert not 抄襲, "指路檔抄了正版的內容：\n" + "\n".join(抄襲)


def test_指路檔章節索引與正版同步(kit_root: Path):
    """索引表是指路檔唯一會過期的部分——正版加章節就必須回來補一列。"""
    正版 = (kit_root / ".agent/resources/team_protocol.md").read_text(encoding="utf-8")
    指路檔 = (kit_root / "docs/standards/team_protocol.md").read_text(encoding="utf-8")

    章節 = re.findall(r"^### (\d+\.\d+) ", 正版, flags=re.MULTILINE)
    assert 章節, "正版找不到任何 §x.y 章節，測試本身可能過期了"
    缺漏 = [f"§{s}" for s in 章節 if f"| §{s} |" not in 指路檔]
    assert not 缺漏, "指路檔的章節索引漏了：" + "、".join(缺漏)


# --- skill 與守則的一致性（PEV-DEV-AGENT-026）-------------------------------
# 兩條檢查都只驗證「有沒有正確引用」，不驗證「引用之後有沒有照做」——
# 後者是語意判斷，不該進閘門。

引用路徑 = re.compile(r"team_protocol\.md|git_workflow\.md")


def _守則章節(kit_root: Path) -> dict[str, str]:
    """§X.Y → 標題主體。括號裡的英文與 emoji 是修飾，不納入比對。

    這是誤報緩解的唯一機制：把 `取證通道保真 (🔬 Evidence Channel Fidelity)`
    收斂成 `取證通道保真`，於是補英文、加 emoji 這類純修飾改動不會轉紅。
    """
    正版 = (kit_root / ".agent/resources/team_protocol.md").read_text(encoding="utf-8")
    return {
        m.group(1): m.group(2).split("(")[0].strip()
        for m in re.finditer(r"^### (\d+\.\d+) (.+)$", 正版, flags=re.MULTILINE)
    }


def _適用全角色的章節(kit_root: Path) -> list[str]:
    """標了「適用全角色」的章節編號。範圍是該章節標題到下一個 ### 為止。"""
    正版 = (kit_root / ".agent/resources/team_protocol.md").read_text(encoding="utf-8")
    區塊 = re.split(r"^### (\d+\.\d+) ", 正版, flags=re.MULTILINE)
    # split 後為 [前言, 編號, 內容, 編號, 內容, ...]
    return [區塊[i] for i in range(1, len(區塊), 2) if "適用全角色" in 區塊[i + 1]]


def test_適用全角色的章節被十三份_skill_全部引用(kit_root: Path):
    """標「適用全角色」卻只有半數 skill 引用的章節，等於對另外半數不存在。

    §1.12 就是實例：它是 PEV-DEV-AGENT-023 從 §2.3（只綁審查者）升級成全角色的，
    升級當下要手動補 13 份 skill——漏掉任何一份都不會有執行期錯誤。

    ⚠️ 已知限制（邊界）：本檢查依賴**規範作者記得寫「適用全角色」那四個字**。
    沒標記的章節抓不到，因此它防的是「規範標了但 skill 沒跟上」，
    **不是**「規範作者忘了標記適用範圍」。後者沒有機器判準——
    一個章節該不該適用全角色是設計決定，不是可從文字推導的事實。
    """
    章節 = _適用全角色的章節(kit_root)
    assert 章節, "team_protocol.md 找不到任何標「適用全角色」的章節，測試本身可能過期了"

    缺漏 = []
    for d in skill_dirs(kit_root):
        內容 = (d / "SKILL.md").read_text(encoding="utf-8")
        for 編號 in 章節:
            # (?!\d) 不可省：否則找 §1.1 時 §1.12 會誤判為命中
            if not re.search(rf"§{re.escape(編號)}(?!\d)", 內容):
                缺漏.append(f"{d.name}/SKILL.md 沒有引用 §{編號}（該節標了「適用全角色」）")
    assert not 缺漏, "適用全角色的章節沒被全部 skill 引用：\n" + "\n".join(缺漏)


def test_skill_引用守則的編號與標題都要對得上(kit_root: Path):
    """只比對編號是不夠的——編號幾乎總是還在，錯的是它現在指向誰。

    DN-004 §4 附錄用丟棄式原型實跑過：在「§1.9 後插入一節、後續各往下推一格」的
    重編號情境中，4 筆 `§1.12` 引用當場指到「文檔權威階序」而非「取證通道保真」，
    而只比對編號的版本**仍然全綠**。加上標題比對後同一情境抓到全部 4 筆。

    比對方式是**反向**的：不去猜「標題在原文裡到哪裡結束」（結尾符號有
    `）`、`。`、`、`、` 的「…」` 等多種，猜不完），而是取真實標題去比對
    `§X.Y ` 後面是不是以它開頭。

    只驗 `team_protocol.md` 的引用。歸屬方式是往前找最近提到的檔名，因為
    `§1.9 程式碼隔離與分支、§1.10 Commit 閘門` 這種寫法只在第一個編號前寫了檔名。
    指向 `git_workflow.md` 的引用不在本檢查範圍（AC-02），它們的正版在另一份文件。
    """
    章節 = _守則章節(kit_root)
    問題 = []

    for d in skill_dirs(kit_root):
        內容 = (d / "SKILL.md").read_text(encoding="utf-8")
        for m in re.finditer(r"§(\d+\.\d+)", 內容):
            編號 = m.group(1)
            前文 = 內容[: m.start()]
            最近檔名 = 引用路徑.findall(前文)
            if not 最近檔名 or 最近檔名[-1] != "team_protocol.md":
                continue

            行號 = 前文.count("\n") + 1
            位置 = f"{d.name}/SKILL.md:{行號}"
            if 編號 not in 章節:
                問題.append(f"{位置} 引用了不存在的 §{編號}")
                continue

            尾巴 = 內容[m.end() :]
            # 編號後面沒接空白 = 只引用編號、沒宣稱標題，那就只驗編號存在
            if 尾巴[:1] not in (" ", "　"):
                continue
            期望 = 章節[編號]
            實際 = 尾巴.lstrip(" 　")
            if not 實際.startswith(期望):
                問題.append(
                    f"{位置} §{編號} 的標題對不上："
                    f"期望「{期望}」，實際「{實際.splitlines()[0][: len(期望) + 8]}」"
                )

    assert not 問題, "skill 對守則的引用與正版不符：\n" + "\n".join(問題)


def test_kit_不得殘留已廢除的流程規則(kit_root: Path):
    """規範反轉後，舊敘述會躺在沒人想到要改的角落，而且不會有任何執行期錯誤。

    規則散落在 team_protocol、十三份 SKILL.md、十三份 evals.json 與 workflows，
    靠人工 grep 收工已經失守過一次：PEV-DEV-AGENT-001 改了四份 SKILL.md，
    漏掉 code-reviewer 的 evals.json，而當時的測試全綠照樣放行。

    邊界一（漏抓）：這是回顧性防護，只擋「已知被廢除」的說法，擋不了新產生的不一致。
    維護方式就是每次推翻一條規則，回來加一列——漏加一列等於那條規則沒有防線，
    PEV-DEV-AGENT-001 二輪審查抓到的就是這個：它廢除了「結案 commit 填 PR 編號」，
    卻沒為自己加那一列，殘留於是在 98 passed 底下隱形。

    邊界二（誤判）：表達不出「教舊規則」與「**禁止**舊規則」的差別。
    「審查者不得將 Status 由 APPROVED 改為 Done」這種語意正確的句子會被命中。
    處置是改寫措辭（例如避開字面組合）或為該列加豁免，不是刪測試——
    它會帶著 `檔案:行號` 大聲失敗，不會安靜地錯。

    只掃 kit/：`docs/design_notes/` 底下的 🎓 Graduated DN 依 DN-001 是凍結的歷史
    紀錄、不得作為規格依據，掃進去只會對「當時的設計」產生設計上的必然誤判。
    """
    命中 = []
    for path in sorted(kit_root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json"}:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern, 為什麼 in 已廢除的流程規則:
                if re.search(pattern, line):
                    命中.append(f"{path.relative_to(kit_root)}:{lineno} → {為什麼}")
    assert not 命中, "殘留已廢除的流程規則：\n" + "\n".join(命中)


def test_standards_文件都登記在_DOCS_MAP(kit_root: Path):
    """漏登記的規範文件等於不存在——沒有人用 ls 找規範，只會查 DOCS_MAP。"""
    docs_map = (kit_root / "docs/DOCS_MAP.md").read_text(encoding="utf-8")
    漏登記 = [
        p.name
        for p in sorted((kit_root / "docs/standards").glob("*.md"))
        # README.md 是 standards/ 自己的目錄索引，DOCS_MAP 不必再列一次
        if p.name != "README.md" and p.name not in docs_map
    ]
    assert not 漏登記, "這些規範文件沒登記進 DOCS_MAP：" + "、".join(漏登記)


def _載入_precheck(kit_root: Path):
    """從 kit/ 載入出貨版 precheck，而不是根目錄那份安裝實例。"""
    import importlib.util

    路徑 = kit_root / ".agent/scripts/precheck.py"
    spec = importlib.util.spec_from_file_location("_kit_precheck", 路徑)
    模組 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(模組)
    return 模組


def test_能力對照表的檢查內容與_precheck_實際項目一致(kit_root: Path):
    """§8.1 多寫一項而腳本沒跑，就是承諾了一個不存在的閘門——本節原本的毛病。"""
    precheck = _載入_precheck(kit_root)
    腳本項目 = [標題 for 標題, _ in precheck.CHECKS]

    表格 = (kit_root / "docs/standards/git_workflow.md").read_text(encoding="utf-8")
    自動檢查列 = [
        line for line in 表格.splitlines() if line.startswith("| 自動檢查 |")
    ]
    assert len(自動檢查列) == 1, "§8.1 找不到（或找到多列）「自動檢查」列"
    檢查內容欄 = 自動檢查列[0].strip().strip("|").split("|")[-1].strip()
    表格項目 = [x.strip() for x in 檢查內容欄.split("、")]

    assert 表格項目 == 腳本項目, (
        "§8.1「檢查內容」欄與 precheck.py 的 CHECKS 不一致：\n"
        f"  表格：{表格項目}\n"
        f"  腳本：{腳本項目}"
    )


def test_出貨的_workflow_只做第一層(kit_root: Path):
    """第 2 層跟技術棧綁定，kit 猜不到；猜了就是出貨一份跑不動的 CI。"""
    workflow = kit_root / ".github/workflows/kit-precheck.yml"
    assert workflow.is_file(), "kit 沒有出貨 CI workflow，但規範三處指向它"

    內容 = workflow.read_text(encoding="utf-8")
    生效行 = [
        line
        for line in 內容.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert any("precheck.py" in line for line in 生效行), "workflow 沒有呼叫 precheck.py"

    for 禁字 in ("uv ", "pytest", "npm ", "go test"):
        違規 = [line for line in 生效行 if 禁字 in line]
        assert not 違規, (
            f"出貨的 workflow 不該含專案測試指令（{禁字.strip()}）：{違規}"
        )


def test_出貨的_workflow_監聽所有分支(kit_root: Path):
    """只監聽主線的話，不開 PR 的專案整批 commit 在合併前從未被檢查（§8.3（b））。"""
    內容 = (kit_root / ".github/workflows/kit-precheck.yml").read_text(encoding="utf-8")
    assert "branches: ['**']" in 內容, (
        "出貨的 workflow 必須監聽所有分支，否則對「有遠端但不推送 PR」的專案形同不存在"
    )


# --- 根目錄 README 與出貨內容的同步 ---------------------------------------
# README 是評估用門面，它抄的每一份表述都是「第二份表述」，依 design_note §3.8
# 必然漂移。以下三個測試把漂移變成紅燈，而不是靠人記得回來改。


def _表格第一欄(內容: str, 標題: str) -> list[str]:
    """取出指定標題底下第一張表格的第一欄（去掉表頭、分隔列與尾綴的節號）。"""
    行 = 內容.split("\n")
    for i, l in enumerate(行):
        if l.startswith(標題):
            起 = i
            break
    else:
        raise AssertionError(f"找不到標題：{標題}")

    欄, 進入表格 = [], False
    for l in 行[起 + 1 :]:
        if l.startswith("|"):
            進入表格 = True
            欄.append([c.strip() for c in l.strip().strip("|").split("|")][0])
        elif 進入表格:
            break
    return [re.sub(r"（§[^）]*）$", "", c) for c in 欄[2:]]


def test_README_能力對照表與_git_workflow_同步(kit_root: Path, repo_root: Path):
    """README 摘要的那七列，必須就是正版 §8.1 的那七列。"""
    正版 = _表格第一欄(
        (kit_root / "docs" / "standards" / "git_workflow.md").read_text(encoding="utf-8"),
        "### 8.1 能力對照表",
    )
    摘要 = _表格第一欄(
        (repo_root / "README.md").read_text(encoding="utf-8"), "## Git 流程與換平台"
    )
    assert 摘要 == 正版, (
        "README 的能力對照表與 git_workflow.md §8.1 不同步：\n"
        f"  README：{摘要}\n  正版　：{正版}"
    )


def _內容物樹(readme: str) -> str:
    """取出「## 內容物」底下那個 fenced block。

    ⚠️ 不能拿整份 README 做子字串比對——正文別處順口提到 `precheck.py`
    就會把樹裡的缺漏遮掉（實測過，負向對照因此不轉紅）。
    """
    起 = readme.index("## 內容物")
    前, _, 後 = readme[起:].partition("```")
    區塊, _, _ = 後.partition("```")
    assert 區塊.strip(), "「## 內容物」底下找不到目錄樹區塊"
    return 區塊


def test_README_內容物涵蓋出貨的腳本與目錄(kit_root: Path, repo_root: Path):
    """新增出貨腳本或頂層目錄卻沒寫進 README 的目錄樹，就是門面落後於出貨內容。"""
    readme = _內容物樹((repo_root / "README.md").read_text(encoding="utf-8"))
    缺漏 = []
    for p in sorted((kit_root / ".agent" / "scripts").glob("*.py")):
        if p.name not in readme:
            缺漏.append(f".agent/scripts/{p.name}")
    for p in sorted(kit_root.iterdir()):
        if p.is_dir() and p.name not in readme:
            缺漏.append(f"{p.name}/")
    for p in sorted((kit_root / "docs").iterdir()):
        if p.is_dir() and p.name not in readme:
            缺漏.append(f"docs/{p.name}/")
    assert not 缺漏, "README「內容物」沒跟上 kit 的實際結構：\n" + "\n".join(缺漏)


def test_README_沒有死連結(kit_root: Path, repo_root: Path):
    """precheck 只掃 docs/、test_kit_內沒有死連結 只掃 kit/，根目錄 README 兩邊都漏。"""
    precheck = _載入_precheck(kit_root)
    broken = _死連結(precheck, repo_root / "README.md", repo_root, "README.md")
    assert not broken, "README 死連結：\n" + "\n".join(broken)


def test_模板的_commit_範例帶上_body_格式(kit_root: Path):
    """只寫「格式見 …」等於沒寫——那個地址在順手 commit 的路徑上不會被載入。

    本套件自己踩過：`CLAUDE.md` 忠實照抄了只指路的舊範例，整批歷史 commit 的 Body
    因此寫成散文，而 `commit-message.md` 要求的是 `- **標題**：說明`。
    模板是槓桿最大的地方——它錯一次，每個裝了 kit 的專案都跟著錯。
    """
    模板 = (kit_root / "CLAUDE.md").read_text(encoding="utf-8")
    起 = 模板.index("## Commit 規則這裡必須寫")
    _, _, 後 = 模板[起:].partition("```markdown")
    範例, _, _ = 後.partition("```")
    assert 範例.strip(), "「Commit 規則這裡必須寫」底下找不到範例區塊"

    for 必要, 說明 in [
        ("- **標題**：說明", "Body 條列格式"),
        ("AI 署名 trailer", "禁止 AI 署名 trailer"),
        ("合併回主線前", "閘門的範圍"),
    ]:
        assert 必要 in 範例, f"範例沒帶上「{說明}」，等於又退回只指路"

    行數 = len([l for l in 範例.strip().splitlines() if l.strip()])
    assert 行數 <= 5, f"範例 {行數} 行，超過模板自訂的五行紀律"
