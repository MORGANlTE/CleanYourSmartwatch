"""Preview -> fresh snapshot -> durable write-ahead journal -> verified single change."""

from pathlib import Path

from .adb import SafetyError
from .inventory import CATALOG, eligible, snapshot
from .protection import protect
from .storage import locked, new_path, now, read, save


def same_device(adb, identity: dict):
    if adb.identity() != identity:
        raise SafetyError("Physical device or firmware differs; stopping")


def plan(adb, profile: str, selected: list[str]) -> dict:
    if profile not in CATALOG["profiles"]:
        raise SafetyError("Unknown profile")
    if len(selected) != len(set(selected)):
        raise SafetyError("Duplicate package selection")
    data = snapshot(adb)
    changes = []
    for package in selected:
        if package not in CATALOG["profiles"][profile] or package not in data["packages"]:
            raise SafetyError("Package is absent or outside the reviewed optional-app catalog")
        eligible(adb, package)
        previous = adb.state(package)
        if previous not in (0, 1):
            raise SafetyError("Selected app is already disabled or has an unsupported state")
        changes.append(dict(package=package, previous=previous, target=3))
    same_device(adb, data["identity"])
    return dict(
        schema=1,
        created=now(),
        catalog=CATALOG["version"],
        profile=profile,
        identity=data["identity"],
        changes=changes,
        warning="UNTESTED ON HARDWARE. Local dependency review and backup required.",
    )


def validate_changes(data):
    if not isinstance(data, dict):
        raise SafetyError("Plan/session must be a JSON object")
    changes = data.get("changes")
    if data.get("schema") != 1 or not isinstance(changes, list):
        raise SafetyError("Unsupported plan/session schema")
    seen = set()
    for change in changes:
        if not isinstance(change, dict) or not isinstance(change.get("package"), str):
            raise SafetyError("Malformed package change")
        p = change.get("package")
        protect(p)
        if p not in CATALOG["packages"] or p in seen:
            raise SafetyError("Unapproved or duplicate package in local state")
        if type(change.get("previous")) is not int or change["previous"] not in (0, 1):
            raise SafetyError("Unsafe restore state")
        if type(change.get("target")) is not int or change["target"] != 3:
            raise SafetyError("Unsafe target state")
        seen.add(p)
    if not isinstance(data.get("identity"), dict):
        raise SafetyError("Missing device identity")


def apply(adb, root: Path, proposed: dict, confirm, backup_confirm) -> Path | None:
    validate_changes(proposed)
    if proposed.get("catalog") != CATALOG["version"]:
        raise SafetyError("Catalog changed; generate a new plan")
    if not proposed["changes"]:
        raise SafetyError("Plan has no changes")
    with locked(root):
        for path in (root / "sessions").glob("*.json"):
            previous_session = read(path)
            validate_changes(previous_session)
            if any(
                c.get("status") in {"pending", "restoring"} for c in previous_session["changes"]
            ):
                raise SafetyError("Unresolved interrupted session; restore it before new changes")
        same_device(adb, proposed["identity"])
        # Validate whole plan before first write to watch.
        for change in proposed["changes"]:
            eligible(adb, change["package"])
            if adb.state(change["package"]) != change["previous"]:
                raise SafetyError("Package state drifted; generate a fresh plan")
        if not backup_confirm():
            raise SafetyError("Recent Samsung backup has not been confirmed")
        for change in proposed["changes"]:
            if not confirm(change):
                raise SafetyError("Approval declined; no watch changes made")
        backup = snapshot(adb)
        # Save exact package metadata only for selected optional apps.
        backup["package_metadata"] = {
            c["package"]: adb.details(c["package"]) for c in proposed["changes"]
        }
        backup["created"] = now()
        backup_path = save(new_path(root, "backups"), backup)
        journal_path = new_path(root, "sessions")
        journal = {
            **proposed,
            "backup": str(backup_path.resolve()),
            "started": now(),
            "status": "applying",
            "changes": [dict(c, status="planned") for c in proposed["changes"]],
        }
        save(journal_path, journal)
        try:
            for change in journal["changes"]:
                same_device(adb, journal["identity"])
                eligible(adb, change["package"])
                if adb.state(change["package"]) != change["previous"]:
                    raise SafetyError("Package state changed during apply")
                change["status"] = "pending"  # Must reach disk BEFORE the command.
                save(journal_path, journal)
                change["result"] = adb.set_state(change["package"], 3)
                same_device(adb, journal["identity"])
                if adb.state(change["package"]) != 3 or change["package"] not in adb.packages(True):
                    raise SafetyError("Disable verification failed")
                change["status"] = "applied"
                save(journal_path, journal)
            journal["status"] = "complete"
        except BaseException as exc:
            journal["status"] = "interrupted; inspect and restore before continuing"
            journal["error"] = type(exc).__name__
            raise
        finally:
            save(journal_path, journal)
        return journal_path


def restore(adb, root: Path, path: Path, confirm, only: str | None = None):
    with locked(root):
        journal = read(path)
        validate_changes(journal)
        if "started" not in journal or "status" not in journal:
            raise SafetyError("Restore needs a session journal, not a plan")
        same_device(adb, journal["identity"])
        changes = [
            c
            for c in reversed(journal["changes"])
            if c.get("status") in {"pending", "applied", "restoring"}
            and (only is None or c["package"] == only)
        ]
        if not changes:
            raise SafetyError("No outstanding changes selected in this session")
        for change in changes:
            eligible(adb, change["package"])
            current = adb.state(change["package"])
            if current not in (3, change["previous"]):
                raise SafetyError("Unexpected state drift during restore; inspect manually")
        if not confirm(changes):
            raise SafetyError("Restore declined")
        for change in changes:
            same_device(adb, journal["identity"])
            eligible(adb, change["package"])
            current = adb.state(change["package"])
            if current not in (3, change["previous"]):
                raise SafetyError("Package state changed during restore")
            change["status"] = "restoring"
            save(path, journal)
            if current != change["previous"]:
                change["restore_result"] = adb.set_state(change["package"], change["previous"])
            same_device(adb, journal["identity"])
            if adb.state(change["package"]) != change["previous"]:
                raise SafetyError("Restore verification failed; retain journal and reconnect")
            change["status"] = "restored"
            save(path, journal)
        journal["status"] = (
            "restored"
            if all(c["status"] in {"restored", "planned"} for c in journal["changes"])
            else "partial restore"
        )
        save(path, journal)
