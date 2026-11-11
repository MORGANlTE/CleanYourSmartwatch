"""Verify recorded package states without claiming all telemetry is eliminated."""

from .adb import SafetyError
from .engine import same_device, validate_changes
from .storage import now


def verify(adb, journal):
    validate_changes(journal)
    if "started" not in journal:
        raise SafetyError("Verification requires an actual session journal, not a dry-run plan")
    same_device(adb, journal["identity"])
    disabled = adb.packages(True)
    checks = []
    for change in journal["changes"]:
        status = change.get("status")
        current = adb.state(change["package"])
        if status in {"planned", "restored"}:
            expected = change["previous"]
        elif status == "applied":
            expected = change["target"]
        elif status in {"pending", "restoring"}:
            expected = None  # An interrupted command requires explicit reconciliation/restore.
        else:
            raise SafetyError("Unknown change status in session")
        matches = (
            expected is not None
            and current == expected
            and (change["package"] in disabled) == (expected in {2, 3, 4})
        )
        checks.append(
            {
                "package": change["package"],
                "journal_status": status,
                "expected": expected,
                "actual": current,
                "matches": matches,
            }
        )
    same_device(adb, journal["identity"])
    return {
        "at": now(),
        "identity": journal["identity"],
        "checks": checks,
        "all_recorded_states_match": bool(checks) and all(c["matches"] for c in checks),
        "functional_checks": "User testing of pairing, Health, calls/LTE, updates and UI still required",
        "telemetry_eliminated": "NOT VERIFIED; state checks are not traffic measurements",
        "device_changes": [],
    }
