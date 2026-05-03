# Slice 1: Port Millrace Contracts To Rust

Implement the typed contract foundation needed for behavioral parity with the
Python `millrace-ai` reference at `v0.16.1`.

Goals:
- Port stage planes, work item kinds, legal terminal markers, result classes,
  running markers, and stage metadata.
- Port task, spec, incident, and learning-request document models.
- Implement headed markdown parsing and rendering for canonical work documents.
- Port runtime snapshot, recovery counter, mailbox envelope, compile
  diagnostics, stage-result, and token-usage schemas.
- Add Rust tests against representative Python-produced fixtures.

Non-Goals:
- Do not implement runtime scheduling in this slice.
- Do not translate Python modules one-for-one unless that is the cleanest Rust
  boundary.

Acceptance:
- Rust parses and renders representative Python fixture documents.
- JSON contracts round-trip against Python-produced fixtures.
- Invalid terminal markers and illegal stage/result combinations fail clearly.
- `cargo fmt --check` and `cargo test` pass.

References:
- `docs/rust-port-roadmap.md`
- `../millrace-py/src/millrace_ai/contracts/`
- `../millrace-py/src/millrace_ai/workspace/work_documents.py`
- `../millrace-py/tests/runtime/test_contracts.py`
- `../millrace-py/tests/workspace/test_queue_store.py`
