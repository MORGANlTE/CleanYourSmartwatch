import pytest

from cleanmywatch.adb import SafetyError
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
