# Millrace Rust v0.2.1 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.2.1` port release.

## Release

- Rust release: `v0.2.1`
- Python baseline: `v0.17.3`
- Python target: `v0.17.4` (`304e537964ff772c815689b87e4c1e3b805c656c`)
- Auto-port idea: `idea-auto-port-python-v0.17.3-to-v0.17.4-rust-0.2.1`
- Evidence tarball: `dist/v0.2.1-port-evidence.tar.gz`
- Tarball SHA256: `6bc0e5da724c426c4450fe02e5472da6b7663111039fb6308f5493c82b608ca7`

## Sanitized Contents

- Bundle payload files: 72
- Selected stage results: 16
- Selected runs: 6
- Selected work items: 6
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.

## Local Verification

```bash
python scripts/verify_post_v0_1_0_evidence.py --version 0.2.1 --bundle dist/v0.2.1-port-evidence.tar.gz
```
