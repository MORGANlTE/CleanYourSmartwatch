import pytest

from cleanmywatch.adb import SafetyError


class FakeADB:
    def __init__(self, state=0, firmware="synthetic-watch4-wearos3"):
        self.states = {
            "android": 0,
            "com.android.phone": 0,
            "com.spotify.music": state,
            "org.example.pre_disabled": 3,
        }
        self.firmware = firmware
        self.token = "synthetic-physical-device-token"
        self.calls = []
        self.fail = None
        self.system_app = False

    def identity(self):
        return {"device_token": self.token, "ro.build.fingerprint": self.firmware}

    def packages(self, disabled=False):
        return {p for p, state in self.states.items() if not disabled or state in (2, 3, 4)}

    def details(self, package):
        if package not in self.states:
            return "Unable to find package"
        flags = "SYSTEM HAS_CODE" if self.system_app else "HAS_CODE"
        return (
            f"Package [{package}]\n  codePath=/data/app/synthetic\n"
            f"  pkgFlags=[ {flags} ]\n  User 0: installed=true hidden=false enabled={self.states[package]}\n"
        )

    def state(self, package):
        return self.states[package]

    def set_state(self, package, state):
        self.calls.append((package, state))
        if self.fail == "before":
            raise SafetyError("Synthetic dropped connection")
        self.states[package] = state
        if self.fail == "after":
            raise SafetyError("Synthetic dropped response")
        if self.fail == "ignored":
            self.states[package] = 0
        return "synthetic command result"


@pytest.fixture
def adb():
    return FakeADB()
