# Slice 3: Port Assets And Compiler Authority

Port the embedded asset surfaces and compiler-owned frozen plan behavior.

Goals:
- Package modes, graphs, stage-kind registry, entrypoints, and skills in the
  Rust crate.
- Port mode resolution, graph materialization, node materialization,
  completion behavior, learning triggers, and plane concurrency policy.
- Port compile-input fingerprints and current/stale/missing inspection.
- Implement `millrace compile validate` and enough `compile show` output to
  inspect the compiled authority.

Non-Goals:
- Do not implement runner execution in this slice.
- Do not hand-roll behavior outside the compiled-plan contract.

Acceptance:
- Rust `compile validate` succeeds for all built-in modes.
- `compiled_plan.json` matches the Python structure after normalizing ids,
  timestamps, and platform paths.
- Stale-plan refusal cases are covered.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/assets/`
- `../millrace-py/src/millrace_ai/compilation/`
- `../millrace-py/docs/runtime/millrace-compiler-and-frozen-plans.md`
- `../millrace-py/tests/integration/test_compiler.py`
