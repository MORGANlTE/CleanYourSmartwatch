from types import SimpleNamespace

import pytest

from cleanmywatch.adb import ADB, SafetyError, endpoint, package_name


def test_target_required_before_shell_execution(monkeypatch):
    calls = []
    monkeypatch.setattr("subprocess.run", lambda *a, **k: calls.append(a))
    with pytest.raises(SafetyError):
        ADB(binary="synthetic-adb").shell("pm", "list", "packages")
    assert calls == []


def test_subprocess_argv_no_host_shell(monkeypatch):
    def run(command, **kwargs):
        assert command == [
            "synthetic-adb",
            "-s",
            "synthetic-device",
            "shell",
            "pm",
            "disable-user",
            "--user",
            "0",
            "com.spotify.music",
        ]
        assert not kwargs.get("shell", False)
        return SimpleNamespace(returncode=0, stdout="ok")

    monkeypatch.setattr("subprocess.run", run)
    assert ADB("synthetic-device", "synthetic-adb").set_state("com.spotify.music", 3) == "ok"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("User 0: installed=true enabled=0", 0),
        ("User 0: installed=true hidden=false enabled=1", 1),
        ("User 10: installed=true enabled=1", None),
        ("User 0: installed=false enabled=1", None),
        ("User 0: installed=true enabled=10", None),
        ("error: synthetic", None),
        (
            "Resolver metadata mentions User 0: unrelated\n  User 0: installed=true enabled=0\n  User 0:\n",
            0,
        ),
        ("User 0: installed=true enabled=0\nUser 0: installed=true enabled=1", None),
        (
            "Packages:\n  User 0: installed=true enabled=1\nHidden system packages:\n  User 0: installed=true enabled=0",
            1,
        ),
    ],
)
def test_strict_user_zero_state_parser(monkeypatch, text, expected):
    adb = ADB("synthetic-device", "synthetic-adb")
    monkeypatch.setattr(adb, "details", lambda p: text)
    if expected is None:
        with pytest.raises(SafetyError):
            adb.state("com.spotify.music")
    else:
        assert adb.state("com.spotify.music") == expected


def test_android_base_package_in_inventory(monkeypatch):
    adb = ADB("synthetic-device", "synthetic-adb")
    monkeypatch.setattr(adb, "shell", lambda *a: "package:android\npackage:com.android.phone")
    assert adb.packages() == {"android", "com.android.phone"}


@pytest.mark.parametrize(
    "value", ["--help", "host:0", "host:65536", "host:123;reboot", "host port:123"]
)
def test_invalid_connection_input(value):
    with pytest.raises(SafetyError):
        endpoint(value)


@pytest.mark.parametrize("value", ["*", "com.app;reboot", "$(reboot)", "com.app x", "--help"])
def test_package_injection(value):
    with pytest.raises(SafetyError):
        package_name(value)


@pytest.mark.parametrize("manufacturer,characteristics", [("samsung", "phone"), ("other", "watch")])
def test_non_watch_or_non_samsung_rejected(monkeypatch, manufacturer, characteristics):
    adb = ADB("synthetic-device", "synthetic-adb")

    def shell(*args):
        return {
            "ro.product.manufacturer": manufacturer,
            "ro.build.characteristics": characteristics,
        }.get(args[-1], "synthetic")

    monkeypatch.setattr(adb, "shell", shell)
    with pytest.raises(SafetyError):
        adb.identity()
