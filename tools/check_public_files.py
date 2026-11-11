"""Check public working/staged files and optionally history without echoing private matches."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PRIVATE_PARTS = {".cleanmywatch", "backups", "reports", "shots", ".venv", "__pycache__"}
PATTERNS = [
    r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b",
    r"(?i)[a-z]:[\\/]users[\\/][a-z0-9]",
    r"/(?:home|Users)/[A-Za-z0-9_.-]+/",
    r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
    r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
    r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
    r'"device_token"\s*:\s*"[a-f0-9]{64}"',
    r"\badb-[A-Z0-9]{8,}-[a-z0-9]+\b",
]


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def private_path(name):
    path = Path(name)
    return bool(
        PRIVATE_PARTS.intersection(path.parts)
        or path.name.startswith((".env", "adbkey"))
        or path.suffix in {".log", ".pcap", ".pcapng"}
    )


def findings(content, deny_terms=()):
    try:
        text = content.decode("utf-8")
    except UnicodeError:
        return True
    return any(re.search(p, text) for p in PATTERNS) or any(
        term.casefold() in text.casefold() for term in deny_terms
    )


def scan(history=False, revision=None):
    if revision is not None and (
        revision.startswith("-") or not re.fullmatch(r"[A-Za-z0-9_./-]+", revision)
    ):
        raise ValueError("Invalid history revision")
    root = Path(os.environ.get("CLEANMYWATCH_HOME", ".cleanmywatch"))
    policy_path = root / "public-policy.local.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8")) if policy_path.exists() else {}
    terms = policy.get("deny_terms", [])
    if not isinstance(terms, list) or any(not isinstance(t, str) or len(t) < 4 for t in terms):
        raise ValueError("Private deny_terms must be strings of at least four characters")
    names = [n for n in git("ls-files", "-z").decode("utf-8").split("\0") if n]
    if not names:
        raise ValueError("No tracked files; stage the intended public files first")
    failures = set()

    def check(label, name, content):
        if private_path(name) or findings(content, terms):
            failures.add((label, name))

    for name in names:
        path = Path(name)
        if path.exists():
            check("working", name, path.read_bytes())
    for entry in git("ls-files", "--stage", "-z").decode("utf-8").split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        check("index", name, git("cat-file", "blob", metadata.split()[1]))
    if history:
        seen = set()
        for commit in git("rev-list", revision or "--all").decode().splitlines():
            author = git("show", "-s", "--format=%an%n%ae%n%cn%n%ce", commit)
            lines = author.decode("utf-8").splitlines()
            if findings(author, terms) or any(
                email and not email.endswith("@users.noreply.github.com")
                for email in (lines[1], lines[3])
            ):
                failures.add((commit[:12], "<author metadata; review privately>"))
            for entry in git("ls-tree", "-r", "-z", commit).decode("utf-8").split("\0"):
                if not entry:
                    continue
                metadata, name = entry.split("\t", 1)
                mode, kind, oid = metadata.split()
                if (oid, name) in seen:
                    continue
                seen.add((oid, name))
                if kind != "blob":
                    failures.add((commit[:12], name))
                    continue
                check(commit[:12], name, git("cat-file", "blob", oid))
    for label, name in sorted(failures):
        print(f"{label}: {name}: possible private data; inspect locally")
    print(
        f"Public-file guard: {len(failures)} finding(s). This is not a complete privacy guarantee."
    )
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true")
    parser.add_argument(
        "--revision", help="Scan only this local branch/commit history, instead of all refs"
    )
    args = parser.parse_args()
    try:
        return scan(args.history, args.revision)
    except (OSError, ValueError, subprocess.CalledProcessError):
        print(
            "Privacy scan could not complete; review local Git state/policy. Do not publish unchecked files."
        )
        return True


if __name__ == "__main__":
    sys.exit(main())
