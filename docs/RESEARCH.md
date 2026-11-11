# Research notes and release scope

These are evidence sources, not a safe-to-disable authority. Individual hardware test details remain private.

- [Samsung connection guide](https://developer.samsung.com/health/sensor/guide/connect-watch.html): watch developer options, five taps, wireless pairing and connection. Firmware UI varies.
- [Google Wear OS Wi-Fi debugging](https://developer.android.com/training/wearables/get-started/debug-wifi) and [ADB command reference](https://developer.android.com/tools/adb): supported non-root inventory and device targeting. A package manager command's existence does not guarantee a safe watch configuration.
- [Samsung backup guide](https://www.samsung.com/us/support/answer/ANS10013461/): phone-side backup status and Smart Switch. Coverage is limited and firmware-dependent.
- [CleanYourTV prompt](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md): workflow inspiration (preview, backup, approval, verify). Independently implemented watch workflow; no TV launcher/disable lists copied.
- [doubleangels/GalaxyWatch4](https://github.com/doubleangels/GalaxyWatch4): archived third-party Watch4 ADB debloat project. Its existence is not dependency evidence for current builds.
- [Vermaarp/galaxy-watch-debloat-toolkit](https://github.com/Vermaarp/galaxy-watch-debloat-toolkit): third-party toolkit advertises disabling and power-management overrides. Its claimed reversibility does not establish safety. Lists and overrides are not imported here.
- Official publisher listings for [Spotify](https://play.google.com/store/apps/details?id=com.spotify.music) and [Strava](https://play.google.com/store/apps/details?id=com.strava) support app identities and Wear OS availability. They do not validate disabling on a particular firmware. Strava documents workout tiles/complications; loss of optional integrations is a material consequence.

No complete, authoritative firmware-specific dependency graph was established for Samsung Health, Galaxy Wearable pairing, Play Services, One UI Watch or LTE components. Therefore all system packages and all unknown packages are protected. Names only provide explicitly low-confidence audit hints. No system telemetry-removal, aggressive power tuning or verified zero-telemetry claim is made.

[Samsung's package inventory](https://docs.samsungknox.com/CCMode/G970U1_P.pdf) identifies `com.sec.android.diagmonagent` as DiagMonAgent on a phone. This is publisher evidence of identity, not watch dependency or disable/restore evidence. The telemetry review preserves that distinction and never automatically disables a candidate.

## Phase status

1. Inventory/detection: implemented, mocked tests; read-only identification and audit succeeded on one Watch4 LTE. Exact device/firmware details remain private. Other devices pending.
2. Classification: protected hints, evidence-labelled diagnostics, and an expanded optional-app catalog; preloaded firmware dependency verification remains pending.
3. Preference-first cleanup, preview/disable/rollback and post-change state verification: implemented for user-installed catalog apps; preloaded candidates remain blocked and hardware change/restore validation is pending.
4. Network: offline user-log analysis and manual guidance; no endpoint list or live interception.
5. Battery: samples/comparison and manual recommendations; no measured improvement.
6. CLI/Rich menu, tests, CI and documentation: implemented; terminal rendering and hardware behavior need maintainer review before a stable release.

This is a usable, deliberately limited experimental release, not completion of unverified system debloating. Expand only with evidence and real disable/restore/function checks.
