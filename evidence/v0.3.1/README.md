# Millrace Rust v0.3.1 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.3.1` port release.

## Release

- Rust release: `v0.3.1`
- Python baseline: `v0.18.0`
- Python target: `v0.18.1` (`0396c7852793b212d31345862b38a7d6f3f02854`)
- Auto-port idea: `idea-auto-port-python-v0.18.0-to-v0.18.1-rust-0.3.1`
- Evidence tarball: `dist/v0.3.1-port-evidence.tar.gz`
- Tarball SHA256: `3f7940f6c4df5a37d3f280d1942da8da844e93cf6d2cdc67a78c999c82d8522e`

## Sanitized Contents

- Bundle payload files: 98
- Selected stage results: 25
- Selected runs: 9
- Selected work items: 9
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.

## Local Verification

```bash
python scripts/verify_post_v0_1_0_evidence.py --version 0.3.1 --bundle dist/v0.3.1-port-evidence.tar.gz
```
