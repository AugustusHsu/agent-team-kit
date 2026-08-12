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
    """`team_protocol.md` 若被複製進 docs/standards/ 一定會 drift。"""
    copies = [p for p in kit_root.rglob("team_protocol.md")]
    assert [p.relative_to(kit_root).as_posix() for p in copies] == [
        ".agent/resources/team_protocol.md"
    ]
