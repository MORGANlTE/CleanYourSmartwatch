# Compatibility and evidence

Profile schema 1. `tested_firmware` is intentionally empty.

| Family | Detection / design target | Change + restore validation |
|---|---|---|
| Galaxy Watch4 LTE | Read-only identification and audit passed; exact device details remain private | Not performed |
| Other Galaxy Watch4, Watch4 Classic (BT / LTE) | Primary Wear OS target | Not performed |
| Other Samsung Wear OS models | Experimental; model and firmware must be read | Not performed |
| Samsung Tizen | Rejected / unsupported | Not applicable |
| Non-Samsung or non-watch Android | Rejected | Not applicable |

Pairing, connection, Samsung/watch identification and package inventory/audit succeeded on one Watch4 LTE. Exact model codes, firmware and individual activity dates are intentionally omitted. No app was disabled or restored. Catalog `tested_firmware` remains empty because no modification has been validated.

Wear OS 3 and newer firmware differ in pairing UI, package versions and dependency behavior. Marketing model names do not establish firmware compatibility. ADB output parsers and the default-deny catalog are also software-tested using synthetic fixtures; no fixture is a real-device test report. No LTE/eSIM/emergency functionality has been physically validated by this project.

## Adding a verified record

Keep exact model codes, firmware, app versions, state enums and activity dates in a private test record. Publish only a broad family and clearly separated test outcomes by default. Publishing any exact-build record requires separate explicit consent after reviewing the proposed text. Never include addresses, device hashes, usernames, timestamps of personal activity or raw dumps.

Mark read-only identification, change validation, rollback validation and functional checks separately. Do not report the watch as fully tested if only one step succeeded. Never test by dialing an emergency number. A successful report for one build does not authorize a different firmware.
