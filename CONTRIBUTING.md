# Contributing

All initial code and documentation are AI generated. Review and evidence are welcome. Install with `python -m pip install -e '.[dev]'`; run `python -m pytest`, `python -m ruff check .`, and `python tools/check_public_files.py`.

Tests must use synthetic ADB fixtures. Do not connect CI to real watches or attach raw device logs. Follow docs/COMPATIBILITY.md for consented model/firmware records. Add regressions for safety boundaries, including malformed state, unknown packages, wrong device and interrupted recovery. Never weaken a guard to make a package list pass.

Changing the optional-app catalog requires public publisher evidence, consequences/dependencies, and clear firmware test status. System-package disabling needs a separately reviewed design and exact-build hardware evidence; it is not enabled by editing a profile. Preserve backward recovery paths when evolving schemas or catalogs.

No claimed battery or privacy improvement without measurements and limitations. Name-based heuristics are protected hints, never proof of spyware. Keep changes small, auditable and local by default.
