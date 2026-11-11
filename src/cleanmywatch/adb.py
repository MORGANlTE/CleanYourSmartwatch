"""Small ADB boundary. No shell=True, host shell interpolation, or implicit targets."""

import hashlib
import os
import re
import shutil
import subprocess


class SafetyError(RuntimeError):
    pass


def package_name(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*", value):
        raise SafetyError("Invalid package identifier")
    return value


def endpoint(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*:[0-9]{1,5}", value):
        raise SafetyError("Use a host:port endpoint (no URLs, spaces or shell syntax)")
    if not 1 <= int(value.rsplit(":", 1)[1]) <= 65535:
        raise SafetyError("Port outside 1..65535")
    return value


class ADB:
    def __init__(self, serial: str | None = None, binary: str | None = None):
        self.binary = binary or os.environ.get("CLEANMYWATCH_ADB") or shutil.which("adb")
        if not self.binary:
            raise SafetyError("ADB missing. Install official Platform Tools; see docs/SETUP.md")
        if serial and not re.fullmatch(r"[A-Za-z0-9_.:-]+", serial):
            raise SafetyError("Invalid device selector")
        self.serial = serial

    def run(self, *args: str, targeted: bool = False) -> str:
        command = [self.binary]
        if targeted:
            if not self.serial:
                raise SafetyError(
                    "Explicit --device required, even when only one device is connected"
                )
            command += ["-s", self.serial]
        try:
            result = subprocess.run(
                command + list(args), capture_output=True, text=True, timeout=45, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SafetyError("ADB unavailable or timed out; inspect connection locally") from exc
        if result.returncode:
            # Do not put raw ADB output (possibly identifiers) into reports/exceptions.
            raise SafetyError("ADB failed; check authorization, connection port and server locally")
        return result.stdout.strip()

    def shell(self, *args: str) -> str:
        return self.run("shell", *args, targeted=True)

    def packages(self, disabled: bool = False) -> set[str]:
        args = ["pm", "list", "packages", "--user", "0"]
        if disabled:
            args.append("-d")
        output = self.shell(*args)
        if any(line and not line.startswith("package:") for line in output.splitlines()):
            raise SafetyError("Unexpected package-list response")
        return {package_name(line[8:]) for line in output.splitlines() if line}

    def identity(self) -> dict:
        props = {}
        for key in (
            "ro.product.manufacturer",
            "ro.product.model",
            "ro.build.fingerprint",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.build.characteristics",
        ):
            props[key] = self.shell("getprop", key)
        if "watch" not in props["ro.build.characteristics"].split(","):
            raise SafetyError("Target does not identify as an Android watch")
        if props["ro.product.manufacturer"].lower() != "samsung":
            raise SafetyError("This release supports Samsung Wear OS inventory only")
        serial = self.shell("getprop", "ro.serialno")
        fingerprint = props["ro.build.fingerprint"]
        if not serial or serial.lower() in {"unknown", "null"} or not fingerprint:
            raise SafetyError("Cannot reliably bind backup to physical watch and firmware")
        props["device_token"] = hashlib.sha256(serial.encode()).hexdigest()
        features = self.shell("pm", "list", "features")
        props["telephony_feature"] = "feature:android.hardware.telephony" in features.splitlines()
        props["lte_note"] = "Feature declaration only; eSIM provisioning and calls not verified"
        return props

    def details(self, package: str) -> str:
        return self.shell("dumpsys", "package", package_name(package))

    def state(self, package: str) -> int:
        text = self.details(package)
        match = re.search(r"User 0:([^\r\n]*)", text)
        state = re.search(r"\benabled=([0-4])\b", match[1]) if match else None
        if not state or not re.search(r"\binstalled=true\b", match[1]):
            raise SafetyError("Cannot parse installed user-0 enabled state; refusing to guess")
        return int(state[1])

    def set_state(self, package: str, state: int) -> str:
        verbs = {0: "default-state", 1: "enable", 3: "disable-user"}
        if state not in verbs:
            raise SafetyError("Unsupported state transition")
        return self.shell("pm", verbs[state], "--user", "0", package_name(package))
