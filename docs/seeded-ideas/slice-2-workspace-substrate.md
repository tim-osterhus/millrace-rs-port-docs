# Slice 2: Port Workspace Substrate

Implement the filesystem substrate for the Rust runtime while preserving the
Python `millrace-ai` workspace contract.

Goals:
- Implement workspace path modeling for `millrace-agents/`.
- Implement `millrace init` behavior.
- Implement baseline manifest creation and managed asset deployment.
- Implement queue and state stores for canonical markdown documents and JSON
  state artifacts.
- Implement runtime lock inspection/acquire/release behavior.
- Implement first workspace doctor checks.

Non-Goals:
- Do not run real stage runners in this slice.
- Do not start daemon scheduling in this slice.

Acceptance:
- Python and Rust `init` produce equivalent required tree structure after
  normalization.
- Selected bootstrap files match after normalizing platform paths and
  timestamps.
- Queue/store tests cover claim, transition, block, done, and repair paths.
- Tests never write `millrace-agents/` into the repository root except through
  the intentionally initialized operator workspace.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/workspace/`
- `../millrace-py/tests/workspace/`
- `../millrace-py/docs/runtime/millrace-workspace-baselines-and-upgrades.md`
