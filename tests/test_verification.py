import pytest

from cleanmywatch.adb import SafetyError
from cleanmywatch.engine import apply, plan, restore
from cleanmywatch.storage import read
from cleanmywatch.verification import verify

APP = "com.spotify.music"


def test_verify_disable_and_exact_restore_without_mutation(adb, tmp_path):
    path = apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    calls = list(adb.calls)
    result = verify(adb, read(path))
    assert result["all_recorded_states_match"]
    assert result["telemetry_eliminated"].startswith("NOT VERIFIED")
    assert adb.calls == calls
    restore(adb, tmp_path, path, lambda c: True)
    assert verify(adb, read(path))["all_recorded_states_match"]


def test_verify_detects_reenabled_app(adb, tmp_path):
    path = apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    adb.states[APP] = 0
    assert not verify(adb, read(path))["all_recorded_states_match"]


def test_pending_command_is_not_certified_clean(adb, tmp_path):
    path = apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    journal = read(path)
    journal["changes"][0]["status"] = "pending"
    assert not verify(adb, journal)["all_recorded_states_match"]


def test_plan_cannot_be_used_as_proof_of_actual_changes(adb):
    with pytest.raises(SafetyError):
        verify(adb, plan(adb, "conservative", [APP]))
