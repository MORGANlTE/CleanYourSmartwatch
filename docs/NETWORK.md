# Network privacy guidance

Non-root ADB inventory is not a packet trace. Package names and vendor ownership do not establish spyware or prove data transmission. The audit reads selected network settings without changing them. Explicit `dns-plan`, `dns-apply`, `dns-status` and `dns-restore` commands add opt-in AdGuard Private DNS with exact old-setting recovery. Status extracts per-network validation from connectivity metadata without saving the full dump. It does not intercept TLS, install a VPN, configure a proxy, read Wi-Fi credentials or enumerate accounts. See [active DNS controls](PRIVACY-CONTROLS.md).

Before adding a DNS filter, check whether your router already uses Pi-hole, AdGuard Home, domain-based VPN routing or another resolver policy. Watch-level encrypted DNS can bypass those rules. Companion-phone forwarding may make traffic appear to come from the phone. Filter logs must be scoped by client, and even that may not prove the originating app/watch. Consult your router/filter documentation and keep an undo copy of existing configuration.

Offline input: a UTF-8 CSV with `domain` header and one queried domain per row. Other columns are ignored, but do not import sensitive client identities unnecessarily. DNS reports remain private. Exact-domain rules are supplied by you; the project contains no asserted real telemetry endpoints.

```json
{
  "analytics.example.invalid": {
    "category": "analytics",
    "confidence": "high",
    "evidence": "Synthetic example only; replace with a reviewed source"
  }
}
```

Categories: advertising, analytics, crash-reporting, essential, mixed. Without a rule the classification is unknown/low-confidence. `--export-blocklist` emits only high-confidence advertising/analytics exact labels as AdGuard `||domain^` rules, which also match subdomains. Review that broader scope before use. Pi-hole and other formats are not generated. No export is automatically applied.

Shared endpoints can carry essential authentication, health sync, software updates and analytics together. Never block these automatically. Crash reporting is separate and excluded from the export. DNS blocking cannot see payloads or block all hardcoded/encrypted endpoints and does not prove zero telemetry or battery savings.
