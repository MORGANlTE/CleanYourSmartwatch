import pytest

from cleanmywatch import dns
from cleanmywatch.adb import SafetyError
from cleanmywatch.storage import read


class Watch:
    def __init__(self):
        self.values = dict.fromkeys(dns.KEYS, "null")
        self.token = "synthetic-watch"
        self.calls = []
        self.fail = False
        self.networks = ""

    def identity(self):
        return {"device_token": self.token, "ro.build.fingerprint": "synthetic-build"}

    def shell(self, *args):
        if args == ("dumpsys", "connectivity"):
            return self.networks
        _, verb, namespace, key, *value = args
        assert namespace == "global" and key in dns.KEYS
        if verb == "get":
            return self.values[key]
        self.calls.append(args)
        self.values[key] = "null" if verb == "delete" else ("" if value[0] == "''" else value[0])
        if self.fail:
            raise SafetyError("Synthetic dropped response after setting persisted")
        return ""


@pytest.mark.parametrize(
    "mode,host", [("null", "null"), ("opportunistic", ""), ("hostname", "resolver.example.org")]
)
def test_dns_exact_restore_and_write_ahead(tmp_path, mode, host):
    watch = Watch()
    watch.values = {"private_dns_mode": mode, "private_dns_specifier": host}
    previous = dict(watch.values)
    proposed = dns.plan(watch)
    assert watch.calls == []
    original = watch.shell

    def checked(*args):
        if args[:2] == ("settings", "put"):
            journal = next((tmp_path / "dns-sessions").glob("*.json"))
            assert read(journal)["status"] in {"applying", "restoring"}
            if read(journal)["status"] == "applying":
                assert read(journal)["changes"][-1]["status"] == "pending"
        return original(*args)

    watch.shell = checked
    path = dns.apply(watch, tmp_path, proposed, lambda _: True)
    assert watch.values == dns.TARGET
    dns.restore(watch, tmp_path, path, lambda _: True)
    assert watch.values == previous
    assert read(path)["status"] == "restored"


def test_interrupted_dns_can_restore_and_blocks_new_apply(tmp_path):
    watch = Watch()
    proposed = dns.plan(watch)
    watch.fail = True
    with pytest.raises(SafetyError):
        dns.apply(watch, tmp_path, proposed, lambda _: True)
    watch.fail = False
    path = next((tmp_path / "dns-sessions").glob("*.json"))
    assert read(path)["changes"][-1]["status"] == "pending"
    with pytest.raises(SafetyError, match="existing DNS session"):
        dns.apply(watch, tmp_path, dns.plan(watch), lambda _: True)
    dns.restore(watch, tmp_path, path, lambda _: True)
    assert all(value == "null" for value in watch.values.values())


@pytest.mark.parametrize("reason", ["declined", "identity", "drift", "tamper"])
def test_dns_refuses_preflight_without_mutation(tmp_path, reason):
    watch = Watch()
    proposed = dns.plan(watch)
    if reason == "identity":
        watch.token = "different-watch"
    elif reason == "drift":
        watch.values["private_dns_mode"] = "off"
    elif reason == "tamper":
        proposed["target"]["private_dns_specifier"] = "arbitrary.example.org"
    with pytest.raises(SafetyError):
        dns.apply(watch, tmp_path, proposed, lambda _: reason != "declined")
    assert watch.calls == []


def test_dns_restore_refuses_wrong_device_and_unknown_setting(tmp_path):
    watch = Watch()
    path = dns.apply(watch, tmp_path, dns.plan(watch), lambda _: True)
    watch.token = "different-watch"
    count = len(watch.calls)
    with pytest.raises(SafetyError):
        dns.restore(watch, tmp_path, path, lambda _: True)
    assert len(watch.calls) == count
    with pytest.raises(SafetyError):
        dns.put(watch, "unrelated_setting", "0")


def test_dns_restore_rechecks_drift_after_prompt(tmp_path):
    watch = Watch()
    path = dns.apply(watch, tmp_path, dns.plan(watch), lambda _: True)
    count = len(watch.calls)

    def approve(_):
        watch.values["private_dns_mode"] = "off"
        return True

    with pytest.raises(SafetyError, match="drifted during restore"):
        dns.restore(watch, tmp_path, path, approve)
    assert len(watch.calls) == count


def test_dns_status_requires_same_network_hostname_and_validation():
    watch = Watch()
    watch.values = dict(dns.TARGET)
    watch.networks = """
NetworkAgentInfo{network{101} ni{WIFI CONNECTED} lp{PrivateDnsServerName: dns.adguard-dns.com ValidatedPrivateDnsAddresses: []} nc{Transports: WIFI Capabilities: INTERNET} factorySerialNumber=1}
NetworkAgentInfo{network{102} ni{COMPANION_PROXY CONNECTED} lp{ValidatedPrivateDnsAddresses: [8.8.8.8]} nc{Transports: BLUETOOTH Capabilities: INTERNET} factorySerialNumber=2}
"""
    result = dns.status(watch)
    assert result["adguard_configured"]
    assert not result["adguard_validated_on_observed_network"]
    watch.networks = watch.networks.replace(
        "ValidatedPrivateDnsAddresses: []", "ValidatedPrivateDnsAddresses: [94.140.14.14]"
    )
    assert dns.status(watch)["adguard_validated_on_observed_network"]
