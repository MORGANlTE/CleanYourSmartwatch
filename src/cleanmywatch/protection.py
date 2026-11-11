"""Core package boundaries remain enforced even if a catalog is edited incorrectly."""

from .adb import SafetyError

CORE = {
    "android",
    "com.android.vending",
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.android.phone",
    "com.android.server.telecom",
}
CORE_PREFIXES = ("com.android.providers.", "com.google.android.overlay.")
CORE_TERMS = (
    "systemui",
    "launcher",
    "watchface",
    "bluetooth",
    "telephony",
    "euicc",
    "esim",
    "emergency",
    "shealth",
    "health",
    "sensor",
    "wallet",
    "samsungpay",
    "companion",
    "wearable.app",
    "watchmanager",
    "permissioncontroller",
    "packageinstaller",
    "inputmethod",
    "settings",
    "fota",
    "updater",
)


def protect(package):
    if (
        package in CORE
        or package.startswith(CORE_PREFIXES)
        or any(term in package.lower() for term in CORE_TERMS)
    ):
        raise SafetyError(
            "Protected essential package; store, health, safety and core services stay enabled"
        )
