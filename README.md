# Millrace Rust Port Evidence

This repository is the public evidence package for Millrace's Rust port and
follow-on Rust parity maintenance loop.

The short version:

> Millrace has demonstrated a bounded Level 5 autonomous software-factory cell
> for Python-to-Rust parity generation and maintenance. It has not demonstrated
> universal Level 5 autonomy for arbitrary software products.

The Rust crate itself lives at
[`tim-osterhus/millrace-rs`](https://github.com/tim-osterhus/millrace-rs). This
repository carries the proof material: claim boundaries, evidence bundles,
metrics, verification scripts, redaction policy, and reader-facing summaries.

## Read This First

- [`CLAIMS.md`](CLAIMS.md): the claim matrix, including what is and is not
  proven.
- [`FOR_SKEPTICS.md`](FOR_SKEPTICS.md): direct answers to the obvious skeptical
  objections.
- [`HUMAN_INTERVENTION_LEDGER.md`](HUMAN_INTERVENTION_LEDGER.md): where humans
  acted, where the release gate acted, and where no manual code edits are
  claimed.
- [`EVIDENCE_LEVELS.md`](EVIDENCE_LEVELS.md): what kind of evidence each claim
  has.
- [`REDACTION_POLICY.md`](REDACTION_POLICY.md): what the public bundles remove
  and why.

## Proof Tracks

| Track | Status | Start here |
| --- | --- | --- |
| Initial Rust port | Publicly evidenced | [`docs/01-initial-rust-port-v0.1.0.md`](docs/01-initial-rust-port-v0.1.0.md) |
| Published Rust crate efficacy smoke | Publicly evidenced smoke | [`docs/rust-efficacy-run.md`](docs/rust-efficacy-run.md) |
| Post-`v0.1.0` autonomous maintenance loop | Strongest public claim | [`docs/02-autonomous-maintenance-loop-v0.2.0-v0.3.2.md`](docs/02-autonomous-maintenance-loop-v0.2.0-v0.3.2.md) |
| Runtime recovery after external abort | Public operational evidence | [`docs/04-runtime-recovery-after-openclaw-abort.md`](docs/04-runtime-recovery-after-openclaw-abort.md) |
| Downstream Millracer port | Separate downstream evidence repo | [`docs/03-downstream-millracer-rs-port.md`](docs/03-downstream-millracer-rs-port.md) |

## Headline v0.1.0 Metrics

| Metric | Value |
| --- | ---: |
| Seeded ideas | 8 |
| Completed specs | 11 |
| Completed tasks | 57 |
| Recorded runs | 99 |
| Recorded stage calls | 261 |
| Stage calls with token usage | 254 |
| Wall-clock campaign span | 28h 9m 49.5s |
| Input tokens | 726,741,873 |
| Cached input tokens | 693,844,224 |
| Output tokens | 3,664,884 |
| Reasoning output tokens | 1,268,285 |

These figures are generated from Millrace run artifacts, not hand counted. The
generated summaries live under
[`evidence/v0.1.0/generated/`](evidence/v0.1.0/generated/).

## Post-v0.1.0 Evidence

The follow-on port runs are tracked as one evidence directory per Rust release.
The generated summaries and checksums are committed; matching tarballs are
published as release assets and may also exist locally under `dist/`.

| Rust release | Python range | Evidence directory | Bundle SHA256 |
| --- | --- | --- | --- |
| `v0.2.0` | `v0.16.1 -> v0.17.3` | [`evidence/v0.2.0/`](evidence/v0.2.0/) | `39f4797d629810a5d6a82457343b0ee3351351dc2c342dfe1593ac70c91d94be` |
| `v0.2.1` | `v0.17.3 -> v0.17.4` | [`evidence/v0.2.1/`](evidence/v0.2.1/) | `6bc0e5da724c426c4450fe02e5472da6b7663111039fb6308f5493c82b608ca7` |
| `v0.3.0` | `v0.17.4 -> v0.18.0` | [`evidence/v0.3.0/`](evidence/v0.3.0/) | `286aabfd4c476de458ba53d661368e6471fa7ca0c4f21ba2fef13fcef4e25123` |
| `v0.3.1` | `v0.18.0 -> v0.18.1` | [`evidence/v0.3.1/`](evidence/v0.3.1/) | `3f7940f6c4df5a37d3f280d1942da8da844e93cf6d2cdc67a78c999c82d8522e` |
| `v0.3.2` | `v0.18.1 -> v0.18.2` | [`evidence/v0.3.2/`](evidence/v0.3.2/) | `2c9dc315483ea8e911c1011b9b989d8d9c1324e731a1ca1e97bbed1f7f1e0987` |
| `v0.3.4` | `v0.18.3 -> v0.18.4` | [`evidence/v0.3.4/`](evidence/v0.3.4/) | `6d1e55511696b16349e9e16732069751c11f5a2b4079ed5557b01bd18563c6b3` |
| `v0.3.5` | `v0.18.4 -> v0.18.6` | [`evidence/v0.3.5/`](evidence/v0.3.5/) | `19b91453d2db72bae2ba48d473ae93a9323804262b6f8d483e5bef92828bfc8c` |
| `v0.4.0` | `v0.18.6 -> v0.19.0` | [`evidence/v0.4.0/`](evidence/v0.4.0/) | `2baca79899161030ce771cb503f4eb12d0763519472c0c7b5bdab900bf5a7b77` |
| `v0.5.0` | `v0.19.0 -> v0.20.0` | [`evidence/v0.5.0/`](evidence/v0.5.0/) | `518077224e96fa020183271ee19403a470d2f10dbbab9087e640cf398793c844` |Verify one of these bundles with:

```bash
python3 scripts/verify_post_v0_1_0_evidence.py \
  --bundle dist/v0.3.2-port-evidence.tar.gz \
  --version 0.3.2 \
  --sha256 2c9dc315483ea8e911c1011b9b989d8d9c1324e731a1ca1e97bbed1f7f1e0987
```

## v0.1.0 Evidence Bundle

The initial sanitized public bundle is published as:

[`v0.1.0-port-evidence.tar.gz`](https://github.com/tim-osterhus/millrace-rs-port-docs/releases/download/v0.1.0/v0.1.0-port-evidence.tar.gz)

Bundle details:

- Files in bundle: 386
- SHA256: `46f620b8a4054dd11a7e4db48dd358d713d2042c1e7255278f61081e64609e06`
- Release: [`v0.1.0`](https://github.com/tim-osterhus/millrace-rs-port-docs/releases/tag/v0.1.0)

Verify it with:

```bash
python3 scripts/verify_v0_1_0_evidence.py \
  --bundle dist/v0.1.0-port-evidence.tar.gz \
  --sha256 46f620b8a4054dd11a7e4db48dd358d713d2042c1e7255278f61081e64609e06
```

## Supporting Docs

- [`docs/how-to-verify.md`](docs/how-to-verify.md): verification commands and
  verifier boundaries.
- [`docs/limitations.md`](docs/limitations.md): residual caveats.
- [`docs/public-reader-guide.md`](docs/public-reader-guide.md): orientation for
  readers new to Millrace.
- [`docs/04-runtime-recovery-after-openclaw-abort.md`](docs/04-runtime-recovery-after-openclaw-abort.md):
  an observed recovery event where the live auto-port daemon resumed after an
  external process-tree abort.
- [`docs/rust-port-roadmap.md`](docs/rust-port-roadmap.md): the original parity
  plan.
- [`docs/seeded-ideas/`](docs/seeded-ideas/): the eight large work slices fed
  into Millrace.
- [`EVIDENCE_PACKET_STANDARD.md`](EVIDENCE_PACKET_STANDARD.md): the desired
  generated shape for future Blogger-produced packets.

## License

This documentation is licensed under Apache-2.0. See [LICENSE](LICENSE).
