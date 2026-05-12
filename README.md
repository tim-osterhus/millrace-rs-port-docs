# Millrace Rust Port Documentation

This repository is the public evidence and narrative package for the autonomous
Rust port of Millrace.

The Rust crate itself lives at
[`tim-osterhus/millrace-rs`](https://github.com/tim-osterhus/millrace-rs). That
repository is intentionally utilitarian: install, use, test, and evolve the
Rust crate. This repository carries the heavier proof material: the port
roadmap, seeded ideas, autonomous-build metrics, raw-evidence verification
scripts, and post-publish efficacy notes.

## Start Here

- [Autonomous build proof](docs/v0.1.0-autonomous-build-proof.md): detailed
  metrics for the Python Millrace v0.16.1 campaign that built
  `millrace-ai` v0.1.0 in Rust.
- [How to verify](docs/how-to-verify.md): one-command checks for recomputing
  the published metrics from raw artifacts.
- [Limitations](docs/limitations.md): what the proof does and does not claim.
- [Public reader guide](docs/public-reader-guide.md): a short orientation for
  readers who are new to Millrace.
- [Rust port roadmap](docs/rust-port-roadmap.md): the original parity plan.
- [Seeded ideas](docs/seeded-ideas/): the eight large work slices fed into
  Millrace.
- [Post-publish Rust efficacy run](docs/rust-efficacy-run.md): a live smoke of
  the published Rust crate.
- [Post-v0.1.0 autonomous porting](docs/post-v0.1.0-autonomous-porting.md):
  what happened after the initial proof, including the Rust maintenance releases
  through `millrace-ai` `v0.3.2` and the in-progress Millracer harness.

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

These figures are generated from the raw Millrace run artifacts, not hand
counted. The generated summaries live under
[`evidence/v0.1.0/generated/`](evidence/v0.1.0/generated/).

## After The Initial Proof

The Rust port has continued beyond `v0.1.0`. As of 2026-05-12, the public
`millrace-ai` crate has advanced through `v0.3.2`, tracking Python Millrace
through `v0.18.2` by way of the autonomous auto-port loop. The same harness
pattern is also being applied to the separate `millracer` crate, where a
bootstrap parity run from Python `millracer` `v0.1.4` to Rust `0.1.1` is in
progress.

See [Post-v0.1.0 autonomous porting](docs/post-v0.1.0-autonomous-porting.md)
for the release timeline, version policy, and public-safe status summary.

## Post-v0.1.0 Evidence

The follow-on port runs are tracked as one evidence directory per Rust release.
The generated summaries and checksums are committed; the matching tarballs are
release-asset candidates and are intentionally kept out of git.

| Rust release | Evidence directory | Bundle SHA256 |
| --- | --- | --- |
| `v0.2.0` | [`evidence/v0.2.0/`](evidence/v0.2.0/) | `39f4797d629810a5d6a82457343b0ee3351351dc2c342dfe1593ac70c91d94be` |
| `v0.2.1` | [`evidence/v0.2.1/`](evidence/v0.2.1/) | `6bc0e5da724c426c4450fe02e5472da6b7663111039fb6308f5493c82b608ca7` |
| `v0.3.0` | [`evidence/v0.3.0/`](evidence/v0.3.0/) | `286aabfd4c476de458ba53d661368e6471fa7ca0c4f21ba2fef13fcef4e25123` |
| `v0.3.1` | [`evidence/v0.3.1/`](evidence/v0.3.1/) | `3f7940f6c4df5a37d3f280d1942da8da844e93cf6d2cdc67a78c999c82d8522e` |
| `v0.3.2` | [`evidence/v0.3.2/`](evidence/v0.3.2/) | `2c9dc315483ea8e911c1011b9b989d8d9c1324e731a1ca1e97bbed1f7f1e0987` |

You can recreate and verify those bundles with:

```bash
python3 scripts/export_post_v0_1_0_evidence.py --source ../millrace-rs --versions all
python3 scripts/verify_post_v0_1_0_evidence.py \
  --bundle dist/v0.3.2-port-evidence.tar.gz \
  --version 0.3.2 \
  --sha256 2c9dc315483ea8e911c1011b9b989d8d9c1324e731a1ca1e97bbed1f7f1e0987
```

## Evidence Bundle

The sanitized raw evidence bundle is intentionally not committed to git because
it is large and mostly machine-readable run artifacts. The exporter redacts
local path roots and captured auth/cookie-style header values before archiving;
those redactions do not affect the metrics the verifier recomputes. The
expected public artifact is a release asset named:

```text
v0.1.0-port-evidence.tar.gz
```

Local export details from this workspace:

- Files in bundle: 940
- SHA256: `faffab654195d12b97788b35882435fcc35d64c4b9e0c26ec6468dee9fff4293`
- Release: [`v0.1.0`](https://github.com/tim-osterhus/millrace-rs-port-docs/releases/tag/v0.1.0)
- Download: [`v0.1.0-port-evidence.tar.gz`](https://github.com/tim-osterhus/millrace-rs-port-docs/releases/download/v0.1.0/v0.1.0-port-evidence.tar.gz)

If you have an adjacent checkout of `millrace-rs`, you can recreate that bundle:

```bash
python3 scripts/export_v0_1_0_evidence.py --source ../millrace-rs --output dist/v0.1.0-port-evidence.tar.gz
```

Then verify the metrics:

```bash
python3 scripts/verify_v0_1_0_evidence.py \
  --bundle dist/v0.1.0-port-evidence.tar.gz \
  --sha256 faffab654195d12b97788b35882435fcc35d64c4b9e0c26ec6468dee9fff4293
```

For the local workspace layout used during development, this shorter command is
equivalent:

```bash
./scripts/verify_v0_1_0_evidence.sh
```

## License

This documentation is licensed under Apache-2.0. See [LICENSE](LICENSE).
