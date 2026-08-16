"""kit/ 內容本身的一致性：SKILL frontmatter、evals schema、文件連結。

這些是 clone 這份套件的人最先踩到的東西，壞掉不會有任何執行期錯誤提醒你。
"""

import json
import re
from pathlib import Path

import pytest

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EVAL_KEYS = {"id", "prompt", "expected_output", "files", "expectations"}
# 文中拿來說明格式、不是真實路徑的字面值
LINK_PLACEHOLDERS = {"路徑", "relative/path"}
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
        "§6.1 一律 squash，已合併的判準改為比對樹（§6.4）",
    ),
    (r"訊號.{0,6}主線含該 commit", "squash 後過程 commit 不在主線，判準是樹相同（§6.4）"),
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


def test_kit_內沒有死連結(kit_root: Path):
    broken = []
    for md in markdown_files(kit_root):
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
            for match in LINK.finditer(line):
                target = match.group(1).split("#")[0].strip()
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target in LINK_PLACEHOLDERS:
                    continue
                if not (md.parent / target).exists():
                    broken.append(f"{md.relative_to(kit_root)}:{lineno} → {target}")
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
