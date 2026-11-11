# Privacy controls while keeping fitness features

The target is less optional diagnostics, advertising and unwanted app activity. This toolkit cannot make a connected watch untrackable. Samsung Health, Google Play services, the companion phone, carrier and cloud accounts still have their own data paths. Disabling unrelated apps does not anonymize fitness synchronization.

## Keep fitness working

Keep Samsung Health, Health Monitor, Android Health Connect, Google Health Services, sensors, location services, Bluetooth, companion/pairing services, phone/LTE/eSIM/emergency services, payments, the active watch face, updates and Play services enabled. Do not deny their network access or broadly block Samsung/Google domains. No health records are read or deleted by these controls.

Choose separately whether you want cloud backup/sync for Health. Local viewing and cloud synchronization are different privacy choices; preserving the apps does not prove either works after changes. Check a new workout appears on the phone, heart-rate history is visible, notifications arrive and normal calling still works. Do not make emergency test calls.

## Optional applications

`cleanup` asks which applications to keep, with KEEP as the default. Gallery, Reminder and SmartThings have separate decisions. Gallery disabling removes that application's photo-viewing/sync functionality; it does not intentionally delete pictures. Reminder disabling stops reminder alerts; SmartThings disabling stops smart-home controls. Music, Maps, weather, alarms, calculator, voice assistants and Buds controls are not automatically removed.

Default profiles still refuse system/preloaded variants. A few exact identifiers can be selected with `--experimental-system`, after metadata review and explicit app approval. The switch is not blanket permission for all system packages.

```text
cleanmywatch plan --device WATCH_SELECTOR --profile custom --experimental-system --package com.samsung.android.gallery.watch
cleanmywatch apply --device WATCH_SELECTOR PLAN_JSON_PATH
```

## Experimental diagnostics and advertising controls

Two exact opt-in candidates are available:

| Package | Intended effect | Limits and consequences |
|---|---|---|
| `com.sec.android.diagmonagent` | Disable Samsung DiagMonAgent package for user 0 | Diagnostic reporting/support functionality can stop. It may share the system UID. Firmware dependencies and functional safety are not certified. |
| `com.android.adservices.api` | Disable the Android advertising API APK for user 0 | Advertising API consumers can fail. This leaves the APEX module and SDK sandbox installed. It is not a universal ad blocker. |

Neither is selected automatically. Package presence does not establish current transmissions. No Health logger, system UI logger, modem logger, Knox security component or unknown package is automatically disabled. A general third-party debloat list is not a dependency graph.

```text
cleanmywatch plan --device WATCH_SELECTOR --profile custom --experimental-system --package com.sec.android.diagmonagent
cleanmywatch apply --device WATCH_SELECTOR PLAN_JSON_PATH
cleanmywatch verify --device WATCH_SELECTOR --session SESSION_JSON_PATH
cleanmywatch restore --device WATCH_SELECTOR --session SESSION_JSON_PATH
```

Use one package per initial session. The plan binds to the physical watch and firmware. Disable uses `pm disable-user`, never uninstall. A durable journal records prior state 0/1; restoration uses `default-state`/`enable` respectively. No data/eSIM recovery is promised if ADB is inaccessible.

## Consent settings

Review **Send diagnostic data** in watch Settings or Galaxy Wearable. Samsung documents Watch settings → Watch information → Legal information → Sending diagnostic data to Samsung; paths vary by firmware. Turn it off if offered. Review Google usage/diagnostics, Samsung customization and account/app consent separately. These toggles are not automatically changed: no undocumented settings keys are guessed. `send_action_app_error` controls a crash dialog's Report button in AOSP and is not proof of Samsung telemetry consent.

## Active AdGuard Private DNS

First ask whether the router/phone already uses Pi-hole, AdGuard Home, NextDNS, DNS-based VPN routing or a fake-IP proxy. Strict Private DNS may bypass those rules. The provider receives DNS queries; this is a trust choice, not anonymity.

```text
cleanmywatch dns-plan --device WATCH_SELECTOR
cleanmywatch dns-apply --device WATCH_SELECTOR DNS_PLAN_JSON_PATH
cleanmywatch dns-status --device WATCH_SELECTOR
cleanmywatch dns-restore --device WATCH_SELECTOR DNS_SESSION_JSON_PATH
```

The built-in provider is `dns.adguard-dns.com`. The tool saves exact old mode and hostname before changing either value, including absent settings. Apply sets the hostname first and strict mode second. Restore reverses the order and deletes settings that were originally absent. Recovery records are in `.cleanmywatch/dns-sessions/`, separately from package sessions; package `restore --all-sessions` does not restore DNS.

`dns-status` separates configured values from observed per-network TLS validation. A validated Wi-Fi resolver does not establish Bluetooth companion-proxy or LTE coverage. If strict DNS cannot validate, that transport may lose internet access. Restore DNS promptly if connectivity, Health sync, sign-in, updates or payments regress. Do not claim all ads/trackers were blocked from a settings readback alone. Direct-IP traffic, app-managed DNS, shared content/ad domains and phone-originated traffic can bypass this layer; YouTube-style same-domain ads are not reliably blocked.

## Backup choice and recovery

Samsung backup remains the default requirement. A user who explicitly accepts no Samsung backup can run `apply --skip-backup`, then type `SKIP BACKUP`. This is recorded as a waiver, never as a verified backup. Per-package approval and local recovery snapshots/journals remain mandatory. Do not enter `BACKUP VERIFIED` unless a real backup was verified.

Before calling privacy protection complete, compare network evidence on Wi-Fi, LTE and companion-phone paths, test fitness and other essential features, reconnect after a normal reboot and re-run verification. Local records must never be committed. Disable Wireless debugging and ADB debugging when finished.

## Sources and reference decisions

- [CleanYourTV DNS workflow](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md): adopted the opt-in Private DNS approach, with exact prior-state rollback rather than assuming opportunistic was the previous mode. TV package lists and launcher changes do not apply to watches.
- [AdGuard public DNS](https://adguard-dns.io/en/public-dns.html): provider hostname and filtering purpose.
- [Android AdServices architecture](https://source.android.com/docs/core/ota/modular-system/adservices): APK/APEX and advertising API role; not a watch-disable safety certification.
- [Samsung diagnostics consent guidance](https://us.community.samsung.com/t5/Tips/How-to-cancel-sending-diagnostic-data/td-p/2569130): documented watch consent route, with firmware caveats.
- [Bloatbuster Samsung candidates](https://github.com/thongtech/bloatbuster/blob/main/src/data/packages/bloatware/samsung.ts) and [Android candidates](https://github.com/thongtech/bloatbuster/blob/main/src/data/packages/bloatware/android.ts): names for review, not automatic permission. Lists include packages this project protects. No database/code is copied wholesale.
- [Older Watch4 script](https://github.com/diegomdrs/script-debloat-galaxy-watch-4/blob/main/debloat.sh): reviewed as data only. Its phone, telephony-provider, payment and watch-face removals conflict with preserving essential watch functions. It is not executed.
