# Downstream Millracer Port

This page keeps downstream Millracer evidence separate from the Millrace Rust
port proof.

## Claim Boundary

Millracer is a downstream application of the auto-port pattern. It is not the
same claim as "Millrace generated and maintained its own Rust parity port."

The useful downstream claim is:

> The Rust Millrace runtime can be used as the porting engine for another
> Python-to-Rust parity project.

## Evidence Location

Millracer evidence belongs in the separate public repository:

[`tim-osterhus/millracer-rs-port-docs`](https://github.com/tim-osterhus/millracer-rs-port-docs)

That repository should carry its own:

- claim matrix
- evidence bundles
- human-intervention ledger
- redaction policy
- verification instructions
- per-release proof pages

## Why Keep It Separate

The Millrace Rust proof and Millracer proof have different:

- Python source versions
- Rust crate versions
- release gates
- runtime state
- auto-port ideas
- Arbiter targets
- evidence packets

Keeping them separate prevents a completed Millrace proof from being weakened by
an in-progress downstream run, and prevents a downstream success from obscuring
the more specific Millrace parity-maintenance claim.

