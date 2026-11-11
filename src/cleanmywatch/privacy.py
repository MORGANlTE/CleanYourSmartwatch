"""Offline DNS log summary; observations do not prove purpose or watch origin."""

import csv
import re
from collections import Counter
from pathlib import Path

from .adb import SafetyError
from .storage import read


def dns_summary(path: Path, rules_path: Path | None = None) -> dict:
    rules = read(rules_path) if rules_path else {}
    categories = {"advertising", "analytics", "crash-reporting", "essential", "mixed"}
    for domain, rule in rules.items():
        if (
            not valid_domain(domain)
            or not isinstance(rule, dict)
            or rule.get("category") not in categories
            or not rule.get("evidence")
        ):
            raise SafetyError("Rules require exact domains, category and evidence")
    counts = Counter()
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or "domain" not in reader.fieldnames:
            raise SafetyError(
                "DNS CSV needs a domain column; export only the relevant client first"
            )
        for row in reader:
            domain = row["domain"].lower().rstrip(".")
            if not valid_domain(domain):
                raise SafetyError("Invalid domain in DNS CSV")
            counts[domain] += 1
    return {
        "origin": "User-supplied log; watch versus companion-phone origin NOT verified",
        "endpoints": [
            dict(
                domain=d,
                count=n,
                **rules.get(
                    d, {"category": "unknown", "evidence": "DNS query only", "confidence": "low"}
                ),
            )
            for d, n in sorted(counts.items())
        ],
        "limitations": "Shared endpoints may be essential. DNS does not expose encrypted payloads.",
    }


def valid_domain(domain: str) -> bool:
    return (
        len(domain) <= 253
        and "." in domain
        and all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p) for p in domain.split("."))
    )


def blocklist(summary: dict) -> str:
    # Explicit, evidence-backed user labels only; never mixed or essential endpoints.
    return (
        "\n".join(
            "||" + item["domain"] + "^"
            for item in summary["endpoints"]
            if item["category"] in {"advertising", "analytics"} and item.get("confidence") == "high"
        )
        + "\n"
    )
