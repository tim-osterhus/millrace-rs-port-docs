# How To Verify The v0.1.0 Evidence

The proof documents are intended to be reproducible. Against an adjacent
`millrace-rs` checkout, the verifier recomputes the published metrics from
Millrace artifacts and compares them to the committed summaries under
`evidence/v0.1.0/generated/`. Against the public release bundle, it verifies the
embedded summaries, selected stage-result count, checksums, and sanitizer policy
without requiring raw runner event streams to be public.

## Option 1: Verify Against An Adjacent Rust Checkout

Use this when `millrace-rs` is checked out next to this repository:

```bash
./scripts/verify_v0_1_0_evidence.sh
```

Equivalent explicit command:

```bash
python3 scripts/verify_v0_1_0_evidence.py --source ../millrace-rs
```

The command should end with:

```text
verification: ok
```

## Option 2: Verify A Downloaded Evidence Bundle

Download the release asset:

```text
v0.1.0-port-evidence.tar.gz
```

Then run:

```bash
python3 scripts/verify_v0_1_0_evidence.py \
  --bundle v0.1.0-port-evidence.tar.gz \
  --sha256 46f620b8a4054dd11a7e4db48dd358d713d2042c1e7255278f61081e64609e06
```

The verifier extracts the sanitized bundle to a temporary directory, rejects raw
runner/log members, checks for local path/host/token-shaped leaks, confirms the
embedded `metrics.json` matches the committed copy, and confirms the bundle
contains the expected 261 stage-result envelopes.

## Recreate The Bundle

From the development workspace:

```bash
python3 scripts/export_v0_1_0_evidence.py \
  --source ../millrace-rs \
  --output dist/v0.1.0-port-evidence.tar.gz
```

The exporter prints the bundle SHA256. It excludes raw runner event streams,
raw completion payloads, daemon logs, process environment dumps, and pycache
files; it also redacts local path roots, hostnames, and captured
auth/cookie-style header values before archiving. Upload the tarball as a
release asset and copy that hash into release notes.

## What Is Verified

- Count of recorded runs and stage results.
- Count of stage results with/without raw token usage.
- First stage start and last stage completion.
- Wall-clock campaign span and sum of stage durations.
- Token totals from the generated metrics derived from the original raw
  `turn.completed` events.
- Stage-call counts by plane/stage.
- Terminal-result counts.
- Result-class counts.
- Slice-level run, stage, work-item, duration, and token totals.
- Done task/spec counts and seeded-idea count.

## What Is Not Verified

The verifier does not rerun the whole autonomous build. The public bundle does
not include raw runner event streams, so bundle verification checks the embedded
public summaries and selected stage envelopes rather than recomputing token
usage from raw event logs. Re-executing the build would require the original
Python Millrace runtime, Codex credentials, network access, and a long-running
daemon session.
