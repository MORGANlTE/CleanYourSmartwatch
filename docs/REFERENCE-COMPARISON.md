# Reference repositories and deliberate differences

These projects are useful starting points for comparison, not firmware safety certifications. Their source is reviewed as data and never executed or downloaded into the toolkit.

| Behavior | Reference implementations | CleanMyWatch |
|---|---|---|
| Connection | ADB network connection | Modern pairing/connection ports; explicit target on each watch command |
| Inventory | Package lists and optional process/Doze snapshots | Private package classification and diagnostics review |
| Changes | Uninstall, disable or background restrictions, depending on script | User-installed catalog apps by default; exact experimental system exceptions with opt-in; per-app approval; Health/core/unknown packages protected |
| Backup | Package lists and generated restore helpers | Samsung backup confirmation by default or explicit honest waiver; fresh state snapshot and durable per-command journal |
| Restore | Re-enable apps or reset power policies to assumed defaults | Restore each exact prior enabled enum, verify it, and reconcile interrupted operations |
| Verification | Often checks command output | Independent enabled-state and disabled-list checks; explicit session verification after reconnect/reboot |
| Telemetry claim | Lists include diagnostics candidates | Source-labelled review; no complete removal or traffic-silence claim |
| Public privacy | Depends on script/log handling | Ignored local reports, generic documentation, staged-file and optional history scanning |

The [Watch4 removal script](https://github.com/doubleangels/galaxywatch4/blob/main/remove_bloat.sh) uninstalls packages including the media provider, payment application and Health Monitor, then installs local APKs. Those operations conflict with this project's preservation requirements. No such command is imported.

The [watch optimizer](https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/watch_optimizer.sh) includes components this project protects and lets users skip a package-list backup. A generated list is not a full data backup. The [background manager](https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/bg_process_manager.sh) resets standby/app-op/Doze state to assumed normal values rather than retaining every original setting. This toolkit does not implement those resets or restrictions. **Play Store and Play Services always remain protected so users retain normal app installation and updates.**

Identifying a background process is not evidence that it is unnecessary. Finding a package in a list is not proof of its role on a particular watch. Package-state verification establishes the recorded state, while privacy outcomes require separate consent and network evidence. Modem, companion-phone, account and cloud paths cannot be certified absent by non-root package inventory.

Active DNS now follows the opt-in resolver pattern in CleanYourTV, with exact prior-value rollback. Bloatbuster and the older diegomdrs Watch4 script were reviewed as candidate references, not executed or copied wholesale. See [reference decisions](PRIVACY-CONTROLS.md#sources-and-reference-decisions).
