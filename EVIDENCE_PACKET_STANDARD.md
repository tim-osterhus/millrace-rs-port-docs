# Evidence Packet Standard

Future evidence packets should be generated in a consistent shape so readers do
not have to infer what each release proves.

## Required Public Files

Each release packet should include:

- `README.md`
- `manifest.json`
- `claim-boundary.json`
- `human-intervention-ledger.json`
- `generated/metrics.json`
- `generated/stage-summary.csv`
- `generated/run-summary.csv` for post-`v0.1.0` packets
- `generated/sanitizer-review.json`
- `generated/checksums.sha256`
- `tarball.sha256`
- `dist/vX.Y.Z-port-evidence.tar.gz`

## `claim-boundary.json`

This file should state:

- the exact Rust version;
- the exact Python source range;
- the auto-port idea id;
- the runtime engine;
- the claim being made;
- the claims explicitly not being made;
- the evidence level;
- links to the relevant docs.

## `human-intervention-ledger.json`

This file should state, per release:

- whether a human authored source changes;
- whether a human edited generated Rust code;
- whether a human prompted mid-run;
- whether a human directly mutated queues;
- whether the release gate committed/tagged/pushed/published;
- whether evidence packaging was manual or automated.

## `sanitizer-review.json`

This file should report:

- redaction rules applied;
- rejected file classes;
- issue count;
- zero sanitizer issues for publishable bundles.

If the issue count is nonzero, the packet should not be published.

## Blogger Integration

The planned Blogger flow should generate these files automatically after a
successful Arbiter-closed release. It should publish evidence independently
from crate release state so a docs push failure cannot trigger duplicate crate
publishing.

