# Millrace Rust v0.5.2 Port Evidence

This directory records sanitized public evidence metadata for the Rust `millrace-ai` `0.5.2` auto-port release.

## Release

- Rust release: `v0.5.2`
- Python baseline: `v0.20.1`
- Python target: `v0.20.3` (`c607c0c12ee91c5982f2808481ee5b818de12da9`)
- Auto-port idea: `idea-auto-port-python-v0.20.1-to-v0.20.3-rust-0.5.2`
- Evidence tarball: `dist/v0.5.2-port-evidence.tar.gz`
- Tarball SHA256: `12b91b30c83206422111c39375e5ce78c100d18b9d7cf631b4c9d44faf3c7891`

## Sanitized Contents

- Bundle payload files: 146
- Selected stage results: 52
- Selected runs: 15
- Selected work items: 11
- Stage calls with token usage: 0
- Input tokens: 0
- Cached input tokens: 0
- Output tokens: 0
- Reasoning output tokens: 0
- Arbiter verdict: `complete` / `ARBITER_COMPLETE`

The bundle intentionally excludes raw runner prompts, stdout/stderr, runner event streams, process env dumps, daemon logs, and pycache files.
