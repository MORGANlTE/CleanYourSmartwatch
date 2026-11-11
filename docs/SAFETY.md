# Safety and recovery

There is no guarantee of harmlessness. Read-only inventory has been tested on one Watch4 LTE; package state readbacks do not certify physical-watch functional safety or rollback. Use one optional app per session and review local metadata and dependencies before approval. A non-system flag is a guard, not proof that an app is unnecessary.

## Two different backups

**Samsung backup**: app data/settings supported by Galaxy Wearable / Smart Switch, verified on the paired phone. Some data is excluded. Check Health/workout sync separately; eSIM recovery may require your carrier. There is no full non-root watch image backup here.

**CleanMyWatch state backup**: local package inventory, disabled list, selected optional-app package metadata, identity hash, model and firmware. Each session saves the exact prior user-0 enabled enum, commands' output, progress and errors. It can undo only changes made by this toolkit while ADB remains authorized and reachable. It does not restore settings changed manually or by other software.

Only states 0 (default) and 1 (explicit enabled) may be disabled. Existing states 2/3/4 are refused and never broadly re-enabled. Restoration uses `pm default-state --user 0 PACKAGE` or `pm enable --user 0 PACKAGE` respectively. Verify with `dumpsys package PACKAGE`, User 0 `enabled=`, and `pm list packages -d --user 0`.

## Before applying

Keep `.cleanmywatch/` in this private checkout; make a private external copy of session journals and recovery instructions. Windows file permissions inherit the containing directory: use a private account folder and appropriate ACLs. The directory may be backed up or synchronized by your OS/cloud provider. A toolkit with no uploads cannot prevent that.

Plans bind to a hash of the physical hardware serial and exact firmware. No raw hardware serial or watch address is saved by the package. Never publish the token; a hash remains a persistent identifier. Preflight rechecks all package states. Device identity and state are rechecked around each operation. These checks reduce wrong-target risk but cannot make several ADB calls an atomic hardware transaction.

Apply requires interactive backup confirmation or an explicit `--skip-backup` waiver (`SKIP BACKUP`), and individual exact app approval. A waiver is recorded honestly and never described as a successful Samsung backup. A fresh inventory and durable journal are saved before mutation. Status is written as `pending` before issuing a command, so a dropped connection or interrupted process can be reconciled later. Successful exit code alone does not count: disabled enum and list are checked. Errors stop further changes. There is no automatic rollback that could hide a failed recovery.

The local exclusive lock prevents two normal operations using the same state directory. Always use one checkout/state directory for a watch, never simultaneous raw ADB modifications. After a killed process, inspect sessions and confirm no toolkit process is running before deleting `.cleanmywatch/operation.lock` manually. Restore interrupted sessions before new work. Do not delete journals to clear an error.

## Verify after each session

Test Home, settings, watch face and tiles; phone reconnect and notification delivery; Bluetooth and Wi-Fi; normal calls and LTE data where applicable; Health, sensor/workout sync; Wallet/payment availability and updates. Check SOS/emergency settings without placing an emergency test call. User confirmation is necessary: package manager output cannot prove these features work.

If you reboot manually, wait at least 15 seconds after changes, then check states again after reconnecting. Firmware may re-enable an app. Do not repeatedly disable it automatically; record the behavior and stop. ADB and Wi-Fi debugging add power load; disable debugging before battery comparisons.

## Restore

```text
cleanmywatch history
cleanmywatch restore --device WATCH_SELECTOR --last
cleanmywatch restore --device WATCH_SELECTOR --session SESSION_JSON_PATH --package com.spotify.music
cleanmywatch restore --device WATCH_SELECTOR --all-sessions
cleanmywatch recovery --session SESSION_JSON_PATH
```

Restore rechecks identity, current package metadata and states; prompts; writes `restoring` before the command; verifies exact prior enum. It can resume after interruption, including a command that succeeded before its final journal update. It never executes an arbitrary command from a JSON file. Treat all state files as private trusted records; they are validated but not cryptographically signed. Do not share a writable state directory with other users.

All-sessions processes sessions newest first and stops at the first failure or device mismatch. A mixed-device directory therefore requires explicit session selection. Catalog removal in a future release may require retaining this version to restore; preserve this checkout/environment with backups.

If firmware changed, **automatic apply and restore refuse**. Do not alter the journal's identity to bypass this. Verify the original physical watch and exact app role again, and review the printed `recovery` command with someone who understands the updated firmware. Those commands require a deliberate manual identity check.

If ADB is unavailable, try re-enabling the app through the watch's Settings UI if that firmware offers it. A non-booting/unreachable device may need vendor support or a factory reset, with potential data/eSIM loss. Do not promise recovery from these snapshots. Never experiment on a watch you rely on as your only emergency or medical device.

## Experimental privacy controls

See [privacy controls](PRIVACY-CONTROLS.md). `--experimental-system` permits only exact reviewed exceptions, never Health/core/unknown packages. Shared system UIDs and APEX-hosted APKs are material risks. DNS changes use separate write-ahead journals, block additional applies until restored, bind to physical watch and firmware, and restore missing values by deletion. Verify each network transport; strict DNS can make a transport unusable if validation fails. Package restore does not undo DNS; use `dns-restore --session DNS_SESSION_JSON_PATH`.
