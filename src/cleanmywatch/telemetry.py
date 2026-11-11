"""Evidence-labelled diagnostics review. Discovery is separate from disable permission."""

from .adb import SafetyError

REVIEW_CATALOG = {
    "com.sec.android.diagmonagent": {
        "purpose": "DiagMonAgent diagnostic component",
        "category": "diagnostics",
        "confidence": "Publisher identifies package; watch dependencies not established",
        "source": "https://docs.samsungknox.com/CCMode/G970U1_P.pdf",
        "source_scope": "Samsung phone package inventory, not a watch safety test",
    },
    "com.samsung.android.diagmonagent": {
        "purpose": "Diagnostics candidate named by third-party toolkit",
        "category": "diagnostics candidate",
        "confidence": "Low; alternate namespace must not be assumed equivalent",
        "source": "https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/watch_optimizer.sh",
        "source_scope": "Third-party package list; not authoritative dependency evidence",
    },
    "com.google.android.gms.feedback": {
        "purpose": "Feedback/crash reporting candidate named by third-party toolkit",
        "category": "crash-reporting candidate",
        "confidence": "Low; installed package and firmware role must be verified",
        "source": "https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/watch_optimizer.sh",
        "source_scope": "Third-party package list; not authoritative dependency evidence",
    },
    "com.samsung.android.wear.shealth.service.logger": {
        "purpose": "Health-related logger candidate; protect health dependencies",
        "category": "health diagnostics candidate",
        "confidence": "Low; health dependencies unknown",
        "source": "https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/watch_optimizer.sh",
        "source_scope": "Third-party package list; health functionality must be preserved",
    },
    "com.google.android.apps.wearable.systemui.logging": {
        "purpose": "System UI logging candidate; protect system UI dependencies",
        "category": "system diagnostics candidate",
        "confidence": "Low; system dependencies unknown",
        "source": "https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/watch_optimizer.sh",
        "source_scope": "Third-party package list; system functionality must be preserved",
    },
}


def review(adb):
    identity = adb.identity()
    installed = adb.packages()
    findings = []
    for package, evidence in REVIEW_CATALOG.items():
        if package not in installed:
            continue
        findings.append(
            {
                "package": package,
                **evidence,
                "state": adb.state(package),
                "action": "protected by default; exact experimental opt-in exists for DiagMonAgent only; firmware functional safety unverified",
                "network_observation": "Not measured; package presence does not prove transmission",
                "metadata": adb.details(package),
            }
        )
    if adb.identity() != identity:
        raise SafetyError("Watch or firmware changed during diagnostics review")
    return {
        "identity": identity,
        "findings": findings,
        "device_changes": [],
        "coverage": "Small evidence-labelled catalog, not a complete telemetry inventory",
        "telemetry_eliminated": "NOT VERIFIED",
        "manual_guidance": (
            "Review Samsung diagnostic-data consent in the watch/Galaxy Wearable privacy or "
            "legal settings where offered. Record the previous value privately. Menu paths vary; "
            "no undocumented setting is written by this toolkit. Review app/account privacy "
            "consents separately; preserve essential health synchronization and safety features."
        ),
    }
