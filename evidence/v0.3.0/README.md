# Millrace Rust v0.3.0 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.3.0` port release.

## Release

- Rust release: `v0.3.0`
- Python baseline: `v0.17.4`
- Python target: `v0.18.0` (`e4ccf099c8345a8b8708cdaa1ac510bdc7851387`)
- Auto-port idea: `idea-auto-port-python-v0.17.4-to-v0.18.0-rust-0.3.0`
- Evidence tarball: `dist/v0.3.0-port-evidence.tar.gz`
- Tarball SHA256: `286aabfd4c476de458ba53d661368e6471fa7ca0c4f21ba2fef13fcef4e25123`

## Sanitized Contents

- Bundle payload files: 81
- Selected stage results: 19
- Selected runs: 7
- Selected work items: 7
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.

## Local Verification

```bash
python scripts/verify_post_v0_1_0_evidence.py --version 0.3.0 --bundle dist/v0.3.0-port-evidence.tar.gz
```
