# Synthetic audit (not hardware evidence)

Model: SAMPLE-WATCH. Firmware: example/synthetic/build. No real watch was used.

| Package | Finding | Allowed action |
|---|---|---|
| android | Protected Android package | None |
| com.android.phone | Protected telephony hint | None |
| com.samsung.android.wearable.example | Protected pairing hint | None |
| com.spotify.music | Optional app candidate; verify user install and dependencies | Explicit review, preview and approval |
| org.example.unknown | Unknown | None |

Example preview: `com.spotify.music: state 0 → disabled-user (3)`. Restoration would return state 0 using `default-state`, never indiscriminately enable all disabled apps. Example outcome is illustrative only; no disable or restore has been performed on hardware.
