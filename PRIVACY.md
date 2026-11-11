# Privacy policy

CleanMyWatch has no analytics, telemetry collection, project backend or maintainer upload. Host CLI commands communicate with the explicitly selected watch through ADB. Optional DNS configuration makes the watch send applicable DNS queries to AdGuard; it is a separate external data recipient, not the project maintainer. Companion-phone and app-managed DNS paths may differ. Installing dependencies uses package indexes; GitHub publishing and AI chat use those services separately.

Private local `.cleanmywatch/` files can include model, firmware, package inventory, optional app permissions/services metadata, battery state, device-id hash, configuration notes, previous DNS mode/hostname, DNS session journals, selected network-validation summaries, command output and operation times. No raw hardware serial, connection address, pairing code, health measurements, accounts, Wi-Fi credentials, IMEI or eSIM identifiers are intentionally persisted by the toolkit. Third-party ADB manages its own pairing keys/known devices outside this project; those are not copied into reports.

Reports are **private**, not automatically anonymized for sharing. Hashes can identify the same device over time. Package dumps and diagnostic text may contain unexpected identifiers on future firmware. The toolkit does not dump all getprop/settings, account services, Health data or logcat. Remove private files after you no longer need rollback; keep a secure private recovery copy first. Deleting `.cleanmywatch/` destroys local history/backups, not installed app state or ADB authorizations.

Synthetic examples contain no real watch data. For public reports, write a fresh minimal description manually and omit device hashes, serials, local addresses, user paths, raw diagnostics and personal activity. There is no automatic safe-share exporter.

The operating system or a cloud backup service may sync your project directory. The toolkit cannot control that; store private state in an appropriate directory via `CLEANMYWATCH_HOME` if necessary. Keep one state directory per operational workflow, and never run concurrent toolkits in different directories against the same watch. Directory access controls govern confidentiality.

Public documentation must describe supported platforms generically. Do not copy an individual's host setup, exact model code, firmware, activity dates, serial, network details, or personal test record from a private conversation into public files. Compatibility records use broad device families by default. Exact-build test evidence stays private unless its owner explicitly consents to publication.

If you invoke Codex/Claude Code, their services may receive private content you let the assistant read. Read-only ADB access is not permission to publish its results. Review agent actions and limit access to the data needed.
