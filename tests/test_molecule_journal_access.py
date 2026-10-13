"""The journal regression must run without utilities absent in minimal images."""
import yaml
from test_templates import REPO_ROOT


def test_journal_regression_uses_the_docker_user_not_su() -> None:
    play = yaml.safe_load((REPO_ROOT / "molecule/resources/verify.yml").read_text())[0]
    block = next(task for task in play["tasks"] if task["name"] == "Check journals as the unprivileged Docker user")
    assert block["vars"]["ansible_user"] == "vitals-journal-reader"
    assert not block.get("become", False)
    identity, scan, verdict = block["block"]
    assert identity["ansible.builtin.command"]["argv"] == ["id", "-un"]
    assert "vitals-journal-reader" in identity["failed_when"]
    assert scan["ansible.builtin.include_role"]["name"].endswith(".vitals_scan")
    assert "apply" not in scan["ansible.builtin.include_role"]
    assert any("length == 2" in rule for rule in verdict["ansible.builtin.assert"]["that"])


def test_prepare_does_not_require_logger_to_populate_the_journal() -> None:
    tasks = yaml.safe_load((REPO_ROOT / "molecule/resources/prepare.yml").read_text())[0]["tasks"]
    commands = [task["ansible.builtin.command"]["argv"][0]
                for task in tasks if "ansible.builtin.command" in task]
    assert "logger" not in commands
    assert "systemctl" in commands
