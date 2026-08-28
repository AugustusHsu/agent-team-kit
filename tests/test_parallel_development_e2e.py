"""以真實安裝、Git repo 與 subprocess 驗證並行開發流程的完整鏈路。"""

import json
import subprocess
import sys
from pathlib import Path

from conftest import INSTALL_SH


def _執行(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return _執行("git", *args, cwd=repo, check=check)


def _建立_git_repo(path: Path) -> Path:
    path.mkdir()
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.name", "agent-team-kit e2e")
    _git(path, "config", "user.email", "agent-team-kit@example.invalid")
    _git(path, "config", "commit.gpgsign", "false")
    return path


def _提交全部(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _提交檔案(repo: Path, rel: str, content: str, message: str) -> str:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _安裝(target: Path) -> subprocess.CompletedProcess:
    target.mkdir()
    return _執行(str(INSTALL_SH), str(target), cwd=INSTALL_SH.parent)


def _工單(
    task_id: str,
    *,
    blocked_by: str = "—",
    write_scope: str,
    external_effects: str,
    contract: str = "—",
) -> str:
    return (
        f"# [Task ID: {task_id}] 端到端測試工單\n\n"
        "**🔗 依附母任務 (Parent Task ID):** Independent\n"
        "**🏷️ 任務類型 (Task Type):** queue_backend\n"
        "**👤 負責人 (Assignee):** backend-developer\n"
        f"**⛓️ 前置工單 (Blocked By):** {blocked_by}\n"
        f"**✍️ 寫入範圍 (Write Scope):** `{write_scope}`\n"
        f"**🌐 外部副作用 (External Effects):** {external_effects}\n"
        f"**📜 共用契約 (Contract):** {contract}\n"
        "**🔁 變更集合 (Change Set):** —\n"
        "**🪜 變更階段 (Phase):** —\n"
        "**🚥 任務狀態 (Status):** Pending\n"
        "**📅 建立時間 (Created):** 2026-08-28T10:00+08:00\n"
        "**✅ 完成時間 (Closed):** —\n"
        "**🔀 審查載體編號 (PR/MR):** —\n"
    )


def _寫五張工單與輪次(project: Path, opening_base: str) -> list[str]:
    task_ids = [f"E2E-DEV-AGENT-00{index}" for index in range(1, 6)]
    tasks_dir = project / "docs/features/e2e/tasks"
    tasks_dir.mkdir(parents=True)
    definitions = {
        task_ids[0]: _工單(
            task_ids[0],
            write_scope="docs/contracts/bootstrap.md",
            external_effects="repo:contracts/bootstrap",
        ),
        task_ids[1]: _工單(
            task_ids[1],
            blocked_by=task_ids[0],
            write_scope="src/left.py",
            external_effects="repo:src/left",
            contract="`docs/contracts/shared.md`",
        ),
        task_ids[2]: _工單(
            task_ids[2],
            blocked_by=task_ids[0],
            write_scope="tests/right.py",
            external_effects="repo:tests/right",
            contract="`docs/contracts/shared.md`",
        ),
        task_ids[3]: _工單(
            task_ids[3],
            blocked_by=f"{task_ids[1]}, {task_ids[2]}",
            write_scope="docs/integration.md",
            external_effects="repo:docs/integration",
        ),
        task_ids[4]: _工單(
            task_ids[4],
            blocked_by=task_ids[3],
            write_scope="docs/release.md",
            external_effects="repo:docs/release",
        ),
    }
    for task_id, content in definitions.items():
        (tasks_dir / f"{task_id}.md").write_text(content, encoding="utf-8")

    round_dir = project / "docs/development/rounds"
    round_dir.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f"| `{task_id}` | 驗證 {task_id} | Pending |" for task_id in task_ids)
    (round_dir / "ROUND-901_e2e.md").write_text(
        "# [Round ID: ROUND-901] 端到端測試輪次\n\n"
        "**🚥 輪次狀態 (Status):** Open\n"
        "**🎯 輪次目標 (Goal):** 驗證完整並行鏈路\n"
        "**🌿 輪次分支 (Branch):** `feature/e2e-round`\n"
        f"**📍 開輪基準 (Opening Base):** `{opening_base}`\n"
        "**📅 建立時間 (Created):** 2026-08-28T10:00+08:00\n"
        "**🔎 整合審查對象 (Integration Review Target):** —\n\n"
        "## 1. 封閉工單集合（唯一來源）\n\n"
        "| Task ID | 目標 | 初始狀態 |\n"
        "|---|---|---|\n"
        f"{rows}\n\n"
        "## 2. 衍生視圖\n\n由掃描器產生。\n",
        encoding="utf-8",
    )
    return task_ids


def _parents(repo: Path, revision: str) -> list[str]:
    return _git(repo, "show", "-s", "--format=%P", revision).stdout.split()


def test_安裝後五工單_dag_wave_contract與條件式_worktree串成完整鏈路(
    tmp_path: Path,
):
    """從空專案安裝後，規劃來源與同 wave worktree 必須能由同一條鏈路實跑。"""
    project = tmp_path / "project"
    install = _安裝(project)
    (project / "docs/contracts").mkdir(parents=True)
    (project / "docs/contracts/shared.md").write_text("# Shared contract\n", encoding="utf-8")
    _git(project, "init", "-b", "main")
    _git(project, "config", "user.name", "agent-team-kit e2e")
    _git(project, "config", "user.email", "agent-team-kit@example.invalid")
    _git(project, "config", "commit.gpgsign", "false")
    opening_base = _提交全部(project, "建立安裝後 opening base")
    task_ids = _寫五張工單與輪次(project, opening_base)

    graph_result = _執行(
        sys.executable,
        ".agent/scripts/scan_backlog.py",
        "--format",
        "graph",
        cwd=project,
        check=False,
    )
    graph = json.loads(graph_result.stdout)
    round_view = graph["rounds"]["ROUND-901"]
    _git(project, "branch", "feature/e2e-round", opening_base)
    left_tree = tmp_path / task_ids[1]
    right_tree = tmp_path / task_ids[2]
    _git(
        project,
        "worktree",
        "add",
        "-b",
        task_ids[1],
        str(left_tree),
        "feature/e2e-round",
    )
    _git(
        project,
        "worktree",
        "add",
        "-b",
        task_ids[2],
        str(right_tree),
        "feature/e2e-round",
    )
    active = _git(project, "worktree", "list", "--porcelain").stdout.splitlines()
    _git(project, "worktree", "remove", str(left_tree))
    _git(project, "worktree", "remove", str(right_tree))
    cleaned = _git(project, "worktree", "list", "--porcelain").stdout.splitlines()

    assert "✅ 安裝完成" in install.stdout, "空專案應能由正式 installer 完成安裝"
    assert (project / ".agent/.kit-manifest").is_file(), "安裝後缺少 kit manifest"
    assert graph_result.returncode == 0, graph_result.stderr
    assert graph["errors"] == [], f"合法五工單規劃不應產生錯誤：{graph['errors']}"
    assert round_view["topological_order"] == task_ids, "五張工單拓撲順序不符合 DAG"
    assert round_view["waves"] == {
        "1": [task_ids[0]],
        "2": [task_ids[1], task_ids[2]],
        "3": [task_ids[3]],
        "4": [task_ids[4]],
    }, "wave 應由 Blocked By 唯一推導"
    assert [task_ids[1], task_ids[2]] in round_view["parallel_candidates"], (
        "同 wave 且 Write Scope、Contract、External Effects 可隔離的工單應成為候選"
    )
    assert sum(line.startswith("worktree ") for line in active) == 3
    assert sum(line.startswith("worktree ") for line in cleaned) == 1
    for task_id in task_ids[1:3]:
        assert _git(project, "show-ref", "--verify", f"refs/heads/{task_id}").returncode == 0


def test_工單進輪次再進當下主線候選保留兩層_first_parent與安全回收(
    tmp_path: Path,
):
    """同期 main 前進時，integration candidate 仍要保留 task→round→main 兩層 merge。"""
    repo = _建立_git_repo(tmp_path / "repo")
    opening_base = _提交檔案(repo, "README.md", "opening base\n", "建立 opening base")
    _git(repo, "branch", "feature/e2e-round", opening_base)

    _git(repo, "switch", "-c", "E2E-DEV-AGENT-001", "feature/e2e-round")
    task_a_head = _提交檔案(repo, "task-a.txt", "A\n", "完成 E2E-DEV-AGENT-001")
    _git(repo, "switch", "feature/e2e-round")
    _git(repo, "switch", "-c", "E2E-DEV-AGENT-002", "feature/e2e-round")
    task_b_head = _提交檔案(repo, "task-b.txt", "B\n", "完成 E2E-DEV-AGENT-002")
    _git(repo, "switch", "main")
    main_concurrent = _提交檔案(repo, "main.txt", "main moved\n", "main 同期前進")

    _git(repo, "switch", "feature/e2e-round")
    _git(
        repo,
        "merge",
        "--no-ff",
        "E2E-DEV-AGENT-001",
        "-m",
        "merge(task): [E2E-DEV-AGENT-001] 併入輪次",
    )
    task_a_merge = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(
        repo,
        "merge",
        "--no-ff",
        "E2E-DEV-AGENT-002",
        "-m",
        "merge(task): [E2E-DEV-AGENT-002] 併入輪次",
    )
    round_head = _git(repo, "rev-parse", "HEAD").stdout.strip()

    _git(repo, "switch", "-c", "integration/ROUND-901", "main")
    _git(
        repo,
        "merge",
        "--no-ff",
        "feature/e2e-round",
        "-m",
        "merge(round): [ROUND-901] 建立當下主線候選",
        "-m",
        "- E2E-DEV-AGENT-001\n- E2E-DEV-AGENT-002",
    )
    integration_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    round_first_parent = _git(
        repo, "log", "--first-parent", "--format=%s", "feature/e2e-round"
    ).stdout.splitlines()
    integration_first_parent = _git(
        repo, "log", "--first-parent", "--format=%s", "integration/ROUND-901"
    ).stdout.splitlines()

    for branch in ("E2E-DEV-AGENT-001", "E2E-DEV-AGENT-002", "feature/e2e-round"):
        _git(repo, "merge-base", "--is-ancestor", branch, "integration/ROUND-901")
        _git(repo, "branch", "-d", branch)

    assert _parents(repo, task_a_merge) == [opening_base, task_a_head]
    assert task_b_head in _parents(repo, round_head) and len(_parents(repo, round_head)) == 2
    assert _parents(repo, integration_head) == [main_concurrent, round_head]
    assert round_first_parent[:3] == [
        "merge(task): [E2E-DEV-AGENT-002] 併入輪次",
        "merge(task): [E2E-DEV-AGENT-001] 併入輪次",
        "建立 opening base",
    ]
    assert integration_first_parent[:3] == [
        "merge(round): [ROUND-901] 建立當下主線候選",
        "main 同期前進",
        "建立 opening base",
    ]
    assert (repo / "main.txt").read_text(encoding="utf-8") == "main moved\n"
    assert (repo / "task-a.txt").read_text(encoding="utf-8") == "A\n"
    assert (repo / "task-b.txt").read_text(encoding="utf-8") == "B\n"
    refs = _git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout
    assert "E2E-DEV-AGENT" not in refs and "feature/e2e-round" not in refs


def test_review_target漂移與整合失敗歸因只退回受影響層(tmp_path: Path):
    """不可變 SHA 用真實 commit 證明失效；退回策略使用安裝後第 1 層規範判定。"""
    installed = tmp_path / "installed"
    _安裝(installed)
    standard = (installed / "docs/standards/parallel_development.md").read_text(
        encoding="utf-8"
    )
    round_template = (installed / "docs/development/rounds/_TEMPLATE.md").read_text(
        encoding="utf-8"
    )
    repo = _建立_git_repo(tmp_path / "repo")
    opening_base = _提交檔案(repo, "README.md", "base\n", "建立 opening base")
    _git(repo, "branch", "feature/e2e-round", opening_base)
    _git(repo, "switch", "-c", "E2E-DEV-AGENT-001", "feature/e2e-round")
    task_review_head = _提交檔案(repo, "task.txt", "reviewed\n", "固定 task target")
    task_target = (
        f"base={opening_base}; head={task_review_head}; id=E2E-DEV-AGENT-001"
    )
    changed_task_head = _提交檔案(repo, "task.txt", "drifted\n", "審查後 head 漂移")
    _git(repo, "switch", "feature/e2e-round")
    _git(
        repo,
        "merge",
        "--no-ff",
        "E2E-DEV-AGENT-001",
        "-m",
        "merge(task): [E2E-DEV-AGENT-001] 併入輪次",
    )
    round_review_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    round_target = f"base={opening_base}; head={round_review_head}; id=ROUND-901"
    changed_round_head = _提交檔案(
        repo,
        "round-evidence.md",
        "metadata changed\n",
        "審查後 round head 漂移",
    )

    assert len(opening_base) == len(task_review_head) == len(round_review_head) == 40
    assert task_target.endswith("id=E2E-DEV-AGENT-001")
    assert round_target.endswith("id=ROUND-901")
    assert changed_task_head != task_review_head, "task head 改變後舊窄審 target 必須失效"
    assert changed_round_head != round_review_head, "round head 改變後舊 panel target 必須失效"
    _git(repo, "merge-base", "--is-ancestor", task_review_head, changed_task_head)
    _git(repo, "merge-base", "--is-ancestor", round_review_head, changed_round_head)
    assert "task head 改變重跑該工單窄審；round head 改變重跑" in standard
    assert "受影響 panel 面向" in standard
    assert "可歸因到單張工單" in standard and "重建原 branch／worktree 修正" in standard
    assert "跨工單互動：開 integration-fix" in standard
    assert "超過五張就重新規劃" in standard
    assert "供應商、模型、PR 平台與 worktree 工具都不是流程語意的一部分" in standard
    for evidence_field in (
        "QA Candidate Target",
        "失敗歸因／退回紀錄",
        "Panel Candidate Target",
        "Final Review Target",
    ):
        assert evidence_field in round_template, f"安裝後 Round 範本缺少 {evidence_field}"
