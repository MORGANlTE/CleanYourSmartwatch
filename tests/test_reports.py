import json

import pytest
from typer.testing import CliRunner

from cleanmywatch.adb import SafetyError
from cleanmywatch.battery import compare
from cleanmywatch.cli import app
from cleanmywatch.privacy import blocklist, dns_summary


def test_cli_help_and_device_requirement():
    runner = CliRunner()
    assert runner.invoke(app, ["--help"]).exit_code == 0
    assert runner.invoke(app, ["audit"]).exit_code == 2
    assert runner.invoke(app, ["optimize"]).exit_code == 0


def test_menu_quit_without_device_commands(monkeypatch):
    monkeypatch.setenv("CLEANMYWATCH_ADB", "synthetic-adb")
    assert (
        CliRunner().invoke(app, ["tui", "--device", "synthetic-device"], input="q\n").exit_code == 0
    )


def test_dns_unknown_default_and_mixed_exclusion(tmp_path):
    log = tmp_path / "dns.csv"
    log.write_text(
        "domain\nunknown.example.invalid\nmixed.example.invalid\nad.example.invalid\n",
        encoding="utf-8",
    )
    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps(
            {
                "mixed.example.invalid": {
                    "category": "mixed",
                    "confidence": "high",
                    "evidence": "synthetic",
                },
                "ad.example.invalid": {
                    "category": "advertising",
                    "confidence": "high",
                    "evidence": "synthetic",
                },
            }
        ),
        encoding="utf-8",
    )
    data = dns_summary(log, rules)
    assert blocklist(data) == "||ad.example.invalid^\n"
    assert any(e["category"] == "unknown" for e in data["endpoints"])


def test_dns_rule_syntax_injection_rejected(tmp_path):
    log = tmp_path / "dns.csv"
    log.write_text("domain\nexample.invalid\n", encoding="utf-8")
    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps(
            {
                "example.invalid\n||other.invalid^": {
                    "category": "analytics",
                    "evidence": "synthetic",
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SafetyError):
        dns_summary(log, rules)


def test_battery_comparison_and_charging_limit():
    before = dict(
        identity={"firmware": "synthetic"},
        at="2026-01-01T00:00:00+00:00",
        percent=80,
        charging=False,
        configuration="synthetic unchanged",
    )
    after = dict(before, at="2026-01-01T04:00:00+00:00", percent=72)
    assert compare(before, after)["estimated_points_per_hour"] == 2
    assert compare(before, dict(after, charging=True))["estimated_points_per_hour"] is None
    with pytest.raises(SafetyError):
        compare(before, dict(after, identity={"firmware": "other"}))
