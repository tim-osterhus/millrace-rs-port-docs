# Millrace Rust v0.5.1 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.5.1` auto-port release.

## Release

- Rust release: `v0.5.1`
- Python baseline: `v0.20.0`
- Python target: `v0.20.1` (`83178d37497d7c299dbcaa50264ee0e51b150a18`)
- Auto-port idea: `idea-auto-port-python-v0.20.0-to-v0.20.1-rust-0.5.1`
- Evidence tarball: `dist/v0.5.1-port-evidence.tar.gz`
- Tarball SHA256: `b9e800d2fd3cb9ea6d1ceff14f4318d992627ccae740b99d5555ebd734110bb2`

## Sanitized Contents

- Bundle payload files: 96
- Selected stage results: 26
- Selected runs: 9
- Selected work items: 8
- Stage calls with token usage: 0
- Input tokens: 0
- Cached input tokens: 0
- Output tokens: 0
- Reasoning output tokens: 0
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.
