# CleanMyWatch

Local-first Samsung Wear OS cleanup, experimental diagnostics controls, and opt-in ad/tracker DNS filtering, with exact-state rollback.

**This library, code, tests, and documentation are AI generated. They have not received an independent security review. Version 0.1 is experimental. Package-state checks do not establish firmware safety. Independent functional validation of changes, rollback, fitness sync and networking remains incomplete.**

Inspired by the backup / preview / approve / verify approach of [CleanYourTV](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md). Independently implemented; no TV package lists or scripts are used.

## What works in this release

- Explicit ADB device selection, wireless pairing and connection, Samsung Android watch detection.
- Read-only package inventory and classification; local JSON and Markdown audit reports.
- Dry-run profiles, exact previous-state snapshots, per-app approval, write-ahead recovery journals.
- Preference-first review of Outlook, Gallery, Voice Recorder, Reminder, SmartThings and Samsung Global Goals, plus explicit Spotify/Strava selection. User-installed catalog apps are eligible by default. A small exact system-package allowlist requires `--experimental-system`; Health/core/unknown packages remain protected.
- Read-only battery baseline/comparison and manual optimization guidance.
- Active opt-in AdGuard Private DNS with exact old-setting recovery and per-network TLS status, plus offline DNS CSV analysis and optional rule export.
- Evidence-labelled diagnostics review and explicit post-change package-state verification.
- Rich keyboard menu: `cleanmywatch tui --device WATCH_SELECTOR`.

**Privacy reduction is experimental, not a zero-telemetry or anonymity guarantee.** DiagMonAgent and the Android advertising API APK can be explicitly selected with `--experimental-system`. Gallery and Reminder system variants have the same opt-in requirement. Conservative, balanced and aggressive expose the same catalog and select nothing automatically. Fitness packages, phone sync, payments and essential services stay protected. See [privacy controls and fitness preservation](docs/PRIVACY-CONTROLS.md).

No root, uninstall, bootloader changes, modem commands, silent settings writes, analytics, network scanning, or battery-life guarantees. LTE/eSIM, emergency services, Health, payment services, pairing, launcher/watch faces, notifications, updates, and all system packages outside the exact experimental allowlist are protected by the default-deny policy.

**Play Store and Google Play Services stay enabled.** Normal app installation and updates are preserved. Core-package guards remain in effect even if a profile is edited incorrectly.

## Watches and testing

| Watch family | Intended scope | Physical testing in this project |
|---|---|---|
| Galaxy Watch4 40mm LTE | Primary target | Read-only identification and audit passed; **functional validation incomplete** |
| Other Watch4 / Watch4 Classic variants | Primary Samsung Wear OS target; exact model/firmware detected | **Not independently validated** |
| Other Samsung watches running Wear OS | Experimental read-only inventory; no firmware safety claim | **Not independently validated** |
| Samsung Tizen watches (Watch3, Active2, older) | Unsupported | None |
| Other Wear OS brands, Apple, Garmin, Fitbit | Unsupported in this release | None |

Mocked ADB tests verify software behavior; they do not prove that a real watch, LTE, emergency calls or restore works. See [compatibility records](docs/COMPATIBILITY.md). Never interpret “primary target” as “tested.”

## Before connecting or using an AI coding assistant

1. On the paired phone, check **Galaxy Wearable → Watch settings → Accounts and backup**. Follow the Smart Switch/backup options available on your firmware. Verify a recent successful timestamp; sync Health and workouts. Keep carrier/eSIM recovery information privately. Menu names and supported backup data vary.
2. On the watch, open **Settings → About watch → Software / Software information → Software version**, and tap it **five times**. Return to Settings → Developer options.
3. Enable **ADB debugging**, then **Wireless debugging** if available. Put the computer and watch on the same trusted Wi-Fi. Keep the watch awake while connecting. Do not expose debugging to the internet.
4. For modern firmware, open **Wireless debugging → Pair new device**. The pairing port and connection port are different. Pair locally, then use the main Wireless debugging screen's connection address:

