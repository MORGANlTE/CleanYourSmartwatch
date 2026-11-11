import pytest

from cleanmywatch.adb import ADB, SafetyError


@pytest.mark.parametrize(
    "release,sdk,build,telephony",
    [
        ("11", "30", "synthetic-wearos3-build", True),
        ("13", "33", "synthetic-wearos4-build", True),
        ("14", "34", "synthetic-newer-build", False),
    ],
)
def test_synthetic_firmware_identity_and_no_raw_serial(monkeypatch, release, sdk, build, telephony):
    raw_serial = "SYNTHETIC_NOT_A_REAL_DEVICE"
    props = {
        "ro.product.manufacturer": "samsung",
        "ro.product.model": "SAMPLE-WATCH",
        "ro.build.fingerprint": build,
        "ro.build.version.release": release,
        "ro.build.version.sdk": sdk,
        "ro.build.characteristics": "watch,nosdcard",
        "ro.serialno": raw_serial,
    }
    adb = ADB("synthetic-device", "synthetic-adb")

    def shell(*args):
        if args[0] == "getprop":
            return props[args[1]]
        return (
            "feature:android.hardware.telephony" if telephony else "feature:android.hardware.watch"
        )

    monkeypatch.setattr(adb, "shell", shell)
    result = adb.identity()
    assert result["telephony_feature"] is telephony
    assert result["ro.build.fingerprint"] == build
    assert raw_serial not in str(result)
    assert len(result["device_token"]) == 64


def test_missing_physical_identity_refused(monkeypatch):
    adb = ADB("synthetic-device", "synthetic-adb")

    def shell(*args):
        return {
            "ro.product.manufacturer": "samsung",
            "ro.build.characteristics": "watch",
            "ro.serialno": "unknown",
        }.get(args[-1], "synthetic")

    monkeypatch.setattr(adb, "shell", shell)
    with pytest.raises(SafetyError):
        adb.identity()
