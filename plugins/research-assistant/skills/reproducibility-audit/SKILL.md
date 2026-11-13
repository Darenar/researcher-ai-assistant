---
name: reproducibility-audit
description: Audit whether reported research results can be traced and regenerated from data, code, environment, and documented parameters. Use for reproducibility checks, stale-output detection, or before sharing and submission.
---

# Reproducibility audit

Trace each important result through `raw data -> processing -> analysis -> table or figure -> manuscript claim`.

- Inspect data pointers, dependency locks, environment files, random seeds, configuration, scripts, notebooks, generated artifacts, and manuscript references.
- Identify the command that should reproduce each sampled result. Do not execute costly jobs, access remote data, or overwrite outputs without authorization.
- When execution is safe and requested, run in the documented environment and compare regenerated artifacts with tracked results. Distinguish numerical differences from formatting-only changes.
- Check that raw data remain outside Git as required by `../research-data-sync/SKILL.md`, while code, metadata, and immutable pointers remain versioned.
- Report findings by severity with evidence, affected result, and the smallest corrective action. Mark anything not tested as unverified rather than reproducible.
