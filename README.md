# CleanMyWatch

Local-first Samsung Wear OS auditing, battery measurements, and reversible optional-app disabling.

**This library, code, tests, and documentation are AI generated. They have not received an independent security review. Version 0.1 is experimental. Read-only inventory has been tested on one Watch4 LTE; package changes and rollback have not been hardware-tested.**

Inspired by the backup / preview / approve / verify approach of [CleanYourTV](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md). Independently implemented; no TV package lists or scripts are used.

## What works in this release

- Explicit ADB device selection, wireless pairing and connection, Samsung Android watch detection.
- Read-only package inventory and classification; local JSON and Markdown audit reports.
- Dry-run profiles, exact previous-state snapshots, per-app approval, write-ahead recovery journals.
- Preference-first review of Outlook, Gallery, Voice Recorder, Reminder and Samsung Global Goals, plus Spotify and Strava. Disable/restore is restricted to **separately user-installed catalog apps**, after local dependency review. System/preloaded variants remain blocked.
- Read-only battery baseline/comparison and manual optimization guidance.
- Offline DNS CSV analysis and optional AdGuard-format export from your own evidence-backed rules.
- Evidence-labelled diagnostics review and explicit post-change package-state verification.
- Rich keyboard menu: `cleanmywatch tui --device WATCH_SELECTOR`.

**Samsung/Google diagnostics and telemetry debloating is deliberately unavailable until package dependencies and exact firmware behavior are validated.** Conservative, balanced and aggressive currently expose the same optional-app catalog. No profile selects any app automatically. Custom selection is limited to that catalog. Unknown packages stay protected. This release does not provide a one-click system debloater.

No root, uninstall, bootloader changes, modem commands, silent settings writes, analytics, network scanning, or battery-life guarantees. LTE/eSIM, emergency services, Health, payment services, pairing, launcher/watch faces, notifications, updates, and all other system packages are protected by the default-deny policy.

**Play Store and Google Play Services stay enabled.** Normal app installation and updates are preserved. Core-package guards remain in effect even if a profile is edited incorrectly.

## Watches and testing

| Watch family | Intended scope | Physical testing in this project |
|---|---|---|
| Galaxy Watch4 40mm LTE | Primary target | Read-only identification and audit passed; **disable/restore untested** |
| Other Watch4 / Watch4 Classic variants | Primary Samsung Wear OS target; exact model/firmware detected | **Not yet tested** |
| Other Samsung watches running Wear OS | Experimental read-only inventory; no firmware safety claim | **Not yet tested** |
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

Start with `cleanmywatch cleanup --device WATCH_SELECTOR`. It asks which apps to **keep**, defaults to keeping every app, explains consequences, and saves a dry-run proposal. Preloaded variants are clearly marked blocked; a candidate is not an executable change. Each user supplies their own preferences before any apply approval.

Only choose an app you do not use, after inspecting its local metadata, tiles, complications and role on your firmware. Sync any app data first. Example for a separately installed Spotify:

```text
cleanmywatch plan --device WATCH_SELECTOR --profile conservative --package com.spotify.music
# Prints a dry-run preview and a local .cleanmywatch/plans/....json path.
cleanmywatch apply --device WATCH_SELECTOR PLAN_JSON_PATH
```

Apply previews again, requires `BACKUP VERIFIED`, then requires the exact phrase `DISABLE com.spotify.music`. A generated ADB snapshot does **not** satisfy the Samsung backup requirement. There is no `--yes` bypass. Snapshot and journal files must be saved successfully before any change. Each disable is verified with package state and disabled-package inventory.

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

This read-only command checks a small documented catalog, reports exact installed identifiers and states locally, and saves private metadata for review. Samsung's package inventory identifies DiagMonAgent; community scripts supply additional, explicitly low-confidence candidates. Neither source establishes safe removal on current watch firmware. Catalog presence is not proof that data is being sent. System diagnostics remain protected.

Review diagnostic-data consent in watch/Galaxy Wearable privacy or legal settings where available; menus vary. The toolkit does not guess undocumented settings keys. Review app/account consents separately and retain essential Health synchronization. No package-state check or DNS blocklist can certify that every telemetry path has been removed. See [comparison and limits](docs/REFERENCE-COMPARISON.md).

**A package-state backup cannot restore deleted data, repair a boot loop or recreate an eSIM. No tool can promise that nothing will go wrong.** ADB rollback needs an accessible, authorized watch. Do not factory-reset to solve an optional-app issue before trying restore.

## Battery and DNS

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
