"""Conservative classification; names are never evidence of safe removal."""

import json
import re
from importlib.resources import files

from .adb import SafetyError, package_name
from .protection import protect
from .telemetry import REVIEW_CATALOG

CATALOG = json.loads(files("cleanmywatch").joinpath("profiles.json").read_text(encoding="utf-8"))

# Exact opt-in exceptions, never a blanket permission for system packages.
EXPERIMENTAL_SYSTEM = frozenset(
    {
        "com.sec.android.diagmonagent",
        "com.android.adservices.api",
        "com.samsung.android.gallery.watch",
        "com.samsung.android.app.reminder",
    }
)


def classification(package: str) -> dict:
    if package in CATALOG["packages"]:
        action = (
            "protected"
            if package in {"com.sec.android.diagmonagent", "com.android.adservices.api"}
            else "review only"
        )
        return {"package": package, **CATALOG["packages"][package], "action": action}
    if package in REVIEW_CATALOG:
        item = REVIEW_CATALOG[package]
        return dict(
            package=package,
            purpose=item["purpose"],
            category=item["category"],
            confidence=item["confidence"],
            evidence=item["source"],
            dependencies="Not established on watch firmware; protected",
            consequences="Unknown; may affect essential services",
            reversibility="No change permitted",
            tested_firmware=[],
            action="protected",
        )
    # These categories are protective hints, not a complete dependency map.
    if re.search(r"phone|telephony|telecom|euicc|esim|emergency|ims|ril", package):
        category = "LTE / modem / emergency (protected hint)"
    elif re.search(r"health|sensor|fitness", package):
        category = "Health and sensors (protected hint)"
    elif re.search(r"wearable|companion|accessory|notification", package):
        category = "Pairing / notifications (protected hint)"
    elif package.startswith(("com.google.", "com.android.", "android")):
        category = "Android / Google services (protected; exact role unverified)"
    elif package.startswith("com.samsung."):
        category = "Samsung services (protected; exact role unverified)"
    else:
        category = "Unknown / needs verification"
    return dict(
        package=package,
        purpose="Exact purpose unverified",
        category=category,
        confidence="low",
        evidence="Package namespace/name only; insufficient for modification",
        dependencies="Unknown",
        consequences="May break essential watch functions",
        reversibility="No change permitted",
        tested_firmware=[],
        action="protected",
    )


def eligible(adb, package: str, experimental_system: bool = False) -> None:
    package_name(package)
    protect(package)
    if package not in CATALOG["packages"]:
        raise SafetyError("Unknown/core package: modifications are prohibited")
    if (
        package in {"com.sec.android.diagmonagent", "com.android.adservices.api"}
        and not experimental_system
    ):
        raise SafetyError("Diagnostics/advertising package requires experimental-system opt-in")
    info = adb.details(package)
    flags = re.search(r"^\s*(?:pkgFlags|flags)=\[([^\]]*)\]", info, re.MULTILINE)
    if experimental_system and package in EXPERIMENTAL_SYSTEM:
        if not flags or not re.search(
            r"\bcodePath=/(?:system|product|system_ext|data/app|apex)/", info
        ):
            raise SafetyError("Unrecognized experimental package metadata")
        if re.search(r"^\s*libraryNames=", info, re.MULTILINE):
            raise SafetyError("Shared-library provider requires separate dependency review")
        return
    if not flags or any(flag in flags[1].split() for flag in ("SYSTEM", "UPDATED_SYSTEM_APP")):
        raise SafetyError("System/preloaded or unrecognized package flags; protected")
    if not re.search(r"\bcodePath=/data/app/", info):
        raise SafetyError("Only user-installed /data/app optional apps may be changed")


def snapshot(adb) -> dict:
    before = adb.identity()
    packages = sorted(adb.packages())
    if not packages:
        raise SafetyError("Empty inventory; stopping")
    disabled = sorted(adb.packages(disabled=True))
    if adb.identity() != before:
        raise SafetyError("Device or firmware changed during inventory")
    return dict(
        identity=before,
        packages=packages,
        disabled=disabled,
        classifications=[classification(p) for p in packages],
    )


def audit(adb) -> dict:
    report = snapshot(adb)
    commands = {
        "battery": ("dumpsys", "battery"),
        "power_management": ("dumpsys", "deviceidle"),
        "storage": ("df", "/data"),
        "private_dns_mode": ("settings", "get", "global", "private_dns_mode"),
        "wifi_on": ("settings", "get", "global", "wifi_on"),
    }
    report["local_diagnostics"] = {}
    for label, command in commands.items():
        try:
            report["local_diagnostics"][label] = adb.shell(*command)
        except SafetyError:
            report["local_diagnostics"][label] = "Unavailable through non-root ADB"
    # Avoid enumerating unrelated apps' permissions/services or health data.
    report["optional_package_metadata"] = {
        p: adb.details(p) for p in report["packages"] if p in CATALOG["packages"]
    }
    if adb.identity() != report["identity"]:
        raise SafetyError("Device changed during audit")
    return report
