from github.git_operations import GitOperations


def test_rollback_files(monkeypatch):
    commands = []

    def fake_run_git_command(command):
        commands.append(command)
        return ""

    monkeypatch.setattr(
        "github.git_operations._run_git_command",
        fake_run_git_command,
    )

    git = GitOperations()

    result = git.rollback_files(
        ["calculator.py"]
    )

    assert result is True

    assert commands == [
        'git restore -- "calculator.py"'
    ]