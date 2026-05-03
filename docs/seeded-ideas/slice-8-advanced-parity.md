# Slice 8: Finish Advanced Runtime Parity

Close the remaining high-value parity gaps once contracts, compiler, CLI,
serial runtime, daemon runtime, and runners are in place.

Goals:
- Port usage governance and subscription quota telemetry behavior.
- Port learning promotions and skill evidence flows.
- Port closure lineage drift diagnostics and repair.
- Finish run inspection depth and E2E handoff scenarios.
- Document any intentionally preview-only Rust surfaces.

Non-Goals:
- Do not broaden the public extension surface beyond Python parity.
- Do not silently accept incompatible workspace artifacts.

Acceptance:
- Python fixture scenarios can be replayed through Rust.
- Usage-governance pause/resume behavior matches Python.
- Learning-plane evidence flows remain operator-controlled.
- Docs state which surfaces are fully compatible and which remain preview.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/runtime/usage_governance/`
- `../millrace-py/src/millrace_ai/runtime/learning_promotions.py`
- `../millrace-py/src/millrace_ai/workspace/lineage_integrity.py`
- `../millrace-py/tests/runtime/test_usage_governance.py`
