# v0.1.0 Evidence

This directory contains generated public summaries for the Rust v0.1.0 port
campaign.

- `generated/metrics.json`: canonical machine-readable proof metrics.
- `generated/stage-summary.csv`: stage-call and token totals by plane/stage.
- `generated/slice-summary.csv`: slice-level run/stage/task/timing/token totals.
- `generated/checksums.sha256`: SHA256 checksums for generated summaries.

The sanitized public evidence bundle is not committed here. It should be
distributed as a release asset named:

```text
v0.1.0-port-evidence.tar.gz
```

Local export details from the current public bundle:

- Files in bundle: 386
- SHA256: `46f620b8a4054dd11a7e4db48dd358d713d2042c1e7255278f61081e64609e06`

Recreate the generated summaries from an adjacent `millrace-rs` checkout:

```bash
python3 scripts/generate_v0_1_0_metrics.py --source ../millrace-rs --output evidence/v0.1.0/generated
```

Verify the summaries:

```bash
python3 scripts/verify_v0_1_0_evidence.py --source ../millrace-rs
```
