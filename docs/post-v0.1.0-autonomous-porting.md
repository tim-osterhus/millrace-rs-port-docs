# Post-v0.1.0 Autonomous Porting

This note summarizes what the Millrace Rust port has done after the initial
`millrace-ai` `v0.1.0` autonomous build proof. It is intentionally a public
reader summary: it records release outcomes, parity targets, and sanitized
operational facts, not raw daemon logs or private workspace state.

As of 2026-05-12, the Rust port has continued from a one-time proof into an
autonomous maintenance loop for the `millrace-ai` crate. The same pattern is
also being applied to a second project, `millracer`, whose evidence belongs in
the separate `millracer-rs-port-docs` repository.

## Public Release Timeline

| Rust crate release | Python reference range | Result |
| --- | --- | --- |
| `millrace-ai` `v0.1.0` | Python Millrace `v0.16.1` | Initial autonomous Rust port proof. |
| `millrace-ai` `v0.2.0` | `v0.16.1` to `v0.17.3` | First autonomous maintenance release after the proof run. |
| `millrace-ai` `v0.2.1` | `v0.17.3` to `v0.17.4` | Patch-level parity release for learning-plane updates. |
| `millrace-ai` `v0.3.0` | `v0.17.4` to `v0.18.0` | Minor parity release for graph and trace inspection surfaces. |
| `millrace-ai` `v0.3.1` | `v0.18.0` to `v0.18.1` | Patch-level parity release for Recon and probe queue surfaces. |
| `millrace-ai` `v0.3.2` | `v0.18.1` to `v0.18.2` | Patch-level parity release for Integrator assets, integrated modes, and status diagnostics. |

The latest published Rust crate verified from crates.io during this update was
`millrace-ai` `v0.3.2`. The Rust repository tag history also contains
`v0.2.0`, `v0.2.1`, `v0.3.0`, `v0.3.1`, and `v0.3.2` after the original
`v0.1.0` proof release.

## What Changed After The Proof

The original proof showed that Python Millrace could autonomously build a
usable Rust port of itself. The follow-on work changed the evidence from "one
large autonomous build happened" into "a durable auto-port maintenance loop can
keep a Rust port moving as the Python reference changes."

The private operational loop now performs these deterministic steps around the
Millrace runtime:

1. Fetch and inspect the adjacent Python reference checkout.
2. Detect the latest Python semver tag.
3. Compute the next Rust crate version from the configured version policy.
4. Enqueue one auto-port idea through the Millrace CLI.
5. Wait for Arbiter closure over the full lineage of generated work.
6. Run deterministic release checks.
7. When explicitly enabled, commit, tag, push, publish the crate, and update the
   local release state ledger.

Normal Millrace stages still do not publish, push, tag, or upload artifacts.
Those actions remain outside the stage graph in a deterministic release gate.

## Version Policy In Practice

The maintenance loop follows the policy used in the release timeline:

- a Python minor-version jump maps to a Rust minor-version bump;
- a Python patch-version jump maps to a Rust patch-version bump.

For example, the Python `v0.16.1` to `v0.17.3` jump moved Rust from `0.1.0` to
`0.2.0`, while the Python `v0.17.3` to `v0.17.4` jump moved Rust from `0.2.0`
to `0.2.1`.

## Release Highlights

`v0.2.0` carried the first autonomous maintenance release after the initial
proof. It recorded parity for runner-neutral thinking-level behavior, Codex
reasoning-effort compatibility, Pi thinking mapping, daemon monitor idle
throttling, closure-target actionability, task lifecycle integrity, and an
explicit unsupported-gap decision for the optional Python web dashboard.

`v0.2.1` carried learning-plane parity for no-op terminal outcomes, the `no_op`
result class, Analyst-first generic learning, direct Curator trigger
destination safety, and run-inspection/runtime JSON no-op coverage.

`v0.3.0` carried compiled-stage-graph exports, run-trace persistence and
inspection, and read-only graph/trace CLI commands. It also preserved the
dashboard/web package as an explicit unsupported Rust gap rather than silently
pretending the Rust crate shipped that surface.

`v0.3.1` carried Recon/probe parity: probe work documents, Recon packet
contracts, Recon managed assets, probe queue lifecycle, add-probe CLI/mailbox
behavior, and runtime Recon routing/result application.

`v0.3.2` carried Integrator and integrated-mode parity: Integrator managed
assets, opt-in integrated Codex modes, status JSON diagnostics, invalid Recon
handoff hardening, graph validation guards, stage/work-item ownership
validation, package include readiness, and another explicit optional-web
unsupported-gap record.

Across these releases, the Rust crate kept the web dashboard and native watcher
surfaces as explicit known gaps where the Rust project intentionally remained a
CLI/runtime crate rather than a full Python package mirror.

## Second Harness: Millracer

The same auto-port pattern has also been adapted for a second project:
`millracer`.

The downstream evidence should be read in
[`tim-osterhus/millracer-rs-port-docs`](https://github.com/tim-osterhus/millracer-rs-port-docs),
not in this repository. This repo may point to that work, but should not mix
Millrace self-port claims with Millracer release claims.

The reason to mention Millracer here is narrow: it demonstrates the next use of
the same loop, using the Rust Millrace runtime and established auto-port harness
pattern to pursue parity for another Python project.

## Learning Feedback

The post-proof runs also exercised Millrace's learning plane. During the
Millracer run, Checker found a subtle Python-to-Rust parity issue around JSON
truthiness and alias fallback. The run then triggered a learning request:

- Analyst researched the incident and identified the reusable lesson.
- Professor drafted a narrow patch for the `millracer-auto-port-parity` skill.
- Curator was responsible for deciding whether to apply the patch.

The lesson was concrete: when a Python reference uses `payload.get(...) or ...`,
alias fallback, truthy checks, or normalization helpers, the Rust port must
distinguish between a key merely being present and the value being usable. That
learning event is useful because it shows the porting loop can convert a caught
parity miss into future-stage guidance.

## Evidence Boundaries

This document deliberately avoids committing raw daemon logs, runner prompts,
local paths, terminal captures, environment variables, or machine-specific
process state. The public evidence value is the sequence of published crate
versions, release notes, parity targets, deterministic release-gate behavior,
and sanitized status summaries.

For the original raw proof bundle and recomputable `v0.1.0` metrics, see
[Autonomous build proof](v0.1.0-autonomous-build-proof.md) and
[How to verify](how-to-verify.md).
