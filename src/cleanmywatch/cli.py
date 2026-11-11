"""Explicit target CLI and keyboard-friendly Rich menu using the same safety engine."""

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from . import battery as power
from .adb import ADB, SafetyError, endpoint
from .cleanup import prepare as prepare_cleanup
from .engine import apply as execute
from .engine import plan as make_plan
from .engine import restore as undo
from .inventory import CATALOG, snapshot
from .inventory import audit as collect_audit
from .privacy import blocklist, dns_summary
from .storage import new_path, read, save
from .telemetry import review as review_telemetry
from .verification import verify as verify_session

app = typer.Typer(
    no_args_is_help=True, help="Local Wear OS audit and reversible optional-app toolkit"
)
console = Console()
Device = Annotated[str, typer.Option("--device", "-s", help="Explicit ADB device selector")]
STATE = Path(os.environ.get("CLEANMYWATCH_HOME", ".cleanmywatch"))


def show(data):
    console.print_json(data=data)


def write(data, kind):
    path = save(new_path(STATE, kind), data)
    console.print(f"Private local file: {path}", markup=False)
    return path


def preview(proposed):
    console.print(proposed.get("warning", "Exact change preview"), markup=False)
    table = Table("Package", "Previous", "Proposed", "Consequence")
    for c in proposed["changes"]:
        table.add_row(
            c["package"],
            str(c["previous"]),
            "disabled-user (3)",
            CATALOG["packages"][c["package"]]["consequences"],
        )
    console.print(table)


def approve_change(change):
    package = change["package"]
    show(CATALOG["packages"][package])
    response = typer.prompt(
        f"After inspecting metadata and checking tiles/dependencies, type 'DISABLE {package}'"
    )
    return response == f"DISABLE {package}"


def backup_confirm():
    return (
        typer.prompt(
            "Verify a recent successful Samsung/Smart Switch backup on your phone. "
            "Type 'BACKUP VERIFIED' (an ADB snapshot is insufficient)"
        )
        == "BACKUP VERIFIED"
    )


@app.command()
def devices():
    """List devices locally; output contains private connection identifiers."""
    adb = ADB()
    console.print(adb.run("version"), markup=False)
    console.print(adb.run("devices", "-l"), markup=False)


@app.command()
def pair(address: str):
    """Pair using the PAIRING port. Code is entered privately into adb, never CLI history."""
    address = endpoint(address)
    adb = ADB()
    # Leave stdin to adb's own pairing prompt; code is not passed on the command line or logged.
    import subprocess

    result = subprocess.run([adb.binary, "pair", address], check=False)
    if result.returncode:
        raise SafetyError("Pairing failed; reopen Pair new device and use its current port")


@app.command()
def connect(address: str):
    """Connect using the CONNECTION port (usually different from pairing port)."""
    console.print(ADB().run("connect", endpoint(address)), markup=False)


@app.command()
def inspect(device: Device):
    """Identify watch/firmware; physical identifier is hashed locally."""
    show(ADB(device).identity())


@app.command()
def scan(device: Device):
    """Inventory and classify packages without disabling anything."""
    data = snapshot(ADB(device))
    write(data, "inventory")
    table = Table("Package", "Classification", "Action")
    for item in data["classifications"]:
        table.add_row(item["package"], item["category"], item["action"])
    console.print(table)


@app.command()
def audit(device: Device):
    """Save private detailed JSON and readable Markdown reports."""
    data = collect_audit(ADB(device))
    path = write(data, "audits")
    lines = [
        "# Private CleanMyWatch audit",
        "",
        "Package modification safety: UNTESTED",
        "",
        "Unknown/core apps remain protected. Local-only report; do not publish.",
        "",
    ]
    for item in data["classifications"]:
        lines += [f"## {item['package']}", ""]
        lines += [f"- {key}: {value}" for key, value in item.items() if key != "package"]
        lines.append("")
    path.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    console.print(f"Audit saved: {len(data['packages'])} packages; no changes made")


@app.command()
def plan(
    device: Device,
    profile: str = "conservative",
    package: Annotated[list[str] | None, typer.Option("--package", "-p")] = None,
):
    """Generate a dry-run plan. Every package requires explicit selection."""
    proposed = make_plan(ADB(device), profile, package or [])
    preview(proposed)
    write(proposed, "plans")
    console.print("No device changes. Balanced/aggressive add no unverified analytics packages.")


@app.command()
def apply(device: Device, plan_file: Path):
    """Preview again, verify backup, approve EACH package, journal then disable."""
    proposed = read(plan_file)
    from .engine import validate_changes

    validate_changes(proposed)
    preview(proposed)
    path = execute(ADB(device), STATE, proposed, approve_change, backup_confirm)
    console.print(
        f"Session saved: {path}. Test features using docs/SAFETY.md before continuing.",
        markup=False,
    )


@app.command()
def restore(
    device: Device,
    session: Path | None = None,
    package: str | None = None,
    last: bool = False,
    all_sessions: bool = False,
):
    """Restore one session, last session or all sessions in reverse time order."""
    if sum((session is not None, last, all_sessions)) != 1:
        raise SafetyError("Select exactly one of --session, --last, --all-sessions")
    paths = sorted((STATE / "sessions").glob("*.json"), reverse=True)
    paths = [
        p
        for p in paths
        if any(
            c.get("status") in {"pending", "applied", "restoring"}
            for c in read(p).get("changes", [])
        )
    ]
    if session:
        paths = [session]
    elif last:
        paths = paths[:1]
    if not paths:
        raise SafetyError("No sessions to restore")
    adb = ADB(device)
    for path in paths:

        def approve(changes):
            show(changes)
            return typer.confirm("Restore these exact previous states?", default=False)

        undo(adb, STATE, path, approve, package)
        console.print(f"Restored selected changes in {path}", markup=False)


