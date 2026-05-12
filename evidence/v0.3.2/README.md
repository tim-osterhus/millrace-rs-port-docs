# Millrace Rust v0.3.2 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.3.2` port release.

## Release

- Rust release: `v0.3.2`
- Python baseline: `v0.18.1`
- Python target: `v0.18.2` (`5444cb9485ea90b67b2ed6ba7e0723ae9fe7b79f`)
- Auto-port idea: `idea-auto-port-python-v0.18.1-to-v0.18.2-rust-0.3.2`
- Evidence tarball: `dist/v0.3.2-port-evidence.tar.gz`
- Tarball SHA256: `2c9dc315483ea8e911c1011b9b989d8d9c1324e731a1ca1e97bbed1f7f1e0987`

## Sanitized Contents

- Bundle payload files: 103
- Selected stage results: 30
- Selected runs: 9
- Selected work items: 9
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.

## Local Verification

```bash
python scripts/verify_post_v0_1_0_evidence.py --version 0.3.2 --bundle dist/v0.3.2-port-evidence.tar.gz
```