```text
cleanmywatch pair WATCH_IP:PAIRING_PORT
# Enter the temporary pairing code into adb's local prompt.
cleanmywatch connect WATCH_IP:CONNECTION_PORT
cleanmywatch devices
cleanmywatch inspect --device WATCH_SELECTOR
cleanmywatch audit --device WATCH_SELECTOR
```

These are placeholders, not literal addresses. `WATCH_SELECTOR` is the exact first column from `devices`, usually the connection address. Ports can change. On older firmware with only “Debug over Wi-Fi,” use the address shown there and approve the watch prompt; do not force plaintext TCP mode on modern firmware. [Samsung's connection guide](https://developer.samsung.com/health/sensor/guide/connect-watch.html) and [Google's Wear OS guide](https://developer.android.com/training/wearables/get-started/debug-wifi) explain setup.

5. Open this repository in Codex or Claude Code. Copy [PROMPT.md](PROMPT.md) into the chat. Give connection details only in your private chat/terminal; never add them to source files. Ask it to audit first and show an exact plan. AI services receive anything you paste or allow an agent to read; the CLI itself sends nothing to them.

## Preview, approve, disable, restore

Start with `cleanmywatch cleanup --device WATCH_SELECTOR`. It asks which apps to **keep**, defaults to keeping every app, explains consequences, and saves a dry-run proposal. Preloaded variants are clearly marked blocked; a candidate is not an executable change. Each user supplies their own preferences before any apply approval. Gallery disabling stops viewing/syncing pictures in Gallery; Reminder and SmartThings lose their own alerts/controls. These apps are not assumed unwanted.

Only choose an app you do not use, after inspecting its local metadata, tiles, complications and role on your firmware. Sync any app data first. Example for a separately installed Spotify:

```text
cleanmywatch plan --device WATCH_SELECTOR --profile conservative --package com.spotify.music
# Prints a dry-run preview and a local .cleanmywatch/plans/....json path.
cleanmywatch apply --device WATCH_SELECTOR PLAN_JSON_PATH
```

Apply previews again, requires `BACKUP VERIFIED`, then requires the exact phrase `DISABLE com.spotify.music`. A generated ADB snapshot does **not** constitute a Samsung backup. If you explicitly choose to proceed without one, `apply --skip-backup` requires `SKIP BACKUP` and records an honest waiver. There is no `--yes` bypass and no bypass of per-package approval. Snapshot and journal files must be saved successfully before any change. Each disable is verified with package state and disabled-package inventory.

Test watch features after each session before making another change. Stop at any regression. Restore uses the exact original state: `default-state` for 0, `enable` for 1.

```text
cleanmywatch history
cleanmywatch restore --device WATCH_SELECTOR --last
cleanmywatch restore --device WATCH_SELECTOR --session SESSION_JSON_PATH --package com.spotify.music
cleanmywatch restore --device WATCH_SELECTOR --all-sessions
cleanmywatch recovery --session SESSION_JSON_PATH
cleanmywatch verify --device WATCH_SELECTOR --session SESSION_JSON_PATH
```

Restore prompts before execution, binds to the physical device and firmware, and can resume pending/interrupted changes. `recovery` prints validated manual commands for offline use. Save those instructions on another device before changes. Do not edit journals or overwrite an original backup. A changed firmware blocks automatic restore; consult [recovery limitations](docs/SAFETY.md).

`verify` independently re-reads each session package's user-0 state and the disabled-package list. Run it after applying, reconnecting or a deliberate reboot, and after restoring. Mismatches and interrupted operations fail verification. A match verifies recorded package states only; it does not prove functional health, network silence or zero telemetry.

## Diagnostics and telemetry review

```text
cleanmywatch telemetry --device WATCH_SELECTOR
```

This read-only command checks a small documented catalog, reports exact installed identifiers and states locally, and saves private metadata for review. Samsung's package inventory identifies DiagMonAgent; community scripts supply additional, explicitly low-confidence candidates. Neither source establishes safe removal on current watch firmware. Catalog presence is not proof that data is being sent. Diagnostics remain protected by default; the two exact experimental candidates require explicit selection, metadata review and individual approval. This does not establish that disabling them is harmless.

Review diagnostic-data consent in watch/Galaxy Wearable privacy or legal settings where available; menus vary. The toolkit does not guess undocumented settings keys. Review app/account consents separately and retain essential Health synchronization. No package-state check or DNS blocklist can certify that every telemetry path has been removed. See [comparison and limits](docs/REFERENCE-COMPARISON.md).

**A package-state backup cannot restore deleted data, repair a boot loop or recreate an eSIM. No tool can promise that nothing will go wrong.** ADB rollback needs an accessible, authorized watch. Do not factory-reset to solve an optional-app issue before trying restore.

## Active DNS filtering and experimental system controls

Check for an existing router/phone DNS filter before using strict Private DNS: it can bypass those rules. AdGuard receives DNS queries. It blocks known ad/tracker domains, not every ad, tracking method or same-domain video ad.

```text
cleanmywatch dns-plan --device WATCH_SELECTOR
cleanmywatch dns-apply --device WATCH_SELECTOR DNS_PLAN_JSON_PATH
cleanmywatch dns-status --device WATCH_SELECTOR
cleanmywatch dns-restore --device WATCH_SELECTOR DNS_SESSION_JSON_PATH

# One experimental package per initial session; every apply still prompts.
cleanmywatch plan --device WATCH_SELECTOR --profile custom --experimental-system --package com.sec.android.diagmonagent
cleanmywatch apply --device WATCH_SELECTOR PLAN_JSON_PATH
```

The other experimental diagnostics/advertising candidate is `com.android.adservices.api`. No APEX module is uninstalled. DNS sessions live separately in `.cleanmywatch/dns-sessions/`; package restore does not restore DNS. Status distinguishes configured settings from per-network encrypted-DNS validation. Wi-Fi validation does not prove LTE or companion-phone proxy coverage. Failed validation can break connectivity; restore the exact saved values if functions regress.

Keep Samsung Health, Health Monitor, Health Connect, sensors and phone pairing enabled. Cloud fitness synchronization can still transfer your fitness data by design. Test a new workout syncing to the phone before calling this working. [Details, consent toggles and limitations](docs/PRIVACY-CONTROLS.md) · [Maintainer file map](docs/REPO-CHANGES.md).

## Battery and offline DNS analysis

```text
cleanmywatch battery --device WATCH_SELECTOR --configuration "LTE auto; Wi-Fi on; AOD off"
# Later, after comparable use and no charging:
cleanmywatch battery --device WATCH_SELECTOR --configuration "LTE auto; Wi-Fi on; AOD off" --before BEFORE_JSON_PATH
cleanmywatch optimize
cleanmywatch network --log LOCAL_DNS_CSV_PATH
```

Battery comparisons report elapsed hours, percentage-point change and estimated drain/hour. Charging between samples cannot be ruled out automatically. Turn debugging off between measurements and use comparable workloads; no before/after improvement has been demonstrated.

DNS logs must be exported for the relevant client, with a `domain` CSV column. All endpoints default to unknown. Exact-domain user rules can supply `category`, `confidence` and `evidence` via `--rules RULES_JSON_PATH`; `--export-blocklist` exports only high-confidence advertising/analytics labels in AdGuard syntax. Mixed, essential and unknown domains are never exported. There is no built-in endpoint list. See [network guidance](docs/NETWORK.md).

## Finish securely

After functional checks, disable **Wireless debugging and ADB debugging** on the watch and forget/revoke the computer's debugging authorization. `adb disconnect` alone does not turn off the watch's listener. Confirm the toggles remain off after a normal reboot. This project does not automatically reboot or claim it has verified a closed port.

## Development

```text
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
```

[Safety / recovery](docs/SAFETY.md) · [Privacy policy](PRIVACY.md) · [Research and limits](docs/RESEARCH.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [MIT license](LICENSE)
