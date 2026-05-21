# Millrace Rust v0.5.0 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.5.0` auto-port release.

## Release

- Rust release: `v0.5.0`
- Python baseline: `v0.19.0`
- Python target: `v0.20.0` (`c432786242e9e7cf9f7262ec0ec4f906f4bb7bf7`)
- Auto-port idea: `idea-auto-port-python-v0.19.0-to-v0.20.0-rust-0.5.0`
- Evidence tarball: `dist/v0.5.0-port-evidence.tar.gz`
- Tarball SHA256: `518077224e96fa020183271ee19403a470d2f10dbbab9087e640cf398793c844`

## Sanitized Contents

- Bundle payload files: 128
- Selected stage results: 39
- Selected runs: 12
- Selected work items: 11
- Stage calls with token usage: 0
- Input tokens: 0
- Cached input tokens: 0
- Output tokens: 0
- Reasoning output tokens: 0
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.
