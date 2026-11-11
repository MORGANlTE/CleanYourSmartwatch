"""Opt-in Private DNS with durable exact-state recovery, not a traffic-silence claim."""

import re

from .adb import SafetyError
from .engine import same_device
from .privacy import valid_domain
from .storage import locked, new_path, now, read, save

HOST = "dns.adguard-dns.com"
KEYS = ("private_dns_specifier", "private_dns_mode")
TARGET = {"private_dns_specifier": HOST, "private_dns_mode": "hostname"}


def settings(adb):
    values = {key: adb.shell("settings", "get", "global", key) for key in KEYS}
    validate_values(values)
    return values


def validate_values(values):
    if not isinstance(values, dict) or set(values) != set(KEYS):
        raise SafetyError("Invalid DNS setting keys")
    if not isinstance(values["private_dns_mode"], str) or values["private_dns_mode"] not in {
        "null",
        "off",
        "opportunistic",
        "hostname",
    }:
        raise SafetyError("Unknown Private DNS mode")
    host = values["private_dns_specifier"]
    if not isinstance(host, str) or (host not in {"null", ""} and not valid_domain(host)):
        raise SafetyError("Unrecognized prior DNS hostname; refusing to guess")


def plan(adb):
    identity = adb.identity()
    previous = settings(adb)
    same_device(adb, identity)
    return dict(
        kind="private-dns",
        schema=1,
        identity=identity,
        previous=previous,
        target=dict(TARGET),
        created=now(),
        notice="AdGuard receives DNS queries. DNS filtering is not anonymity; phone-proxy, app-managed DNS and direct-IP paths require separate tests.",
    )


def validate(data):
    if (
        not isinstance(data, dict)
        or data.get("schema") != 1
        or data.get("kind") != "private-dns"
        or not isinstance(data.get("identity"), dict)
        or data.get("target") != TARGET
    ):
        raise SafetyError("Invalid DNS plan/session")
    validate_values(data.get("previous"))


def put(adb, key, value):
    if key not in KEYS:
        raise SafetyError("Unknown DNS key")
    if value == "null":
        adb.shell("settings", "delete", "global", key)
    else:
        adb.shell("settings", "put", "global", key, "''" if value == "" else value)
    if adb.shell("settings", "get", "global", key) != value:
        raise SafetyError("DNS setting write did not persist")


def apply(adb, root, proposed, confirm):
    validate(proposed)
    with locked(root):
        for path in (root / "dns-sessions").glob("*.json"):
            old = read(path)
            validate(old)
            if old.get("status") != "restored":
                raise SafetyError("Restore the existing DNS session before applying another")
        same_device(adb, proposed["identity"])
        if settings(adb) != proposed["previous"]:
            raise SafetyError("DNS settings changed; generate a fresh plan")
        if not confirm(proposed):
            raise SafetyError("DNS approval declined")
        path = new_path(root, "dns-sessions")
        journal = dict(proposed, status="applying", started=now(), changes=[])
        save(path, journal)
        try:
            for key in KEYS:  # Hostname first, strict mode second.
                same_device(adb, journal["identity"])
                expected = dict(journal["previous"])
                expected.update({c["key"]: TARGET[c["key"]] for c in journal["changes"]})
                if settings(adb) != expected:
                    raise SafetyError("DNS settings drifted during apply")
                change = dict(key=key, status="pending")
                journal["changes"].append(change)
                save(path, journal)
                put(adb, key, TARGET[key])
                change["status"] = "applied"
                save(path, journal)
            same_device(adb, journal["identity"])
            journal["status"] = "applied; network validation still required"
        except BaseException:
            journal["status"] = "interrupted; restore before retrying"
            raise
        finally:
            save(path, journal)
        return path


def restore(adb, root, path, confirm):
    with locked(root):
        data = read(path)
        validate(data)
        if "started" not in data:
            raise SafetyError("Restore requires a DNS session, not a plan")
        same_device(adb, data["identity"])
        current = settings(adb)
        for key in KEYS:
            if current[key] not in (data["previous"][key], TARGET[key]):
                raise SafetyError("DNS settings drifted; review before overwriting")
        if not confirm(data):
            raise SafetyError("DNS restore declined")
        data["status"] = "restoring"
        save(path, data)
        # Remove strict mode first, then restore the previous hostname.
        for key in reversed(KEYS):
            same_device(adb, data["identity"])
            if settings(adb) != current:
                raise SafetyError("DNS settings drifted during restore")
            put(adb, key, data["previous"][key])
            current[key] = data["previous"][key]
        if settings(adb) != data["previous"]:
            raise SafetyError("DNS restore verification failed")
        same_device(adb, data["identity"])
        data["status"] = "restored"
        save(path, data)


def status(adb):
    identity = adb.identity()
    configured = settings(adb)
    # Extract only active agents, not historical callbacks, SSIDs or addresses.
    output = adb.shell("dumpsys", "connectivity")
    networks = []
    for section in re.findall(
        r"NetworkAgentInfo\{.*?(?=\n\s*NetworkAgentInfo\{|\n\s*Network Requests|\Z)", output, re.S
    ):
        head = section.split("factorySerialNumber=", 1)[0]
        if "ni{" not in head:
            continue
        server = re.search(r"PrivateDnsServerName:\s*([^\s}]+)", head)
        validated = re.search(r"ValidatedPrivateDnsAddresses:\s*\[([^\]]*)\]", head)
        transport = re.search(r"Transports:\s*([A-Z| ]+?)\s+Capabilities:", head)
        networks.append(
            dict(
                transport=transport[1].strip() if transport else "unknown",
                private_dns_host=server[1] if server else None,
                tls_validated=bool(validated and validated[1].strip()),
                adguard_tls_validated=bool(
                    server and server[1] == HOST and validated and validated[1].strip()
                ),
            )
        )
    same_device(adb, identity)
    return dict(
        settings=configured,
        networks=networks,
        adguard_configured=configured == TARGET,
        adguard_validated_on_observed_network=any(n["adguard_tls_validated"] for n in networks),
        limitations="TLS validation is not proof every app uses this resolver or that all trackers are blocked. LTE, companion-phone forwarding and health sync require separate checks.",
    )
