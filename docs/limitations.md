# Limitations

This repository is a proof package, not a magical eraser for all uncertainty.
It aims to make the Rust-port campaign inspectable and mechanically checkable,
while being precise about the claim.

For the full claim matrix, read [`../CLAIMS.md`](../CLAIMS.md) first. The
cleanest classification is "bounded Level 5 autonomous software-factory cell
for Python-to-Rust parity maintenance," not "universal software factory."

## What The v0.1.0 Proof Claims

- Python Millrace v0.16.1 accepted eight seeded parity ideas for a Rust port.
- It decomposed those ideas into specs, tasks, closure targets, and remediation
  work.
- It ran a large Codex-backed implementation campaign through Millrace runtime
  stages.
- It produced the Rust `millrace-ai` v0.1.0 parity implementation.
- The campaign left completed work artifacts, arbiter verdicts, run artifacts,
  and token/timing evidence.
- The published Rust crate later passed a separate real daemon smoke test.

## What The v0.1.0 Proof Does Not Claim

- It does not claim the Rust crate autonomously rebuilt itself.
- It does not claim universal autonomous software development across arbitrary
  projects.
- It does not claim the proof documents alone contain every raw artifact.
- It does not claim every future Rust surface is stable API.
- It does not claim Pi live-runner behavior was proven in the post-publish
  smoke, because the local Pi RPC CLI was not available for that check.
- It does not claim that publishing, release tagging, repository administration,
  or independent verification were autonomous.

## Known Evidence Boundaries

- Token totals come from 254 raw Codex `turn.completed` usage payloads.
- Seven recorded stage results had no usage payload and are excluded from token
  totals while still counted in stage, timing, and terminal-result metrics.
- The sanitized public evidence bundle is expected to be distributed as a
  release asset rather than committed directly to git.
- The public bundle excludes raw runner event streams, raw completion payloads,
  daemon logs, process environment dumps, and pycache files.
- The public bundle redacts local path roots, hostnames, and captured
  auth/cookie-style header values before publication.
- The verifier checks metrics against raw artifacts when an adjacent development
  checkout is available. For the public bundle, it checks embedded summaries,
  stage envelopes, checksums, and sanitizer policy; it does not replay the
  original long-running agent work.
- The public evidence does not prove an absence of all human observation. It
  supports narrower claims such as no manual Rust code edits inside the
  autonomous porting window and release-gate-driven publishing for later
  maintenance releases.

For the human-action boundary, see
[`../HUMAN_INTERVENTION_LEDGER.md`](../HUMAN_INTERVENTION_LEDGER.md). For the
redaction boundary, see [`../REDACTION_POLICY.md`](../REDACTION_POLICY.md).

## Why This Is Still Useful

The evidence is strong because it is not just a success story. It includes
non-happy-path routing: blocked stages, fix-needed checker outcomes, fixers,
doublecheckers, arbiter remediation, and deferred learning requests. Those
artifacts show Millrace operating as a runtime with state, recovery, and closure
behavior rather than as a one-shot prompt wrapper.
