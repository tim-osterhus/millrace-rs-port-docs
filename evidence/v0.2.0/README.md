# Millrace Rust v0.2.0 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.2.0` port release.

## Release

- Rust release: `v0.2.0`
- Python baseline: `v0.16.1`
- Python target: `v0.17.3` (`a0d6b1bd5b71284eab7e9a5dcc9f76cee6580aaf`)
- Auto-port idea: `idea-auto-port-python-v0.16.1-to-v0.17.3-rust-0.2.0`
- Evidence tarball: `dist/v0.2.0-port-evidence.tar.gz`
- Tarball SHA256: `39f4797d629810a5d6a82457343b0ee3351351dc2c342dfe1593ac70c91d94be`

## Sanitized Contents

- Bundle payload files: 114
- Selected stage results: 32
- Selected runs: 11
- Selected work items: 11
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.

## Local Verification

```bash
python scripts/verify_post_v0_1_0_evidence.py --version 0.2.0 --bundle dist/v0.2.0-port-evidence.tar.gz
```
