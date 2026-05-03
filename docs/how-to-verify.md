# How To Verify The v0.1.0 Evidence

The proof documents are intended to be reproducible. The verifier recomputes the
published metrics from sanitized raw Millrace artifacts and compares them to the
committed summaries under `evidence/v0.1.0/generated/`.

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
  --sha256 faffab654195d12b97788b35882435fcc35d64c4b9e0c26ec6468dee9fff4293
```

The verifier extracts the sanitized bundle to a temporary directory, recomputes
the stage, run, token, slice, task, spec, incident, and timing metrics, and
compares them to the committed `metrics.json`.

## Recreate The Bundle

From the development workspace:

```bash
python3 scripts/export_v0_1_0_evidence.py \
  --source ../millrace-rs \
  --output dist/v0.1.0-port-evidence.tar.gz
```

The exporter prints the bundle SHA256. It redacts local path roots and captured
auth/cookie-style header values before archiving. Upload the tarball as a
release asset and copy that hash into release notes.

## What Is Verified

- Count of recorded runs and stage results.
- Count of stage results with/without raw token usage.
- First stage start and last stage completion.
- Wall-clock campaign span and sum of stage durations.
- Token totals from raw `turn.completed` events.
- Stage-call counts by plane/stage.
- Terminal-result counts.
- Result-class counts.
- Slice-level run, stage, work-item, duration, and token totals.
- Done task/spec counts and seeded-idea count.

## What Is Not Verified

The verifier does not rerun the whole autonomous build. It checks that the
published proof metrics match the provided sanitized raw artifact bundle.
Re-executing the build would require the original Python Millrace runtime, Codex
credentials, network access, and a long-running daemon session.
