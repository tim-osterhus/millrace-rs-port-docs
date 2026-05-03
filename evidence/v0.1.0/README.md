# v0.1.0 Evidence

This directory contains generated public summaries for the Rust v0.1.0 port
campaign.

- `generated/metrics.json`: canonical machine-readable proof metrics.
- `generated/stage-summary.csv`: stage-call and token totals by plane/stage.
- `generated/slice-summary.csv`: slice-level run/stage/task/timing/token totals.
- `generated/checksums.sha256`: SHA256 checksums for generated summaries.

The sanitized raw run artifacts are not committed here. They should be
distributed as a release asset named:

```text
v0.1.0-port-evidence.tar.gz
```

Local export details from the original workspace:

- Files in bundle: 940
- SHA256: `faffab654195d12b97788b35882435fcc35d64c4b9e0c26ec6468dee9fff4293`

Recreate the generated summaries from an adjacent `millrace-rs` checkout:

```bash
python3 scripts/generate_v0_1_0_metrics.py --source ../millrace-rs --output evidence/v0.1.0/generated
```

Verify the summaries:

```bash
python3 scripts/verify_v0_1_0_evidence.py --source ../millrace-rs
```
