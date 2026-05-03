# Slice 6: Port Daemon Runtime

Implement long-running daemon orchestration after the serial runtime is proven.

Goals:
- Port daemon ownership locking, mailbox intake, watcher/poll intake, stop,
  pause, resume, retry, and config reload behavior.
- Port basic monitor rendering and monitor-log support.
- Port plane-concurrent daemon scheduling from Python `v0.16.1`.
- Ensure completed worker outcomes are applied serially by one owner.

Non-Goals:
- Do not depend on real Codex/Pi adapters for daemon CI.
- Do not make Rust Millrace self-host the port.

Acceptance:
- Default modes remain serial.
- Learning modes allow one learning lane beside permitted foreground work.
- Config reload waits for active planes to drain.
- Shutdown clears running state without corrupting active artifacts.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/runtime/supervisor.py`
- `../millrace-py/docs/runtime/millrace-runtime-lifecycle-diagram.md`
- `../millrace-py/tests/runtime/test_supervisor.py`
- `../millrace-py/tests/runtime/test_plane_concurrency.py`
