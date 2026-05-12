# Claims

This repository supports a scoped autonomy claim. It does not ask the reader to
accept a slogan first and reconstruct the boundaries later.

## Canonical Claim

Millrace has demonstrated a bounded Level 5 autonomous software-factory cell for
Python-to-Rust parity generation and maintenance. Python Millrace autonomously
produced the first Rust parity implementation of Millrace, and the follow-on
auto-port loop has kept the Rust crate tracking later Python releases through
verified evidence bundles. This does not prove universal Level 5 autonomy for
arbitrary software products.

## Claim Matrix

| Claim | Status | What it proves | What it does not prove | Evidence |
| --- | --- | --- | --- | --- |
| Python Millrace built Rust Millrace `v0.1.0` | Publicly evidenced | A large autonomous Python-Millrace-driven Rust parity campaign completed across seeded specs, tasks, fixes, and Arbiter closure. | The Rust crate did not self-host or rebuild itself for the initial port. Publishing and repository administration were outside the stage graph. | [`docs/01-initial-rust-port-v0.1.0.md`](docs/01-initial-rust-port-v0.1.0.md), [`docs/v0.1.0-autonomous-build-proof.md`](docs/v0.1.0-autonomous-build-proof.md), [`evidence/v0.1.0/`](evidence/v0.1.0/) |
| Published Rust crate can execute real Millrace work | Publicly evidenced smoke | The `millrace-ai v0.1.0` crate ran a real Codex-backed daemon path and completed a filesystem task through `builder -> checker -> updater`. | It does not prove every runtime surface, long unattended operation, Pi behavior, or learning behavior. | [`docs/rust-efficacy-run.md`](docs/rust-efficacy-run.md) |
| Post-`v0.1.0` Rust maintenance loop | Strongest public claim | A bounded auto-port maintenance loop detected Python releases, generated Rust parity work, waited for Arbiter closure, ran release checks, and produced Rust releases through `v0.3.2`. | It does not prove arbitrary greenfield software development or independent product-direction invention. The Python reference remains the upstream source of truth. | [`docs/02-autonomous-maintenance-loop-v0.2.0-v0.3.2.md`](docs/02-autonomous-maintenance-loop-v0.2.0-v0.3.2.md), [`evidence/v0.2.0/`](evidence/v0.2.0/), [`evidence/v0.2.1/`](evidence/v0.2.1/), [`evidence/v0.3.0/`](evidence/v0.3.0/), [`evidence/v0.3.1/`](evidence/v0.3.1/), [`evidence/v0.3.2/`](evidence/v0.3.2/) |
| Downstream Millracer port | Separate downstream proof | The same harness pattern is being applied outside Millrace itself, using Rust Millrace to port Millracer. | This repository is not the Millracer proof package; Millracer release claims belong in the separate Millracer evidence repository. | [`docs/03-downstream-millracer-rs-port.md`](docs/03-downstream-millracer-rs-port.md), [`tim-osterhus/millracer-rs-port-docs`](https://github.com/tim-osterhus/millracer-rs-port-docs) |
| Universal Level 5 software factory | Not claimed | Nothing in this repository needs that broad claim to be true. | It does not prove arbitrary autonomous product creation across unknown domains. | This boundary is intentional. |

## Classification

The clean public classification is:

> Bounded Level 5 autonomous software-factory cell for Rust parity maintenance
> of a Python reference runtime.

That wording is intentionally narrower than "universal software factory" and
more precise than "rebuilt itself." It preserves the actual accomplishment
without letting a broader, easier-to-attack claim obscure the evidence.

