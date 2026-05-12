# For Skeptics

This page answers the objections a careful reader should ask first.

## "Is this just a README story?"

No. The repository contains generated metrics, per-release evidence
directories, checksums, sanitizer reviews for post-`v0.1.0` packets, verifier
scripts, and release-asset tarballs.

Start with [`CLAIMS.md`](CLAIMS.md), then verify a bundle using
[`docs/how-to-verify.md`](docs/how-to-verify.md).

## "Did the Rust crate rebuild itself?"

Not for `v0.1.0`, and that is not the claim. Python Millrace drove the initial
Rust parity build. The stronger self-referential claim starts after the Rust
runtime exists: the auto-port maintenance loop uses the established runtime and
release gate to keep Rust releases tracking later Python releases.

## "Could a human have secretly edited the code?"

The public claim is narrower: no manual Rust code edits are claimed inside the
autonomous porting windows. The public bundles provide run, stage, task,
Arbiter, and release evidence, but they are sanitized and do not include a full
raw terminal/process replay.

See [`HUMAN_INTERVENTION_LEDGER.md`](HUMAN_INTERVENTION_LEDGER.md) for the
human-action boundary.

## "Was publishing manual?"

For `v0.1.0`, yes: release tagging, publishing, and repository administration
were operator actions outside the autonomous stage graph.

For later maintenance releases, publishing is handled by a deterministic
release gate when explicitly enabled. That gate is not a weakness; it is the
governance boundary. Millrace stages perform implementation, remediation, QA,
and Arbiter closure. The gate performs release authority actions only after
closure and checks.

## "Does this prove arbitrary autonomous software development?"

No. The strongest public proof is a bounded factory cell: Python-to-Rust parity
generation and maintenance for a known reference runtime. That is a serious
autonomy claim, but it is not universal software production from arbitrary
product ideas.

## "Are sanitized bundles enough?"

They are enough for the public E3-E5 claim: selected machine-readable artifacts,
checksums, generated metrics, and verifier scripts. They are not the same as an
E4 raw private audit or E7 public rerun.

See [`EVIDENCE_LEVELS.md`](EVIDENCE_LEVELS.md) and
[`REDACTION_POLICY.md`](REDACTION_POLICY.md).

## "Is Millracer proof part of this repo?"

No. Millracer is downstream proof that the same pattern can be applied to
another project. Its evidence belongs in
[`tim-osterhus/millracer-rs-port-docs`](https://github.com/tim-osterhus/millracer-rs-port-docs).

This repo should not mix completed Millrace proof with downstream Millracer
status updates.

## "What would falsify the claim?"

Examples:

- evidence showing human-authored Rust patches inside the claimed autonomous
  implementation window;
- release artifacts that do not match the claimed tags or checksums;
- Arbiter closure targets missing for claimed completed runs;
- generated metrics that cannot be reproduced from the published bundle or
  adjacent source artifacts;
- sanitizer output that removed or changed proof-critical fields rather than
  only private/security-sensitive data.

