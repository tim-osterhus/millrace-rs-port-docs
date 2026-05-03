# Slice 4: Port CLI Read/Write Surface

Implement operator commands that do not require real stage-runner execution.

Goals:
- Implement queue, config, modes, skills, status, runs, doctor, and upgrade
  command surfaces where they can operate without real runner dispatch.
- Implement control commands that mutate offline state or enqueue mailbox
  commands.
- Normalize output enough for parity tests while preserving Rust-native code
  boundaries.

Non-Goals:
- Do not implement `run once` or `run daemon` behavior in this slice beyond
  placeholder errors if needed.
- Do not implicitly compile in commands where Python does not.

Acceptance:
- Command exit codes match Python for covered scenarios.
- Key output lines match normalized snapshots.
- Read-only commands remain read-only.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/cli/`
- `../millrace-py/docs/runtime/millrace-cli-reference.md`
- `../millrace-py/tests/cli/test_cli.py`
