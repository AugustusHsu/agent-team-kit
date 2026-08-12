"""測試共用 fixtures。

測試策略：**不在本 repo 內就地跑腳本**，而是先用 `install.sh` 把 `kit/` 安裝到暫存目錄，
再把假專案（`tests/fixture_project/`）疊上去，最後在該目錄裡執行腳本。
這樣一次驗證兩件事：install.sh 的複製行為，以及腳本在「安裝後的真實環境」裡能不能跑。
"""

import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
KIT_ROOT = REPO_ROOT / "kit"
INSTALL_SH = REPO_ROOT / "install.sh"
FIXTURE_PROJECT = Path(__file__).resolve().parent / "fixture_project"

TZ_TAIPEI = timezone(timedelta(hours=8))


def _expand_date_placeholders(root: Path) -> None:
    """把 fixture 工單裡的日期佔位符換成相對於「現在」的實際時間。

    寫死日期的話，`--recent-days` 的近期結案測試會隨著時間流逝自己壞掉。
    """
    now = datetime.now(TZ_TAIPEI)
    mapping = {
        "{{CLOSED_RECENT}}": (now - timedelta(days=1)).isoformat(timespec="minutes"),
        "{{CLOSED_OLD}}": (now - timedelta(days=400)).isoformat(timespec="minutes"),
    }
    for md in root.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        replaced = text
        for key, value in mapping.items():
            replaced = replaced.replace(key, value)
        if replaced != text:
            md.write_text(replaced, encoding="utf-8")


def run_script(project: Path, script: str, *args, timeout: int = 60):
    """在指定專案目錄裡執行 `.agent/scripts/<script>`，回傳 CompletedProcess。"""
    return subprocess.run(
        [sys.executable, f".agent/scripts/{script}", *args],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


@pytest.fixture(scope="session")
def bare_install(tmp_path_factory) -> Path:
    """只跑 install.sh、不疊 fixture 的乾淨安裝結果（給 test_install.py 用）。"""
    target = tmp_path_factory.mktemp("bare_install")
    subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)
    return target


@pytest.fixture(scope="session")
def project(tmp_path_factory) -> Path:
    """已安裝 kit + 已鋪好假工單的專案目錄。"""
    target = tmp_path_factory.mktemp("project")
    shutil.copytree(FIXTURE_PROJECT, target, dirs_exist_ok=True)
    _expand_date_placeholders(target)
    subprocess.run([str(INSTALL_SH), str(target)], check=True, capture_output=True, text=True)
    return target


@pytest.fixture(scope="session")
def kit_root() -> Path:
    return KIT_ROOT


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT
