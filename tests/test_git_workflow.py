"""以真實暫存 Git repo 驗證兩層 merge、worktree 生命週期與安全回收。"""

import subprocess
from pathlib import Path


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
    )


def _建立_repo(path: Path) -> Path:
    path.mkdir()
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.name", "agent-team-kit test")
    _git(path, "config", "user.email", "agent-team-kit@example.invalid")
    _git(path, "config", "commit.gpgsign", "false")
    return path


def _提交(repo: Path, rel: str, content: str, message: str) -> str:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _parents(repo: Path, revision: str) -> list[str]:
    return _git(repo, "show", "-s", "--format=%P", revision).stdout.split()


def test_兩層_merge保留_first_parent且可安全回收(tmp_path: Path):
    """task→round→main 都保留 merge commit，branch ref 刪除後仍可從歷史反查。"""
    repo = _建立_repo(tmp_path / "repo")
    _提交(repo, "README.md", "opening base\n", "建立 opening base")
    _git(repo, "branch", "feature/round-test")

    task_a_tree = tmp_path / "TASK-001-worktree"
    task_b_tree = tmp_path / "TASK-002-worktree"
    _git(repo, "worktree", "add", "-b", "TASK-001", str(task_a_tree), "feature/round-test")
    _git(repo, "worktree", "add", "-b", "TASK-002", str(task_b_tree), "feature/round-test")
    active_worktrees = _git(repo, "worktree", "list", "--porcelain").stdout.splitlines()
    assert sum(line.startswith("worktree ") for line in active_worktrees) == 3
    task_a_head = _提交(task_a_tree, "task-a.txt", "A\n", "完成 TASK-001")
    task_b_head = _提交(task_b_tree, "task-b.txt", "B\n", "完成 TASK-002")

    main_concurrent = _提交(repo, "main.txt", "main moved\n", "main 同期前進")

    _git(repo, "switch", "feature/round-test")
    _git(repo, "merge", "--no-ff", "TASK-001", "-m", "merge(task): [TASK-001] 併入輪次")
    task_a_merge = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "merge", "--no-ff", "TASK-002", "-m", "merge(task): [TASK-002] 併入輪次")
    task_b_merge = _git(repo, "rev-parse", "HEAD").stdout.strip()
    round_head = task_b_merge

    _git(repo, "worktree", "remove", str(task_a_tree))
    _git(repo, "worktree", "remove", str(task_b_tree))
    assert _git(repo, "show-ref", "--verify", "refs/heads/TASK-001").returncode == 0
    assert _git(repo, "show-ref", "--verify", "refs/heads/TASK-002").returncode == 0

    returned_tree = tmp_path / "TASK-001-returned"
    _git(repo, "worktree", "add", str(returned_tree), "TASK-001")
    assert _git(returned_tree, "rev-parse", "HEAD").stdout.strip() == task_a_head
    _git(repo, "worktree", "remove", str(returned_tree))

    round_first_parent = _git(
        repo, "log", "--first-parent", "--format=%s", "feature/round-test"
    ).stdout.splitlines()
    assert round_first_parent[:3] == [
        "merge(task): [TASK-002] 併入輪次",
        "merge(task): [TASK-001] 併入輪次",
        "建立 opening base",
    ]
    assert len(_parents(repo, task_a_merge)) == 2
    assert len(_parents(repo, task_b_merge)) == 2
    assert task_a_head in _parents(repo, task_a_merge)
    assert task_b_head in _parents(repo, task_b_merge)

    _git(repo, "switch", "main")
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == main_concurrent
    _git(
        repo,
        "merge",
        "--no-ff",
        "feature/round-test",
        "-m",
        "merge(round): [ROUND-001] 完成輪次",
        "-m",
        "- TASK-001\n- TASK-002",
    )
    round_merge = _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert len(_parents(repo, round_merge)) == 2
    assert round_head in _parents(repo, round_merge)
    assert (repo / "main.txt").read_text(encoding="utf-8") == "main moved\n"
    assert (repo / "task-a.txt").read_text(encoding="utf-8") == "A\n"
    assert (repo / "task-b.txt").read_text(encoding="utf-8") == "B\n"

    main_first_parent = _git(repo, "log", "--first-parent", "--format=%s", "main").stdout.splitlines()
    assert main_first_parent[:3] == [
        "merge(round): [ROUND-001] 完成輪次",
        "main 同期前進",
        "建立 opening base",
    ]

    for branch in ("TASK-001", "TASK-002", "feature/round-test"):
        _git(repo, "merge-base", "--is-ancestor", branch, "main")
        _git(repo, "branch", "-d", branch)

    refs = _git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.splitlines()
    assert refs == ["main"]
    worktree_lines = _git(repo, "worktree", "list", "--porcelain").stdout.splitlines()
    assert sum(line.startswith("worktree ") for line in worktree_lines) == 1

    history = _git(repo, "log", "--all", "--format=%s%n%b").stdout
    assert "TASK-001" in history
    assert "TASK-002" in history
    assert "ROUND-001" in history


def test_安全刪除拒絕尚未合併的工單分支(tmp_path: Path):
    """安全回收失敗時不得把 branch -d 偷換成會丟資料的 branch -D。"""
    repo = _建立_repo(tmp_path / "repo")
    _提交(repo, "README.md", "base\n", "建立 base")
    _git(repo, "switch", "-c", "TASK-UNMERGED")
    _提交(repo, "unmerged.txt", "尚未合併\n", "未合併變更")
    _git(repo, "switch", "main")

    result = _git(repo, "branch", "-d", "TASK-UNMERGED", check=False)

    assert result.returncode != 0
    assert _git(repo, "show-ref", "--verify", "refs/heads/TASK-UNMERGED").returncode == 0


def test_rerere_維持_repo_local選用且不取代驗證(repo_root: Path):
    """kit 不預設啟用 rerere；操作指引必須保留 local、diff 與測試三道限制。"""
    skill = (repo_root / "kit/.agent/skills/devops-engineer/SKILL.md").read_text(encoding="utf-8")
    standard = (repo_root / "kit/docs/standards/parallel_development.md").read_text(
        encoding="utf-8"
    )
    installer = (repo_root / "install.sh").read_text(encoding="utf-8")

    assert "git config --local rerere.enabled true" in skill
    assert "人工檢查 diff" in skill
    assert "重跑受影響測試" in skill
    assert "不得版控 `.git/rr-cache`" in standard
    assert "rerere.enabled" not in installer


def test_devops_操作指引保留條件式隔離與安全命令(repo_root: Path):
    """操作指南必須對應真實 repo 測過的建立、合併、重建與安全清理命令。"""
    skill = (repo_root / "kit/.agent/skills/devops-engineer/SKILL.md").read_text(encoding="utf-8")

    assert "只有同一輪有兩張以上工單同時活躍" in skill
    assert "只有一張活躍時沿用主工作目錄" in skill
    assert "git worktree add -b <TaskID> <path> <round-branch>" in skill
    assert "git worktree add <path> <TaskID>" in skill
    assert "git merge --no-ff" in skill
    assert "git worktree remove <path>" in skill
    assert "git merge-base --is-ancestor <branch> main" in skill
    assert "git branch -d <branch>" in skill
    assert "刪除失敗不得改用 `-D`" in skill
