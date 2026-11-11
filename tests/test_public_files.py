import runpy
from pathlib import Path

import pytest

MODULE = runpy.run_path(str(Path(__file__).parents[1] / "tools" / "check_public_files.py"))


def test_private_paths_and_credentials_are_flagged():
    assert MODULE["private_path"](".cleanmywatch/audits/example.json")
    assert MODULE["private_path"]("adbkey.pub")
    assert MODULE["private_path"]("capture.pcap")
    assert not MODULE["private_path"]("examples/synthetic-audit.md")
    token = ("ghp" + "_" + "A" * 30).encode()
    assert MODULE["findings"](token)


def test_private_local_policy_is_case_insensitive():
    assert MODULE["findings"](b"PRIVATE-SYNTHETIC-CONTEXT", ["private-synthetic-context"])
    assert not MODULE["findings"](b"Generic platform installation guide")


def test_history_revision_cannot_inject_git_options():
    with pytest.raises(ValueError):
        MODULE["scan"](True, "--all")
