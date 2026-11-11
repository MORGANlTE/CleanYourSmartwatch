# Privacy implementation and maintainer handoff

These files are already placed in the local checkout. Review the diff and publish only public source, tests and documentation. Do not add `.cleanmywatch/` or private recovery files to Git.

## File placement

| Path from repository root | Change |
|---|---|
| `src/cleanmywatch/adb.py`, `tests/test_adb.py` | Parse actual installed user-0 state headers; reject ambiguous duplicate active headers, distinguish inactive factory copies of updated system apps, and ignore unrelated metadata mentions. |
| `src/cleanmywatch/dns.py` | New active AdGuard DNS plan/apply/status/restore; exact old values, per-key journal, identity checks, interrupted-session protection and drift rejection. |
| `src/cleanmywatch/cli.py` | `dns-plan`, `dns-apply`, `dns-status`, `dns-restore`; `plan --experimental-system`; honest opt-in `apply --skip-backup`. |
| `src/cleanmywatch/inventory.py` | Exact experimental system allowlist, default-deny behavior, metadata checks and shared-library-provider rejection. |
| `src/cleanmywatch/engine.py` | Carry explicit experimental opt-in through plan, disable and restore; existing package journal and verification remain in use. |
| `src/cleanmywatch/profiles.json` | Evidence/consequences for DiagMonAgent, advertising API APK and SmartThings; no automatic selections. |
| `src/cleanmywatch/cleanup.py` | Separate KEEP prompt for SmartThings; all keep prompts still default to yes. |
| `tests/test_dns.py` | Exact restore including missing/empty settings, interrupted write, wrong device, drift/tamper rejection and per-network validation parsing. |
| `tests/test_telemetry.py` | Experimental opt-in, exact restore and continued rejection of Health/core/unknown packages. |
| `docs/PRIVACY-CONTROLS.md` | User workflow, reference evaluation, consequences, fitness preservation and remaining limits. |
| `README.md`, `PROMPT.md`, `docs/SAFETY.md`, `docs/NETWORK.md`, `docs/RESEARCH.md`, `docs/REFERENCE-COMPARISON.md`, `docs/COMPATIBILITY.md`, `docs/SETUP.md`, `PRIVACY.md` | Align advertised behavior and assistant workflow with the new opt-in controls. |

No extra shell scripts, external APKs, VPN, root or third-party database downloads are required. Existing `tools/check_public_files.py` remains the public-data check; run it before publication. Private helpers used during a local watch session are not reusable public entry points.

## README wording

Describe the result as **optional-app cleanup, experimental diagnostics/advertising-package controls and opt-in DNS filtering**. State that default profiles select nothing and system exceptions require explicit opt-in. Do not claim all telemetry is removed, a connected watch cannot be tracked, no fitness data leaves the device, every connection uses AdGuard, or battery life has improved without measurements.

Explain that Health sync can intentionally transfer fitness data, while local history can remain useful without every optional cloud integration. Changes here preserve Health packages and permissions; actual sync and sensor function still require the user's test. Clarify Gallery's photo-viewing tradeoff before approval.

## Release checks

Run the test suite, Ruff and the public-file checker. Review new files too: the checker principally scans tracked/indexed files. Hardware state readback is not functional validation. Keep exact device/build records private; do not fill `tested_firmware` from a successful disable command alone.

Remaining work: independent code/security review; real disable/restore/reboot/function tests across firmware; consent UI discovery without guessing hidden keys; traffic evidence for Wi-Fi, LTE and companion-proxy paths; evidence-backed optional DNS rules and allowlist workflows. A public DNS resolver provides no per-user block log or custom allowlist, so custom exclusions require a user-managed provider or local DNS filter.
