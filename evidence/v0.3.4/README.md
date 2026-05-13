# Millrace Rust v0.3.4 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.3.4` auto-port release.

## Release

- Rust release: `v0.3.4`
- Python baseline: `v0.18.3`
- Python target: `v0.18.4` (`516e947e90155b6436dbc9efcf932254f34bc39c`)
- Auto-port idea: `idea-auto-port-python-v0.18.3-to-v0.18.4-rust-0.3.4`
- Evidence tarball: `dist/v0.3.4-port-evidence.tar.gz`
- Tarball SHA256: `6d1e55511696b16349e9e16732069751c11f5a2b4079ed5557b01bd18563c6b3`

## Sanitized Contents

- Bundle payload files: 100
- Selected stage results: 27
- Selected runs: 10
- Selected work items: 9
- Stage calls with token usage: 0
- Input tokens: 0
- Cached input tokens: 0
- Output tokens: 0
- Reasoning output tokens: 0
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.
