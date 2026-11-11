import pytest

from cleanmywatch.adb import SafetyError
from cleanmywatch.engine import apply, plan, restore
from cleanmywatch.inventory import CATALOG, classification, eligible
from cleanmywatch.telemetry import review


def test_diagnostic_presence_is_not_removal_permission(adb):
    adb.states["com.sec.android.diagmonagent"] = 0
    report = review(adb)
    assert report["findings"][0]["category"] == "diagnostics"
    assert report["telemetry_eliminated"] == "NOT VERIFIED"
    assert classification("com.sec.android.diagmonagent")["action"] == "protected"
    with pytest.raises(SafetyError):
        eligible(adb, "com.sec.android.diagmonagent")
    assert adb.calls == []


@pytest.mark.parametrize(
    "package",
    [
        "com.android.vending",
        "com.google.android.gms",
        "com.samsung.android.shealthmonitor",
        "com.samsung.android.samsungpay.gear",
        "com.android.providers.media",
    ],
)
def test_core_protection_survives_catalog_misconfiguration(adb, monkeypatch, package):
    monkeypatch.setitem(CATALOG["packages"], package, {"purpose": "synthetic bad catalog entry"})
    with pytest.raises(SafetyError, match="Protected essential"):
        eligible(adb, package)
    assert adb.calls == []


@pytest.mark.parametrize(
    "package",
    [
        "com.sec.android.diagmonagent",
        "com.android.adservices.api",
        "com.samsung.android.gallery.watch",
        "com.samsung.android.app.reminder",
    ],
)
def test_experimental_system_requires_opt_in_and_restores(adb, tmp_path, package):
    adb.states[package] = 0
    adb.system_app = True
    with pytest.raises(SafetyError):
        plan(adb, "custom", [package])
    proposed = plan(adb, "custom", [package], experimental_system=True)
    path = apply(adb, tmp_path, proposed, lambda _: True, lambda: True)
    assert adb.states[package] == 3
    restore(adb, tmp_path, path, lambda _: True)
    assert adb.states[package] == 0


def test_experimental_mode_cannot_disable_health_or_unknown_system_app(adb):
    for package in ["com.samsung.android.wear.shealth", "org.example.unknown", "com.android.phone"]:
        adb.states[package] = 0
        with pytest.raises(SafetyError):
            plan(adb, "custom", [package], experimental_system=True)
    assert adb.calls == []
