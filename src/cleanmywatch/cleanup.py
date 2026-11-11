"""Preference-first optional app review; no package is selected for mutation silently."""

from .adb import SafetyError
from .engine import plan
from .inventory import eligible

OPTIONAL_APPS = {
    "com.samsung.android.oneconnect": (
        "SmartThings",
        "Smart-home controls, tiles and shortcuts",
    ),
    "com.microsoft.office.outlook": (
        "Outlook",
        "Mail/calendar, related notifications, tiles and complications",
    ),
    "com.samsung.android.gallery.watch": (
        "Gallery",
        "Viewing/synchronizing images and image shortcuts",
    ),
    "com.samsung.android.wear.voicerecorder": (
        "Voice Recorder",
        "Recording, playback and recording synchronization",
    ),
    "com.samsung.android.app.reminder": (
        "Reminder",
        "Reminder notifications, tiles and synchronization",
    ),
    "com.samsung.sree": (
        "Samsung Global Goals",
        "Goals content and possible optional watch-face integrations",
    ),
}


def prepare(adb, keep):
    identity = adb.identity()
    installed = adb.packages()
    candidates = []
    ready = []
    for package, (label, consequence) in OPTIONAL_APPS.items():
        if package not in installed:
            continue
        retained = keep(package, label, consequence)
        item = {
            "package": package,
            "label": label,
            "consequence": consequence,
            "decision": "keep" if retained else "candidate",
            "executable": False,
        }
        if not retained:
            try:
                eligible(adb, package)
                ready.append(package)
                item["executable"] = True
            except SafetyError as exc:
                item["blocked_reason"] = str(exc)
                item["next_step"] = "Firmware-specific dependency review required; no guard bypass"
        candidates.append(item)
    proposed = plan(adb, "custom", ready)
    if adb.identity() != identity:
        raise SafetyError("Watch or firmware changed during cleanup preparation")
    return {
        "identity": identity,
        "candidates": candidates,
        "plan": proposed,
        "device_changes": [],
        "backup_requirement": "Recent successful Samsung backup before apply",
        "telemetry_eliminated": "NOT VERIFIED",
    }
