# Evidence Levels

This repository contains several kinds of evidence. They should not be treated
as interchangeable.

| Level | Name | Meaning |
| ---: | --- | --- |
| E0 | Narrative | Human-written explanation only. Useful orientation, not proof by itself. |
| E1 | Public release trail | Git tags, crate versions, package pages, release assets, and checksums. |
| E2 | Generated summaries | Metrics, CSVs, manifests, and notes derived from run artifacts. |
| E3 | Sanitized evidence bundle | Machine-readable artifacts with private paths, credentials, and unsafe raw files removed. |
| E4 | Raw private audit bundle | Full private logs/artifacts available only to a trusted auditor under an explicit review boundary. |
| E5 | Reproducible verifier | A command recomputes or validates metrics, checksums, file counts, and sanitizer policy. |
| E6 | Independent audit | A third party verifies a claim and states exactly what was and was not reviewed. |
| E7 | Public rerun | A clean-room public or controlled rerun reproduces the behavior. |

## Current Evidence By Claim

| Claim | Current public evidence level | Notes |
| --- | --- | --- |
| Initial Rust port `v0.1.0` | E3-E5 | Public bundle, generated metrics, checksums, and verifier are available. Raw runner streams are not public. |
| Rust crate efficacy smoke | E2-E3 | The smoke is documented and included in the `v0.1.0` proof package, but it is not a full parity proof. |
| Post-`v0.1.0` maintenance loop | E3-E5 | Each public Rust maintenance release has an evidence directory, bundle checksum, and verifier path. |
| Millracer downstream port | E3-E5 in separate repo for completed packets | This repo should point out to `millracer-rs-port-docs` rather than mix the claims. |
| Universal arbitrary software factory | No claim | No evidence level is assigned because this is outside the proof boundary. |

## Remaining Trust Multipliers

The most valuable future upgrades would be:

- E6: a narrow independent technical audit of the public bundles and verifier
  scripts.
- E7: a controlled public rerun of a small auto-port release, designed in
  advance for public audit rather than private workspace operation.

