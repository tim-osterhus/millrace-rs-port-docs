# Slice 5: Port Serial Runtime With Fake Runner

Implement the deterministic `run once` runtime path using a fake runner before
real Codex or Pi integration.

Goals:
- Port startup lifecycle, config loading, compile-if-needed behavior, and stale
  state reconciliation.
- Implement deterministic tick ordering.
- Implement claim ordering, stage request construction, fake runner dispatch,
  result persistence, routing, recovery counters, and status marker updates.
- Implement closure target and Arbiter activation behavior covered by Python
  tests.

Non-Goals:
- Do not run real Codex/Pi adapters in this slice.
- Do not implement daemon worker concurrency yet.

Acceptance:
- Fake-runner scenarios reproduce Python queue and state transitions.
- Runtime-owned mutation remains single-writer.
- Stage code never directly mutates authoritative queue state.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/runtime/tick_cycle.py`
- `../millrace-py/src/millrace_ai/runtime/result_application.py`
- `../millrace-py/tests/runtime/test_runtime.py`
- `../millrace-py/tests/integration/test_e2e_handoffs.py`
