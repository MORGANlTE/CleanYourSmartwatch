# Installation and connection

## Windows 10/11 (PowerShell)

Install Python 3.11+ from python.org and official [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools). Extract Platform Tools to a private user-owned folder and add it to PATH. Git Bash/GitHub Desktop do not supply ADB. Open a new terminal and check `adb version` and `py --version`.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\cleanmywatch.exe devices
```

No environment activation is required. For an ADB binary outside PATH, set `$env:CLEANMYWATCH_ADB` to the full local path of `adb.exe` in this terminal. Do not commit that path. For every example command, use `.\.venv\Scripts\cleanmywatch.exe` instead of `cleanmywatch`.

## Linux

Install Python 3.11+ and its venv package using your distribution's package manager; install Google's current Linux Platform Tools to a user-owned folder and add it to PATH. Distribution ADB packages may be older and lack modern wireless pairing. No toolkit command needs sudo/root.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
adb version
cleanmywatch --help
```

Dependency installation uses PyPI/network access. After installation, the toolkit uses only local files and the selected local ADB target. Release dependencies use bounded ranges rather than a fully locked supply-chain environment.

## Backup before debugging

On the paired phone: Galaxy Wearable → Watch settings → Accounts and backup. Check “Last backed up,” follow Smart Switch options if present, and confirm successful recent completion. Firmware, phone vendor and region affect available controls; some versions back up automatically under conditions. Do not assume backup merely because the app is installed. Sync Health/workouts separately. Keep the phone paired, and retain carrier recovery details privately. Consult [Samsung's backup instructions](https://www.samsung.com/us/support/answer/ANS10013461/).

## Developer options and pairing

1. Same trusted Wi-Fi for watch and computer. Charge adequately and keep the screen awake for connection prompts. Do not use public Wi-Fi, forwarding or internet-exposed ADB.
2. Settings → About watch → Software → tap Software version five times. Unlock the watch if asked. Settings → Developer options → ADB debugging on.
3. Enable Wireless debugging, approve the trusted network prompt, choose Pair new device. Note the temporary **pairing** address/port. Run `cleanmywatch pair WATCH_IP:PAIRING_PORT`; adb prompts locally for the code. Keep the pairing screen open until done.
4. Return to Wireless debugging's main screen. Use its **connection** address/port with `cleanmywatch connect WATCH_IP:CONNECTION_PORT`. These ports usually differ and can change. `devices` gives the explicit target selector.
5. Approve the watch's debugging authorization if displayed. `offline`/`unauthorized` means not ready. Never operate a phone accidentally: the toolkit requires `--device` and refuses a target lacking Samsung/watch identification.

Older Wear OS firmware may expose Debug over Wi-Fi with an address instead of pairing. Use what that firmware displays; no automatic `adb tcpip` command is provided. Samsung Tizen uses different tooling and is unsupported.

## Troubleshooting

- Connection refused: check Wireless debugging on, current connection port, same Wi-Fi, watch awake, and pairing status. An IP alone is insufficient. Do not assume port 5555.
- Server fails on the PC: run `adb version` and `adb devices` in a normal local terminal. Check firewall/endpoint security and competing ADB installations. An AI execution sandbox may block the local server/network. Do not disable your firewall globally or make an unauthenticated relay.
- Pairing failure: reopen Pair new device; its code and port are temporary. Never place the code in Git/chat. CLI pairing runs adb's local interactive prompt.
- Unrecognized firmware output: stop. Strict parsing failure is preferable to guessed state. File a minimal, manually redacted issue.
- After finishing: turn Wireless debugging and ADB debugging off, forget/revoke PC authorization, and confirm settings after a normal reboot. `adb disconnect` affects the client only.

References: [Samsung](https://developer.samsung.com/health/sensor/guide/connect-watch.html), [Wear OS Wi-Fi debugging](https://developer.android.com/training/wearables/get-started/debug-wifi), [ADB](https://developer.android.com/tools/adb).

## Optional privacy controls

After auditing, review [privacy controls](PRIVACY-CONTROLS.md) for explicit app choices, experimental system-package opt-in and AdGuard DNS setup/restore. Keep Health and core connectivity enabled. A Samsung backup is recommended and required by default; an owner may explicitly choose `apply --skip-backup` with its honest typed waiver.
