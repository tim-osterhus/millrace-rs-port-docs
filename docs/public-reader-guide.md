# Public Reader Guide

This guide is for readers who are not already inside the Millrace project.

## What Is Millrace?

Millrace is a local runtime for agent work that is too long-running or
stateful for a single chat session. It owns queues, compiled plans, runtime
state, stage routing, recovery paths, and closure checks around local agent
tools such as Codex.

## What Was Built?

The Python Millrace runtime was used to build a Rust crate named
`millrace-ai`. The Rust crate exposes a `millrace` binary and ports the
operator-visible behavior of the Python runtime:

- workspace initialization
- queue intake and inspection
- config, mode, status, doctor, and upgrade commands
- serial and daemon runtime paths
- runner request/result artifacts
- Codex and Pi adapter contracts
- Arbiter, closure, recovery, learning, and usage-governance surfaces

## What Is The Proof?

The proof is not a screenshot or a single demo. It is a structured audit trail:

- 8 seeded ideas
- 11 completed specs
- 57 completed tasks
- 99 recorded runs
- 261 recorded stage calls
- raw Codex event streams with token usage
- Arbiter verdicts and remediation records
- a released Rust v0.1.0 crate
- a post-publish smoke test of that crate

The detailed proof is in
[`v0.1.0-autonomous-build-proof.md`](v0.1.0-autonomous-build-proof.md).

## How Should I Read This Repository?

1. Read the [claim matrix](../CLAIMS.md) so the proof boundary is clear.
2. Read [For skeptics](../FOR_SKEPTICS.md) for the direct caveats.
3. Read the [README](../README.md) for the short version.
4. Read the [limitations](limitations.md) and
   [human-intervention ledger](../HUMAN_INTERVENTION_LEDGER.md).
5. Skim the [seeded ideas](seeded-ideas/) to understand the work slices.
6. Open the [proof document](v0.1.0-autonomous-build-proof.md) for metrics.
7. Run the [verifier](how-to-verify.md) if you want mechanical confirmation.

## Why Is This Separate From `millrace-rs`?

The Rust crate repository should stay focused on the actual crate: source,
tests, install instructions, and concise developer docs. This repository is the
case study and audit trail for how that crate was produced.
