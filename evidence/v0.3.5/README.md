# Millrace Rust v0.3.5 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.3.5` auto-port release.

## Release

- Rust release: `v0.3.5`
- Python baseline: `v0.18.4`
- Python target: `v0.18.6` (`63e623bc6fcfcf74ae0cc2ce5605a12ae4179873`)
- Auto-port idea: `idea-auto-port-python-v0.18.4-to-v0.18.6-rust-0.3.5`
- Evidence tarball: `dist/v0.3.5-port-evidence.tar.gz`
- Tarball SHA256: `19b91453d2db72bae2ba48d473ae93a9323804262b6f8d483e5bef92828bfc8c`

## Sanitized Contents

- Bundle payload files: 111
- Selected stage results: 33
- Selected runs: 11
- Selected work items: 9
- Stage calls with token usage: 0
- Input tokens: 0
- Cached input tokens: 0
- Output tokens: 0
- Reasoning output tokens: 0
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.
