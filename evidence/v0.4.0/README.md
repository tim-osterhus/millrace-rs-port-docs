# Millrace Rust v0.4.0 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.4.0` auto-port release.

## Release

- Rust release: `v0.4.0`
- Python baseline: `v0.18.6`
- Python target: `v0.19.0` (`efb9c5881f524d23dcb78aecfc96fdf7cda9d26f`)
- Auto-port idea: `idea-auto-port-python-v0.18.6-to-v0.19.0-rust-0.4.0`
- Evidence tarball: `dist/v0.4.0-port-evidence.tar.gz`
- Tarball SHA256: `2baca79899161030ce771cb503f4eb12d0763519472c0c7b5bdab900bf5a7b77`

## Sanitized Contents

- Bundle payload files: 108
- Selected stage results: 31
- Selected runs: 10
- Selected work items: 9
- Stage calls with token usage: 0
- Input tokens: 0
- Cached input tokens: 0
- Output tokens: 0
- Reasoning output tokens: 0
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.
