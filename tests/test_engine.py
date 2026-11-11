import pytest

from cleanmywatch.adb import SafetyError
from cleanmywatch.engine import apply, plan, restore
from cleanmywatch.storage import locked, read, save

APP = "com.spotify.music"


@pytest.mark.parametrize("previous", [0, 1])
def test_exact_previous_state_and_unrelated_disabled_preserved(adb, tmp_path, previous):
    adb.states[APP] = previous
    proposed = plan(adb, "conservative", [APP])
    assert adb.calls == []
    journal = apply(adb, tmp_path, proposed, lambda c: True, lambda: True)
    assert adb.states[APP] == 3
    assert read(journal)["changes"][0]["previous"] == previous
    assert list((tmp_path / "backups").glob("*.json"))
    restore(adb, tmp_path, journal, lambda c: True)
    assert adb.states[APP] == previous
    assert adb.states["org.example.pre_disabled"] == 3
    assert read(journal)["status"] == "restored"


@pytest.mark.parametrize(
    "reason", ["no-backup", "declined", "different-device", "firmware", "drift"]
)
def test_preflight_fails_without_any_change(adb, tmp_path, reason):
    proposed = plan(adb, "conservative", [APP])
    if reason == "different-device":
        adb.token = "different-watch"
    if reason == "firmware":
        adb.firmware = "synthetic-watch4-wearos4"
    if reason == "drift":
        adb.states[APP] = 1
    with pytest.raises(SafetyError):
        apply(
            adb, tmp_path, proposed, lambda c: reason != "declined", lambda: reason != "no-backup"
        )
    assert adb.calls == []


@pytest.mark.parametrize("failure", ["before", "after", "ignored"])
def test_interrupted_command_can_be_reconciled(adb, tmp_path, failure):
    proposed = plan(adb, "conservative", [APP])
    adb.fail = failure
    with pytest.raises(SafetyError):
        apply(adb, tmp_path, proposed, lambda c: True, lambda: True)
    journal = next((tmp_path / "sessions").glob("*.json"))
    assert read(journal)["changes"][0]["status"] == "pending"
    adb.fail = None
    restore(adb, tmp_path, journal, lambda c: True)
    assert adb.states[APP] == 0


def test_write_ahead_journal_exists_before_device_mutation(adb, tmp_path):
    original = adb.set_state

    def checked(package, state):
        journal = next((tmp_path / "sessions").glob("*.json"))
        assert read(journal)["changes"][0]["status"] == "pending"
        assert list((tmp_path / "backups").glob("*.json"))
        return original(package, state)

    adb.set_state = checked
    apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)


@pytest.mark.parametrize(
    "package",
    ["com.android.phone", "android", "org.example.unknown", "com.spotify.music;reboot", "*"],
)
def test_unknown_core_and_injection_rejected(adb, package):
    with pytest.raises(SafetyError):
        plan(adb, "aggressive", [package])
    assert adb.calls == []


@pytest.mark.parametrize("state", [2, 3, 4])
def test_existing_disabled_states_refused(adb, state):
    adb.states[APP] = state
    with pytest.raises(SafetyError):
        plan(adb, "balanced", [APP])


def test_preloaded_optional_app_protected(adb):
    adb.system_app = True
    with pytest.raises(SafetyError):
        plan(adb, "conservative", [APP])


@pytest.mark.parametrize("tamper", ["package", "state", "target", "duplicate"])
def test_tampered_plan_rejected(adb, tmp_path, tamper):
    proposed = plan(adb, "conservative", [APP])
    if tamper == "package":
        proposed["changes"][0]["package"] = "com.android.phone"
    elif tamper == "state":
        proposed["changes"][0]["previous"] = 4
    elif tamper == "target":
        proposed["changes"][0]["target"] = 0
    else:
        proposed["changes"] *= 2
    with pytest.raises(SafetyError):
        apply(adb, tmp_path, proposed, lambda c: True, lambda: True)
    assert adb.calls == []


def test_wrong_device_restore_rejected(adb, tmp_path):
    journal = apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    adb.token = "another-device"
    with pytest.raises(SafetyError):
        restore(adb, tmp_path, journal, lambda c: True)
    assert adb.states[APP] == 3


def test_restore_pending_after_response_lost(adb, tmp_path):
    journal = apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    adb.fail = "after"
    with pytest.raises(SafetyError):
        restore(adb, tmp_path, journal, lambda c: True)
    assert read(journal)["changes"][0]["status"] == "restoring"
    adb.fail = None
    restore(adb, tmp_path, journal, lambda c: True)
    assert read(journal)["status"] == "restored"


def test_lock_blocks_concurrent_operations(tmp_path):
    with locked(tmp_path), pytest.raises(SafetyError), locked(tmp_path):
        pass


def test_backup_write_failure_prevents_mutation(adb, tmp_path, monkeypatch):
    def fail(*args):
        raise OSError("synthetic disk full")

    monkeypatch.setattr("cleanmywatch.engine.save", fail)
    with pytest.raises(OSError):
        apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    assert adb.calls == []


def test_empty_plan_does_not_write_to_watch(adb, tmp_path):
    proposed = plan(adb, "conservative", [])
    with pytest.raises(SafetyError):
        apply(adb, tmp_path, proposed, lambda c: True, lambda: True)
    assert adb.calls == []


def test_recovery_record_cannot_enable_unknown_package(adb, tmp_path):
    journal = apply(adb, tmp_path, plan(adb, "conservative", [APP]), lambda c: True, lambda: True)
    data = read(journal)
    data["changes"][0]["package"] = "com.android.phone"
    save(journal, data)
    with pytest.raises(SafetyError):
        restore(adb, tmp_path, journal, lambda c: True)


def test_interrupted_session_blocks_new_apply(adb, tmp_path):
    proposed = plan(adb, "conservative", [APP])
    adb.fail = "before"
    with pytest.raises(SafetyError):
        apply(adb, tmp_path, proposed, lambda c: True, lambda: True)
    adb.fail = None
    with pytest.raises(SafetyError, match="Unresolved interrupted session"):
        apply(adb, tmp_path, proposed, lambda c: True, lambda: True)
    assert len(adb.calls) == 1


@pytest.mark.parametrize(
    "malformed", [[], {"schema": 1, "changes": [None]}, {"schema": 1, "changes": [{"package": []}]}]
)
def test_malformed_json_state_stops_cleanly(adb, tmp_path, malformed):
    with pytest.raises(SafetyError):
        apply(adb, tmp_path, malformed, lambda c: True, lambda: True)
    assert not adb.calls
