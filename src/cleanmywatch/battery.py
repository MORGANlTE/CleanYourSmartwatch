"""Read-only battery sampling with explicit measurement limitations."""

import re
from datetime import datetime

from .adb import SafetyError
from .storage import now

GUIDANCE = """Change these on the watch, one at a time, and record the old value:
* Display: Always On Display, brightness and screen timeout.
* Galaxy Wearable: reduce notifications from apps you do not need.
* Keep LTE, location and sensors available when needed for safety, navigation and health.
* Compare similar daily use and signal coverage with Wi-Fi debugging OFF between samples.
* Sync workouts before disabling optional workout apps.
No undocumented settings, Doze overrides, app-ops or background limits are written.
DNS filters can disrupt sign-in, updates and health sync; use an allowlist and test.
"""


def sample(adb, config: str) -> dict:
    identity = adb.identity()
    text = adb.shell("dumpsys", "battery")
    values = {}
    for key in ("level", "scale", "status"):
        match = re.search(rf"^\s*{key}:\s*(\d+)\s*$", text, re.MULTILINE)
        if not match:
            raise SafetyError("Battery measurement unavailable")
        values[key] = int(match[1])
    if not values["scale"] or values["level"] > values["scale"]:
        raise SafetyError("Invalid battery scale or level")
    powered = bool(re.search(r"^\s*(?:AC|USB|Wireless|Dock) powered:\s*true", text, re.MULTILINE))
    if adb.identity() != identity:
        raise SafetyError("Device changed during battery sample")
    return dict(
        identity=identity,
        at=now(),
        percent=100 * values["level"] / values["scale"],
        charging=powered or values["status"] in (2, 5),
        configuration=config,
        limitations="Coarse battery percentage; workload, coverage and debugging affect results",
    )


def compare(before: dict, after: dict) -> dict:
    if before["identity"] != after["identity"]:
        raise SafetyError("Battery samples belong to different devices/firmware")
    hours = (
        datetime.fromisoformat(after["at"]) - datetime.fromisoformat(before["at"])
    ).total_seconds() / 3600
    if hours <= 0:
        raise SafetyError("Samples must be in chronological order")
    change = before["percent"] - after["percent"]
    valid = not (before["charging"] or after["charging"] or change < 0)
    return dict(
        duration_hours=hours,
        percentage_points_used=change,
        estimated_points_per_hour=change / hours if valid else None,
        before_configuration=before["configuration"],
        after_configuration=after["configuration"],
        limitation="Intermediate charging is not detectable. Short tests and changed workloads are unreliable.",
    )