@app.command()
def history():
    """Display local recovery session paths."""
    for path in sorted((STATE / "sessions").glob("*.json")):
        console.print(str(path) + ": " + read(path).get("status", "unknown"), markup=False)


@app.command()
def recovery(session: Annotated[Path, typer.Option("--session")]):
    """Print validated manual recovery commands, without storing a target address."""
    from .engine import validate_changes

    journal = read(session)
    validate_changes(journal)
    console.print("Verify physical watch and firmware against this LOCAL session first.")
    console.print(
        "Replace WATCH_SELECTOR with the current ADB selector. Run ONE command at a time."
    )
    for c in reversed(journal["changes"]):
        if c.get("status") in {"pending", "applied", "restoring"}:
            verb = "default-state" if c["previous"] == 0 else "enable"
            console.print(
                f"adb -s WATCH_SELECTOR shell pm {verb} --user 0 {c['package']}", markup=False
            )
    console.print(
        "Verify with dumpsys package and pm list packages -d --user 0. No ADB means no ADB rollback."
    )


@app.command()
def battery(
    device: Device, configuration: str = "LTE/Wi-Fi/AOD not recorded", before: Path | None = None
):
    """Record a battery sample, optionally compare with an earlier sample."""
    data = power.sample(ADB(device), configuration)
    write(data, "battery")
    show(power.compare(read(before), data) if before else data)


@app.command()
def optimize():
    """Show user-guided reversible recommendations; no device writes."""
    console.print(power.GUIDANCE)


@app.command()
def cleanup(device: Device):
    """Ask which optional apps to KEEP, then save a dry-run proposal; no watch writes."""
    console.print("Which apps do you want to keep? The default for every app is KEEP.")

    def keep(package, label, consequence):
        console.print(f"{label}: disabling would affect {consequence}", markup=False)
        return typer.confirm(f"Keep {label} ({package})?", default=True)

    report = prepare_cleanup(ADB(device), keep)
    write(report, "cleanup")
    show(report["candidates"])
    preview(report["plan"])
    if report["plan"]["changes"]:
        write(report["plan"], "plans")
    console.print("No watch changes. Blocked candidates are NOT executable plans.")


@app.command()
def telemetry(device: Device):
    """Review evidence-labelled diagnostics candidates; does not disable packages."""
    report = review_telemetry(ADB(device))
    write(report, "telemetry")
    for finding in report["findings"]:
        show({key: value for key, value in finding.items() if key != "metadata"})
    console.print(report["coverage"], markup=False)
    console.print(report["manual_guidance"], markup=False)
    console.print("No watch changes. Telemetry elimination is NOT VERIFIED.")


@app.command()
def verify(device: Device, session: Annotated[Path, typer.Option("--session")]):
    """Recheck exact recorded package states, including after reconnect/reboot."""
    report = verify_session(ADB(device), read(session))
    write(report, "verification")
    show(report)
    if not report["all_recorded_states_match"]:
        raise SafetyError(
            "Package verification has mismatches or unresolved changes; inspect/restore"
        )


@app.command()
def network(
    log: Annotated[Path, typer.Option("--log")],
    rules: Path | None = None,
    export_blocklist: bool = False,
):
    """Analyze a domain-column CSV offline; optional user-evidenced AdGuard syntax export."""
    data = dns_summary(log, rules)
    path = write(data, "dns")
    show(data)
    if export_blocklist:
        path.with_suffix(".adguard.txt").write_text(blocklist(data), encoding="utf-8")
        console.print("Review before importing; test essential features and retain an undo copy.")


@app.command()
def tui(device: Device):
    """Keyboard menu using the same audit, preview, approval and recovery code."""
    adb = ADB(device)
    while True:
        console.rule("CleanMyWatch · local only · hardware safety untested")
        console.print(
            "[1] Status  [2] Audit / browser  [3] Plan  [4] Apply\n"
            "[5] Battery  [6] Recommendations  [7] History  [8] Restore  [q] Quit"
        )
        choice = typer.prompt("Choice", default="q")
        if choice == "q":
            return
        try:
            if choice == "1":
                show(adb.identity())
            elif choice == "2":
                audit(device)
                scan(device)
            elif choice == "3":
                profile = typer.prompt(
                    "Profile: conservative/balanced/aggressive/custom", default="conservative"
                )
                console.print("Only explicit, locally reviewed optional apps:")
                show(CATALOG["packages"])
                selected = typer.prompt(
                    "Exact packages separated by spaces; empty = no changes",
                    default="",
                    show_default=False,
                ).split()
                plan(device, profile, selected)
            elif choice == "4":
                apply(device, Path(typer.prompt("Local plan JSON path")))
            elif choice == "5":
                battery(device, typer.prompt("LTE/Wi-Fi/AOD configuration"), None)
            elif choice == "6":
                optimize()
            elif choice == "7":
                history()
            elif choice == "8":
                restore(device, session=Path(typer.prompt("Session JSON path")))
        except SafetyError as exc:
            console.print(f"Stopped: {exc}", markup=False)


def main():
    try:
        app()
    except (SafetyError, OSError, ValueError, KeyError, TypeError) as exc:
        message = (
            str(exc)
            if isinstance(exc, SafetyError)
            else "Invalid or inaccessible local input; operation stopped"
        )
        console.print(f"Stopped: {message}", style="red", markup=False)
        raise SystemExit(1) from None
