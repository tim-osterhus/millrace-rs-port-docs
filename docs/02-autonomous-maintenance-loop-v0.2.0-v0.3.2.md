# Autonomous Maintenance Loop: v0.2.0 Through v0.3.2

This is the strongest public autonomy claim in this repository.

## Claim

After the initial Rust port existed, the auto-port loop maintained the Rust
`millrace-ai` crate against later Python Millrace releases. It detected Python
version changes, generated Rust parity work, waited for Arbiter closure, ran
release checks, and produced Rust releases through `v0.3.2`.

## Why This Is Different From v0.1.0

The `v0.1.0` proof is a large Python-Millrace-driven build campaign. The
post-`v0.1.0` loop is a maintenance factory cell: a Python reference changes,
the Rust parity target is computed, the work is queued, the runtime executes
and closes it, and the release gate ships the resulting Rust crate when enabled.

## Release Evidence

| Rust release | Python reference range | Stage results | Runs | Work items | Wall time | Bundle SHA256 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `v0.2.0` | `v0.16.1 -> v0.17.3` | 32 | 11 | 11 | 3h 51m 58.4s | `39f4797d629810a5d6a82457343b0ee3351351dc2c342dfe1593ac70c91d94be` |
| `v0.2.1` | `v0.17.3 -> v0.17.4` | 16 | 6 | 6 | 2h 33m 13.7s | `6bc0e5da724c426c4450fe02e5472da6b7663111039fb6308f5493c82b608ca7` |
| `v0.3.0` | `v0.17.4 -> v0.18.0` | 19 | 7 | 7 | 2h 31m 8.9s | `286aabfd4c476de458ba53d661368e6471fa7ca0c4f21ba2fef13fcef4e25123` |
| `v0.3.1` | `v0.18.0 -> v0.18.1` | 25 | 9 | 9 | 3h 42m 4.2s | `3f7940f6c4df5a37d3f280d1942da8da844e93cf6d2cdc67a78c999c82d8522e` |
| `v0.3.2` | `v0.18.1 -> v0.18.2` | 30 | 9 | 9 | 4h 32m 6.8s | `2c9dc315483ea8e911c1011b9b989d8d9c1324e731a1ca1e97bbed1f7f1e0987` |

## Release Gate Boundary

The autonomous factory has two layers:

- Millrace stages perform implementation, remediation, checking, updating, and
  Arbiter closure.
- The deterministic release gate performs packaging and release actions only
  after the runtime reaches a verified closure state.

That separation is intentional. It makes release authority explicit instead of
burying publishing inside arbitrary stage output.

## What This Proves

- The Rust port continued tracking the Python reference after the initial proof.
- Each follow-on release has a version-scoped evidence directory and bundle
  checksum.
- The loop operated inside a bounded Python-to-Rust parity maintenance domain.

## What This Does Not Prove

- It does not prove arbitrary greenfield product creation.
- It does not prove that Millrace invents upstream product direction; Python
  Millrace remains the reference.
- It does not provide a public raw forensic replay of every process and
  terminal event.

## Evidence

- Reader summary: [`post-v0.1.0-autonomous-porting.md`](post-v0.1.0-autonomous-porting.md)
- Evidence directories:
  [`../evidence/v0.2.0/`](../evidence/v0.2.0/),
  [`../evidence/v0.2.1/`](../evidence/v0.2.1/),
  [`../evidence/v0.3.0/`](../evidence/v0.3.0/),
  [`../evidence/v0.3.1/`](../evidence/v0.3.1/),
  [`../evidence/v0.3.2/`](../evidence/v0.3.2/)

