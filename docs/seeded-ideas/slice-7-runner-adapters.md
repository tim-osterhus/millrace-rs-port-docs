# Slice 7: Port Runner Adapters

Port real runner integrations after fake-runner runtime parity exists.

Goals:
- Port runner request construction, registry, dispatcher, and normalization.
- Port Codex CLI command construction, artifact capture, timeout handling, and
  token extraction.
- Port Pi RPC JSONL transport and adapter behavior.
- Preserve run artifact contracts used by Python run inspection.

Non-Goals:
- Do not make real runner tests mandatory in normal CI.
- Do not change compiled-plan semantics while porting adapters.

Acceptance:
- Adapter artifacts match the Python contract after normalization.
- Fake runner remains the default CI path.
- Real adapters have smoke tests gated behind explicit environment variables.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/runners/`
- `../millrace-py/docs/runtime/millrace-runner-architecture.md`
- `../millrace-py/tests/runners/`
